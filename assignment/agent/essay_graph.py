"""Request-local LangGraph assembly for the essay workflow."""

import time
from dataclasses import dataclass
from typing import Protocol

import anyio
from langgraph.graph import END, START, StateGraph
from pydantic import ValidationError

from agent.budget import ExecutionBudgetError, RevisionReservationError
from agent.contracts import (
    DraftRequest,
    ErrorResponse,
    NeedsInputResponse,
    ReadyResponse,
    ReviewNeededResponse,
)
from agent.deps import RequestContext, WorkflowDeps
from agent.essay_collect import ContextCollector
from agent.essay_route import decide, error_result, ready, review_needed
from agent.flow_state import FlowStateError
from agent.nodes.plan import build_plan
from agent.nodes.review import ReviewNode
from agent.nodes.revise import RevisionNode
from agent.nodes.write import WriteNode
from agent.nodes.writing_support import WritingError
from agent.providers import ProviderError
from agent.state import WorkflowState


def after_collect(state: WorkflowState) -> str:
    return "stop" if state.get("outcome") is not None else "plan"


def after_decide(state: WorkflowState) -> str:
    route = state.get("route")
    if route is None:
        raise ProviderError("INVALID_RESPONSE")
    return route


class CompiledEssayGraph(Protocol):
    async def ainvoke(self, input: WorkflowState) -> WorkflowState: ...


@dataclass(frozen=True, slots=True)
class EssayWorkflow:
    deps: WorkflowDeps

    def _graph(self, context: RequestContext) -> CompiledEssayGraph:
        graph = StateGraph(WorkflowState)
        collector = ContextCollector(self.deps, context)
        writer = WriteNode(self.deps.model)
        reviewer = ReviewNode(self.deps.model)
        reviser = RevisionNode(self.deps.model)

        async def write(state: WorkflowState) -> WorkflowState:
            return await writer.run(state, context.budget)

        async def review(state: WorkflowState) -> WorkflowState:
            return await reviewer.run(state, context.budget)

        async def replan(state: WorkflowState) -> WorkflowState:
            reservation = await context.budget.reserve_revision("D")
            return build_plan(state, context.budget, reservation)

        async def revise(state: WorkflowState) -> WorkflowState:
            reservation = await context.budget.reserve_revision("I")
            return await reviser.run(state, context.budget, reservation)

        _ = graph.add_node("collect", collector.run)
        _ = graph.add_node("plan", lambda state: build_plan(state, context.budget))
        _ = graph.add_node("write", write)
        _ = graph.add_node("review", review)
        _ = graph.add_node("decide", lambda state: decide(state, context))
        _ = graph.add_node("replan", replan)
        _ = graph.add_node("revise", revise)
        _ = graph.add_node("ready", lambda state: ready(state, context))
        _ = graph.add_node("review_needed", lambda state: review_needed(state, context))
        _ = graph.add_edge(START, "collect")
        _ = graph.add_conditional_edges("collect", after_collect, {"stop": END, "plan": "plan"})
        _ = graph.add_edge("plan", "write")
        _ = graph.add_edge("write", "review")
        _ = graph.add_edge("review", "decide")
        _ = graph.add_conditional_edges(
            "decide",
            after_decide,
            {"H": "ready", "U": "review_needed", "D": "replan", "I": "revise"},
        )
        _ = graph.add_edge("replan", "write")
        _ = graph.add_edge("revise", "review")
        _ = graph.add_edge("ready", END)
        _ = graph.add_edge("review_needed", END)
        return graph.compile()

    async def run(
        self, request: DraftRequest
    ) -> ReadyResponse | ReviewNeededResponse | NeedsInputResponse | ErrorResponse:
        context = self.deps.new_request(request)
        graph = self._graph(context)
        try:
            with anyio.fail_after(max(0, context.budget.deadline - time.monotonic())):
                result = await graph.ainvoke(context.state)
            outcome = result.get("outcome")
            if outcome is None:
                return error_result(context, "INVALID_RESPONSE")
        except TimeoutError:
            context.budget.cancel()
            return error_result(context, "TIMEOUT")
        except (
            ProviderError,
            ExecutionBudgetError,
            RevisionReservationError,
            FlowStateError,
            WritingError,
            ValidationError,
        ) as error:
            return error_result(context, getattr(error, "code", "INVALID_RESPONSE"))
        else:
            return outcome
