"""Adversarial fact, reservation and provider boundary scenarios."""

from datetime import UTC, datetime

import pytest

from agent.budget import ExecutionBudget, RevisionReservation, RevisionReservationError
from agent.contracts import (
    CompanyFact,
    DraftEnvelope,
    ExperienceEvidence,
    FlowAnalysisResult,
    FlowRequirement,
    JobRequirement,
    PlanClaim,
    UserProvidedSource,
)
from agent.flow_state import FlowStateError
from agent.nodes.plan import build_plan
from agent.nodes.revise import RevisionNode, RevisionPatches
from agent.nodes.write import WriteNode
from agent.nodes.writing_support import WritingContext, WritingError, validate_writing_facts
from tests.test_writing_nodes import (
    ControlledProvider,
    evaluated,
    generated,
    require_plan,
    writing_state,
)


def test_plan_prioritizes_job_and_omits_optional_company_values() -> None:
    # Given
    budget = ExecutionBudget()
    state = writing_state(budget)
    state["plan"] = None
    report = state.get("research")
    assert report is not None
    source = UserProvidedSource(
        id="source",
        kind="user_provided",
        title="시험 공고",
        checked_at=datetime.now(UTC),
        excerpt="협업을 요구한다.",
    )
    state["research"] = report.model_copy(
        update={
            "sources": (source,),
            "job_requirements": (
                JobRequirement(id="job", text="협업을 요구한다.", source_ids=("source",)),
            ),
            "company_facts": (CompanyFact(id="value", text="인재상", source_ids=("source",)),),
        }
    )
    # When
    plan = require_plan(build_plan(state, budget))
    # Then
    assert "job" in plan.selected_evidence_ids
    assert "value" not in plan.selected_evidence_ids
    assert plan.claims[1].kind == "company_fact"


@pytest.mark.parametrize("attack", ["fragment", "offset", "gap", "missing_candidate"])
def test_plan_blocks_invalid_personal_evidence(attack: str) -> None:
    # Given
    budget = ExecutionBudget()
    state = writing_state(budget)
    state["plan"] = None
    context = WritingContext.from_state(state)
    analysis = context.analysis
    if attack == "fragment":
        analysis = analysis.model_copy(
            update={
                "experience_evidence": (
                    ExperienceEvidence(id="e1", quote="실행", start=0, end=2, category="action"),
                )
            }
        )
    if attack == "offset":
        analysis = analysis.model_copy(
            update={
                "experience_evidence": (
                    ExperienceEvidence(
                        id="e1", quote="실행했다.", start=1, end=6, category="action"
                    ),
                )
            }
        )
    if attack == "gap":
        analysis = analysis.model_copy(update={"gaps": ("경험 부족",)})
    if attack == "missing_candidate":
        analysis = analysis.model_copy(
            update={
                "requirements": (
                    analysis.requirements[0].model_copy(update={"candidate_evidence_ids": ()}),
                )
            }
        )
    state["flow_analysis"] = analysis
    # When / Then
    with pytest.raises((WritingError, FlowStateError)):
        _ = build_plan(state, budget)
    assert budget.snapshot().model_calls == 0


@pytest.mark.anyio
async def test_d_then_e_uses_one_writer_call_and_keeps_reservation() -> None:
    # Given
    budget = ExecutionBudget()
    state = writing_state(budget)
    _ = evaluated(state, "plan_or_claim")
    reservation = await budget.reserve_revision("D")
    state.update(build_plan(state, budget, reservation))
    response = generated(require_plan(state))
    # When
    result = await WriteNode(ControlledProvider(response)).run(state, budget)
    # Then
    assert result.get("draft_envelope") == response
    assert budget.snapshot().revision_count == 1
    assert budget.snapshot().model_calls == 1


@pytest.mark.anyio
async def test_second_revision_reservation_cannot_cross_routes() -> None:
    # Given
    budget = ExecutionBudget()
    _ = await budget.reserve_revision("D")
    # When / Then
    with pytest.raises(RevisionReservationError, match="REVISION_EXHAUSTED"):
        _ = await budget.reserve_revision("I")


@pytest.mark.anyio
async def test_d_rejects_forged_observed_revision_count() -> None:
    # Given
    budget = ExecutionBudget()
    state = writing_state(budget)
    _ = evaluated(state, "plan_or_claim")
    state["revision_count"] = 1
    # When / Then
    with pytest.raises(WritingError, match="INVALID_REVISION"):
        _ = build_plan(state, budget, RevisionReservation("D"))


@pytest.mark.anyio
async def test_revision_rejects_mixed_plan_and_wording_issues_before_model() -> None:
    # Given
    budget = ExecutionBudget()
    state = writing_state(budget)
    patch = evaluated(state, "plan_or_claim")
    reservation = await budget.reserve_revision("I")
    response = RevisionPatches(draft_version=1, plan_version=1, patches=(patch,))
    # When / Then
    with pytest.raises(WritingError, match="INVALID_PATCH"):
        _ = await RevisionNode(ControlledProvider(response)).run(state, budget, reservation)
    assert budget.snapshot().model_calls == 0


@pytest.mark.anyio
async def test_company_evidence_cannot_be_laundered_as_personal_fact() -> None:
    # Given
    budget = ExecutionBudget()
    state = writing_state(budget)
    draft = generated(require_plan(state))
    data = draft.model_dump()
    data["claim_map"][0]["kind"] = "company_fact"
    response = DraftEnvelope.model_validate(data)
    # When / Then
    update = await WriteNode(ControlledProvider(response)).run(state, budget)
    result = update.get("draft_envelope")
    assert result is not None
    assert result.claim_map[0].kind == "user_fact"
    assert result.claim_map[0].evidence_ids == draft.claim_map[0].evidence_ids


def test_unicode_sentence_offsets_and_source_order_are_preserved() -> None:
    # Given
    budget = ExecutionBudget()
    state = writing_state(budget)
    request = state.get("input_snapshot")
    assert request is not None
    state["input_snapshot"] = request.model_copy(update={"experience": "😀 실행했다.\n배웠다."})
    state["flow_analysis"] = FlowAnalysisResult(
        requirements=(
            FlowRequirement(
                id="r1",
                text="경험",
                mandatory=True,
                check_condition="설명",
                candidate_evidence_ids=("e1", "e2"),
            ),
        ),
        experience_evidence=(
            ExperienceEvidence(id="e1", quote="😀 실행했다.", start=0, end=7, category="action"),
            ExperienceEvidence(id="e2", quote="배웠다.", start=8, end=12, category="learning"),
        ),
        gaps=(),
    )
    context = WritingContext.from_state(state)
    claims = (
        PlanClaim(id="a", text="배웠다.", kind="user_fact", evidence_ids=("e2",)),
        PlanClaim(id="b", text="😀 실행했다.", kind="user_fact", evidence_ids=("e1",)),
    )
    original = generated(require_plan(state))
    data = original.model_dump()
    data.update(
        draft="배웠다. 😀 실행했다.",
        claim_map=claims,
        paragraphs=({"paragraph_id": "p", "start": 0, "end": 12},),
    )
    draft = DraftEnvelope.model_validate(data)
    # When / Then
    with pytest.raises(WritingError, match="FACT_CHANGED"):
        validate_writing_facts(draft, context)


@pytest.mark.parametrize("missing", ["company", "job"])
def test_plan_uses_personal_evidence_without_optional_job_research(missing: str) -> None:
    # Given
    budget = ExecutionBudget()
    state = writing_state(budget)
    state["plan"] = None
    report = state.get("research")
    assert report is not None
    state["research"] = report.model_copy(
        update={
            "resolved_company": None if missing == "company" else report.resolved_company,
            "job_requirements": () if missing == "job" else report.job_requirements,
        }
    )
    # When
    result = build_plan(state, budget)
    # Then
    plan = result.get("plan")
    assert plan is not None
    if missing == "job":
        assert all(claim.kind != "company_fact" for claim in plan.claims)
    assert budget.snapshot().model_calls == 0


@pytest.mark.anyio
async def test_d_reconsiders_affected_experience_from_existing_candidates() -> None:
    # Given
    budget = ExecutionBudget()
    state = writing_state(budget)
    request = state.get("input_snapshot")
    analysis = state.get("flow_analysis")
    assert request is not None
    assert analysis is not None
    state["input_snapshot"] = request.model_copy(update={"experience": "실행했다. 배웠다."})
    state["flow_analysis"] = analysis.model_copy(
        update={
            "experience_evidence": (
                *analysis.experience_evidence,
                ExperienceEvidence(id="e2", quote="배웠다.", start=6, end=10, category="learning"),
            ),
            "requirements": (
                analysis.requirements[0].model_copy(
                    update={"candidate_evidence_ids": ("e1", "e2")}
                ),
            ),
        }
    )
    _ = evaluated(state, "plan_or_claim")
    reservation = await budget.reserve_revision("D")
    # When
    plan = require_plan(build_plan(state, budget, reservation))
    # Then
    assert "e2" in plan.selected_evidence_ids
    assert "e1" not in plan.selected_evidence_ids
    assert plan.claims[0].text == "배웠다."
    assert budget.snapshot().model_calls == 0
