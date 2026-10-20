"""Injected monotonic time exercises whole-scope deadlines without real waits."""

from typing import Literal

import pytest

from agent.budget import ExecutionBudget, ExecutionBudgetError, OperationContext
from tests.test_budget import Clock, complete


@pytest.mark.anyio
@pytest.mark.parametrize(("scope", "elapsed"), [("request", 180.0), ("research", 45.0)])
async def test_scope_deadline_rejects_late_orchestration(
    scope: Literal["request", "research"], elapsed: float
) -> None:
    # Given
    clock = Clock()
    budget = ExecutionBudget(now=clock)
    seen: list[float] = []

    async def late(_context: OperationContext) -> str:
        _ = seen.append(_context.timeout_seconds)
        clock.value = elapsed
        return "late"

    operation = budget.run_request if scope == "request" else budget.run_research
    # When / Then
    with pytest.raises(ExecutionBudgetError) as raised:
        _ = await operation(late)
    assert raised.value.code == "DEADLINE_EXCEEDED"
    assert seen == [elapsed]
    with pytest.raises(ExecutionBudgetError):
        _ = await budget.run_model("analysis", complete)
    assert budget.snapshot().model_calls == 0


@pytest.mark.anyio
async def test_research_stage_remainder_clamps_model_timeout_to_five_seconds() -> None:
    # Given
    clock = Clock()
    budget = ExecutionBudget(now=clock)

    async def research(_context: OperationContext) -> OperationContext:
        clock.value = 40.0
        return await budget.run_native_research(complete)

    # When
    result = await budget.run_research(research)
    # Then
    assert result.timeout_seconds == 5.0


@pytest.mark.anyio
async def test_research_expiry_blocks_hosted_reservation_after_idle_work() -> None:
    # Given
    clock = Clock()
    budget = ExecutionBudget(now=clock)

    async def research(_context: OperationContext) -> None:
        clock.value = 45.0
        _ = await budget.run_native_research(complete)

    # When / Then
    with pytest.raises(ExecutionBudgetError) as raised:
        _ = await budget.run_research(research)
    assert raised.value.code == "DEADLINE_EXCEEDED"
    assert budget.snapshot().model_calls == 0
    assert budget.snapshot().native_tool_calls_reserved == 0
