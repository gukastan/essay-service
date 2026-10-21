"""Source, evidence, claim and review contracts; offsets are Unicode code points."""

from typing import Annotated, Literal, Self

from pydantic import AwareDatetime, Field, model_validator
from pydantic_core import PydanticCustomError

from agent.contract_input import Contract, HttpUrl, NormalizedText, Text, normalize_text


class SourceBase(Contract):
    id: Text
    title: Text
    checked_at: AwareDatetime
    published_at: Text | None = None
    closing_at: Text | None = None
    excerpt: Text


class OfficialSource(SourceBase):
    kind: Literal["official"]
    url: HttpUrl


class UserProvidedSource(SourceBase):
    kind: Literal["user_provided"]
    url: HttpUrl | None = None


Source = Annotated[OfficialSource | UserProvidedSource, Field(discriminator="kind")]
NonemptyIds = Annotated[tuple[Text, ...], Field(min_length=1)]


class CompanyFact(Contract):
    id: Text
    text: Text
    source_ids: NonemptyIds


class JobRequirement(Contract):
    id: Text
    text: Text
    source_ids: NonemptyIds


class ExperienceEvidence(Contract):
    id: Text
    quote: NormalizedText
    start: Annotated[int, Field(strict=True, ge=0)]
    end: Annotated[int, Field(strict=True, gt=0)]
    category: Literal["action", "result", "learning", "context"]

    @model_validator(mode="after")
    def check_offsets(self) -> Self:
        if self.end <= self.start:
            raise PydanticCustomError("offset_order", "End must follow start")
        return self


def evidence_matches(experience: str, evidence: ExperienceEvidence) -> bool:
    """Check exact LF-normalized source span without UTF-16 interpretation."""
    normalized = normalize_text(experience)
    return 0 <= evidence.start < evidence.end <= len(normalized) and (
        normalized[evidence.start : evidence.end] == evidence.quote
    )


class Claim(Contract):
    id: Text
    text: Text
    kind: Literal["user_fact", "company_fact", "interpretation", "future_plan"]
    evidence_ids: tuple[Text, ...]

    @model_validator(mode="after")
    def check_fact_evidence(self) -> Self:
        if self.kind in {"user_fact", "company_fact"} and not self.evidence_ids:
            raise PydanticCustomError("fact_evidence", "Facts require evidence identifiers")
        return self


class FitReason(Contract):
    experience_evidence_ids: NonemptyIds
    job_requirement_ids: tuple[Text, ...]
    reason: Text


class ReviewIssue(Contract):
    code: Text
    claim_ids: tuple[Text, ...]
    reason: Text
    action: Literal["revise", "needs_input"]
