"""Paid opt-in: ESSAY_LIVE_COMPATIBILITY=1 uv run --frozen pytest
 tests/test_live_compatibility.py -q -s.

Only two allowed settings are read from root .env.local inside the process.
No full provider response, prompt, draft, experience, or key is recorded.
"""

import io
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar, Final
from uuid import uuid4

import anyio
import pytest
from dotenv import dotenv_values
from openai import AsyncOpenAI
from pydantic import BaseModel, ConfigDict

from agent.budget import ExecutionBudget, ExecutionBudgetError
from agent.contracts import ResearchInput
from agent.mcp_client import MCPClient, MCPError
from agent.openai_llm import OpenAIModelProvider
from agent.providers import ProviderError, StructuredModelRequest
from agent.settings import disable_tracing

ROOT: Final = Path(__file__).resolve().parents[2]


class CompatibilityOutput(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid", frozen=True)
    company: str
    role: str
    note: str | None = None


class ProbeSummary(BaseModel):
    """Mutable accumulator of sanitized live-run metadata only."""

    schema_success: bool = False
    error_code: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    tool_calls_reported: int = 0
    model_calls_reserved: int = 0
    native_tool_calls_reserved: int = 0
    elapsed_seconds: float = 0


class CompatibilitySummary(BaseModel):
    """One immutable completed compatibility run."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)
    model: str
    started_at: datetime
    finished_at: datetime
    plain: ProbeSummary
    research: ProbeSummary
    automatic_retries: int = 0
    timeout_seconds_per_model: int = 30
    max_tool_calls: int = 2


@pytest.mark.anyio
@pytest.mark.skipif(
    os.environ.get("ESSAY_LIVE_COMPATIBILITY") != "1", reason="explicit paid opt-in required"
)
async def test_paid_structured_model_and_real_mcp_search(monkeypatch: pytest.MonkeyPatch) -> None:
    # Given: public inputs only, server-local settings, no shell source.
    root = ROOT
    allowed = {"OPENAI_API_KEY", "OPENAI_MODEL"}
    selected = "\n".join(
        line
        for line in (await anyio.Path(root / ".env.local").read_text()).splitlines()
        if line.partition("=")[0].strip() in allowed
    )
    settings = dotenv_values(stream=io.StringIO(selected), interpolate=False)
    for name in sorted(allowed):
        value = settings.get(name)
        assert value, f"Required server configuration {name} is absent"
        monkeypatch.setenv(name, value)
    disable_tracing()
    key, model = os.environ["OPENAI_API_KEY"], os.environ["OPENAI_MODEL"]
    plain_budget, research_budget = ExecutionBudget(), ExecutionBudget()
    plain, research = ProbeSummary(), ProbeSummary()
    started_at = datetime.now(UTC)
    started = time.monotonic()
    # When: exactly one plain model plus one actual MCP hosted research call; no retry.
    async with AsyncOpenAI(
        api_key=key, base_url="https://api.openai.com/v1", max_retries=0, timeout=30.0
    ) as client:
        try:
            result = await OpenAIModelProvider(client, model).generate(
                StructuredModelRequest(
                    role="analysis",
                    instructions=(
                        "Return the supplied company and role in the schema, with note null."
                    ),
                    input='{"company":"OpenAI","role":"Software Engineer"}',
                    schema=CompatibilityOutput,
                ),
                plain_budget,
            )
            plain.schema_success = result.value == CompatibilityOutput(
                company="OpenAI", role="Software Engineer"
            )
            plain.input_tokens = result.usage.input_tokens if result.usage else None
            plain.output_tokens = result.usage.output_tokens if result.usage else None
        except (ProviderError, ExecutionBudgetError) as error:
            plain.error_code = error.code
    plain.elapsed_seconds = round(time.monotonic() - started, 3)
    plain.model_calls_reserved = plain_budget.snapshot().model_calls
    started = time.monotonic()
    async with MCPClient() as mcp:
        try:
            report = await mcp.research(
                ResearchInput(company="OpenAI", role="Software Engineer"), research_budget, uuid4()
            )
            research.schema_success = True
            research.tool_calls_reported = report.tool_calls_reported
            research.input_tokens = report.usage.input_tokens if report.usage else None
            research.output_tokens = report.usage.output_tokens if report.usage else None
        except (MCPError, ExecutionBudgetError) as error:
            research.error_code = error.code
    research.elapsed_seconds = round(time.monotonic() - started, 3)
    research.model_calls_reserved = research_budget.snapshot().model_calls
    research.native_tool_calls_reserved = research_budget.snapshot().native_tool_calls_reserved
    # Then: preserve every run, including typed failures, using unique artifact names.
    summary = CompatibilitySummary(
        model=model,
        started_at=started_at,
        finished_at=datetime.now(UTC),
        plain=plain,
        research=research,
    )
    artifact = root / f"docs/qa-evidence/assignment/foundation/checks/live-{uuid4()}.json"
    _ = artifact.write_text(summary.model_dump_json(indent=2) + "\n")
    assert plain.schema_success, f"Plain compatibility failed; sanitized metadata: {artifact}"
    assert research.schema_success, f"MCP compatibility failed; sanitized metadata: {artifact}"
    assert 1 <= research.tool_calls_reported <= 2
