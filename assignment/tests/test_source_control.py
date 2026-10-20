"""Direct-read cancellation, media and injected DNS attack boundaries."""

import socket

import anyio
import httpx
import pytest

from agent.budget import ExecutionBudget, ExecutionBudgetError
from agent.source_http import SafePageReader, resolve_public
from agent.source_page import PageReadError
from tests.test_source_http import PUBLIC, page, public_dns


@pytest.mark.anyio
async def test_system_dns_mixed_answers_are_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    # Given
    async def answers(
        _host: str, port: int, *, type: socket.SocketKind
    ) -> list[tuple[socket.AddressFamily, socket.SocketKind, int, str, tuple[str, int]]]:
        assert type == socket.SOCK_STREAM
        return [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", (PUBLIC, port)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("169.254.169.254", port)),
        ]

    monkeypatch.setattr(anyio, "getaddrinfo", answers)
    # When
    with pytest.raises(PageReadError) as raised:
        _ = await resolve_public("rebind.example", 443)
    # Then
    assert raised.value.code == "UNSAFE_URL"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "headers", [{"content-type": "application/json"}, {"content-encoding": "gzip"}]
)
async def test_unsupported_content_cannot_become_evidence(headers: dict[str, str]) -> None:
    # Given
    reader = SafePageReader(
        resolver=public_dns,
        transport=httpx.MockTransport(lambda _: httpx.Response(200, headers=headers)),
    )
    # When
    with pytest.raises(PageReadError) as raised:
        _ = await reader.read("https://careers.example/jobs", ExecutionBudget())
    # Then
    assert raised.value.code == "INVALID_PAGE"


@pytest.mark.anyio
async def test_active_read_cancellation_stops_followup_before_transmission() -> None:
    # Given
    entered = anyio.Event()
    budget = ExecutionBudget()
    sent: list[str] = []
    errors: list[str] = []

    async def respond(request: httpx.Request) -> httpx.Response:
        sent.append(str(request.url))
        entered.set()
        await anyio.sleep_forever()
        return page()

    reader = SafePageReader(resolver=public_dns, transport=httpx.MockTransport(respond))

    async def read() -> None:
        try:
            _ = await reader.read("https://careers.example/jobs", budget)
        except ExecutionBudgetError as error:
            errors.append(error.code)

    # When
    with anyio.fail_after(5):
        async with anyio.create_task_group() as tasks:
            _ = tasks.start_soon(read)
            await entered.wait()
            budget.cancel()
    # Then
    with pytest.raises(ExecutionBudgetError) as raised:
        _ = await reader.read("https://careers.example/other", budget)
    assert errors == ["CANCELLED"]
    assert raised.value.code == "CANCELLED"
    assert len(sent) == budget.snapshot().page_reads == 1
