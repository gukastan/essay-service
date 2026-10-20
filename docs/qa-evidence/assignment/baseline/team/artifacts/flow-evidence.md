# Member B handoff — ESSAY-18 original flow evidence

Owned changes: `docs/qa-evidence/assignment/baseline/flow/` only, plus this memo. No source, planning docs, Jira or git history changed.

- Report: `docs/qa-evidence/assignment/baseline/flow/report.md` (Korean, acceptance mapping + tested/untested + exact commands).
- API/SSE: `api-results.json`, 25/25 checks, real localhost FastAPI + LangGraph, fake model/JSON telemetry. First incident captured retry=1, gate_removed=1, one replan, 2 validation attempts. SSE later retry=0. Health instance unchanged, creation_count=1.
- MCP: `mcp-results.json`, 8/8 checks, independent real stdio ops/docs sessions. Tool, resource, prompt executed; only prompt hash+length persisted. Unknown system and missing resource control checks passed. Client sessions closed. No paid API calls.
- Runners: `run-api.mjs` (20s/request; fresh/warm explicit), `probe-mcp.py` (30s; clean environment invocation in report). Node syntax and installed Python no-excuse checker passed.
- Source audit: `source-audit.md`, `audited-source-sha256.txt`, `source-symbol-lines.txt`.
- Validation: `artifact-validation.json`, 33 checks pass; no persisted prompt/last_prompt/key fields.

Important limits: actual analysis node entered but AnalysisSkipped, not completed analysis. Fake emits whole-draft callback chunks, not upstream token streaming. MCP lock serializes protocol calls; gather schedules tasks but no throughput claim. Final parallel_elapsed is only last research pass. First transient is a client-side deliberate exception, not an actual MCP outage. Existing fake routing example for cache-service routes chat (captured explicitly as limitation, not success of diagnosis). Do not report simulated cost as billed spend.

A preserved first incident state and owns runtime stop; leader owns browser. Initial localhost sandbox EPERM artifacts retained separately and marked failed environment attempt; approved retry passed. No environment/database contents read. Restart persistence, actual model paths and performance untested.

Self-review: modules each own one evidence surface; Python telemetry parses into frozen Pydantic boundary type; no broad catches, casts, Any annotations, enum branching or source patch. Files below 200 pure LOC. Tests are real protocol checks, not implementation-only tests. No additional standalone test suite for the evidence runners.
