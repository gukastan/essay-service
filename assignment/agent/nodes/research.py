"""One MCP candidate call followed by bounded official evidence verification."""

from dataclasses import dataclass, field
from typing import Literal
from uuid import UUID

from agent.budget import ExecutionBudget, ExecutionBudgetError, OperationContext
from agent.contract_input import Contract
from agent.contracts import (
    DraftRequest,
    ErrorResponse,
    NeedsInputResponse,
    ResearchInput,
    ResearchResult,
)
from agent.mcp_client import MCPClient, MCPError
from agent.providers import TokenUsage
from agent.source_http import PageReader, SafePageReader
from agent.source_page import PageReadError
from agent.source_trust import DEFAULT_ANCHORS, CompanyAnchor
from agent.source_verify import SourceVerifier


class ResearchSuccess(Contract):
    status: Literal["research-success"] = "research-success"
    result: ResearchResult
    tool_calls_reported: int
    usage: TokenUsage | None


ResearchOutcome = ResearchSuccess | NeedsInputResponse | ErrorResponse


@dataclass(frozen=True, slots=True)
class ResearchNode:
    mcp: MCPClient
    reader: PageReader = field(default_factory=SafePageReader)
    anchors: tuple[CompanyAnchor, ...] = DEFAULT_ANCHORS

    async def run(
        self, input: ResearchInput | DraftRequest, budget: ExecutionBudget, request_id: UUID
    ) -> ResearchOutcome:
        public = ResearchInput(
            company=input.company,
            role=input.role,
            job_posting_url=input.job_posting_url,
            job_posting_text=input.job_posting_text,
        )
        anchors = tuple(
            anchor
            for anchor in self.anchors
            if public.company.casefold() in {alias.casefold() for alias in anchor.aliases}
        )
        anchor = anchors[0] if len(anchors) == 1 else None
        if anchor is None and public.job_posting_url is None and public.job_posting_text is None:
            return ResearchSuccess(
                result=ResearchResult(
                    resolved_company=None,
                    sources=(),
                    company_facts=(),
                    job_requirements=(),
                    gaps=("NO_TRUSTED_EXTERNAL_SOURCE",),
                ),
                tool_calls_reported=0,
                usage=None,
            )

        async def execute(_context: OperationContext) -> ResearchOutcome:
            report = await self.mcp.research(public, budget, request_id)
            result = await SourceVerifier(self.reader, anchor).verify(report.result, public, budget)
            return ResearchSuccess(
                result=result, tool_calls_reported=report.tool_calls_reported, usage=report.usage
            )

        try:
            return await budget.run_research(execute)
        except (MCPError, ExecutionBudgetError) as error:
            return error_response(error, request_id)
        except PageReadError as error:
            if error.code == "TIMEOUT":
                budget.cancel()
            return ErrorResponse(
                status="error",
                request_id=request_id,
                code="TIMEOUT" if error.code == "TIMEOUT" else "SEARCH_ERROR",
                message="출처에 연결하지 못했습니다.",
            )


def error_response(error: MCPError | ExecutionBudgetError, request_id: UUID) -> ErrorResponse:
    codes: dict[
        str,
        Literal[
            "CONFIG_ERROR",
            "TIMEOUT",
            "INVALID_RESPONSE",
            "SEARCH_ERROR",
            "MODEL_ERROR",
            "BUDGET_EXCEEDED",
            "CANCELLED",
        ],
    ] = {
        "CONFIG_ERROR": "CONFIG_ERROR",
        "TIMEOUT": "TIMEOUT",
        "INVALID_RESPONSE": "INVALID_RESPONSE",
        "PROTOCOL_ERROR": "SEARCH_ERROR",
        "MODEL_ERROR": "MODEL_ERROR",
        "REFUSAL": "MODEL_ERROR",
        "INCOMPLETE": "MODEL_ERROR",
        "LIMIT_EXCEEDED": "BUDGET_EXCEEDED",
        "DEADLINE_EXCEEDED": "TIMEOUT",
        "CANCELLED": "CANCELLED",
    }
    return ErrorResponse(
        status="error",
        request_id=request_id,
        code=codes[error.code],
        message="조사를 완료하지 못했습니다.",
    )
