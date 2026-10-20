# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false, reportUnnecessaryComparison=false
# Installed LangGraph exposes incomplete generic SDK member types; local state stays checked.
"""Real LangGraph channels and join harness, not a business pipeline."""

from typing import Literal, assert_never

import anyio
import pytest
from langgraph.graph import END, START, StateGraph

from agent.budget import ExecutionBudget
from agent.contracts import AnalysisResult, DraftRequest, ResearchResult
from agent.state import WorkflowState, WorkflowStateError, initial_state


def request() -> DraftRequest:
    return DraftRequest(company="회사", role="직무", question="문항", experience="경험")


@pytest.mark.anyio
@pytest.mark.parametrize("first", ["research", "analysis"])
async def test_real_graph_joins_once_for_either_completion_order(first: str) -> None:
    # Given
    ready = anyio.Event()
    joins: list[str] = []
    research = ResearchResult(
        resolved_company=None, sources=(), company_facts=(), job_requirements=(), gaps=("공고",)
    )
    analysis = AnalysisResult(question_requirements=(), experience_evidence=(), gaps=("경험",))

    async def research_node(state: WorkflowState) -> WorkflowState:
        if first == "research":
            _ = ready.set()
        else:
            _ = await ready.wait()
        _ = state
        return {"research": research}

    async def analysis_node(state: WorkflowState) -> WorkflowState:
        if first == "analysis":
            _ = ready.set()
        else:
            _ = await ready.wait()
        _ = state
        return {"analysis": analysis}

    def join_node(state: WorkflowState) -> WorkflowState:
        assert state.get("research") == research
        assert state.get("analysis") == analysis
        _ = joins.append(str(state.get("request_id")))
        return {}

    graph = StateGraph(WorkflowState)
    _ = graph.add_node("research_fixture", research_node)
    _ = graph.add_node("analysis_fixture", analysis_node)
    _ = graph.add_node("join_fixture", join_node)
    _ = graph.add_edge(START, "research_fixture")
    _ = graph.add_edge(START, "analysis_fixture")
    _ = graph.add_edge(["research_fixture", "analysis_fixture"], "join_fixture")
    _ = graph.add_edge("join_fixture", END)
    state = initial_state(request(), ExecutionBudget())
    # When
    result = await graph.compile().ainvoke(state)
    # Then
    assert joins == [str(state.get("request_id"))]
    assert result["input_snapshot"] == state.get("input_snapshot")
    assert result["deadline"] == state.get("deadline")
    assert result["revision_count"] == 0


@pytest.mark.anyio
@pytest.mark.parametrize("field", ["request_id", "input_snapshot", "deadline"])
async def test_graph_rejects_immutable_context_overwrite(
    field: Literal["request_id", "input_snapshot", "deadline"],
) -> None:
    # Given
    initial = initial_state(request(), ExecutionBudget())

    def overwrite(state: WorkflowState) -> WorkflowState:
        match field:
            case "request_id":
                return {"request_id": state.get("request_id")}
            case "input_snapshot":
                return {"input_snapshot": state.get("input_snapshot")}
            case "deadline":
                return {"deadline": state.get("deadline")}
            case unreachable:
                assert_never(unreachable)

    graph = StateGraph(WorkflowState)
    _ = graph.add_node("overwrite", overwrite)
    _ = graph.add_edge(START, "overwrite")
    _ = graph.add_edge("overwrite", END)
    # When / Then
    with pytest.raises(WorkflowStateError) as raised:
        _ = await graph.compile().ainvoke(initial)
    assert raised.value.code == "IMMUTABLE_CONTEXT"


@pytest.mark.anyio
async def test_revision_rollback_rejected_by_actual_graph() -> None:
    # Given
    def revise(state: WorkflowState) -> WorkflowState:
        _ = state
        return {"revision_count": 1}

    def rollback(state: WorkflowState) -> WorkflowState:
        _ = state
        return {"revision_count": 0}

    graph = StateGraph(WorkflowState)
    _ = graph.add_node("revise", revise)
    _ = graph.add_node("rollback", rollback)
    _ = graph.add_edge(START, "revise")
    _ = graph.add_edge("revise", "rollback")
    _ = graph.add_edge("rollback", END)
    # When / Then
    with pytest.raises(WorkflowStateError) as raised:
        _ = await graph.compile().ainvoke(initial_state(request(), ExecutionBudget()))
    assert raised.value.code == "REVISION_DECREASE"


@pytest.mark.anyio
async def test_failed_graph_node_has_no_automatic_retry() -> None:
    # Given
    attempts: list[int] = []

    def failure(state: WorkflowState) -> WorkflowState:
        _ = state
        _ = attempts.append(1)
        message = "fixture failure"
        raise OSError(message)

    graph = StateGraph(WorkflowState)
    _ = graph.add_node("failure", failure)
    _ = graph.add_edge(START, "failure")
    _ = graph.add_edge("failure", END)
    # When / Then
    with pytest.raises(OSError, match="fixture failure"):
        _ = await graph.compile().ainvoke(initial_state(request(), ExecutionBudget()))
    assert attempts == [1]


def test_initial_state_containers_are_request_local() -> None:
    # Given / When
    first = initial_state(request(), ExecutionBudget())
    second = initial_state(request(), ExecutionBudget())
    first["draft"] = "private first request"
    # Then
    assert first.get("request_id") != second.get("request_id")
    assert second.get("draft") is None
    assert first.get("usage") is not second.get("usage")
    assert first.get("research") is None
    assert first.get("analysis") is None
    assert first.get("outcome") is None
