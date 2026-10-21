# ESSAY-16 Python·MCP·Vue 전체 회귀 검증

- 검증일: 2026-10-21
- 범위: `assignment/`의 실제 LangGraph·FastAPI 생성 API·Vue 프록시와 브라우저, 기존 Next.js 보존본
- 외부 유료 모델 호출: 0회. 생성 결과는 통제 모델·조사 대역의 시험자료이며 문장 품질이나 실제 기업 사실성의 증거가 아니다.

## 실제 연결 결과

`tests/test_end_to_end.py`는 실제 분석·계획·작성·검토 노드를 `POST /api/drafts`와 Vue 프록시를 거쳐 호출한다. 정상 ready200은 900코드포인트·모델 예약4회·수정0회였다. D와 I 수정은 각각 모델6회·수정1회로 ready200, 정보 부족은 needs_input200, 수정 후 품질 실패는422였다. 혼합 구성/문장 지적은 D로 갔고, I 수정 후 새로운 구성 실패는 이전 통과를 재사용하지 않고422였다. 모델 오류502·시간 초과504·키 누락500은 원문 없이 반환됐으며 자동 재시도는 없었다. 동시 요청 두 건은 별도 requestId·모델 예산4회를 가졌다. 사용자 제공 공고 본문 `협업을 요구한다.`는 별도 시험자료로 표시했다.

`tests/essay16_fixture_server.py`는 제품 API·Vue 프록시를 각각 실제 localhost Uvicorn 서버로 실행하되 모델과 조사 결과만 통제한다. 실제 Chrome에서 `tests/essay16_browser.cjs`를 실행해 POST 3회, 요청 본문 전송과 URL 내 경험 비노출, 근거 표시, 900코드포인트 결과, 편집 후 미검토 표시와 현재 내용 복사를 관찰했다. 이어 실제 API의 needs_input200·품질 실패422를 화면에 표시하고 이전 편집 결과와 입력을 보존하는지 확인했다. 브라우저 오류는 0건이다. [완료 화면](essay16-real-chain-ready.png)·[편집 화면](essay16-real-chain-edited.png)·[보완 화면](essay16-real-chain-needs.png)·[품질 실패 화면](essay16-real-chain-quality.png)을 저장했다. 초안의 반복 문구는 고정 시험 출력이며 작성 품질을 보여주지 않는다.

## 최소 명세 NF-01~10 대응

| ID | 실행 증거 | 판정 |
| --- | --- | --- |
| NF-01 | `test_proxy_api_graph_real_roles_and_terminal_status[case0]`, 기존 `test_actual_role_nodes_join_into_reviewed_ready` | 최초 H·4회 |
| NF-02 | 같은 프록시 시험의 missing 사례, `test_analysis_gap_cancels_parallel_research_before_writing` | J·조기 조사 취소·작성 없음 |
| NF-03 | 같은 프록시 시험의 반복 plan 사례, `test_failed_revision_returns_quality_error_without_third_writer` | J422·세 번째 작성 없음 |
| NF-04 | 같은 프록시 시험의 plan 사례, `test_mixed_plan_and_wording_feedback_replans_before_wording` | D→E→전체 F, 6회·수정1회 |
| NF-05 | 같은 프록시 시험의 wording 사례, `test_revision_rejects_adversarial_patches_without_refund` | I→전체 F, 계획·사실 범위 고정 |
| NF-06 | `test_missing_information_wins_over_plan_issue_in_routing`, `test_mixed_plan_and_wording_feedback_replans_before_wording`, `test_second_revision_reservation_cannot_cross_routes` | 정보 부족 우선·그다음 D·공통 기회1회 |
| NF-07 | 프록시 시험의 plan→pass 및 wording→pass 사례 | 수정 한도1에서도 H |
| NF-08 | `test_revision_rejects_control_attacks_before_model`, `test_revision_rejects_adversarial_patches_without_refund`, `test_evaluation_rejects_every_missing_mandatory_criterion` | 잘못된 범위·버전·평가 계약 거부 |
| NF-09 | `test_wording_repair_rechecks_entire_draft_and_rejects_new_plan_failure`, `test_revision_evaluates_full_new_draft_and_keeps_semantic_failure` | I 뒤 전체 F·이전 pass 미재사용 |
| NF-10 | 새 프록시 운영 오류·동시 요청 시험, `test_active_mcp_cancellation_retains_charge_and_blocks_next_send`, `test_actual_mcp_adversarial_results_are_sanitized` | timeout/단절/취소·요청 격리 |

추가 경계: Python `test_length_uses_code_points_when_at_boundaries`와 `test_writer_preserves_length_boundary_for_f_without_padding`는 800/801/1000/1001자를 확인했고 JavaScript `test_web_contract.mjs`도 같은 경계를 검사했다. `test_text_parity.py`는 CRLF·한글·이모지 offset의 Python/JavaScript 일치를 확인했다. `test_mcp.py`는 실제 stdio 도구 발견·프로토콜 호출·model1/hosted2 선예약을, `test_mcp_control.py`는 단절·잘못된 응답·취소를 확인했다. 동명 기업·상충 공고·출처/ID 오류·지시문·사설망 URL·허위 성과는 `test_source_*.py`, `test_personal_analysis.py`, `test_review_evidence.py`의 경계 테스트에 포함돼 전체 회귀에서 다시 통과했다. 공식 자료의 실시간 진위는 이 대역 검증만으로 확정하지 않는다.

## 실행 결과

| 실행 | 결과 |
| --- | --- |
| `assignment/.venv/bin/python -m pytest -q` | 485 passed, 유료 opt-in 2 skipped, 31.46초. localhost 시험 포트 허용 환경 |
| `assignment/.venv/bin/ruff check .` / `ruff format --check .` | 검사 통과 / 97개 파일 형식 통과 |
| `assignment/.venv/bin/basedpyright` | 0 errors, 0 warnings, 0 notes |
| `node --test tests/test_foundation.mjs tests/test_web_contract.mjs` | 13 passed |
| `node tests/essay16_browser.cjs <프록시 포트> <API 포트>` | Chrome 실제 POST 3건·900자·편집/복사·보완/품질 실패 후 이전 결과 보존·pageerror 0 |
| 루트 `pnpm test` / `pnpm typecheck` / `pnpm lint` | 기존 Next.js 156 passed·1 skipped / 성공 / 41개 파일 통과 |
| `git diff --name-only`로 보존 경로 비교 | `tests/fixtures/live-samples.json`, v1 QA와 ESSAY-9 증거의 기준 커밋 대비 변경 없음 |

첫 동시성 시험은 테스트용 프록시 HTTP 클라이언트를 두 요청에 재사용해 실패했다. 요청마다 독립 클라이언트를 만들도록 시험 코드를 고친 뒤 새 파일 11개와 전체 485개가 통과했다. 제품 코드 변경은 없었다. 180초 요청 deadline, 190초 프록시·195초 브라우저 제한은 코드와 단축/가상시계 테스트로 확인했으며 180초를 연속으로 기다리는 실제 HTTP 시험은 하지 않았다.

ESSAY-17에서 실제 OpenAI 모델·공식 기업 자료·기존 5개 샘플의 새 서비스 실행, 실제 작성 품질·사실성, 작성자 승인을 별도로 확인한다. 위 통제 출력이나 기존 ESSAY-7 승인을 그 결과로 대신하지 않는다.
