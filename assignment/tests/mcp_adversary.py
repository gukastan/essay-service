# pyright: reportUnnecessaryComparison=false, reportUnreachable=false
# Exhaustive assert_never intentionally guards future fixture modes.
# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["fastmcp==4.1.1"]
# ///
# How to run: assignment/.venv/bin/python tests/mcp_adversary.py
"""Real MCP protocol fixture supplying adversarial structured tool replies."""

import os
from typing import Literal, assert_never
from uuid import uuid4

import anyio
from fastmcp import Context, FastMCP
from fastmcp.tools import ToolResult
from pydantic import TypeAdapter

from agent.contracts import ResearchInput

server = FastMCP("adversarial-fixture")
Mode = Literal[
    "malformed",
    "wrong-correlation",
    "tool-error",
    "disconnect",
    "timeout",
    "tracing",
    "timeout-error",
]


@server.tool()
async def research_company_role(input: ResearchInput, _ctx: Context) -> ToolResult:
    mode = TypeAdapter(Mode).validate_python(os.environ["FIXTURE_MODE"])
    match mode:
        case "malformed":
            return ToolResult(structured_content={"unexpected": "private-body"})
        case "wrong-correlation":
            return ToolResult(
                structured_content={
                    "requestId": str(uuid4()),
                    "result": {
                        "resolvedCompany": input.company,
                        "sources": [],
                        "companyFacts": [],
                        "jobRequirements": [],
                        "gaps": [],
                    },
                    "toolCallsReported": 0,
                    "actions": [],
                    "usage": None,
                    "verification": "unverified",
                    "maxToolCalls": 2,
                }
            )
        case "tool-error":
            return ToolResult(content="private-provider-error", is_error=True)
        case "timeout-error":
            return ToolResult(content="TIMEOUT", is_error=True)
        case "disconnect":
            _ = os._exit(0)
        case "timeout":
            _ = await anyio.sleep_forever()
            raise AssertionError("unreachable")
        case "tracing":
            return ToolResult(
                structured_content={
                    key: os.environ.get(key)
                    for key in (
                        "LANGCHAIN_TRACING",
                        "LANGCHAIN_TRACING_V2",
                        "LANGSMITH_TRACING",
                        "OTEL_SDK_DISABLED",
                    )
                }
            )
        case unreachable:
            assert_never(unreachable)
    return None


if __name__ == "__main__":
    _ = server.run(transport="stdio", show_banner=False)
