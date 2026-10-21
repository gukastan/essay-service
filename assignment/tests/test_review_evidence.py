"""Controlled F evidence fixtures; no live model quality claim."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from agent.contracts import (
    DraftEnvelope,
    DraftRequest,
    FitReason,
    JobRequirement,
    ParagraphSpan,
    PlanClaim,
    UserProvidedSource,
)
from agent.flow_state import FlowStateError
from agent.validate_evidence import ReviewInput, check_evidence
from tests.flow_fixture import analysis, plan, research


def review_input(text: str = "실행했다.") -> ReviewInput:
    source = UserProvidedSource(
        id="s1",
        kind="user_provided",
        title="공고",
        checked_at=datetime.now(UTC),
        excerpt="검증 업무",
        url=None,
    )
    report = research().model_copy(
        update={
            "sources": (source,),
            "job_requirements": (JobRequirement(id="j1", text="검증 업무", source_ids=("s1",)),),
        }
    )
    factual = plan().claims[0].model_copy(update={"text": text})
    opinion = PlanClaim(
        id="c2",
        text="저는 " + "검증을 중시하며 " * 50 + "배우려 합니다.",
        kind="future_plan",
        evidence_ids=(),
    )
    body = text + " " + opinion.text
    padding = " " * (900 - len(body))
    body += padding
    outline = plan().model_copy(
        update={
            "claims": (factual, opinion),
            "paragraphs": (plan().paragraphs[0].model_copy(update={"claim_ids": ("c1", "c2")}),),
        }
    )
    draft = DraftEnvelope(
        version=1,
        plan_version=1,
        draft=body,
        paragraphs=(ParagraphSpan(paragraph_id="p1", start=0, end=len(body)),),
        claim_map=outline.claims,
        fit_reasons=(
            FitReason(
                experience_evidence_ids=("e1",),
                job_requirement_ids=("j1",),
                reason="실행 경험을 검증 업무에 연결합니다.",
            ),
        ),
    )
    return ReviewInput(
        request_id=uuid4(),
        request=DraftRequest(company="회사", role="검증", question="경험", experience="실행했다."),
        analysis=analysis(),
        research=report,
        plan=outline,
        draft=draft,
    )


def test_code_passes_when_exact_evidence_and_context_match() -> None:
    # Given
    context = review_input()
    # When
    result = check_evidence(context)
    # Then
    assert result.all_passed
    assert len(result.criteria) == 7


@pytest.mark.parametrize(
    "text",
    ["성과 90%를 달성했다.", "2024년에 실행했다.", "실행해서 매출을 높였다.", "회사가 실행했다."],
)
def test_fact_failure_when_claim_invents_achievement_time_cause_or_actor(text: str) -> None:
    # Given
    context = review_input(text)
    # When
    result = check_evidence(context)
    # Then
    issue = next(item for item in result.issues if item.criterion_id == "user_factuality")
    assert issue.scope == "plan_or_claim"
    assert context.draft.draft[issue.start : issue.end] == text
    assert issue.claim_ids == ("c1",)


@pytest.mark.parametrize("length", [800, 801, 1000, 1001])
def test_length_uses_code_points_when_at_boundaries(length: int) -> None:
    # Given
    context = review_input()
    body = context.draft.draft.rstrip().ljust(length)
    draft = context.draft.model_copy(
        update={
            "draft": body,
            "paragraphs": (ParagraphSpan(paragraph_id="p1", start=0, end=length),),
        }
    )
    # When
    result = check_evidence(context.model_copy(update={"draft": draft}))
    # Then
    assert next(c.passed for c in result.criteria if c.criterion_id == "length") == (
        801 <= length <= 1000
    )


@pytest.mark.parametrize("missing", [True, False])
def test_job_failure_requires_connection_but_not_optional_posting(*, missing: bool) -> None:
    # Given
    context = review_input()
    context = context.model_copy(
        update={"draft": context.draft.model_copy(update={"fit_reasons": ()})}
    )
    if missing:
        context = context.model_copy(
            update={"research": context.research.model_copy(update={"job_requirements": ()})}
        )
    # When
    result = check_evidence(context)
    # Then
    issue = next(item for item in result.issues if item.criterion_id == "job_fit")
    assert issue.scope == "plan_or_claim"
    assert issue.missing_fields == ()


@pytest.mark.parametrize("attack", ["unmapped", "disguised", "company", "source_type"])
def test_evidence_failure_when_provenance_is_broken(attack: str) -> None:
    # Given
    context = review_input("매출 90%를 달성했다.")
    claim = context.draft.claim_map[0]
    if attack == "source_type":
        claim = claim.model_copy(update={"evidence_ids": ("j1",)})
    if attack == "disguised":
        claim = claim.model_copy(update={"kind": "interpretation"})
    if attack == "company":
        claim = claim.model_copy(update={"kind": "company_fact", "evidence_ids": ("j1",)})
    claims = (claim, context.draft.claim_map[1])
    outline = context.plan.model_copy(
        update={"claims": claims, "selected_evidence_ids": ("e1", "j1")}
    )
    draft = context.draft.model_copy(update={"claim_map": claims})
    if attack == "unmapped":
        body = draft.draft.rstrip() + " 숨긴 사실이다."
        draft = draft.model_copy(
            update={
                "draft": body,
                "paragraphs": (ParagraphSpan(paragraph_id="p1", start=0, end=len(body)),),
            }
        )
    context = context.model_copy(update={"plan": outline, "draft": draft})
    # When / Then
    if attack == "source_type":
        with pytest.raises(FlowStateError):
            _ = check_evidence(context)
    else:
        result = check_evidence(context)
        criterion = {
            "unmapped": "contract_evidence",
            "disguised": "expression_kind",
            "company": "company_factuality",
        }[attack]
        assert any(item.criterion_id == criterion for item in result.issues)
