"""Paid opt-in: ESSAY_LIVE_RESEARCH=1 ESSAY_RESEARCH_CASE=naver pytest
tests/test_research_live.py -q -s. Exactly one node request per explicit invocation.
"""
# Exhaustive guard remains useful when a new outcome variant is added.
# pyright: reportUnnecessaryComparison=false

import hashlib
import io
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar, Final, assert_never
from uuid import uuid4

import anyio
import pytest
from dotenv import dotenv_values
from pydantic import BaseModel, ConfigDict

from agent.budget import BudgetSnapshot, ExecutionBudget
from agent.contracts import ErrorResponse, NeedsInputResponse, ResearchInput
from agent.mcp_client import MCPClient
from agent.nodes.research import ResearchNode, ResearchSuccess
from agent.settings import disable_tracing
from agent.source_http import SafePageReader
from tests.research_live_capture import Diagnostic, ResearchCapture

ROOT: Final = Path(__file__).resolve().parents[2]
CASES: Final = {
    "naver": ResearchInput(
        company="네이버",
        role="N배송 운영 지원",
        job_posting_url="https://recruit.navercorp.com/rcrt/view.do?annoId=30005457",
    ),
    "synthetic": ResearchInput(
        company="Example Fixture Company",
        role="Software Engineer",
        job_posting_text=(
            "Synthetic QA posting, not an actual company or vacancy.\n"
            "Example Fixture Company\nSoftware Engineer\n"
            "Software Engineer requirements: experience writing Python tests."
        ),
    ),
    "anthropic": ResearchInput(
        company="Anthropic",
        role="Software Engineer",
        job_posting_url="https://www.anthropic.com/careers/jobs",
    ),
}


class SourceSummary(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)
    id: str
    kind: str
    url: str | None
    checked_at: datetime
    excerpt_prefix: str


class SourceHash(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)
    path: str
    sha256: str


class LiveSummary(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)
    request: ResearchInput
    request_id: str
    model: str
    started_at: datetime
    elapsed_seconds: float
    status: str
    code: str | None
    sources: tuple[SourceSummary, ...]
    job_requirements: tuple[str, ...]
    budget: BudgetSnapshot
    tool_calls_reported: int | None
    input_tokens: int | None
    output_tokens: int | None
    source_hashes: tuple[SourceHash, ...]
    diagnostics: tuple[Diagnostic, ...]


@pytest.mark.anyio
@pytest.mark.skipif(
    os.environ.get("ESSAY_LIVE_RESEARCH") != "1", reason="explicit paid node opt-in required"
)
async def test_paid_research_node_once(monkeypatch: pytest.MonkeyPatch) -> None:
    # Given: only public fixture input and the two approved server configuration keys.
    request = CASES[os.environ.get("ESSAY_RESEARCH_CASE", "naver")]
    allowed = {"OPENAI_API_KEY", "OPENAI_MODEL"}
    selected = "\n".join(
        line
        for line in (await anyio.Path(ROOT / ".env.local").read_text()).splitlines()
        if line.partition("=")[0].strip() in allowed
    )
    settings = dotenv_values(stream=io.StringIO(selected), interpolate=False)
    for name in sorted(allowed):
        value = settings.get(name)
        assert value, f"Required server configuration {name} absent"
        monkeypatch.setenv(name, value)
    disable_tracing()
    budget = ExecutionBudget()
    request_id = uuid4()
    started_at, started = datetime.now(UTC), time.monotonic()
    capture = ResearchCapture(SafePageReader())
    # When: the production MCP child owns its official SDK endpoint and retries=0.
    async with MCPClient() as mcp:
        capture.instrument(monkeypatch, mcp)
        outcome = await ResearchNode(mcp, reader=capture).run(request, budget, request_id)
    # Then: preserve both success and typed failure without provider response or prompts.
    sources: tuple[SourceSummary, ...] = ()
    jobs: tuple[str, ...] = ()
    reported: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    code: str | None = None
    match outcome:
        case ResearchSuccess():
            sources = tuple(
                SourceSummary(
                    id=source.id,
                    kind=source.kind,
                    url=source.url,
                    checked_at=source.checked_at,
                    excerpt_prefix=source.excerpt[:240],
                )
                for source in outcome.result.sources
            )
            jobs = tuple(job.text[:240] for job in outcome.result.job_requirements)
            reported = outcome.tool_calls_reported
            if outcome.usage:
                input_tokens = outcome.usage.input_tokens
                output_tokens = outcome.usage.output_tokens
        case NeedsInputResponse():
            code = outcome.reason_code
        case ErrorResponse():
            code = outcome.code
        case unreachable:
            assert_never(unreachable)
    summary = LiveSummary(
        request=request,
        request_id=str(request_id),
        model=os.environ["OPENAI_MODEL"],
        started_at=started_at,
        elapsed_seconds=round(time.monotonic() - started, 3),
        status=outcome.status,
        code=code,
        sources=sources,
        job_requirements=jobs,
        budget=budget.snapshot(),
        tool_calls_reported=reported,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        source_hashes=tuple(
            SourceHash(
                path=str(path.relative_to(ROOT)),
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            )
            for path in sorted((ROOT / "assignment/agent").rglob("*.py"))
        ),
        diagnostics=tuple(capture.events),
    )
    artifact = ROOT / f"docs/qa-evidence/assignment/research/checks/live-node-{uuid4()}.json"
    _ = artifact.write_text(summary.model_dump_json(indent=2) + "\n")
    assert budget.snapshot().model_calls == 1, f"Metadata artifact: {artifact}"
    assert budget.snapshot().native_tool_calls_reserved == 2, f"Metadata artifact: {artifact}"
    if os.environ.get("ESSAY_RESEARCH_CASE") == "anthropic":
        assert outcome.status == "needs_input", f"Metadata artifact: {artifact}"
        assert code == "JOB_EVIDENCE_MISSING", f"Metadata artifact: {artifact}"
    else:
        assert outcome.status == "research-success", f"Metadata artifact: {artifact}"
