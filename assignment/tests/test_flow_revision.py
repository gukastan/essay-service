"""Shared revision reservation observed through the request budget."""

from typing import Literal
from uuid import uuid4

import anyio
import pytest

from agent.budget import (
    ExecutionBudget,
    ExecutionBudgetError,
    OperationContext,
    RevisionReservationError,
)
from agent.contracts import DraftRequest
from agent.nodes.research import error_response
from agent.state import initial_state


@pytest.mark.anyio
async def test_concurrent_d_and_i_have_exactly_one_winner() -> None:
    # Given
    budget = ExecutionBudget()
    winners: list[str] = []
    failures: list[str] = []

    async def reserve(route: Literal["D", "I"]) -> None:
        try:
            result = await budget.reserve_revision(route)
            winners.append(result.route)
        except RevisionReservationError as error:
            failures.append(error.code)

    # When
    async with anyio.create_task_group() as tasks:
        for route in ("D", "I"):
            _ = tasks.start_soon(reserve, route)
    # Then
    assert len(winners) == 1
    assert failures == ["REVISION_EXHAUSTED"]
    assert budget.snapshot().revision_count == 1
    assert budget.snapshot().revision_route == winners[0]
    assert budget.snapshot().model_calls == 0


@pytest.mark.anyio
async def test_revision_is_not_refunded_after_writer_failure() -> None:
    # Given
    budget = ExecutionBudget()
    _ = await budget.reserve_revision("D")

    async def fail(_context: OperationContext) -> None:
        message = "synthetic writer failure"
        raise OSError(message)

    # When
    with pytest.raises(OSError, match="synthetic writer failure"):
        await budget.run_model("writer", fail)
    # Then
    with pytest.raises(RevisionReservationError) as rejected:
        _ = await budget.reserve_revision("I")
    assert rejected.value.code == "REVISION_EXHAUSTED"
    assert budget.snapshot().revision_count == 1
    assert budget.snapshot().model_calls == 1


@pytest.mark.anyio
async def test_revision_survives_actual_cancellation() -> None:
    # Given
    budget = ExecutionBudget()
    reserved = anyio.Event()

    async def revise() -> None:
        _ = await budget.reserve_revision("I")
        reserved.set()
        await budget.run_model("writer", pending)

    async def pending(_context: OperationContext) -> None:
        await anyio.sleep_forever()

    # When
    async with anyio.create_task_group() as tasks:
        _ = tasks.start_soon(revise)
        await reserved.wait()
        tasks.cancel_scope.cancel()
    # Then
    assert budget.snapshot().revision_count == 1
    with pytest.raises(ExecutionBudgetError) as rejected:
        _ = await budget.reserve_revision("D")
    assert rejected.value.code == "CANCELLED"


@pytest.mark.anyio
async def test_requests_reserve_independently_and_state_cannot_reset_budget() -> None:
    # Given
    first, second = ExecutionBudget(), ExecutionBudget()
    request = DraftRequest(company="회사", role="직무", question="문항", experience="경험")
    # When
    _ = await first.reserve_revision("D")
    _ = await second.reserve_revision("I")
    reconstructed = initial_state(request, first)
    # Then
    assert reconstructed.get("revision_count") == 1
    assert first.snapshot().revision_route == "D"
    assert second.snapshot().revision_route == "I"
    with pytest.raises(RevisionReservationError) as rejected:
        _ = await first.reserve_revision("I")
    assert rejected.value.code == "REVISION_EXHAUSTED"


@pytest.mark.anyio
async def test_revision_stays_consumed_after_request_deadline() -> None:
    # Given
    now = [0.0]
    budget = ExecutionBudget(now=lambda: now[0])
    _ = await budget.reserve_revision("D")
    now[0] = 180.0
    # When / Then
    with pytest.raises(ExecutionBudgetError) as rejected:
        _ = await budget.reserve_revision("I")
    assert rejected.value.code == "DEADLINE_EXCEEDED"
    assert budget.snapshot().revision_count == 1


@pytest.mark.anyio
@pytest.mark.parametrize("route", ["H", "J", "", "d"])
async def test_invalid_revision_route_does_not_consume_opportunity(route: str) -> None:
    # Given
    budget = ExecutionBudget()
    # When / Then
    with pytest.raises(RevisionReservationError) as rejected:
        _ = await budget.reserve_revision(route)
    assert rejected.value.code == "INVALID_REVISION_ROUTE"
    assert budget.snapshot().revision_count == 0
    assert budget.snapshot().revision_route is None
    assert (await budget.reserve_revision("D")).revision_count == 1


@pytest.mark.anyio
async def test_revision_exhaustion_does_not_enter_research_budget_error_boundary() -> None:
    # Given
    budget = ExecutionBudget()
    _ = await budget.reserve_revision("D")
    result: list[str] = []
    # When
    try:
        _ = await budget.reserve_revision("I")
    except ExecutionBudgetError as error:
        result.append(error_response(error, uuid4()).code)
    except RevisionReservationError as error:
        result.append(error.code)
    # Then
    assert result == ["REVISION_EXHAUSTED"]
