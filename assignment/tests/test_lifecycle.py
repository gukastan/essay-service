"""Actual app lifespan and MCP resources with isolated request contexts."""

import os
from pathlib import Path
from typing import Literal, Protocol

import anyio
import httpx2
import pytest
from pydantic import SecretStr

from agent.contracts import DraftRequest
from agent.deps import WorkflowDeps
from agent.settings import Settings, model_client
from server import create_app


class RuntimeState(Protocol):
    def __getattr__(self, key: Literal["deps"]) -> WorkflowDeps: ...


def runtime_deps(state: RuntimeState) -> WorkflowDeps:
    return state.__getattr__("deps")


@pytest.mark.anyio
async def test_real_lifespan_reuses_dependencies_and_never_creates_database(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Given
    _ = monkeypatch.chdir(tmp_path)
    for name in ("LANGCHAIN_TRACING", "LANGCHAIN_TRACING_V2", "LANGSMITH_TRACING"):
        _ = monkeypatch.setenv(name, "true")
    app = create_app(Settings(openai_api_key=None, openai_model=None))
    draft = DraftRequest(company="회사", role="직무", question="문항", experience="경험")
    # When
    async with app.router.lifespan_context(app):
        deps = runtime_deps(app.state)
        first, second = deps.new_request(draft), deps.new_request(draft)
        async with httpx2.AsyncClient(
            transport=httpx2.ASGITransport(app=app), base_url="http://fixture"
        ) as client:
            health1, health2 = await client.get("/health"), await client.get("/health")
            for method, path in (
                ("GET", "/chat/stream"),
                ("POST", "/chat"),
            ):
                response = await client.request(method, path)
                assert response.status_code == 404
                assert "prompt" not in response.text
            invalid = await client.post("/api/drafts", json={})
            assert invalid.status_code == 400
            assert invalid.json()["code"] == "INVALID_INPUT"
            unavailable = await client.post("/api/drafts", json=draft.model_dump(by_alias=True))
            assert unavailable.status_code == 500
            assert unavailable.json()["code"] == "CONFIG_ERROR"
        assert deps is runtime_deps(app.state)
        assert deps.mcp.connected
        assert first.request_id != second.request_id
        assert first.budget is not second.budget
        assert first.state is not second.state
        assert health1.json() == health2.json()
        assert health1.json()["mcpConnected"] is True
        assert health1.json()["pipelineAvailable"] is True
        assert health1.json()["creationCount"] == 1
        assert all(
            os.environ[name] == "false"
            for name in ("LANGCHAIN_TRACING", "LANGCHAIN_TRACING_V2", "LANGSMITH_TRACING")
        )
    # Then
    assert not deps.mcp.connected
    assert not await anyio.to_thread.run_sync(lambda: list(tmp_path.glob("**/*.db")))
    assert not hasattr(app.state, "deps")


@pytest.mark.anyio
async def test_server_settings_ignore_inherited_provider_destination(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given
    _ = monkeypatch.setenv("OPENAI_BASE_URL", "http://invalid.example/sentinel")
    config = Settings(openai_api_key=SecretStr("fixture-not-a-real-key"), openai_model="fixture")
    # When
    async with model_client(config) as client:
        # Then: inspect config only, make no external request.
        assert client is not None
        assert str(client.base_url) == "https://api.openai.com/v1/"
        assert client.max_retries == 0
