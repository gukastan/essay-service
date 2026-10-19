# Member A — revision 6 controlled experiment

Stable model source SHA-256 `52fc6b7395870e68418243e1e097c1cb7710edda6db265212c75210966fb20b0`.

Read run-5 raw ordinary and attack responses. Length success did not resolve unsupported prior discussion method, publication/feedback chronology or explicitly asserted unsupplied learning. Leader authorized isolated effort change after freshly checking official model support: https://developers.openai.com/api/docs/models/gpt-5.6-terra.

Exactly two one-line edits: `reasoning.effort` none → low in `src/server/model.ts`, and matching SDK expectation in `src/server/model.test.ts`. Revision5 instructions and dynamic numeric guidance are unchanged. Model stays gpt-5.6-terra; max_output_tokens4000, strict JSON output, retries0, 30-second cancellation and two-call pipeline remain unchanged. No assumption that low guarantees factuality or that none cannot reason; this experiment isolates effort as a variable. Live latency must remain inside the existing limit.

Evidence directory: `/Users/jay/Projects/essay-service/.omo/evidence/factuality-prompt/run-6/`.

| Scenario | Invocation | Observable | Artifact |
| --- | --- | --- | --- |
| Adapter sends low effort with unchanged controls; numeric guidance; bounded pipeline | `pnpm test src/server --reporter=verbose` |18 tests passed | `server-tests.log` |
| Strict typing | `pnpm typecheck` |exit0 | `typecheck.log` |
| Static server check | `pnpm exec biome check src/server` |exit0 | `lint.log` |
| Isolated diff/source identity | baseline diff + Node hash/line count |2 one-line changes, model83 pure lines | `model.patch`, `model-test.patch`, `source-review.json` |

The tests verify transport/mechanics only. No new semantic mock tests. Source responsibilities and typed boundaries unchanged; no casts, helpers, extra calls, logs or temporary services. No paid calls, environment, README or QA-document changes by A. Source frozen for leader-owned run-6 and independent review; final improvement remains pending real evidence.
