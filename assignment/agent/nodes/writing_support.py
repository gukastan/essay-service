"""Writing boundaries shared by D/E/I; semantic review remains F's responsibility."""

import re
from dataclasses import dataclass
from typing import Literal, assert_never, final

from agent.budget import ExecutionBudget, RevisionReservation
from agent.contracts import DraftEnvelope, DraftRequest, FlowAnalysisResult, ResearchResult
from agent.flow_state import (
    EvaluationBinding,
    validate_analysis_context,
    validate_evaluation_context,
)
from agent.state import WorkflowState


@final
class WritingError(Exception):
    def __init__(
        self,
        code: Literal[
            "MISSING_CONTEXT",
            "MISSING_EVIDENCE",
            "INVALID_SENTENCE",
            "FACT_CHANGED",
            "UNMAPPED_TEXT",
            "INVALID_REVISION",
            "STALE_EVALUATION",
            "INVALID_PATCH",
        ],
    ) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class WritingContext:
    request: DraftRequest
    analysis: FlowAnalysisResult
    research: ResearchResult

    @classmethod
    def from_state(cls, state: WorkflowState) -> "WritingContext":
        request, analysis, research = (
            state.get("input_snapshot"),
            state.get("flow_analysis"),
            state.get("research"),
        )
        if request is None or analysis is None or research is None:
            raise WritingError("MISSING_CONTEXT")
        validate_analysis_context(analysis, request)
        return cls(request, analysis, research)


def sentence_spans(text: str) -> tuple[tuple[int, int], ...]:
    """Conservative sentence boundaries: terminal punctuation plus whitespace/end."""
    return tuple(
        (match.start(), match.end())
        for match in re.finditer(r"\S(?:.*?\S)?[.!?\u3002\uff01\uff1f](?=\s|$)", text, re.DOTALL)
    )


def require_reservation(
    budget: ExecutionBudget, reservation: RevisionReservation, route: Literal["D", "I"]
) -> None:
    snapshot = budget.snapshot()
    if (
        reservation.route != route
        or reservation.revision_count != 1
        or snapshot.revision_route != route
        or snapshot.revision_count != 1
    ):
        raise WritingError("INVALID_REVISION")


def current_evaluation(state: WorkflowState) -> EvaluationBinding:
    binding, draft, plan = state.get("evaluation"), state.get("draft_envelope"), state.get("plan")
    if binding is None or draft is None or plan is None:
        raise WritingError("MISSING_CONTEXT")
    if (
        binding.request_id != state.get("request_id")
        or binding.draft != draft
        or binding.plan != plan
    ):
        raise WritingError("STALE_EVALUATION")
    validate_evaluation_context(binding.evaluation, draft, plan)
    if draft.version != 1 or plan.version != 1:
        raise WritingError("INVALID_REVISION")
    return binding


def validate_writing_facts(draft: DraftEnvelope, context: WritingContext) -> None:
    """Require complete claim coverage and exact, ordered personal source sentences."""
    evidence = {item.id: item for item in context.analysis.experience_evidence}
    company = {
        item.id: item.text
        for item in (*context.research.company_facts, *context.research.job_requirements)
    }
    source_spans = sentence_spans(context.request.experience)
    validate_claim_coverage(draft)
    source_end = 0
    for claim in draft.claim_map:
        match claim.kind:
            case "user_fact":
                if len(claim.evidence_ids) != 1:
                    raise WritingError("FACT_CHANGED")
                original = evidence[claim.evidence_ids[0]]
                if (
                    claim.text != original.quote
                    or original.start < source_end
                    or (original.start, original.end) not in source_spans
                ):
                    raise WritingError("FACT_CHANGED")
                source_end = original.end
            case "company_fact":
                if len(claim.evidence_ids) != 1 or claim.text != company[claim.evidence_ids[0]]:
                    raise WritingError("FACT_CHANGED")
            case "interpretation" | "future_plan":
                if re.search(r"\d|했[다습]|였[다습]|었[다습]|achieved|won", claim.text):
                    raise WritingError("FACT_CHANGED")
            case _:
                assert_never(claim.kind)


def validate_claim_coverage(draft: DraftEnvelope) -> None:
    cursor = 0
    boundaries = sentence_spans(draft.draft)
    for claim in draft.claim_map:
        start = draft.draft.find(claim.text, cursor)
        if start < cursor or draft.draft[cursor:start].strip():
            raise WritingError("UNMAPPED_TEXT")
        cursor = start + len(claim.text)
        if claim.kind != "company_fact" and (start, cursor) not in boundaries:
            raise WritingError("INVALID_SENTENCE")
    if draft.draft[cursor:].strip():
        raise WritingError("UNMAPPED_TEXT")
