"""Versioned draft envelopes with Unicode paragraph spans."""

from typing import Annotated, Self

from pydantic import Field, model_validator
from pydantic_core import PydanticCustomError

from agent.contract_evidence import FitReason
from agent.contract_flow_plan import FlowId, PlanClaim, Version, unique
from agent.contract_input import Contract, NormalizedText

Offset = Annotated[int, Field(strict=True, ge=0, le=4000)]


class ParagraphSpan(Contract):
    paragraph_id: FlowId
    start: Offset
    end: Offset

    @model_validator(mode="after")
    def check_order(self) -> Self:
        if self.end <= self.start:
            raise PydanticCustomError("span_order", "Span end must follow start")
        return self


class DraftEnvelope(Contract):
    version: Version
    plan_version: Version
    draft: Annotated[NormalizedText, Field(max_length=4000)]
    paragraphs: Annotated[tuple[ParagraphSpan, ...], Field(min_length=1, max_length=10)]
    claim_map: Annotated[tuple[PlanClaim, ...], Field(min_length=1, max_length=40)]
    fit_reasons: Annotated[tuple[FitReason, ...], Field(max_length=20)]

    @model_validator(mode="after")
    def check_spans(self) -> Self:
        unique(tuple(item.paragraph_id for item in self.paragraphs))
        unique(tuple(item.id for item in self.claim_map))
        cursor = 0
        for span in self.paragraphs:
            if span.start < cursor or span.end > len(self.draft):
                raise PydanticCustomError(
                    "draft_span", "Paragraph spans must be ordered and in bounds"
                )
            if self.draft[cursor : span.start].strip():
                raise PydanticCustomError("draft_coverage", "Paragraph spans must cover all text")
            cursor = span.end
        if self.draft[cursor:].strip():
            raise PydanticCustomError("draft_coverage", "Paragraph spans must cover all text")
        if any(claim.text not in self.draft for claim in self.claim_map):
            raise PydanticCustomError("draft_claim", "Claim text must occur in draft")
        return self
