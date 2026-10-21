"""Serve the essay workflow through a request-isolated FastAPI endpoint."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Literal
from uuid import UUID, uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from agent.contract_input import Contract
from agent.contracts import (
    DraftRequest,
    ErrorResponse,
    NeedsInputResponse,
    ReadyResponse,
    ReviewNeededResponse,
)
from agent.deps import WorkflowDeps
from agent.essay_graph import EssayWorkflow
from agent.mcp_client import MCPClient
from agent.openai_llm import OpenAIModelProvider
from agent.providers import ProviderError
from agent.settings import Settings, disable_tracing, model_client


class Health(Contract):
    status: Literal["ok"] = "ok"
    model_configured: bool
    mcp_connected: bool
    pipeline_available: Literal[True] = True
    instance_id: UUID
    creation_count: Literal[1] = 1


@dataclass(frozen=True, slots=True)
class Runtime:
    settings: Settings
    deps: WorkflowDeps
    instance_id: UUID


def response_status(
    result: ReadyResponse | ReviewNeededResponse | NeedsInputResponse | ErrorResponse,
) -> int:
    match result.status:
        case "ready" | "review_needed" | "needs_input":
            return 200
        case "error":
            match result.code:
                case "INVALID_INPUT":
                    return 400
                case "CONFIG_ERROR":
                    return 500
                case "TIMEOUT":
                    return 504
                case _:
                    return 502


def create_app(settings: Settings | None = None) -> FastAPI:
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

    @app.exception_handler(RequestValidationError)
    async def invalid_input(_request: Request, _error: RequestValidationError) -> JSONResponse:
        response = ErrorResponse(
            status="error",
            request_id=uuid4(),
            code="INVALID_INPUT",
            message="입력 형식을 확인해 주세요.",
        )
        return JSONResponse(
            status_code=400, content=response.model_dump(mode="json", by_alias=True)
        )

    @app.post(
        "/api/drafts",
        response_model=ReadyResponse | ReviewNeededResponse | NeedsInputResponse | ErrorResponse,
    )
    async def drafts(payload: DraftRequest) -> JSONResponse:
        if runtime is None:
            result = ErrorResponse(
                status="error",
                request_id=uuid4(),
                code="CONFIG_ERROR",
                message="초안 생성 서버를 사용할 수 없습니다.",
            )
        else:
            result = await EssayWorkflow(runtime.deps).run(payload)
        return JSONResponse(
            status_code=response_status(result),
            content=result.model_dump(mode="json", by_alias=True),
        )

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
