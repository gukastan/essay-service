# Member A — revision 2 handoff

Changed only `src/server/model.ts` instruction string. Stable SHA-256: `7da479ec75a3fd733cea0cfa66d2f6275f2c8dfe8545e5cae63d16bf4444422b`.

Read all five run-1 HTTP artifacts. Both ordinary samples returned needs_input despite provided situations, roles, actions and lessons; their requests for finer optional details show a utility regression. Long experience remained a draft. Insufficient and sparse achievement-injection clarification remained appropriate. This revision addresses sufficiency without relaxing historical grounding.

Added positive sufficiency guidance: situation, role, problem, multiple concrete actions and observed result or stated lesson can support a draft. Exact wording, names, full artifact contents and numerical achievements are not prerequisites. Safe elaboration arranges provided steps into coherent paragraphs, explains present significance tied to the stated lesson, and adds a short explicitly prospective application. It must not add past motives, results, habits or chronology. Genuine inability to create a grounded length-compliant draft still yields needs_input. No sample-specific text, threshold or predetermined response was added.

Evidence directory: `/Users/jay/Projects/essay-service/.omo/evidence/factuality-prompt/run-2/`.

| Check/scenario | Invocation | Observable | Artifact |
| --- | --- | --- | --- |
| SDK transport/schema/retry/timeouts and bounded length pipeline, needs_input, errors | `pnpm test src/server --reporter=verbose` | 17/17 passed | `server-tests.log` |
| Strict typecheck | `pnpm typecheck` | exit 0 | `typecheck.log` |
| Server lint | `pnpm exec biome check src/server` | exit 0, 5 files checked | `lint.log` |
| Exact revision scope/size | `diff -u` from stored revision1 source; Node hash/line count | instruction-only patch, 82 pure lines | `model.patch`, `source-review.json`, `model-before.ts.txt` |

Model/reasoning/schema/API limits remain unchanged. Existing tests establish transport and bounded behavior only; no new mocked factuality claim or prompt keyword test. Live utility and factuality remain pending leader-owned run-2 and independent QA review. No servers, paid calls, environment or other source files were changed. Source is frozen for that run.
