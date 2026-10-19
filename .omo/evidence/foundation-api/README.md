# Foundation and API evidence — member A

Project: `/Users/jay/Projects/essay-service`. Executed 2026-10-19. No active ulw-loop attempt was configured. Evidence is under this directory; no secrets recorded.

## Scope and changes

ESSAY-1: Next.js 16.4.2, React 19.3.1, TypeScript 5.9.3, pnpm lockfile, Vitest 5.0.5, Biome configuration, root layout, shared request/response schemas and Unicode helpers, `.env.example`, README setup and demo.

ESSAY-4/5: real OpenAI Responses adapter, request/config parsing, schema validation, bounded two-call pipeline, 30-second cancellation, facts-only generation/rewrite instructions, redacted API errors. No production mock mode, persistence or additional backend.

Page/CSS ownership was released to B immediately after foundation verification. QA tests/docs belong to C. No commits, pushes, deployments or Jira writes performed by this member.

## Scenario ledger

Paths below are relative to this evidence directory. All test scenarios use deterministic provider/SDK mocks, not a live model.

| Criterion/scenario | Invocation | Binary observable | Captured artifact |
| --- | --- | --- | --- |
| Runnable foundation | `pnpm dev`; `curl -D foundation-http-headers.txt http://127.0.0.1:3000 -o foundation-home.html` | HTTP 200 and Korean page content | `foundation-http-headers.txt`, `foundation-home.html` |
| Unicode boundaries 800/801/1000/1001 and whitespace, CRLF, CR, Korean, emoji, combining marks | `pnpm test src/shared src/server --reporter=verbose` | All 5 shared tests pass; valid only 801/1000 | `api-tests.log` |
| First draft 801/1000 | same command | HTTP outcome 200; actual count; exactly 1 provider call | `api-tests.log` |
| First draft 800/1001 | same command | Exactly 2 calls; rewrite contains original input, normalized draft and actual count | `api-tests.log` |
| Both drafts invalid | same command | Outcome 422, exactly 2 calls, no leaked draft | `api-tests.log` |
| Needs-input first/second call | same command | Outcome 200 and generationCalls 1/2 respectively, no length retry | `api-tests.log` |
| Malformed model output | same command | 502 MODEL_ERROR after one call for null, missing fields, whitespace draft, wrong message type | `api-tests.log` |
| Deadline | same command, fake timers advanced 29999 then 1 ms | Signal false before deadline, aborted at 30000; 504; 1 call; no leftover timer | `api-tests.log` |
| Provider failure | same command | 502; internal details absent; 1 call; no leftover timer | `api-tests.log` |
| SDK guardrails | same command | Constructor/request maxRetries 0 and timeout 30000, passed AbortSignal, strict JSON schema, store false | `api-tests.log` |
| Generation/rewrite transport | `pnpm test src/server/model.test.ts --reporter=verbose` | Identical nonempty instructions in both calls; original input, rewrite context and target range passed correctly | `adapter-tests.log` |
| Incomplete response/bad JSON | same command | Adapter rejects; exactly 1 SDK call | `api-tests.log` |
| Missing configuration on actual HTTP route | `curl -H 'Content-Type: application/json' --data '{"company":"회사","role":"개발","question":"경험","experience":"팀 프로젝트"}' http://127.0.0.1:3000/api/drafts` | HTTP 500 and CONFIG_ERROR | `config-http-headers.txt`, `config-http-body.json` |
| Invalid input on actual HTTP route | `curl -H 'Content-Type: application/json' --data '{}' http://127.0.0.1:3000/api/drafts` | HTTP 400 and INVALID_INPUT, four field messages | `invalid-http-headers.txt`, `invalid-http-body.json` |
| Strict typecheck | `pnpm typecheck` | Exit 0 | `api-typecheck.log` |
| Owned-file static check | `pnpm exec biome check src/server src/shared src/app/layout.tsx src/app/api package.json tsconfig.json biome.json next.config.ts vitest.config.ts` | Exit 0, no errors; 2 informational computed-key suggestions intentionally retained for TS index-signature flag | `owned-lint.log` |
| File-size review | Node counts nonblank/noncomment lines in owned TS sources | Every source below 250 lines | `source-review.json` |

Owned suite: 22 tests in 3 files passed before the test-only prompt assertion correction. After correction, the affected adapter suite passed 4/4 (`adapter-tests.log`). The correction replaces literal prose assertions with instruction transport and context checks; product code is unchanged. QA owns the additional actual-route contract suite. Leader owns final build after screen edits and dev server shutdown; this report does not claim a build was executed.

## Model selection and limitation

Selected `gpt-5.6-terra`, `reasoning.effort: none`. Retrieved official model documentation on 2026-10-19: https://developers.openai.com/api/docs/models/gpt-5.6-terra. It explicitly supports reasoning `none`, Responses API and structured outputs. Structured request syntax checked at https://developers.openai.com/api/docs/guides/structured-outputs; SDK retry/timeout controls checked against https://raw.githubusercontent.com/openai/openai-node/master/README.md and installed SDK types. Next.js setup checked using official Next.js documentation through Context7.

Required environment variables: `OPENAI_API_KEY`, `OPENAI_MODEL`. Current session has neither and project has no configured env file. Real provider access, real latency and five-sample factuality/quality are **unverified**. Tests prove instruction transport and mechanics, not model factuality. Facts-only generation/rewrite instructions were manually reviewed in `src/server/model.ts`; that review does not guarantee factual output. User factual review remains required for ESSAY-7.

## Architectural self-review

Each module owns one responsibility: character counting, API contracts, config parsing, provider transport, drafting orchestration, or HTTP boundary. Untrusted request/config/model data are parsed before business use. Tagged model output uses exhaustive switch; no any/type assertions/non-null assertions or suppressed TypeScript errors were added. Error handling at boundaries deliberately redacts foreign errors. Shared helpers serve multiple callers; no duplicate generation abstraction. Functions have at most three parameters. No logging framework was added to the initially log-free project. No destructive cleanup/reverification or negative-state naming was introduced. Tests above lock the observable contracts.

## Resource handoff

Initial dev process was terminated by the interrupted turn. Replacement `pnpm dev` is on port 3000, unified exec session `61586`, log `dev.log`. It is intentionally handed to leader/QA for ongoing browser checks; leader should stop it before production build. No other temporary service remains owned by this member.
