# ESSAY-10 independent QA handoff (superseded)

Final completed handoff is `artifacts/checks-final.md`; the original progress notes below are retained as history.

Owner B has modified only assignment/tests and research/checks evidence. No paid call invoked.

Completed:

- test_source_http.py, test_source_page.py: 32 initial passing deterministic HTTP policy/extraction checks, `checks/http-first.txt`.
- page_wire.py, test_source_socket.py: actual default HTTPX/socket path, numeric target observed at connector, ephemeral local GET server; `checks/socket-granted.txt` passed after initial sandbox denial in `checks/socket-first.txt`.
- test_source_verification.py: source identity/IDs/exact quotation/ATS and overflow regressions. `checks/trust-red.txt` preserves real aggregate-cache and blog false acceptance. Tests now expect retained ATS root provenance.
- test_source_user.py: exact supplied text identity, fabricated source, legitimate API-key job and negated-conflict cases. `checks/user-control-red.txt` retains four failures before product fixes.
- test_research_node.py: actual stdio MCP + real OpenAI SDK to local deterministic HTTP; 7 passed in `checks/node-first.txt`. Privacy sentinels excluded from actual request, one model/two hosted reservations observed before wire.
- test_source_control.py: DNS system resolver denial, unsupported media, event-driven cancellation. Strict fixes applied.
- test_source_domestic.py: exact parent employer vs NAVER Cloud/WEBTOON/Kakao Pay/Bank; unrelated role in navigation; JS shell denial.
- test_source_conflicts.py: numeric/negation critical conflict and optional-fact suppression.
- test_research_live.py: explicit paid opt-in runner, unique sanitized artifacts, never invoked by B. Driver needs final type/lint/default-skip verification.

Next steps before completion:

1. Update driver NAVER case to user-selected public posting `https://recruit.navercorp.com/rcrt/view.do?annoId=30005457`, role `N배송 운영 지원`.
2. Run full current Python suite and 12 JavaScript foundation tests with paid opt-ins unset. Capture strict ruff/basedpyright/no-excuse, source hashes and JUnit logs.
3. Repair only owned test issues; send product failures to A. Add no extra scope.
4. Replace this handoff with exact final criterion/scenario/command/artifact mapping and limitations.

Product API drift already accommodated: FetchedPage now includes job_titles/employers; fixture fetched() explicitly supplies Engineer title. Model candidate fixture company is Acme; deliberate mismatch is isolated in its own test. SourceVerifier accepts only title-bound official role evidence and domestic exact employer metadata; core owns product and configuration.
