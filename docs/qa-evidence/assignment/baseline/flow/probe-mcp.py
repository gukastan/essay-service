#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["anyio", "pydantic>=2", "mcp", "fastmcp", "langsmith"]
# ///
# ─── How to run ───
# uv run probe-mcp.py /absolute/path/to/assignment output.json
# Baseline reproduction uses A's isolated Python for the exact installed versions.
# Launches its own stdio children; never reads dotenv or a session database.
# ──────────────────
"""Observe real original MCP capabilities without persisting prompt contents."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

import anyio
from pydantic import BaseModel, ConfigDict

ROOT: Final = Path(sys.argv[1]).resolve()
OUTPUT: Final = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(ROOT))
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LLM_BACKEND"] = "fake"

from agent.mcp_client import MCPClient
from agent.retry import with_retry


class Monitoring(BaseModel):
    """Typed public telemetry boundary; fields originate from the mock JSON fixture."""
    model_config = ConfigDict(frozen=True)
    system_name: str
    status: str
    cpu_percent: float
    memory_percent: float
    last_checked: str
    alerts: list[str]


async def main() -> None:
    """Exercise two real MCP servers and bounded positive/negative capability calls."""
    started = datetime.now(timezone.utc).isoformat()
    client = MCPClient()
    observations = []
    checks: dict[str, bool] = {}
    with anyio.fail_after(30):
        await client.start()
        try:
            checks["two_live_mcp_sessions"] = set(client.sessions) == {"ops", "docs"}
            prompt_server = await client.find_prompt("incident_analysis_prompt")
            prompt = await client.get_prompt(
                "incident_analysis_prompt",
                {"system_name": "auth-service", "symptom": "장애 진단"},
                server=prompt_server,
            )
            checks["prompt_discovered_and_returned"] = prompt_server == "ops" and len(prompt) > 0
            observations.append({"operation": "find_prompt/get_prompt", "server": prompt_server,
                                 "name": "incident_analysis_prompt", "characters": len(prompt),
                                 "sha256": hashlib.sha256(prompt.encode()).hexdigest()})
            raw, retries = await with_retry(
                client.call_tool, "get_monitoring_status", {"system_name": "auth-service"},
            )
            telemetry = Monitoring.model_validate(raw)
            checks["tool_retry_then_valid_result"] = retries == 1 and telemetry.system_name == "auth-service" and telemetry.status == "degraded"
            observations.append({"operation": "call_tool", "name": "get_monitoring_status", "retries": retries, "result": telemetry.model_dump()})
            server, template = await client.find_resource_template("get_incident_runbook")
            uri = template.format(incident_type="high-latency")
            resource = await client.read_resource(uri, server=server)
            fixture = (ROOT / "data/runbooks/high-latency.md").read_text()
            checks["resource_matches_public_fixture"] = server == "ops" and resource == fixture
            observations.append({"operation": "find_resource_template/read_resource", "server": server,
                                 "uri": uri, "characters": len(resource),
                                 "sha256": hashlib.sha256(resource.encode()).hexdigest()})
            raw, retries = await with_retry(
                client.call_tool, "get_monitoring_status", {"system_name": "unknown-service"},
            )
            unknown = Monitoring.model_validate(raw)
            checks["unknown_system_control"] = retries == 0 and unknown.status == "unknown" and unknown.cpu_percent == 0 and len(unknown.alerts) == 1
            observations.append({"operation": "call_tool", "name": "get_monitoring_status", "retries": retries, "result": unknown.model_dump()})
            missing = await client.read_resource(template.format(incident_type="essay18-missing"), server=server)
            checks["missing_resource_control"] = missing.startswith("# Runbook Not Found")
            observations.append({"operation": "read_resource", "uri": template.format(incident_type="essay18-missing"), "result": missing})
            docs_templates = await client.list_resource_templates("docs")
            checks["decoy_templates_listed"] = len(docs_templates) > 0
            observations.append({"operation": "list_resource_templates", "server": "docs", "count": len(docs_templates)})
        finally:
            await client.stop()
    checks["client_sessions_closed"] = len(client.sessions) == 0
    report = {"started_at": started, "completed_at": datetime.now(timezone.utc).isoformat(),
              "invocation": sys.argv, "python": sys.version, "source": str(ROOT),
              "environment": {"LLM_BACKEND": "fake", "LANGCHAIN_TRACING_V2": "false", "LANGSMITH_TRACING": "false"},
              "protocol": "real stdio MCP", "telemetry": "mock JSON fixture with random jitter",
              "full_prompts_persisted": False, "checks": checks, "observations": observations}
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(OUTPUT), "checks": checks}))
    assert all(checks.values()), "MCP capability scenario failed; inspect result artifact"


if __name__ == "__main__":
    anyio.run(main)
