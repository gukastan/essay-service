# Separate bounded model diagnostic

This is a direct invocation of the production `generateModelOutput` adapter on the unchanged `normal-service` input. It is not one of the five HTTP responses in run-4 and does not reveal the hidden drafts from those earlier requests.

The recorded two calls returned 736 and 749 Unicode code points after LF normalization. The second call received the original input, the first draft and the measured count, using the same length-only rewrite condition. It added only 13 code points, leaving the response below 801. This directly demonstrates an insufficient expansion in this diagnostic; it does not establish the direction of earlier HTTP 422 failures.

The raw text also attributes an unprovided historical interpretation to the author (customers needing to visit before checking the process) and places the understanding check after posting the notice, a sequence not established by the source. These remain useful failure examples for revision; neither raw draft is accepted as a passing output.

No response was substituted into the HTTP samples. The adapter retained the configured model, no automatic retries, a 30-second per-call deadline and `store: false`. Exactly two adapter calls were observed by this harness; provider billing was not queried. The receipt contains only synthetic sample output and non-secret configuration.

Runner: `/Users/jay/Documents/Codex/2026-10-19/omo-teammode-agents-md-docs-prd-2/outputs/diagnose-draft-length.mjs`.
