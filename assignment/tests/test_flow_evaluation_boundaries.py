"""Adversarial F contracts exercised through parsing and the real SDK adapter."""

import httpx2
import pytest
from openai import AsyncOpenAI
from pydantic import ValidationError

from agent.budget import ExecutionBudget
from agent.contracts import Evaluation, EvaluationIssue
from agent.openai_llm import OpenAIModelProvider
from agent.providers import ProviderError, StructuredModelRequest
from tests.flow_fixture import evaluation
from tests.wire_fixture import JSON, assert_strict_schema, response_body


@pytest.mark.parametrize("omitted", range(7))
def test_evaluation_rejects_every_missing_mandatory_criterion(omitted: int) -> None:
    # Given
    payload = evaluation().model_dump(mode="json")
    del payload["criteria"][omitted]
    # When / Then
    with pytest.raises(ValidationError):
        _ = Evaluation.model_validate(payload)


def test_duplicate_pass_cannot_replace_a_missing_criterion() -> None:
    # Given
    payload = evaluation().model_dump(mode="json")
    payload["criteria"][-1] = payload["criteria"][0]
    # When / Then
    with pytest.raises(ValidationError):
        _ = Evaluation.model_validate(payload)


def test_failed_criterion_requires_an_issue() -> None:
    # Given
    payload = evaluation().model_dump()
    payload["criteria"][0]["passed"] = False
    # When / Then
    with pytest.raises(ValidationError):
        _ = Evaluation.model_validate(payload)


def test_all_pass_cannot_hide_a_reported_issue() -> None:
    # Given
    payload = evaluation().model_dump()
    payload["issues"] = [
        {
            "id": "i1",
            "criterion_id": "length",
            "claim_ids": [],
            "paragraph_ids": [],
            "start": None,
            "end": None,
            "reason": "Too short.",
            "scope": "plan_or_claim",
            "instruction": "Replan with existing evidence.",
            "missing_fields": [],
        }
    ]
    # When / Then
    with pytest.raises(ValidationError):
        _ = Evaluation.model_validate(payload)


@pytest.mark.parametrize(
    ("scope", "missing_fields", "start", "end"),
    [
        ("missing_info", [], None, None),
        ("wording", ["experience"], 0, 1),
        ("plan_or_claim", ["company"], None, None),
        ("wording", [], None, None),
        ("wording", [], 0, None),
        ("wording", [], 2, 1),
        ("unclassified", [], 0, 1),
    ],
)
def test_issue_rejects_false_missing_info_or_unusable_scope(
    scope: str,
    missing_fields: list[str],
    start: int | None,
    end: int | None,
) -> None:
    # Given / When / Then
    with pytest.raises(ValidationError):
        _ = EvaluationIssue.model_validate(
            {
                "id": "i1",
                "criterionId": "length",
                "claimIds": [],
                "paragraphIds": ["p1"],
                "start": start,
                "end": end,
                "reason": "Length needs work.",
                "scope": scope,
                "instruction": "Use existing evidence.",
                "missingFields": missing_fields,
            }
        )


@pytest.mark.anyio
async def test_real_sdk_adapter_rejects_incomplete_mandatory_evaluation() -> None:
    # Given
    payload = evaluation().model_dump(mode="json", by_alias=True)
    del payload["criteria"][0]
    malformed = JSON.dump_json(payload).decode()
    requests: list[httpx2.Request] = []

    def respond(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, content=response_body(malformed))

    budget = ExecutionBudget()
    async with (
        httpx2.AsyncClient(transport=httpx2.MockTransport(respond)) as transport,
        AsyncOpenAI(api_key="fixture", http_client=transport, max_retries=2) as sdk,
    ):
        # When / Then
        with pytest.raises(ProviderError) as raised:
            _ = await OpenAIModelProvider(sdk, "fixture-model").generate(
                StructuredModelRequest(
                    role="review",
                    instructions="Fixture.",
                    input="Fixture.",
                    schema=Evaluation,
                ),
                budget,
            )
    assert raised.value.code == "INVALID_RESPONSE"
    assert len(requests) == 1
    assert budget.snapshot().model_calls == 1
    wire = JSON.validate_json(requests[0].content)
    assert isinstance(wire, dict)
    text = wire["text"]
    assert isinstance(text, dict)
    formatting = text["format"]
    assert isinstance(formatting, dict)
    assert formatting["strict"] is True
    assert_strict_schema(formatting["schema"])
