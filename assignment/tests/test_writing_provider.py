"""Real OpenAI adapter at a controlled HTTP boundary; no live network/model calls."""

import httpx2
import pytest
from openai import AsyncOpenAI

from agent.budget import ExecutionBudget
from agent.nodes.revise import RevisionNode, RevisionPatches
from agent.nodes.write import WriteNode
from agent.openai_llm import OpenAIModelProvider
from agent.providers import ProviderError
from tests.test_writing_nodes import evaluated, generated, require_plan, writing_state
from tests.wire_fixture import JSON, assert_strict_schema, response_body


@pytest.mark.anyio
@pytest.mark.parametrize("revision", [False, True])
async def test_writing_schema_and_budget_cross_real_sdk_wire(*, revision: bool) -> None:
    # Given
    budget = ExecutionBudget()
    state = writing_state(budget)
    reservation = None
    value = generated(require_plan(state)).model_dump_json(by_alias=True)
    if revision:
        patch = evaluated(state)
        reservation = await budget.reserve_revision("I")
        value = RevisionPatches(draft_version=1, plan_version=1, patches=(patch,)).model_dump_json(
            by_alias=True
        )
    requests: list[httpx2.Request] = []

    def respond(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, content=response_body(value))

    async with (
        httpx2.AsyncClient(transport=httpx2.MockTransport(respond)) as transport,
        AsyncOpenAI(api_key="fixture", http_client=transport, max_retries=3) as sdk,
    ):
        provider = OpenAIModelProvider(sdk, "fixture-model")
        # When
        if reservation is None:
            result = await WriteNode(provider).run(state, budget)
        else:
            result = await RevisionNode(provider).run(state, budget, reservation)
    # Then
    assert result.get("draft_envelope") is not None
    assert len(requests) == 1
    assert budget.snapshot().model_calls == 1
    wire = JSON.validate_json(requests[0].content)
    assert isinstance(wire, dict)
    assert wire["store"] is False
    assert "tools" not in wire
    formatting = wire["text"]
    assert isinstance(formatting, dict)
    schema_format = formatting["format"]
    assert isinstance(schema_format, dict)
    assert schema_format["strict"] is True
    _ = assert_strict_schema(schema_format["schema"])


@pytest.mark.anyio
@pytest.mark.parametrize("failure", ["http", "invalid_json", "timeout"])
async def test_writer_operational_errors_are_sanitized_without_retry(failure: str) -> None:
    # Given
    budget = ExecutionBudget()
    state = writing_state(budget)
    calls: list[int] = []

    def respond(request: httpx2.Request) -> httpx2.Response:
        calls.append(1)
        if failure == "http":
            return httpx2.Response(500, json={"error": {"message": "private failure"}})
        if failure == "timeout":
            message = "private failure"
            raise httpx2.ReadTimeout(message, request=request)
        return httpx2.Response(200, content=response_body("invalid private response"))

    async with (
        httpx2.AsyncClient(transport=httpx2.MockTransport(respond)) as transport,
        AsyncOpenAI(api_key="fixture", http_client=transport, max_retries=3) as sdk,
    ):
        # When / Then
        with pytest.raises(ProviderError) as error:
            _ = await WriteNode(OpenAIModelProvider(sdk, "fixture-model")).run(state, budget)
    assert (
        error.value.code
        == {"http": "MODEL_ERROR", "invalid_json": "INVALID_RESPONSE", "timeout": "TIMEOUT"}[
            failure
        ]
    )
    assert "private" not in str(error.value)
    assert calls == [1]
    assert budget.snapshot().model_calls == 1
