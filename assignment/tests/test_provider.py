"""OpenAI SDK serialized HTTP boundary with deterministic response fixtures."""

from typing import ClassVar
from uuid import uuid4

import httpx2
import pytest
from openai import AsyncOpenAI
from pydantic import BaseModel, ConfigDict

from agent.budget import ExecutionBudget, ExecutionBudgetError
from agent.contracts import ResearchInput
from agent.openai_llm import OpenAIModelProvider
from agent.providers import ProviderError, StructuredModelRequest
from agent.research import OpenAIResearchProvider, ResearchMetadata
from tests.wire_fixture import JSON, assert_strict_schema, research_body, response_body


class ProbeOutput(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid", frozen=True)
    answer: str
    note: str | None = None


def probe() -> StructuredModelRequest[ProbeOutput]:
    return StructuredModelRequest(
        role="analysis",
        instructions="Return a structured response.",
        input="public fixture",
        schema=ProbeOutput,
    )


@pytest.mark.anyio
async def test_sdk_wire_is_strict_nullable_and_disables_storage_and_tools() -> None:
    # Given
    requests: list[httpx2.Request] = []

    def respond(request: httpx2.Request) -> httpx2.Response:
        _ = requests.append(request)
        return httpx2.Response(200, content=response_body('{"answer":"ok","note":null}'))

    async with (
        httpx2.AsyncClient(transport=httpx2.MockTransport(respond)) as transport,
        AsyncOpenAI(api_key="fixture", http_client=transport, max_retries=2) as sdk,
    ):
        # When
        result = await OpenAIModelProvider(sdk, "fixture-model").generate(
            probe(), ExecutionBudget()
        )
    # Then
    assert result.value == ProbeOutput(answer="ok")
    assert result.usage is not None
    assert result.usage.output_tokens == 7
    assert len(requests) == 1
    wire = JSON.validate_json(requests[0].content)
    assert isinstance(wire, dict)
    assert wire["store"] is False
    assert wire["max_output_tokens"] == 3000
    assert not wire.get("tools")
    assert "max_tool_calls" not in wire
    text = wire["text"]
    assert isinstance(text, dict)
    formatting = text["format"]
    assert isinstance(formatting, dict)
    assert formatting["type"] == "json_schema"
    assert formatting["strict"] is True
    schema = formatting["schema"]
    _ = assert_strict_schema(schema)
    assert isinstance(schema, dict)
    properties = schema["properties"]
    assert isinstance(properties, dict)
    note = properties["note"]
    assert isinstance(note, dict)
    assert note["anyOf"] == [{"type": "string"}, {"type": "null"}]


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("body", "code"),
    [
        (response_body("private-refusal-body", refusal=True), "REFUSAL"),
        (response_body("private-incomplete-body", status="incomplete"), "INCOMPLETE"),
        (response_body("private-invalid-json"), "INVALID_RESPONSE"),
        (response_body('{"answer":42}'), "INVALID_RESPONSE"),
        (b'{"status":"completed"}', "INVALID_RESPONSE"),
        (b'{"status":"completed","output":null}', "INVALID_RESPONSE"),
        (b'{"status":"completed","output":"wrong"}', "INVALID_RESPONSE"),
    ],
)
async def test_provider_failures_are_typed_sanitized_and_not_repaired(
    body: bytes, code: str
) -> None:
    # Given
    calls: list[int] = []

    def respond(_request: httpx2.Request) -> httpx2.Response:
        _ = calls.append(1)
        return httpx2.Response(200, content=body)

    budget = ExecutionBudget()
    async with (
        httpx2.AsyncClient(transport=httpx2.MockTransport(respond)) as transport,
        AsyncOpenAI(api_key="fixture", http_client=transport) as sdk,
    ):
        # When / Then
        with pytest.raises(ProviderError) as raised:
            _ = await OpenAIModelProvider(sdk, "fixture-model").generate(probe(), budget)
    assert raised.value.code == code
    assert str(raised.value) == code
    assert calls == [1]
    assert budget.snapshot().model_calls == 1


@pytest.mark.anyio
async def test_http_failure_disables_sdk_retry_even_if_client_default_allows_it() -> None:
    # Given
    calls: list[int] = []

    def respond(_request: httpx2.Request) -> httpx2.Response:
        _ = calls.append(1)
        return httpx2.Response(500, json={"error": {"message": "private-provider-error"}})

    async with (
        httpx2.AsyncClient(transport=httpx2.MockTransport(respond)) as transport,
        AsyncOpenAI(api_key="fixture", http_client=transport, max_retries=3) as sdk,
    ):
        # When / Then
        with pytest.raises(ProviderError) as raised:
            _ = await OpenAIModelProvider(sdk, "fixture-model").generate(probe(), ExecutionBudget())
    assert raised.value.code == "MODEL_ERROR"
    assert str(raised.value) == "MODEL_ERROR"
    assert calls == [1]


@pytest.mark.anyio
async def test_sdk_timeout_prevents_later_transmission() -> None:
    # Given
    calls: list[int] = []

    def timeout(request: httpx2.Request) -> httpx2.Response:
        _ = calls.append(1)
        raise httpx2.ReadTimeout("private-provider-error", request=request)

    budget = ExecutionBudget()
    async with (
        httpx2.AsyncClient(transport=httpx2.MockTransport(timeout)) as transport,
        AsyncOpenAI(api_key="fixture", http_client=transport) as sdk,
    ):
        provider = OpenAIModelProvider(sdk, "fixture-model")
        # When / Then
        with pytest.raises(ProviderError) as raised:
            _ = await provider.generate(probe(), budget)
        with pytest.raises(ExecutionBudgetError):
            _ = await provider.generate(
                StructuredModelRequest(
                    role="writer", instructions="", input="public", schema=ProbeOutput
                ),
                budget,
            )
    assert raised.value.code == "TIMEOUT"
    assert calls == [1]
    assert budget.snapshot().model_calls == 1


@pytest.mark.anyio
async def test_hosted_research_is_one_wire_call_with_two_tool_capacity() -> None:
    # Given
    requests: list[httpx2.Request] = []

    def respond(request: httpx2.Request) -> httpx2.Response:
        _ = requests.append(request)
        return httpx2.Response(200, content=research_body())

    request_id = uuid4()
    async with (
        httpx2.AsyncClient(transport=httpx2.MockTransport(respond)) as transport,
        AsyncOpenAI(api_key="fixture", http_client=transport) as sdk,
    ):
        # When
        result = await OpenAIResearchProvider(sdk, "fixture-model").research(
            ResearchInput(company="회사", role="직무"),
            ResearchMetadata(request_id=request_id, timeout_seconds=4.0),
        )
    # Then
    assert result.request_id == request_id
    assert result.result.resolved_company == "회사"
    assert result.verification == "unverified"
    assert result.tool_calls_reported == 1
    assert result.max_tool_calls == 2
    assert len(requests) == 1
    wire = JSON.validate_json(requests[0].content)
    assert isinstance(wire, dict)
    assert wire["store"] is False
    assert wire["max_tool_calls"] == 2
    assert wire["max_output_tokens"] == 3000
    assert wire["tools"] == [{"type": "web_search"}]
    text = wire["text"]
    assert isinstance(text, dict)
    formatting = text["format"]
    assert isinstance(formatting, dict)
    assert formatting["strict"] is True
    _ = assert_strict_schema(formatting["schema"])
    assert requests[0].extensions["timeout"]["read"] == 4.0
