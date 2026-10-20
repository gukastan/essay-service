"""Deterministic network-policy checks at the real HTTPX transport boundary."""

from typing import Final

import httpx
import pytest

from agent.budget import ExecutionBudget, ExecutionBudgetError
from agent.source_http import SafePageReader
from agent.source_page import PageReadError

PUBLIC: Final = "93.184.216.34"


async def public_dns(_host: str, _port: int) -> tuple[str, ...]:
    return (PUBLIC,)


def page(body: bytes = b"<p>Acme Engineer builds systems.</p>") -> httpx.Response:
    return httpx.Response(200, headers={"content-type": "text/html"}, stream=httpx.ByteStream(body))


@pytest.mark.anyio
@pytest.mark.parametrize(
    "addresses",
    [
        ("127.0.0.1",),
        ("10.0.0.1",),
        ("172.16.0.1",),
        ("192.168.1.1",),
        ("169.254.169.254",),
        ("::1",),
        ("fe80::1",),
        ("fc00::1",),
        ("::ffff:127.0.0.1",),
        ("::ffff:192.168.0.1",),
        (PUBLIC, "10.0.0.1"),
        (),
    ],
)
async def test_nonpublic_or_mixed_dns_never_sends(addresses: tuple[str, ...]) -> None:
    # Given
    sent: list[httpx.Request] = []

    async def resolve(_host: str, _port: int) -> tuple[str, ...]:
        return addresses

    def respond(request: httpx.Request) -> httpx.Response:
        sent.append(request)
        return page()

    reader = SafePageReader(resolver=resolve, transport=httpx.MockTransport(respond))
    # When
    with pytest.raises(PageReadError) as raised:
        _ = await reader.read("https://careers.example/job", ExecutionBudget())
    # Then
    assert raised.value.code == "UNSAFE_URL"
    assert sent == []


@pytest.mark.anyio
@pytest.mark.parametrize("url", ["file:///etc/passwd", "http://u:p@example.com", "http://a\\b/x"])
async def test_unsafe_url_rejected_before_dns(url: str) -> None:
    # Given
    resolved: list[str] = []

    async def resolve(host: str, _port: int) -> tuple[str, ...]:
        resolved.append(host)
        return (PUBLIC,)

    # When
    with pytest.raises(PageReadError) as raised:
        _ = await SafePageReader(resolver=resolve).read(url, ExecutionBudget())
    # Then
    assert raised.value.code == "UNSAFE_URL"
    assert resolved == []


@pytest.mark.anyio
async def test_connection_target_is_numeric_but_host_and_tls_identity_are_original() -> None:
    # Given
    sent: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        sent.append(request)
        return page()

    reader = SafePageReader(resolver=public_dns, transport=httpx.MockTransport(respond))
    # When
    result = await reader.read("https://careers.example/jobs/1", ExecutionBudget())
    # Then
    assert len(sent) == 1
    assert str(sent[0].url) == f"https://{PUBLIC}/jobs/1"
    assert sent[0].headers["host"] == "careers.example"
    assert sent[0].extensions["sni_hostname"] == "careers.example"
    assert result.url == "https://careers.example/jobs/1"


@pytest.mark.anyio
async def test_redirect_private_target_is_checked_and_never_sent() -> None:
    # Given
    sent: list[str] = []
    budget = ExecutionBudget()

    async def resolve(host: str, _port: int) -> tuple[str, ...]:
        return ("127.0.0.1",) if host == "internal.example" else (PUBLIC,)

    def respond(request: httpx.Request) -> httpx.Response:
        sent.append(str(request.url))
        return httpx.Response(302, headers={"location": "https://internal.example/private"})

    reader = SafePageReader(resolver=resolve, transport=httpx.MockTransport(respond))
    # When
    with pytest.raises(PageReadError) as raised:
        _ = await reader.read("https://careers.example/job", budget)
    # Then
    assert raised.value.code == "UNSAFE_URL"
    assert sent == [f"https://{PUBLIC}/job"]
    assert budget.snapshot().page_reads == 2


@pytest.mark.anyio
async def test_redirect_loop_charges_each_hop_and_stops_before_fourth_send() -> None:
    # Given
    sent: list[str] = []
    budget = ExecutionBudget()

    def respond(request: httpx.Request) -> httpx.Response:
        sent.append(str(request.url))
        return httpx.Response(302, headers={"location": "/again"})

    reader = SafePageReader(resolver=public_dns, transport=httpx.MockTransport(respond))
    # When
    with pytest.raises(ExecutionBudgetError) as raised:
        _ = await reader.read("https://careers.example/job", budget)
    # Then
    assert raised.value.code == "LIMIT_EXCEEDED"
    assert len(sent) == budget.snapshot().page_reads == 3


@pytest.mark.anyio
async def test_research_deadline_shared_across_redirects_blocks_later_send() -> None:
    # Given
    now = [0.0]
    budget = ExecutionBudget(now=lambda: now[0])
    sent: list[str] = []

    def respond(request: httpx.Request) -> httpx.Response:
        sent.append(str(request.url))
        now[0] = 45.0
        return httpx.Response(302, headers={"location": "/later"})

    reader = SafePageReader(resolver=public_dns, transport=httpx.MockTransport(respond))
    # When
    with pytest.raises(ExecutionBudgetError) as raised:
        _ = await reader.read("https://careers.example/job", budget)
    # Then
    assert raised.value.code == "DEADLINE_EXCEEDED"
    assert len(sent) == 1
    assert budget.snapshot().page_reads == 1
