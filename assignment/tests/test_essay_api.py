from typing import Literal
from uuid import uuid4

import httpx2
import pytest
from pydantic import JsonValue, TypeAdapter

from agent.contracts import (
    DraftRequest,
    ErrorResponse,
    NeedsInputResponse,
    ReadyResponse,
    ReviewNeededResponse,
)
from agent.essay_graph import EssayWorkflow
from agent.settings import Settings
from server import create_app
from tests.test_flow_handoff import ready_fixture, review_needed_fixture


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("kind", "expected"),
    [
        ("ready", 200),
        ("needs", 200),
        ("quality", 200),
        ("config", 500),
        ("model", 502),
        ("timeout", 504),
    ],
)
async def test_post_drafts_maps_typed_outcomes_without_leaking_inputs(
    monkeypatch: pytest.MonkeyPatch,
    kind: Literal["ready", "needs", "quality", "config", "model", "timeout"],
    expected: int,
) -> None:
    request = DraftRequest(
        company="회사",
        role="개발",
        question="경험을 설명하세요.",
        experience="비공개 경험을 설명했다.",
    )
    result: ReadyResponse | ReviewNeededResponse | NeedsInputResponse | ErrorResponse
    match kind:
        case "ready":
            result = ready_fixture()
        case "needs":
            result = NeedsInputResponse(
                status="needs_input",
                request_id=uuid4(),
                message="경험 보완이 필요합니다.",
                missing_fields=("experience",),
                questions=("직접 수행한 일을 알려 주세요.",),
                reason_code="EXPERIENCE_INSUFFICIENT",
            )
        case "quality":
            result = review_needed_fixture()
        case "config":
            result = ErrorResponse(
                status="error",
                request_id=uuid4(),
                message="설정을 확인해 주세요.",
                code="CONFIG_ERROR",
            )
        case "model":
            result = ErrorResponse(
                status="error",
                request_id=uuid4(),
                message="모델을 사용할 수 없습니다.",
                code="MODEL_ERROR",
            )
        case "timeout":
            result = ErrorResponse(
                status="error",
                request_id=uuid4(),
                message="처리 시간이 초과됐습니다.",
                code="TIMEOUT",
            )

    async def fake_run(
        _self: EssayWorkflow, _request: DraftRequest
    ) -> ReadyResponse | ReviewNeededResponse | NeedsInputResponse | ErrorResponse:
        return result

    monkeypatch.setattr(EssayWorkflow, "run", fake_run)
    app = create_app(Settings(openai_api_key=None, openai_model=None))
    async with (
        app.router.lifespan_context(app),
        httpx2.AsyncClient(
            transport=httpx2.ASGITransport(app=app), base_url="http://fixture"
        ) as client,
    ):
        response = await client.post("/api/drafts", json=request.model_dump(by_alias=True))
    assert response.status_code == expected
    assert response.json()["status"] == result.status
    if result.status == "error":
        payload = TypeAdapter(dict[str, JsonValue]).validate_json(response.content)
        assert set(payload) == {"status", "requestId", "message", "code"}
        assert request.experience not in response.text
