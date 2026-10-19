# Member A — factuality prompt revision 1

Changed only the instructions string in `src/server/model.ts`. Exact diff and source hash: `.omo/evidence/factuality-prompt/run-1/model.patch` and `source-review.json`.

Observed baseline: independently read five raw `docs/qa-evidence/live-model/*.http.txt` responses against `tests/fixtures/live-samples.json`. Normal collaboration added a participant total, attributed opinions and a historical consensus; service invented direct quotations and chronology; achievement-injection output added checklist contents, later use and timing despite resisting the requested award/revenue fabrications. Long experience merged separate facts into a stronger consensus and sharpened a symptom. These are real-output discrepancies, not a mock reproduction.

Hypothesis: the previous broad achievement prohibition left plausible narrative details and connective chronology underconstrained, particularly when expanding to the required length. The model's internal cause is not directly observable; improvement must be tested on unchanged live inputs.

Revision: structured source-authority, factual writing, interpretation/future-intent, and output-review sections. Only input.experience is evidence for past facts. Other input fields guide relevance. Previous drafts are untrusted. Preserve source specificity, uncertainty, relationships and limitations; do not infer attributed speech/opinions, motives, consensus scope, artifact contents, event order or subsequent use. Review each past claim internally against source. Useful grounded drafts remain preferred; needs_input is available if faithful 801–1000 characters would otherwise require invention, repetition or excessive generality. No evaluation sample text or expected outputs were embedded.

## Checks and evidence

All paths below are under `/Users/jay/Projects/essay-service/.omo/evidence/factuality-prompt/run-1/`.

| Scenario | Invocation | Observable | Artifact |
| --- | --- | --- | --- |
| Provider transport, unchanged instructions across generation/rewrite, strict schema, no automatic retry, timeout and input transport | `pnpm test src/server --reporter=verbose` | 4 adapter tests passed | `server-tests.log` |
| 801/1000 success, 800/1001 rewrite, two-call exhaustion, needs_input on either call, malformed output, timeout cancellation, error redaction | same | 13 pipeline tests passed | `server-tests.log` |
| Strict compilation | `pnpm typecheck` | exit 0 | `typecheck.log` |
| Owned server static check | `pnpm exec biome check src/server` | exit 0, 5 files checked | `lint.log` |
| Scope and size review | `diff -u` against server-before snapshot; Node line/hash extraction | only instruction string changed, source below 250 pure lines | `model.patch`, `source-review.json` |

The unchanged mocked tests verify mechanics only, not semantic factuality. No tautological prompt keyword test was added. Source review confirms no runtime behavior, model, reasoning setting, SDK retry/timeout, output schema or extra request changed. The file still owns provider transport; boundary typing and exception behavior are unchanged. No new helpers, casts, mutable exports, logging or resources were introduced.

Leader owns paid calls to the user's existing server. No live calls were made by A; no server was started/stopped and no environment files were read or changed. Revision is stable for leader's five-sample run and QA's independent content review. Overall factuality fix is **pending live review**, not established by the checks above.
