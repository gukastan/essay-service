# ESSAY-11 B/C role verification

Executed 2026-10-21 in `/Users/jay/Projects/essay-service/assignment`, Python 3.12.15.
Scope: executable independent analysis/join modules with a typed mock model provider and synthetic research result. No live OpenAI, MCP, search, full graph/API, writing or browser integration was executed. Those remain ESSAY-14/16/17 responsibilities.

## Implementation and handoff

- `agent.nodes.analyze.AnalyzeNode(provider).run(request, budget, request_id)` returns `AnalysisSuccess` or `NeedsInputResponse`. Operational provider/budget exceptions propagate to the caller for the common error adapter. Invalid contextual output becomes sanitized `ProviderError("INVALID_RESPONSE")`; no retry occurs.
- One `ModelProvider.generate(role="analysis", schema=FlowAnalysisResult)` shares B/C extraction. Existing provider reserves analysis once in the request budget. The node has no research/MCP dependency. Reinvocation with the same budget is rejected by the provider reservation.
- `validate_personal_analysis` checks normalized exact source quotes, code-point offsets, complete sentence boundaries, original order, selected instruction markers, and literal question grounding for mandatory text/checkCondition. Optional advice remains nonmandatory. The prompt requires no added past roles/actions/outcomes/numbers/timing/causality/mental changes and concrete blocking gap questions.
- `agent.nodes.analysis_evidence.AnalysisJoin(request, request_id).run(analysis, research)` returns `None` while pending, forwards early terminal responses, or returns `EvidenceBundle(analysis, research)` only when both branches are present. Personal evidence remains separate from research. Missing company/core job evidence blocks; absent values do not. Cross-kind ID collisions/missing source references are rejected.
- `ResearchSuccess` must come from existing source-verifying `ResearchNode`; the join does not itself authenticate sources or rerun research. ESSAY-14 must execute branches concurrently, cancel unnecessary pending work on terminal outcomes, and start D only once on `EvidenceBundle`.
- No shared contracts, exports, state, budget, configuration, original source or other roles' files changed.

## Reproduction and captured observables

Artifacts use `.omo/evidence/essay11-analysis/` because `omo-agent-toolkit ulw-loop status --json` reported `ULW_LOOP_PLAN_MISSING` (no active attempt).

From `assignment/`:

```sh
.venv/bin/pytest tests/test_personal_analysis.py tests/test_analysis_join.py -v --junitxml=../.omo/evidence/essay11-analysis/pytest.xml
.venv/bin/ruff check agent/nodes/analyze.py agent/nodes/analysis_evidence.py tests/test_personal_analysis.py tests/test_analysis_join.py
.venv/bin/basedpyright agent/nodes/analyze.py agent/nodes/analysis_evidence.py tests/test_personal_analysis.py tests/test_analysis_join.py
.venv/bin/python /Users/jay/.codex/plugins/cache/sisyphuslabs/omo/5.1.38/skills/programming/scripts/python/check-no-excuse-rules.py agent/nodes/analyze.py agent/nodes/analysis_evidence.py tests/test_personal_analysis.py tests/test_analysis_join.py
```

| Criterion / exact scenario | Binary observable | Captured artifact |
| --- | --- | --- |
| Normalized CRLF/emoji evidence, linked requirement/candidate, one analysis call, no research payload | `test_analysis_normalized_emoji_one_call_and_no_research`: correct start 8; one invocation; second reservation rejected | `.omo/evidence/essay11-analysis/pytest.txt`, `pytest.xml` |
| Fabricated role/numeric result/time/causality/mental change | Five `test_analysis_rejects_added_facts` cases raise INVALID_RESPONSE | same pytest artifacts |
| Input injection/false achievement directives/incomplete sentence selected as evidence | Four `test_analysis_rejects_instruction_or_fragment_evidence` cases raise INVALID_RESPONSE | same pytest artifacts |
| Long experience and concrete blocking question | `test_analysis_long_experience_and_concrete_gaps`: long valid source succeeds; gap returns needs_input with exact question | same pytest artifacts |
| Unrequested mandatory condition | `test_analysis_rejects_invented_mandatory_condition`: INVALID_RESPONSE | same pytest artifacts |
| Wrong offsets and partial exact substring | Three `test_analysis_rejects_wrong_codepoint_offsets` and `test_analysis_rejects_exact_but_partial_sentence`: INVALID_RESPONSE | same pytest artifacts |
| Operational failure, retry zero | `test_analysis_operational_failure_never_retries`: TIMEOUT propagates, one invocation | same pytest artifacts |
| Both branches required, separate evidence, missing values allowed | `test_analysis_join_requires_both_branches_and_keeps_sources_separate`: pending None, then EvidenceBundle | same pytest artifacts |
| Company/core job missing | Two `test_analysis_join_core_gaps_stop`: needs_input | same pytest artifacts |
| Cross-kind collision/missing company source | Two `test_analysis_join_rejects_collisions_and_missing_sources`: INVALID_REFERENCE | same pytest artifacts |
| Early terminal while other branch pending | `test_analysis_join_propagates_early_terminal`: same gap/error returned | same pytest artifacts |
| Static checks | Ruff “All checks passed”; basedpyright “0 errors, 0 warnings, 0 notes”; audit “no violations in 4 file(s)” | `.omo/evidence/essay11-analysis/ruff.txt`, `typecheck.txt`, `audit.txt` |

Result: 23 tests passed. Each scenario above is in the captured verbose/JUnit report. Pure line counts: analyze 104, join 76, personal tests 161, join tests 82. Files have single responsibilities; boundary models remain typed; no Any/casts/ignore directives or broad exception catch was added.

## Limits

These mocks establish deterministic guard/call/join behavior, not real model extraction quality or semantic completeness. Literal mandatory grounding is deliberately conservative: model paraphrases of required conditions are rejected. Sentence extraction requires terminal punctuation and whitespace/end after the quote; incomplete notes should yield concrete gaps instead. Instruction-marker filtering is defense in depth, not a complete natural-language prompt-injection detector. Complete original sentences may themselves contain incorrect user assertions; source equality cannot establish truth. Semantic past/future/category judgments still depend on the analysis prompt and subsequent F evaluation. No live-model factuality approval or actual ESSAY-14 branch cancellation/integration is claimed.
