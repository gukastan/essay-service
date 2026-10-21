"""Role results and final response variants; no business pipeline is implemented here."""

from typing import Annotated, Literal, Self
from uuid import UUID

from pydantic import BeforeValidator, Field, JsonValue, TypeAdapter, model_validator
from pydantic_core import PydanticCustomError

from agent.contract_evidence import (
    Claim,
    CompanyFact,
    ExperienceEvidence,
    FitReason,
    JobRequirement,
    ReviewIssue,
    Source,
)
from agent.contract_flow_evaluation import CriterionId, MissingField
from agent.contract_input import Contract, NormalizedText, Text, count_characters


class ResearchResult(Contract):
    resolved_company: Text | None
    sources: tuple[Source, ...]
    company_facts: tuple[CompanyFact, ...]
    job_requirements: tuple[JobRequirement, ...]
    gaps: tuple[Text, ...]


class QuestionRequirement(Contract):
    id: Text
    text: Text


class AnalysisResult(Contract):
    question_requirements: tuple[QuestionRequirement, ...]
    experience_evidence: tuple[ExperienceEvidence, ...]
    gaps: tuple[Text, ...]


class WriterResult(Contract):
    draft: NormalizedText
    claim_map: tuple[Claim, ...]
    fit_reasons: tuple[FitReason, ...]


class ReviewResult(Contract):
    verdict: Literal["pass", "revise", "needs_input"]
    issues: tuple[ReviewIssue, ...]
    revision_instructions: tuple[Text, ...]

    @model_validator(mode="after")
    def check_pass(self) -> Self:
        if self.verdict == "pass" and self.issues:
            raise PydanticCustomError("review_pass", "Passing review cannot contain issues")
        return self


def strict_revision(value: JsonValue) -> JsonValue:
    if type(value) is not int:
        raise PydanticCustomError("revision_type", "Revision count must be an integer")
    return value


class Usage(Contract):
    model_calls: Annotated[int, Field(strict=True, ge=0, le=6)]
    revision_count: Annotated[Literal[0, 1], BeforeValidator(strict_revision)]


class Evidence(Contract):
    company_facts: tuple[CompanyFact, ...]
    job_requirements: tuple[JobRequirement, ...]
    experience_evidence: tuple[ExperienceEvidence, ...]
    claim_map: tuple[Claim, ...]
    fit_reasons: tuple[FitReason, ...]


class ReadyResponse(Contract):
    status: Literal["ready"]
    request_id: UUID
    draft: NormalizedText
    character_count: Annotated[int, Field(strict=True, ge=801, le=1000)]
    sources: tuple[Source, ...]
    evidence: Evidence
    review_summary: Literal["생성 당시 검토 통과"]
    usage: Usage

    @model_validator(mode="after")
    def check_count(self) -> Self:
        if count_characters(self.draft) != self.character_count:
            raise PydanticCustomError("character_count", "Draft count does not match")
        return self


class ReviewNotice(Contract):
    criterion_id: CriterionId
    reason: Text
    instruction: Text
    missing_fields: tuple[MissingField, ...] = ()


class ReviewNeededResponse(Contract):
    status: Literal["review_needed"]
    request_id: UUID
    draft: NormalizedText
    character_count: Annotated[int, Field(strict=True, ge=1, le=4000)]
    sources: tuple[Source, ...]
    evidence: Evidence
    review_summary: Literal["생성 당시 기준 미충족 · 직접 검토 필요"]
    review_issues: Annotated[tuple[ReviewNotice, ...], Field(min_length=1, max_length=40)]
    usage: Usage

    @model_validator(mode="after")
    def check_count(self) -> Self:
        if count_characters(self.draft) != self.character_count:
            raise PydanticCustomError("character_count", "Draft count does not match")
        return self


class NeedsInputResponse(Contract):
    status: Literal["needs_input"]
    request_id: UUID
    message: Text
    missing_fields: Annotated[
        tuple[
            Literal[
                "company",
                "role",
                "question",
                "experience",
                "jobPostingUrl",
                "jobPostingText",
            ],
            ...,
        ],
        Field(min_length=1),
    ]
    questions: Annotated[tuple[Text, ...], Field(min_length=1)]
    reason_code: Literal[
        "COMPANY_AMBIGUOUS",
        "JOB_EVIDENCE_MISSING",
        "EXPERIENCE_INSUFFICIENT",
        "EVIDENCE_INSUFFICIENT",
    ]


class ErrorResponse(Contract):
    status: Literal["error"]
    request_id: UUID
    message: Text
    code: Literal[
        "INVALID_INPUT",
        "V2_DISABLED",
        "CONFIG_ERROR",
        "MODEL_ERROR",
        "SEARCH_ERROR",
        "INVALID_RESPONSE",
        "TIMEOUT",
        "CANCELLED",
        "BUDGET_EXCEEDED",
    ]


DraftResponse = TypeAdapter(
    Annotated[
        ReadyResponse | ReviewNeededResponse | NeedsInputResponse | ErrorResponse,
        Field(discriminator="status"),
    ]
)
