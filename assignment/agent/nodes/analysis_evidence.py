"""C joins independently completed B and verified research without new calls."""

from dataclasses import dataclass
from typing import assert_never
from uuid import UUID

from agent.contracts import (
    DraftRequest,
    ErrorResponse,
    FlowAnalysisResult,
    NeedsInputResponse,
    ResearchResult,
)
from agent.flow_state import FlowStateError
from agent.nodes.analyze import AnalysisOutcome, experience_gap, validate_personal_analysis
from agent.nodes.research import ResearchOutcome


@dataclass(frozen=True, slots=True)
class EvidenceBundle:
    analysis: FlowAnalysisResult
    research: ResearchResult


@dataclass(frozen=True, slots=True)
class AnalysisJoin:
    request: DraftRequest
    request_id: UUID

    def run(
        self, analysis: AnalysisOutcome | None, research: ResearchOutcome | None
    ) -> EvidenceBundle | NeedsInputResponse | ErrorResponse | None:
        """None means pending; only EvidenceBundle permits D.

        ResearchSuccess must originate in the source-verifying ResearchNode.
        This join checks references, not network source authenticity.
        """
        if analysis is not None:
            match analysis.status:
                case "needs_input":
                    return analysis
                case "analysis-success":
                    validate_personal_analysis(analysis.result, self.request)
                case _:
                    assert_never(analysis.status)
        if research is not None:
            match research.status:
                case "needs_input" | "error":
                    return research
                case "research-success":
                    pass
                case _:
                    assert_never(research.status)
        if analysis is None or research is None:
            return None
        gap = experience_gap(analysis.result, self.request_id)
        if gap is not None:
            return gap
        result = research.result
        validate_research_binding(analysis.result, result)
        return EvidenceBundle(analysis.result, result)


def validate_research_binding(analysis: FlowAnalysisResult, result: ResearchResult) -> None:
    personal = {item.id for item in analysis.experience_evidence}
    facts = (*result.company_facts, *result.job_requirements)
    ids = {item.id for item in facts}
    sources = {item.id for item in result.sources}
    if (
        personal & ids
        or len(ids) != len(facts)
        or len(sources) != len(result.sources)
        or any(set(item.source_ids) - sources for item in facts)
    ):
        raise FlowStateError("INVALID_REFERENCE")
