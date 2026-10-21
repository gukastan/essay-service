"""F state capture and finite review budget at the executable node boundary."""

from dataclasses import dataclass
from uuid import uuid4

import pytest
from pydantic import BaseModel

from agent.budget import ExecutionBudget, ExecutionBudgetError, OperationContext
from agent.contracts import CriterionResult, Evaluation
from agent.flow_state import FlowStateError, require_ready_evaluation
from agent.nodes.review import ReviewNode
from agent.providers import ModelResult, StructuredModelRequest
from agent.state import WorkflowState
from agent.validate_evidence import evaluation_from_issues, general_issue
from tests.test_review_evidence import review_input


@dataclass(frozen=True, slots=True)
class ControlledReview:
    value: Evaluation
    state: WorkflowState

    async def generate[T: BaseModel](
        self,
        request: StructuredModelRequest[T],
        budget: ExecutionBudget,
    ) -> ModelResult[T]:
        async def invoke(_context: OperationContext) -> ModelResult[T]:
            self.state["request_id"] = uuid4()
            return ModelResult(
                request.schema.model_validate_json(self.value.model_dump_json()), None
            )

        return await budget.run_model(request.role, invoke)


@pytest.mark.anyio
async def test_run_binds_captured_request_when_state_changes_during_model_call() -> None:
    # Given
    context = review_input()
    state = WorkflowState(
        request_id=context.request_id,
        input_snapshot=context.request,
        flow_analysis=context.analysis,
        research=context.research,
        plan=context.plan,
        draft_envelope=context.draft,
    )
    node = ReviewNode(ControlledReview(evaluation_from_issues(context, ()), state))
    # When
    result = await node.run(state, ExecutionBudget())
    # Then
    binding = result.get("evaluation")
    assert binding is not None
    assert binding.request_id == context.request_id
    assert result.get("outcome") is None
    current_id = state.get("request_id")
    assert current_id is not None
    with pytest.raises(FlowStateError, match="FOREIGN_EVALUATION"):
        require_ready_evaluation(binding, current_id, context.draft, context.plan)


@pytest.mark.anyio
async def test_third_review_is_rejected_without_forced_success() -> None:
    # Given
    context = review_input()
    failed = evaluation_from_issues(context, (general_issue("question_coverage", "문항 미응답"),))
    node = ReviewNode(ControlledReview(failed, WorkflowState()))
    budget = ExecutionBudget()
    first = await node.evaluate(context, budget)
    second = await node.evaluate(context, budget)
    # When / Then
    with pytest.raises(ExecutionBudgetError):
        _ = await node.evaluate(context, budget)
    assert not first.binding.evaluation.all_passed
    assert not second.binding.evaluation.all_passed
    assert budget.snapshot().model_calls == 2


@pytest.mark.anyio
@pytest.mark.parametrize("criterion", ["company_factuality", "question_coverage", "job_fit"])
async def test_semantic_failures_survive_when_deterministic_checks_pass(criterion: str) -> None:
    # Given
    context = review_input()
    criterion_id = CriterionResult.model_validate(
        {"criterionId": criterion, "passed": False}
    ).criterion_id
    failed = evaluation_from_issues(context, (general_issue(criterion_id, "의미상 근거 불일치"),))
    node = ReviewNode(ControlledReview(failed, WorkflowState()))
    # When
    result = await node.evaluate(context, ExecutionBudget())
    # Then
    assert result.code.all_passed
    assert not result.binding.evaluation.all_passed
    assert result.binding.evaluation.issues[0].criterion_id == criterion
