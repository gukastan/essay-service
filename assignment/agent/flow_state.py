"""Context-bound checks for flow handoffs; semantic evaluation remains F's responsibility."""

from dataclasses import dataclass
from typing import Final, Literal, assert_never, final
from uuid import UUID

from agent.contract_evidence import Claim, evidence_matches
from agent.contract_flow_draft import DraftEnvelope
from agent.contract_flow_evaluation import Evaluation
from agent.contract_flow_plan import FlowAnalysisResult, WritingPlan
from agent.contract_input import DraftRequest
from agent.contract_results import ResearchResult

MIN_READY_CHARACTERS: Final = 801
MAX_READY_CHARACTERS: Final = 1000


@final
class FlowStateError(Exception):
    def __init__(
        self,
        code: Literal[
            "INVALID_REFERENCE",
            "INVALID_EVIDENCE",
            "SOURCE_TYPE_MISMATCH",
            "VERSION_MISMATCH",
            "PLAN_MISMATCH",
            "INVALID_RANGE",
            "FOREIGN_EVALUATION",
            "STALE_EVALUATION",
            "EVALUATION_FAILED",
            "INVALID_LENGTH",
        ],
    ) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class EvaluationBinding:
    request_id: UUID
    evaluation: Evaluation
    draft: DraftEnvelope
    plan: WritingPlan


def validate_analysis_context(analysis: FlowAnalysisResult, request: DraftRequest) -> None:
    if any(not evidence_matches(request.experience, item) for item in analysis.experience_evidence):
        raise FlowStateError("INVALID_EVIDENCE")


def _evidence_ids(
    analysis: FlowAnalysisResult, research: ResearchResult
) -> tuple[set[str], set[str]]:
    personal = {item.id for item in analysis.experience_evidence}
    company_items = (*research.company_facts, *research.job_requirements)
    company = {item.id for item in company_items}
    sources = {item.id for item in research.sources}
    if (
        personal & company
        or len(company) != len(company_items)
        or len(sources) != len(research.sources)
        or any(set(item.source_ids) - sources for item in company_items)
    ):
        raise FlowStateError("INVALID_REFERENCE")
    return personal, company


def _validate_claim(claim: Claim, personal: set[str], company: set[str]) -> None:
    references = set(claim.evidence_ids)
    if references - (personal | company):
        raise FlowStateError("INVALID_REFERENCE")
    match claim.kind:
        case "user_fact":
            if not references <= personal:
                raise FlowStateError("SOURCE_TYPE_MISMATCH")
        case "company_fact":
            if not references <= company:
                raise FlowStateError("SOURCE_TYPE_MISMATCH")
        case "interpretation" | "future_plan":
            return
        case _:
            assert_never(claim.kind)


def validate_plan_context(
    plan: WritingPlan, analysis: FlowAnalysisResult, research: ResearchResult
) -> None:
    personal, company = _evidence_ids(analysis, research)
    if set(plan.selected_evidence_ids) - (personal | company):
        raise FlowStateError("INVALID_REFERENCE")
    available = {item.id for item in analysis.requirements}
    covered = {identifier for item in plan.paragraphs for identifier in item.requirement_ids}
    mandatory = {item.id for item in analysis.requirements if item.mandatory}
    if covered - available or mandatory - covered:
        raise FlowStateError("INVALID_REFERENCE")
    for claim in plan.claims:
        _validate_claim(claim, personal, company)


def _validate_draft_plan(draft: DraftEnvelope, plan: WritingPlan) -> None:
    if draft.plan_version != plan.version:
        raise FlowStateError("VERSION_MISMATCH")
    if tuple(item.paragraph_id for item in draft.paragraphs) != tuple(
        item.id for item in plan.paragraphs
    ):
        raise FlowStateError("PLAN_MISMATCH")
    planned = {item.id: item for item in plan.claims}
    if {item.id for item in draft.claim_map} != planned.keys():
        raise FlowStateError("PLAN_MISMATCH")
    for claim in draft.claim_map:
        original = planned[claim.id]
        if claim.kind != original.kind or claim.evidence_ids != original.evidence_ids:
            raise FlowStateError("PLAN_MISMATCH")
    spans = {item.paragraph_id: item for item in draft.paragraphs}
    claims = {item.id: item for item in draft.claim_map}
    for paragraph in plan.paragraphs:
        span = spans[paragraph.id]
        if any(
            claims[identifier].text not in draft.draft[span.start : span.end]
            for identifier in paragraph.claim_ids
        ):
            raise FlowStateError("PLAN_MISMATCH")


def validate_draft_context(
    draft: DraftEnvelope,
    plan: WritingPlan,
    analysis: FlowAnalysisResult,
    research: ResearchResult,
) -> None:
    validate_plan_context(plan, analysis, research)
    _validate_draft_plan(draft, plan)
    personal, company = _evidence_ids(analysis, research)
    jobs = {item.id for item in research.job_requirements}
    for claim in draft.claim_map:
        _validate_claim(claim, personal, company)
    if any(
        set(item.experience_evidence_ids) - personal or set(item.job_requirement_ids) - jobs
        for item in draft.fit_reasons
    ):
        raise FlowStateError("INVALID_REFERENCE")


def validate_evaluation_context(
    evaluation: Evaluation, draft: DraftEnvelope, plan: WritingPlan
) -> None:
    _validate_draft_plan(draft, plan)
    if evaluation.draft_version != draft.version or evaluation.plan_version != plan.version:
        raise FlowStateError("VERSION_MISMATCH")
    claims = {item.id: item for item in draft.claim_map}
    paragraphs = {item.paragraph_id: item for item in draft.paragraphs}
    for issue in evaluation.issues:
        if set(issue.claim_ids) - claims.keys() or set(issue.paragraph_ids) - paragraphs.keys():
            raise FlowStateError("INVALID_REFERENCE")
        if issue.start is not None and issue.end is not None:
            if not 0 <= issue.start < issue.end <= len(draft.draft):
                raise FlowStateError("INVALID_RANGE")
            if any(
                not _claim_overlaps(draft.draft, claims[identifier].text, issue.start, issue.end)
                for identifier in issue.claim_ids
            ):
                raise FlowStateError("INVALID_RANGE")
            if issue.paragraph_ids and not any(
                paragraphs[identifier].start <= issue.start
                and issue.end <= paragraphs[identifier].end
                for identifier in issue.paragraph_ids
            ):
                raise FlowStateError("INVALID_RANGE")


def _claim_overlaps(text: str, claim: str, start: int, end: int) -> bool:
    position = text.find(claim)
    while position != -1:
        if position < end and start < position + len(claim):
            return True
        position = text.find(claim, position + 1)
    return False


def bind_evaluation(
    request_id: UUID, evaluation: Evaluation, draft: DraftEnvelope, plan: WritingPlan
) -> EvaluationBinding:
    """Bind at F's invocation boundary using the captured request, draft, and plan."""
    validate_evaluation_context(evaluation, draft, plan)
    return EvaluationBinding(request_id, evaluation, draft, plan)


def require_ready_evaluation(
    binding: EvaluationBinding, request_id: UUID, draft: DraftEnvelope, plan: WritingPlan
) -> None:
    """Reject a pass reused across requests, versions, or same-version content changes."""
    if binding.request_id != request_id:
        raise FlowStateError("FOREIGN_EVALUATION")
    if binding.draft != draft or binding.plan != plan:
        raise FlowStateError("STALE_EVALUATION")
    validate_evaluation_context(binding.evaluation, draft, plan)
    if not MIN_READY_CHARACTERS <= len(draft.draft) <= MAX_READY_CHARACTERS:
        raise FlowStateError("INVALID_LENGTH")
    if not all(item.passed for item in binding.evaluation.criteria):
        raise FlowStateError("EVALUATION_FAILED")
