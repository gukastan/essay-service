# v2 전환 구현 백로그

- 갱신일: 2026-10-20 / 상태: ESSAY-18 완료, ESSAY-19 Python 공통 기반 구현·검증 완료
- 기존 ESSAY-1~7 및 ESSAY-9는 완료 상태로 보존한다. ESSAY-8은 진행 중이다.
- ESSAY-10~17은 Python·MCP·Vue 기준으로 변경하고 ESSAY-18~20을 추가한다. 미착수 구현/검증/제출 티켓은 할 일이다.
- [전환 계획](ASSIGNMENT_MIGRATION.md) · [PRD](PRD_V2.md) · [기술 설계](TECH_DESIGN_V2.md) · [QA](qa-v2.md)
- [이전 문서 기준선](archive/nextjs-v2/README.md) · [Jira 동기화 기록](jira-v2.json)

## 순서와 소유권

ESSAY-18 → ESSAY-19 → (ESSAY-10 조사 ∥ ESSAY-11 분석 ∥ ESSAY-15 Vue) → ESSAY-12 작성 → ESSAY-13 검토 → ESSAY-14 그래프/FastAPI → ESSAY-16 회귀 → ESSAY-17 실제 QA/작성자 승인 → ESSAY-20 제출 자료.

ESSAY-16은 ESSAY-14·15 모두를 선행으로 한다. ESSAY-19는 ESSAY-18과 완료된 ESSAY-9를 따른다. 기존 ESSAY-9→10/11/15 연결도 보존하지만 Python 구현 착수에는 ESSAY-19가 추가 필수다.

공통 계약·의존성·server.py/MCP 기반은 ESSAY-19 담당자가 먼저 소유하고 ESSAY-10/14 담당자에게 순차 인계한다. 역할별 노드와 해당 단위 테스트는 각 역할 담당자, 화면/프록시는 ESSAY-15, 통합 증거는 QA 담당자가 맡는다. 다른 사람의 변경을 되돌리지 않는다.

| ID | Jira | 작업 | 선행 |
| --- | --- | --- | --- |
| MIG-01 | [ESSAY-18](https://kmskojb.atlassian.net/browse/ESSAY-18) | 제공 프로젝트 기준선 보존과 Mac 원본 실행 확인 | 없음 |
| MIG-02 | [ESSAY-19](https://kmskojb.atlassian.net/browse/ESSAY-19) | Python 공통 계약·예산·MCP 실행 기반 이식 | ESSAY-18, ESSAY-9 |
| V2-01 | [ESSAY-9](https://kmskojb.atlassian.net/browse/ESSAY-9) | 공통 계약·LangGraph 실행 기반 구성 (완료된 TypeScript 기준선) | 없음 |
| V2-02 | [ESSAY-10](https://kmskojb.atlassian.net/browse/ESSAY-10) | MCP 기업·직무 조사와 공식 출처 검증 구현 | ESSAY-9, ESSAY-19 |
| V2-03 | [ESSAY-11](https://kmskojb.atlassian.net/browse/ESSAY-11) | Python 경험·문항 분석과 원문 근거 추출 구현 | ESSAY-9, ESSAY-19 |
| V2-04 | [ESSAY-12](https://kmskojb.atlassian.net/browse/ESSAY-12) | Python 근거 기반 초안 작성 역할 구현 | ESSAY-10, ESSAY-11 |
| V2-05 | [ESSAY-13](https://kmskojb.atlassian.net/browse/ESSAY-13) | Python 근거 검사·사실성 검토와 제한된 수정 구현 | ESSAY-12 |
| V2-06 | [ESSAY-14](https://kmskojb.atlassian.net/browse/ESSAY-14) | Python LangGraph 네 역할과 FastAPI 통합 | ESSAY-13 |
| V2-07 | [ESSAY-15](https://kmskojb.atlassian.net/browse/ESSAY-15) | Vue 자기소개서 입력·근거·편집·보완 화면 구현 | ESSAY-9, ESSAY-19 |
| V2-08 | [ESSAY-16](https://kmskojb.atlassian.net/browse/ESSAY-16) | Python·MCP·Vue 전체 흐름과 예외 회귀 검증 | ESSAY-14, ESSAY-15 |
| V2-09 | [ESSAY-17](https://kmskojb.atlassian.net/browse/ESSAY-17) | 전환 서비스 실제 모델·MCP·Vue QA와 사실성 승인 | ESSAY-16 |
| MIG-03 | [ESSAY-20](https://kmskojb.atlassian.net/browse/ESSAY-20) | 과제 제출 소스·README·변경 설명·검증 자료 완성 | ESSAY-17 |

## 완료된 기준선

### V2-01 공통 계약·LangGraph 실행 기반 구성

Jira: [ESSAY-9](https://kmskojb.atlassian.net/browse/ESSAY-9)

- 유형: 작업
- 요구사항: V2-R1, V2-R6
- 선행: 없음
- 소유 범위: package.json·pnpm-lock.yaml, src/shared/contracts-v2.ts, src/server/workflow/state.ts·budget.ts·providers.ts·native-provider.ts·provider-schemas.ts 및 해당 테스트

기존 /api/drafts를 유지하면서 /api/v2/drafts의 입력·출력, 네 역할의 상태와 근거 ID, 공통 실행 예산을 정의한다. LangGraph JS와 현재 Next.js/Node/OpenAI 조합의 호환성을 확인하고 버전을 고정한다. 검색·페이지 읽기는 교체 가능한 서버 어댑터로 정의하며 실제 제공자/자격증명/지원 모델을 작은 실연결 검사로 확정해 ADR에 기록한다.

완료 조건:

- [x] 필수 4개 입력과 선택 공고 URL·본문, ready/needs_input/error 계약을 런타임 스키마로 검증한다.
- [x] 모델 호출 최대 6회, 자동 재시도 0, 호출당 최대 30초, 요청 180초 및 조사 전체 45초 예산을 공유한다. 병렬 실행에서도 원자적으로 차감한다.
- [x] 사용자 승인에 따라 기본 내장 도구 호출 최대 2회로 변경했다. 모델1/내장 도구 용량2 원자 예약·취소·무환불·추가 호출 차단을 검사하고 실제 서버의 `max_tool_calls=2` 반영을 확인했다. 별도 주입 검색2/직접 읽기3 제한도 개별 검사했다.
- [x] v1 API·기존 테스트는 유지된다. 모델/검색 제공자 지원 여부와 필요한 환경변수 이름만 기록하고 키는 노출하지 않는다.

제공자 내부 검색어·페이지 수·바이트는 독립 통제하지 않는다. `nativeToolCallsReserved`는 용량 예약이며 실제 보고 도구 수와 구분한다. 구현 상세와 작은 실연결 4회의 증거는 [ADR](decisions/langgraph-v2.md), 전체 확인 결과는 [QA 기록](qa-v2.md)에 있다.


위 완료 기록은 TypeScript 구현의 역사다. Python 이식 완료를 뜻하지 않으며 ESSAY-19에서 별도로 검증한다.

## 현재 작업 계약

assignment/에는 ESSAY-18 기준선 위에 ESSAY-19 공통 기반이 구현됐다. 아래 업무 역할·전체 그래프/API·화면 기능은 후속 계획이며 사용자 지정 범위만 착수한다.

### MIG-01 제공 프로젝트 기준선 보존과 Mac 원본 실행 확인

Jira: [ESSAY-18](https://kmskojb.atlassian.net/browse/ESSAY-18) / 유형: 작업 / 상태: 완료

- 선행: 없음
- 소유 범위: assignment/ 초기 복사본, docs/qa-evidence/assignment/baseline/, docs/ASSIGNMENT_MIGRATION.md

제공된 all_total_vue_student를 실제 출발점으로 확보하고, 기능 변경 전 원본 AI Agent의 실행과 처리 흐름을 확인한다. 기존 Next.js v1·ESSAY-9 코드와 검증 기록은 보존한다.

완료 조건:

- [x] 기준 커밋 c5299e954d0ff1b0848dad238e7b731ef078bb51 및 기존 src/·tests/·QA 증거가 보존됨을 기록했다. 원본 Downloads 폴더는 수정하지 않았다.
- [x] 제공 프로젝트의 소스 46개를 assignment/에 복사하고 원본 경로·파일별 해시·제외 목록을 기록했다. .env·.venv·session.db·캐시·기존 실행 로그는 복사하지 않았고 런타임 파일은 제외한다.
- [x] 별도 Mac 가상환경과 패키지 설치로 원본을 실행하고 Python/패키지 버전·명령·상태 코드·화면을 기록했다. run.sh 누락과 제공 sh/ 스크립트의 실행 방식 차이를 기록했다.
- [x] 일반 대화와 장애 문의의 경로·실제 MCP·재작성 루프를 관찰했다. analysis 노드는 FakeLLM 정책에 따라 AnalysisSkipped였으며 LLM·JSON 자료는 모의다.
- [x] 실행 소스 수정 없이 원본 실행을 검증했다. 공개 증거에 실제 키나 실행 시 전체 프롬프트를 저장하지 않았다.

실행 환경 13개·API/SSE 25개·MCP 8개·브라우저 5개 점검 통과. 명령·결과·한계·해시·화면은 [기준선 검증 보고서](qa-evidence/assignment/baseline/verification.md)에 있다. 실제 모델 호출과 ESSAY-19 이식은 미실행이다.

### MIG-02 Python 공통 계약·예산·MCP 실행 기반 이식

Jira: [ESSAY-19](https://kmskojb.atlassian.net/browse/ESSAY-19) / 유형: 작업 / 상태: 완료

- 선행: [ESSAY-18](https://kmskojb.atlassian.net/browse/ESSAY-18), [ESSAY-9](https://kmskojb.atlassian.net/browse/ESSAY-9)
- 소유 범위: assignment/agent/{contracts,state,budget,providers}.py, agent/deps.py, agent/mcp_client.py, agent/openai_llm.py, server.py의 lifespan, requirements.txt·잠금 파일·.env.example·run.sh, 기반 테스트

ESSAY-9의 TypeScript 계약과 제한 정책을 제공된 Python/FastAPI/LangGraph/MCP 구조에 이식한다. 완료된 ESSAY-9를 다시 열거나 Python 구현 완료로 재해석하지 않는다.

완료 조건:

- [x] Pydantic 입력·출력/근거 계약, 요청별 LangGraph 상태와 예산을 구현하고 Python 의존성 버전을 실제 호환 검사 후 고정한다. 네 필수 입력·선택 공고 자료·ready/needs_input/error를 검증한다.
- [x] 서버 lifespan에서 재사용 가능한 모델/MCP 연결을 생성·정리하고 노드에는 타입 있는 의존성을 주입한다. 입력·deadline·호출 예산은 요청마다 새로 만들며 SQLite 경험/초안 저장과 외부 추적 전송은 기본 비활성화한다.
- [x] 정상 4회·최대 6회, 회당 30초·조사 45초·전체 180초·클라이언트 195초·자동 재시도 0을 검사한다. 병렬 요청 및 취소 후에도 추가 호출을 차단하며 원본의 의도적 첫 실패·재시도는 제품 경로에서 비활성화한다.
- [x] 조사 노드가 MCP research_company_role을 호출하기 전에 모델1/내장 도구 용량2를 원자 예약하고 trusted timeout 한도를 전달한다. MCP 서버는 OpenAI Responses 1회에 max_tool_calls=2·store:false·재시도0을 적용한다. 조사 후 별도 요약 LLM을 호출하지 않으며 예약은 오류·취소 후에도 환급하지 않는다.
- [x] MCP 입력은 기업·직무·선택 공고 자료만 허용하고 경험·문항을 제거한다. 실제 도구 보고량과 예약량을 구분하며 내부 검색어·페이지 수 통제를 주장하지 않는다. 프로토콜 오류·단절·취소·동시성 격리를 검증한다.
- [x] 글자 수와 근거 offset은 LF 정규화 후 Unicode 코드 포인트로 통일한다. Python과 Vue가 한글·CRLF·이모지 fixture에서 일치하고 UTF-16 기반 ESSAY-9 offset을 그대로 해석하지 않는다.
- [x] OpenAI 키는 로컬 서버 설정으로만 주입한다. 기존 키/모델의 Python 구조화 출력·내장 검색 호환성은 별도 opt-in 작은 실연결로 확인하고 결과를 기록한다. 모의 검사만 수행한 경우 실연결을 통과로 보고하지 않는다.
- [x] assignment/에서 bash run.sh로 실행·종료할 수 있는 진입점과 빈 값의 .env.example을 제공한다. README 명령은 깨끗한 설치 환경에서 확인한다.

Python131·JS12·실제 Vue 기반5·실행5·설치 중단3 검사와 기존 모델의 구조화 출력1회·실제 MCP 검색1회 통과. 세부 증거와 제한은 [기반 보고서](qa-evidence/assignment/foundation/verification.md)를 따른다. 네 업무 역할과 전체 API/화면은 후속 작업이다.

### V2-02 MCP 기업·직무 조사와 공식 출처 검증 구현

Jira: [ESSAY-10](https://kmskojb.atlassian.net/browse/ESSAY-10) / 유형: 작업 / 상태: 할 일

- 선행: [ESSAY-9](https://kmskojb.atlassian.net/browse/ESSAY-9), [ESSAY-19](https://kmskojb.atlassian.net/browse/ESSAY-19)
- 소유 범위: assignment/agent/nodes/research.py, assignment/mcp_server.py, assignment/agent/research/, 해당 테스트

원본 모니터링/장애 매뉴얼 조회를 기업·채용 정보 조사로 바꾸고, 실제 MCP를 통해 회사와 직무 근거를 얻는다.

완료 조건:

- [ ] 원본 agent/mcp_client.py와 MCP 서버 등록 구조를 활용해 research_company_role 도구를 실제 호출한다. 사용되지 않는 장애 진단·decoy docs 서버는 제품 실행에서 제외하고 변경 이유를 기록한다.
- [ ] 현재 OpenAI 키와 내장 검색을 유지한다. 조사 모델은 MCP 서버 안의 Responses 1회이며 그래프에서 추가 조사/요약 모델을 호출하지 않는다. 모델1/도구2 선예약·30/45초 제한을 지킨다.
- [ ] 기업 식별·공식 채용 도메인/공식 링크 관계·출처 구절을 확인한다. 후보 자료는 unverified이며 검색 요약만으로 official로 승격하지 않는다. sourceId·URL 또는 사용자 본문 표시·확인 시각·근거 구절을 저장한다.
- [ ] 사용자 공고는 user_provided로 구분하고 문항·직무 요구를 인재상보다 우선한다. 인재상만 없으면 생략, 회사 식별/직무 근거 부족은 needs_input, 제공자 장애·잘못된 응답은 error로 종료한다.
- [ ] 동명 기업·상충 자료·지시문 삽입·빈 자료·접근 거부를 시험한다. 경험·문항은 MCP 조사 입력이나 외부 검색에 포함하지 않는다.
- [ ] 공식 페이지 직접 확인이 필요하면 HTTP(S)만 허용하고 DNS/IP/모든 리다이렉트에서 내부망을 차단한다. 직접 읽기3회·페이지1MiB·정리 텍스트12000 코드 포인트 제한을 적용한다. hosted 내부 페이지 수/바이트와 혼동하지 않는다.

### V2-03 Python 경험·문항 분석과 원문 근거 추출 구현

Jira: [ESSAY-11](https://kmskojb.atlassian.net/browse/ESSAY-11) / 유형: 작업 / 상태: 할 일

- 선행: [ESSAY-9](https://kmskojb.atlassian.net/browse/ESSAY-9), [ESSAY-19](https://kmskojb.atlassian.net/browse/ESSAY-19)
- 소유 범위: assignment/agent/nodes/analyze.py 및 해당 테스트

문항 요구와 경험의 사실을 추출하는 독립 노드를 구현한다. 기업 조사와 병렬 실행하며 외부 자료로 개인 경험을 보충하지 않는다.

완료 조건:

- [ ] questionRequirements·experienceEvidence·gaps를 구조화 출력으로 반환하고 각 경험 근거에 ID·원문 구절·코드 포인트 start/end를 연결한다.
- [ ] LF 정규화한 경험의 원문 구절과 위치를 서버에서 대조한다. 없는 역할·행동·결과·수치·시점·인과관계·과거 심리 변화를 추가하지 않는다.
- [ ] 경험 부족 시 구체적 보완 항목과 질문을 반환해 작성 호출 전에 종료할 수 있다.
- [ ] 긴 경험·불완전한 경험·허위 성과 요구·입력 내 지시문·CRLF/이모지 인용을 시험한다. 모델은 최대1회이고 조사 도구를 호출하지 않는다.

### V2-04 Python 근거 기반 초안 작성 역할 구현

Jira: [ESSAY-12](https://kmskojb.atlassian.net/browse/ESSAY-12) / 유형: 작업 / 상태: 할 일

- 선행: [ESSAY-10](https://kmskojb.atlassian.net/browse/ESSAY-10), [ESSAY-11](https://kmskojb.atlassian.net/browse/ESSAY-11)
- 소유 범위: assignment/agent/nodes/write.py 및 해당 테스트

검증된 기업·직무 근거와 경험 분석을 합쳐 자기소개서 문항에 답한다. 기존 factual-drafting 결정의 사실 보존 원칙을 이식한다.

완료 조건:

- [ ] 작성 입력에 원래 문항·검증된 두 결과·원문을 포함한다. 기업 사실과 개인 사실의 근거를 분리하고 claimMap·fitReasons를 반환한다.
- [ ] 과거 사실은 원문의 완전한 문장을 선택해 표현·순서를 보존한다. 새 문장은 별도 현재 해석·미래 계획으로 구분하며 없는 근거 ID·수치·성과를 만들지 않는다.
- [ ] 직무 요구를 일반 인재상보다 우선하고 인재상 자료가 없을 때 임의 생성하지 않는다.
- [ ] 서버가 계산한 길이·검토 지적을 받아 같은 작성 역할로 한 번만 수정한다. 문자열 자르기·패딩으로 801~1000자를 맞추지 않는다.
- [ ] 허위 성과 유도·회사 사실의 개인 성과 전용·수정 중 사실 추가 사례를 단위 테스트한다.

### V2-05 Python 근거 검사·사실성 검토와 제한된 수정 구현

Jira: [ESSAY-13](https://kmskojb.atlassian.net/browse/ESSAY-13) / 유형: 작업 / 상태: 할 일

- 선행: [ESSAY-12](https://kmskojb.atlassian.net/browse/ESSAY-12)
- 소유 범위: assignment/agent/nodes/review.py, assignment/agent/validate_evidence.py 및 해당 테스트

원본의 단순 형식 검사와 반복 후 강제 통과를 자기소개서용 근거 검사·독립 모델 검토로 교체한다.

완료 조건:

- [ ] 근거 ID 존재·원문 인용·초안 구절·Unicode 길이를 코드로 검사하고 검토 모델은 pass/revise/needs_input, issues, revisionInstructions를 반환한다.
- [ ] 없는 성과·시점 추가·출처 없는 회사 주장·회사/사용자 사실 혼동·문항 미응답 반례를 검출한다. 모델 pass가 코드 검사 실패를 덮을 수 없다.
- [ ] 사실성·문항·분량 문제는 같은 수정1회 예산을 공유하고 수정 후 재검토 실패는 needs_input 또는 QUALITY_CHECK_FAILED로 끝낸다.
- [ ] 원본의 세 번째 시도 강제 통과를 사용하지 않는다. 검토 미완료/실패 초안을 ready로 반환하지 않는다.
- [ ] 검토 통과를 사실성의 증명이나 합격 보장으로 표현하지 않는다.

### V2-06 Python LangGraph 네 역할과 FastAPI 통합

Jira: [ESSAY-14](https://kmskojb.atlassian.net/browse/ESSAY-14) / 유형: 작업 / 상태: 할 일

- 선행: [ESSAY-13](https://kmskojb.atlassian.net/browse/ESSAY-13)
- 소유 범위: assignment/agent/graph.py, assignment/server.py의 POST /api/drafts, 통합 테스트

원본 build_graph/deps/FastAPI 생명주기 구조를 활용해 조사·분석 병렬→합류→작성→검토→최대1회 수정 흐름을 구현한다.

완료 조건:

- [ ] 실제 Python StateGraph가 두 분기를 한 번만 합류하고 정상4회·수정최대6회로 종료한다. 조사/분석 보완·실패 시 작성하지 않고 가능한 진행 작업을 취소한다.
- [ ] 요청별 상태·예산·MCP 응답을 격리하고 숨은 SDK/도구/그래프 재시도 및 중복 실행을 차단한다. MCP 조사를 전체 모델/시간 예산에 포함한다.
- [ ] FastAPI POST /api/drafts가 ready/needs_input 200, INVALID_INPUT400, 품질실패422, CONFIG_ERROR500, 제공자오류502, timeout504를 반환한다. FastAPI 기본 입력 오류422는 공통 입력 계약400으로 정규화한다.
- [ ] 모든 ready는 근거 검사·모델 검토·801~1000자를 통과한다. 오류 응답은 requestId·code·message만 포함하고 초안·원문·키·전체 프롬프트를 노출하지 않는다.
- [ ] 원본 GET /chat/stream에 경험을 싣지 않으며 제출 서비스는 POST JSON으로 처리한다. 원본 대화 이력 SQLite 저장/전체 프롬프트 반환/외부 tracing을 제품 경로에서 사용하지 않는다.
- [ ] Next.js 루트는 별도로 실행되는 보존본이다. Next.js /api/v2/drafts·DRAFT_PIPELINE_VERSION 추가는 취소된 계획이며 assignment 서버와 포트를 분리하고 180초 요청 지원을 실제 확인한다.

### V2-07 Vue 자기소개서 입력·근거·편집·보완 화면 구현

Jira: [ESSAY-15](https://kmskojb.atlassian.net/browse/ESSAY-15) / 유형: 스토리 / 상태: 할 일

- 선행: [ESSAY-9](https://kmskojb.atlassian.net/browse/ESSAY-9), [ESSAY-19](https://kmskojb.atlassian.net/browse/ESSAY-19)
- 소유 범위: assignment/web_chat.html, assignment/web_demo_server.py, 화면 계약 테스트

제공된 Vue 화면과 FastAPI 프록시를 재사용해 네 입력·선택 공고·결과 근거·편집·복사 흐름으로 바꾼다.

완료 조건:

- [ ] 기업·직무·문항·경험 필수 입력과 선택 공고 URL/본문을 제공하고 요청 당시 스냅샷을 결과와 연결한다. POST JSON으로 전송하며 경험을 URL에 담지 않는다.
- [ ] ready에서 원문 비교·출처/확인일·user_provided 표시·직무 연결 이유·편집·복사를 제공한다. 복사본은 현재 편집 내용과 일치한다.
- [ ] 생성 중 입력/버튼 잠금·중복 방지·195초 제한·취소를 구현하고 보완/실패 시 현재 입력과 이전 결과를 보존한다.
- [ ] 서버와 동일한 LF/Unicode 코드 포인트로 글자 수를 계산한다. 편집 후 생성 당시 검토와 수정본 미검토를 구분하고 범위 밖에서도 사용자 복사는 허용한다.
- [ ] 실제 단계 이벤트를 연결하지 않으므로 공통 처리 중 표시만 사용한다. 원본 SSE 표시·full prompt 영역을 제품 화면에서 사용하지 않는다.
- [ ] 모의 응답과 실제 FastAPI를 구분해 시험하고 데스크톱/모바일·클립보드 실패·잘못된 응답을 확인한다. 프록시가 원본의 무한 timeout을 계승하지 않도록 제한한다.

### V2-08 Python·MCP·Vue 전체 흐름과 예외 회귀 검증

Jira: [ESSAY-16](https://kmskojb.atlassian.net/browse/ESSAY-16) / 유형: 작업 / 상태: 할 일

- 선행: [ESSAY-14](https://kmskojb.atlassian.net/browse/ESSAY-14), [ESSAY-15](https://kmskojb.atlassian.net/browse/ESSAY-15)
- 소유 범위: assignment/tests/, assignment/tests/fixtures/, docs/qa-v2.md, docs/qa-evidence/assignment/automated/

전환 구현의 실제 그래프/API/MCP 경계/화면을 자동 검증한다. 제공 프로젝트를 실행했다는 증거와 전환 서비스 검증을 분리한다.

완료 조건:

- [ ] 정상4회·수정6회·합류1회·보완즉시종료·수정실패종료를 실제 그래프와 제어 가능한 모델/도구 대역의 호출 기록으로 검증한다.
- [ ] 800/801/1000/1001자·CRLF·한글/이모지·offset 일치, 입력400·응답형식·설정누락·모델/검색시간초과·예산소진·취소·동시요청 격리를 검증한다.
- [ ] MCP stdio 연결·도구 발견·실제 프로토콜 호출·단절/잘못된 응답/취소를 검사한다. 제공자 대역을 쓴 경우 실제 MCP와 실제 OpenAI 검증을 혼동하지 않는다.
- [ ] 동명기업·공고상충·출처없음·지시문삽입·내부망URL·근거ID오류·없는성과 추가를 포함하고 hosted 예약2/보고량 및 모델1 선예약을 검사한다.
- [ ] 기존 5개 샘플 원본과 v1/run-7/ESSAY-9 증거를 변경하지 않는다. 전환용 fixture·추가 공고는 별도로 출처를 표시한다.
- [ ] Python lint/타입 검사/전체 테스트 및 Vue/프록시 검증, 기존 Next.js 회귀 확인 또는 기존 증거 대비 미실행 사유를 기록한다. 새 Python 통과를 기존156개 통과로 대체하지 않는다.

### V2-09 전환 서비스 실제 모델·MCP·Vue QA와 사실성 승인

Jira: [ESSAY-17](https://kmskojb.atlassian.net/browse/ESSAY-17) / 유형: 작업 / 상태: 할 일

- 선행: [ESSAY-16](https://kmskojb.atlassian.net/browse/ESSAY-16)
- 소유 범위: docs/qa-v2.md, docs/qa-evidence/assignment/live/, assignment/tests/실모델 실행 도구

전환 서비스에서 기존 5개 샘플과 실제 기업 자료를 다시 실행하고 화면·예외·사실성을 검증한다.

완료 조건:

- [ ] 원본5개 입력을 그대로 새 서비스에 실행한다. 가상 회사/직무 근거 부족은 needs_input이며 작성 회귀용 추가 공고는 user_provided 시험자료로 별도 실행한다.
- [ ] 실제 기업2곳 이상을 대상으로 공식공고성공·인재상만있고직무근거없음·동명기업·접근불가를 포함한다. MCP가 실제 호출됐는지, 검색/모델이 실제인지 대역인지 각각 표시한다.
- [ ] 입력·선택자료·기대결과·실제출력·판정·실행시각·커밋·모델/의존성버전·출처/확인일·역할별시간·토큰·모델호출·내장예약/보고량을 저장한다. 미관측 비용/내부페이지 수는 추정해 확정하지 않는다.
- [ ] 사용자 사실추가0건·회사주장출처일치·문항충족·801~1000자·6회/180초 이내를 사람과 실행기록으로 대조한다. 실패·수정·같은사례재검증을 별도 보존한다.
- [ ] 실제 Vue 브라우저에서 입력→생성→근거→편집→복사와 보완/오류 후 입력 보존을 확인하고 화면을 저장한다. 입력누락·키누락·MCP단절·timeout·품질실패는 통제된 예외 주입 여부를 표시한다.
- [ ] 작성자의 새 사실성 승인을 기록한 뒤 이 티켓을 완료한다. 기존 ESSAY-7 승인은 재사용하지 않는다. 에픽 완료에는 별도 제출 자료 작업도 완료돼야 하며 Next.js 기본값 전환은 하지 않는다.

### MIG-03 과제 제출 소스·README·변경 설명·검증 자료 완성

Jira: [ESSAY-20](https://kmskojb.atlassian.net/browse/ESSAY-20) / 유형: 작업 / 상태: 할 일

- 선행: [ESSAY-17](https://kmskojb.atlassian.net/browse/ESSAY-17)
- 소유 범위: assignment/README.md, assignment/docs/changes.md, assignment/docs/verification.md, 제출 패키지 목록 및 docs/qa-v2.md

과제의 여섯 제출물을 실행·검증 증거와 연결해 완성한다. 전환 구현과 QA를 수행하기 전에는 자료 완료로 표시하지 않는다.

완료 조건:

- [ ] 신규 서비스 전체 소스를 assignment/ 기준으로 독립 실행 가능한 제출물로 구성한다. 필요한 fixture/설정예시/잠금파일은 포함하고 실제 .env·키·DB·가상환경·캐시·개인 실행로그는 제외한다.
- [ ] README에 서비스명·목적·네역할구조·Mac 가상환경/패키지설치·API키 변수명·bash run.sh·종료·테스트·3분 시연을 작성하고 깨끗한 환경에서 그대로 따라 실행한다.
- [ ] 원본파일→유지/변경기능→신규파일→변경이유→검증증거 대응표를 작성한다. 실제 코드 재사용과 Next.js 설계/규칙 이식을 구분한다.
- [ ] 입력·정상결과·근거·편집/복사·보완·오류의 실제 화면을 포함한다. 모의 화면을 실제 모델 실행 화면으로 표기하지 않는다.
- [ ] 주요기능별 테스트 입력/기대결과/실제결과와 오류·예외 결과를 링크해 재현 가능하게 정리한다. 실패와 수정 이력을 지우지 않고 기존 5개 재실행과 실제 기업 사례를 구분한다.
- [ ] ESSAY-17의 작성자 승인 및 모든 필수 항목 완료를 확인하고 제출본 비밀정보/누락 파일 검사 결과를 기록한다. 이후에만 ESSAY-8 완료를 검토한다.


## 상태와 보존 규칙

실제 구현을 시작한 티켓만 진행 중, 완료 조건을 관찰한 티켓만 완료로 바꾼다. 이번 ESSAY-18은 원본 실행 검증까지 완료했고 후속 티켓은 할 일로 유지한다. 기존 ESSAY-7·9를 다시 열지 않는다. ESSAY-17 작성자 승인과 ESSAY-20 여섯 제출물 확인 후에만 ESSAY-8을 완료한다.

기존 담당자·유형·스프린트·기한을 임의 변경하지 않는다. 신규 작업은 같은 에픽 아래에 두고 실제 Blocks 링크로 선행을 연결한다. 현재 동기화 결과는 jira-v2.json을 따른다.

