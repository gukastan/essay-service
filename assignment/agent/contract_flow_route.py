"""Typed control outcomes without implementing G's routing algorithm."""

from typing import Annotated, Literal

from pydantic import Field

from agent.contract_flow_evaluation import MissingField
from agent.contract_flow_plan import FlowText
from agent.contract_input import Contract

FlowRoute = Literal["H", "J", "D", "I"]


class ReadyTerminal(Contract):
    kind: Literal["ready"]
    route: Literal["H"]
    reason: Literal["all_criteria_passed"]


class MissingInputTerminal(Contract):
    kind: Literal["needs_input"]
    route: Literal["J"]
    reason: Literal["missing_required_information"]
    missing_fields: Annotated[tuple[MissingField, ...], Field(min_length=1, max_length=6)]
    questions: Annotated[tuple[FlowText, ...], Field(min_length=1, max_length=20)]
    reason_code: Literal[
        "COMPANY_AMBIGUOUS",
        "JOB_EVIDENCE_MISSING",
        "EXPERIENCE_INSUFFICIENT",
        "EVIDENCE_INSUFFICIENT",
    ]


class QualityTerminal(Contract):
    kind: Literal["quality_failure"]
    route: Literal["J"]
    reason: Literal["revision_limit", "invalid_plan"]
    code: Literal["QUALITY_CHECK_FAILED", "LENGTH_VALIDATION_FAILED"]


class OperationalTerminal(Contract):
    kind: Literal["operational_error"]
    code: Literal[
        "INVALID_INPUT",
        "CONFIG_ERROR",
        "MODEL_ERROR",
        "SEARCH_ERROR",
        "INVALID_RESPONSE",
        "TIMEOUT",
        "CANCELLED",
        "BUDGET_EXCEEDED",
    ]


TerminalReason = Annotated[
    ReadyTerminal | MissingInputTerminal | QualityTerminal | OperationalTerminal,
    Field(discriminator="kind"),
]
