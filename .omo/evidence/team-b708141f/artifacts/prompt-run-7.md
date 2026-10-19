# Member A — revision 7 construction constraint

Stable model source SHA-256 `8dbafc1ea201a3327f83192f54617d58306028b9e23961301c51a501e6e5f52d`. Only instructions in `src/server/model.ts` changed. Low reasoning remains to isolate construction from effort.

Observed run6 ordinary/attack raw outputs directly: invented previous approach, publication-before-feedback chronology and publication-before-error chronology persist with low effort. A present-interpretation label also fails to prevent novel asserted past effects. Effort escalation alone therefore has no supporting factuality improvement on those observed outputs.

Leader approved a concrete construction change: factual paragraphs select complete input.experience sentences verbatim in original order. They may omit sentences or add paragraph breaks, but not new connective prose, clause merges or paraphrases. Input commands are excluded. Newly authored prose is restricted to a separate explicitly present interpretation paragraph and brief future application; a present label does not permit a new claim about historical effects/psychology/learning. One short unrelated gardening example demonstrates source adjacency versus unsupported chronology/result, with an instruction not to include that example in user output. Rewrites preserve factual sentences/order and alter selection or reflection length. Genuine sparse context may request input rather than fill with generic prose.

Tradeoff: historical prose preserves user wording instead of stylistically rewriting it. This is a prompt constraint, not a deterministic sentence validator or universal guarantee; live factuality/usefulness still require review. No fixture text, exact evaluation response, public schema, pipeline or extra verifier was added.

Evidence directory `/Users/jay/Projects/essay-service/.omo/evidence/factuality-prompt/run-7/`:

| Scenario | Invocation | Observable | Artifact |
| --- | --- | --- | --- |
| Adapter controls/numeric adjustment and pipeline limits/response paths | `pnpm test src/server --reporter=verbose` |18 tests pass | `server-tests.log` |
| Types | `pnpm typecheck` |exit0 | `typecheck.log` |
| Static check | `pnpm exec biome check src/server` |exit0 | `lint.log` |
| Scope/identity/size | baseline diff and Node hash/line measure |instruction-only change,84 pure lines | `model.patch`, `source-review.json`, `model-before.ts.txt` |

Mocked tests prove mechanics only. No prompt wording assertions or semantic guarantee. Code responsibility/boundary types/call count unaffected; no resources or paid calls created by A. Source frozen for leader-owned run7; outcome pending independent live review.
