"""DNS-pinned HTTP reads with explicit, charged redirects and bounded bodies."""

import ipaddress
import socket
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import partial
from typing import Protocol
from urllib.parse import urljoin, urlsplit

import anyio
import httpx
from pydantic import TypeAdapter

from agent.budget import ExecutionBudget, OperationContext
from agent.source_page import MAX_PAGE_BYTES, FetchedPage, PageReadError, extract_page


class PageReader(Protocol):
    async def read(self, url: str, budget: ExecutionBudget) -> FetchedPage: ...


def public_ip(address: str) -> bool:
    try:
        ip = ipaddress.ip_address(address)
    except ValueError:
        return False
    if isinstance(ip, ipaddress.IPv6Address) and (ip.ipv4_mapped or ip.sixtofour or ip.teredo):
        return False
    return ip.is_global and not ip.is_multicast and not ip.is_unspecified and "%" not in address


async def resolve_public(host: str, port: int) -> tuple[str, ...]:
    records = await anyio.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    addresses = tuple(dict.fromkeys(str(record[4][0]) for record in records))
    if not addresses or not all(public_ip(address) for address in addresses):
        raise PageReadError("UNSAFE_URL")
    return addresses


@dataclass(frozen=True, slots=True)
class SafePageReader:
    resolver: Callable[[str, int], Awaitable[tuple[str, ...]]] = resolve_public
    transport: httpx.AsyncBaseTransport | None = None

    async def read(self, url: str, budget: ExecutionBudget) -> FetchedPage:
        current = url
        while True:
            try:
                redirect, page = await budget.run("page", partial(self._hop, current))
            except PageReadError as error:
                if error.code == "TIMEOUT":
                    budget.cancel()
                raise
            if page is not None:
                return page
            if redirect is None:
                raise PageReadError("INVALID_PAGE")
            current = redirect

    async def _hop(
        self, url: str, context: OperationContext
    ) -> tuple[str | None, FetchedPage | None]:
        try:
            host, port = target(url)
            addresses = await self.resolver(host, port)
            if not addresses or not all(public_ip(address) for address in addresses):
                raise PageReadError("UNSAFE_URL")
            original = httpx.URL(url)
            pinned = original.copy_with(host=addresses[0])
            transport = self.transport or httpx.AsyncHTTPTransport(retries=0)
            async with (
                httpx.AsyncClient(
                    transport=transport,
                    trust_env=False,
                    follow_redirects=False,
                    timeout=httpx.Timeout(context.timeout_seconds),
                ) as client,
                client.stream(
                    "GET",
                    pinned,
                    headers={
                        "Host": original.netloc.decode("ascii"),
                        "Accept-Encoding": "identity",
                    },
                    extensions={"sni_hostname": original.host},
                ) as response,
            ):
                return await read_response(response, url)
        except (ValueError, httpx.InvalidURL):
            raise PageReadError("UNSAFE_URL") from None
        except httpx.TimeoutException:
            raise PageReadError("TIMEOUT") from None
        except (OSError, httpx.HTTPError):
            raise PageReadError("NETWORK_ERROR") from None


def target(url: str) -> tuple[str, int]:
    parsed = urlsplit(url)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or any(char.isspace() or not char.isprintable() for char in url)
        or "\\" in url
        or "%" in parsed.hostname
    ):
        raise PageReadError("UNSAFE_URL")
    if parsed.port not in {None, 80, 443}:
        raise PageReadError("UNSAFE_URL")
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    return parsed.hostname, port


async def read_response(
    response: httpx.Response, url: str
) -> tuple[str | None, FetchedPage | None]:
    if response.is_redirect:
        location = TypeAdapter(str | None).validate_python(response.headers.get("location"))
        if not location:
            raise PageReadError("INVALID_PAGE")
        return urljoin(url, location), None
    if response.status_code in {401, 403, 404, 410, 429, 451}:
        raise PageReadError("ACCESS_DENIED")
    if response.is_error:
        raise PageReadError("NETWORK_ERROR")
    if response.headers.get("content-encoding", "identity") != "identity":
        raise PageReadError("INVALID_PAGE")
    media = (
        TypeAdapter(str)
        .validate_python(response.headers.get("content-type", ""))
        .split(";")[0]
        .strip()
    )
    if media not in {"text/html", "text/plain", "application/xhtml+xml"}:
        raise PageReadError("INVALID_PAGE")
    body = bytearray()
    async for chunk in response.aiter_raw():
        if len(body) + len(chunk) > MAX_PAGE_BYTES:
            raise PageReadError("TOO_LARGE")
        body.extend(chunk)
    return None, extract_page(url, bytes(body), datetime.now(UTC))
