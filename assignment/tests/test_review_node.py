"""F invokes the real SDK adapter against controlled HTTP responses."""

import httpx2
import pytest
from openai import AsyncOpenAI

from agent.budget import ExecutionBudget
from agent.flow_state import FlowStateError, require_ready_evaluation
from agent.nodes.review import ReviewNode
from agent.openai_llm import OpenAIModelProvider
from agent.providers import ProviderError
from agent.validate_evidence import evaluation_from_issues, general_issue
from tests.test_review_evidence import review_input
from tests.wire_fixture import JSON, assert_strict_schema, response_body


@pytest.mark.anyio
@pytest.mark.parametrize("fabricated", [True, False])
async def test_model_pass_cannot_override_code_failure(*, fabricated: bool) -> None:
    # Given
    context = review_input("90%를 달성했다." if fabricated else "실행했다.")
    model = evaluation_from_issues(context, ())
    requests: list[httpx2.Request] = []

    def respond(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, content=response_body(model.model_dump_json(by_alias=True)))

    budget = ExecutionBudget()
    async with (
        httpx2.AsyncClient(transport=httpx2.MockTransport(respond)) as transport,
        AsyncOpenAI(api_key="fixture", http_client=transport) as sdk,
    ):
        # When
        result = await ReviewNode(OpenAIModelProvider(sdk, "fixture-model")).evaluate(
            context, budget
        )
    # Then
    assert result.model.all_passed
    assert result.binding.evaluation.all_passed != fabricated
    assert result.binding.request_id == context.request_id
    assert result.binding.draft == context.draft
    assert len(requests) == budget.snapshot().model_calls == 1
    wire = JSON.validate_json(requests[0].content)
    assert isinstance(wire, dict)
    assert wire["input"] == context.model_dump_json(by_alias=True)
    assert wire["store"] is False
    formatting = wire["text"]
    assert isinstance(formatting, dict)
    schema = formatting["format"]
    assert isinstance(schema, dict)
    _ = assert_strict_schema(schema["schema"])


@pytest.mark.anyio
@pytest.mark.parametrize("route", ["D", "I"])
async def test_revision_evaluates_full_new_draft_and_keeps_semantic_failure(route: str) -> None:
    # Given
    context = review_input()
    revised = context.model_copy(
        update={
            "draft": context.draft.model_copy(
                update={"version": 2, "plan_version": 2 if route == "D" else 1}
            ),
            "plan": context.plan.model_copy(update={"version": 2 if route == "D" else 1}),
        }
    )
    inputs: list[str] = []

    def respond(request: httpx2.Request) -> httpx2.Response:
        wire = JSON.validate_json(request.content)
        assert isinstance(wire, dict)
        assert isinstance(wire["input"], str)
        inputs.append(wire["input"])
        response = (
            evaluation_from_issues(context, ())
            if len(inputs) == 1
            else evaluation_from_issues(
                revised,
                (general_issue("question_coverage", "문항의 실제 행동 설명이 빠졌습니다."),),
            )
        )
        return httpx2.Response(200, content=response_body(response.model_dump_json(by_alias=True)))

    budget = ExecutionBudget()
    async with (
        httpx2.AsyncClient(transport=httpx2.MockTransport(respond)) as transport,
        AsyncOpenAI(api_key="fixture", http_client=transport) as sdk,
    ):
        node = ReviewNode(OpenAIModelProvider(sdk, "fixture-model"))
        initial = await node.evaluate(context, budget)
        # When
        result = await node.evaluate(revised, budget)
    # Then
    assert initial.binding.evaluation.all_passed
    assert not result.binding.evaluation.all_passed
    assert inputs == [
        context.model_dump_json(by_alias=True),
        revised.model_dump_json(by_alias=True),
    ]
    assert budget.snapshot().model_calls == 2
    with pytest.raises(FlowStateError, match="STALE_EVALUATION"):
        require_ready_evaluation(initial.binding, context.request_id, revised.draft, revised.plan)


@pytest.mark.anyio
@pytest.mark.parametrize("attack", ["stale", "range", "fact_wording", "http", "json", "timeout"])
async def test_invalid_or_failed_model_review_never_returns_a_pass(attack: str) -> None:
    # Given
    context = review_input()
    calls: list[int] = []
    issue = general_issue("expression_kind", "표현 수정")
    if attack in {"range", "fact_wording"}:
        issue = issue.model_copy(
            update={
                "scope": "wording",
                "claim_ids": ("c1",),
                "start": 0,
                "end": 901 if attack == "range" else 5,
            }
        )
    model = evaluation_from_issues(context, (issue,))
    if attack == "stale":
        model = model.model_copy(update={"draft_version": 2})

    def respond(request: httpx2.Request) -> httpx2.Response:
        calls.append(1)
        if attack == "http":
            return httpx2.Response(500)
        if attack == "timeout":
            message = "private text"
            raise httpx2.ReadTimeout(message, request=request)
        body = "private invalid json" if attack == "json" else model.model_dump_json(by_alias=True)
        return httpx2.Response(200, content=response_body(body))

    budget = ExecutionBudget()
    async with (
        httpx2.AsyncClient(transport=httpx2.MockTransport(respond)) as transport,
        AsyncOpenAI(api_key="fixture", http_client=transport, max_retries=3) as sdk,
    ):
        # When / Then
        with pytest.raises((FlowStateError, ProviderError)):
            _ = await ReviewNode(OpenAIModelProvider(sdk, "fixture-model")).evaluate(
                context, budget
            )
    assert calls == [1]
    assert budget.snapshot().model_calls == 1


@pytest.mark.anyio
async def test_wording_rejects_later_occurrence_of_fact_text() -> None:
    # Given
    context = review_input()
    original = context.draft.claim_map[0]
    body = context.draft.draft.rstrip() + " " + original.text
    start = body.rindex(original.text)
    paragraph = context.draft.paragraphs[0].model_copy(update={"end": len(body)})
    context = context.model_copy(
        update={
            "draft": context.draft.model_copy(
                update={
                    "draft": body,
                    "paragraphs": (paragraph,),
                }
            )
        }
    )
    issue = general_issue("expression_kind", "표현 수정").model_copy(
        update={
            "scope": "wording",
            "claim_ids": (original.id,),
            "start": start,
            "end": start + len(original.text),
        }
    )
    model = evaluation_from_issues(context, (issue,))

    def respond(_request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(200, content=response_body(model.model_dump_json(by_alias=True)))

    budget = ExecutionBudget()
    async with (
        httpx2.AsyncClient(transport=httpx2.MockTransport(respond)) as transport,
        AsyncOpenAI(api_key="fixture", http_client=transport) as sdk,
    ):
        # When / Then
        with pytest.raises(ProviderError, match="INVALID_RESPONSE"):
            _ = await ReviewNode(OpenAIModelProvider(sdk, "fixture-model")).evaluate(
                context, budget
            )
    assert budget.snapshot().model_calls == 1
