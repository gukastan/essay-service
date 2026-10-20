# A — contract implementation evidence

Scope: additive flow contracts, public exports, strict-tool include paths, typed synthetic fixtures and owned tests. No legacy research/output model changes; no provider adapter changes; no role algorithms, external requests, commits or Jira actions.

## Scenarios and observables

All commands ran from `/Users/jay/Projects/essay-service/assignment`. Exact invocations and exit codes are captured in each artifact.

| Criterion | Scenario / invocation | Binary observable | Artifact |
| --- | --- | --- | --- |
| Bounded requirement/plan contracts | pytest `test_flow_contracts.py`: strict versions, duplicate selection, unknown evidence, allocation/order, dangling analysis candidates | Expected ValidationError; positive frozen JSON roundtrip | `tests.txt` |
| Draft version/paragraph spans | Same test file: outside bounds, omitted text, zero-length spans | Expected ValidationError | `tests.txt` |
| Complete evaluation | Same test file: empty/omitted/duplicate criteria, failure without issue, invalid issue scopes | Expected ValidationError; complete explicit result exposes all_passed | `tests.txt` |
| Strict provider compatibility | pytest `test_flow_provider.py`: recursive strict-schema assertion on eight flow/terminal models | All object properties required, extra fields forbidden recursively | `tests.txt` |
| Existing contracts/provider preserved | pytest `test_contracts.py test_provider.py` | All existing tests pass, combined 111 passed | `tests.txt` |
| Type/lint/format discipline | basedpyright, ruff check/format, programming skill checker on all eight owned Python files | All exits 0; 0 type errors/warnings, no lint/style/discipline violations | `types.txt`, `lint.txt`, `format.txt`, `discipline.txt` |
| Final file identity / size | SHA-256 and nonblank/noncomment line counts | All owned Python files below 250 pure LOC | `hashes.txt` |

All artifact paths above are relative to this report. Test-only synthetic source/draft text is used. Real semantic evaluation and routing are deliberately not implemented by this ticket.

## Ownership handoff

Changed product/config files: `assignment/agent/contract_flow_plan.py`, `contract_flow_draft.py`, `contract_flow_evaluation.py`, `contract_flow_route.py`, `contracts.py`, `assignment/pyproject.toml`.

Changed owned tests: `assignment/tests/flow_fixture.py`, `test_flow_contracts.py`, `test_flow_provider.py`.

Public API and field/bound details: `.omo/teams/team-d5c089ce/artifacts/api-contract.md`.

ESSAY-11 consumes FlowAnalysisResult; ESSAY-12 consumes WritingPlan/DraftEnvelope; ESSAY-13 produces Evaluation; ESSAY-14 consumes route/terminal types and B's contextual state guards. Existing foundation role payloads remain compatible but future flow uses the additive types.

## Self-review

Each new module owns one contract boundary. External inputs parse into frozen models with strict integer/boolean fields and typed validation errors. No raw untyped data escapes model boundaries. Literal test switches are exhaustive; the targeted unnecessary-comparison setting preserves assert_never checks. No casts, Any annotations, broad catches, hidden retries, new dependencies, logging, destructive operations, or user-facing guarantees were introduced. Shared uniqueness validation serves multiple contracts. Meaningful negative tests fail if the corresponding validators are removed.
