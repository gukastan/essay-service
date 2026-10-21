"""Real FastAPI proxy against a synthetic upstream transport, never a model run."""

from unittest.mock import patch

import anyio
import httpx
import pytest
from fastapi.testclient import TestClient

import web_demo_server as web
from agent.contracts import ErrorResponse, NeedsInputResponse, ReadyResponse
from tests.test_flow_handoff import needs_input_fixture, quality_failure_fixture, ready_fixture

REQUEST = {"company": "예시", "role": "개발", "question": "경험", "experience": "행동"}


@pytest.mark.parametrize(
    ("response", "status"),
    [(ready_fixture(), 200), (needs_input_fixture(), 200), (quality_failure_fixture(), 422)],
)
def test_proxy_preserves_typed_response(
    response: ReadyResponse | NeedsInputResponse | ErrorResponse, status: int
) -> None:
    observed: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        observed.append(request)
        return httpx.Response(status, content=response.model_dump_json(by_alias=True))

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    with (
        patch("web_demo_server.httpx.AsyncClient", return_value=client),
        TestClient(web.app) as browser,
    ):
        result = browser.post("/api/drafts", json=REQUEST)
    assert result.status_code == status
    assert result.json() == response.model_dump(mode="json", by_alias=True)
    assert observed[0].method == "POST"
    assert str(observed[0].url) == "http://127.0.0.1:8001/api/drafts"
    assert b"experience" in observed[0].content


@pytest.mark.parametrize(
    ("body", "status"),
    [
        (b"not-json", 200),
        (b"{}", 200),
        (ready_fixture().model_dump_json(by_alias=True).encode(), 500),
        (quality_failure_fixture().model_dump_json(by_alias=True).encode(), 200),
    ],
)
def test_malformed_upstream_is_sanitized(body: bytes, status: int) -> None:
    client = httpx.AsyncClient(
        transport=httpx.MockTransport(lambda request: httpx.Response(status, content=body))
    )
    with (
        patch("web_demo_server.httpx.AsyncClient", return_value=client),
        TestClient(web.app) as browser,
    ):
        result = browser.post("/api/drafts", json=REQUEST)
    assert result.status_code == 502
    assert result.json()["code"] == "INVALID_RESPONSE"


def test_timeout_is_bounded_and_has_no_retry() -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        message = "private diagnostic"
        raise httpx.ReadTimeout(message)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    with (
        patch("web_demo_server.httpx.AsyncClient", return_value=client),
        TestClient(web.app) as browser,
    ):
        result = browser.post("/api/drafts", json=REQUEST)
    assert len(calls) == 1
    assert result.status_code == 504
    assert result.json()["code"] == "TIMEOUT"
    assert "private" not in result.text
    assert web.PROXY_DEADLINE < 195


def test_invalid_input_and_static_routes() -> None:
    with TestClient(web.app) as browser:
        assert browser.post("/api/drafts", json={}).status_code == 400
        assert browser.get("/").status_code == 200
        assert browser.get("/health").json() == {"status": "ok", "service": "vue-proxy"}
        assert browser.get("/web/web_app.js").status_code == 200
        assert browser.get("/web/secrets.env").status_code == 404
        assert browser.get("/chat/stream?message=private").status_code == 404


def test_total_deadline_cancels_a_stalled_upstream() -> None:
    calls: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        await anyio.sleep(1)
        return httpx.Response(200, content=ready_fixture().model_dump_json(by_alias=True))

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    with (
        patch("web_demo_server.httpx.AsyncClient", return_value=client),
        patch.object(web, "PROXY_DEADLINE", 0.01),
        TestClient(web.app) as browser,
    ):
        result = browser.post("/api/drafts", json=REQUEST)
    assert result.status_code == 504
    assert result.json()["code"] == "TIMEOUT"
    assert len(calls) == 1
