"""Exercise the real essay graph through both FastAPI applications."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Literal, override
from unittest.mock import patch

import httpx
import pytest
from openai import AsyncOpenAI
from pydantic import BaseModel, JsonValue, TypeAdapter

import server
import web_demo_server as web
from agent.budget import ExecutionBudget
from agent.contracts import DraftRequest, EvaluationIssue, ResearchInput
from agent.nodes.revise import RevisionPatches
from agent.providers import ModelResult, ProviderError, StructuredModelRequest
from agent.settings import Settings
from agent.validate_evidence import ReviewInput, general_issue
from tests.test_essay_integration import ControlledProvider
from tests.test_personal_analysis import request

pytest_plugins = ("tests.test_essay_integration",)


@dataclass(frozen=True)
class Case:
    reviews: tuple[Literal["pass", "plan", "wording", "missing"], ...]
    status: int
    code: str | None
    calls: int
    revisions: int


@asynccontextmanager
async def connected_apps(
    monkeypatch: pytest.MonkeyPatch, provider: ControlledProvider | None
) -> AsyncGenerator[httpx.AsyncClient]:
    if provider is not None:

        def provider_factory(_client: AsyncOpenAI, _model: str | None) -> ControlledProvider:
            return provider

        monkeypatch.setattr(server, "OpenAIModelProvider", provider_factory)
    api = server.create_app(Settings(openai_api_key=None, openai_model=None))
    client_type = httpx.AsyncClient
    browser = httpx.AsyncClient(
        transport=httpx.ASGITransport(app=web.app), base_url="http://vue-proxy"
    )

    def client_factory(**_kwargs: object) -> httpx.AsyncClient:
        return client_type(transport=httpx.ASGITransport(app=api), base_url=web.BACKEND)

    async with api.router.lifespan_context(api), browser:
        with patch("web_demo_server.httpx.AsyncClient", side_effect=client_factory):
            yield browser


@pytest.mark.anyio
@pytest.mark.parametrize(
    "case",
    [
        Case(("pass",), 200, None, 4, 0),
        Case(("plan", "pass"), 200, None, 6, 1),
        Case(("wording", "pass"), 200, None, 6, 1),
        Case(("missing",), 200, None, 4, 0),
        Case(("plan", "plan"), 422, "QUALITY_CHECK_FAILED", 6, 1),
    ],
)
async def test_proxy_api_graph_real_roles_and_terminal_status(
    monkeypatch: pytest.MonkeyPatch,
    researched: list[ResearchInput],
    case: Case,
) -> None:
    source = request().model_copy(update={"job_posting_text": "협업을 요구한다."})
    provider = ControlledProvider(source, case.reviews)
    async with connected_apps(monkeypatch, provider) as browser:
        result = await browser.post("/api/drafts", json=source.model_dump(by_alias=True))
    assert result.status_code == case.status
    body = TypeAdapter(dict[str, JsonValue]).validate_json(result.content)
    assert body["status"] == (
        "error" if case.code else "needs_input" if case.reviews == ("missing",) else "ready"
    )
    assert body.get("code") == case.code
    if body["status"] == "ready":
        assert body["characterCount"] == 900
        assert body["usage"] == {
            "modelCalls": case.calls,
            "revisionCount": case.revisions,
        }
        evidence = body["evidence"]
        assert isinstance(evidence, dict)
        requirements = evidence["jobRequirements"]
        assert isinstance(requirements, list)
        first = requirements[0]
        assert isinstance(first, dict)
        assert first["sourceIds"] == ["s1"]
    assert provider.roles.count("analysis") == 1
    assert provider.roles.count("writer") == 1 + case.revisions
    assert provider.roles.count("review") == 1 + case.revisions
    assert len(researched) == 1


@pytest.mark.anyio
async def test_proxy_api_parallel_requests_keep_results_isolated(
    monkeypatch: pytest.MonkeyPatch, researched: list[ResearchInput]
) -> None:
    source = request().model_copy(update={"job_posting_text": "협업을 요구한다."})
    provider = ControlledProvider(source)
    async with connected_apps(monkeypatch, provider) as browser:
        first, second = await asyncio.gather(
            browser.post("/api/drafts", json=source.model_dump(by_alias=True)),
            browser.post("/api/drafts", json=source.model_dump(by_alias=True)),
        )
    assert first.status_code == second.status_code == 200
    first_body = TypeAdapter(dict[str, JsonValue]).validate_json(first.content)
    second_body = TypeAdapter(dict[str, JsonValue]).validate_json(second.content)
    assert first_body["requestId"] != second_body["requestId"]
    assert first_body["usage"] == {"modelCalls": 4, "revisionCount": 0}
    assert second_body["usage"] == {"modelCalls": 4, "revisionCount": 0}
    assert len(researched) == 2


class MixedProvider(ControlledProvider):
    writer_schemas: list[type[BaseModel]]

    def __init__(self, source: DraftRequest) -> None:
        super().__init__(source, ("wording", "pass"))
        self.writer_schemas = []

    @override
    def review_issues(self, context: ReviewInput) -> tuple[EvaluationIssue, ...]:
        if self.roles.count("review") == 1:
            return (
                general_issue("question_coverage", "계획 변경이 필요합니다."),
                *super().review_issues(context),
            )
        return ()

    @override
    async def generate[T: BaseModel](
        self, request: StructuredModelRequest[T], budget: ExecutionBudget
    ) -> ModelResult[T]:
        if request.role == "writer":
            self.writer_schemas.append(request.schema)
        return await super().generate(request, budget)


@pytest.mark.anyio
async def test_mixed_plan_and_wording_feedback_replans_before_wording(
    monkeypatch: pytest.MonkeyPatch, researched: list[ResearchInput]
) -> None:
    source = request().model_copy(update={"job_posting_text": "협업을 요구한다."})
    provider = MixedProvider(source)
    async with connected_apps(monkeypatch, provider) as browser:
        result = await browser.post("/api/drafts", json=source.model_dump(by_alias=True))
    assert result.status_code == 200
    assert provider.writer_schemas != []
    assert len(provider.writer_schemas) == 2
    assert all(schema is not RevisionPatches for schema in provider.writer_schemas)
    assert result.json()["usage"] == {"modelCalls": 6, "revisionCount": 1}
    assert len(researched) == 1


@pytest.mark.anyio
async def test_wording_repair_rechecks_entire_draft_and_rejects_new_plan_failure(
    monkeypatch: pytest.MonkeyPatch, researched: list[ResearchInput]
) -> None:
    source = request().model_copy(update={"job_posting_text": "협업을 요구한다."})
    provider = ControlledProvider(source, ("wording", "plan"))
    async with connected_apps(monkeypatch, provider) as browser:
        result = await browser.post("/api/drafts", json=source.model_dump(by_alias=True))
    assert result.status_code == 422
    assert result.json()["code"] == "QUALITY_CHECK_FAILED"
    assert provider.roles == ["analysis", "writer", "review", "writer", "review"]
    assert len(researched) == 1


class FailingProvider(ControlledProvider):
    code: Literal["MODEL_ERROR", "TIMEOUT"]
    attempts: int

    def __init__(self, source: DraftRequest, code: Literal["MODEL_ERROR", "TIMEOUT"]) -> None:
        super().__init__(source)
        self.code = code
        self.attempts = 0

    @override
    async def generate[T: BaseModel](
        self, request: StructuredModelRequest[T], budget: ExecutionBudget
    ) -> ModelResult[T]:
        if request.role == "analysis":
            self.attempts += 1
            raise ProviderError(self.code)
        return await super().generate(request, budget)


@pytest.mark.anyio
@pytest.mark.parametrize(("code", "status"), [("MODEL_ERROR", 502), ("TIMEOUT", 504)])
async def test_proxy_graph_operational_errors_are_sanitized_without_retry(
    monkeypatch: pytest.MonkeyPatch,
    researched: list[ResearchInput],
    code: Literal["MODEL_ERROR", "TIMEOUT"],
    status: int,
) -> None:
    source = request().model_copy(update={"job_posting_text": "협업을 요구한다."})
    provider = FailingProvider(source, code)
    async with connected_apps(monkeypatch, provider) as browser:
        result = await browser.post("/api/drafts", json=source.model_dump(by_alias=True))
    assert result.status_code == status
    body = TypeAdapter(dict[str, JsonValue]).validate_json(result.content)
    assert body["code"] == code
    assert set(body) == {"status", "requestId", "message", "code"}
    assert provider.attempts == 1
    assert source.experience not in result.text
    assert len(researched) <= 1


@pytest.mark.anyio
async def test_proxy_graph_without_model_configuration_reports_500(
    monkeypatch: pytest.MonkeyPatch, researched: list[ResearchInput]
) -> None:
    source = request().model_copy(update={"job_posting_text": "협업을 요구한다."})
    async with connected_apps(monkeypatch, None) as browser:
        result = await browser.post("/api/drafts", json=source.model_dump(by_alias=True))
    assert result.status_code == 500
    assert result.json()["code"] == "CONFIG_ERROR"
    assert source.experience not in result.text
    assert len(researched) <= 1
