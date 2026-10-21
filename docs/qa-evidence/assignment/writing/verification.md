# ESSAY-12 writing role verification

Verified 2026-10-21 in `/Users/jay/Projects/essay-service/assignment`.

Scope: executable D/E/I role modules, common ESSAY-21 contracts, controlled analysis/research fixtures, and real OpenAI SDK adapter with an HTTP MockTransport. No live model, MCP, complete LangGraph/API integration, or prose-quality approval was performed. Those remain ESSAY-14/16/17 work. Shared contracts/state/budget/settings and other roles' code were not edited.

## Result and invocation

41 tests passed. Targeted basedpyright: 0 errors/warnings. Ruff: all checks passed. Programming discipline: no violations in 8 files.

Run from `assignment/`:

```sh
.venv/bin/pytest tests/test_writing*.py -v --junitxml=../.omo/evidence/writing/junit.xml
.venv/bin/ruff check agent/nodes/{plan,write,revise,writing_support}.py tests/test_writing*.py
.venv/bin/basedpyright agent/nodes/{plan,write,revise,writing_support}.py tests/test_writing*.py
python3 /Users/jay/.codex/plugins/cache/sisyphuslabs/omo/5.1.38/skills/programming/scripts/python/check-no-excuse-rules.py agent/nodes/plan.py agent/nodes/write.py agent/nodes/revise.py agent/nodes/writing_support.py tests/test_writing_nodes.py tests/test_writing_boundaries.py tests/test_writing_expression.py tests/test_writing_provider.py
PYTHONPATH=. .venv/bin/python ../.omo/evidence/writing/replay.py
```

Captured artifacts (repository-relative):

- `.omo/evidence/writing/pytest.txt`: verbose scenario outcomes, 41 passed.
- `.omo/evidence/writing/junit.xml`: per-case binary pass/fail results.
- `.omo/evidence/writing/ruff.txt`, `types.txt`, `discipline.txt`: static verification output.
- `.omo/evidence/writing/replay.py`, `replay.txt`, `role-replay.json`: reproducible synthetic D/E/I role replay and full typed output. The replay records versions 1→2, writer calls=2, revision count=1, unchanged outside text, and invalidated evaluation.

No active ulw-loop attempt existed (`ULW_LOOP_PLAN_MISSING`); evidence is under `.omo/evidence/writing/`.

## Acceptance evidence

Every row uses the pytest invocation above and the captured `pytest.txt`/`junit.xml`. The named test is the exact scenario selector; parametrized variants appear separately in the artifacts.

| Criterion | Scenario(s) | Binary observable |
| --- | --- | --- |
| Code-owned D plan, requirements, IDs, target allocation | `test_plan_is_code_owned_and_covers_requirements` | selected e1/job, mandatory r1 covered, target sum 900, zero model calls |
| D revision from F without another analysis/research/model plan call | `test_d_revision_restructures_without_model_and_e_uses_reserved_budget`, `test_d_reconsiders_affected_experience_from_existing_candidates` | version2, three sections, alternate existing e2 selected for affected requirement, zero model calls, reservation remains1 |
| E consumes original context and fixed plan with bounded output | `test_writer_returns_short_draft_unpadded_for_full_review`, `test_writer_rejects_invented_or_misbound_output` | exact DraftEnvelope returned; invented fact, unmapped prose, foreign source and wrong version rejected |
| Complete source sentences and source order, Unicode offsets | `test_plan_blocks_invalid_personal_evidence`, `test_unicode_sentence_offsets_and_source_order_are_preserved` | fragments, incorrect offsets, missing candidates/gaps and reordered source facts rejected |
| Job priority, no fabricated values, late missing evidence | `test_plan_prioritizes_job_and_omits_optional_company_values`, `test_plan_late_missing_research_stops_without_a_model` | job selected, optional company value omitted, missing company/job raises MISSING_EVIDENCE before model |
| Reserved D→E and I only; no count reset | `test_d_then_e_uses_one_writer_call_and_keeps_reservation`, `test_second_revision_reservation_cannot_cross_routes`, `test_d_rejects_forged_observed_revision_count` | writer calls1, revision count1, second reservation rejected, forged observed count rejected |
| I applies only latest allowed sentence range, fixes facts/plan | `test_revision_reassembles_full_draft_and_invalidates_evaluation`, `test_revision_rejects_control_attacks_before_model`, `test_revision_rejects_adversarial_patches_without_refund`, `test_revision_rejects_mixed_plan_and_wording_issues_before_model` | exact outside text unchanged, fact claim unchanged, paragraph end recomputed, version2/plan1, F cleared; unreserved/wrong-route/stale/foreign/overlap/outside/old-version/fact/invention rejected |
| No string padding/truncation at length boundary | `test_writer_preserves_length_boundary_for_f_without_padding` | input model texts of length800/801/1000/1001 returned byte-for-byte for full F; no ready decision |
| False achievements/company fact laundering/new revision facts | writer rejection and revision adversarial scenarios; `test_company_evidence_cannot_be_laundered_as_personal_fact`, `test_explicit_future_achievement_is_not_treated_as_past_fact` | invented past fact and source-kind mismatch rejected; explicit future intent accepted |
| Real provider schema, no retries, sanitized failures | `test_writing_schema_and_budget_cross_real_sdk_wire`, `test_writer_operational_errors_are_sanitized_without_retry` | E/I strict JSON schemas, store=false, no tools, one wire call; HTTP/invalid JSON/timeout typed error, one call/no repair |

## ESSAY-14 handoff

- `agent.nodes.plan.build_plan(state, budget, reservation=None) -> WorkflowState`: initial code plan. For revision, pass the real `RevisionReservation` returned by G's `await budget.reserve_revision("D")`. D validates current request/draft/plan/evaluation binding. It reconsiders affected ranked candidates and separates current interpretation/future intent sections. Merge its update before E.
- `agent.nodes.write.WriteNode(provider).run(state, budget) -> WorkflowState`: E. ModelProvider owns model reservation, so the node does not double-charge. It emits the full draft and clears `evaluation`.
- `agent.nodes.revise.RevisionNode(provider).run(state, budget, reservation) -> WorkflowState`: I. G must reserve I first. Both token route/count and live budget route/count are checked, independently of observed state count. I returns the full updated draft and clears F. Always invoke full F again.
- `WritingError.code` is sanitized. `MISSING_EVIDENCE` is a late missing-input signal; `MISSING_CONTEXT` is a programming/handoff failure; malformed facts/ranges/reservations/versions must not become ready. Existing `FlowStateError`, Pydantic boundary errors and provider/budget exceptions propagate for G/API to map. No HTTP result assembly is added here.
- The local fixture extends `tests.flow_fixture.research()` with an explicit synthetic `user_provided` job/source so D receives a realistic validated C handoff. The shared fixture is unchanged. Synthetic length tests are counting tests, not essay quality evidence.

## Limits and self-review

Exact structural/source checks do not prove arbitrary natural-language semantics. F must independently review the entire draft, including factual claims disguised as interpretation/future intent. A conservative lexical guard rejects digits and common past-achievement expressions in generated nonfact claims; it is deliberately not presented as a complete semantic validator. Sentence boundaries conservatively require terminal punctuation, and each selected personal evidence item must be one complete source sentence. Company claim text is copied from verified research evidence rather than paraphrased. The minimal plan chooses the first ranked candidate per requirement and first verified job requirement; F still assesses actual question/job coverage.

Self-review checked only owned files and preserved concurrent work. Tests were split by responsibility after the file-size discipline check; the complete role suite was rerun after that change. The replay and tests do not call B/C/research or reserve a new revision inside D/I. No claims are made about the future graph's exactly-once node scheduling or end-to-end normal4/max6 call counts.
