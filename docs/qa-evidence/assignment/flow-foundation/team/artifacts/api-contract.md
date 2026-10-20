# ESSAY-21 flow contract handoff

All new models are frozen Pydantic `Contract` subclasses, reject unknown fields and serialize camelCase. Import public types from `agent.contracts`. Legacy `AnalysisResult`, `QuestionRequirement`, `WriterResult`, `ReviewResult`, `ResearchResult` and HTTP responses remain unchanged. Future ESSAY-11/12/13 flow uses the following additive types, not legacy analysis/review payloads.

- `FlowRequirement(id, text, mandatory, check_condition, candidate_evidence_ids)`.
- `FlowAnalysisResult(requirements, experience_evidence, gaps)`: validates unique requirement/evidence IDs and candidate references into personal evidence.
- `PlanClaim(id,text,kind,evidence_ids)`: bounded subtype of existing Claim; kinds remain user_fact/company_fact/interpretation/future_plan.
- `PlanParagraph(id,purpose,order,target_characters,requirement_ids,claim_ids)`.
- `WritingPlan(version,selected_evidence_ids,claims,paragraphs)`: contiguous one-based paragraph order; total target allocation 801–1000; unique IDs; selected evidence contains claim evidence; paragraph claims cover exactly plan claims. Context guards validate actual requirement/evidence references.
- `ParagraphSpan(paragraph_id,start,end)`: half-open Unicode code-point offsets.
- `DraftEnvelope(version,plan_version,draft,paragraphs,claim_map,fit_reasons)`: nonoverlapping ordered bounded spans cover all non-whitespace text; claim text occurs in draft. Allows 1–4000 characters so F can represent length failure. Context guard compares the envelope with the fixed plan.
- `CriterionResult(criterion_id,passed)`: explicit strict boolean.
- `EvaluationIssue(id,criterion_id,claim_ids,paragraph_ids,start,end,reason,scope,instruction,missing_fields)`: start/end required together or both null; wording requires an anchored span; missing fields required only for missing_info.
- `Evaluation(draft_version,plan_version,criteria,issues)`: exact seven unique mandatory results, issues cover exactly failed criteria, computed all_passed property.

Mandatory criterion IDs: `contract_evidence`, `user_factuality`, `company_factuality`, `question_coverage`, `job_fit`, `length`, `expression_kind`.

Issue scopes: `missing_info`, `plan_or_claim`, `wording`. Versions are strict integers 1–2, matching the initial pass plus one global revision. IDs ≤80 code points; structured text ≤500; purpose ≤200; up to 20 requirements, 40 claims/evidence references, 10 paragraphs, 40 issues. No hidden reasoning fields exist.

`FlowRoute` is H/J/D/I. `TerminalReason` discriminates on kind:

- `ReadyTerminal(kind="ready",route="H",reason="all_criteria_passed")`.
- `MissingInputTerminal(kind="needs_input",route="J",reason="missing_required_information",missing_fields,questions,reason_code)` preserves existing reason codes.
- `QualityTerminal(kind="quality_failure",route="J",reason="revision_limit"|"invalid_plan",code="QUALITY_CHECK_FAILED"|"LENGTH_VALIDATION_FAILED")` has no missing information fields.
- `OperationalTerminal(kind="operational_error",code)` uses existing operational error codes and has no draft.

Terminal contracts describe control outcomes only. Actual G precedence and HTTP response adaptation remain ESSAY-14; semantic evaluation remains ESSAY-13; D/E/I algorithms remain ESSAY-12. B owns cross-object provenance/version checks and the shared atomic D/I revision reservation.

Typed fixtures: `tests.flow_fixture.analysis()`, `research()`, `plan()`, `draft()`, `evaluation()`. Fixtures are synthetic and perform no external calls.
