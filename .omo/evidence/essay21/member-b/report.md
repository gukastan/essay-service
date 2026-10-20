# Member B verification

Scope: ESSAY-21 shared revision reservation, flow state and structural/version guards. Tests use synthetic inputs and real Pydantic, AnyIO and LangGraph objects. No paid/external requests, business routing or service E2E claims.

Working directory for commands: `/Users/jay/Projects/essay-service/assignment`.

## Compatibility correction after leader review

The leader reproduced a real compatibility defect: adding REVISION_EXHAUSTED to ExecutionBudgetError expanded the accepted input of research.error_response beyond its code map. The correction restores the original budget-error variants and introduces a separate RevisionReservationError for exhausted/invalid revision routes. Runtime route validation rejects values other than D/I before consuming the reservation. The unused top-level requirements mirror was removed; flow_analysis.requirements is canonical.

| Scenario | Invocation | Binary observable | Artifact |
| --- | --- | --- | --- |
| Exhaustion bypasses research budget-error handler | `.venv/bin/pytest tests/test_flow_revision.py tests/test_flow_state.py tests/test_flow_context_boundaries.py tests/test_state.py tests/test_budget.py -v` | `test_revision_exhaustion_does_not_enter_research_budget_error_boundary` PASSED; catches distinct revision exception instead of reaching real research adapter | `tests-compatibility.log` |
| Invalid H/J/empty/lowercase route leaves opportunity available | Same invocation | Four `test_invalid_revision_route_does_not_consume_opportunity` cases PASSED; snapshot remains 0/None and subsequent valid D succeeds | `tests-compatibility.log` |
| State, guards, reservation and legacy budget regressions | Same invocation | 55 passed, exit 0, including real LangGraph analysis handoff and C's independently updated error boundary checks | `tests-compatibility.log` |
| Strict lint | `.venv/bin/ruff check agent/budget.py agent/state.py agent/flow_state.py tests/test_flow_state.py tests/test_flow_revision.py` | Exit 0 | `ruff-compatibility.log` |
| Full-project types | `.venv/bin/basedpyright` | Exit 0, zero errors/warnings/notes | `basedpyright-compatibility.log` |
| Programming audit | `.venv/bin/python /Users/jay/.codex/plugins/cache/sisyphuslabs/omo/5.1.38/skills/programming/scripts/python/check-no-excuse-rules.py agent/budget.py agent/state.py agent/flow_state.py tests/test_flow_state.py tests/test_flow_revision.py` | Exit 0, no violations in 5 files | `audit-compatibility.log` |

`hashes-compatibility.txt` records the corrected owned files. The earlier 46-test evidence below is retained as historical evidence; the 55-test run supersedes it.

## Original implementation verification

| Criterion / exact scenario | Invocation | Binary observable | Captured artifact |
| --- | --- | --- | --- |
| Simultaneous D and I reservation | `.venv/bin/pytest tests/test_flow_revision.py tests/test_flow_state.py tests/test_flow_context_boundaries.py tests/test_state.py tests/test_budget.py -v` | `test_concurrent_d_and_i_have_exactly_one_winner` PASSED; exactly one reservation succeeds and one returns REVISION_EXHAUSTED | `tests-final.log` |
| No refund after writer error, real task-group cancellation or deadline expiry | Same invocation | `test_revision_is_not_refunded_after_writer_failure`, `test_revision_survives_actual_cancellation`, `test_revision_stays_consumed_after_request_deadline` PASSED | `tests-final.log` |
| Request isolation and no reset on state reconstruction | Same invocation | `test_requests_reserve_independently_and_state_cannot_reset_budget` PASSED | `tests-final.log` |
| Real LangGraph state extension and existing reducer protections | Same invocation | `test_real_graph_preserves_flow_values_and_bound_evaluation` and all existing `test_state.py` scenarios PASSED | `tests-final.log` |
| Reject stale versions, same-version mutations and foreign evaluation bindings | Same invocation | All `test_flow_state.py` guard scenarios PASSED | `tests-final.log` |
| Cross-context IDs, source types, ranges and false length pass | Same invocation | All 15 independent `test_flow_context_boundaries.py` scenarios PASSED | `tests-final.log` |
| Preserve existing model/token limits and timeout reservation behavior | Same invocation | Existing `test_budget.py` normal/revision/race/cancel/deadline scenarios PASSED | `tests-final.log` |
| Strict lint for owned files | `.venv/bin/ruff check agent/budget.py agent/state.py agent/flow_state.py tests/test_flow_state.py tests/test_flow_revision.py` | Exit 0, All checks passed | `ruff.log` |
| Strict types for owned files | `.venv/bin/basedpyright agent/budget.py agent/state.py agent/flow_state.py tests/test_flow_state.py tests/test_flow_revision.py` | Exit 0, zero errors/warnings/notes | `basedpyright-owned.log` |
| Programming-rule audit | `.venv/bin/python /Users/jay/.codex/plugins/cache/sisyphuslabs/omo/5.1.38/skills/programming/scripts/python/check-no-excuse-rules.py agent/budget.py agent/state.py agent/flow_state.py tests/test_flow_state.py tests/test_flow_revision.py` | Exit 0, no violations in 5 files | `audit.log` |

Final relevant suite: 46 passed, exit 0. Log files are in this directory.

Full-project `.venv/bin/basedpyright` was rerun after C repaired the independently edited test's Any update variable: exit 0, zero errors/warnings/notes. The directly observed result is recorded in `basedpyright.log`.

The issue-to-claim range defect was found by C: a span 100..110 could reference a claim located at 0..5. B added occurrence-overlap validation; the complete relevant suite above includes the now-passing counterexample. C owns the original failed-run artifact.

`hashes.txt` records owned source/test hashes after verification. Repository model/time policy files were not modified by B.
