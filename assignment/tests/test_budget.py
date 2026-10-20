"""Atomic reservation, deadline, cancellation, and isolation behavior."""

import anyio
import pytest

from agent.budget import ExecutionBudget, ExecutionBudgetError, OperationContext
from agent.providers import ModelRole


class Clock:
    """Explicitly mutable deterministic monotonic clock."""

    def __init__(self) -> None:
        self.value: float = 0.0

    def __call__(self) -> float:
        return self.value


async def complete(context: OperationContext) -> OperationContext:
    return context


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("revision", "expected_calls", "expected_tokens"), [(False, 4, 12000), (True, 6, 18000)]
)
async def test_normal_and_revision_reservations(
    *, revision: bool, expected_calls: int, expected_tokens: int
) -> None:
    # Given
    budget = ExecutionBudget()
    roles: list[ModelRole] = ["analysis", "writer", "review"]
    if revision:
        _ = roles.extend(["writer", "review"])
    # When
    native = await budget.run_native_research(complete)
    for role in roles:
        _ = await budget.run_model(role, complete)
    # Then
    usage = budget.snapshot()
    assert (usage.model_calls, usage.output_tokens_reserved, usage.native_tool_calls_reserved) == (
        expected_calls,
        expected_tokens,
        2,
    )
    assert (native.max_tool_calls, native.max_output_tokens) == (2, 3000)


@pytest.mark.anyio
async def test_simultaneous_reservations_never_oversubscribe() -> None:
    # Given
    budget = ExecutionBudget()
    outcomes: list[str] = []

    async def reserve(role: ModelRole) -> None:
        try:
            _ = await budget.run_model(role, complete)
            _ = outcomes.append("accepted")
        except ExecutionBudgetError as error:
            _ = outcomes.append(error.code)

    # When
    async with anyio.create_task_group() as tasks:
        for role in ("research", "analysis", "writer", "review", "writer", "review"):
            _ = tasks.start_soon(reserve, role)
        for _ in range(6):
            _ = tasks.start_soon(reserve, "writer")
    # Then
    assert outcomes.count("accepted") == 6
    assert outcomes.count("LIMIT_EXCEEDED") == 6
    assert budget.snapshot().model_calls == 6
    assert budget.snapshot().output_tokens_reserved == 18000


@pytest.mark.anyio
async def test_racing_hosted_attempts_reserve_only_once() -> None:
    # Given
    budget = ExecutionBudget()
    transmissions: list[int] = []
    rejected: list[str] = []

    async def transmit(context: OperationContext) -> None:
        assert budget.snapshot().model_calls == 1
        assert budget.snapshot().native_tool_calls_reserved == 2
        _ = transmissions.append(context.max_tool_calls)

    async def attempt() -> None:
        try:
            _ = await budget.run_native_research(transmit)
        except ExecutionBudgetError as error:
            _ = rejected.append(error.code)

    # When
    async with anyio.create_task_group() as tasks:
        for _ in range(8):
            _ = tasks.start_soon(attempt)
    # Then
    assert transmissions == [2]
    assert rejected == ["LIMIT_EXCEEDED"] * 7
    assert budget.snapshot().output_tokens_reserved == 3000


@pytest.mark.anyio
async def test_failed_hosted_call_cannot_repeat_or_refund() -> None:
    # Given
    budget = ExecutionBudget()
    calls = 0

    async def fail(_context: OperationContext) -> None:
        nonlocal calls
        calls += 1
        message = "fixture provider failure"
        raise OSError(message)

    # When
    with pytest.raises(OSError, match="fixture provider failure"):
        _ = await budget.run_native_research(fail)
    with pytest.raises(ExecutionBudgetError) as raised:
        _ = await budget.run_native_research(fail)
    # Then
    assert raised.value.code == "LIMIT_EXCEEDED"
    assert calls == 1
    assert budget.snapshot().model_calls == 1
    assert budget.snapshot().native_tool_calls_reserved == 2


@pytest.mark.anyio
async def test_active_cancel_stops_work_and_blocks_next_transmission() -> None:
    # Given
    budget = ExecutionBudget()
    entered = anyio.Event()
    outcomes: list[str] = []

    async def pending(_context: OperationContext) -> None:
        _ = entered.set()
        _ = await anyio.sleep_forever()

    async def dispatch() -> None:
        try:
            _ = await budget.run_native_research(pending)
        except ExecutionBudgetError as error:
            _ = outcomes.append(error.code)

    # When
    async with anyio.create_task_group() as tasks:
        _ = tasks.start_soon(dispatch)
        _ = await entered.wait()
        _ = budget.cancel()
    with pytest.raises(ExecutionBudgetError) as raised:
        _ = await budget.run_model("analysis", complete)
    # Then
    assert outcomes == ["CANCELLED"]
    assert raised.value.code == "CANCELLED"
    assert budget.snapshot().model_calls == 1
    assert budget.snapshot().native_tool_calls_reserved == 2


@pytest.mark.anyio
@pytest.mark.parametrize(("elapsed", "expected"), [(0.0, 30.0), (179.0, 1.0)])
async def test_model_timeout_uses_request_remainder(elapsed: float, expected: float) -> None:
    # Given
    clock = Clock()
    budget = ExecutionBudget(now=clock)
    clock.value = elapsed
    # When
    context = await budget.run_model("analysis", complete)
    # Then
    assert context.timeout_seconds == expected


@pytest.mark.anyio
@pytest.mark.parametrize("elapsed", [30.0, 31.0])
async def test_late_model_completion_expires_request(elapsed: float) -> None:
    # Given
    clock = Clock()
    budget = ExecutionBudget(now=clock)

    async def late(_context: OperationContext) -> str:
        clock.value = elapsed
        return "late"

    # When / Then
    with pytest.raises(ExecutionBudgetError) as raised:
        _ = await budget.run_model("analysis", late)
    assert raised.value.code == "DEADLINE_EXCEEDED"
    assert budget.snapshot().model_calls == 1
    with pytest.raises(ExecutionBudgetError):
        _ = await budget.run_model("writer", complete)


@pytest.mark.anyio
async def test_request_deadline_blocks_initial_transmission() -> None:
    # Given
    clock = Clock()
    budget = ExecutionBudget(now=clock)
    clock.value = 180.0
    # When / Then
    with pytest.raises(ExecutionBudgetError) as raised:
        _ = await budget.run_native_research(complete)
    assert raised.value.code == "DEADLINE_EXCEEDED"
    assert budget.snapshot().model_calls == 0
    assert budget.snapshot().native_tool_calls_reserved == 0


@pytest.mark.anyio
async def test_separate_requests_have_independent_counters() -> None:
    # Given
    first, second = ExecutionBudget(), ExecutionBudget()
    # When
    _ = await first.run_native_research(complete)
    _ = await second.run_native_research(complete)
    _ = await first.run_model("analysis", complete)
    # Then
    assert first.snapshot().model_calls == 2
    assert second.snapshot().model_calls == 1
    assert (
        first.snapshot().native_tool_calls_reserved
        == second.snapshot().native_tool_calls_reserved
        == 2
    )
