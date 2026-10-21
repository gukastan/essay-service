import hashlib
import io
import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Final
from uuid import UUID

import pytest
from dotenv import dotenv_values
from openai import AsyncOpenAI
from pydantic import BaseModel, JsonValue, TypeAdapter, ValidationError

from agent.budget import ExecutionBudget
from agent.contracts import DraftRequest, Evaluation, FlowAnalysisResult, ResearchInput
from agent.deps import WorkflowDeps
from agent.essay_graph import EssayWorkflow
from agent.flow_state import (
    FlowStateError,
    validate_draft_context,
    validate_evaluation_context,
)
from agent.mcp_client import MCPClient
from agent.nodes.analyze import anchor_personal_analysis, validate_personal_analysis
from agent.nodes.review import anchor_plan_issues
from agent.nodes.write import DraftClaims, WritingInput, assemble_draft
from agent.nodes.writing_support import WritingContext, WritingError, validate_writing_facts
from agent.openai_llm import OpenAIModelProvider
from agent.providers import ModelResult, StructuredModelRequest
from agent.research import ResearchReport
from agent.settings import disable_tracing
from agent.validate_evidence import ReviewInput

ROOT: Final = Path(__file__).resolve().parents[2]
FIXTURE: Final = ROOT / "tests/fixtures/live-samples.json"
CASES: Final = TypeAdapter(list[dict[str, str]]).validate_json(FIXTURE.read_bytes())
SUPPLEMENTAL: Final = {
    "id": "user-posting-service-planner",
    "company": "Example Fixture Company",
    "role": "Service Planner",
    "question": CASES[0]["question"],
    "experience": CASES[0]["experience"],
    "jobPostingText": (
        "Synthetic QA posting, not an actual company or vacancy.\n"
        "Example Fixture Company\n"
        "Service Planner\n"
        "Service Planner requirements: experience coordinating teammates and improving "
        "user-facing page flows."
    ),
}


def writer_validation_event(value: DraftClaims, input_json: str) -> dict[str, JsonValue]:
    writer_input = WritingInput.model_validate_json(input_json)
    details: dict[str, JsonValue] = {
        "role": "writer-validation",
        "claimIds": [item.id for item in value.claim_map],
        "expectedIds": [item.id for item in writer_input.plan.claims],
        "factMatchesPlan": {
            item.id: item.text == planned.text
            for item in value.claim_map
            for planned in writer_input.plan.claims
            if item.id == planned.id and item.kind in {"user_fact", "company_fact"}
        },
        "claimBindingsMatchPlan": {
            item.id: item.kind == planned.kind and item.evidence_ids == planned.evidence_ids
            for item in value.claim_map
            for planned in writer_input.plan.claims
            if item.id == planned.id
        },
        "generatedTextChecks": {
            item.id: {
                "hasDigit": any(character.isdigit() for character in item.text),
                "hasPastMarker": any(
                    marker in item.text
                    for marker in ("했다", "했습", "였다", "였습", "었다", "었습")
                ),
                "length": len(item.text),
            }
            for item in value.claim_map
            if item.id in {"interpretation", "future"}
        },
    }
    try:
        draft = assemble_draft(value, writer_input.plan)
        validate_draft_context(
            draft, writer_input.plan, writer_input.analysis, writer_input.research
        )
        validate_writing_facts(
            draft,
            WritingContext(writer_input.request, writer_input.analysis, writer_input.research),
        )
    except (FlowStateError, WritingError, ValidationError) as error:
        details["error"] = str(getattr(error, "code", type(error).__name__))
    else:
        details["draftLength"] = len(draft.draft)
    return details


def analysis_validation_events(
    value: FlowAnalysisResult, request: DraftRequest
) -> list[dict[str, JsonValue]]:
    try:
        anchored = anchor_personal_analysis(value, request)
        validate_personal_analysis(anchored, request)
    except FlowStateError as error:
        return [
            {
                "role": "analysis-validation",
                "error": error.code,
                "evidenceOffsets": [
                    {
                        "id": item.id,
                        "quote": item.quote,
                        "start": item.start,
                        "end": item.end,
                        "sourceSlice": request.experience[item.start : item.end],
                    }
                    for item in value.experience_evidence
                ],
            }
        ]
    corrected = sum(
        source.start != current.start or source.end != current.end
        for source, current in zip(
            value.experience_evidence, anchored.experience_evidence, strict=True
        )
    )
    return [{"role": "analysis-anchoring", "correctedOffsets": corrected}] if corrected else []


def review_validation_event(value: Evaluation, input_json: str) -> dict[str, JsonValue]:
    review_input = ReviewInput.model_validate_json(input_json)
    anchored = anchor_plan_issues(value, review_input.draft)
    details: dict[str, JsonValue] = {
        "role": "review-validation",
        "draftLength": len(review_input.draft.draft),
        "correctedIssues": sum(
            source.start != fixed.start
            or source.end != fixed.end
            or source.paragraph_ids != fixed.paragraph_ids
            for source, fixed in zip(value.issues, anchored.issues, strict=True)
        ),
        "issues": [
            {
                "criterion": item.criterion_id,
                "scope": item.scope,
                "claimIds": list(item.claim_ids),
                "paragraphIds": list(item.paragraph_ids),
                "start": item.start,
                "end": item.end,
            }
            for item in anchored.issues
        ],
    }
    try:
        validate_evaluation_context(anchored, review_input.draft, review_input.plan)
    except FlowStateError as error:
        details["error"] = error.code
    return details


@pytest.mark.anyio
@pytest.mark.parametrize(
    "sample", [*CASES, SUPPLEMENTAL], ids=[sample["id"] for sample in [*CASES, SUPPLEMENTAL]]
)
@pytest.mark.skipif(os.environ.get("ESSAY_LIVE_ESSAY") != "1", reason="paid opt-in required")
async def test_essay_live_case(sample: dict[str, str], monkeypatch: pytest.MonkeyPatch) -> None:
    selected = "\n".join(
        line
        for line in (ROOT / ".env.local").read_text().splitlines()
        if line.partition("=")[0].strip() in {"OPENAI_API_KEY", "OPENAI_MODEL"}
    )
    config = dotenv_values(stream=io.StringIO(selected), interpolate=False)
    key, model = config.get("OPENAI_API_KEY"), config.get("OPENAI_MODEL")
    assert key, "OpenAI key is required for live QA"
    assert model, "OpenAI model is required for live QA"
    monkeypatch.setenv("OPENAI_API_KEY", key)
    monkeypatch.setenv("OPENAI_MODEL", model)
    disable_tracing()

    input_request = DraftRequest.model_validate(
        {
            name: sample[name]
            for name in ("company", "role", "question", "experience", "jobPostingText")
            if name in sample
        }
    )
    events: list[dict[str, JsonValue]] = []

    class RecordingProvider:
        def __init__(self, provider: OpenAIModelProvider) -> None:
            self.provider: OpenAIModelProvider = provider

        async def generate[T: BaseModel](
            self, request: StructuredModelRequest[T], budget: ExecutionBudget
        ) -> ModelResult[T]:
            started = time.monotonic()
            try:
                result = await self.provider.generate(request, budget)
            except Exception as error:
                events.append(
                    {
                        "role": request.role,
                        "seconds": round(time.monotonic() - started, 3),
                        "error": getattr(error, "code", type(error).__name__),
                    }
                )
                raise
            events.append(
                {
                    "role": request.role,
                    "seconds": round(time.monotonic() - started, 3),
                    "inputTokens": result.usage.input_tokens if result.usage else None,
                    "outputTokens": result.usage.output_tokens if result.usage else None,
                }
            )
            if isinstance(result.value, FlowAnalysisResult):
                events.extend(analysis_validation_events(result.value, input_request))
            if isinstance(result.value, DraftClaims):
                events.append(writer_validation_event(result.value, request.input))
            if isinstance(result.value, Evaluation):
                events.append(review_validation_event(result.value, request.input))
            return result

    started_at, started = datetime.now(UTC), time.monotonic()
    async with (
        AsyncOpenAI(
            api_key=key, base_url="https://api.openai.com/v1", max_retries=0, timeout=30.0
        ) as client,
        MCPClient() as mcp,
    ):
        research = mcp.research

        async def recorded_research(
            public: ResearchInput | DraftRequest,
            budget: ExecutionBudget,
            request_id: UUID,
        ) -> ResearchReport:
            call_started = time.monotonic()
            try:
                report = await research(public, budget, request_id)
            except Exception as error:
                events.append(
                    {
                        "role": "research",
                        "seconds": round(time.monotonic() - call_started, 3),
                        "error": getattr(error, "code", type(error).__name__),
                    }
                )
                raise
            events.append(
                {
                    "role": "research",
                    "seconds": round(time.monotonic() - call_started, 3),
                    "toolCallsReported": report.tool_calls_reported,
                    "inputTokens": report.usage.input_tokens if report.usage else None,
                    "outputTokens": report.usage.output_tokens if report.usage else None,
                }
            )
            return report

        monkeypatch.setattr(mcp, "research", recorded_research)
        response = await EssayWorkflow(
            WorkflowDeps(RecordingProvider(OpenAIModelProvider(client, model)), mcp)
        ).run(input_request)

    output = {
        "sampleId": sample["id"],
        "supplementalSyntheticPosting": sample is SUPPLEMENTAL,
        "fixtureSha256": hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
        "startedAt": started_at.isoformat(),
        "elapsedSeconds": round(time.monotonic() - started, 3),
        "model": model,
        "path": "real OpenAI model + real stdio MCP; no stub",
        "request": input_request.model_dump(by_alias=True, mode="json"),
        "response": response.model_dump(by_alias=True, mode="json"),
        "events": events,
    }
    run_stamp = started_at.strftime("%Y%m%dT%H%M%S%fZ")
    kind = "supplemental" if sample is SUPPLEMENTAL else "original"
    target = ROOT / f"docs/qa-evidence/assignment/live/{kind}-{sample['id']}-{run_stamp}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    _ = target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    expected = "needs_input" if sample["id"] == "insufficient" else "ready"
    assert response.status == expected, f"Expected {expected}: {target}"
