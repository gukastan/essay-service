# 자소서 서비스 개발 지침

이 디렉터리는 자소서 서비스 전용 개발 프로젝트다. 3일 MVP인 v1은 ESSAY-1~7과 작성자 사실성 검토까지 완료했다. v2는 ESSAY-9 공통 기반을 구현했으며 네 역할·API·화면 통합은 후속 작업이다. 사용자에게는 한국어로 설명한다.

## 먼저 읽을 자료

1. `docs/PRD.md`: 제품 범위와 사용자 관점의 완료 기준.
2. `docs/TECH_DESIGN.md`: API, 글자 수, 재작성, 오류, 테스트 계약.
3. v2 작업 시 `docs/PRD_V2.md`, `docs/TECH_DESIGN_V2.md`, `docs/decisions/langgraph-v2.md`, `docs/BACKLOG_V2.md`, `docs/qa-v2.md`.
4. 해당 버전의 백로그에 연결된 Jira 본문과 실제 의존관계. ESSAY-1~7은 완료된 v1 기준선이다.
5. 팀 개발을 시작하라는 요청을 받은 경우 v2는 `START_OMO_V2.md`, 과거 v1 요청문은 `START_OMO.md`.

현재 문서와 최신 사용자 지시를 확인하고 작업한다. 문서 파일이 존재한다는 이유만으로 개발이나 Jira 상태 변경을 시작하지 않는다. 사용자가 시작을 요청하면 계획 제안만으로 끝내지 말고 구현과 검증까지 진행한다.

## v1 구현 범위와 보존 계약

- 새 프로젝트의 기본 기술은 Next.js + TypeScript다. 앱 구성과 의존성 설치는 ESSAY-1에서 수행한다.
- 필요한 프로젝트 파일을 이 루트에 추가한다. 기존 문서가 있다는 이유로 폴더를 삭제하거나 덮어쓰지 않는다.
- 기업명·직무·문항·경험 입력 → 실제 모델 생성 → 길이 검증 → 편집·복사 흐름을 구현한다.
- 유효한 초안은 공백·줄바꿈 포함 801~1,000자다. 800자 이하 또는 1,000자 초과면 한 번 재작성한다.
- 요청당 모델 호출은 최대 2회, 회당 30초다. SDK 자동 재시도를 끈다.
- 없는 경력·수상·성과 수치를 추가하지 않는다. 정보 보완 응답에는 초안 길이 규칙을 적용하지 않는다.
- 로그인·DB 저장·RAG·MCP·서비스 내부 멀티에이전트·서비스 자체 Jira 자동 연동은 추가하지 않는다.
- 모델 제공자·모델명은 ESSAY-1에서 확정한다. 실제 자격증명이 없으면 독립 작업을 진행하되 실제 모델 검증은 미검증으로 남긴다.

## v2 구현 범위

- 명세는 `docs/PRD_V2.md`와 `docs/TECH_DESIGN_V2.md`다. v1의 서비스 내부 멀티에이전트 제외 및 최대 2회 제한은 v2에 적용하지 않는다.
- 기업·직무 조사와 경험·문항 분석을 병렬로 실행하고, 작성·검토를 연결한다. 수정은 작성·검토 각각 한 번만 추가한다.
- 정상 4회, 최대 6회 모델 호출, 호출당 최대 30초, 조사 전체 45초, 요청 전체 180초, 자동 재시도 0을 지킨다.
- 2026-10-19 사용자 결정에 따라 현재 OpenAI 키의 내장 검색을 사용한다. 요청당 내장 도구 용량 2회를 선예약하고 `max_tool_calls=2`로 제한한다. 내부 검색어·페이지 수·응답 바이트를 직접 통제한다고 주장하지 않는다. 별도 주입 검색/직접 읽기 경로의 2회/3회 카운터와 구분한다.
- 공식 자료 또는 명시된 사용자 제공 공고와 경험 원문에 근거한다. 문항·직무 요건을 일반 인재상보다 우선한다. 기업 식별·직무 근거가 없으면 보완을 요청한다.
- `/api/v2/drafts`와 `DRAFT_PIPELINE_VERSION`을 새로 구현하며 기본 v1을 유지한다. 구현 전 존재한다고 가정하지 않는다.
- 로그인·DB·벡터 RAG·MCP·서비스의 Jira 자동 연동은 여전히 범위 밖이다.
- 기존 5개 샘플·v1 QA·run-7 승인 기록을 보존한다. v2 QA는 별도 문서에 기록하고 작성자의 새 확인 후 완료한다.

## 협업과 소유권

사용자가 OMO 팀 개발을 요청하면 설치된 `omo:teammode` 지침과 실제 사용 가능한 도구를 확인해 적용한다. 메인이 조율하고 제품 코드 편집은 구현 에이전트에 위임한다.

- 프런트엔드: ESSAY-2·3, `src/app/page.tsx`, `src/app/globals.css`, `src/components/essay/`.
- 백엔드: ESSAY-4·5, `src/app/api/drafts/`, `src/server/`, 관련 단위 테스트.
- QA: ESSAY-6·7, `tests/`, 샘플, `docs/qa.md`. 제품 코드 결함은 구현 담당자에게 전달한다.
- 메인: ESSAY-1 총괄, 공통 계약·설정·통합·README 조율. 실제 공통 파일 편집 담당자는 한 명만 지정한다.

위 배정은 v1 기록이다. v2는 `docs/BACKLOG_V2.md`의 작업·파일 소유권을 따른다. V2-01 공통 계약 이후 조사·분석·화면을 병렬로 진행할 수 있으며, 작성·검토·통합·QA 의존관계를 지킨다. 실제 개발 에이전트와 제품 안의 네 역할을 구분한다.

모든 작업자는 다른 작업자가 함께 수정 중임을 인지하고 다른 사람의 변경을 되돌리지 않는다. 공유 파일은 소유권을 순차적으로 넘기거나 설치된 팀 지침에 따라 격리해 충돌을 방지한다.

## 검증과 기록

- 실제 수행한 검사와 결과만 보고한다. 모의 응답 테스트, 실제 모델 검증, 실제 브라우저 검증을 구분한다.
- 800·801·1,000·1,001자 경계, 재작성 횟수, 입력 오류, 모델 오류·시간 초과를 확인한다.
- 코드의 글자 수 계산과 사람이 검토하는 사실성 평가는 별개다.
- 프로젝트 작성자의 최종 사실성 확인 전에는 ESSAY-7을 완료로 처리하지 않는다.
- 실제 API 키는 브라우저 코드·저장소·보고서에 기록하지 않는다. 필요한 환경변수 이름만 `.env.example`과 README에 문서화한다.
- 구현이 끝나면 README에 실제 실행·검증 방법과 3분 시연 순서를 갱신한다.
- Jira 쓰기는 사용자에게 승인받은 개발 범위에서 메인만 수행하고, 각 작업자는 메인에게 변경 파일·검증 결과·남은 문제를 보고한다.

<!-- BEGIN:nextjs-agent-rules -->

## This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` (resolved from this file's directory; in monorepos the `next` package may not be visible from the repo root) before writing any code. Heed deprecation notices.

This block is written and re-added by `next dev` — verify at `node_modules/next/dist/server/lib/generate-agent-files.js`. Removing it from a diff only re-creates the uncommitted change; committing it with your work keeps the tree clean.

<!-- END:nextjs-agent-rules -->
