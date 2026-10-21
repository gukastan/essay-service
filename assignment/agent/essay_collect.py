"""Parallel B/C evidence collection with one join and early cancellation."""

from dataclasses import dataclass

import anyio

from agent.budget import ExecutionBudgetError
from agent.contracts import (
    ErrorResponse,
    MissingInputTerminal,
    NeedsInputResponse,
    OperationalTerminal,
)
from agent.deps import RequestContext, WorkflowDeps
from agent.essay_route import error_result
from agent.nodes.analysis_evidence import AnalysisJoin, EvidenceBundle
from agent.nodes.analyze import AnalysisOutcome, AnalyzeNode
from agent.nodes.research import ResearchNode, ResearchOutcome
from agent.providers import ProviderError
from agent.state import WorkflowState


def terminal_for(
    outcome: NeedsInputResponse | ErrorResponse,
) -> MissingInputTerminal | OperationalTerminal:
    match outcome:
        case NeedsInputResponse():
            return MissingInputTerminal(
                kind="needs_input",
                route="J",
                reason="missing_required_information",
                missing_fields=outcome.missing_fields,
                questions=outcome.questions,
                reason_code=outcome.reason_code,
            )
        case ErrorResponse():
            return OperationalTerminal.model_validate(
                {"kind": "operational_error", "code": outcome.code}
            )


@dataclass(frozen=True, slots=True)
class ContextCollector:
    deps: WorkflowDeps
    context: RequestContext

    async def run(self, _state: WorkflowState) -> WorkflowState:
        analysis: AnalysisOutcome | None = None
        research: ResearchOutcome | None = None
        failures: list[ErrorResponse] = []
        join = AnalysisJoin(self.context.input_snapshot, self.context.request_id)

        async with anyio.create_task_group() as tasks:

            async def analyze() -> None:
                nonlocal analysis
                try:
                    analysis = await AnalyzeNode(self.deps.model).run(
                        self.context.input_snapshot,
                        self.context.budget,
                        self.context.request_id,
                    )
                except (ProviderError, ExecutionBudgetError) as error:
                    failures.append(error_result(self.context, error.code))
                if failures or isinstance(join.run(analysis, research), NeedsInputResponse):
                    tasks.cancel_scope.cancel()

            async def investigate() -> None:
                nonlocal research
                research = await ResearchNode(self.deps.mcp).run(
                    self.context.input_snapshot.research_input(),
                    self.context.budget,
                    self.context.request_id,
                )
                if research.status == "error" or isinstance(
                    join.run(analysis, research), NeedsInputResponse
                ):
                    tasks.cancel_scope.cancel()

            _ = tasks.start_soon(analyze)
            _ = tasks.start_soon(investigate)

        if failures:
            failure = failures[0]
            return WorkflowState(
                outcome=failure,
                terminal_reason=terminal_for(failure),
                usage=self.context.budget.snapshot(),
            )
        joined = join.run(analysis, research)
        match joined:
            case EvidenceBundle(analysis=personal, research=company):
                return WorkflowState(
                    flow_analysis=personal,
                    research=company,
                    usage=self.context.budget.snapshot(),
                )
            case NeedsInputResponse() | ErrorResponse():
                return WorkflowState(
                    outcome=joined,
                    terminal_reason=terminal_for(joined),
                    usage=self.context.budget.snapshot(),
                )
            case None:
                raise ProviderError("INVALID_RESPONSE")
