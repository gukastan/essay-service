"""Run the real API and Vue proxy with a deterministic model for browser regression."""

import asyncio
import json
import socket
import sys
from datetime import UTC, datetime
from typing import Literal, cast
from unittest.mock import patch
from uuid import UUID

import uvicorn
from openai import AsyncOpenAI

import server
import web_demo_server as web
from agent.budget import ExecutionBudget, OperationContext
from agent.contracts import (
    DraftRequest,
    JobRequirement,
    ResearchInput,
    ResearchResult,
    UserProvidedSource,
)
from agent.nodes.research import ResearchNode, ResearchSuccess
from agent.settings import Settings
from tests.test_essay_integration import ControlledProvider
from tests.test_personal_analysis import request


async def research(
    _self: ResearchNode,
    _input: ResearchInput | DraftRequest,
    budget: ExecutionBudget,
    _request_id: UUID,
) -> ResearchSuccess:
    async def result(_context: OperationContext) -> ResearchSuccess:
        return ResearchSuccess(
            result=ResearchResult(
                resolved_company="회사",
                sources=(
                    UserProvidedSource(
                        id="s1",
                        kind="user_provided",
                        title="ESSAY-16 통제 공고",
                        checked_at=datetime.now(UTC),
                        excerpt="협업을 요구한다.",
                    ),
                ),
                company_facts=(),
                job_requirements=(
                    JobRequirement(id="j1", text="협업을 요구한다.", source_ids=("s1",)),
                ),
                gaps=(),
            ),
            tool_calls_reported=0,
            usage=None,
        )

    return await budget.run_native_research(result)


def listening_socket() -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", 0))
    sock.listen(128)
    sock.settimeout(0.0)
    return sock


async def main() -> None:
    source = request().model_copy(update={"job_posting_text": "협업을 요구한다."})
    provider = ControlledProvider(source)

    def provider_factory(_client: AsyncOpenAI, _model: str | None) -> ControlledProvider:
        return provider

    with (
        patch.object(server, "OpenAIModelProvider", provider_factory),
        patch.object(ResearchNode, "run", research),
    ):
        api = server.create_app(Settings(openai_api_key=None, openai_model=None))

        @api.post("/__fixture/{mode}")
        async def set_mode(mode: Literal["pass", "missing", "quality"]) -> dict[str, str]:
            provider.roles.clear()
            provider.reviews = ("plan", "plan") if mode == "quality" else (mode,)
            return {"mode": mode}

        api_socket, proxy_socket = listening_socket(), listening_socket()
        api_port = cast("tuple[str, int]", api_socket.getsockname())[1]
        proxy_port = cast("tuple[str, int]", proxy_socket.getsockname())[1]
        web.BACKEND = f"http://127.0.0.1:{api_port}"
        api_server = uvicorn.Server(
            uvicorn.Config(api, host="127.0.0.1", log_level="error", access_log=False)
        )
        proxy_server = uvicorn.Server(
            uvicorn.Config(web.app, host="127.0.0.1", log_level="error", access_log=False)
        )
        api_task = asyncio.create_task(api_server.serve(sockets=[api_socket]))
        proxy_task = asyncio.create_task(proxy_server.serve(sockets=[proxy_socket]))
        try:
            while not (api_server.started and proxy_server.started):
                if api_task.done() or proxy_task.done():
                    raise RuntimeError
                await asyncio.sleep(0.05)
            _ = sys.stdout.write(json.dumps({"apiPort": api_port, "proxyPort": proxy_port}) + "\n")
            _ = sys.stdout.flush()
            _ = await asyncio.to_thread(sys.stdin.readline)
        finally:
            api_server.should_exit = True
            proxy_server.should_exit = True
            _ = await asyncio.gather(api_task, proxy_task)


if __name__ == "__main__":
    asyncio.run(main())
