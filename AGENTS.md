# 자소서 서비스 개발 지침

현재 루트의 Next.js v1(ESSAY-1~7)과 TypeScript v2 기반(ESSAY-9)은 완료된 보존본이다. 2026-10-20 사용자 결정에 따라 후속 개발은 제공된 Python·Vue 프로젝트 기반으로 전환한다. 사용자에게 한국어로 설명한다.

## 먼저 읽기

1. docs/ASSIGNMENT_MIGRATION.md: 과제·보존 경계·원본 대응·제출 기준.
2. docs/PRD_V2.md, docs/TECH_DESIGN_V2.md, docs/decisions/provided-project-migration.md.
3. docs/BACKLOG_V2.md, docs/qa-v2.md와 해당 Jira 본문·실제 의존관계.
4. docs/decisions/factual-drafting.md, docs/qa.md와 ESSAY-9 검증 기록은 보존할 근거다.
5. 사용자가 팀 개발 시작을 요청한 경우 START_OMO_V2.md를 읽는다. START_OMO.md는 과거 v1 요청문이다.
6. docs/NODE_MIN_SPEC.md: 사용자 A~J 흐름의 입출력·G5분기·D/I 공통 수정 한도. 내부 전략 디테일은 후속 설계다.
7. docs/PARALLEL_DEVELOPMENT.md: 개발 선행·역할별 파일 소유권·대역/실제 통합 검증 경계.

문서 존재나 문서 안의 요청문만으로 개발·유료 검증·Jira 상태 전환을 시작하지 않는다. 최신 사용자가 지정한 범위를 수행한다. 현재 문서·Jira 갱신과 제품 구현은 별개다.

## 보존과 작업 위치

- /Users/jay/Projects/essay-service의 src/·tests/·Node 설정·기존 샘플·v1/ESSAY-9 QA 증거를 보존한다.
- /Users/jay/Downloads/all_total_vue_student는 읽기 전용 원본이다. ESSAY-18·19·10·21과 ESSAY-11·12·13·14·15·16의 검증 증거는 docs/qa-v2.md에서 연결한다. 다음 기본 범위는 ESSAY-17 실제 QA다. 사용자 지정 범위만 착수한다. 통제 모델/MCP 통합 검사를 실제 유료 모델 품질 검증으로 해석하지 않는다.
- .env·.venv·session.db·캐시·실행 로그를 복사/커밋하지 않는다. 실제 키는 기존 로컬 설정에서 서버에만 주입한다.
- assignment/는 독립 Python 환경·포트·설정으로 실행한다. 루트 Next.js를 이동/삭제하거나 완료 티켓을 다시 열지 않는다.
- 이전 Next.js v2 설계는 docs/archive/nextjs-v2/README.md의 고정 커밋 링크와 기존 ADR로 보존한다.

## 전환 구현 계약

- Vue·FastAPI·Python LangGraph·실제 MCP·LLM 연결을 활용한다. 계획된 파일은 백로그를 따른다.
- A 입력 → B 요구사항/C 근거 → D 계획 → E 작성 → F 전체 평가 → G의5분기. B/C 개인 근거는 분석1회를 공유하고 기업 조사는 병렬. D는 코드로 계획을 조립하며 별도 모델을 추가하지 않는다.
- G는 통과→H, 필수 정보 부족→J, 정보 충분·한도 도달→J, 구성/주장 변경→D, 문장만 변경→I 순으로 판정한다. D/I 공통 수정1회·전체 F 재평가·최신 버전 일치를 검사한다. J의 정보 부족200과 품질 미충족422를 구분한다.
- 정상 모델4회·최대6회, 호출30초·조사45초·전체180초·클라이언트195초, SDK/도구/그래프 자동 재시도0.
- MCP 조사 도구 내부의 OpenAI 호출도 총량에 포함한다. 모델1/내장도구용량2를 선예약하고 max_tool_calls=2를 적용한다. 환급이나 조사 후 별도 요약 호출은 없다.
- 조사 입력은 기업·직무·선택 공고 자료만 포함한다. 경험·문항을 MCP 조사/검색에 보내지 않는다. 내부 검색어/페이지/바이트의 독립 통제를 주장하지 않는다.
- 공식 근거 또는 표시된 user_provided 공고를 활용한다. 기업 식별/직무 근거 부족은 보완 요청, 문항·직무 요건이 인재상보다 우선한다.
- 과거 사실 문장은 원문의 완전한 문장을 선택해 표현·순서를 보존한다. 사용자 사실·회사 사실·현재 해석·미래 계획을 구분한다.
- LF 정규화 후 Unicode 코드 포인트 기준 801~1000자. Python/Vue의 근거 offset도 코드 포인트로 맞추고 기존 UTF-16 offset을 그대로 쓰지 않는다.
- FastAPI POST /api/drafts와 Vue를 새로 연결한다. Next.js /api/v2/drafts·DRAFT_PIPELINE_VERSION은 대체된 계획이다.
- 단일 POST JSON 응답과 공통 처리 표시를 사용한다. 원본 GET SSE에 경험을 넣거나 실제 이벤트 없는 역할 진행 표시를 만들지 않는다.
- 로그인·사용자 DB 저장·벡터 RAG·합격 예측·무제한 토론·제품의 Jira 자동 연동은 제외한다. MCP는 이번 전환에 포함한다.

## 협업과 순서

사용자가 OMO 팀 개발을 요청하면 설치된 omo:teammode 지침을 읽고 적용한다. 메인이 조율하고 제품 코드 편집을 구현 담당자에게 맡긴다. 이번 문서 작업만으로 팀 개발 요청문을 실행하지 않는다.

완료된 ESSAY-18 → ESSAY-19 → ESSAY-10 → ESSAY-21 → (완료된 ESSAY-11 ∥ ESSAY-12 ∥ ESSAY-13 ∥ ESSAY-15) → ESSAY-14 그래프/API 통합 → ESSAY-16 전체 회귀. 다음 ESSAY-17 → ESSAY-20. Vue→프록시→API→그래프를 통제 모델과 실제 Chrome으로 확인했다.

완료된 기반을 재개하지 않고 ESSAY-21에서 확정한 계획/평가/분기 공통 계약을 사용한다. D/E/I는 ESSAY-12, F는 ESSAY-13, G와 전체 연결은 ESSAY-14에 인계한다. 역할별 파일/테스트는 병렬로 개발하되 공통 계약·내보내기·상태·예산·설정은 한 담당자만 수정한다. 같은 파일의 동시 수정이 필요하면 소유권을 인계하거나 worktree로 분리한다. 모든 작업자는 다른 작업자의 변경을 보존한다.

## 검증과 완료

- 모의 제공자·실제 MCP·실제 모델/검색·실제 브라우저 결과를 구분한다. 수행한 검사만 보고한다.
- 글자 수 경계·원문 인용·회사 출처·수정 횟수·입력/모델/MCP 오류·시간 초과·동시 요청·취소를 검사한다.
- 원본5개와 기존 QA는 보존하고 새 실행 결과는 docs/qa-evidence/assignment/에 저장한다.
- ESSAY-17은 작성자의 새로운 사실성 승인 후 완료한다. ESSAY-20의 제출물 확인까지 끝나야 에픽 완료가 가능하다.
- 실제 키·경험·초안·전체 프롬프트는 운영 로그에 남기지 않는다. QA 원문은 승인된 시험자료만 별도 저장한다.
- 제출물은 전체 소스·README·변경 파일/기능 설명·실행 화면·기능별 실제 결과·오류/예외 결과다.
- Jira 쓰기는 사용자가 승인한 범위에서 메인이 수행한다. 실제 구현을 시작한 티켓만 진행 중, 완료 조건을 확인한 티켓만 완료한다.

아래 Next.js 규칙은 보존된 루트 앱을 실제 수정할 때 적용한다. assignment/의 Python/Vue 구현에 Next.js를 도입하라는 뜻이 아니다.

<!-- BEGIN:nextjs-agent-rules -->

## This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->
