"""Bounded analysis and plan contracts for the code-owned D handoff."""

from typing import Annotated, Final, Self

from pydantic import Field, StrictBool, model_validator
from pydantic_core import PydanticCustomError

from agent.contract_evidence import Claim, ExperienceEvidence
from agent.contract_input import Contract, Text

FlowId = Annotated[Text, Field(max_length=80)]
FlowText = Annotated[Text, Field(max_length=500)]
Version = Annotated[int, Field(strict=True, ge=1, le=2)]
Ids = Annotated[tuple[FlowId, ...], Field(max_length=40)]
MIN_DRAFT_CHARACTERS: Final = 801
MAX_DRAFT_CHARACTERS: Final = 1000


def unique(values: tuple[str, ...]) -> None:
    if len(values) != len(set(values)):
        raise PydanticCustomError("duplicate_id", "Identifiers must be unique")


class FlowRequirement(Contract):
    id: FlowId
    text: FlowText
    mandatory: StrictBool
    check_condition: FlowText
    candidate_evidence_ids: Ids

    @model_validator(mode="after")
    def check_candidates(self) -> Self:
        unique(self.candidate_evidence_ids)
        return self


class FlowAnalysisResult(Contract):
    requirements: Annotated[tuple[FlowRequirement, ...], Field(min_length=1, max_length=20)]
    experience_evidence: Annotated[tuple[ExperienceEvidence, ...], Field(max_length=40)]
    gaps: Annotated[tuple[FlowText, ...], Field(max_length=20)]

    @model_validator(mode="after")
    def check_references(self) -> Self:
        unique(tuple(item.id for item in self.requirements))
        unique(tuple(item.id for item in self.experience_evidence))
        available = {item.id for item in self.experience_evidence}
        if any(set(item.candidate_evidence_ids) - available for item in self.requirements):
            raise PydanticCustomError("candidate_reference", "Candidate evidence must exist")
        return self


class PlanClaim(Claim):
    id: FlowId
    text: FlowText
    evidence_ids: Ids

    @model_validator(mode="after")
    def check_ids(self) -> Self:
        unique(self.evidence_ids)
        return self


class PlanParagraph(Contract):
    id: FlowId
    purpose: Annotated[Text, Field(max_length=200)]
    order: Annotated[int, Field(strict=True, ge=1, le=10)]
    target_characters: Annotated[int, Field(strict=True, ge=1, le=1000)]
    requirement_ids: Annotated[Ids, Field(min_length=1)]
    claim_ids: Annotated[Ids, Field(min_length=1)]

    @model_validator(mode="after")
    def check_ids(self) -> Self:
        unique(self.requirement_ids)
        unique(self.claim_ids)
        return self


class WritingPlan(Contract):
    version: Version
    selected_evidence_ids: Annotated[Ids, Field(min_length=1)]
    claims: Annotated[tuple[PlanClaim, ...], Field(min_length=1, max_length=40)]
    paragraphs: Annotated[tuple[PlanParagraph, ...], Field(min_length=1, max_length=10)]

    @model_validator(mode="after")
    def check_structure(self) -> Self:
        unique(self.selected_evidence_ids)
        unique(tuple(item.id for item in self.claims))
        unique(tuple(item.id for item in self.paragraphs))
        if tuple(item.order for item in self.paragraphs) != tuple(
            range(1, len(self.paragraphs) + 1)
        ):
            raise PydanticCustomError("paragraph_order", "Paragraph order must be contiguous")
        allocation = sum(item.target_characters for item in self.paragraphs)
        if not MIN_DRAFT_CHARACTERS <= allocation <= MAX_DRAFT_CHARACTERS:
            raise PydanticCustomError("plan_length", "Allocation must total 801 to 1000")
        selected = set(self.selected_evidence_ids)
        if any(set(item.evidence_ids) - selected for item in self.claims):
            raise PydanticCustomError("plan_evidence", "Claim evidence must be selected")
        referenced = {claim for paragraph in self.paragraphs for claim in paragraph.claim_ids}
        if referenced != {item.id for item in self.claims}:
            raise PydanticCustomError(
                "plan_claim", "Paragraph claims must cover exactly plan claims"
            )
        return self
