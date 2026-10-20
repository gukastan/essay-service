# ESSAY-21 state and revision handoff

Owner B changed only `assignment/agent/budget.py`, `state.py`, new `flow_state.py`, and `tests/test_flow_state.py`, `test_flow_revision.py`. Shared checkout; no commits, dependencies, model calls, business graph, API, or UI implementation.

## Invocation contract

`await budget.reserve_revision(route: str) -> RevisionReservation` validates that route is D or I, then atomically consumes the shared opportunity under ExecutionBudget's existing lock. Success carries typed `route: Literal["D", "I"]` and `revision_count=1`. Invalid routes raise `RevisionReservationError("INVALID_REVISION_ROUTE")` without consuming the opportunity. Another attempt raises `RevisionReservationError("REVISION_EXHAUSTED")`; a stopped or expired request raises its existing `ExecutionBudgetError` first. The separate revision exception preserves the original budget-error variants accepted by research/transport adapters. Reservations survive failures, cancellation and deadline expiry. Budget snapshots expose `revision_count` and `revision_route`; these are observations, not a second mutable owner.

G's future implementation must reserve before invoking D or I, then return `{"revision_count": reservation.revision_count, "usage": budget.snapshot()}` as its state update. Never infer permission to revise from a state snapshot alone. The existing state reducer remains a monotonic mirror, not the reservation owner. `initial_state` derives revision count from the budget, so reconstructing state with an already used budget cannot reset it. Fresh requests require fresh budgets.

WorkflowState adds `flow_analysis`, `plan`, `draft_envelope`, `evaluation`, `route`, and `terminal_reason`. Requirements belong only to `flow_analysis.requirements`. Plan and draft versions live inside their typed envelopes; no duplicate scalar version owner exists. The old immutable context/revision reducers and old state fields remain.

## Guard sequence for downstream owners

1. ESSAY-11 calls `validate_analysis_context(analysis, request)` to compare personal evidence quote offsets with the actual normalized request experience.
2. ESSAY-12 calls `validate_plan_context(plan, analysis, research)` and `validate_draft_context(draft, plan, analysis, research)`. These reject foreign evidence/requirement/source references, personal/company evidence collisions and source-type swaps, missing mandatory requirement mappings, changed plan versions/claim kinds/evidence selections, paragraph mismatches and fit-reference mixups.
3. ESSAY-13 captures request ID, draft and plan before starting F, then calls `bind_evaluation(request_id, evaluation, captured_draft, captured_plan)`. This returns frozen `EvaluationBinding`, which state stores under `evaluation`. The guard validates evaluated versions, issue references and range bounds, named paragraph containment, and overlap with each named claim.
4. ESSAY-14 calls `require_ready_evaluation(binding, current_request_id, current_draft, current_plan)` immediately before ready construction. It rejects another request's binding, newer versions, modified same-version contents, failed criteria and lengths outside 801..1000. A replacement draft leaves previous evaluation unusable until F returns a fresh binding.

The binding is code-owned, not model output. It must be created against the captured invocation context, never rebound to whatever happens to be latest when an asynchronous evaluation returns. The helpers are structural checks; semantic fact review and the complete ready-response builder remain downstream work.

## Evidence

`/Users/jay/Projects/essay-service/.omo/evidence/essay21/member-b/report.md` records scenarios, exact invocations, observations and artifacts.
