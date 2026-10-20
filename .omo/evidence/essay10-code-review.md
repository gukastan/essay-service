# ESSAY-10 final code review

codeQualityStatus: WATCH
recommendation: APPROVE
blockers: []

Final frozen review, 2026-10-20. This report supersedes interim BLOCK and earlier passing snapshots/counts. Exact current product, tests and evidence SHA-256 binding: `.omo/teams/team-fb2113fe/artifacts/final-close-review-hashes.json`. B `docs/qa-evidence/assignment/research/checks/final-userline-source-sha256.txt` independently checked against current bytes: zero mismatches. Baseline: 2da2c898f71120ce087963feae12727848f24b64. ULW status returned ULW_LOOP_PLAN_MISSING, so fallback report location used. No notepad path supplied.

## CRITICAL
None.

## HIGH
None remaining. Previously demonstrated blockers are resolved:
- Generic career/editorial h1 is not job identity; exactly one structured JobPosting is required.
- Title and employer stay paired in the same typed posting; multiple postings fail closed.
- Aggregate-overflow pages cannot enter cache and bypass the text cap on reuse.
- External ATS URLs require exact fetched official linkage, with root provenance retained.
- Direct HTTP restricts targets/ports, rejects unsafe and mixed DNS answers and transition addresses, pins numeric connection with original Host/SNI, checks/charges each redirect and applies byte/text/shared-time caps. Fast transport timeout stops the shared budget.

## MEDIUM
None requiring changes within the reviewed scope.

## LOW
`assignment/agent/source_admission.py:34`: supplemental instruction-phrase filtering can reject legitimate job text discussing system prompts. This reduces coverage but fails toward supplementation; do not present it as complete prompt-injection detection. General semantic conflict detection is also not claimed.

## Final narrow deltas

- Prompt now asks original-language literal duty/skill bullets for NAVER section verification rather than repeated role/header or whole-page metadata. Original ownership, privacy, one-model and unverified-candidate instructions remain. Only research prompt changed at that stage; formatting-only string wrapping preserved its assembled content.
- Official quotation canonicalization only collapses whitespace to the same representation used by fetched-page extraction. Translation, Markdown insertion, punctuation/case/content changes remain unsupported. User text stays raw.
- NAVER section parser is limited to exact recruitment detail host/path and observed one-card/title/detail-box layout. Exact card title must match the same single verified posting. A candidate quote must occur literally in one actual supported duties/skills section, with original source URL/ID association. Returned excerpt comes from fetched section text, not translated model metadata. Unrelated footer/value sections, wrong title/employer, multiposting and stitched quotes fail. This is bounded site support, not generic DOM understanding.
- New user-provided fallback requires company identity plus the requested role and explicit requirements/qualifications/responsibilities marker with colon on the same original LF line. Quote must equal the **complete raw value after that heading**, preserving internal whitespace and content. No interior-substring acceptance, cross-line binding, translation or removal of negation/trailing caveats. Existing official verifier is unchanged by this fallback.
- Final explicit `+` between regex string pieces was inspected: assembled regex unchanged. The last lint/type issues are fixed and final gates below are clean.

## Verification evidence

Inspected final root artifacts under `docs/qa-evidence/assignment/research/`:
- `leader-final-pytest.txt`: **242 passed, 2 paid opt-in skips, exit 0**, 19.95 seconds.
- `leader-post-concat-ruff.txt`: all checks passed, exit 0.
- `leader-post-concat-format.txt`: 59 files formatted, exit 0.
- `leader-final-types.txt`: zero errors/warnings, exit 0.
- `checks/final-userline-no-excuse.txt`: no violations in 17 owned files.

Reviewer independently ran staged focused suites after material changes: 75 source tests after paired-identity fixes; 42 after quotation delta; 55 after section integration; latest **35 passed in 0.46s** covering complete user-line values, raw user evidence, section proof and official quotation behavior. Latest invocation/output saved at team artifact `reviewer-userline-tests.txt`; prior focused evidence remains alongside it. The final regex formatting-only concatenation was inspected after that run, and the root final gates cover the frozen result. Tests were not replaced with prompt-prose assertions.

Read actual leader-owned result artifacts:
- `checks/live-node-620b999e-3d4d-40ce-ac7b-1fc42d5cda3a.json`: NAVER research-success, four official requirements, 11.825 seconds, one model call.
- `checks/live-node-2e80bf28-3442-4a38-9c16-c3e2d9de0235.json`: synthetic posting research-success, one user_provided requirement, 5.605 seconds, one model call.

Earlier failed real assertions are retained; they are not relabelled as success. Reviewer made no paid calls and does not claim full UI/product QA. Paid requests and evidence accounting remain leader-owned.

## Skills and scope

Loaded programming/SKILL.md, Python reference README and remove-ai-slops/SKILL.md and applied both perspectives throughout. Final tests distinguish demonstrated acceptance/rejection behavior, use real parsing and real MCP/socket seams where appropriate, and include qualifier-omission regressions. No deletion-only, requested-removal, tautological, implementation-constant or brittle prompt-prose tests identified in scope. Paired posting and bounded NAVER section parsing are necessary trust-boundary work for the observed failures; no unrelated extraction framework or dependency migration was introduced. No blocking violation of either skill perspective remains.

Approval covers this conservative research implementation. Maintained roots are OpenAI, Anthropic, NAVER/네이버 and Kakao/카카오; shared-site employer identity is separate from publisher trust. Unsupported layouts, JS-only/inaccessible pages and ambiguous data may require pasted user_provided evidence. Source ownership is not inferred from model labels, TLS or company-name text. Existing HTTPX reuse and limited semantic checks are intentional scope choices. Design/provenance memos: team artifacts `trust-audit.md` and `domestic-trust.md`.
