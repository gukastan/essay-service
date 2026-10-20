"""FastAPI foundation lifespan; the drafts business pipeline arrives in ESSAY-14."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Literal
from uuid import UUID, uuid4

from fastapi import FastAPI

from agent.contract_input import Contract
from agent.deps import WorkflowDeps
from agent.mcp_client import MCPClient
from agent.openai_llm import OpenAIModelProvider
from agent.providers import ProviderError
from agent.settings import Settings, disable_tracing, model_client


class Health(Contract):
    status: Literal["ok"] = "ok"
    model_configured: bool
    mcp_connected: bool
    pipeline_available: Literal[False] = False
    instance_id: UUID
    creation_count: Literal[1] = 1


@dataclass(frozen=True, slots=True)
class Runtime:
    settings: Settings
    deps: WorkflowDeps
    instance_id: UUID


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build a server with no legacy graph, database, chat or automatic model call."""
    runtime: Runtime | None = None

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        nonlocal runtime
        disable_tracing()
        config = settings or Settings()
        async with model_client(config) as client, MCPClient() as mcp:
            deps = WorkflowDeps(OpenAIModelProvider(client, config.openai_model), mcp)
            runtime = Runtime(config, deps, uuid4())
            app.state.deps = deps
            try:
                yield
            finally:
                runtime = None
                del app.state.deps

    app = FastAPI(lifespan=lifespan)

    @app.get("/health")
    async def health() -> Health:
        if runtime is None:
            raise ProviderError("CONFIG_ERROR")
        return Health(
            model_configured=runtime.settings.model_configured,
            mcp_connected=runtime.deps.mcp.connected,
            instance_id=runtime.instance_id,
        )

    return app


app = create_app()
