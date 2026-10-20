# pyright: reportUnnecessaryComparison=false
# Exhaustive assert_never guards future fixture variants.
"""Actual MCP metadata, active cancellation, and process ownership checks."""

import os
import sys
from pathlib import Path
from threading import Event
from typing import Literal, assert_never
from uuid import uuid4

import anyio
import pytest
from fastmcp import Client
from fastmcp.client.transports import ClientTransport, StdioTransport

from agent.budget import ExecutionBudget, ExecutionBudgetError
from agent.contracts import ResearchInput
from agent.mcp_client import MCPClient, MCPError
from tests.test_budget import complete
from tests.test_mcp import ROOT, adversarial_client, wire_client
from tests.wire_fixture import HttpReply, research_body, serve_wire


@pytest.mark.anyio
@pytest.mark.parametrize("location", ["metadata", "domain", "timeout"])
async def test_untrusted_overrides_never_reach_provider(
    location: Literal["metadata", "domain", "timeout"],
) -> None:
    # Given
    domain = {"company": "회사", "role": "직무"}
    metadata = {"requestId": str(uuid4()), "timeoutSeconds": 30.0}
    match location:
        case "metadata":
            metadata["maxToolCalls"] = 999
        case "domain":
            domain["timeoutSeconds"] = "999"
        case "timeout":
            metadata["timeoutSeconds"] = 999.0
        case unreachable:
            assert_never(unreachable)
    with serve_wire(lambda _: HttpReply(research_body())) as wire:
        async with wire_client(wire.base_url) as raw:
            # When
            result = await raw.call_tool(
                "research_company_role", {"input": domain}, meta=metadata, raise_on_error=False
            )
        # Then
        assert result.is_error
        assert wire.requests.empty()


@pytest.mark.anyio
async def test_active_mcp_cancellation_retains_charge_and_blocks_next_send() -> None:
    # Given
    entered, release = Event(), Event()
    budget = ExecutionBudget()
    errors: list[str] = []

    def respond(_payload: bytes) -> HttpReply:
        _ = entered.set()
        assert release.wait(timeout=10)
        return HttpReply(research_body())

    with serve_wire(respond) as wire:
        async with MCPClient(wire_client(wire.base_url)) as mcp:

            async def dispatch() -> None:
                try:
                    _ = await mcp.research(
                        ResearchInput(company="회사", role="직무"), budget, uuid4()
                    )
                except ExecutionBudgetError as error:
                    _ = errors.append(error.code)

            try:
                # When
                async with anyio.create_task_group() as tasks:
                    _ = tasks.start_soon(dispatch)
                    assert await anyio.to_thread.run_sync(lambda: entered.wait(timeout=5))
                    _ = budget.cancel()
                with pytest.raises(ExecutionBudgetError):
                    _ = await mcp.research(
                        ResearchInput(company="다른회사", role="직무"), budget, uuid4()
                    )
            finally:
                _ = release.set()
        # Then
        assert wire.requests.qsize() == 1
    assert errors == ["CANCELLED"]
    assert budget.snapshot().model_calls == 1
    assert budget.snapshot().native_tool_calls_reserved == 2


@pytest.mark.anyio
async def test_mcp_exit_reaps_owned_child_before_parent_exits(tmp_path: Path) -> None:
    # Given
    pid_path = tmp_path / "owned-child.pid"
    with serve_wire(lambda _: HttpReply(research_body())) as wire:
        raw = Client[ClientTransport](
            StdioTransport(
                command=sys.executable,
                args=[str(ROOT / "tests/mcp_wire_server.py")],
                cwd=str(ROOT),
                env={
                    "PYTHONPATH": str(ROOT),
                    "FIXTURE_BASE_URL": wire.base_url,
                    "FIXTURE_PID_PATH": str(pid_path),
                },
            )
        )
        try:
            # When
            async with MCPClient(raw):
                child_pid = int(pid_path.read_text())
                _ = os.kill(child_pid, 0)
            # Then
            with pytest.raises(ProcessLookupError):
                _ = os.kill(child_pid, 0)
        finally:
            _ = await raw.close()


@pytest.mark.anyio
async def test_mcp_reported_timeout_stops_followup_transmission() -> None:
    # Given

    budget = ExecutionBudget()
    async with MCPClient(adversarial_client("timeout-error")) as mcp:
        # When / Then
        with pytest.raises(MCPError) as raised:
            _ = await mcp.research(ResearchInput(company="회사", role="직무"), budget, uuid4())
        with pytest.raises(ExecutionBudgetError):
            _ = await budget.run_model("analysis", complete)
    assert raised.value.code == "TIMEOUT"
    assert budget.snapshot().model_calls == 1
    assert budget.snapshot().native_tool_calls_reserved == 2


@pytest.mark.anyio
async def test_actual_mcp_transport_timeout_retains_reservation() -> None:
    # Given

    now = [0.0]
    budget = ExecutionBudget(now=lambda: now[0])
    async with MCPClient(adversarial_client("timeout")) as mcp:
        now[0] = 179.98
        # When / Then: a pending tool is interrupted by the actual remaining 20ms scope.
        with pytest.raises((ExecutionBudgetError, MCPError)) as raised:
            _ = await mcp.research(ResearchInput(company="회사", role="직무"), budget, uuid4())
        assert raised.value.code in {"DEADLINE_EXCEEDED", "TIMEOUT"}
        with pytest.raises(ExecutionBudgetError):
            _ = await budget.run_model("analysis", complete)
    assert raised.value.code in {"DEADLINE_EXCEEDED", "TIMEOUT"}
    assert budget.snapshot().model_calls == 1
    assert budget.snapshot().native_tool_calls_reserved == 2
