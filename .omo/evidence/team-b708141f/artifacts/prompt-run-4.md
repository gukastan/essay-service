# Member A — revision 4 handoff

Stable source SHA-256 `e63a37c0689491e1532e36177ac7bfe5b50d239fc8ff59663529e17c8fbfcf25`. Only `src/server/model.ts` instructions changed.

Read run-3 raw responses. Collaboration now produced a draft but added unsupported historical narrative bridges, including an earlier discussion method and follow-through from an assigned role and decision. Service and sparse achievement case returned 422; their failed internal drafts are intentionally absent from public errors, so their exact out-of-range lengths/directions are not observed. Long experience returned a draft and insufficient experience requested input.

Diagnosis shared with leader before editing: paragraph quotas likely encourage filling historical gaps; an upper-edge target leaves little length margin. These remain hypotheses about model behavior, not directly measured internals.

Revision removes fixed historical-section quotas while preserving a positive composition sequence. Past facts stay near source scope; assigned responsibilities and decisions do not prove later implementation, and gaps must not be filled with invented methods/actions. Expansion is directed into explicitly present interpretation connected to supplied learning and prospective application. Contract target 1000 and valid 801–1000 remain unchanged; working length approximately 900 supplies margin. Rewrites use server actual-count delta toward 900 and recheck past claims. Sparse experience still supports needs_input.

Evidence directory: `/Users/jay/Projects/essay-service/.omo/evidence/factuality-prompt/run-4/`.

| Scenario | Invocation | Observable | Artifact |
| --- | --- | --- | --- |
| Provider transport/schema/retry/timeout and bounded pipeline paths | `pnpm test src/server --reporter=verbose` | 17 tests passed | `server-tests.log` |
| Strict typing | `pnpm typecheck` | exit 0 | `typecheck.log` |
| Server static check | `pnpm exec biome check src/server` | exit 0 | `lint.log` |
| Scope, hash, size | baseline diff and Node source measurement | only instructions changed, 83 pure lines | `model.patch`, `source-review.json`, `model-before.ts.txt` |

Mocked mechanics tests do not validate semantic grounding. No keyword tests or fixture-specific examples added. Model, reasoning, JSON schema, two-call maximum and per-call deadline remain unchanged. No live calls, environment edits or server resource changes by A. Source frozen for leader-owned validation; quality remains pending independent live review.
