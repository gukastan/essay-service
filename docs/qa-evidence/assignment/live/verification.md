# ESSAY-17 실제 실행 중간 기록

- 실행일: 2026-10-21 UTC / 기준 커밋: `e417d00b8ef30b29c39c6a95f46dcfeafb858ff4` / Jira: 진행 중.
- 실제 모델: `gpt-5.6-terra`. OpenAI SDK 3.35.1, LangGraph 1.2.16, FastMCP 4.1.1, Pydantic 2.14.1.
- 원본 입력: `tests/fixtures/live-samples.json`을 변경하지 않고 `assignment/tests/test_live_essay.py`로 실행. 실제 OpenAI 모델과 stdio MCP를 사용했고 대역은 없다. 각 JSON에는 요청, 응답, 실행시각, 역할별 관측 시간/토큰, 원본 파일 해시가 있다. 취소된 병렬 호출의 토큰과 내부 검색 페이지 수는 관측하지 못했다.
- opt-in 없이 실행한 전체 Python 회귀는 **485 passed, 8 skipped**였다. 유료 실행 파일 2개의 여덟 사례는 기본 제외다. Ruff 전체 검사·포맷 98파일·basedpyright 0오류, `docs/jira-v2.json` 구문 검사를 통과했다. 실제 유료 실행의 실패는 이 기본 회귀 통과에 포함하지 않는다.

| 원본 샘플 | 첫 실행 결과 | 시간 | 기록 |
| --- | --- | ---: | --- |
| normal-collaboration | `needs_input / COMPANY_AMBIGUOUS` | 5.136초 | [JSON](original-normal-collaboration.json) |
| normal-service | `error / INVALID_RESPONSE`; 분석 호출 후 검증 실패 추정, 세부 원인은 첫 기록에 없음 | 3.981초 | [실패 JSON](original-normal-service.json) |
| insufficient | `needs_input / EXPERIENCE_INSUFFICIENT` | 2.174초 | [JSON](original-insufficient.json) |
| long-experience | `needs_input / COMPANY_AMBIGUOUS` | 4.600초 | [JSON](original-long-experience.json) |
| invented-achievement | `needs_input / COMPANY_AMBIGUOUS` | 5.142초 | [JSON](original-invented-achievement.json) |

`normal-service`를 진단 이벤트를 추가해 같은 원본으로 한 번 더 실행했을 때는 조사 역할이 먼저 종료돼 `needs_input / COMPANY_AMBIGUOUS`가 나왔다. [재실행 JSON](original-normal-service-20261021T011605798303Z.json)을 첫 실패와 별도로 보존한다. 첫 실패를 성공으로 덮어쓰지 않는다. 가상 기업 5개에서 작성 호출과 최종 초안은 없었으므로 사실성·801~1000자·검토 품질의 통과 증거가 아니다.

원본과 별도로 `normal-collaboration`의 경험·문항을 재사용하고 명시적인 **합성 사용자 공고**(`Example Fixture Company / Service Planner`)를 넣어 전체 작성 경로도 두 번 실행했다. 이 자료는 실제 기업이나 공식 출처가 아니다. [첫 실행](original-user-posting-service-planner-20261021T011910175543Z.json)은 조사 성공·분석 성공 이후 개인 근거 원문 검증 `INVALID_EVIDENCE`로 종료했다(22.07초). [두 번째 실행](original-user-posting-service-planner-20261021T011948842279Z.json)은 조사·분석을 통과했으나 작성 모델이 30초 역할 제한에 걸려 `TIMEOUT`으로 종료했다(42.843초). 초안·평가·수정 경로는 관측되지 않았다. 이는 실제 모델 호환성/성능 문제로 남겨 두며 통제 모델의 ready 결과로 대체하지 않는다.

실제 기업 조사는 같은 키와 모델로 네이버/N배송 운영 지원의 [공식 공고](https://recruit.navercorp.com/rcrt/view.do?annoId=30005457)를 확인했다. 실제 MCP 보고 도구 1회/예약 2회, 모델 1회, 직접 확인된 공식 출처 1개와 업무 인용 4개를 기록했다. [실행 JSON](../research/checks/live-node-84d4d53a-04ff-4ac2-8f52-f1b4d56af75d.json). Anthropic/Software Engineer는 [채용 목록](https://www.anthropic.com/careers/jobs)만으로 단일 직무 근거를 확정할 수 없어 `needs_input / JOB_EVIDENCE_MISSING`이었다. 실제 MCP 예약 2회/모델 1회이며 공식 공고 성공으로 세지 않는다. [실행 JSON](../research/checks/live-node-c573a0e4-3c0d-4505-a6ff-cd89100c6ca1.json).

남은 검증은 실제 기업의 근거 있는 전체 초안과 사람의 사실성 대조, `INVALID_EVIDENCE`·작성 timeout의 원인 분석/수정과 같은 사례 재검증, Vue 실제 모델 화면 흐름, 동명 기업·접근 거부·예외 사례, 경로/버전/수정 횟수 계측이다. 작성자의 새 사실성 승인을 받기 전 ESSAY-17을 완료하지 않는다.
