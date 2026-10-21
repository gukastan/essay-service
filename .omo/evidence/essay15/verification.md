# ESSAY-15 Vue verification

2026-10-21. Implemented in the provided Vue shell and FastAPI proxy; existing Next.js code is unchanged. No paid model, MCP research, or ESSAY-14 integrated generation was run. Browser responses below are explicitly synthetic, not evidence of essay quality.

## Reproduction and binary observables

Commands run from `assignment/`. Raw command output is under `.omo/evidence/essay15/` at repository root. No ulw-loop attempt exists (`ulw-loop status` returned ULW_LOOP_PLAN_MISSING).

| Scenario | Exact invocation | Binary observable | Artifact |
| --- | --- | --- | --- |
| FastAPI proxy forwards typed ready 200, needs_input 200, quality 422 by POST body; malformed upstream is sanitized; invalid input; allowlisted assets; legacy SSE absent | `.venv/bin/python -m pytest tests/test_web_proxy.py -q` | 10 passed; status/content assertions; request URL contains no experience | `.omo/evidence/essay15/proxy-tests.txt` |
| Read timeout and stalled upstream total deadline | Same pytest invocation | one call, TIMEOUT 504; actual anyio deadline reduced to 0.01s for stalled fixture; configured production bound 190s < client 195s | same artifact |
| LF normalization, astral code points at 800/801/1000/1001, unsafe links, wrong offsets/variants/status | `node tests/test_web_contract.mjs` | all assertions pass; rejects malformed ready | `.omo/evidence/essay15/contract-tests.txt` |
| Browser form validation, immutable request snapshot, POST, provenance view, edit/count/copy, denied clipboard, needs-input/quality separation, preserved input/result, malformed response, duplicate lock, cancel, deadline, overflow | Start `.venv/bin/python -m uvicorn web_demo_server:app --host 127.0.0.1 --port 8615`; run `node tests/test_web_browser.cjs` | 4 configurations pass 12 scenarios each; zero page errors; no horizontal overflow; clipboard equals edited text | `browser-results.json`, `.omo/evidence/essay15/browser-tests.txt`, 24 PNG captures beside this report |
| Strict Python typecheck | `.venv/bin/basedpyright web_demo_server.py tests/test_web_proxy.py` | 0 errors, warnings, notes | `.omo/evidence/essay15/typecheck.txt` |
| Python lint | `.venv/bin/ruff check web_demo_server.py tests/test_web_proxy.py` | All checks passed | `.omo/evidence/essay15/lint.txt` |

The browser driver uses installed real Chrome via bundled Playwright (override module location with PLAYWRIGHT_PATH). It intercepts only `/api/drafts`; the page/assets are served by a real local FastAPI process and Vue is loaded from its pinned CDN URL. Proxy tests use FastAPI TestClient with synthetic httpx transport. These are distinct from an actual ESSAY-14 backend, which does not yet expose the completed generation flow. The 195-second client deadline test uses Chrome's virtual clock; no claim of a 195-second wall-clock run is made. Client cancellation aborts fetch and preserves content; end-to-end server/model cancellation remains ESSAY-14/16 integration scope.

## Requirement mapping

- Four required fields plus optional posting URL/body; code-point length validation matches request limits. Request is JSON POST, with immutable snapshot bound to each accepted result.
- Ready shows selected exact experience quotes, full original snapshot, source title/link/check date, explicit user_provided label, company facts, job fit reasons and matched experience/requirements, and claim kinds. Vue interpolation escapes response text; unsafe source URLs are rejected.
- Editing identifies the unreviewed revision; LF-normalized current text is copied even outside 801–1000. Clipboard denial gives direct-copy instructions.
- Pending locks input and result editing, prevents duplicate requests, offers cancellation, uses a single generic processing message and 195000ms deadline. No fabricated stage events or full prompt view remain.
- needs_input displays actual missing fields/questions. Quality 422 displays generation failure, never invents missing fields or exposes rejected draft. All failed attempts preserve current input and earlier edited result.
- Proxy parses request/response with existing Pydantic contracts, uses 185s HTTP read / 5s connect and pool timeouts inside a 190s total deadline, no retries/redirect following. `/health` reports only the local vue-proxy service; it is not a backend/model health guarantee.

## Visual review

Fresh matrix: widths 390 and 1440, system light and dark, each in empty/pending/ready/needs/quality/timeout states. Files follow `{width}-{theme}-{state}.png`. Every capture is a full document screenshot including end content. Mobile uses one column; desktop uses input/result columns; the document owns scrolling. Fields and buttons use visible labels, focus rings, and minimum 48px controls.

Independent reviewer `/root` inspected all 24 captures and reported: “No clipping, overlap, or unreadable state found; pending controls and preserved prior result visible, needs vs quality vs timeout distinct.” This is independent visual acceptance of this matrix, not live-model content acceptance. Executor also opened 390-light-ready directly. No exact visual clone was requested; source design is `DESIGN.md` adapted from the preserved essay design contract.

Limitations: no Lighthouse score or screen-reader audit was produced. The bundled accent-stripe checker could not execute under available Node because its extensionless TypeScript import failed (raw diagnostic `.omo/evidence/essay15/accent-stripes.txt`); direct CSS inspection shows only neutral full borders/dividers and input-validation borders. Image self-diff (`capture-integrity.json`) checks capture decode/dimensions only and is NOT a fidelity metric or independent approval. React tooling is inapplicable to this Vue assignment. Real API/model/MCP integration and full service regression remain ESSAY-14/16/17 scope.

## Integration review repair: default backend port

The independent integration review found the inherited 8100 proxy target disagreed with `run.sh` and README's default 8001. `web_demo_server.py` now forwards to `http://127.0.0.1:8001/api/drafts`. No environment/configuration surface was added.

Regression: updated the real FastAPI/synthetic-transport test to assert the literal documented target, then ran it before changing the proxy. All three ready/needs_input/quality forwarding variants failed on 8100 versus 8001 (`port-regression-before.txt`). After the one-line proxy fix, `.venv/bin/python -m pytest tests/test_web_proxy.py -q` passes all 10 tests (`proxy-tests.txt`), including the actual observed outgoing URL assertion. Ruff and basedpyright were rerun clean (`lint.txt`, `typecheck.txt`); JS boundary tests also pass. No rendered UI changed, so the existing independently reviewed screenshot matrix remains applicable. This verifies routing to the default backend port; it does not claim the pending ESSAY-14 endpoint is implemented.
