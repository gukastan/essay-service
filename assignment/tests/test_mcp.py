"""Actual stdio MCP and real SDK -> local HTTP fixture boundary."""

import os
import sys
from pathlib import Path
from uuid import uuid4

import anyio
import pytest
from fastmcp import Client
from fastmcp.client.transports import ClientTransport, StdioTransport

from agent.budget import ExecutionBudget, ExecutionBudgetError
from agent.contracts import DraftRequest, ResearchInput
from agent.mcp_client import MCPClient, MCPError
from tests.wire_fixture import JSON, HttpReply, research_body, serve_wire

ROOT = Path(__file__).resolve().parents[1]


def wire_client(base_url: str) -> Client[ClientTransport]:
    return Client[ClientTransport](
        StdioTransport(
            command=sys.executable,
            args=[str(ROOT / "tests/mcp_wire_server.py")],
            cwd=str(ROOT),
            env={"PYTHONPATH": str(ROOT), "FIXTURE_BASE_URL": base_url},
        )
    )


def adversarial_client(mode: str) -> Client[ClientTransport]:
    return Client[ClientTransport](
        StdioTransport(
            command=sys.executable,
            args=[str(ROOT / "tests/mcp_adversary.py")],
            cwd=str(ROOT),
            env={"PYTHONPATH": str(ROOT), "FIXTURE_MODE": mode},
        )
    )


@pytest.mark.anyio
async def test_actual_mcp_discovery_reserved_before_sdk_wire_and_private_fields_removed() -> None:
    # Given
    budget = ExecutionBudget()
    observed: list[tuple[int, int]] = []

    def respond(_payload: bytes) -> HttpReply:
        usage = budget.snapshot()
        _ = observed.append((usage.model_calls, usage.native_tool_calls_reserved))
        return HttpReply(research_body())

    draft = DraftRequest(
        company="회사", role="직무", question="PRIVATE_QUESTION", experience="PRIVATE_EXPERIENCE"
    )
    request_id = uuid4()
    with serve_wire(respond) as wire:
        raw = wire_client(wire.base_url)
        async with MCPClient(raw) as mcp:
            tools = await raw.list_tools()
            assert [tool.name for tool in tools] == ["research_company_role"]
            # When
            report = await mcp.research(draft, budget, request_id)
        # Then
        assert report.request_id == request_id
        assert report.result.resolved_company == "회사"
        assert report.tool_calls_reported == 1
        assert observed == [(1, 2)]
        assert wire.requests.qsize() == 1
        payload = wire.requests.get_nowait()
        assert b"PRIVATE_QUESTION" not in payload
        assert b"PRIVATE_EXPERIENCE" not in payload
        body = JSON.validate_json(payload)
        assert isinstance(body, dict)
        assert isinstance(body["input"], str)
        domain = JSON.validate_json(body["input"])
        assert isinstance(domain, dict)
        assert set(domain) <= {"company", "role", "jobPostingUrl", "jobPostingText"}
        assert body["max_tool_calls"] == 2
        assert body["store"] is False


@pytest.mark.anyio
async def test_actual_mcp_failure_is_not_retried_and_reservations_remain() -> None:
    # Given
    budget = ExecutionBudget()
    with serve_wire(lambda _: HttpReply(b'{"error":{"message":"PRIVATE_ERROR"}}', 500)) as wire:
        async with MCPClient(wire_client(wire.base_url)) as mcp:
            # When / Then
            with pytest.raises(MCPError) as raised:
                _ = await mcp.research(ResearchInput(company="회사", role="직무"), budget, uuid4())
            with pytest.raises(ExecutionBudgetError) as repeated:
                _ = await mcp.research(ResearchInput(company="회사", role="직무"), budget, uuid4())
        assert wire.requests.qsize() == 1
    assert raised.value.code == "MODEL_ERROR"
    assert str(raised.value) == "MODEL_ERROR"
    assert repeated.value.code == "LIMIT_EXCEEDED"
    assert budget.snapshot().model_calls == 1
    assert budget.snapshot().native_tool_calls_reserved == 2


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("mode", "expected"),
    [
        ("malformed", "INVALID_RESPONSE"),
        ("wrong-correlation", "INVALID_RESPONSE"),
        ("tool-error", "PROTOCOL_ERROR"),
        ("disconnect", "PROTOCOL_ERROR"),
    ],
)
async def test_actual_mcp_adversarial_results_are_sanitized(mode: str, expected: str) -> None:
    # Given
    budget = ExecutionBudget()
    async with MCPClient(adversarial_client(mode)) as mcp:
        # When / Then
        with pytest.raises(MCPError) as raised:
            _ = await mcp.research(ResearchInput(company="회사", role="직무"), budget, uuid4())
    assert raised.value.code == expected
    assert str(raised.value) == expected
    assert budget.snapshot().model_calls == 1
    assert budget.snapshot().native_tool_calls_reserved == 2


@pytest.mark.anyio
async def test_shared_mcp_connection_keeps_concurrent_requests_correlated() -> None:
    # Given
    reports: list[tuple[str, str, int]] = []

    def respond(payload: bytes) -> HttpReply:
        wire = JSON.validate_json(payload)
        assert isinstance(wire, dict)
        assert isinstance(wire["input"], str)
        domain = JSON.validate_json(wire["input"])
        assert isinstance(domain, dict)
        assert isinstance(domain["company"], str)
        return HttpReply(research_body(domain["company"]))

    with serve_wire(respond) as wire:
        async with MCPClient(wire_client(wire.base_url)) as mcp:

            async def dispatch(company: str) -> None:
                budget = ExecutionBudget()
                request_id = uuid4()
                report = await mcp.research(
                    ResearchInput(company=company, role="직무"), budget, request_id
                )
                assert report.request_id == request_id
                _ = reports.append(
                    (company, report.result.resolved_company or "", budget.snapshot().model_calls)
                )

            # When
            async with anyio.create_task_group() as tasks:
                _ = tasks.start_soon(dispatch, "회사A")
                _ = tasks.start_soon(dispatch, "회사B")
        # Then
        assert wire.requests.qsize() == 2
    assert sorted(reports) == [("회사A", "회사A", 1), ("회사B", "회사B", 1)]


@pytest.mark.anyio
@pytest.mark.parametrize("stopped", ["cancelled", "expired"])
async def test_stopped_budget_does_not_reach_actual_mcp_wire(stopped: str) -> None:
    # Given
    now = [0.0]
    budget = ExecutionBudget(now=lambda: now[0])
    if stopped == "cancelled":
        _ = budget.cancel()
    else:
        now[0] = 180.0
    with serve_wire(lambda _: HttpReply(research_body())) as wire:
        async with MCPClient(wire_client(wire.base_url)) as mcp:
            # When / Then
            with pytest.raises(ExecutionBudgetError):
                _ = await mcp.research(ResearchInput(company="회사", role="직무"), budget, uuid4())
        assert wire.requests.empty()
    assert budget.snapshot().model_calls == 0


@pytest.mark.anyio
async def test_actual_mcp_child_suppresses_inherited_tracing_flags(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Given
    trace_path = tmp_path / "tracing-sentinels.json"
    names = ("LANGCHAIN_TRACING", "LANGCHAIN_TRACING_V2", "LANGSMITH_TRACING")
    for name in names:
        _ = monkeypatch.setenv(name, "true")
    with serve_wire(lambda _: HttpReply(research_body())) as wire:
        env = {
            "PYTHONPATH": str(ROOT),
            "FIXTURE_BASE_URL": wire.base_url,
            "FIXTURE_TRACE_PATH": str(trace_path),
            **dict.fromkeys(names, "true"),
        }
        raw = Client[ClientTransport](
            StdioTransport(
                command=sys.executable,
                args=[str(ROOT / "tests/mcp_wire_server.py")],
                cwd=str(ROOT),
                env=env,
            )
        )
        # When
        async with MCPClient(raw):
            child = JSON.validate_json(trace_path.read_text())
        # Then
        assert child == {**dict.fromkeys(names, "false"), "OTEL_SDK_DISABLED": "true"}
        assert all(os.environ[name] == "false" for name in names)
        assert wire.requests.empty()
