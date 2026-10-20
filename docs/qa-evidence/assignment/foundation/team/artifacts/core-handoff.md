# ESSAY-19 foundation core handoff

Owner A, shared checkout `/Users/jay/Projects/essay-service`. Product source is stable. No paid requests, commits, pushes, Jira changes, root Next.js edits, source Downloads edits, or previous QA edits were made by A.

## Delivered

- Frozen camelCase Pydantic contracts live in `contract_input.py`, `contract_evidence.py`, `contract_results.py`, reexported from `contracts.py`. Unknown fields are rejected. Domain strings preserve wording/whitespace while normalizing CRLF/CR to LF. Lengths/offsets use Python Unicode code points. Evidence bounds are checked before slicing. Numeric/boolean optional input and malformed URL ports are rejected. Revision counters reject booleans and noninteger values.
- `state.py` exports actual LangGraph-compatible TypedDict annotations, immutable-context reducers, monotonic revision reducer, and fresh request state. `deps.py` provides frozen shared WorkflowDeps and fresh RequestContext. Runtime budgets remain outside graph state. No business graph, prompts for four roles, or draft API is installed.
- `budget.py` owns atomic AnyIO reservations, per-role call limits, output capacity 18,000, model max6 (normal4), search2/page3, hosted reservation2, monotonic request180/research45/model30, active cancellation and no refunds. Cancellation while awaiting the reservation lock permanently stops that budget. Provider/MCP timeout permanently stops later transmissions.
- `openai_llm.py` provides one structured Responses call per requested role; `research.py` makes exactly one hosted Responses call with required web_search, sources inclusion, max_tool_calls2, output3000, store=false and max_retries0. No summary call follows. `provider_schema.py` turns domain schema optional defaults into strict required/nullable wire objects, replaces oneOf with anyOf and removes discriminator/default. `response_wire.py` revalidates SDK output containers/variants and usage before consuming them because the installed SDK permissively constructs response objects. Refusal, incomplete, malformed and provider failures expose sanitized typed codes.
- `mcp_client.py` shares a real stdio FastMCP Client and reserves model1/hosted2 before sending. Only projected company/role/optional posting data enter tool arguments; requestId/remaining timeout enter MCP metadata. The server strips only five standard SDK-added protocol metadata fields and strictly rejects other unknown fields or timeout escalation. Results are schema-validated and request correlation checked. Exact whitelisted errors are preserved without forwarding raw content; MCP REQUEST_TIMEOUT(-32001) is recognized. Hosted reported actions/counts remain distinct from capacity reserved.
- `mcp_server.py` retains the actual MCP/lifespan architecture with injectable ResearchProvider, default reused SDK client, and callable research_company_role. Output is explicitly `verification: unverified`; official identity/source checks remain ESSAY-10.
- `server.py` creates/closes one reused SDK pool and MCP connection per lifespan, advertises honest config readiness, and does not load legacy graph/SQLite/chat/SSE/educational retry. `/api/drafts` remains404 until ESSAY-14. stdio keep_alive=false plus shielded client.close ensures owned child teardown. `settings.py` reads assignment/.env only, requires key+model at invocation, explicitly pins official API origin to avoid inherited OPENAI_BASE_URL redirection, and disables inherited LangChain/LangSmith/OTEL tracing.
- Python3.12.15 environment installed; direct packages exactly pinned in pyproject.toml, full uv.lock and hash-bearing requirements.txt exported. SDK3.35.1 uses httpx2 natively. Root requirements/Node environment unchanged. Public interface details are in `api-contract.md`.

## Direct evidence and invocations

All paths below are relative to repo root. A records under `.omo/evidence/essay19/core/` (ulw-loop status reported no active plan/attempt).

| Scenario | Invocation (assignment cwd unless stated) | Binary observable | Captured artifact |
|---|---|---|---|
| Domain boundaries, atomics/deadlines, actual LangGraph reducer compatibility | `.venv/bin/python -m pytest tests/test_contracts.py tests/test_budget.py tests/test_state.py -q` | 89 passed after fixes | `contracts-budget-state.txt` |
| Real SDK HTTP and real stdio MCP normal/error/correlation regressions | `.venv/bin/python -m pytest tests/test_contracts.py tests/test_budget.py tests/test_state.py tests/test_provider.py tests/test_mcp.py -q` |107 passed | `pytest-third.txt` |
| Malformed SDK container and actual MCP protocol timeout correction | `.venv/bin/python -m pytest tests/test_provider.py tests/test_mcp_control.py tests/test_mcp.py -q` |28 passed | `edge-fixed.txt` |
| First full offline suite before final newly added edges | `.venv/bin/python -m pytest -q` |121 passed,1 paid opt-in skipped | `pytest-full.txt` |
| Subsequent full offline regression | `.venv/bin/python -m pytest -q` |130 passed,1 test-only RuntimeState assertion failed,1 paid skipped; preserved red receipt; B corrected the test protocol afterward | `pytest-final.txt` (red receipt, not claimed final pass) |
| Strict typing of all foundation/test files | `.venv/bin/basedpyright --outputjson` |0 errors/0 warnings over32 files | `typecheck-final.json` |
| Strict Ruff and formatting | `.venv/bin/ruff check --output-format concise`; `.venv/bin/ruff format --check` |All checks passed; all files formatted | `ruff-final.txt`, `format-final.txt` |
| Programming no-excuse check | installed `check-no-excuse-rules.py` over17 owned product Python files |0 violations; largest module173 pure LOC | `no-excuse-final.txt`, `source-manifest.json` |
| Installed runtime and SDK API compatibility | Python introspection of package versions, Client.call_tool, Responses.create, model_client |max_retries0, official base URL, expected actual SDK fields, paid_requests0 | `compatibility.json`, `research-wire-schema.json` |
| Reproducible clean startup/shutdown | C-owned `bash run.sh` harness; leader final-source smoke |C5 runtime scenarios passed with final child teardown; leader smoke passed source hashes stable | `docs/qa-evidence/assignment/foundation/runtime/runtime-result.json`; leader report authoritative |

Final combined offline run is owned by B and must supersede the explicitly preserved red lifecycle assertion receipt above. Paid compatibility is owned by the leader and is NOT claimed by A. A's dependency/schema evidence proves API availability and mocked-wire compatibility only.

## Architectural review

Each module has one boundary responsibility; models are parsed at input/SDK/MCP seams. No new Any/cast/type-ignore or broad exception catches. Existing legacy files remain reference-only. Mutable state is confined to the documented request budget, graph state, and lifespan holder. Explicit typed errors contain fixed codes only. Public SDK action matches retain exhaustive assertions; narrow `reportUnnecessaryComparison=false` handles the checker considering that final assertion redundant. Ruff retains ALL with documented project exceptions for self-describing schema names, fixed error codes, public reexports and standard pytest constructs. No product file exceeds200 pure LOC.

## Remaining scope

Official source verification, real four-role task prompts, full business graph, POST draft response, Vue service UI, complete browser/model QA, author factuality approval and submission bundle remain future tickets. The only current readiness claim is foundation startup/configuration and verified primitives. Small live model/search compatibility remains the leader's separate opt-in evidence.
