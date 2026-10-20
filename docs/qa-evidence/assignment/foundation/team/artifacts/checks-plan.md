# B foundation test plan

Scope: ESSAY-19 only, no role/business-prompt tests or full draft API completion claim.

1. Contracts: required field blank/type/extra rejection; exact code-point limits; LF offsets; tagged outcomes with no draft/error leakage. Real StateGraph join both completion orders, immutable context, fresh request state.
2. Lifespan: startup/shutdown shares model/MCP objects, fresh request budget, no SQLite/legacy chat/SSE/tracing.
3. Budget: 4/6 role reservations and 12k/18k tokens; concurrent model6/hosted2 cap; atomic token exhaustion; timeout30/45/180; no refund; cancel/deadline blocks subsequent transmission.
4. Provider wire: actual SDK HTTP request strict required/nullable schema, store=false, max_tool_calls2, retries0. Refusal/incomplete/invalid outputs become sanitized typed errors.
5. Real stdio MCP: discovery/call, model1/hosted2 reserved before transmission, domain projection, trusted metadata, malformed/error/disconnect/timeout/cancel, correlation and concurrency isolation. Local HTTP fixture behind actual SDK where practical.
6. Python/JS parity: Hangul/CRLF/emoji offsets and count; client timeout195 with scheduler injection.
7. Opt-in live: exactly one plain structured model plus actual MCP hosted search, public input, 30s each, retries0, sanitized metadata. B writes only; leader invokes paid run.
8. Launcher: C owns clean-install and owned-process start/stop evidence.

Evidence: assigned checks directory pytest transcript/JUnit plus report mapping each criterion to exact test invocation and binary observable. No active ulw-loop attempt found (ULW_LOOP_PLAN_MISSING), so assigned evidence location applies.
