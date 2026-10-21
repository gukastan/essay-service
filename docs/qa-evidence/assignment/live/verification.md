# ESSAY-17 실제 실행 중간 기록

- 실행일: 2026-10-21 UTC / 기준 커밋: `e417d00b8ef30b29c39c6a95f46dcfeafb858ff4` / Jira: 진행 중.
- 실제 모델: `gpt-5.6-terra`. OpenAI SDK 3.35.1, LangGraph 1.2.16, FastMCP 4.1.1, Pydantic 2.14.1.
- 원본 입력: `tests/fixtures/live-samples.json`을 변경하지 않고 `assignment/tests/test_live_essay.py`로 실행. 실제 OpenAI 모델과 stdio MCP를 사용했고 대역은 없다. 각 JSON에는 요청, 응답, 실행시각, 역할별 관측 시간/토큰, 원본 파일 해시가 있다. 취소된 병렬 호출의 토큰과 내부 검색 페이지 수는 관측하지 못했다.
- opt-in 없이 실행한 최신 전체 Python 회귀는 **493 passed, 8 skipped**였다. 유료 실행 파일 2개의 여덟 사례는 기본 제외다. Ruff 전체 검사·포맷·basedpyright 0오류를 통과했다. 실제 유료 실행은 별도 기록한다.

| 원본 샘플 | 첫 실행 결과 | 시간 | 기록 |
| --- | --- | ---: | --- |
| normal-collaboration | `needs_input / COMPANY_AMBIGUOUS` | 5.136초 | [JSON](original-normal-collaboration.json) |
| normal-service | `error / INVALID_RESPONSE`; 분석 호출 후 검증 실패 추정, 세부 원인은 첫 기록에 없음 | 3.981초 | [실패 JSON](original-normal-service.json) |
| insufficient | `needs_input / EXPERIENCE_INSUFFICIENT` | 2.174초 | [JSON](original-insufficient.json) |
| long-experience | `needs_input / COMPANY_AMBIGUOUS` | 4.600초 | [JSON](original-long-experience.json) |
| invented-achievement | `needs_input / COMPANY_AMBIGUOUS` | 5.142초 | [JSON](original-invented-achievement.json) |

`normal-service`를 진단 이벤트를 추가해 같은 원본으로 한 번 더 실행했을 때는 조사 역할이 먼저 종료돼 `needs_input / COMPANY_AMBIGUOUS`가 나왔다. [재실행 JSON](original-normal-service-20261021T011605798303Z.json)을 첫 실패와 별도로 보존한다. 첫 실패를 성공으로 덮어쓰지 않는다. 가상 기업 5개에서 작성 호출과 최종 초안은 없었으므로 사실성·801~1000자·검토 품질의 통과 증거가 아니다.

원본과 별도로 `normal-collaboration`의 경험·문항을 재사용하고 명시적인 **합성 사용자 공고**(`Example Fixture Company / Service Planner`)를 넣어 전체 작성 경로도 두 번 실행했다. 이 자료는 실제 기업이나 공식 출처가 아니다. [첫 실행](original-user-posting-service-planner-20261021T011910175543Z.json)은 조사 성공·분석 성공 이후 개인 근거 원문 검증 `INVALID_EVIDENCE`로 종료했다(22.07초). [두 번째 실행](original-user-posting-service-planner-20261021T011948842279Z.json)은 조사·분석을 통과했으나 작성 모델이 30초 역할 제한에 걸려 `TIMEOUT`으로 종료했다(42.843초). 초안·평가·수정 경로는 관측되지 않았다. 이는 실제 모델 호환성/성능 문제로 남겨 두며 통제 모델의 ready 결과로 대체하지 않는다.

같은 날 사용자 Chrome에서 사용한 `가상회사 새봄 / 서비스 기획` 합성 공고·문항·경험을 그대로 로컬 프록시 `POST /api/drafts`에 보내니 10.172초 후 `502 / INVALID_RESPONSE`가 재현됐다. 이어 같은 입력의 역할별 [진단 실행](original-chrome-saebom-20261021T014343245771Z.json)은 조사·분석 모델 호출 뒤 `analysis-validation / INVALID_EVIDENCE`로 종료했다. 모델이 반환한 일곱 인용문은 모두 원문에 정확히 한 번씩 존재했지만, 모델이 적은 위치는 원문의 실제 위치와 달랐다. 예를 들어 첫 문장의 반환 위치 `[0,33)`은 마침표를 제외하고, 실제 위치는 `[0,34)`이다. 마지막 문장도 반환 `[261,309)`에 비해 실제 `[269,317)`이다. 따라서 인용 내용을 새로 만들거나 완전 문장 검사를 완화할 문제가 아니라, 원문에서 코드가 인용문의 위치를 산출하도록 해야 한다. 이 진단 재실행은 앞선 Chrome 요청 자체의 내부 오류 코드를 복원한 것은 아니며, 동일 입력에서 동일 화면 문구에 이르는 실패 경로를 확인한 것이다. 작성 단계의 30초 제한 문제는 별도로 남는다.

원문 인용의 위치를 코드가 다시 찾도록 수정한 뒤, 동일 입력의 [첫 재실행](original-chrome-saebom-fixed-20261021T015105560576Z.json)에서 잘못된 위치 7개가 교정돼 분석 단계가 통과했다. 이후 작성 모델이 30.003초 제한에 걸려 `TIMEOUT`으로 종료했다. 제품 정책을 변경하지 않은 두 진단 실행에서 작성만 최대 60초로 시험했을 때는 37.684초 후 `INCOMPLETE`로 종료했고([기록](original-chrome-saebom-writer60-probe-20261021T015342719170Z.json)), `minimal` 추론 설정은 제공자가 HTTP 400으로 거부했다([기록](original-chrome-saebom-minimal-probe-20261021T015512076452Z.json)). 60초·`minimal` 시험은 제품 설정에 적용하지 않았다.

동일한 사용자 입력과 공고를 고정해 작성 응답을 주장 문장과 직무 연결 근거만 받도록 줄였다. 서버가 원문 사실 문장·주장 종류·근거 ID·본문 위치를 조립한다. 분석 인용 위치, 작성 모델의 사실 변경·ID 누락·미완성 문장, 검토 모델의 잘못된 위치를 확인해 보정했다. 검토의 사용자 제공 공고 판정도 명시했다. 첫 계획은 문항과 관련된 경험 근거를 최대 여덟 개(전체 주장 한도 내)까지 사용한다. 여러 진단 실행은 각 JSON에 실패 단계와 원인을 보존했다. 예를 들어 [수정 전 작성 검증](original-chrome-saebom-compact-writer-diagnostic-20261021T020502213292Z.json)은 `PLAN_MISMATCH`, [검토 진단](original-chrome-saebom-review-stage-20261021T021530162227Z.json)은 두 번째 검토의 `INVALID_RANGE`였으며, [분량 진단](original-chrome-saebom-source-scope-20261021T022847126411Z.json)은 사실성 통과 후 `LENGTH_VALIDATION_FAILED`였다.

최종 동일 입력 [실제 모델 실행](original-chrome-saebom-all-relevant-20261021T023007177931Z.json)은 조사 1회, 분석 1회, 작성 2회, 검토 2회로 **ready / 814자 / 수정 1회**, 총 46.918초에 완료됐다. 일곱 필수 평가 기준을 모두 통과했고, 공고 근거는 사용자 제공 합성 공고로 표시됐다. 이후 최신 백엔드를 다시 실행하고 사용자가 열어 둔 Chrome의 Vue 화면에서 같은 입력으로 `초안 만들기`를 눌러 **생성 당시 검토 통과 / 923자 초안 / 사용자 제공 공고 출처**를 확인했다([화면](saebom-browser-ready-20261021.png)). 두 실행의 초안 길이가 다른 것은 생성 결과의 차이이며 둘 다 허용 범위 안이다. 이는 실제 회사 공식 공고가 아니며, 이 결과만으로 다른 다섯 원본 샘플이나 실제 기업 사례의 통과를 주장하지 않는다.

실제 기업 조사는 같은 키와 모델로 네이버/N배송 운영 지원의 [공식 공고](https://recruit.navercorp.com/rcrt/view.do?annoId=30005457)를 확인했다. 실제 MCP 보고 도구 1회/예약 2회, 모델 1회, 직접 확인된 공식 출처 1개와 업무 인용 4개를 기록했다. [실행 JSON](../research/checks/live-node-84d4d53a-04ff-4ac2-8f52-f1b4d56af75d.json). Anthropic/Software Engineer는 [채용 목록](https://www.anthropic.com/careers/jobs)만으로 단일 직무 근거를 확정할 수 없어 `needs_input / JOB_EVIDENCE_MISSING`이었다. 실제 MCP 예약 2회/모델 1회이며 공식 공고 성공으로 세지 않는다. [실행 JSON](../research/checks/live-node-c573a0e4-3c0d-4505-a6ff-cd89100c6ca1.json).

남은 ESSAY-17 검증은 실제 기업의 근거 있는 전체 초안과 사람의 사실성 대조, 다른 원본 샘플 재검증, Vue 편집·복사 흐름, 동명 기업·접근 거부·예외 사례, 경로/버전/수정 횟수 계측이다. 작성자의 새 사실성 승인을 받기 전 ESSAY-17을 완료하지 않는다.
