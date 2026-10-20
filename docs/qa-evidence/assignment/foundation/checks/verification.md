# ESSAY-19 foundation checks — B

Final deterministic result: **131 Python tests passed; 1 paid test skipped by default; 12 JavaScript tests passed.** Strict basedpyright reports 0 errors/warnings across 32 included product/test files. Ruff check and format pass. Programming audit reports no violations in 15 test Python files. No module exceeds 250 pure LOC (largest: 171).

These are foundation contracts, budget/state harnesses, actual provider serialization, actual stdio MCP, and actual FastAPI lifespan checks. They do not claim implemented four-role business behavior, complete draft service, official source verification, or real model/search success. The paid probe was separately invoked by the leader and passed; its exact sanitized result is linked below. B made no paid calls.

## Exact invocations and captured results

Working directory: `/Users/jay/Projects/essay-service/assignment`.

| Invocation | Binary observable | Artifact |
| --- | --- | --- |
| `.venv/bin/python -m pytest -q -p no:cacheprovider --junitxml=../docs/qa-evidence/assignment/foundation/checks/pytest.xml` | Exit 0; 131 passed, 1 explicit paid skip | [pytest.txt](pytest.txt), [pytest.xml](pytest.xml) |
| `node --test tests/test_foundation.mjs` | Exit 0; 12 passed, no failures/skips | [js-tests.txt](js-tests.txt) |
| `.venv/bin/basedpyright --outputjson` | errorCount=0, warningCount=0 | [typecheck-final.json](typecheck-final.json) |
| `.venv/bin/ruff check tests --no-cache` | All checks passed | [ruff-final.txt](ruff-final.txt) |
| `.venv/bin/ruff format tests --check --no-cache` | 15 files already formatted | [format-final.txt](format-final.txt) |
| `.venv/bin/python /Users/jay/.codex/plugins/cache/sisyphuslabs/omo/5.1.38/skills/programming/scripts/python/check-no-excuse-rules.py tests` | No violations in 15 files | [test-discipline.txt](test-discipline.txt) |

The initial suite was 121 passed / 1 paid skip ([full-first.txt](full-first.txt)). Final coverage adds 3 malformed SDK output variants, 2 actual MCP timeout scenarios, and 5 strict revision-value variants. These ten were requested review concerns, not additional product scope. After core fixes, the focused affected contract/provider/MCP/lifecycle run passed 94 cases ([final-edge-pass.txt](final-edge-pass.txt)), followed by the full final suite above.

## Acceptance mapping

All named Python scenarios below ran in the exact full-suite invocation above. `pytest.xml` records each parameterized case independently with classname, scenario name, elapsed time, and pass/failure/skip status.

| ESSAY-19 criterion | Exact scenarios and binary observables | Evidence |
| --- | --- | --- |
| 1. Pydantic inputs/outcomes/evidence, request LangGraph state | `tests.test_contracts` (74 cases): four required input types/blankness; exact emoji code-point bounds; optional values; URL scheme/length/port rejection; extra metadata/private research input rejection; source/claim/range constraints; ready801/1000 and count equality; needs_input/error reject draft leakage; revision booleans rejected. `tests.test_state` (8): real StateGraph joins once in both completion orders, rejects context overwrite/revision rollback, executes failed node once, isolates initial state. | [pytest.xml](pytest.xml) |
| 2. Shared lifespan deps, fresh requests, disabled persistence/tracing | `test_real_lifespan_reuses_dependencies_and_never_creates_database`: two health results share instance; two request contexts have distinct ids/budgets/states; real MCP connected inside lifespan and disconnected after; no temp DB; chat/SSE/draft routes404. `test_mcp_exit_reaps_owned_child_before_parent_exits`: recorded child PID exists inside context and `kill(pid,0)` raises ProcessLookupError immediately after exit. `test_actual_mcp_child_suppresses_inherited_tracing_flags`: only four named flag sentinels captured, true inputs become false/OTEL disabled in actual child. | [pytest.xml](pytest.xml), [lifecycle-final.txt](lifecycle-final.txt) |
| 3. Calls/tokens/timing/retries/cancellation | `tests.test_budget` (12) + `tests.test_budget_timing` (4): normal4/12000 and revision6/18000 reservation examples; simultaneous over-cap attempts blocked; hosted2 reserved once; failed/cancelled calls retain charges; clock-injected model30/request180/research45 boundaries and stage remainder5; expired request reserves nothing. SDK500 fixture observes exactly1 request despite client retries3; failed real LangGraph node executes once. JS body-read test actually fires injected195000ms timer, rejects TimeoutError after1 fetch, cleans listener/timer. | [pytest.xml](pytest.xml), [js-tests.txt](js-tests.txt) |
| 4. MCP reserves before provider, one hosted call, limits | `test_actual_mcp_discovery_reserved_before_sdk_wire_and_private_fields_removed`: actual stdio discovery and tool execution reaches real SDK localhost HTTP fixture with parent model1/tool2 already reserved; HTTP queue size1. `test_actual_mcp_failure_is_not_retried_and_reservations_remain`: HTTP500 observed once, typed error, repeat blocked. `test_hosted_research_is_one_wire_call_with_two_tool_capacity`: serialized request store=false, max_tool_calls2, token3000, web_search; response actual reported tool1 separate from capacity2. | [pytest.xml](pytest.xml) |
| 5. Research privacy, metadata, protocol errors/correlation | Actual MCP SDK HTTP payload excludes distinct PRIVATE_QUESTION/PRIVATE_EXPERIENCE canaries and only allows company/role/posting keys. `test_untrusted_overrides_never_reach_provider` rejects domain timeout, metadata tool escalation and timeout999 before HTTP. Actual stdio malformed/wrong correlation/tool error/disconnect give typed sanitized errors. Concurrent shared connection returns correct company and request UUID separately. Active cancellation stops following send and retains model1/tool2. Reported TIMEOUT and real pending-tool20ms deadline permanently stop future operations. | [pytest.xml](pytest.xml) |
| 6. LF/code-point Python and JS parity | `tests.test_text_parity` (3) invokes actual Node helper for Hangul, CRLF+emoji, combining mark+ZWJ emoji fixtures and compares independently expected normalized text/count/span. Contract slice-clamping regression rejects end beyond text. JS12 also rejects negative/fractional/inverted/out-of-bounds offsets. Leader's actual Vue harness is separate browser evidence. | [pytest.xml](pytest.xml), [js-tests.txt](js-tests.txt), [browser report](../browser/README.md) |
| 7. Local settings and optional live compatibility | `test_server_settings_ignore_inherited_provider_destination` proves canonical OpenAI origin and retries0 with sentinel override and dummy key, no network call. Default suite explicitly skips `test_paid_structured_model_and_real_mcp_search`. Runner loads only two allowed settings in-process; canonical destination; one plain model+one actual MCP web_search;30s each; unique sanitized artifact with UTC times/model/counts/tokens. B made no paid calls. | [pytest.xml](pytest.xml); [leader-run live result](live-84299595-7260-43ce-8596-7a6276699470.json): both schema successes; plain model1, research model1/hosted reported1/reserved2 |
| 8. Launcher/environment/clean install | Owned by C, independently verified by leader. B provides documented test commands and code-point/client boundary tests. No launcher completion claim is derived from unit tests. | [runtime report](../runtime/README.md), [leader smoke](../leader/runtime-result.json) |

## Honest boundary separation

- **Deterministic HTTP-level provider fixtures:** 11 provider tests use the installed OpenAI SDK with httpx2.MockTransport. They inspect serialized SDK requests and parse actual SDK response objects. No real OpenAI server/model is used.
- **Actual stdio MCP:** 17 MCP/MCP-control tests spawn real FastMCP subprocesses. Happy-path and HTTP500 cases use the production MCP server + production OpenAI adapter + real localhost HTTP server on port0. Adversarial protocol fixtures exercise malformed results, disconnect, timeouts and correlation. The model responses are deterministic local fixtures.
- **Actual FastAPI lifespan:** 2 tests enter production lifespan, create/close real MCP dependencies, and drive health/routes via ASGI HTTP transport. C/leader separately exercise live localhost Uvicorn and signals.
- **Actual model/search:** the leader ran the single opt-in probe successfully at 2026-10-20T06:51:26Z–06:51:39Z, configured model `gpt-5.6-terra`. Plain structured call: 1.680s, input/output tokens97/23, model reservation1. Actual MCP hosted search: 11.300s, tokens13320/1197, model reservation1, hosted reported1 versus reserved2. Both schemas passed, retries0, max_tool_calls2. B inspected the [sanitized unique artifact](live-84299595-7260-43ce-8596-7a6276699470.json); no prompts/provider bodies/keys are present. This is compatibility evidence, not full essay or official-source QA.
- **Browser:** B's Node tests and Python/Node parity are utility checks. Leader's Vue5 harness is real browser evidence; neither is a full draft-service browser claim.

## Regressions found and repaired by the product owner

Preserved red artifacts document non-string optional input AttributeError, invalid URL ports and evidence slice clamping ([contracts-first.txt](contracts-first.txt)); FastMCP protocol metadata rejected before provider transmission ([mcp-first.txt](mcp-first.txt)); malformed SDK output raw errors and MCP timeout not stopping subsequent work ([final-edge-first.txt](final-edge-first.txt), [mcp-timeout-red.txt](mcp-timeout-red.txt)); boolean revision acceptance ([revision-red.txt](revision-red.txt)). Final tests retain these cases and pass. Intermediate import/type/lint failures are retained as diagnostic history; only the final artifacts above are completion evidence.

## Review and ownership

Test/fixture modules each own one boundary. JSON crosses into typed Pydantic values; no Any/object/cast/type-ignore escape hatches. SDK transport, real MCP, events, injected clocks and unique temp directories are used instead of mocked whole services, fixed ports or sleeps. No natural-language prompt assertions. Narrow documented directives address incomplete third-party LangGraph signatures and exhaustive unreachable guards only. Source hashes, pure LOC, test counts and final artifact existence are captured in [evidence-manifest.json](evidence-manifest.json).

B changed only assignment/tests, checks evidence, and team memos. Product fixes, dependency pinning, launcher/browser evidence, paid execution, Jira, commits and integration remain with their assigned owners.

Actual live invocation (leader, assignment cwd): `env -i PATH=/usr/bin:/bin LANG=en_US.UTF-8 PYTHONDONTWRITEBYTECODE=1 ESSAY_LIVE_COMPATIBILITY=1 /Users/jay/Projects/essay-service/assignment/.venv/bin/python -m pytest tests/test_live_compatibility.py -q -s`. Result: exit0, 1 passed in13.40s. The default full suite still intentionally skips it. No further paid execution is needed.
