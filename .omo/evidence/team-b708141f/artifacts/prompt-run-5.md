# Member A — revision 5 handoff

Stable model source SHA-256: `e5993a3e3eab627bebf0b09aaf56e6e4072fd159b1a99468e76d16c6bcbfdd6c`. Changed `src/server/model.ts` and its adapter unit test only.

Observed evidence driving revision: leader's actual adapter diagnostic (`docs/qa-evidence/live-model-revalidation/run-4/diagnostic/receipt.json`) has normal-service first draft 736 and rewritten draft 749 code points. Rewrite added only 13, versus 164 required to reach working target 900 from the initial draft. It also retained invented past interpretation and altered chronology. This confirms a short-draft failure in that diagnostic; it does not reveal the hidden lengths of every previous public 422.

Consolidated duplicated instructions into five ordered steps: source authority, sufficient experience, factual composition/current interpretation, actual-length rewriting, internal source check. No new sample-specific example. Past learning not supplied by source is no longer licensed as an essay opener; reflection must be present interpretation. Core adequate experiences should draft; sparse events needing generic padding can request real detail.

Runtime change explicitly authorized by leader: append a JSON `rewriteLength` object to the common instruction prefix on rewrite. It carries server-trusted actual count, working target 900, signed delta and allowed boundaries 801–1000. Positive delta requests substantive length addition from omitted source facts or distinct current interpretation tied to supplied actions/learning, rather than paraphrasing the same content. Negative delta requests reduction. The public target remains 1000 and valid range 801–1000; no API/output schema change. Input JSON retains original input and rewrite context. No extra model request or verifier was added.

Evidence directory: `/Users/jay/Projects/essay-service/.omo/evidence/factuality-prompt/run-5/`.

| Scenario | Invocation | Binary observable | Artifact |
| --- | --- | --- | --- |
| Adapter preserves base instructions/context and sends numeric positive adjustment | `pnpm test src/server --reporter=verbose` | actual800 → working900 / delta100 in instruction suffix, common prefix retained | `server-tests.log` |
| Adapter sends numeric reduction without extra requests | same | actual1200 → working900 / delta-300; exactly2 calls across generation+rewrite test | `server-tests.log` |
| SDK limits/schema and pipeline length/needs_input/errors | same | total18 tests passed | `server-tests.log` |
| Strict types | `pnpm typecheck` | exit0 | `typecheck.log` |
| Owned static check | `pnpm exec biome check src/server` | exit0,5 files checked | `lint.log` |
| Source scope/hash/size | baseline diff and Node measurement | model83/test115 pure lines | `model.patch`, `model-test.patch`, `source-review.json` |

Tests assert instruction transport/numeric calculation, not prompt wording or factuality. The existing common-instruction test now verifies shared prefix and parsed JSON suffix instead of requiring byte-identical full instruction strings. Source review: one provider responsibility, trusted count is typed internal data, no new unchecked external boundary, no helper/parameter bloat/casts/logging/resources. Model/reasoning/schema/retries0/30-second timeout/two-call pipeline unchanged.

Source frozen for leader-owned live validation. No paid calls by A and no server/env changes. Factuality and utility remain unverified until independent review of revision5 live outputs.
