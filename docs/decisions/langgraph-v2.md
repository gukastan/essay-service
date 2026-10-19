# 결정: LangGraph를 이용한 네 역할 워크플로

- 날짜: 2026-10-19
- 상태: 채택된 v2 개발 방향, ESSAY-9 공통 기반 구현·검증 완료
- 사용자 결정: 기업·직무 조사 + 경험·문항 분석 + 작성 + 검토를 연결하고 작업문서와 Jira 티켓을 추가한다.
- 관련: [v2 PRD](../PRD_V2.md), [기술 설계](../TECH_DESIGN_V2.md), [백로그](../BACKLOG_V2.md)

## 배경

v1은 네 입력을 직접 OpenAI 모델에 전달하고 길이 초과/미달일 때 한 번 재작성한다. 실제 모델 5개 샘플의 사실성 문제를 수정하고 작성자 확인을 받아 ESSAY-7까지 완료했다. 기업 공식 자료 조사와 서비스 내부 멀티에이전트는 v1 범위 밖이었다.

이제 회사 이름과 직무명만 전달하는 수준에서 나아가, 실제 직무 요구와 확인 가능한 기업 정보를 사용자 경험에 연결할 필요가 있다.

## 결정

LangGraph JS로 정해진 네 역할과 상태 전이를 구성한다. 조사와 경험 분석은 병렬로 수행하고, 작성 → 검토 → 필요 시 한 번 수정 → 재검토로 종료한다. 네 역할은 동일 모델을 공유해도 되며 각각의 지시·구조화 출력·근거 범위를 분리한다.

기업 인재상은 공식 근거가 있을 때 보조적으로 활용한다. 문항과 실제 직무 요건을 우선한다. 사용자가 제공한 공고 본문은 별도 출처 등급으로 허용한다. 검색 제공자·의존성 버전과 V2-01의 실제 호환성 검사 결과는 아래에 기록했다.

## 선택 이유와 비용

고정 흐름은 합류·보완·실패·수정 횟수를 코드와 테스트로 확인할 수 있다. 역할별 출력을 분리하면 어느 단계에서 사실이나 근거가 누락됐는지 추적하기 쉽다. [공식 LangGraph 문서](https://docs.langchain.com/oss/javascript/langgraph/workflows-agents)의 병렬 처리와 평가·수정 워크플로를 참고한다.

정상 4회, 최대 6회 모델 호출과 검색 비용이 추가된다. 지연·비용·사실성이 개선됐다는 주장은 검증 전에는 하지 않는다. 검토 모델도 잘못 판정할 수 있어 원문/출처의 결정적 검사와 사람의 최종 확인을 유지한다.

현재의 원문 사실 문장 보존 규칙을 유지한다. 회사 정보가 있더라도 사용자의 과거 행동·성과를 확장할 근거가 되지 않는다.

## 적용과 제외

기존 API와 QA를 보존하고 새 v2 API를 기능 설정으로 활성화한다. 새 호출 상한은 v2에만 적용한다. 로그인/DB, 벡터 RAG, MCP, 무제한 에이전트 토론, 제품의 Jira 자동화는 도입하지 않는다.

개발 에이전트(OMO 팀)와 서비스 안에서 실행되는 네 역할은 서로 다른 개념이다. 문서를 읽는 것만으로 개발·배포·유료 검증을 수행했다고 간주하지 않는다.

## 구현 시 확정·기록할 항목

ESSAY-9에서 LangGraph 1.5.1·LangChain core 1.2.18·Zod 4.6.7을 고정하고 모델/검색 연결을 확인했다. 실제 StateGraph 실행·전체 회귀·production build 증거는 [ESSAY-9 기록](../qa-evidence/v2/essay-9/verification.md)에 있다. 호스팅의 180초 요청 허용은 배포 환경을 정하는 ESSAY-14에서 확인하고, 전체 역할별 지연·토큰·검색량·가능한 비용과 작성 품질은 ESSAY-17에서 검증한다.


## ESSAY-9 제공자 호환성 결정 (2026-10-19)

모델 기반은 기존 `openai@7.39.0` Responses API, `OPENAI_MODEL=gpt-5.6-terra`, reasoning `low`를 유지한다. 필요한 서버 설정은 `OPENAI_API_KEY`, `OPENAI_MODEL`이다. 현재 키 존재와 실제 요청 성공을 확인했으며 키 자체는 기록하지 않았다. SDK 자동 재시도는 클라이언트와 요청 모두 0, `store:false`, 역할별 출력 상한 3,000/3,000/4,000/2,000 토큰을 적용한다. 호출별 signal/timeout은 공유 ExecutionBudget에서 받아 모델 6회·30초, 조사 45초, 요청 180초를 넘는 새 호출을 차단한다. v1 구현은 변경하지 않는다.

교체 가능한 `ModelProvider`, `SearchProvider`, `PageReader`와 예산을 적용하는 `createResearchTools`를 정의했다. 검색 입력은 company/role 두 필드로 다시 구성하므로 넓은 요청 객체를 전달해도 경험·문항을 전송하지 않는다. 검색 결과는 공식 검증 완료 자료가 아닌 후보 자료다. 페이지 reader의 DNS/IP·리다이렉트 안전성, 1 MiB 응답 제한과 공식성 확인은 ESSAY-10 구현 책임이며 이번 기반에는 검증되지 않은 기본 네트워크 reader를 연결하지 않는다. 검색 기본 전략은 사용자 승인에 따라 OpenAI native web_search로 확정했다. 별도 서버 페이지 reader는 이번 기반에 연결하지 않는다.

OpenAI strict JSON은 모든 필드를 요구하므로 선택 날짜·URL을 포함한 도메인 ResearchResultSchema를 그대로 보낼 수 없었다. `provider-schemas.ts`의 ResearchModelOutputSchema는 선택 항목을 필수 nullable로 표현하고 `normalizeResearchModelOutput`으로 null을 생략한 도메인 계약을 다시 검증한다. 다른 세 역할은 기존 스키마를 그대로 변환한다. 이는 wire 표현만 바꾸며 사용자 API의 선택 필드를 바꾸지 않는다. 실제 SDK helper 변환 및 정상화 회귀 검사를 수행했다. 역할별 실제 프롬프트/전체 도메인 출력의 유료 검증은 후속 작업이다.

### 작은 실연결 결과

실행: `RUN_V2_PROVIDER_PROBE=1 node tests/probe-v2-provider.mjs` (2회), 이어서 같은 명령에 `--combined` (1회). 기본 실행은 환경 플래그 없으면 요청 없이 종료한다. 총 3회, 자동 재시도 0, 공개 OpenAI 회사/소프트웨어 엔지니어 직무만 검색했다. 원본 사용자 경험이나 문항은 전송하지 않았다. 모든 요청은 max_output_tokens=400, timeout=30초였다.

| 검사 | 관찰 | 지연 | 입력/출력 토큰 |
| --- | --- | --- | --- |
| strict JSON | completed, `{"ok":true}` | 2,417ms | 33 / 13 |
| native web_search | completed, 공식 채용 URL, search action 1개 | 3,315ms | 8,589 / 52 |
| strict JSON + native web_search | completed, `url` JSON, search action 1개 | 3,492ms | 8,702 / 63 |

두 검색 검사는 `tool_choice:required`, `max_tool_calls:1`, allowed_domains=`openai.com`을 사용했다. 각각 보고된 query 1개와 source URL 18개, open_page action 0개를 관찰했다. source 수는 페이지 읽기 수를 의미하지 않는다. 검색 내부의 크롤링/페이지 바이트 수는 노출되지 않아 계수할 수 없다. 비용 금액은 청구 자료가 없어 추정하지 않았으며 위 토큰 수와 보고된 도구 호출만 기록했다. 3회 결과만으로 성능·비용 일반화를 하지 않는다.

원본 증거: `.omo/evidence/essay9-providers/live-probe.json`, `live-combined.json`. 유료 확인을 다시 실행하면 추가 비용이 발생하므로 별도 의도 없이 기본 test에 포함하지 않는다.

### 검색 제공자 선택 및 사용자 승인

[공식 web search 문서](https://developers.openai.com/api/docs/guides/tools-web-search)와 설치 SDK `src/resources/responses/responses.ts`를 확인했다. SDK의 `max_tool_calls`는 응답 안의 모든 built-in tool call 합계 상한이다. `search` action에는 복수 `queries`가 올 수 있고 query가 생략될 수도 있다. `open_page`, `find_in_page`도 같은 도구 계열이다. 독립 query 수·페이지 수·페이지당 바이트 상한을 설정하는 인자는 없다. 따라서 이번 성공은 모델의 검색 지원 증거이며 기존 내부 검색 2회/페이지 읽기 3회/1 MiB 계약을 보장하는 증거가 아니다.

1. 기존 키로 native search를 선택하면 strict JSON과 검색을 조사 모델 1회 안에서 실행할 수 있다. 다만 독립 검색/페이지 상한을 built-in tool-call 합계 상한 및 관찰 가능한 action 계수로 명시적으로 변경해야 한다. 호출 후 query 수를 검사하는 것은 이미 실행된 비용을 막지 못한다. 별도 서버 페이지 reader를 함께 쓰더라도 hosted search 내부 읽기를 통제하지 못한다.
2. 현재 독립 상한을 유지하려면 숨은 검색 반복이 없는 외부 검색 API를 선택하고, 서버에서 검색 요청 2회와 안전한 페이지 요청 3회를 각각 예약해야 한다. 공급자 선택·자격증명·작은 실연결 확인이 추가로 필요하다. 현재 `.env.local`에는 외부 검색 자격증명이 없다. 이 경로의 검색 API는 모델 생성 호출과 별개라 정상 4회 모델 예산을 유지할 수 있다.

사용자는 현재 OpenAI 키를 사용하고 내부 검색/페이지 횟수 대신 native tool-call 한도로 변경하도록 승인했다. `native-provider.ts`의 createOpenAINativeResearchProvider를 기본 조사 제공자 기반으로 채택한다. 요청 전체에서 조사 모델 1회와 hosted tool-call 용량 2회를 원자적으로 예약하고 `max_tool_calls:2`를 보낸다. 오류/취소/실제 도구 미사용분도 환급하지 않아 두 번째 native 조사 요청을 시작하지 않는다. 일반 모델 어댑터에는 도구가 없다. 기존 외부 SearchProvider/PageReader 인터페이스와 검색2/페이지3 예약은 교체 경로용으로 남으며 native 내부 계수라고 보고하지 않는다.

Native 입력은 company/role와 선택 공고 URL/본문만 투영한다. 경험/문항은 모델 도구 문맥에 보내지 않는다. 검색어에 company/role만 사용하도록 지시하지만 hosted 모델 내부 query 생성은 서버에서 사전 가로채지 못한다. 공고 본문과 웹 자료의 명령은 신뢰하지 않는 데이터로 지시한다. 반환된 action/query/source URL, reported tool-call 수 및 예약량은 `verification:unverified`인 제공자 관찰값이다. 공식성/인용/직무 근거의 실제 판정은 ESSAY-10이며 이 기반에서 완료를 주장하지 않는다. 내부 쿼리 수, 페이지 열람 수, 페이지당 바이트와 hosted DNS/redirect 처리는 독립적인 서버 상한/검증 대상이 아니다.

설치 SDK7.39의 HTTP 요청 타입에는 max_tool_calls가 누락되어 있지만 같은 파일의 WebSocket ResponseCreate 타입과 [현재 공식 HTTP API 문서](https://developers.openai.com/api/reference/resources/responses/methods/create)에 정의되어 있다. 해당 필드를 명시한 intersection payload 타입으로 직렬화한다. 타입 강제 단언이나 ts-ignore는 사용하지 않았다. 실제 API 응답이 max_tool_calls=2를 반환하는 것도 아래 실연결에서 확인했다.

추가 승인된 마지막 실연결은 `RUN_V2_NATIVE_ADAPTER_PROBE=1 pnpm exec vitest run tests/probe-v2-provider.live.test.ts`로 제품 어댑터와 실제 ExecutionBudget을 통과했다. 2026-10-19T08:30:05.936Z 시작, 4,700ms, 입력 8,626/출력 97토큰, JSON 공식 채용 URL 반환, reported search action1/query1/source18, reserved hosted2/model1, serverToolCallLimit2, retries0, max_output_tokens3000이었다. 증거는 `.omo/evidence/essay9-providers/live-adapter.json`, `live-adapter-run.txt`다. 총 유료 확인은 네 번(기존3+제품 어댑터1)이며 기본 단위검사는 paid traffic을 실행하지 않는다. 호스팅180초 지원·실제 네 역할 프롬프트·전체 v2 QA는 이 검사로 검증한 것이 아니다.
