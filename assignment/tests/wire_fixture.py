# pyright: reportUnnecessaryComparison=false, reportUnreachable=false
# Exhaustive recursive JSON alternatives intentionally retain an assert_never guard.
"""Local HTTP wire fixture; real SDK traffic and no external connection."""

import json
from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from queue import Queue
from threading import Thread
from typing import Final, assert_never, override

from pydantic import JsonValue, TypeAdapter

JSON: Final = TypeAdapter(JsonValue)


def response_body(
    text: str, *, status: str = "completed", refusal: bool = False, search: bool = False
) -> bytes:
    content: dict[str, JsonValue] = (
        {"type": "refusal", "refusal": text}
        if refusal
        else {"type": "output_text", "text": text, "annotations": []}
    )
    output: list[JsonValue] = [
        {
            "type": "message",
            "id": "msg_fixture",
            "role": "assistant",
            "status": "completed",
            "content": [content],
        }
    ]
    if search:
        _ = output.insert(
            0,
            {
                "type": "web_search_call",
                "id": "ws_fixture",
                "status": "completed",
                "action": {"type": "search", "query": "public company role"},
            },
        )
    return json.dumps(
        {
            "id": "resp_fixture",
            "object": "response",
            "created_at": 1,
            "model": "fixture-model",
            "status": status,
            "output": output,
            "usage": {"input_tokens": 11, "output_tokens": 7, "total_tokens": 18},
            "incomplete_details": {"reason": "max_output_tokens"}
            if status == "incomplete"
            else None,
        }
    ).encode()


def research_body(company: str = "회사") -> bytes:
    return response_body(
        json.dumps(
            {
                "resolvedCompany": company,
                "sources": [],
                "companyFacts": [],
                "jobRequirements": [],
                "gaps": [],
            }
        ),
        search=True,
    )


@dataclass(frozen=True, slots=True)
class HttpReply:
    body: bytes
    status: int = 200


@dataclass(frozen=True, slots=True)
class WireServer:
    base_url: str
    requests: Queue[bytes]


@contextmanager
def serve_wire(reply: Callable[[bytes], HttpReply]) -> Generator[WireServer]:
    """Own ephemeral local HTTP server, thread and request capture queue."""
    requests: Queue[bytes] = Queue()

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            payload = self.rfile.read(int(self.headers["Content-Length"]))
            _ = requests.put(payload)
            response = reply(payload)
            _ = self.send_response(response.status)
            _ = self.send_header("Content-Type", "application/json")
            _ = self.send_header("Content-Length", str(len(response.body)))
            _ = self.send_header("Connection", "close")
            _ = self.end_headers()
            try:
                _ = self.wfile.write(response.body)
            except BrokenPipeError:
                return

        @override
        def log_message(self, format: str, *args: str | int) -> None:
            """Synthetic fixture contains no operational logging."""

    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        thread = Thread(target=server.serve_forever, daemon=True)
        _ = thread.start()
        try:
            yield WireServer(f"http://127.0.0.1:{server.server_port}/v1", requests)
        finally:
            _ = server.shutdown()
            _ = thread.join(timeout=3)
            assert not thread.is_alive()


def assert_strict_schema(value: JsonValue) -> None:
    """Verify every emitted object and union is accepted by strict structured output."""
    match value:
        case dict():
            assert "discriminator" not in value
            assert "oneOf" not in value
            assert "default" not in value
            if value.get("type") == "object":
                properties = value.get("properties")
                assert isinstance(properties, dict)
                assert value.get("additionalProperties") is False
                required = value.get("required", [])
                assert isinstance(required, list)
                assert set(required) == set(properties)
            for child in value.values():
                _ = assert_strict_schema(child)
        case list():
            for child in value:
                _ = assert_strict_schema(child)
        case str() | int() | float() | None:
            return
        case unreachable:
            assert_never(unreachable)
