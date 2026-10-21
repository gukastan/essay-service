"""LangGraph schemas with protected context and monotonic revision reducer."""

from typing import Annotated, Literal, TypedDict, final
from uuid import UUID, uuid4

from agent.budget import BudgetSnapshot, ExecutionBudget
from agent.contract_input import Contract
from agent.contracts import (
    AnalysisResult,
    Claim,
    DraftEnvelope,
    DraftRequest,
    ErrorResponse,
    FitReason,
    FlowAnalysisResult,
    FlowRoute,
    NeedsInputResponse,
    ReadyResponse,
    ResearchResult,
    ReviewNeededResponse,
    ReviewResult,
    TerminalReason,
    WritingPlan,
)
from agent.flow_state import EvaluationBinding


@final
class WorkflowStateError(Exception):
    def __init__(
        self, code: Literal["IMMUTABLE_CONTEXT", "REVISION_DECREASE", "INVALID_REVISION"]
    ) -> None:
        self.code = code
        super().__init__(code)


def write_once[T](current: T | None, incoming: T) -> T:
    if current is not None:
        raise WorkflowStateError("IMMUTABLE_CONTEXT")
    return incoming


def revision_reducer(current: Literal[0, 1], incoming: int) -> Literal[0, 1]:
    if type(incoming) is not int or incoming not in (0, 1):
        raise WorkflowStateError("INVALID_REVISION")
    if current == 1 and incoming != 1:
        raise WorkflowStateError("REVISION_DECREASE")
    return 1 if incoming == 1 else 0


class DeterministicChecks(Contract):
    character_count: int
    length_valid: bool
    evidence_valid: bool
    issues: tuple[str, ...]


class WorkflowState(TypedDict, total=False):
    request_id: Annotated[UUID | None, write_once]
    input_snapshot: Annotated[DraftRequest | None, write_once]
    deadline: Annotated[float | None, write_once]
    research: ResearchResult | None
    analysis: AnalysisResult | None
    flow_analysis: FlowAnalysisResult | None
    plan: WritingPlan | None
    draft_envelope: DraftEnvelope | None
    evaluation: EvaluationBinding | None
    route: FlowRoute | None
    terminal_reason: TerminalReason | None
    draft: str | None
    claim_map: tuple[Claim, ...]
    fit_reasons: tuple[FitReason, ...]
    deterministic_checks: DeterministicChecks | None
    review: ReviewResult | None
    revision_count: Annotated[Literal[0, 1], revision_reducer]
    usage: BudgetSnapshot
    outcome: ReadyResponse | ReviewNeededResponse | NeedsInputResponse | ErrorResponse | None


def initial_state(
    input: DraftRequest,
    budget: ExecutionBudget,
    request_id: UUID | None = None,
) -> WorkflowState:
    return WorkflowState(
        request_id=request_id or uuid4(),
        input_snapshot=input,
        deadline=budget.deadline,
        research=None,
        analysis=None,
        flow_analysis=None,
        plan=None,
        draft_envelope=None,
        evaluation=None,
        route=None,
        terminal_reason=None,
        draft=None,
        claim_map=(),
        fit_reasons=(),
        deterministic_checks=None,
        review=None,
        revision_count=budget.snapshot().revision_count,
        usage=budget.snapshot(),
        outcome=None,
    )
