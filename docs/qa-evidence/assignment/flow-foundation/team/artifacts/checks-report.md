# ESSAY-21 independent boundary checks

Member C owns only the four new test files listed below and this report. No product module, configuration, business node, Jira issue, or commit was changed by C.

## Direct results

All commands ran from `/Users/jay/Projects/essay-service/assignment`.

Latest compatibility repair verification: the leader identified that adding `REVISION_EXHAUSTED` to `ExecutionBudgetError` widened an existing research mapper boundary without a matching mapping. B separated `RevisionReservationError` from the existing budget errors and rejected invalid revision routes before consuming the opportunity. C added ten independent regression cases to the existing two boundary test files. Authoritative artifacts under `/Users/jay/Projects/essay-service/.omo/evidence/essay21-checks/` are now `repair-tests.txt` and `repair-integration.xml` (**137 passed**), `repair-lint.txt` (clean), `repair-format.txt` (4 files already formatted), `repair-types.txt` (0 errors/warnings/notes), `repair-discipline.txt` (no violations), and `repair-hashes.txt`. Each text artifact contains its exact invocation and exit code. C observed the repaired behavior directly; the leader owns the original compatibility failure observation.

Repair scenarios: `test_revision_exhaustion_uses_separate_control_error` requires `RevisionReservationError("REVISION_EXHAUSTED")`; `test_research_retains_existing_execution_budget_error_mapping` verifies the three existing budget errors map to BUDGET_EXCEEDED/TIMEOUT/CANCELLED. `test_untyped_invalid_revision_route_preserves_the_shared_opportunity` starts a real local Python subprocess with JSON inputs `"H"`, `"J"`, `""`, `null`, `1`, and `["D"]`; each produces INVALID_REVISION_ROUTE, leaves revision_count zero and route absent, and allows a subsequent I reservation with no model calls. All ten cases use the same recorded repair suite invocation and have individual JUnit results.

Earlier formatting follow-up: the leader found all four owned test files needed formatting. `uv run --frozen ruff format tests/test_flow_boundaries.py tests/test_flow_context_boundaries.py tests/test_flow_evaluation_boundaries.py tests/test_flow_handoff.py` reformatted only those four files. No assertions or fixture behavior changed during that formatting step. The `final-*` artifacts preserve that 122-test state; initial/focused/integration artifacts below preserve the earlier verification history.

| Scenario / success criterion | Exact invocation | Binary observable | Captured artifact |
| --- | --- | --- | --- |
| Empty/oversized IDs, duplicate plan IDs, unknown candidates/claims, unselected evidence, invalid allocations/versions, invalid draft spans and absent claim text | `uv run --frozen pytest tests/test_flow_boundaries.py tests/test_flow_evaluation_boundaries.py tests/test_flow_context_boundaries.py tests/test_flow_handoff.py -q` | Exit 0; 61 passed | `/Users/jay/Projects/essay-service/.omo/evidence/essay21-checks/focused.txt` |
| Mandatory criterion omission at each of seven positions; duplicate pass row; failed criterion without issue; all-pass with issue; false missing-info/invalid wording scope | Same focused invocation | Exit 0; malformed inputs raise Pydantic ValidationError | Same focused artifact; named cases in integration.xml |
| Actual OpenAI SDK/provider adapter receives incomplete Evaluation through local HTTP transport; strict required/all-fields/additionalProperties=false schema; no retry | Same focused invocation | Typed INVALID_RESPONSE, exactly one request and one reserved model call | Same focused artifact; `test_real_sdk_adapter_rejects_incomplete_mandatory_evaluation` |
| Personal/company provenance swaps, colliding evidence IDs, unknown selected evidence, omitted mandatory requirement, wrong fit-reason domains | Same focused invocation | Typed SOURCE_TYPE_MISMATCH / INVALID_REFERENCE | Same focused artifact; named context cases in integration.xml |
| Invalid issue anchor IDs, out-of-draft span, claim named with unrelated text span, model all-pass on short draft | Same focused invocation | Typed INVALID_REFERENCE / INVALID_RANGE / INVALID_LENGTH | Same focused artifact; prior failing span case in initial-failure.txt |
| Typed downstream examples and ready/needs_input/quality wire contract distinction | Same focused invocation | Public TypeAdapter roundtrip succeeds; invented quality missing-fields/reasonCode rejected | Same focused artifact; `test_flow_handoff.py` |
| Shared D/I race, no refund after failure/cancel/deadline, independent requests, actual graph state, stale/same-version/foreign evaluation binding, old budget/time constraints, recursive strict schemas | `uv run --frozen pytest tests/test_flow_boundaries.py tests/test_flow_evaluation_boundaries.py tests/test_flow_context_boundaries.py tests/test_flow_handoff.py tests/test_flow_contracts.py tests/test_flow_provider.py tests/test_flow_state.py tests/test_flow_revision.py tests/test_budget.py tests/test_budget_timing.py tests/test_state.py -q --junitxml=/Users/jay/Projects/essay-service/.omo/evidence/essay21-checks/integration.xml` | Exit 0; 122 passed, zero failures/skips | `/Users/jay/Projects/essay-service/.omo/evidence/essay21-checks/integration.txt` and `integration.xml` |
| Test lint | `uv run --frozen ruff check tests/test_flow_boundaries.py tests/test_flow_evaluation_boundaries.py tests/test_flow_context_boundaries.py tests/test_flow_handoff.py` | Exit 0; All checks passed | `/Users/jay/Projects/essay-service/.omo/evidence/essay21-checks/lint.txt` |
| Strict test types | `uv run --frozen basedpyright tests/test_flow_boundaries.py tests/test_flow_evaluation_boundaries.py tests/test_flow_context_boundaries.py tests/test_flow_handoff.py` | Exit 0; 0 errors, 0 warnings, 0 notes | `/Users/jay/Projects/essay-service/.omo/evidence/essay21-checks/types.txt` |
| Programming discipline | `uv run --frozen python /Users/jay/.codex/plugins/cache/sisyphuslabs/omo/5.1.38/skills/programming/scripts/python/check-no-excuse-rules.py tests/test_flow_boundaries.py tests/test_flow_evaluation_boundaries.py tests/test_flow_context_boundaries.py tests/test_flow_handoff.py` | Exit 0; no violations in 4 files | `/Users/jay/Projects/essay-service/.omo/evidence/essay21-checks/discipline.txt` |

## Finding and repair

The first focused run produced **53 passed, 1 failed**: `test_issue_claim_anchor_must_overlap_the_named_claim`. Claim `c1` occurs at code-point range 0..5, while the issue named `c1` but selected 100..110. `validate_evaluation_context` accepted it. Exact output is preserved in `/Users/jay/Projects/essay-service/.omo/evidence/essay21-checks/initial-failure.txt`.

B repaired the product guard by requiring overlap with an occurrence of the named claim. The unchanged scenario passes in both subsequent focused and integration evidence. C also identified the readiness length bypass during inspection; B added the independent 801..1000 check before the first focused run. `test_model_pass_cannot_override_failed_code_length_check` verifies that an all-pass model Evaluation cannot make a five-character draft ready. There is no captured pre-fix runtime failure for the length finding.

A test-only handoff construction initially retained the PlanClaim subclass in the legacy Claim response field, causing Python object equality after JSON roundtrip to differ despite identical wire shape. C corrected the fixture to construct the public legacy Claim shape explicitly. This was a fixture issue, not a product wire regression.

## Typed downstream handoff

Public common imports are from `agent.contracts`; control guards are in `agent.flow_state`. The reusable typed examples are in `assignment/tests/test_flow_handoff.py`.

| Consumer | Example / API | Meaning |
| --- | --- | --- |
| ESSAY-11 B/C | `flow_example().analysis: FlowAnalysisResult`; shared `tests.flow_fixture.analysis()` | Requirements and personal evidence in one analysis result. Validated candidates reference `e1`. Research remains a separate role. |
| ESSAY-12 D/E | `flow_example().plan: WritingPlan`, `.draft: DraftEnvelope` | Code-built plan v1, paragraph `p1`, claim `c1`, evidence `e1`, draft v1 bound to plan v1. |
| ESSAY-12 I | `test_sentence_revision_fixture_uses_new_draft_and_evaluation_versions` | A shape-only revised draft v2 retains plan v1 and needs evaluation v2. This does not implement an edit operation. |
| ESSAY-13 F | `flow_example().evaluation: Evaluation` | Exactly seven mandatory criterion results. `bind_evaluation(request_id, evaluation, draft, plan)` captures context; `require_ready_evaluation(binding, request_id, draft, plan)` checks readiness. |
| ESSAY-15 ready | `ready_fixture() -> ReadyResponse` | Existing camelCase wire contract, synthetic 900-code-point content, preserved legacy Claim response shape. Intended future HTTP status: 200. |
| ESSAY-15 missing information | `needs_input_fixture() -> NeedsInputResponse` | `missingFields=["experience"]`, concrete question, `EXPERIENCE_INSUFFICIENT`. Intended future HTTP status: 200. |
| ESSAY-15 quality limit | `quality_failure_fixture() -> ErrorResponse` | `QUALITY_CHECK_FAILED`, no invented missing fields or draft. Intended future HTTP status: 422. |
| ESSAY-15 length-only quality limit | `quality_failure_fixture("LENGTH_VALIDATION_FAILED")` | Existing error shape with length code. Intended future HTTP status: 422. |

These are explicitly synthetic contract fixtures. The repeated text in the draft is test material, not generated essay content. No analysis/writer/reviewer node, full G route selection, actual `/api/drafts` endpoint, Vue UI, live OpenAI/MCP search, semantic factuality evaluation, or real essay quality was completed or claimed. HTTP statuses above describe downstream requirements; this work does not exercise an implemented HTTP route.

Normal four/max-six model calls, shared one revision, 18,000 reserved output tokens, existing timing and no automatic retry are covered by the directly rerun budget/revision suites. B's owned tests already exercise D/I concurrency and state reset isolation, so C did not duplicate those implementations.

## Final source hashes

Invocation: `shasum -a 256 tests/test_flow_boundaries.py tests/test_flow_context_boundaries.py tests/test_flow_evaluation_boundaries.py tests/test_flow_handoff.py` from assignment/. Exact latest output is captured in `repair-hashes.txt`.

```text
8b82bc870799d9dff25fe91297eccb1597a853deb95e096adba37a3da26c70cc  tests/test_flow_boundaries.py
282961aa703235fab36c9d61d5b455f915417f1415d121b0bf9876a9a81fcad6  tests/test_flow_context_boundaries.py
3d98ce12265fb76a84c1ab457f9d1520f40df3c2ed0702e6762dd7829947b6d0  tests/test_flow_evaluation_boundaries.py
e81574992e72c1f99b61dfa84d0c10f363c6f343f71e2af21a0783386135a99f  tests/test_flow_handoff.py
```

Self-review: each file has one responsibility (malformed structures, context references, evaluation adapter, typed examples). Latest nonblank/noncomment line counts are 123, 191, 113, 120 respectively. Untrusted mutations are parsed through real Pydantic boundaries; the deliberately untyped revision input is JSON passed to a fixed local subprocess without casts or suppressions. No exception suppression, variant fallback, operational logging, or product implementation was added. Each rejection case would fail if its corresponding guard disappeared.
