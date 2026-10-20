"""Real HTTP transport and socket with test-only connection redirection."""

import anyio
import pytest
from anyio.abc import SocketStream

from agent.budget import ExecutionBudget
from agent.source_http import SafePageReader
from tests.page_wire import serve_page
from tests.test_source_http import PUBLIC, public_dns


@pytest.mark.anyio
async def test_default_transport_connects_pinned_address_and_sends_original_host(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: replace only socket connection routing, never production IP policy.
    connect = anyio.connect_tcp
    targets: list[tuple[str, int]] = []
    with serve_page() as wire:

        async def local_socket(
            remote_host: str, remote_port: int, local_host: str | None = None
        ) -> SocketStream:
            targets.append((remote_host, remote_port))
            return await connect("127.0.0.1", wire.port, local_host=local_host)

        monkeypatch.setattr(anyio, "connect_tcp", local_socket)
        reader = SafePageReader(resolver=public_dns)
        # When
        result = await reader.read("http://careers.example/jobs/42", ExecutionBudget())
        # Then
        assert targets == [(PUBLIC, 80)]
        assert wire.requests.get_nowait() == ("/jobs/42", "careers.example")
        assert wire.requests.empty()
        assert result.text == "Acme Engineer Build reliable systems."
