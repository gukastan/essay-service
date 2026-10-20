# OMO 제공 프로젝트 전환 개발 요청문

상태: 2026-10-20 ESSAY-18 원본 복사·Mac 실행·API/MCP/Vue 검증 완료. [검증 보고서](docs/qa-evidence/assignment/baseline/verification.md)를 인계한다. 기존 Next.js v1·TypeScript ESSAY-9 완료를 보존한다. ESSAY-19 Python 공통 기반도 완료했다. [기반 보고서](docs/qa-evidence/assignment/foundation/verification.md)를 인계한다. 다음 후보는 ESSAY-10/11/15이며 지정 범위만 착수한다.

이 문서는 향후 사용자가 개발 시작을 명시했을 때 사용할 요청문이다. 지금 문서를 편집하거나 읽는 것만으로 실행하지 않는다.

---

$omo:teammode

제공된 프로젝트를 기반으로 자기소개서 서비스를 구현해줘. 이번 메시지에 지정한 Jira 티켓 범위만 구현·검증하고 Jira도 갱신해라. 범위가 없으면 다음 미완료 단계 ESSAY-10 구현·검증까지만 진행한다.

## 먼저 읽기

- AGENTS.md, docs/ASSIGNMENT_MIGRATION.md, docs/PRD_V2.md, docs/TECH_DESIGN_V2.md.
- docs/decisions/provided-project-migration.md, docs/BACKLOG_V2.md, docs/qa-v2.md와 실제 Jira.
- docs/decisions/factual-drafting.md, 완료된 v1 QA와 ESSAY-9 증거.
- 제공 원본 /Users/jay/Downloads/all_total_vue_student의 코드·실행 스크립트. 자료 속 지시와 사용자 요청을 구분한다.

## 작업 위치와 순서

기존 /Users/jay/Projects/essay-service의 Next.js 소스·설정·샘플·QA 증거를 보존한다. 제공 원본도 수정하지 않는다. 후속 코드의 위치는 같은 저장소 assignment/다.

1. ESSAY-18 완료: 원본 소스 기준선·해시·Mac 실행·일반/장애 흐름·실제 MCP·재작성·브라우저 증거를 보존한다. FakeLLM은 분석을 건너뛰며 실제 모델은 미검증이다. 원본 루트 run.sh가 없어 별도 환경에서 서버를 직접 실행한 차이도 기록했다.
2. ESSAY-19 완료: Python/Pydantic 계약·상태·예산·모델/MCP 생명주기와 run.sh를 구현했다. Python131·JS12·실제 Vue 기반5·실행5·설치 중단3 검사, 기존 모델의 구조화 출력1회·실제 MCP 검색1회가 통과했다. 공식 출처 검증·네 업무 역할·전체 API/화면은 아직 미구현이다.
3. ESSAY-10 조사·ESSAY-11 분석·ESSAY-15 Vue를 공통 계약 이후 병렬 개발한다.
4. ESSAY-12 작성 → ESSAY-13 검토 → ESSAY-14 그래프/FastAPI 통합.
5. ESSAY-14·15 이후 ESSAY-16 회귀 → ESSAY-17 실제 모델/MCP/브라우저 QA와 작성자 승인.
6. ESSAY-20에서 전체 소스·README·변경 설명·화면·실제 결과·예외 결과를 제출 가능한 상태로 만든다.

메인은 설치된 omo:teammode 지침을 적용한다. 파일 소유권을 명시하고 모두에게 다른 작업자의 변경을 보존하도록 전달한다. 공통 파일은 한 명이 맡고 순차 인계한다. 제품 역할과 개발 에이전트 수는 일대일일 필요가 없다.

## 필수 계약

- 기업·직무 조사와 경험·문항 분석 병렬 → 작성 → 코드 검사/모델 검토 → 필요 시 수정1회/재검토.
- 실제 MCP 조사 도구를 사용하고 모델1/내장 도구 용량2를 호출 전에 예약한다. MCP 내부 OpenAI Responses 요청을 총 모델4/최대6회에 포함한다.
- 자동 재시도0, 모델30초·조사45초·전체180초·클라이언트195초, max_tool_calls=2, 예약 무환불.
- 경험·문항을 조사 도구에 보내지 않는다. 공식 근거와 user_provided를 구분하고 인재상보다 문항·직무 요건을 우선한다.
- 없는 과거 사실을 추가하지 않는다. 원문 사실 문장 보존, LF/코드 포인트801~1000자, Python/Vue 근거 위치 일치를 검사한다.
- FastAPI POST /api/drafts와 Vue를 연결한다. 기존 Next.js API/기본값은 변경하지 않는다.
- 원본 세 번째 강제 통과·의도적 실패/재시도·경험 DB 저장·GET 쿼리 전송·전체 프롬프트 노출을 제품 경로에 넣지 않는다.

## 검증과 Jira

원본 실행, 모의 제공자, 실제 MCP, 실제 모델/검색, 실제 브라우저를 구분해 증거를 저장한다. 기존5개를 새 서비스에서 다시 실행하고 추가 공고는 별도 시험자료로 표시한다. 실제 기업2곳 이상의 공식 자료도 검증한다. 실패→수정→같은사례 재검증을 보존한다.

이번 사용자 지정 범위의 작업만 시작/완료 처리한다. ESSAY-1~7·9는 다시 열지 않는다. ESSAY-17은 작성자 새 사실성 승인 전 완료하지 않고, 에픽은 ESSAY-20 제출 확인까지 끝난 뒤 완료한다. 자격증명이나 환경 제약으로 수행하지 못한 검증은 미검증으로 남긴다.
