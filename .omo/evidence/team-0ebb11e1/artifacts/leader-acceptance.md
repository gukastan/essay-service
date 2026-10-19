# ESSAY-9 acceptance ledger

Scope confirmed by user: ESSAY-9 implementation and verification only. Base: ba1713f65bde1c38afc7171c01fabd8ec581d011. Existing v1 behavior and five fixtures remain the regression baseline. ESSAY-10–17 product roles/API/UI are excluded.

| Requirement | Evidence needed | Current state |
| --- | --- | --- |
| Runtime v2 inputs and ready/needs_input/error | Contract tests for Unicode limits, optional URL/text, distinct states and evidence IDs | Pending A |
| LangGraph compatibility | Exact dependency versions, actual compiled graph invocation, clean typecheck/build | Pending A + leader |
| Atomic request budgets | Concurrent over-cap model/search/page dispatch cannot occur | Pending B |
| Deadline and cancellation | Model30s/research45s/request180s, parent abort, caller completes if provider ignores abort, no follow-on dispatch | Pending B |
| Provider boundary | Structured OpenAI request with retries0 and bounded execution, replaceable search/page contracts | Pending C |
| Real provider support | Small live model/search probe, no credentials in artifacts, provider limits documented truthfully | Pending C |
| Preserve v1 | Original76 tests, unchanged fixture/model/UI paths, HTTP invalid-input smoke without a paid request | Pending leader |
| Quality and documentation | lint/typecheck/tests/build; inline self-review; docs/Jira updated to observed status | Pending leader |

Search decision discovered during official SDK/documentation inspection: OpenAI native search max_tool_calls cannot enforce separate internal search-query/page-read counts. This is a design gap, not a tested hard cap. Do not claim a production search provider is ready until its budget contract is resolved.

No automatic Git commit/push or ESSAY-10 implementation in this scope. Original v1 QA evidence is immutable.
