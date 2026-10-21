# ESSAY-13 F 평가 검증

2026-10-21. 범위: `ReviewNode`, `validate_evidence`, 역할별 통제 입력 검증. 실제 모델·검색 또는 ESSAY-14 그래프 통합 결과가 아니다.

## 구현과 인계

- `ReviewNode(provider).evaluate(ReviewInput, budget)`는 코드 평가, 독립 모델 평가, 병합 `EvaluationBinding`을 `ReviewAssessment`로 반환한다. `run(state, budget)`는 `evaluation`, `deterministic_checks`, `usage` 상태 갱신만 반환한다. G/H/J 라우팅·HTTP ready는 구현하지 않는다.
- `ReviewInput`은 요청 ID/입력, 분석, 조사, 계획, 전체 초안을 frozen 계약으로 포착한다. 매 실행마다 전체 입력으로 `review` 모델 역할을 한 번 호출한다. 기존 OpenAI 어댑터가 예산/30초/재시도0을 담당한다.
- 코드가 계약/참조/원문 offset을 검증하고, 개인 사실의 완전한 원문 문장·순서, 회사 사실의 원문/출처 발췌, 본문 주장 대응, 글자 수, 경험·기업·직무 근거와 연결을 검사한다. 모델은 문항 실제 응답, 직무 연결 의미, 시점·인과·회사 귀속 및 해석/미래 계획을 포함한 일곱 기준을 독립 검토한다. 코드의 구조 통과는 의미적 사실성 증명이 아니다.
- 코드/모델 issues를 합쳐 기준별 결과를 재계산하므로 모델 pass가 코드 fail을 지울 수 없다. 지적 ID 충돌을 코드가 재명명한다. 계약·오래된 버전·잘못된 범위는 오류로 종료한다. 사실 문장 수정 또는 실질 기준 실패를 wording으로 보내는 모델 출력도 거부한다.
- 정보 부족은 실제 missingFields를 가진 missing_info, 근거가 있지만 내용이 잘못되면 plan_or_claim이다. 구체적인 범위가 있는 표현 변경만 wording이다. 재평가 결과를 이전 평가와 합성하지 않으며, 세 번째 모델 검토는 기존 예산이 차단한다.

## 재현 명령과 증거

작업 디렉터리: `/Users/jay/Projects/essay-service/assignment`.

```
.venv/bin/python -m pytest tests/test_review_evidence.py tests/test_review_node.py tests/test_review_state.py tests/test_flow_state.py tests/test_flow_evaluation_boundaries.py tests/test_flow_handoff.py -v --junitxml=../.omo/evidence/essay13/pytest.xml
.venv/bin/ruff check agent/nodes/review.py agent/validate_evidence.py tests/test_review_evidence.py tests/test_review_node.py tests/test_review_state.py
.venv/bin/basedpyright agent/nodes/review.py agent/validate_evidence.py tests/test_review_evidence.py tests/test_review_node.py tests/test_review_state.py
```

결과: 62 passed (신규 F 31개 + 기존 흐름 31개), ruff 통과, basedpyright 0 errors/0 warnings. 원본 artifact는 [pytest transcript](../../../../.omo/evidence/essay13/pytest.txt), [JUnit](../../../../.omo/evidence/essay13/pytest.xml), [ruff](../../../../.omo/evidence/essay13/ruff.txt), [basedpyright](../../../../.omo/evidence/essay13/basedpyright.txt)에 있다. 위 상대 링크는 저장소 루트 `.omo/evidence/essay13/`를 가리킨다.

| 완료 조건 / 시나리오 | 실제 검사 | 이진 관찰값 | artifact |
| --- | --- | --- | --- |
| 7개 기준 + 독립 모델 + 코드 우선 | `test_model_pass_cannot_override_code_failure` | 모델 pass여도 조작된 사실은 merged fail, 정상 fixture pass, SDK 호출1, strict schema, 전체 입력 동일 | `.omo/evidence/essay13/pytest.xml` |
| 없는 성과·시점·인과·주체 추가 | `test_fact_failure_when_claim_invents_achievement_time_cause_or_actor` | user_factuality fail, 정확한 claim/span, plan_or_claim | 동일 |
| 출처 없는 회사 주장·사용자/회사 근거 혼동·숨긴 사실 | `test_evidence_failure_when_provenance_is_broken` | company_factuality/expression_kind/contract_evidence fail 또는 SOURCE_TYPE 오류 | 동일 |
| 실제 문항/직무/회사 의미 실패 유지 | `test_semantic_failures_survive_when_deterministic_checks_pass` | code pass + model fail => merged fail | 동일 |
| 800/801/1000/1001 코드 포인트 | `test_length_uses_code_points_when_at_boundaries` | fail/pass/pass/fail | 동일 |
| 정보 부족과 연결 누락 분리 | `test_job_failure_distinguishes_missing_information_from_missing_connection` | missing_info+missingFields 또는 plan_or_claim+빈 missingFields | 동일 |
| 범위/버전/수정 분류 거부 | `test_invalid_or_failed_model_review_never_returns_a_pass` | 오래된 평가/범위 초과/사실 wording 오류, 반환 pass 없음 | 동일 |
| D/E 또는 I 뒤 전체 재검토 | `test_revision_evaluates_full_new_draft_and_keeps_semantic_failure` | 새 전체 입력·버전 호출2, 이전 pass 재사용 거부, 문항 fail 유지 | 동일 |
| 요청 포착 시점 유지 | `test_run_binds_captured_request_when_state_changes_during_model_call` | 모델 중 상태 요청ID 변경에도 원래 ID에 binding, 현재 ID ready 검사 FOREIGN_EVALUATION | 동일 |
| 강제 세 번째 pass 없음 | `test_third_review_is_rejected_without_forced_success` | 두 번 모두 fail, 세 번째 ExecutionBudgetError, model_calls=2 | 동일 |
| 운영 실패와 재시도0 | `test_invalid_or_failed_model_review_never_returns_a_pass` | HTTP/JSON/timeout 오류, HTTP 호출1, model_calls=1 | 동일 |

OpenAI SDK/어댑터는 실제 실행했고 HTTP 응답은 MockTransport의 통제 fixture다. 모델의 자연어 의미 판별 성능을 측정한 결과는 아니다. 합성 초안의 반복문/공백은 글자 수와 경계 검사 목적이며 사용자용 글 품질로 주장하지 않는다. 실제 작성 모듈 연결은 ESSAY-14, 전체 회귀는16, 실모델·작성자 사실성 승인은17에서 별도 검증한다.

구조 자체 검토: 각 파일은 평가 호출/결정적 증거 검사/역할별 테스트를 각각 소유한다. 외부 응답은 기존 typed provider 경계에서 파싱한다. 새 프로덕션 코드에 Any/cast/type-ignore/광범위 catch는 없다. 순수 LOC는 review 113, validator 156, 테스트 150/163/75로 모두 200 이하다. 공유 계약/상태/예산/설정은 수정하지 않았다.

## 독립 검토 후 반복 사실 범위 회귀 수정

`ReviewNode`의 wording 검사는 사실 문자열의 첫 출현만 검사하던 문제를 수정했다. 이제 사용자/회사 사실 문자열의 모든 출현(겹치는 출현 포함)을 순회한다. 뒤쪽 사실 문장을 wording으로 수정하려는 모델 응답은 `ProviderError(INVALID_RESPONSE)`로 거부한다.

- 시나리오: `test_wording_rejects_later_occurrence_of_fact_text`. 원래 사실 문장을 본문 끝에 다시 추가하고 뒤쪽 출현에만 wording 범위를 지정한다. 실제 SDK와 통제 HTTP 응답으로 실행한다.
- 수정 전 명령: `.venv/bin/python -m pytest tests/test_review_node.py::test_wording_rejects_later_occurrence_of_fact_text -q`. 관찰값: `DID NOT RAISE ProviderError`, 1 failed. artifact: `.omo/evidence/essay13/repeated-fact-before.txt`.
- 수정 후 위 전체 관련 시나리오 재실행: 62 passed. 관찰값: 뒤쪽 출현도 INVALID_RESPONSE로 거부, 모델 호출 1회. artifact: `.omo/evidence/essay13/pytest.txt`, `pytest.xml`. ruff 통과, basedpyright 0 errors/0 warnings도 최신 실행으로 갱신했다.
