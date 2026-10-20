# 자소서 서비스 — 기존 MVP와 Python 전환

기업명·직무·문항·경험으로 자기소개서 초안을 만들고, 원본 경험과 비교해 편집·복사하는 서비스다. 완료된 Next.js + TypeScript MVP는 루트에 보존하고, 제공 프로젝트 기반의 Python·Vue 전환판은 assignment/에서 개발한다.

현재 루트의 완료된 Next.js v1과 TypeScript ESSAY-9 공통 기반을 보존한다. 2026-10-20 제공된 LangGraph·MCP·LLM·Vue·FastAPI 프로젝트의 소스를 assignment/에 복사하고 ESSAY-18 원본 실행 검증을 완료했다. 모의 LLM·JSON 자료와 실제 API·MCP·Vue 화면을 구분한 [기준선 검증 보고서](docs/qa-evidence/assignment/baseline/verification.md)가 있다. ESSAY-19 Python 공통 기반 구현·검증도 완료했다. [기반 보고서](docs/qa-evidence/assignment/foundation/verification.md)를 참고한다. ESSAY-10 기업·직무 조사와 공식 출처 검증도 구현·검증했다. 네이버·카카오·OpenAI·Anthropic의 정확한 출처 목록과 실제 공고/사용자 자료 대조를 제공한다. [조사 보고서](docs/qa-evidence/assignment/research/verification.md)에 실제 네이버 공고와 합성 사용자 공고 결과·실패 이력·지원 한계가 있다. 분석·작성·검토·전체 API·새 Vue 화면은 후속 작업이다.

ESSAY-18·19·10 완료 후 [노드별 최소 명세](docs/NODE_MIN_SPEC.md)에 따라 ESSAY-21 공통 계약 확장 → ESSAY-11~17 기능·QA → ESSAY-20 제출 자료 순서로 진행한다. A~J 흐름·G의5분기·수정 한도를 문서화했고 내부 전략 디테일은 후속 설계로 남겼다. 이번 갱신은 구현 착수가 아니다. [전환 계획](docs/ASSIGNMENT_MIGRATION.md)에 재사용/변경 대응과 여섯 제출물이 있다.

## 문서

- [제공 프로젝트 전환 계획](docs/ASSIGNMENT_MIGRATION.md) · [전환 결정](docs/decisions/provided-project-migration.md) · [이전 기준선](docs/archive/nextjs-v2/README.md)

- [기획서 및 PRD](docs/PRD.md)
- [기술 설계서](docs/TECH_DESIGN.md)
- [v2 PRD](docs/PRD_V2.md) · [v2 기술 설계](docs/TECH_DESIGN_V2.md) · [v2 백로그](docs/BACKLOG_V2.md) · [v2 QA 계획](docs/qa-v2.md)
- [A~J 노드별 최소 명세](docs/NODE_MIN_SPEC.md) · [ESSAY-10 조사 검증 결과](docs/qa-evidence/assignment/research/verification.md)
- [개발 에이전트 지침](AGENTS.md)
- [v2 OMO 개발 시작 요청문](START_OMO_V2.md) · [완료된 v1 요청문](START_OMO.md)
- [Jira 프로젝트 작업 목록](https://kmskojb.atlassian.net/jira/software/projects/ESSAY/list)

## OMO로 시작하기

후속 전환 개발은 이 폴더를 열고 원하는 티켓 범위를 명시한다. 범위 없는 다음 개발 요청은 ESSAY-21 공통 계약 확장까지만 진행한다. 이후 ESSAY-11 분석·ESSAY-15 Vue 화면이 따른다. [assignment 실행 안내](assignment/README.md)에 Python 설치·환경설정·bash run.sh·검사가 있다. 현재 Python 서버는 /health에서 pipelineAvailable:false를 반환하고 자기소개서 API는 아직 404다.

```text
$omo:teammode
AGENTS.md, docs/NODE_MIN_SPEC.md, docs/BACKLOG_V2.md를 읽고 START_OMO_V2.md에 따라 ESSAY-21 구현·검증까지만 진행하고 Jira도 갱신해줘.
```

## 보존된 Next.js v1 설치와 실행

Node.js 22 이상과 pnpm 11을 사용한다. 개발 시 확인한 환경은 Node.js 26.7.0, pnpm 11.18.0이다.

```sh
pnpm install --frozen-lockfile
cp .env.example .env.local
pnpm dev
```

브라우저에서 http://127.0.0.1:3000 을 연다. `.env.local`에 `OPENAI_API_KEY`를 로컬에서 설정하고 `OPENAI_MODEL=gpt-5.6-terra`를 입력한 뒤 서버를 다시 시작한다. 키는 채팅·브라우저 코드·저장소에 넣지 않는다. `.env.example`은 변수 이름과 빈 값만 제공한다.

선택한 제공자는 OpenAI, 모델은 `gpt-5.6-terra`, reasoning effort는 `low`다. [공식 모델 문서](https://developers.openai.com/api/docs/models/gpt-5.6-terra)는 이 추론 설정과 Responses API·구조화 출력을 지원한다. [구조화 출력 문서](https://developers.openai.com/api/docs/guides/structured-outputs)에 따른 JSON schema를 사용한다. 모델명 변경 시 추론 설정과 구조화 출력 호환성을 다시 확인한다.

2026-10-19 15:16 KST 같은 고정 샘플 5개를 수정본으로 재검증했다. 협업 844자, 서점 835자, 긴 경험 963자, 허위 성과 요구 912자의 초안과 정보 부족 보완 안내를 받았다. 원본의 과거 사실 문장을 그대로 선택하고 현재의 해석·미래 계획을 나누도록 바꾸어, 이전에 발견된 인원·발언·후속 행동·시점 추가 문제가 이번 결과에서 재현되지 않았다. 실패한 수정본 6회의 결과도 보존했다. 프로젝트 작성자가 보고서를 확인하고 사실성에 문제가 없음을 최종 승인했다. 상세 평가와 최종 상태는 [QA 기록](docs/qa.md), 선택 이유와 한계는 [작성 방식 결정 기록](docs/decisions/factual-drafting.md)을 따른다. 키나 모델명이 없으면 `500 CONFIG_ERROR`를 반환한다. 운영 앱에 모의 생성 모드는 없다.

## 보존된 Next.js v1 구현 계약과 검사

- `POST /api/drafts`의 요청·응답은 [기술 설계서](docs/TECH_DESIGN.md)를 따른다. 공유 타입과 Zod 스키마는 `src/shared/contracts.ts`에 있다.
- `src/shared/characters.ts`로 CRLF·CR을 LF로 바꾸고 공백·줄바꿈을 포함한 Unicode 코드 포인트를 센다. 초안 성공 범위는 801~1,000자다.
- 범위 밖 초안만 한 번 재작성하며 호출은 최대 2회다. 회당 30초에 취소하고 SDK 자동 재시도는 0회다. 형식 오류·모델 오류·시간 초과·보완 안내에는 추가 재시도가 없다.
- 생성과 재작성 모두 입력 경험에 없는 경력·수상·성과 수치 추가를 금지한다. 이 지시나 길이 검사는 사실성을 보증하지 않으므로 사람의 최종 검토가 필요하다.
- 과거 사실은 원문 문장을 선택해 보존하고, 새 문장은 현재의 해석과 미래 계획으로 한정하도록 지시한다. 재작성에는 실제 길이와 약 900자까지 필요한 증감량을 전달한다. 최종 판정은 여전히 서버의 801~1,000자 검사다.
- 서버 저장·로그인·DB·RAG·MCP는 없고 새로고침하면 화면 내용이 사라진다. OpenAI 요청은 `store: false`를 사용한다.

```sh
pnpm test
pnpm typecheck
pnpm lint
pnpm build
pnpm start
```

Vitest는 실제 API route에 제어 가능한 모델 응답을 주입하여 계약을 검사한다. 모의 테스트와 실제 모델 검증은 구분한다. 상세 결과와 남은 검토는 [QA 기록](docs/qa.md)을 참고한다.

실제 모델 샘플 재실행은 서버를 켠 뒤 새 증거 폴더를 지정한다. 원본 응답을 덮어쓰지 않는다.

```sh
QA_BASE_URL=http://127.0.0.1:3000 \
QA_OUTPUT_DIR=docs/qa-evidence/live-model-revalidation/new-run \
node tests/run-live-samples.mjs --confirm-live-model
```

## 보존된 TypeScript ESSAY-9 공통 기반 확인

LangGraph 1.5.1·LangChain core 1.2.18·Zod 4.6.7을 고정했다. `pnpm test`는 실제 LangGraph 상태 합류와 요청 간 격리, 입력/출력 계약, 병렬 예산·취소, 제공자 경계를 검사한다. 일반 테스트에는 실제 유료 요청이 없다.

기존 OpenAI 키와 모델 설정으로 내장 검색을 사용할 수 있다. 사용자 결정에 따라 요청당 내장 도구 용량 2회를 선예약하고 `max_tool_calls=2`를 전송한다. 모델 최대 6회·회당 30초·조사 45초·요청 180초를 공유한다. 제공자 내부 검색어·페이지 수는 별도 통제하지 않으며, 출처 후보의 공식성 검증은 후속 조사 역할에서 수행한다.

실제 제품 어댑터의 연결을 다시 확인하려면 아래 명령을 사용한다. 1회의 유료 요청을 실행하며 공개 OpenAI 회사/직무만 보낸다. 기존 `.omo/evidence/essay9-providers/live-adapter.json`을 먼저 다른 증거 폴더에 복사해 보존한다.

```sh
RUN_V2_NATIVE_ADAPTER_PROBE=1 pnpm exec vitest run tests/probe-v2-provider.live.test.ts
```

검증 결과와 미검증 범위는 [ESSAY-9 기록](docs/qa-evidence/v2/essay-9/verification.md), 제공자 선택은 [결정 기록](docs/decisions/langgraph-v2.md)을 따른다. Next.js `/api/v2/drafts`·`DRAFT_PIPELINE_VERSION` 추가 계획은 별도 Python·Vue 전환으로 대체했다. 위 검사와 아래 시연은 보존된 Next.js 기준이며 전환판 검증이 아니다. 제출 서비스의 설치·bash run.sh·시연은 구현 후 assignment/README.md에서 검증해 제공한다.

## 보존된 Next.js v1 3분 시연

1. 0:00~0:30 — 문제와 목적을 설명하고 네 입력에 실제 경험을 작성한다.
2. 0:30~1:30 — 생성 버튼을 누르고 진행 상태를 보여 준다. 길이 재작성까지 최대 약 60초가 걸릴 수 있다.
3. 1:30~2:20 — 요청 당시 경험과 초안을 비교하고 801~1,000자 표시를 확인한다. 없는 사실이 들어갔는지 검토한다.
4. 2:20~2:45 — 초안을 편집하고 실시간 글자 수·범위 경고를 보여 준다. 현재 내용을 복사해 붙여넣는다.
5. 2:45~3:00 — 보완 안내·실패 후 입력 유지와 현재 한계를 설명한다. 키가 없다면 설정 오류와 모의 테스트 결과만 시연하고 실제 생성으로 소개하지 않는다.

2026-10-19 실제 모델 고정 샘플 5개 검증과 프로젝트 작성자의 최종 사실성 확인을 마치고 [ESSAY-7](https://kmskojb.atlassian.net/browse/ESSAY-7)을 완료 처리했다.
