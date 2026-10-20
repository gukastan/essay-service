# 제공 프로젝트 기반 전환 계획

- 결정일: 2026-10-20
- 상태: ESSAY-18 원본 실행과 ESSAY-19 Python 공통 기반 검증 완료. 업무 역할·전체 API·Vue 제품 기능과 신규 서비스 QA는 후속 작업.
- 원본: `/Users/jay/Downloads/all_total_vue_student/`
- 저장소: `/Users/jay/Projects/essay-service/`
- 전환 코드 위치: `assignment/` (ESSAY-18 복사 기준선에 ESSAY-19 공통 기반 구현. Downloads 원본은 불변)
- 보존 기준 커밋: `c5299e954d0ff1b0848dad238e7b731ef078bb51`
- [PRD](PRD_V2.md) · [기술 설계](TECH_DESIGN_V2.md) · [백로그](BACKLOG_V2.md) · [QA](qa-v2.md) · [결정](decisions/provided-project-migration.md)

## 과제와 사용자 결정

과제는 기존 AI Agent의 기술 구조를 활용해 서버 장애 진단과 다른 목적·기능을 가진 AI 서비스를 만드는 것이다. 제공된 LangGraph·MCP·LLM·Vue·FastAPI 구조를 활용하며 모든 파일을 수정할 필요는 없다. 순서는 원본 실행 확인 → 서비스 목적·기능 및 재사용/변경 대상 정의 → 구현·검증이다.

사용자는 기존 작업 보존과 제공 프로젝트 기반 전환을 승인한 뒤 ESSAY-18 원본 실행 검증을 요청했다. 모의 LLM·JSON 자료를 사용하는 실제 API·MCP·Vue 실행 증거는 [기준선 보고서](qa-evidence/assignment/baseline/verification.md)에 있다. 실제 모델이나 새 자기소개서 서비스 검증을 수행했다는 뜻은 아니다.

## 보존 경계

- 현재 루트 Next.js v1과 TypeScript ESSAY-9 코드·의존성·테스트는 유지한다. ESSAY-1~7 및 ESSAY-9를 다시 열거나 Python 구현 완료로 바꾸지 않는다.
- 기존 5개 샘플, v1 QA, run-7 작성자 승인, ESSAY-9 증거는 수정하거나 전환판 증거로 재분류하지 않는다.
- 현재 문서는 새 방향의 실행 명세다. 이전 문서는 [기준선 목록](archive/nextjs-v2/README.md)의 커밋 고정 링크와 기존 결정 기록에서 확인한다.
- 제공된 Downloads 원본은 읽기 전용 기준으로 보존한다. 소스만 `assignment/`로 복사하며 .env, .venv, session.db, 캐시·실행 로그를 가져오지 않는다.
- `assignment/`는 별도 Python 환경·포트·설정으로 실행한다. 루트 Node 설치·v1 실행 방법을 대체하지 않는다. 제출 시에는 필요한 시험자료까지 포함해 assignment/만으로 실행 가능한 패키지를 만든다.
- 원본의 코드 재사용, 기존 essay의 설계/규칙 이식, 새 구현을 구분한다. 이전 Next.js 코드가 제공 프로젝트에서 파생됐다고 주장하지 않는다.

## 원본 → 전환 대응

원본 파일은 assignment/에 복사됐다. 아래 대응 중 ESSAY-19 공통 계약·모델/MCP·lifespan·실행 진입점은 구현됐다. 업무 역할·전체 그래프/API·Vue 제품 화면은 후속 계획이다. 경로는 assignment/ 기준이다.

| 원본 | 유지할 구조 | 목적에 맞는 변경 | 소유 작업 |
| --- | --- | --- | --- |
| server.py | FastAPI 요청·lifespan·그래프 실행 | POST /api/drafts, 입력/오류 규격, 요청별 예산 | ESSAY-19, ESSAY-14 순차 |
| agent/graph.py | StateGraph·조건 분기·작성/검증 루프 | 조사/분석 병렬 합류·4역할·수정1회 | ESSAY-14 |
| agent/deps.py | 의존성 주입 | 타입 있는 모델·MCP·설정, 요청 상태 분리 | ESSAY-19 |
| agent/mcp_client.py, mcp_server.py | 실제 MCP stdio 연결·도구 호출 | research_company_role 기업·직무 조사 | ESSAY-19, ESSAY-10 순차 |
| agent/openai_llm.py | 모델 연결 경계 | 구조화 출력·Responses 검색·예산·재시도0 | ESSAY-19 |
| graph.py의 업무 노드 | 단계별 책임 분리 | agent/nodes/research.py·analyze.py·write.py·review.py | ESSAY-10~13 |
| validate_node | 검증 후 재작성 분기 | validate_evidence.py 근거·길이 검사, 실패 강제 통과 제거 | ESSAY-13 |
| web_chat.html | Vue 화면과 요청 상태 | 네 입력·근거·원문 비교·편집·복사·보완 | ESSAY-15 |
| web_demo_server.py | 화면 제공·동일 출처 프록시 | POST JSON 프록시·유한 timeout·오류 보존 | ESSAY-15 |
| data/runbooks/, mcp_server_docs.py | 자료/도구와 업무 로직의 분리 개념 | 장애 매뉴얼·decoy 서버는 제출 서비스에서 제외, 이유 기록 | ESSAY-10 |
| agent/session_store.py, GET /chat/stream | 원본 실행 확인용 기준 | 경험 저장·쿼리문자열 전송·전체 프롬프트 노출은 제출 경로에서 제외 | ESSAY-19, ESSAY-14 |

원본의 fake 응답·JSON 모니터링·의도적 첫 실패·세 번째 검증 강제 통과는 교육 시나리오다. 원본 관찰 시 그 성격을 기록하고 새 서비스의 실제 검색·사실성 검증으로 보고하지 않는다.

## 기존 essay 자산의 이식

- PRD의 네 입력·801~1000자·편집/복사·보완 흐름을 유지한다.
- factual-drafting의 원문 사실 문장 보존과 회사 사실/현재 해석/미래 계획 구분을 유지한다.
- ESSAY-9의 계약·예산·제공자 경계는 Python/Pydantic으로 이식하고 다시 검사한다.
- Python/JavaScript 사이의 근거 위치는 LF 정규화 후 Unicode 코드 포인트로 새로 통일한다. 기존 UTF-16 offset을 그대로 사용하지 않는다.
- OpenAI 키와 내장 검색 선택은 유지한다. MCP 조사 도구 내부의 모델 요청도 정상4회/최대6회에 포함하며 검색 요약용 모델을 추가하지 않는다.
- 루트 Next.js에 /api/v2/drafts·DRAFT_PIPELINE_VERSION을 추가하던 계획은 대체됐다. 별도 assignment 서비스로 전환하므로 기존 v1 기본값을 바꾸지 않는다.

## 실행 순서

1. [ESSAY-18](https://kmskojb.atlassian.net/browse/ESSAY-18) 완료: 원본 소스 확보·기준선 기록·Mac 실행 관찰. [검증 보고서](qa-evidence/assignment/baseline/verification.md).
2. [ESSAY-19](https://kmskojb.atlassian.net/browse/ESSAY-19) 완료: Python 계약·예산·MCP/모델 연결·실행 진입점 이식. [기반 검증 보고서](qa-evidence/assignment/foundation/verification.md).
3. ESSAY-10 조사 / ESSAY-11 분석 / ESSAY-15 Vue 화면을 공통 계약 이후 병렬 개발 가능.
4. ESSAY-12 작성 → ESSAY-13 검토 → ESSAY-14 그래프·FastAPI 통합.
5. ESSAY-14·15 이후 ESSAY-16 전체 회귀 → ESSAY-17 실제 모델·MCP·브라우저 QA와 작성자 사실성 승인.
6. [ESSAY-20](https://kmskojb.atlassian.net/browse/ESSAY-20): 제출 소스·README·변경 설명·검증 증거 완성. 모든 필수 작업과 승인 후 ESSAY-8 완료.

기존 ESSAY-9→10/11/15 연결은 완료된 설계 기준선 이력으로 유지한다. 실제 구현 시작에는 ESSAY-19가 추가 필수 선행이다. 공통 server.py·MCP 연결 수정은 소유권을 순차 인계한다.

## 제출물과 검증

| 과제 제출 항목 | 예정 산출물 | 완료 판단 |
| --- | --- | --- |
| 전체 소스코드 | assignment/의 실행 소스·의존성 잠금·빈 환경설정 예시·필요 fixture | 독립 설치·실행, 비밀/DB/가상환경 제외 |
| README.md | assignment/README.md | Mac 설치·API 키 변수·bash run.sh·종료·테스트·시연을 실제 확인 |
| 주요 변경 파일·기능 | assignment/docs/changes.md | 원본→신규 파일, 유지/변경 이유, 검증 링크 |
| 서비스 화면 | docs/qa-evidence/assignment/browser/ 및 제출본에 복사한 이미지 | 입력·결과·근거·편집·보완·오류의 실제 화면 |
| 기능별 입력과 실제 결과 | assignment/docs/verification.md 및 원본 결과 파일 | 기존5개 재실행·별도 실제기업 사례, 기대/실제/판정/시각 |
| 오류·예외 결과 | 같은 검증 보고서의 예외 표 | 입력·키·검색·MCP·모델·시간·근거·길이 실패와 처리 결과 |

기존 승인 결과는 새 구현 통과 증거가 아니다. 모의 제공자, 실제 MCP 프로토콜, 실제 OpenAI/검색, 실제 브라우저의 검증 범위를 각각 표시한다. 미실행·차단 항목은 통과로 처리하지 않는다.

## 원본 실행 안내의 차이

2026-10-20 확인 결과 루트 run.sh와 .env.example은 없고 sh/run_agent_openai.sh, sh/run_agent_ollma.sh, sh/run_frontend.sh가 있었다. 기존 스크립트는 포트 점유 프로세스 강제 종료·DB 삭제·.env 로딩을 포함하므로 그대로 실행하지 않았다. ESSAY-18에서는 새 Python 3.11.15 환경과 비어 있는 환경변수를 사용해 원본 API/UI를 localhost로 직접 실행했다. 설치·시작 명령과 차이는 [실행 기록](qa-evidence/assignment/baseline/source-runtime/README.md)에 있다. ESSAY-19에서 제출 서비스용 bash run.sh 진입점을 만든다.

## ESSAY-18 인계

46개 원본 파일을 복사했고 실행 소스는 바꾸지 않았다. 복사본의 .gitignore만 환경·DB·캐시·로그 제외를 보강했다. API/SSE 25개, 실제 MCP 8개, 브라우저 5개, 실행 환경 점검 13개가 통과했다. 기존 Next.js 코드·샘플·QA는 해시로 보존 여부를 확인했으며 이번에 기존 Node 테스트를 다시 실행하지 않았다.

모의 분석 skip, 의도적 첫 timeout, 길이/형식 검토, 세 번째 강제 통과 코드, fake를 실모델로 부르는 화면 문구와 반려 초안 표시를 구분해 기록했다. 기존 Python 패키지 조합이 원본을 실행했다는 사실만 확인했으며 구조화 출력·검색 호환성은 ESSAY-19에서 별도로 검증한다.

## ESSAY-19 인계

Python 공통 기반은 구현·검증을 완료했다. 위 ESSAY-18 기록은 당시 원본 관찰이며 이후의 구현 결과는 [기반 보고서](qa-evidence/assignment/foundation/verification.md)와 [assignment 실행 안내](../assignment/README.md)를 따른다. 현재 run.sh는 고정 설치 후 localhost 서버를 실행하고 자기 소유 프로세스만 정리한다. 모델/MCP 의존성·계약·예산·문자 경계는 구현됐고 기본 서버는 health만 제공한다. 공식 출처 검증·네 업무 역할·전체 API·새 Vue 제품 화면은 ESSAY-10~15의 후속 범위다. 공통 API/파일 소유권은 기반 보고서의 인계 문서를 읽고 순차 전달한다.
