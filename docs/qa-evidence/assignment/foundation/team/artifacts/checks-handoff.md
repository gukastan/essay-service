# B foundation checks handoff — complete

Ownership respected: only assignment/tests/**, assigned checks evidence, team artifacts changed. No paid calls, product edits, dependency edits, Jira changes, commits or push by B.

The existing default suite reached 121 passed / 1 paid skip, captured in checks/full-first.txt and the initial checks/pytest.txt. Three malformed SDK output cases, two actual MCP timeout cases, and five strict revision cases were then added from already requested review findings. Preserve red evidence: contracts-first.txt, mcp-first.txt, final-edge-first.txt, mcp-timeout-red.txt, revision-red.txt. A owns fixes.

Strict checks currently clean: checks/typecheck-final.json (0 diagnostics), ruff-final.txt (All checks passed), format-final.txt, test-discipline.txt (15 files, no violations). Final full rerun passed131/1 paid skip; JS12. Full acceptance mapping and exact evidence: docs/qa-evidence/assignment/foundation/checks/verification.md. Source bytes are frozen for the leader paid probe.

Paid opt-in runner is tests/test_live_compatibility.py. Leader only may invoke after final deterministic acceptance:
`ESSAY_LIVE_COMPATIBILITY=1 uv run --frozen pytest tests/test_live_compatibility.py -q -s`
It loads only OPENAI_API_KEY/OPENAI_MODEL from root .env.local in-process, uses explicit canonical OpenAI base URL, no retries, one analysis-role structured request plus one actual MCP hosted research request, public OpenAI/Software Engineer input, 30s per model, hosted tool2. Output is unique checks/live-<UUID>.json; UTC start/end, model name, schema success, typed errors, counts/reservations/time/tokens only. Plain parsed result must match supplied public company/role. Default pytest skips it. B has not invoked it.

JS test command: `node --test tests/test_foundation.mjs`; 12 passed, checks/js-tests.txt. Python codepoint parity uses Node import and same three fixtures as leader's actual Vue harness. It is utility parity, not a full Vue product workflow claim.

No-excuse review: each file owns one test boundary or shared fixture. Untrusted JSON is parsed with Pydantic JsonValue/contracts; no Any/object/cast/type-ignore. Real SDK HTTP transports and real stdio MCP used; only clocks, platform fetch/timers, deterministic HTTP responses are controlled. No natural-language prompt assertions. Each module remains below 250 pure LOC. External LangGraph incomplete signatures and exhaustive assert_never intentionally unreachable branches have narrow documented file directives; all other checks remain strict.

Leader executed the one opt-in paid probe successfully; B inspected sanitized checks/live-84299595-7260-43ce-8596-7a6276699470.json. Both schemas pass; plain model1 (1.680s,97/23 tokens); actual MCP research model1 (11.300s,13320/1197 tokens), hosted reported1/reserved2, retries0. No more paid runs needed. Final report and manifest include this separate compatibility result.
