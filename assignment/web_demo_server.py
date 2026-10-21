"""Serve the Vue writing desk and a bounded, validated JSON draft proxy."""

from http import HTTPStatus
from pathlib import Path
from uuid import uuid4

import anyio
import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import ValidationError

from agent.contracts import DraftRequest, DraftResponse, ErrorResponse

BACKEND = "http://127.0.0.1:8001"
HERE = Path(__file__).parent
PROXY_DEADLINE = 190.0
app = FastAPI()


@app.get("/health")
async def proxy_health() -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "vue-proxy"})


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(HERE / "web_chat.html")


@app.get("/web/{asset}", response_model=None)
async def web_asset(asset: str) -> FileResponse | JSONResponse:
    if asset not in {"web_app.js", "web_contract.js", "web_style.css"}:
        return JSONResponse({"detail": "Not found"}, status_code=404)
    return FileResponse(HERE / asset)


def failure(code: str, status: int) -> JSONResponse:
    messages = {
        "INVALID_INPUT": "입력 형식을 확인해 주세요.",
        "INVALID_RESPONSE": "응답 형식을 확인할 수 없습니다. 다시 시도해 주세요.",
        "TIMEOUT": "처리 시간이 초과됐습니다. 다시 시도해 주세요.",
        "MODEL_ERROR": "서버에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.",
    }
    return JSONResponse(
        {"status": "error", "requestId": str(uuid4()), "code": code, "message": messages[code]},
        status_code=status,
    )


@app.post("/api/drafts")
async def proxy_draft(req: Request) -> JSONResponse:
    try:
        body = DraftRequest.model_validate_json(await req.body())
    except ValidationError:
        return failure("INVALID_INPUT", 400)
    try:
        with anyio.fail_after(PROXY_DEADLINE):
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(185.0, connect=5.0, pool=5.0),
                follow_redirects=False,
            ) as client:
                upstream = await client.post(
                    f"{BACKEND}/api/drafts",
                    content=body.model_dump_json(by_alias=True),
                    headers={"content-type": "application/json"},
                )
        response = DraftResponse.validate_json(upstream.content)
        valid_status = upstream.status_code == HTTPStatus.OK
        if isinstance(response, ErrorResponse):
            valid_status = upstream.status_code >= HTTPStatus.BAD_REQUEST
        if not valid_status:
            return failure("INVALID_RESPONSE", 502)
    except (TimeoutError, httpx.TimeoutException):
        return failure("TIMEOUT", 504)
    except httpx.RequestError:
        return failure("MODEL_ERROR", 502)
    except ValidationError:
        return failure("INVALID_RESPONSE", 502)
    return JSONResponse(
        response.model_dump(mode="json", by_alias=True), status_code=upstream.status_code
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8600)
