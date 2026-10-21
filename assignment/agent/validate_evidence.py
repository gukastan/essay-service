"""Deterministic F checks; semantic adequacy is additionally reviewed by the model."""

import re
from typing import assert_never
from uuid import UUID

from agent.contract_flow_evaluation import CriterionId, MissingField
from agent.contract_input import Contract
from agent.contracts import (
    MANDATORY_CRITERIA,
    CriterionResult,
    DraftEnvelope,
    DraftRequest,
    Evaluation,
    EvaluationIssue,
    FlowAnalysisResult,
    PlanClaim,
    ResearchResult,
    WritingPlan,
)
from agent.flow_state import (
    MAX_READY_CHARACTERS,
    MIN_READY_CHARACTERS,
    validate_analysis_context,
    validate_draft_context,
)


class ReviewInput(Contract):
    request_id: UUID
    request: DraftRequest
    analysis: FlowAnalysisResult
    research: ResearchResult
    plan: WritingPlan
    draft: DraftEnvelope


def issue_for_claim(
    context: ReviewInput,
    claim: PlanClaim,
    criterion: CriterionId,
) -> EvaluationIssue:
    start = context.draft.draft.index(claim.text)
    return EvaluationIssue(
        id=f"code-{criterion}-{claim.id}",
        criterion_id=criterion,
        claim_ids=(claim.id,),
        paragraph_ids=(),
        start=start,
        end=start + len(claim.text),
        reason="주장 종류 또는 원문 사실·순서·시점·인과 관계가 근거와 일치하지 않습니다.",
        scope="plan_or_claim",
        instruction="원문 전체 문장을 원래 순서로 복원하고 주장과 근거를 다시 연결하세요.",
        missing_fields=(),
    )


def general_issue(
    criterion: CriterionId,
    reason: str,
    missing: tuple[MissingField, ...] = (),
) -> EvaluationIssue:
    return EvaluationIssue(
        id=f"code-{criterion}",
        criterion_id=criterion,
        claim_ids=(),
        paragraph_ids=(),
        start=None,
        end=None,
        reason=reason,
        scope="missing_info" if missing else "plan_or_claim",
        instruction="표시한 부족 정보를 보완하세요."
        if missing
        else "전체 계획과 해당 기준을 검토하여 수정하세요.",
        missing_fields=missing,
    )


def evaluation_from_issues(
    context: ReviewInput,
    issues: tuple[EvaluationIssue, ...],
) -> Evaluation:
    failed = {item.criterion_id for item in issues}
    return Evaluation(
        draft_version=context.draft.version,
        plan_version=context.plan.version,
        criteria=tuple(
            CriterionResult(criterion_id=item, passed=item not in failed)
            for item in MANDATORY_CRITERIA
        ),
        issues=issues,
    )


def check_evidence(context: ReviewInput) -> Evaluation:
    """Reject invalid contracts, then collect non-overridable evidence failures."""
    validate_analysis_context(context.analysis, context.request)
    validate_draft_context(context.draft, context.plan, context.analysis, context.research)
    personal = {item.id: item for item in context.analysis.experience_evidence}
    company = {
        item.id: item
        for item in (*context.research.company_facts, *context.research.job_requirements)
    }
    sources = {item.id: item for item in context.research.sources}
    sentences = {
        (m.start(), m.end())
        for m in re.finditer(
            r"\S(?:.*?\S)?[.!?\u3002\uff01\uff1f](?=\s|$)",
            context.request.experience,
            re.DOTALL,
        )
    }
    issues: list[EvaluationIssue] = []
    cursor = source_end = 0
    coverage = True
    for claim in context.draft.claim_map:
        start = context.draft.draft.find(claim.text, cursor)
        coverage &= start >= cursor and not context.draft.draft[cursor:start].strip()
        cursor = max(cursor, start + len(claim.text))
        match claim.kind:
            case "user_fact":
                originals = [personal[key] for key in claim.evidence_ids]
                valid = len(originals) == 1 and claim.text == originals[0].quote
                valid &= all(
                    (item.start, item.end) in sentences and item.start >= source_end
                    for item in originals
                )
                if not valid:
                    issues.append(issue_for_claim(context, claim, "user_factuality"))
                source_end = max(item.end for item in originals)
            case "company_fact":
                originals = [company[key] for key in claim.evidence_ids]
                valid = len(originals) == 1 and claim.text == originals[0].text
                valid &= all(
                    item.text in sources[key].excerpt
                    for item in originals
                    for key in item.source_ids
                )
                if not valid:
                    issues.append(issue_for_claim(context, claim, "company_factuality"))
            case "interpretation" | "future_plan":
                if re.search(r"\d|했[다습]|였[다습]|었[다습]|달성|수상|achieved|won", claim.text):
                    issues.append(issue_for_claim(context, claim, "expression_kind"))
            case _:
                assert_never(claim.kind)
    if not coverage or context.draft.draft[cursor:].strip():
        issues.append(
            general_issue("contract_evidence", "본문에 주장 지도와 연결되지 않은 문장이 있습니다.")
        )
    issues.extend(check_available_context(context))
    return evaluation_from_issues(context, tuple(issues))


def check_available_context(context: ReviewInput) -> tuple[EvaluationIssue, ...]:
    issues: list[EvaluationIssue] = []
    if not MIN_READY_CHARACTERS <= len(context.draft.draft) <= MAX_READY_CHARACTERS:
        issues.append(general_issue("length", "본문은 공백 포함 801~1000 코드 포인트여야 합니다."))
    if not context.analysis.experience_evidence:
        issues.append(
            general_issue("user_factuality", "개인 경험 근거가 없습니다.", ("experience",))
        )
    if context.research.resolved_company is None:
        issues.append(
            general_issue("company_factuality", "지원 기업을 식별할 수 없습니다.", ("company",))
        )
    if not context.research.job_requirements:
        issues.append(general_issue("job_fit", "직무 근거가 없습니다.", ("jobPostingText",)))
    elif not context.draft.fit_reasons:
        issues.append(general_issue("job_fit", "개인 경험과 직무 요건 연결이 없습니다."))
    return tuple(issues)
