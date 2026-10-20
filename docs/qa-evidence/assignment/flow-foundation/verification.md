# ESSAY-21 공통 흐름 기반 검증

- 일자: 2026-10-20. 기준 커밋: `86ea5a765fbc19e6e53f1dd15af70d5895734cf1`.
- 범위: A~J 공통 계약·요청 상태·근거/버전 검사·D/I 공통 수정 예약과 병렬 개발 문서/Jira. 실제 B~J 업무 알고리즘·전체 HTTP/Vue·글 품질 평가는 후속 티켓이다.
- 팀: native MultiAgentV2, 계약(A)·상태/수정(B)·독립 반례(C), 리더 전체 검증/문서/Jira. 같은 체크아웃에서 파일 소유권을 분리했다.

## 결과

| 확인 | 실제 관찰 | 증거 |
| --- | --- | --- |
| Python 전체 회귀 | 355 passed, 유료 opt-in 2 skipped, 21.27s, exit0 | [최종 로그](leader/python-final.txt) |
| JavaScript 기존 기반 | 12 passed, exit0 | [로그](leader/javascript.txt) |
| 전체 타입·lint·format | 0 errors/warnings/notes, Ruff 통과, 73 files already formatted | [타입](leader/types-final.txt) · [lint](leader/lint-final.txt) · [format](leader/format-final.txt) |
| 변경 Python 규칙 검사 | 17파일 위반0, exit0 | [로그](leader/discipline.txt) |
| 공개 계약·guard 직접 실행 | 유효900자/7기준 통과, 다른 요청·새 버전·동일 버전 변조 거부, 기준 누락/중복 거부 | [입력 명령](leader/manual-command.txt) · [실제 결과](leader/manual-qa.json) |
| 실제 D/I 동시 예약 | 한 경로 성공, 다른 경로 REVISION_EXHAUSTED; 잘못된 H는 소비0; 새 요청 I 성공 | 같은 수동 실행 결과 |
| 기존 조사 오류 경계 | LIMIT→BUDGET_EXCEEDED, DEADLINE→TIMEOUT, CANCELLED→CANCELLED 유지 | 같은 수동 실행 결과 및 독립 회귀 |
| 역할 간 인계 | 합성 계약·ready/보완/품질 실패 응답의 기존 wire 호환 검증 | [계약 인계](../../../FLOW_CONTRACTS.md) · tests/test_flow_handoff.py |

명령 작업 디렉터리는 assignment/다. 최종 자동 실행은 ESSAY_LIVE_RESEARCH=0, ESSAY_LIVE_COMPATIBILITY=0이며 이번 유료 호출은0회다. 계약용 합성 문장은 글 품질·기업 사실성·새 서비스 E2E 성공 증거가 아니다. 정상4회/최대6회·토큰/시간/재시도 정책과 기존 조사 코드는 보존한다.

## 발견과 수정

- 독립 반례에서 지적 위치가 명시한 주장과 겹치지 않아도 통과할 수 있었다. 실제 주장 발생 위치와의 겹침 검사를 추가했다. 길이 기준이 거짓 pass여도801~1000 밖이면 최종 guard가 차단한다. [최초 실패](members/checks/initial-failure.txt)와 재검증을 보존한다.
- 리더 통합 확인에서 수정 한도 오류를 기존 ExecutionBudgetError에 넣으면 조사 error_response의 매핑과 충돌함을 확인했다. RevisionReservationError로 분리하고 실제 기존 어댑터·런타임 경로 입력 반례를 검증했다. 중복 requirements 상태는 제거했다. [상태 담당 보고서](members/state/report.md) · [독립 검사](team/artifacts/checks-report.md).
- 리더 초기 format 검사에서 테스트4개가 실패했다. 해당 소유자가 형식만 수정한 뒤 전체 format 검사와 회귀가 통과했다. [초기 결과](leader/format-initial.txt)와 최종 결과를 함께 보존한다.
- 중간340개 회귀 통과 후 호환성 반례15개를 추가하고 최종355개를 다시 확인했다. 최종 증거만 현재 소스 해시에 대응한다.

## 범위와 후속 작업

WritingPlan·DraftEnvelope·Evaluation·종료 계약은 frozen/추가 필드 거부/크기 제한을 적용한다. 실제 LangGraph 상태 전달, 원자 예약·실패/취소/시간 초과 무환불, 요청 격리는 테스트로 확인했다. [소스 해시](source-manifest.json)와 [기존 자료 보존](preservation.json)을 기록한다.

[병렬 개발 기준](../../../PARALLEL_DEVELOPMENT.md)에 따라21 완료 후11·12·13·15를 독립 모듈로 개발할 수 있다. 실제11/12/13 모듈 연결은14,14/15 전체 회귀는16, 실제 모델·작성자 사실성 승인은17, 제출은20이다. 이 티켓들의 상태는 할 일을 유지한다. [Jira 동기화 결과](jira-completion.json).

계약/테스트 담당 세 명의 결과·중간 실패·재검증 로그는 members/와 team/artifacts/에 보존했다. 팀 기록을 archive한 뒤 임시 팀 디렉터리를 정리한 내역은 [정리 결과](cleanup.json)에 기록한다. 이 보고서는 커밋 전 구현·검증 시점의 기록이며 이후 사용자 승인에 따른 게시 여부는 Git 이력을 따른다.
