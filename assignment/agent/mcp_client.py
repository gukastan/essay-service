"""Reusable stdio MCP boundary with request-local budget and correlation checks."""

import os
import sys
from contextlib import AsyncExitStack
from pathlib import Path
from types import TracebackType
from typing import Literal, Self, final
from uuid import UUID

import anyio
from fastmcp import Client
from fastmcp.client.client import CallToolResult
from fastmcp.client.transports import ClientTransport, StdioTransport
from fastmcp.exceptions import ToolError
from mcp import MCPError as ProtocolMCPError
from mcp_types import REQUEST_TIMEOUT
from pydantic import TypeAdapter, ValidationError

from agent.budget import ExecutionBudget, OperationContext
from agent.contracts import DraftRequest, ResearchInput
from agent.research import ResearchMetadata, ResearchReport
from agent.settings import disable_tracing

MCPErrorCode = Literal[
    "PROTOCOL_ERROR",
    "INVALID_RESPONSE",
    "CONFIG_ERROR",
    "MODEL_ERROR",
    "REFUSAL",
    "INCOMPLETE",
    "TIMEOUT",
]


@final
class MCPError(Exception):
    def __init__(self, code: MCPErrorCode) -> None:
        self.code = code
        super().__init__(code)


def _remote_error(result: CallToolResult) -> MCPError:
    """Only exact machine codes from this server may cross the error boundary."""
    for content in result.content:
        if content.type == "text":
            try:
                return MCPError(TypeAdapter(MCPErrorCode).validate_python(content.text))
            except ValidationError:
                return MCPError("PROTOCOL_ERROR")
    return MCPError("PROTOCOL_ERROR")


@final
class MCPClient:
    """One lifespan-owned connection; concurrent calls use MCP request correlation."""

    def __init__(self, client: Client[ClientTransport] | None = None) -> None:
        disable_tracing()
        self._stack = AsyncExitStack()
        self.client = client or Client(
            StdioTransport(
                command=sys.executable,
                args=[str(Path(__file__).resolve().parents[1] / "mcp_server.py")],
                cwd=str(Path(__file__).resolve().parents[1]),
                env={**os.environ, "FASTMCP_LOG_LEVEL": "CRITICAL"},
                keep_alive=False,
            )
        )

    @property
    def connected(self) -> bool:
        return self.client.is_connected()

    async def __aenter__(self) -> Self:
        _ = await self._stack.enter_async_context(self.client)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        with anyio.CancelScope(shield=True):
            await self._stack.aclose()
            await self.client.close()

    async def research(
        self,
        input: ResearchInput | DraftRequest,
        budget: ExecutionBudget,
        request_id: UUID,
    ) -> ResearchReport:
        public = ResearchInput(
            company=input.company,
            role=input.role,
            job_posting_url=input.job_posting_url,
            job_posting_text=input.job_posting_text,
        )

        async def invoke(context: OperationContext) -> ResearchReport:
            remaining = min(
                context.timeout_seconds, anyio.current_effective_deadline() - anyio.current_time()
            )
            if remaining <= 0:
                budget.cancel()
                raise MCPError("TIMEOUT")
            metadata = ResearchMetadata(request_id=request_id, timeout_seconds=remaining)
            try:
                return await self._send(public, metadata)
            except MCPError as error:
                if error.code == "TIMEOUT":
                    budget.cancel()
                raise

        return await budget.run_native_research(invoke)

    async def _send(self, public: ResearchInput, metadata: ResearchMetadata) -> ResearchReport:
        try:
            result = await self.client.call_tool(
                "research_company_role",
                {"input": public.model_dump(by_alias=True, mode="json")},
                meta=metadata.model_dump(by_alias=True, mode="json"),
                timeout=metadata.timeout_seconds,
                raise_on_error=False,
            )
        except TimeoutError:
            raise MCPError("TIMEOUT") from None
        except ProtocolMCPError as error:
            if error.code == REQUEST_TIMEOUT:
                raise MCPError("TIMEOUT") from None
            raise MCPError("PROTOCOL_ERROR") from None
        except (
            ToolError,
            RuntimeError,
            OSError,
            anyio.BrokenResourceError,
            anyio.ClosedResourceError,
            anyio.EndOfStream,
        ):
            raise MCPError("PROTOCOL_ERROR") from None
        if result.is_error:
            raise _remote_error(result)
        try:
            report = ResearchReport.model_validate(result.structured_content)
        except ValidationError:
            raise MCPError("INVALID_RESPONSE") from None
        if report.request_id != metadata.request_id:
            raise MCPError("INVALID_RESPONSE")
        return report
