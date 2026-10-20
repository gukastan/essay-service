# ESSAY-10 independent checks

Final run: 2026-10-20, baseline HEAD `2da2c898f71120ce087963feae12727848f24b64`, shared working tree. **242 Python tests passed, 2 paid tests skipped; 12 JavaScript tests passed.** Original 131 Python cases remain included. This QA worker invoked no paid request.

Current integrated gates are leader-owned `../leader-final-*` and `../leader-post-concat-*`; this worker directly read their captured outputs. Current source binding and owned-test audit use `final-userline-*`. Earlier 214-, 220- and 234-test artifacts remain preserved. The final iteration adds complete raw user requirement values bound to their same LF-line role/requirements heading. The full suite preceded one semantics-preserving explicit `+` between regex string literals; lint, formatting and types were rerun after that correction.

## Invocations and results

All commands ran from `assignment/`. The prior section-stage JUnit records the earlier 234-case suite; final integrated text and the focused eight-case output establish the current total.

| Invocation | Binary observable | Artifact |
|---|---|---|
| `.venv/bin/python -m pytest -q` | Exit 0; 242 passed, 2 paid opt-in skips, 19.95 seconds | [integrated text](../leader-final-pytest.txt) |
| `env -u ESSAY_LIVE_RESEARCH -u ESSAY_LIVE_COMPATIBILITY PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest tests/test_user_line_evidence.py -q -p no:cacheprovider` | Exit 0; 8 passed, 0.58 seconds | [complete user values](user-line-complete-value.txt) |
| `node --test tests/test_foundation.mjs` | Exit 0; 12 passed, 0 failed | [JavaScript](final-js.txt) |
| `.venv/bin/ruff check --no-cache .` | Exit 0 | [lint](../leader-post-concat-ruff.txt) |
| `.venv/bin/ruff format --check --no-cache .` | Exit 0; 59 files formatted | [format](../leader-post-concat-format.txt) |
| `.venv/bin/basedpyright --project pyproject.toml` | Exit 0; 0 errors, 0 warnings | [typing](../leader-final-types.txt) |
| `.venv/bin/python /Users/jay/.codex/plugins/cache/sisyphuslabs/omo/5.1.38/skills/programming/scripts/python/check-no-excuse-rules.py tests/test_source*.py tests/test_user_line_evidence.py tests/research_fixture.py tests/naver_section_fixture.py tests/research_live_capture.py tests/page_wire.py tests/test_research_node.py tests/test_research_live.py` | Exit 0; no violations in 17 files | [audit](final-userline-no-excuse.txt) |
| `shasum -a 256` over source modules, node, adapter, MCP boundary, budget, server, manifest and all Python/JS tests | Per-file hashes captured after explicit concatenation correction | [source binding](final-userline-source-sha256.txt) |

## Criterion mapping

The invocation for all Python cases is the full pytest command above. Earlier cases are individually recorded in `final-sections-pytest.xml`; the final eight cases are parameterized in `test_user_line_evidence.py` and captured in `user-line-complete-value.txt`.

| Criterion | Exact scenario or parameterized family | Observable |
|---|---|---|
| Actual MCP, one model and hosted capacity two | `test_real_mcp_node_verifies_source_with_single_reserved_sdk_request` | Production stdio MCP and real SDK reach one local HTTP request; `(1,2)` reservations observed before SDK wire; verified source/job returned |
| Question/experience privacy | Same scenario and existing `test_actual_mcp_discovery_reserved_before_sdk_wire_and_private_fields_removed` | Private sentinels absent from actual SDK bytes; allowed domain keys only; `max_tool_calls=2`, `store=false` |
| Officiality not asserted by model/name/TLS | `test_model_official_label_name_and_https_do_not_create_trust` | Lookalike host, unapproved subdomain and same-name host admit no source/job |
| Provenance IDs, fetched timestamp, quotes | `test_official_evidence_uses_fetched_identity_quote_and_time_not_model_claims`; `test_fabricated_or_changed_quote_cannot_become_job_evidence`; `test_invalid_evidence_ids_fail_closed` | Fetched time replaces fabricated 2099 date; unsupported dates removed; mutated quote rejected; duplicate/reserved/unknown IDs yield `INVALID_RESPONSE` |
| Official whitespace normalization only | `test_official_whitespace_only_variation_returns_canonical_fetched_quote`; `test_nonwhitespace_quote_changes_are_rejected`; `test_user_posting_and_job_quote_preserve_original_internal_whitespace` | Official newline/tab equivalent returns canonical fetched wording; translation/Markdown/case/word changes rejected; user spacing preserved |
| Verified posting-section provenance | `test_exact_bullet_in_bound_posting_section_uses_fetched_section`; `test_real_mcp_node_accepts_exact_korean_bullet_with_server_section_provenance` | Exact Korean bullet without repeated role/header admitted from same-card Required Skills/duties section; returned excerpt comes from fetched section, never translated model metadata; actual MCP node still reserves model 1/hosted 2/page 1 |
| Section boundaries fail closed | `test_culture_and_values_sections_do_not_become_job_requirements`; `test_requirement_heading_outside_posting_card_cannot_authorize_quote`; `test_card_title_must_match_verified_structured_posting`; `test_section_fallback_still_rejects_changed_or_translated_quote`; `test_quote_cannot_stitch_text_from_two_requirement_sections`; `test_explicit_section_does_not_override_affiliate_employer`; `test_explicit_section_does_not_override_multiple_postings` | Culture/value/footer text, wrong card title, changed quote, cross-section stitching, affiliate employer and ambiguous postings all rejected |
| ATS exact relationship and retained proof | `test_external_ats_requires_exact_official_link_not_shared_host` | Exact official link admits job plus root provenance IDs; another tenant on shared host does not |
| Role context, not incidental vocabulary | `test_role_elsewhere_on_page_does_not_promote_company_values_to_job_requirement`; `test_incidental_role_and_requirements_in_official_blog_are_not_hiring_evidence`; `test_role_heading_in_explicit_nonvacancy_culture_page_is_not_job_evidence` | Values/blog/culture content does not become job requirements |
| Domestic employer isolation | `test_shared_recruiting_host_requires_exact_posting_employer`; `test_navigation_role_cannot_override_actual_posting_title`; `test_employer_and_role_cannot_be_combined_across_distinct_postings`; `test_javascript_shell_does_not_promote_model_source_excerpt` | NAVER/네이버 and Kakao/카카오 exact employer accepted; affiliates, navigation-only role, cross-posting identity and JS shells rejected |
| User text bound to supplied input | `test_unknown_company_supplied_posting_uses_server_owned_text_and_source_id`; `test_supplied_posting_must_match_exact_company_and_role_identity`; `test_model_fabricated_user_source_is_not_treated_as_supplied_text` | Exact normalized input gets `user-posting`; AcmeCompetitor/wrong role and model-created user text cannot bind |
| Complete user requirement value | `test_partial_user_quote_requires_same_line_role_and_requirement_context` (8 cases) | Exact whole value after same-line role/requirements colon accepted, including original double spaces; different line/role, values heading, case change, omitted leading negation and omitted trailing caveat rejected; returned source and quote preserve supplied text |
| Malicious instructions remain data | `test_injected_instruction_cannot_promote_fabricated_requirement`; `test_visible_unicode_extraction_drops_executable_text_and_preserves_link_target`; `test_security_role_requirement_with_api_key_is_valid_source_data` | No fabricated requirement admitted; executable containers removed; legitimate API-key qualification retained |
| Optional values versus missing identity/job | Successful node scenario has empty company facts; `test_node_returns_typed_supplement_or_error_from_real_mcp` | Missing optional values succeeds; missing role/access denial supplements; unknown/same-name company supplements; malformed ID errors |
| Critical conflict fail-closed | `test_reported_critical_conflict_suppresses_even_exact_evidence`; `test_resolved_company_disagreement_fails_closed`; `test_conflicting_core_requirements_fail_closed_without_model_gap`; `test_optional_conflicting_facts_are_dropped_while_agreeing_job_survives`; `test_negated_conflict_observation_does_not_suppress_agreeing_evidence` | Critical jobs removed, optional disputed facts omitted, numeric/English-negation conflicts found without model gap, negated conflict observation accepted |
| SSRF URL and DNS denial | `test_nonpublic_or_mixed_dns_never_sends`; `test_system_dns_mixed_answers_are_rejected`; `test_unsafe_url_rejected_before_dns` | Loopback/private/link-local/mapped-private IPv6/mixed answers rejected before send; unsafe schemes/credentials/backslash never reach resolver |
| Connection pinning | `test_connection_target_is_numeric_but_host_and_tls_identity_are_original`; `test_default_transport_connects_pinned_address_and_sends_original_host` | Numeric target plus original Host/SNI; real default HTTPX connector receives numeric IP and ephemeral GET server receives original Host |
| Redirect/byte/text limits | `test_redirect_private_target_is_checked_and_never_sent`; `test_redirect_loop_charges_each_hop_and_stops_before_fourth_send`; `test_raw_page_limit_accepts_exact_boundary_only`; `test_aggregate_page_text_cannot_reenter_via_cached_overflow_page` | Unsafe target not sent; three-hop ceiling; 1 MiB accepted and +1 rejected; cleaned text max12000; aggregate cache bypass rejected |
| Shared time, cancellation, no retry | `test_research_deadline_shared_across_redirects_blocks_later_send`; `test_active_read_cancellation_stops_followup_before_transmission`; original budget/MCP timing suites | Monotonic45-second boundary blocks later send; event-driven cancellation blocks follow-up; failures send once; existing30/45/180 guards pass |
| Live diagnostics and paid default skip | Main actual-MCP node scenario exercises `ResearchCapture`; `test_paid_research_node_once` | Candidate/page/verification records observed locally; explicit paid runner skipped by default |

## Preserved failures

- [trust-red.txt](trust-red.txt): cached aggregate overflow bypass and official blog false job admission.
- [user-control-red.txt](user-control-red.txt): company substring identity, legitimate API-key quote rejection, negated conflict rejection, model identity mismatch acceptance.
- [paired-identity-red.txt](paired-identity-red.txt): culture H1 false posting and employer/role cross-pairing between two JSON-LD postings. [paired-identity-fixed.txt](paired-identity-fixed.txt) records 28 passing focused cases after correction.
- `socket-first.txt` is a sandbox bind denial followed by passing `socket-granted.txt`. `trust-first.txt` predates corrected fixture ordering and is not product-defect proof. `paired-identity-green.txt` contains a fixture alias-construction error despite its initial filename; it is superseded by the fixed and final results.
- [diagnostics-local.txt](diagnostics-local.txt): recorder exercised through local MCP, 7 passed and paid runner skipped. [quote-first.txt](quote-first.txt): six focused whitespace/provenance cases pass.
- [sections-first.txt](sections-first.txt): two positive section cases initially failed, with 11 negative cases passing. [sections-node-first.txt](sections-node-first.txt): all 14 new cases passed after integration, including actual stdio MCP. [DOM observation](naver-dom-observation.md) records the public, unpaid page read and bounded fixture construction.

## Real versus fixture scope

MemoryPages and synthetic company pages are finite fixtures. The socket scenario uses the real default HTTPX transport and test-only connector redirection to loopback; production private-network policy is unchanged. MCP, SDK serialization, process lifetime and local HTTP traffic are real. No external search quality, current hiring status or full essay flow is inferred. Leader-owned `live-node-*.json` files are separate paid runs, not this worker's executions.

Conflict testing covers conservative numeric frames and explicit English negation, not arbitrary semantic contradiction. Official identity is curated to NAVER, Kakao, OpenAI and Anthropic; unsupported/ambiguous posting formats require supplementation. The final implementation requires one paired JSON-LD JobPosting for official job evidence.

The NAVER section fallback is restricted to the reviewed `recruit.navercorp.com/rcrt/view.do` card/detail DOM and the same verified single posting. It does not infer requirement sections from arbitrary pages.

All 17 owned files are below 200 pure lines ([measurement](final-userline-loc.txt)), each owning one behavior group or fixture. Boundary models remain typed. No `Any`, cast, type-ignore or broad catch was added. The diagnostic callback's four arguments preserve the existing SourceVerifier method signature; test-only wrappers delegate to production and pytest restores them.
