# ESSAY-2/3 implementation handoff

Implemented only src/app/page.tsx, src/app/globals.css and src/components/essay/. No package, shared contract, API, Jira or Git changes. DESIGN.md documents the Korean writing-workspace tokens and states.

## Behavior delivered
- Four required fields use shared request validation. Empty or whitespace-only values show linked errors and focus the first invalid field.
- One ky request uses retry: 0 and timeout: 75000. A synchronous in-flight ref blocks duplicate submission; fieldset and existing draft editor stay disabled through final response.
- Response JSON is parsed with shared draftResponseSchema and exhaustive status switch. Errors/needs-input preserve inputs and the previous result; successful draft stores its own immutable request snapshot.
- Editor applies shared LF normalization and shared Unicode code-point counter. 800 or fewer and over 1000 show warning, while copy stays available. Edits make no request.
- Copy uses the current edited text, reports success/failure inline and clears stale copy feedback on edit. Form and result reflow to a single column; system dark mode and reduced motion are supported.

## Direct verification evidence
Artifact: .omo/evidence/essay-screen-validation.json records exact commands, captured outputs, exit codes and tool chunk IDs.

| Scenario | Invocation | Binary observable |
| --- | --- | --- |
| Scoped UI lint/format | pnpm exec biome check src/app/page.tsx src/app/globals.css src/components/essay | exit 0, Checked 8 files; no fixes applied |
| Strict application types | pnpm exec tsc --noEmit --incremental false | exit 0, no diagnostics |
| Running development surface | curl -sS -o /tmp/essay-screen.html -w '%{http_code}' http://127.0.0.1:3000 | HTTP 200; tool chunk 633103 |

The HTML capture is /tmp/essay-screen.html. The first non-escalated curl could not reach the local server; the authorized local check succeeded. Incremental typecheck initially could not write tsbuildinfo under the sandbox; the complete non-incremental typecheck passed. Initial formatting findings were fixed and the full scoped check rerun.

## QA ownership and limitations
Behavioral browser verification is explicitly handed to member C and leader, already notified with stable selectors. This report does not claim browser, clipboard, real-model, screenshot, or Lighthouse verification. QA selectors: #company, #role, #question, #experience, #draft, .original-experience, button text 초안 만들기 and 초안 복사. Status region is above workspace; role=alert announces errors even while viewport is scrolled to submit.

## Self-review
Files have one responsibility: page shell; global tokens/reset/media; form; workspace request state; result editor; chrome/panels/fields styles. TypeScript files are 50–159 physical lines, styles 82–205; globals is in the 200–250 warning band and should be split if expanded. API values are parsed at the boundary; no assertions, any, enum, suppression, automatic retry, persistence or server import exists. Exhaustive response switching and shared count helpers preserve contracts. No logging dependency added. No owned background process or browser resource was started.
