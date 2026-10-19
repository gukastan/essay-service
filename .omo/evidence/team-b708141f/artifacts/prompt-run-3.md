# Member A — revision 3 handoff

Only `src/server/model.ts` instructions changed. Stable SHA-256 `3db47d6762564b6917e49cf2648f5fb2db084c87ef7a6206fa3253198252d04a`.

Observed run-2 ordinary outputs directly: collaboration acknowledges core information but still withholds draft for optional detail; service attributes the notice's contents to customer inquiries. Independent QA additionally identified a narrowing of the observed problem object in the long sample.

Revision adds a positive, flexible paragraph scaffold allocating space to supplied context/role, supplied problem, supplied actions, source-supported outcome/lesson plus current meaning, and short prospective application. Adequate core experience defaults to draft, rather than requests for more vivid detail. Genuine sparse context still permits needs_input. Direct and indirect attributed speech now explicitly preserve source breadth; artifact/solution content is not evidence of another person's request. Summaries preserve the observed object and its qualifiers. Redundant composition prose was removed; no canned essay, evaluation sample, fixture threshold or exact expected response was embedded.

Evidence is under `/Users/jay/Projects/essay-service/.omo/evidence/factuality-prompt/run-3/`:

| Scenario | Invocation | Observable | Artifact |
| --- | --- | --- | --- |
| SDK retry/timeout/schema/transport and pipeline length/needs_input/failure bounds | `pnpm test src/server --reporter=verbose` | 17 tests passed | `server-tests.log` |
| Strict typing | `pnpm typecheck` | exit 0 | `typecheck.log` |
| Owned lint | `pnpm exec biome check src/server` | exit 0 | `lint.log` |
| Scope, source identity, size | baseline diff and Node SHA/line count | only instructions changed, 83 pure lines | `model.patch`, `source-review.json`, `model-before.ts.txt` |

Mocked tests remain mechanics-only evidence. No tests pin prompt wording or assert model factuality. No model, reasoning effort, output schema, call count limit or timeout change; no paid request or process/resource change by A. Current fix quality remains pending unchanged five-sample run-3 and independent QA. Source frozen for leader-owned run.
