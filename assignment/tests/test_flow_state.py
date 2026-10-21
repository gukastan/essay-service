# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false
"""Real flow state channels and evaluation binding guards."""

from uuid import uuid4

import pytest
from langgraph.graph import END, START, StateGraph

from agent.budget import ExecutionBudget
from agent.contracts import (
    MANDATORY_CRITERIA,
    CriterionResult,
    DraftEnvelope,
    DraftRequest,
    Evaluation,
    ParagraphSpan,
    PlanClaim,
    PlanParagraph,
    ReadyTerminal,
    WritingPlan,
)
from agent.flow_state import FlowStateError, bind_evaluation, require_ready_evaluation
from agent.state import WorkflowState, initial_state
from tests.flow_fixture import analysis


def plan() -> WritingPlan:
    return WritingPlan(
        version=1,
        selected_evidence_ids=("experience-1",),
        claims=(
            PlanClaim(id="claim-1", text="경험", kind="user_fact", evidence_ids=("experience-1",)),
        ),
        paragraphs=(
            PlanParagraph(
                id="paragraph-1",
                purpose="경험 설명",
                order=1,
                target_characters=900,
                requirement_ids=("requirement-1",),
                claim_ids=("claim-1",),
            ),
        ),
    )


def draft(version: int = 1, text: str = "경험" + "가" * 799) -> DraftEnvelope:
    return DraftEnvelope(
        version=version,
        plan_version=1,
        draft=text,
        paragraphs=(ParagraphSpan(paragraph_id="paragraph-1", start=0, end=len(text)),),
        claim_map=plan().claims,
        fit_reasons=(),
    )


def evaluation() -> Evaluation:
    return Evaluation(
        draft_version=1,
        plan_version=1,
        criteria=tuple(
            CriterionResult(criterion_id=item, passed=True) for item in MANDATORY_CRITERIA
        ),
        issues=(),
    )


@pytest.mark.anyio
async def test_real_graph_preserves_flow_values_and_bound_evaluation() -> None:
    # Given
    request_id = uuid4()
    current_plan, current_draft = plan(), draft()
    current_analysis = analysis()
    binding = bind_evaluation(request_id, evaluation(), current_draft, current_plan)
    terminal = ReadyTerminal(kind="ready", route="H", reason="all_criteria_passed")

    def attach(state: WorkflowState) -> WorkflowState:
        _ = state
        return {
            "flow_analysis": current_analysis,
            "plan": current_plan,
            "draft_envelope": current_draft,
            "evaluation": binding,
            "route": "H",
            "terminal_reason": terminal,
        }

    graph = StateGraph(WorkflowState)
    _ = graph.add_node("fixture_handoff", attach)
    _ = graph.add_edge(START, "fixture_handoff")
    _ = graph.add_edge("fixture_handoff", END)
    initial = initial_state(
        DraftRequest(company="회사", role="직무", question="문항", experience="경험"),
        ExecutionBudget(),
        request_id,
    )
    # When
    result = await graph.compile().ainvoke(initial)
    # Then
    assert result.get("plan") == current_plan
    assert result.get("flow_analysis") == current_analysis
    assert result.get("draft_envelope") == current_draft
    assert result.get("evaluation") == binding
    assert result.get("route") == "H"
    assert result.get("terminal_reason") == terminal


@pytest.mark.parametrize("changed", [draft(2), draft(text="경험 추가")])
def test_ready_rejects_new_version_and_changed_same_version(changed: DraftEnvelope) -> None:
    # Given
    request_id = uuid4()
    current_plan = plan()
    binding = bind_evaluation(request_id, evaluation(), draft(), current_plan)
    # When / Then
    with pytest.raises(FlowStateError) as raised:
        require_ready_evaluation(binding, request_id, changed, current_plan)
    assert raised.value.code == "STALE_EVALUATION"


def test_ready_rejects_another_requests_pass_with_identical_versions() -> None:
    # Given
    current_plan, current_draft = plan(), draft()
    binding = bind_evaluation(uuid4(), evaluation(), current_draft, current_plan)
    # When / Then
    with pytest.raises(FlowStateError) as raised:
        require_ready_evaluation(binding, uuid4(), current_draft, current_plan)
    assert raised.value.code == "FOREIGN_EVALUATION"


def test_binding_rejects_old_evaluation_version() -> None:
    # Given / When / Then
    with pytest.raises(FlowStateError) as raised:
        _ = bind_evaluation(uuid4(), evaluation(), draft(2), plan())
    assert raised.value.code == "VERSION_MISMATCH"


def test_ready_accepts_the_exact_evaluated_context() -> None:
    # Given
    request_id = uuid4()
    current_plan, current_draft = plan(), draft()
    binding = bind_evaluation(request_id, evaluation(), current_draft, current_plan)
    # When / Then
    assert require_ready_evaluation(binding, request_id, current_draft, current_plan) is None
