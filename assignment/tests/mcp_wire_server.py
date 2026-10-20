# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["fastmcp==4.1.1", "openai==3.35.1"]
# ///
# How to run: assignment/.venv/bin/python tests/mcp_wire_server.py
"""Test-only stdio entrypoint wiring real production MCP to local HTTP fixture."""

import json
import os
from pathlib import Path

from openai import AsyncOpenAI

from agent.research import OpenAIResearchProvider
from mcp_server import create_mcp

if __name__ == "__main__":
    sdk = AsyncOpenAI(
        api_key="fixture-not-a-key", base_url=os.environ["FIXTURE_BASE_URL"], max_retries=0
    )
    if pid_path := os.environ.get("FIXTURE_PID_PATH"):
        _ = Path(pid_path).write_text(str(os.getpid()))
    server = create_mcp(OpenAIResearchProvider(sdk, "fixture-model"))
    if trace_path := os.environ.get("FIXTURE_TRACE_PATH"):
        _ = Path(trace_path).write_text(
            json.dumps(
                {
                    key: os.environ.get(key)
                    for key in (
                        "LANGCHAIN_TRACING",
                        "LANGCHAIN_TRACING_V2",
                        "LANGSMITH_TRACING",
                        "OTEL_SDK_DISABLED",
                    )
                }
            )
        )
    _ = server.run(transport="stdio", show_banner=False)
