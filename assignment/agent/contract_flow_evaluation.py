"""Complete mandatory criterion results; absent checks never imply success."""

from typing import Annotated, Final, Literal, Self

from pydantic import Field, StrictBool, model_validator
from pydantic_core import PydanticCustomError

from agent.contract_flow_draft import Offset
from agent.contract_flow_plan import FlowId, FlowText, Ids, Version, unique
from agent.contract_input import Contract

CriterionId = Literal[
    "contract_evidence",
    "user_factuality",
    "company_factuality",
    "question_coverage",
    "job_fit",
    "length",
    "expression_kind",
]
MANDATORY_CRITERIA: Final[tuple[CriterionId, ...]] = (
    "contract_evidence",
    "user_factuality",
    "company_factuality",
    "question_coverage",
    "job_fit",
    "length",
    "expression_kind",
)
MissingField = Literal[
    "company", "role", "question", "experience", "jobPostingUrl", "jobPostingText"
]
IssueScope = Literal["missing_info", "plan_or_claim", "wording"]


class CriterionResult(Contract):
    criterion_id: CriterionId
    passed: StrictBool


class EvaluationIssue(Contract):
    id: FlowId
    criterion_id: CriterionId
    claim_ids: Ids
    paragraph_ids: Ids
    start: Offset | None
    end: Offset | None
    reason: FlowText
    scope: IssueScope
    instruction: FlowText
    missing_fields: Annotated[tuple[MissingField, ...], Field(max_length=6)]

    @model_validator(mode="after")
    def check_scope(self) -> Self:
        unique(self.claim_ids)
        unique(self.paragraph_ids)
        unique(self.missing_fields)
        if (self.start is None) != (self.end is None):
            raise PydanticCustomError("issue_span", "Both span boundaries are required together")
        if self.start is not None and self.end is not None and self.start >= self.end:
            raise PydanticCustomError("issue_span", "Issue end must follow start")
        if bool(self.missing_fields) != (self.scope == "missing_info"):
            raise PydanticCustomError("missing_fields", "Missing fields require missing_info scope")
        if self.scope == "wording" and (
            self.start is None or not (self.claim_ids or self.paragraph_ids)
        ):
            raise PydanticCustomError("wording_scope", "Wording issues require an anchored span")
        return self


class Evaluation(Contract):
    draft_version: Version
    plan_version: Version
    criteria: Annotated[tuple[CriterionResult, ...], Field(min_length=7, max_length=7)]
    issues: Annotated[tuple[EvaluationIssue, ...], Field(max_length=40)]

    @model_validator(mode="after")
    def check_coverage(self) -> Self:
        unique(tuple(item.criterion_id for item in self.criteria))
        unique(tuple(item.id for item in self.issues))
        if {item.criterion_id for item in self.criteria} != set(MANDATORY_CRITERIA):
            raise PydanticCustomError(
                "evaluation_coverage", "Every mandatory criterion is required"
            )
        failed = {item.criterion_id for item in self.criteria if not item.passed}
        if failed != {item.criterion_id for item in self.issues}:
            raise PydanticCustomError(
                "evaluation_issues", "Issues must cover exactly failed criteria"
            )
        return self

    @property
    def all_passed(self) -> bool:
        return all(item.passed for item in self.criteria)
