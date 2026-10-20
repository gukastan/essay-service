# ESSAY-10 core handoff

Implemented product modules only under assignment/agent, plus explicit lint/typecheck inclusions in assignment/pyproject.toml. ESSAY-19 MCP/Responses wire contract and budgets unchanged. Research prompt now asks contiguous role-bearing quotations. No API/UI/graph/other-role implementation, credentials, paid calls, commit or push performed by core owner. Other contributors' docs/tests preserved.

## Public API
See ../../teams/team-fb2113fe/artifacts/api-contract.md (final-tightening section supersedes initial draft).
ResearchNode.run(input,budget,request_id) performs actual MCP candidate call and returns ResearchSuccess containing only verified result + safe usage counters, or existing NeedsInputResponse/ErrorResponse. Caller owns MCP lifespan. DraftRequest is projected before MCP. Missing/unsupported company or job proof requests input. Provider/protocol failures are sanitized errors. External cancellation propagates; budget cancellation/deadline remains terminal.

## Evidence ledger
| Criterion/scenario | Invocation | Binary observable | Artifact |
| --- | --- | --- | --- |
| Actual MCP once, reserved-before-call, request projection, sanitized outcomes; public pinned socket; source identity/excerpts/user text/HTTP safety | `cd assignment && UV_CACHE_DIR=/private/tmp/essay10-uv uv run --frozen pytest tests/test_source_verification.py tests/test_source_user.py tests/test_source_http.py tests/test_source_control.py tests/test_research_node.py tests/test_source_socket.py -q` | 55 passed | focused-tests.txt |
| Foundation regression + all independent new tests | `cd assignment && UV_CACHE_DIR=/private/tmp/essay10-uv uv run --frozen pytest -q` | All unpaid tests pass; paid tests explicitly skipped | full-tests.txt |
| Strict product lint | `uv run --frozen ruff check agent/source_*.py agent/nodes agent/research.py` | All checks passed | ruff.txt |
| Full scoped strict types | `uv run --frozen basedpyright` | 0 errors/warnings | basedpyright.txt |
| Language hygiene | `uv run --frozen python /Users/jay/.codex/plugins/cache/sisyphuslabs/omo/5.1.38/skills/programming/scripts/python/check-no-excuse-rules.py agent/source_*.py agent/nodes/research.py agent/research.py` | no violations | no-excuse.txt |
| Module responsibility/size review | `awk 'NF && $1 !~ /^#/ {counts[FILENAME]++} END {for (file in counts) print file, counts[file]}' assignment/agent/source_*.py assignment/agent/nodes/research.py assignment/agent/research.py` | Individual bounded modules | module-sizes.txt |

B owns independent red/green scenario evidence. Leader owns public real-source and paid opt-in QA; core's recorded automated suite is not paid-model proof.

## Trust/stability limits
Curated operator registry: OpenAI, Anthropic, NAVER/네이버, Kakao/카카오 only. Primary company/careers provenance is maintained data, not automatic arbitrary-company recognition. Unknown companies require explicit supplied posting with literal company/role. Shared domestic sites require exact JobPosting hiringOrganization employer; affiliates excluded. Official jobs require actual h1/JobPosting title plus role-bearing exact quote, requirement section markers, and job/careers route. Unsupported layouts, JS-only pages, inaccessible pages and paraphrased/noncontiguous candidate excerpts fail closed. This is intentionally conservative, so valid jobs may need pasted text.

Fetched root evidence is retained for external hiring-site links; trust is exact URL, never whole ATS host. Publication/closing dates are omitted rather than invented. No current-open-job assertion. HTTP uses numeric pinned destination + original Host/TLS SNI, no proxy/automatic redirect/retries, public DNS/IP checks including transition-address rejection, per-hop reservation, 1MiB response, aggregate admitted cleaned text12000, common45-second deadline. Hosted-tool internals remain unmetered separately.

Conflict checks cover explicit critical candidate gaps, mismatched resolved identity, and identical claim frames with changed numeric/polarity data. Optional disputed facts are dropped; critical job disputes request input. This does not prove semantic agreement across arbitrary prose. Instruction phrase filtering is supplemental: all page/model/user text stays data and cannot change budgets, tools or credentials regardless of wording.

## Architectural self-review
Each module owns one boundary: HTTP, HTML extraction, structured posting metadata, curated trust, candidate admission, conflict comparison, verification orchestration, or node outcomes. Pydantic parses external JSON; immutable dataclasses/protocols carry internal values. Tagged source matching has exhaustive guards. No Any/casts/type ignores, broad catches, new logging, persistence or prompt dumps. Mutable HTML buffers are explicit parser state. Existing HTTPX manifest retained (no dependency migration). Tests owned by B exercise counterexamples, real MCP and actual local socket behavior. Final source verifier is206 pure lines (the200–250 warning band); it owns source verification orchestration, and all other touched modules are127 lines or fewer. Further growth would require splitting source collection.

## Post-review correction
C/B reproduced two real blockers after the initial freeze: editorial career-culture h1 accepted as posting; independent title/employer lists cross-paired affiliate and target postings. Both are fixed narrowly. `FetchedPage.postings` now holds frozen paired JSON-LD Posting records. Exactly one structured JobPosting must establish role and (where required) employer together; h1 alone cannot establish identity. The earlier h1/independent-tuple API description is superseded. Unsupported or multiple-posting layouts request input. Exact two regressions passed (`paired-identity-fix.txt`); full final gate results and source hash manifest are recorded alongside this handoff.

Final frozen gate after paired identity correction: **214 passed, 2 explicit paid opt-in skips**,20.82s (`full-tests.txt`). Ruff/basedpyright/no-excuse pass. `source-sha256.txt` records all owned product/config bytes; `hash-verification.txt` confirms manifest matches after final gate. Core stops editing at this manifest. Earlier55-test evidence predates this final identity correction; use214-test full run as final acceptance evidence.

## Bounded actual-page integration correction
Actual NAVER model candidates used translated metadata and Markdown-decorated quotation, correctly yielding no admitted evidence. Failures remain preserved by leader. Prompt now explicitly requires original-language visible-page excerpts, own-source contiguous requirement substrings, and no added Markdown/translation. Official quotation matching additionally canonicalizes only whitespace runs, exactly like existing page extraction. Words, case, punctuation, Markdown and language remain literal; raw user source/quote stays untouched and takes precedence. B's six behavior regressions passed (checks/quote-first.txt). C reviewed this delta with no new finding. Current source-sha256.txt supersedes earlier freeze; actual paid same-case rerun remains leader-owned and is not implied by automated tests.

Final quotation-delta gate: **220 passed, 2 explicit paid opt-in skips**,22.30s. Ruff/type/no-excuse pass; source manifest verified after full test run. Source verifier now208 pure lines (warning band); remaining modules<=127. No further product edits after this hash freeze.

## Actual NAVER section correction
A second actual model result supplied correct literal Korean bullets but translated source metadata and omitted repeated role/heading from each bullet. Added source_sections.py for one reviewed NAVER DOM only: exact host/path; one card_wrap; matching card_title; detail_box with What You'll Do or Required Skills heading. Exact single JobPosting/employer proof unchanged. Literal candidate bullet must occur wholly inside one fetched section; returned excerpt is that section, not the translated candidate metadata. No extra model call/prefetch/MCP redesign. Parser does not claim arbitrary DOM support or detail_wrap binding.

Actual no-model public page check admitted4 recorded literal job quotes,1source,1page read,0model calls (public-section-replay.json). Input used the prior diagnostic's excerpt prefix and job quotes; this is expressly NOT a replay of a complete paid response, nor proof that a subsequent model produces admissible candidates. Leader owns paid same-case rerun. B preserves initial section failures and green section/MCP scenarios.

Final section implementation full gate: **234 passed, 2 explicit paid opt-in skips**,21.95s. A subsequent prompt-only correction removed obsolete repeated-role/long-page quotation instructions and explicitly requests individual original-language NAVER duty/skill bullets and their requirement-section excerpt, excluding whole-page employment metadata. Verifier/HTTP/identity bytes unchanged after that full gate. Post-prompt ruff/basedpyright/no-excuse pass. Current source-sha256.txt/hash-verification.txt records this final prompt-aligned freeze; no claim that the234 suite reran after the prose-only delta. Paid same-case success remains leader-owned. Public section replay retains its partial-diagnostic,0model-call label.

## Final user-provided line proof
New fallback accepts a raw quote only when it equals the COMPLETE raw requirement value after an explicit requested-role + requirements/qualifications/responsibilities/자격요건/담당업무/요건 colon heading on one supplied LF line. Company identity remains required in the supplied source. No interior substring admission: omitted negation and trailing caveats fail. Original source text and returned quote remain unchanged, including internal spaces. Legacy full-quote path unchanged. Eight focused cases passed; final strict/full evidence below supersedes earlier gates. The earlier E501 misreport is corrected: prompt literal wraps were AST-SHA identical, failed QA artifacts preserved, each final gate checked independently.

## TERMINAL handoff — final current bytes
Product edits complete. After core became idle, leader explicitly transferred the one regex concatenation syntax correction to B; B added an explicit `+` between raw regex pieces, preserving the assembled expression. No further core product/test edits. Current source-sha256.txt/hash-verification.txt includes that correction.

I directly read the final leader artifacts (repository-relative paths):
- docs/qa-evidence/assignment/research/leader-final-pytest.txt: `.venv/bin/python -m pytest -q`, exit0,242passed/2 explicit paid opt-in skips,19.95s.
- docs/qa-evidence/assignment/research/leader-post-concat-ruff.txt: `.venv/bin/ruff check --no-cache .`, exit0.
- docs/qa-evidence/assignment/research/leader-post-concat-format.txt: `.venv/bin/ruff format --check --no-cache .`, exit0,59files formatted.
- docs/qa-evidence/assignment/research/leader-final-types.txt: `.venv/bin/basedpyright --project pyproject.toml`, exit0,0errors/0warnings.
These final artifacts supersede stale intermediate core gate files and the erroneous earlier clean-gate claim. Failures remain preserved; no gate was skipped or relabeled.

Leader separately reports successful actual NAVER and synthetic user-provided runs, with8 deliberate paid requests total (3successes and5 retained positive-assertion failures). This is leader-owned live evidence, not a core paid-run claim; core made no paid calls. Public-section-replay.json remains expressly a partial diagnostic replay against a fresh public page with0model calls.

No outstanding implementation edits. Registry/layout/semantic limits above remain: conservative official identity, single paired posting, reviewed NAVER card-section proof, exact quotations, exact whole supplied requirement-line value, bounded DNS-pinned direct HTTP. No broad scraper, extra model call, full graph/API/UI, or other role added.
