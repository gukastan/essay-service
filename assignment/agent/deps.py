"""Typed lifespan dependencies and isolated per-request execution context."""

from dataclasses import dataclass
from uuid import UUID, uuid4

from agent.budget import ExecutionBudget
from agent.contracts import DraftRequest
from agent.mcp_client import MCPClient
from agent.providers import ModelProvider
from agent.state import WorkflowState, initial_state


@dataclass(frozen=True, slots=True)
class RequestContext:
    request_id: UUID
    input_snapshot: DraftRequest
    budget: ExecutionBudget
    state: WorkflowState


@dataclass(frozen=True, slots=True)
class WorkflowDeps:
    model: ModelProvider
    mcp: MCPClient

    def new_request(self, input: DraftRequest) -> RequestContext:
        return new_request(input)


def new_request(input: DraftRequest) -> RequestContext:
    request_id = uuid4()
    budget = ExecutionBudget()
    return RequestContext(request_id, input, budget, initial_state(input, budget, request_id))
