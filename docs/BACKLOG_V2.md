# v2 전환 구현 백로그

- 갱신일: 2026-10-21 / 상태: ESSAY-18·19·10·21·11·12·13·14·15·16 완료. Chrome→Vue→API→LangGraph 통제 회귀 확인, 다음 ESSAY-17 실제 QA
- 기존 ESSAY-1~7 및 ESSAY-9는 완료 상태로 보존한다. ESSAY-8은 진행 중이다.
- ESSAY-10~17은 Python·MCP·Vue 기준이다. ESSAY-18~20 전환 작업과 ESSAY-21 노드 공통 계약 확장을 관리한다. 미착수 구현/검증/제출 티켓은 할 일이다.
- 2026-10-20 사용자 A~J 흐름에 맞춰 [노드별 최소 명세](NODE_MIN_SPEC.md)를 추가했다. 2026-10-21 병렬 선행 관계에 따라 ESSAY-11·12·13·15를 역할별 구현·검증했다. 내부 전략 디테일은 후속 설계다.
- [전환 계획](ASSIGNMENT_MIGRATION.md) · [PRD](PRD_V2.md) · [기술 설계](TECH_DESIGN_V2.md) · [QA](qa-v2.md)
- [이전 문서 기준선](archive/nextjs-v2/README.md) · [Jira 동기화 기록](jira-v2.json)
- 사용자 승인 병렬 작업 기준: [병렬 개발·통합 검증](PARALLEL_DEVELOPMENT.md). 실행 흐름 A~J와 개발 티켓의 병렬 순서를 구분한다.

## 순서와 소유권

완료된 ESSAY-18 → ESSAY-19 → ESSAY-10 → ESSAY-21 공통 계약 확장 → (완료된 ESSAY-11 B/C 분석 ∥ ESSAY-12 D/E/I 작성 ∥ ESSAY-13 F 평가 ∥ ESSAY-15 Vue) → ESSAY-14 A/G/H/J 그래프/FastAPI → ESSAY-16 전체 회귀. 다음 ESSAY-17 실제 QA/작성자 승인 → ESSAY-20 제출 자료.

ESSAY-16은 ESSAY-14·15 모두를 선행으로 한다. ESSAY-19는 ESSAY-18과 완료된 ESSAY-9를 따른다. 기존 ESSAY-9→10/11/15 연결도 보존하지만 Python 구현 착수에는 ESSAY-19가 추가 필수다.

완료된 ESSAY-19·10의 계약/실행 기반을 보존한다. ESSAY-21 담당자가 공통 계약·상태를 먼저 확정한다. 이후 역할별 파일은 병렬로 개발하되 공통 계약/내보내기/상태/예산/설정 변경은 한 담당자에게 모아 순차 반영한다. D/E/I는 ESSAY-12, F는 ESSAY-13, 실제 연결과 G는 ESSAY-14, 화면/프록시는 ESSAY-15가 맡는다. 다른 사람의 변경을 되돌리지 않는다.

| ID | Jira | 작업 | 선행 |
| --- | --- | --- | --- |
| MIG-01 | [ESSAY-18](https://kmskojb.atlassian.net/browse/ESSAY-18) | 제공 프로젝트 기준선 보존과 Mac 원본 실행 확인 | 없음 |
| MIG-02 | [ESSAY-19](https://kmskojb.atlassian.net/browse/ESSAY-19) | Python 공통 계약·예산·MCP 실행 기반 이식 | ESSAY-18, ESSAY-9 |
| V2-01 | [ESSAY-9](https://kmskojb.atlassian.net/browse/ESSAY-9) | 공통 계약·LangGraph 실행 기반 구성 (완료된 TypeScript 기준선) | 없음 |
| V2-02 | [ESSAY-10](https://kmskojb.atlassian.net/browse/ESSAY-10) | MCP 기업·직무 조사와 공식 출처 검증 구현 | ESSAY-9, ESSAY-19 |
| V2-10 | [ESSAY-21](https://kmskojb.atlassian.net/browse/ESSAY-21) | A~J 흐름의 공통 계약·계획·평가 상태 확장 | ESSAY-19, ESSAY-10 |
| V2-03 | [ESSAY-11](https://kmskojb.atlassian.net/browse/ESSAY-11) | B/C 요구사항 해석·개인 근거 추출 | ESSAY-9, ESSAY-19, ESSAY-21 |
| V2-04 | [ESSAY-12](https://kmskojb.atlassian.net/browse/ESSAY-12) | D/E/I 작성 계획·초안·부분 수정 | ESSAY-10, ESSAY-21 |
| V2-05 | [ESSAY-13](https://kmskojb.atlassian.net/browse/ESSAY-13) | F 필수 기준 평가·수정 범위 판정 | ESSAY-21 |
| V2-06 | [ESSAY-14](https://kmskojb.atlassian.net/browse/ESSAY-14) | A/G/H/J LangGraph 분기·FastAPI 통합 | ESSAY-11, ESSAY-12, ESSAY-13 |
| V2-07 | [ESSAY-15](https://kmskojb.atlassian.net/browse/ESSAY-15) | Vue 입력·결과·J 종료 사유 구분 | ESSAY-9, ESSAY-19, ESSAY-21 |
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

assignment/에는 ESSAY-18 기준선 위에 ESSAY-19 공통 기반·ESSAY-10 조사 역할·ESSAY-21 A~J 공통 계약·ESSAY-11 분석·ESSAY-12 작성·ESSAY-13 평가·ESSAY-15 Vue 화면·ESSAY-14 LangGraph/API 연결이 구현됐다. ESSAY-16에서 통제 모델과 실제 Chrome으로 Vue→프록시→API→그래프 전체 회귀를 확인했다. 실제 모델 품질은 ESSAY-17 범위다.

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

Jira: [ESSAY-10](https://kmskojb.atlassian.net/browse/ESSAY-10) / 유형: 작업 / 상태: 완료

- 선행: [ESSAY-9](https://kmskojb.atlassian.net/browse/ESSAY-9), [ESSAY-19](https://kmskojb.atlassian.net/browse/ESSAY-19)
- 소유 범위: assignment/agent/nodes/research.py, agent/research.py·source_*.py, 해당 테스트. ESSAY-19 mcp_server.py·mcp_client.py 등록/연결 구조 재사용

원본 모니터링/장애 매뉴얼 조회를 기업·채용 정보 조사로 바꾸고, 실제 MCP를 통해 회사와 직무 근거를 얻는다.

완료 조건:

- [x] 원본 agent/mcp_client.py와 MCP 서버 등록 구조를 활용해 research_company_role 도구를 실제 호출한다. 사용되지 않는 장애 진단·decoy docs 서버는 제품 실행에서 제외하고 변경 이유를 기록한다.
- [x] 현재 OpenAI 키와 내장 검색을 유지한다. 조사 모델은 MCP 서버 안의 Responses 1회이며 그래프에서 추가 조사/요약 모델을 호출하지 않는다. 모델1/도구2 선예약·30/45초 제한을 지킨다.
- [x] 기업 식별·공식 채용 도메인/공식 링크 관계·출처 구절을 확인한다. 후보 자료는 unverified이며 검색 요약만으로 official로 승격하지 않는다. sourceId·URL 또는 사용자 본문 표시·확인 시각·근거 구절을 저장한다.
- [x] 사용자 공고는 user_provided로 구분하고 문항·직무 요구를 인재상보다 우선한다. 인재상만 없으면 생략, 회사 식별/직무 근거 부족은 needs_input, 제공자 장애·잘못된 응답은 error로 종료한다.
- [x] 동명 기업·상충 자료·지시문 삽입·빈 자료·접근 거부를 시험한다. 경험·문항은 MCP 조사 입력이나 외부 검색에 포함하지 않는다.
- [x] 공식 페이지 직접 확인이 필요하면 HTTP(S)만 허용하고 DNS/IP/모든 리다이렉트에서 내부망을 차단한다. 직접 읽기3회·페이지1MiB·정리 텍스트12000 코드 포인트 제한을 적용한다. hosted 내부 페이지 수/바이트와 혼동하지 않는다.

ESSAY-10 완료 당시 구현·최종 통합242개·실제 네이버/합성 공고·실패5회 보존·출처 신뢰 검토는 [조사 보고서](qa-evidence/assignment/research/verification.md)를 따른다. 이후 ESSAY-21 공통 계약과 ESSAY-11·12·13·15 독립 역할 구현·검증도 완료했다.

### V2-10 A~J 흐름의 공통 계약·계획·평가 상태 확장

Jira: [ESSAY-21](https://kmskojb.atlassian.net/browse/ESSAY-21) / 유형: 작업 / 상태: 완료

- 선행: [ESSAY-19](https://kmskojb.atlassian.net/browse/ESSAY-19), [ESSAY-10](https://kmskojb.atlassian.net/browse/ESSAY-10)
- 소유 범위: assignment/agent/contract_flow_{plan,draft,evaluation,route}.py·contracts.py·flow_state.py·state.py·budget.py·assignment/pyproject.toml 및 flow 계약/상태/반례 테스트. 기존 contract_results.py·provider_schema.py는 보존했다.

완료된 공통 기반에 요구사항·작성 계획·평가·분기 자료를 추가한다. 상세 전략은 유예하며 [최소 명세](NODE_MIN_SPEC.md)의 입출력·종료 조건을 후속 역할이 사용할 수 있게 만든다.

완료 조건:

- [x] 요구사항 ID·필수 조건·근거 후보, WritingPlan(근거·주장·문단/요구사항 대응·버전), 초안 버전/문단 범위, Evaluation(기준별 결과·평가 버전·지적 범위), route/종료 사유의 Pydantic 계약과 상태를 확장한다. 기존 ResearchResult와 근거/응답 계약을 보존한다.
- [x] B/C 개인 근거 추출은 분석 모델1회를 공유하고 기업 조사는 기존 MCP 모델1회를 사용한다. D는 코드로 계획을 조립한다. 정상4회·D/I 수정 포함최대6회·18,000토큰·30/45/180/195초·재시도0을 유지하는 호출 배치/소유권을 명시한다.
- [x] D 재계획과 I 부분 수정은 revisionCount 0→1의 같은 원자 예약을 공유하고 재진입·오류 시 초기화/환급하지 않는다. 평가한 초안·계획 버전이 반환 버전과 다르면 ready를 차단할 수 있는 계약을 제공한다.
- [x] 정보 부족은 기존 needs_input 200의 missingFields/questions/reasonCode로 표현한다. 정보 충분·수정 한도 소진은 QUALITY_CHECK_FAILED 또는 길이만 실패 시 LENGTH_VALIDATION_FAILED 422로 표현하고 부족 항목을 지어내지 않는다.
- [x] missing_info / plan_or_claim / wording 지적 범위와 유효한 근거·문단·주장 참조를 검증한다. 숨은 추론을 저장하지 않으며 계획은 짧은 구조화 결과로 제한한다.
- [x] 계약 반례·버전 불일치·원자 수정 예약·요청 격리와 기존 조사/기반 회귀를 검증하고 후속 ESSAY-11~15에 공통 파일 소유권을 순차 인계한다.

Python355·JavaScript12 통과, 유료2개 기본 제외·이번 유료 호출0회. 실제 모델/업무 노드/HTTP 통합 검증은 후속 티켓이다. [검증 보고서](qa-evidence/assignment/flow-foundation/verification.md) · [공통 계약 인계](FLOW_CONTRACTS.md).

### V2-03 B/C 요구사항 해석·개인 근거 추출 구현

Jira: [ESSAY-11](https://kmskojb.atlassian.net/browse/ESSAY-11) / 유형: 작업 / 상태: 완료

- 선행: [ESSAY-9](https://kmskojb.atlassian.net/browse/ESSAY-9), [ESSAY-19](https://kmskojb.atlassian.net/browse/ESSAY-19), [ESSAY-21](https://kmskojb.atlassian.net/browse/ESSAY-21)
- 소유 범위: assignment/agent/nodes/analyze.py, C의 검증 근거 묶음 조립 및 해당 테스트

논리 노드 B와 C의 개인 근거 부분을 분석 모델1회로 구현한다. 기업 조사는 병렬 실행하고, C에서 기존 ESSAY-10 결과와 개인 근거를 합친다. 외부 자료로 개인 경험을 보충하지 않는다.

완료 조건:

- [x] B의 요구사항에 ID·필수 여부·확인 조건·관련 경험 후보 ID를 연결하고 experienceEvidence·gaps를 함께 반환한다. 각 개인 근거에 원문 구절·코드 포인트 start/end를 연결하며 사용자가 요구하지 않은 조건을 필수로 만들지 않는다.
- [x] LF 정규화한 경험의 원문 구절과 위치를 서버에서 대조한다. 없는 역할·행동·결과·수치·시점·인과관계·과거 심리 변화를 추가하지 않는다.
- [x] 경험 부족 시 구체적 보완 항목과 질문을 반환해 작성 호출 전에 종료할 수 있다.
- [x] C에서 검증된 회사/직무 근거와 개인 근거를 분리해 묶고, B/C 모두 준비돼야 D를 실행할 수 있게 한다. 인재상만 없음은 보완 사유가 아니며 핵심 직무/경험 부족과 구분한다.
- [x] 긴 경험·불완전한 경험·허위 성과 요구·입력 내 지시문·CRLF/이모지 인용을 시험한다. 모델은 최대1회이고 조사 도구를 호출하지 않는다.

### V2-04 D/E/I 작성 계획·초안·부분 수정 구현

Jira: [ESSAY-12](https://kmskojb.atlassian.net/browse/ESSAY-12) / 유형: 작업 / 상태: 완료

- 선행: [ESSAY-10](https://kmskojb.atlassian.net/browse/ESSAY-10), [ESSAY-21](https://kmskojb.atlassian.net/browse/ESSAY-21)
- 소유 범위: assignment/agent/nodes/write.py, D 계획 조립·I 부분 수정 모듈 및 해당 테스트

논리 노드 D/E/I를 구현한다. D는 검증된 후보로 최소 계획을 조립하는 코드 단계이며 E/I는 같은 작성 모델 역할을 쓴다. 경험 우선순위·문단 전개 기법의 정교화는 후속 설계로 남기고 계획/근거 계약과 사실 보존 원칙부터 지킨다.

완료 조건:

- [x] D가 선택 근거·주장 종류/근거·필수 요구사항 대응·문단 ID/목적/순서/분량·버전의 WritingPlan을 코드로 생성/검증한다. F의 구성/주장 지적에 따라 계획을 갱신하며 추가 계획 모델을 호출하지 않는다.
- [x] E는 원래 문항·원문·검증된 근거와 계획을 받아 draft·claimMap·fitReasons·문단 범위·버전을 반환한다. 계획을 몰래 변경하지 않고 회사 사실과 개인 사실을 분리한다.
- [x] 과거 사실은 원문의 완전한 문장을 선택해 표현·순서를 보존한다. 새 문장은 별도 현재 해석·미래 계획으로 구분하며 없는 근거 ID·수치·성과를 만들지 않는다.
- [x] 직무 요구를 일반 인재상보다 우선하고 인재상 자료가 없을 때 임의 생성하지 않는다.
- [x] G가 예약한 공통 수정1회에 D→E 또는 I만 실행한다. I는 최신 버전의 허용 문장 범위만 바꾸고 계획·경험 선택·사실 문장을 고정한다. 범위 밖/중복/오래된 패치를 거부하며 전체 초안·claimMap을 재조립해 F로 보낸다.
- [x] 서버 길이·검토 지적을 사용하며 문자열 자르기·패딩으로801~1000자를 맞추지 않는다. 수정 시 B/C·조사를 재실행하거나 횟수를 초기화하지 않는다.
- [x] 허위 성과 유도·회사 사실의 개인 성과 전용·수정 중 사실 추가 사례를 단위 테스트한다.
- [x] ESSAY-21의 실제 공통 계약과 합성 분석/조사 fixture로 독립 모듈을 검증해 ESSAY-11·13·15와 병렬 개발한다. 실제 다른 역할 연결·전체 서비스 통과는 ESSAY-14·16에서 별도로 확인한다.

### V2-05 F 필수 기준 평가·수정 범위 판정 구현

Jira: [ESSAY-13](https://kmskojb.atlassian.net/browse/ESSAY-13) / 유형: 작업 / 상태: 완료

- 선행: [ESSAY-21](https://kmskojb.atlassian.net/browse/ESSAY-21)
- 소유 범위: assignment/agent/nodes/review.py, assignment/agent/validate_evidence.py 및 해당 테스트

논리 노드 F를 구현한다. 원본의 단순 형식 검사·강제 통과를 필수 기준별 근거 검사와 독립 모델 검토로 교체하고, 실제 경로 선택은 G(ESSAY-14)에 맡긴다.

완료 조건:

- [x] 최신 초안/계획 버전의 계약·개인/회사 사실·문항·직무 연결·분량·해석/계획 구분을 기준별로 검사한다. 코드 검사와 독립 모델 검토의 결과·평가 버전을 함께 반환한다.
- [x] 없는 성과·시점 추가·출처 없는 회사 주장·회사/사용자 사실 혼동·문항 미응답 반례를 검출한다. 모델 pass가 코드 검사 실패를 덮을 수 없다.
- [x] issues에 기준 ID·주장/문단 범위·원인·missing_info/plan_or_claim/wording·구체적 수정 지시를 연결한다. 정보 충분 여부와 허용 문장 범위를 설명하며 분류 불가를 임의 pass/부분 수정으로 처리하지 않는다.
- [x] D/E 및 I 수정 뒤 전체 초안을 다시 검토하고 이전 평가를 재사용하지 않는다. 필수 정보 부족과 정보 충분·수정 한도 소진을 G가 구분할 수 있게 반환한다. 점수/가중치·세부 의미 평가 전략은 후속 설계다.
- [x] 원본의 세 번째 시도 강제 통과를 사용하지 않는다. 검토 미완료/실패 초안을 ready로 반환하지 않는다.
- [x] 검토 통과를 사실성의 증명이나 합격 보장으로 표현하지 않는다.
- [x] ESSAY-21의 WritingPlan/DraftEnvelope 합성 fixture와 실제 검토 어댑터로 독립 검증한다. ESSAY-12 완료를 기다리는 의존은 제거하며, 실제 작성 결과와의 연결은 ESSAY-14에서 검증한다.

### V2-06 A/G/H/J LangGraph 분기·FastAPI 통합

Jira: [ESSAY-14](https://kmskojb.atlassian.net/browse/ESSAY-14) / 유형: 작업 / 상태: 완료

- 선행: [ESSAY-11](https://kmskojb.atlassian.net/browse/ESSAY-11), [ESSAY-12](https://kmskojb.atlassian.net/browse/ESSAY-12), [ESSAY-13](https://kmskojb.atlassian.net/browse/ESSAY-13)
- 소유 범위: assignment/agent/essay_graph.py·essay_collect.py·essay_route.py, assignment/server.py의 POST /api/drafts, 통합 테스트. 원본 장애 진단 graph.py는 보존

원본 build_graph/deps/FastAPI 생명주기 구조를 활용해 A~J 논리 흐름과 G의 다섯 분기를 연결한다. G는 코드로 결정하며 [최소 명세](NODE_MIN_SPEC.md)의 분기 순서를 따른다.

완료 조건:

- [x] A 이후 B/C 자료를 한 번만 합류해 D/E/F로 진행한다. B/C 필수 정보 부족·실패 시 작성하지 않고 가능한 진행 작업을 취소한다. 실제 그래프 정상4회·D/I 수정 포함최대6회를 검증한다.
- [x] G가 순서대로 모두 통과→H, 필수 정보 부족→J, 정보 충분·한도 도달→J, 구성/주장 변경→D, 문장만 변경→I를 선택한다. 혼합 지적은 정보 부족 우선·그다음 D 우선이며 D/I는 같은 수정1회 원자 예약을 공유한다.
- [x] H는 최신 전체 F 통과 버전만 반환한다. J는 needs_input200과 정보 충분·품질실패422를 구분한다. 한도1에서 통과한 결과는 H이며 timeout/제공자/계약 오류를 정보 부족으로 바꾸지 않는다.
- [x] 요청별 상태·예산·MCP 응답을 격리하고 숨은 SDK/도구/그래프 재시도 및 중복 실행을 차단한다. MCP 조사를 전체 모델/시간 예산에 포함한다.
- [x] FastAPI POST /api/drafts가 ready/needs_input 200, INVALID_INPUT400, 품질실패422, CONFIG_ERROR500, 제공자오류502, timeout504를 반환한다. FastAPI 기본 입력 오류422는 공통 입력 계약400으로 정규화한다.
- [x] 모든 ready는 근거 검사·모델 검토·801~1000자를 통과한다. 오류 응답은 requestId·code·message만 포함하고 초안·원문·키·전체 프롬프트를 노출하지 않는다.
- [x] 원본 GET /chat/stream에 경험을 싣지 않으며 제출 서비스는 POST JSON으로 처리한다. 원본 대화 이력 SQLite 저장/전체 프롬프트 반환/외부 tracing을 제품 경로에서 사용하지 않는다.
- [x] Next.js 루트는 별도로 실행되는 보존본이다. Next.js /api/v2/drafts·DRAFT_PIPELINE_VERSION 추가는 취소된 계획이며 assignment 서버와 포트를 분리했다. 180초 요청 deadline 적용과 실제 HTTP smoke를 확인했다. 180초 연속 HTTP 연결 시험은 수행하지 않았고 [ESSAY-16 보고서](qa-evidence/assignment/automated/verification.md)에 경계를 기록했다.
- [x] ESSAY-11·12·13의 실제 구현을 기존 ESSAY-10과 연결해 각 모듈 대역을 제거한 실행을 검증한다. 개별 모듈/fixture 통과만으로 전체 그래프 완료를 판정하지 않는다.

### V2-07 Vue 자기소개서 입력·근거·편집·보완 화면 구현

Jira: [ESSAY-15](https://kmskojb.atlassian.net/browse/ESSAY-15) / 유형: 스토리 / 상태: 완료

- 선행: [ESSAY-9](https://kmskojb.atlassian.net/browse/ESSAY-9), [ESSAY-19](https://kmskojb.atlassian.net/browse/ESSAY-19), [ESSAY-21](https://kmskojb.atlassian.net/browse/ESSAY-21)
- 소유 범위: assignment/web_chat.html, assignment/web_demo_server.py, 화면 계약 테스트

제공된 Vue 화면과 FastAPI 프록시를 재사용해 네 입력·선택 공고·결과 근거·편집·복사 흐름으로 바꾼다.

완료 조건:

- [x] 기업·직무·문항·경험 필수 입력과 선택 공고 URL/본문을 제공하고 요청 당시 스냅샷을 결과와 연결한다. POST JSON으로 전송하며 경험을 URL에 담지 않는다.
- [x] ready에서 원문 비교·출처/확인일·user_provided 표시·직무 연결 이유·편집·복사를 제공한다. 복사본은 현재 편집 내용과 일치한다.
- [x] 생성 중 입력/버튼 잠금·중복 방지·195초 제한·취소를 구현하고 보완/실패 시 현재 입력과 이전 결과를 보존한다.
- [x] J에서 실제 필수 정보 부족은 보완 질문으로, 정보 충분·수정 한도 소진422는 이번 생성의 품질 미충족으로 구분한다. 없는 부족 항목을 요청하거나 미검토 초안을 최종 결과로 노출하지 않는다.
- [x] 서버와 동일한 LF/Unicode 코드 포인트로 글자 수를 계산한다. 편집 후 생성 당시 검토와 수정본 미검토를 구분하고 범위 밖에서도 사용자 복사는 허용한다.
- [x] 실제 단계 이벤트를 연결하지 않으므로 공통 처리 중 표시만 사용한다. 원본 SSE 표시·full prompt 영역을 제품 화면에서 사용하지 않는다.
- [x] 모의 응답과 실제 FastAPI를 구분해 시험하고 데스크톱/모바일·클립보드 실패·잘못된 응답을 확인한다. 프록시가 원본의 무한 timeout을 계승하지 않도록 제한한다.

### V2-08 Python·MCP·Vue 전체 흐름과 예외 회귀 검증

Jira: [ESSAY-16](https://kmskojb.atlassian.net/browse/ESSAY-16) / 유형: 작업 / 상태: 완료

- 선행: [ESSAY-14](https://kmskojb.atlassian.net/browse/ESSAY-14), [ESSAY-15](https://kmskojb.atlassian.net/browse/ESSAY-15)
- 소유 범위: assignment/tests/, assignment/tests/fixtures/, docs/qa-v2.md, docs/qa-evidence/assignment/automated/

전환 구현의 실제 그래프/API/MCP 경계/화면을 자동 검증한다. 제공 프로젝트를 실행했다는 증거와 전환 서비스 검증을 분리한다.

완료 조건:

- [x] [최소 명세](NODE_MIN_SPEC.md)의 NF-01~10을 실제 그래프와 제어 가능한 모델/도구 대역으로 검증한다. G의5분기·B/C 조기 보완·혼합 지적 우선순위·한도1에서의 통과를 포함한다.
- [x] D 재계획/I 부분 수정이 같은 수정1회를 공유하고 정상4회·수정최대6회·합류1회로 끝나는지 확인한다. 잘못된 범위/버전·사실 원문 변경·I 이후 전체 재평가 누락·이전 pass 재사용·숨은 재시도를 거부한다.
- [x] 800/801/1000/1001자·CRLF·한글/이모지·offset 일치, 입력400·응답형식·설정누락·모델/검색시간초과·예산소진·취소·동시요청 격리를 검증한다.
- [x] MCP stdio 연결·도구 발견·실제 프로토콜 호출·단절/잘못된 응답/취소를 검사한다. 제공자 대역을 쓴 경우 실제 MCP와 실제 OpenAI 검증을 혼동하지 않는다.
- [x] 동명기업·공고상충·출처없음·지시문삽입·내부망URL·근거ID오류·없는성과 추가를 포함하고 hosted 예약2/보고량 및 모델1 선예약을 검사한다.
- [x] 기존 5개 샘플 원본과 v1/run-7/ESSAY-9 증거를 변경하지 않는다. 전환용 fixture·추가 공고는 별도로 출처를 표시한다.
- [x] Python lint/타입 검사/전체 테스트 및 Vue/프록시 검증, 기존 Next.js 회귀 확인 또는 기존 증거 대비 미실행 사유를 기록한다. 새 Python 통과를 기존156개 통과로 대체하지 않는다. [ESSAY-16 보고서](qa-evidence/assignment/automated/verification.md)를 따른다.

### V2-09 전환 서비스 실제 모델·MCP·Vue QA와 사실성 승인

Jira: [ESSAY-17](https://kmskojb.atlassian.net/browse/ESSAY-17) / 유형: 작업 / 상태: 진행 중

- 선행: [ESSAY-16](https://kmskojb.atlassian.net/browse/ESSAY-16)
- 소유 범위: docs/qa-v2.md, docs/qa-evidence/assignment/live/, assignment/tests/실모델 실행 도구

전환 서비스에서 기존 5개 샘플과 실제 기업 자료를 다시 실행하고 화면·예외·사실성을 검증한다.

2026-10-21 실제 모델·MCP로 원본5개 1차 실행과 실패1개 재실행, 네이버 공식 공고 성공 및 Anthropic 채용 목록 근거 부족을 기록했다. 별도 합성 사용자 공고의 전체 작성 시도는 근거 검증 실패와 작성 timeout으로 종료했다. 아직 전체 초안·Vue 실모델·사실성 승인은 미검증이다. [중간 QA](qa-evidence/assignment/live/verification.md).

완료 조건:

- [ ] 원본5개 입력을 그대로 새 서비스에 실행한다. 가상 회사/직무 근거 부족은 needs_input이며 작성 회귀용 추가 공고는 user_provided 시험자료로 별도 실행한다.
- [ ] 실제 기업2곳 이상을 대상으로 공식공고성공·인재상만있고직무근거없음·동명기업·접근불가를 포함한다. MCP가 실제 호출됐는지, 검색/모델이 실제인지 대역인지 각각 표시한다.
- [ ] 입력·선택자료·기대결과·실제출력·판정·실행시각·커밋·모델/의존성버전·출처/확인일·역할별시간·토큰·모델호출·내장예약/보고량을 저장한다. 미관측 비용/내부페이지 수는 추정해 확정하지 않는다.
- [ ] 사용자 사실추가0건·회사주장출처일치·문항충족·801~1000자·6회/180초 이내를 사람과 실행기록으로 대조한다. 실패·수정·같은사례재검증을 별도 보존한다.
- [ ] 실제 모델에서 계획→초안→전체 평가→경로/종료 사유·계획/초안 버전·수정 횟수를 기록한다. G의5분기는 자동 검사와 대응하고 실모델에서 발생하지 않은 분기는 미관측 또는 통제 주입으로 표시한다. 이를 보기 위해 무제한 유료 반복하지 않는다.
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
- [ ] A~J 논리 노드→실제 코드/모델 역할→테스트 결과를 대응하고 G의5분기·공통 수정 한도·J 종료 사유를 README/변경 설명/검증 자료에 반영한다. 유예한 내부 전략을 구현 완료로 설명하지 않는다.
- [ ] 입력·정상결과·근거·편집/복사·보완·오류의 실제 화면을 포함한다. 모의 화면을 실제 모델 실행 화면으로 표기하지 않는다.
- [ ] 주요기능별 테스트 입력/기대결과/실제결과와 오류·예외 결과를 링크해 재현 가능하게 정리한다. 실패와 수정 이력을 지우지 않고 기존 5개 재실행과 실제 기업 사례를 구분한다.
- [ ] ESSAY-17의 작성자 승인 및 모든 필수 항목 완료를 확인하고 제출본 비밀정보/누락 파일 검사 결과를 기록한다. 이후에만 ESSAY-8 완료를 검토한다.


## 상태와 보존 규칙

실제 구현을 시작한 티켓만 진행 중, 완료 조건을 관찰한 티켓만 완료로 바꾼다. ESSAY-18·19·10·21의 완료와 기존 이력을 보존한다. ESSAY-11·12·13·15 독립 구현·검증, ESSAY-14 실제 역할 연결, ESSAY-16 전체 회귀를 완료했다. ESSAY-17·20은 할 일이며 다음 기본 범위는 ESSAY-17이다. ESSAY-17 작성자 승인과 ESSAY-20 여섯 제출물 확인 후에만 ESSAY-8을 완료한다.

기존 담당자·유형·스프린트·기한을 임의 변경하지 않는다. 신규 작업은 같은 에픽 아래에 두고 실제 Blocks 링크로 선행을 연결한다. 현재 동기화 결과는 jira-v2.json을 따른다.

