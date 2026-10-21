"""Controlled role fixtures; these are not live model or end-to-end quality tests."""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

import pytest
from pydantic import BaseModel

from agent.budget import ExecutionBudget, OperationContext, RevisionReservation
from agent.contracts import (
    MANDATORY_CRITERIA,
    CriterionResult,
    DraftEnvelope,
    DraftRequest,
    Evaluation,
    EvaluationIssue,
    JobRequirement,
    ParagraphSpan,
    PlanClaim,
    UserProvidedSource,
    WritingPlan,
)
from agent.flow_state import FlowStateError, bind_evaluation
from agent.nodes.plan import build_plan
from agent.nodes.revise import RevisionNode, RevisionPatches, SentencePatch
from agent.nodes.write import WriteNode
from agent.nodes.writing_support import WritingError
from agent.providers import ModelResult, StructuredModelRequest
from agent.state import WorkflowState, initial_state
from tests.flow_fixture import analysis, research


@dataclass(frozen=True, slots=True)
class ControlledProvider:
    value: BaseModel

    async def generate[T: BaseModel](
        self, request: StructuredModelRequest[T], budget: ExecutionBudget
    ) -> ModelResult[T]:
        async def invoke(_context: OperationContext) -> ModelResult[T]:
            return ModelResult(
                request.schema.model_validate_json(self.value.model_dump_json()), None
            )

        return await budget.run_model(request.role, invoke)


def writing_state(budget: ExecutionBudget) -> WorkflowState:
    state = initial_state(
        DraftRequest(company="회사", role="직무", question="경험을 설명", experience="실행했다."),
        budget,
    )
    report = research().model_copy(
        update={
            "sources": (
                UserProvidedSource(
                    id="source",
                    kind="user_provided",
                    title="시험 공고",
                    checked_at=datetime(2026, 10, 20, tzinfo=UTC),
                    excerpt="협업을 요구한다.",
                ),
            ),
            "job_requirements": (
                JobRequirement(id="job", text="협업을 요구한다.", source_ids=("source",)),
            ),
        }
    )
    state.update(flow_analysis=analysis(), research=report)
    state.update(build_plan(state, budget))
    return state


def generated(plan: WritingPlan) -> DraftEnvelope:
    claims = tuple(
        PlanClaim(
            id=c.id,
            kind=c.kind,
            evidence_ids=c.evidence_ids,
            text={
                "interpretation": "현재 협업이 중요하다고 생각합니다.",
                "future": "입사 후 협업을 실천하겠습니다.",
            }.get(c.id, c.text),
        )
        for c in plan.claims
    )
    lookup = {c.id: c.text for c in claims}
    text = ""
    spans: list[ParagraphSpan] = []
    for paragraph in plan.paragraphs:
        if text:
            text += "\n\n"
        start = len(text)
        text += " ".join(lookup[c] for c in paragraph.claim_ids)
        spans.append(ParagraphSpan(paragraph_id=paragraph.id, start=start, end=len(text)))
    return DraftEnvelope(
        version=plan.version,
        plan_version=plan.version,
        draft=text,
        paragraphs=tuple(spans),
        claim_map=claims,
        fit_reasons=(),
    )


def require_plan(state: WorkflowState) -> WritingPlan:
    plan = state.get("plan")
    assert plan is not None
    return plan


def evaluated(
    state: WorkflowState, scope: Literal["wording", "plan_or_claim"] = "wording"
) -> SentencePatch:
    plan = require_plan(state)
    draft = generated(plan)
    claim = next(c for c in draft.claim_map if c.id == "interpretation")
    start = draft.draft.index(claim.text)
    issue = EvaluationIssue(
        id="issue",
        criterion_id="expression_kind",
        claim_ids=(claim.id,),
        paragraph_ids=("connection",),
        start=start,
        end=start + len(claim.text),
        reason="표현 검토",
        scope=scope,
        instruction="표현을 명확히 설명",
        missing_fields=(),
    )
    evaluation = Evaluation(
        draft_version=1,
        plan_version=1,
        issues=(issue,),
        criteria=tuple(
            CriterionResult(criterion_id=c, passed=c != "expression_kind")
            for c in MANDATORY_CRITERIA
        ),
    )
    request_id = state.get("request_id")
    assert request_id is not None
    state.update(
        draft_envelope=draft, evaluation=bind_evaluation(request_id, evaluation, draft, plan)
    )
    return SentencePatch(
        claim_id=claim.id,
        start=start,
        end=start + len(claim.text),
        text="현재 협업과 소통이 중요하다고 생각합니다.",
    )


def test_plan_is_code_owned_and_covers_requirements() -> None:
    # Given
    budget = ExecutionBudget()
    # When
    state = writing_state(budget)
    # Then
    plan = require_plan(state)
    assert plan.selected_evidence_ids == ("e1", "job")
    assert sum(p.target_characters for p in plan.paragraphs) == 900
    assert {r for p in plan.paragraphs for r in p.requirement_ids} == {"r1"}
    assert plan.claims[0].text == "실행했다."
    assert budget.snapshot().model_calls == 0


@pytest.mark.anyio
async def test_writer_returns_short_draft_unpadded_for_full_review() -> None:
    # Given
    budget = ExecutionBudget()
    state = writing_state(budget)
    draft = generated(require_plan(state))
    # When
    update = await WriteNode(ControlledProvider(draft)).run(state, budget)
    # Then
    assert update.get("draft_envelope") == draft
    assert len(draft.draft) < 801
    assert update.get("evaluation") is None
    assert budget.snapshot().model_calls == 1


@pytest.mark.anyio
async def test_revision_reassembles_full_draft_and_invalidates_evaluation() -> None:
    # Given
    budget = ExecutionBudget()
    state = writing_state(budget)
    patch = evaluated(state)
    original = state.get("draft_envelope")
    assert original is not None
    reservation = await budget.reserve_revision("I")
    response = RevisionPatches(draft_version=1, plan_version=1, patches=(patch,))
    # When
    update = await RevisionNode(ControlledProvider(response)).run(state, budget, reservation)
    # Then
    result = update.get("draft_envelope")
    assert result is not None
    assert result.draft == original.draft[: patch.start] + patch.text + original.draft[patch.end :]
    assert result.version == 2
    assert result.plan_version == 1
    assert result.claim_map[0] == original.claim_map[0]
    assert result.paragraphs[-1].end == len(result.draft)
    assert update.get("evaluation") is None
    assert update.get("revision_count") == 1
    assert budget.snapshot().model_calls == 1


@pytest.mark.anyio
async def test_d_revision_restructures_without_model_and_e_uses_reserved_budget() -> None:
    # Given
    budget = ExecutionBudget()
    state = writing_state(budget)
    _ = evaluated(state, "plan_or_claim")
    reservation = await budget.reserve_revision("D")
    # When
    update = build_plan(state, budget, reservation)
    # Then
    plan = require_plan(update)
    assert plan.version == 2
    assert len(plan.paragraphs) == 3
    assert budget.snapshot().model_calls == 0
    assert update.get("revision_count") == 1


@pytest.mark.anyio
@pytest.mark.parametrize("attack", ["unreserved", "wrong_route", "stale", "foreign"])
async def test_revision_rejects_control_attacks_before_model(attack: str) -> None:
    # Given
    budget = ExecutionBudget()
    state = writing_state(budget)
    patch = evaluated(state)
    reservation = RevisionReservation("I")
    if attack != "unreserved":
        reservation = await budget.reserve_revision("D" if attack == "wrong_route" else "I")
    if attack == "stale":
        state["draft_envelope"] = generated(require_plan(state)).model_copy(update={"version": 2})
    if attack == "foreign":
        state["request_id"] = uuid4()
    response = RevisionPatches(draft_version=1, plan_version=1, patches=(patch,))
    # When / Then
    with pytest.raises(WritingError):
        _ = await RevisionNode(ControlledProvider(response)).run(state, budget, reservation)
    assert budget.snapshot().model_calls == 0


@pytest.mark.anyio
@pytest.mark.parametrize("attack", ["overlap", "outside", "old_version", "fact", "invention"])
async def test_revision_rejects_adversarial_patches_without_refund(attack: str) -> None:
    # Given
    budget = ExecutionBudget()
    state = writing_state(budget)
    patch = evaluated(state)
    if attack == "outside":
        patch = patch.model_copy(update={"start": 0})
    if attack == "fact":
        patch = SentencePatch(claim_id="personal-1", start=0, end=5, text="수상했다.")
    if attack == "invention":
        patch = patch.model_copy(update={"text": "매출 90%를 달성했습니다."})
    response = RevisionPatches(
        draft_version=2 if attack == "old_version" else 1,
        plan_version=1,
        patches=(patch, patch) if attack == "overlap" else (patch,),
    )
    reservation = await budget.reserve_revision("I")
    # When / Then
    with pytest.raises(WritingError):
        _ = await RevisionNode(ControlledProvider(response)).run(state, budget, reservation)
    assert budget.snapshot().revision_count == 1
    assert budget.snapshot().model_calls == 1


@pytest.mark.anyio
@pytest.mark.parametrize("attack", ["achievement", "unmapped", "source", "version"])
async def test_writer_rejects_invented_or_misbound_output(attack: str) -> None:
    # Given
    budget = ExecutionBudget()
    state = writing_state(budget)
    draft = generated(require_plan(state))
    data = draft.model_dump()
    if attack == "achievement":
        data["claim_map"][0]["text"] = "수상했다."
        data["draft"] = draft.draft.replace("실행했다.", "수상했다.")
    if attack == "unmapped":
        data["draft"] = draft.draft + " 허위"
        data["paragraphs"][-1]["end"] += 3
    if attack == "source":
        data["claim_map"][0]["evidence_ids"] = ("company-fact",)
    if attack == "version":
        data["version"] = 2
    response = DraftEnvelope.model_validate(data)
    # When / Then
    with pytest.raises((WritingError, FlowStateError)):
        _ = await WriteNode(ControlledProvider(response)).run(state, budget)
    assert budget.snapshot().model_calls == 1
