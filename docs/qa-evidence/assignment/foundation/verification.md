# ESSAY-19 Python 공통 기반 검증

검증일: 2026-10-20. 사용자 지정 범위는 ESSAY-19 구현·검증이다. **판정: 완료 조건8개 통과.** Jira ESSAY-19를 완료 처리하고 후속 티켓은 할 일로 유지한다.

| 검사 | 실제 결과 | 증거 |
| --- | --- | --- |
| Python 공통 계약·예산·LangGraph·SDK wire·실제 MCP·lifespan | 131개 통과, 유료1개 기본 skip | [독립 보고서](checks/verification.md), [최종 원자료](leader/pytest.txt) |
| JS 문자·근거 위치·HTTP 취소/오류 | 12개 통과 | [원자료](leader/js.txt) |
| 타입·스타일·포맷 | 기반/테스트32개 파일 타입 진단0, Ruff/format 통과; 제품17·테스트15개 no-excuse 위반0 | [최종 검사](leader/automated-result.json), [타입 원자료](leader/types.txt), 팀 인계 |
| 실제 Vue 기반 화면 | 5개 통과; 제품 자기소개서 화면은 아님 | [보고서](browser/README.md), [화면](browser/vue-foundation.png) |
| 깨끗한 설치·실행·종료 | CPython3.12.15 신규 설치·고정 환경 설치, 실행5개·설치 중단3개 통과 | [실행 보고서](runtime/README.md) |
| 최종 소스 localhost smoke | health 재사용·404 제어3개·실제 MCP 자식·SIGTERM 정리 통과 | [결과/코드 해시](leader/runtime-result.json) |
| 실제 설정 모델 | 구조화 출력1회 + 실제 MCP 검색1회 통과, 추가 유료 실행 없음 | [비밀 제외 결과](checks/live-84299595-7260-43ce-8596-7a6276699470.json) |
| 보존 | Downloads 원본46개·기존 보호 파일441개 해시 동일 | [보존 확인](leader/preservation.json) |

## 작은 실제 모델·검색 검사

2026-10-20 15:51:26~15:51:39 KST, 기존 `gpt-5.6-terra`를 사용했다. 공개 입력은 기업 OpenAI·직무 Software Engineer뿐이다. 구조화 출력은 기업/직무 일치와 null 선택값을 확인했고 1.680초, 입력97/출력23토큰이었다. 실제 stdio MCP 조사 응답은 스키마/요청 상관관계 검증을 통과했고 11.300초, 입력13320/출력1197토큰이었다. 조사 모델 예약1회·내장용량 예약2회와 실제 보고된 도구1회를 구분한다. `store:false`, `max_tool_calls:2`, 자동 재시도0, 모델당30초를 적용했다. 전체 opt-in 검사1개가 13.40초에 통과했다.

실제 실행 위치는 `assignment/`이며 명령은 다음과 같다. 환경변수 파일을 셸에서 실행하지 않고 프로세스 안에서 키/모델 두 변수만 읽었다.

```sh
env -i PATH=/usr/bin:/bin LANG=en_US.UTF-8 PYTHONDONTWRITEBYTECODE=1 ESSAY_LIVE_COMPATIBILITY=1 /Users/jay/Projects/essay-service/assignment/.venv/bin/python -m pytest tests/test_live_compatibility.py -q -s
```

이 검사는 OpenAI Responses·구조화 출력·web_search·MCP 호환성 증거다. 출처의 공식성이나 자기소개서 결과의 품질을 검증한 것은 아니다. 제공자 원문·검색 본문·전체 프롬프트·키는 기록하지 않았다.

## 구현과 후속 작업의 경계

제공 프로젝트의 FastAPI lifespan·의존성 주입·실제 stdio MCP·LLM 어댑터 구조를 활용해 `assignment/`에 공통 기반을 이식했다. 루트 Next.js v1과 TypeScript ESSAY-9는 보존한다.

| 파일/모듈 | 구현 기능 |
| --- | --- |
| `agent/contract_input.py`, `contract_evidence.py`, `contract_results.py`, `contracts.py` | 네 필수 입력·선택 공고, ready/needs_input/error, 출처·근거·검토 결과의 Pydantic 계약 |
| `agent/state.py`, `deps.py` | 요청별 ID·입력 스냅샷·상태·예산, 타입 있는 의존성, 실제 LangGraph 주입 노드의 상태 검사 |
| `agent/budget.py`, `limits.py` | 병렬 예약, 정상4/최대6회·출력예약18000, 30/45/180초, 취소·무환불·후속 호출 차단 |
| `agent/openai_llm.py`, `provider_schema.py`, `response_wire.py`, `providers.py` | 단일 Responses 구조화 출력, strict 스키마·SDK 응답 재검증, 재시도0·오류 정규화 |
| `agent/research.py`, `mcp_client.py`, `mcp_server.py` | 기업·직무·공고만 투영, 별도 trusted 메타데이터, 실제 MCP 조사 후보·상관관계·timeout·연결 수명 |
| `agent/settings.py`, `server.py` | 서버 전용 키, 재사용 SDK/MCP 생성·정리, tracing 비활성, SQLite 미사용, 정직한 health |
| `web/foundation.mjs` | LF·코드 포인트 글자 수/근거 위치, 195초 클라이언트 기한·중단·단일 요청 |
| `pyproject.toml`, `uv.lock`, `.python-version`, `requirements.txt` | CPython3.12 계열·실제 호환된 의존성 고정 |
| `run.sh`, `.env.example`, `README.md` | 빈 키/모델 예시, 고정 설치·시작·소유 프로세스 종료·실행 안내 |

기본 서버는 `GET /health`만 제품 기능으로 노출하며 `pipelineAvailable:false`다. `/api/drafts`, `/chat`, `/chat/stream`은 404다. 네 업무 역할·전체 그래프·자기소개서 API·Vue 제품 화면은 ESSAY-10~15의 후속 구현이다. 기존 원본 graph·fake·화면 파일은 현재 서버에서 실행하지 않는다.

조사 결과의 `verification: unverified`는 후보 자료라는 뜻이다. 공식 기업/채용 플랫폼 확인과 출처 구절 검증은 ESSAY-10의 책임이다. 실제 MCP나 검색 성공을 공식성·자기소개서 사실성·품질 통과로 보고하지 않는다. 내부 검색어·페이지·바이트 수는 독립 통제하지 않는다.

## 증거와 재현

- [완료 기준](acceptance.md): 실행 전 범위와 공식 SDK/MCP 문서.
- [Python 자동 검사](checks/verification.md): 완료 조건8개의 구체적 시나리오·명령·JUnit 결과·실패/수정 매핑. 기본 실행은 유료 검사를 건너뛴다.
- [설치·실행·종료](runtime/README.md): 깨끗한 고정 설치, 실행5개·설치 중단3개 시나리오, DB 불변·포트 충돌·소유 자식 정리. 당시 코드 해시와 이후 포맷 변경을 구분한다.
- [실제 Vue 기반 검사](browser/README.md): Vue3.5.44의 reactive 입력, 한글/CRLF/이모지·결합문자/ZWJ 근거 위치, 실제 HTTP 중단/422. 제품 화면이 아닌 재사용 유틸리티 시험 화면이다.
- [최종 코드 실행](leader/runtime-result.json): 최종 제품 소스 해시에 대응하는 별도 localhost smoke. 이후 변경은 test typing/문서뿐이며 제품 코드는 동결했다.

재현: `assignment/`에서 `uv sync --frozen`, `uv run --frozen pytest`, `node --test tests/test_foundation.mjs`, `uv run --frozen basedpyright`, `uv run --frozen ruff check .`, `uv run --frozen ruff format --check .`. Ruff/type 검사 범위는 새 기반과 테스트이며 보존된 legacy 모듈은 제외한다. 유료 검사는 README의 명시적 opt-in 명령으로만 실행한다.

## 발견·수정 이력

실패 증거를 성공 결과로 덮어쓰지 않는다. 처음 계약 검사11개 실패에서 공고 타입·URL 포트·범위를 넘은 인용 offset 검증을 보강했다. SDK 호환 검사에서 실제 strict 스키마, Responses 결과 값, hosted 검색 강제 사용과 출처 포함을 확인했다. MCP 검사에서는 FastMCP 프로토콜 메타데이터 허용 범위와 안전한 오류 코드 매핑, upstream 시간 초과 후 예산 차단을 수정했다.

공유 MCP의 기본 stdio keep_alive 동작 때문에 단순 context 종료만으로 자식 프로세스 정리가 보장되지 않았다. 명시적 close와 shielded 정리로 수정하고 같은 프로세스에서 재검증했다. 실제 SDK의 환경변수 base URL 상속을 막기 위해 공식 endpoint를 명시했다. 마지막 malformed SDK 응답과 실제 MCP 프로토콜 시간 초과 사례의 red 결과도 별도 보존한다.

실행 harness의 sandbox 프로세스 조회 거부·즉시 reap 판정·uvicorn 포트 충돌 종료 코드 가정은 제품 실패와 구분했다. 최종 판정은 실제 비정상 종료와 기존 listener 보존, 제한된 reap 관찰을 사용한다. 195초를 실제로 기다린 브라우저 검사는 수행하지 않았으며 timer/body 취소는 결정적 JS 검사로 확인한다.

## 보존·제한

Downloads 원본46개와 루트 `src/`·`tests/`·Node 설정·기존 샘플·QA·ESSAY-18 증거를 포함한 보호 파일441개의 해시 불변을 확인했다. 원본 `.env`·가상환경·DB는 복사하지 않았다. 키·경험·초안·전체 프롬프트는 공개 증거에 저장하지 않는다. 이번 작은 실제 검사는 공개 기업·직무만 사용한다.

ESSAY-17의 기존5개 실제 자기소개서 재검증·기업2곳 공식 자료·작성자 새 승인과 ESSAY-20 제출 검증은 미실행이다. ESSAY-1~7·9·18의 완료는 유지하며 후속 티켓을 자동 착수하지 않는다.

## Jira와 팀 인계

[Jira 읽기 확인](jira-sync.json): 총20개 티켓·에픽 하위12개·v2 의존관계16개 유지, ESSAY-19 완료 조건8개 체크/완료, ESSAY-8 진행 중, ESSAY-10~17·20 할 일. 시작 코멘트10020·완료 코멘트10021과 실제 상태를 확인했다. 담당자·스프린트·기한·의존관계는 변경하지 않았다.

OMO 팀은 native MultiAgentV2로 공통 기반·독립 회귀·실행/문자 경계를 나눴다. [공개 API](team/artifacts/api-contract.md), [구현 인계](team/artifacts/core-handoff.md), [검증 인계](team/artifacts/checks-handoff.md), [실행 인계](team/artifacts/launch-text-boundary.md), [보존 팀 상태](team/team.json)를 인계한다. 완료 기록7개 파일의 원본/복사 해시 일치를 확인한 뒤 활성 팀 상태를 삭제했다. V2에는 런타임 archive 기능이 없어 durable 상태 보존만을 의미한다. A/B의 마지막 응답에는 모델 용량 오류가 있었지만 인계 문서·수정·검증 결과는 이미 저장됐고 메인이 확인했다.

실행 서버/자식·소유 브라우저·C의 임시 설치환경은 종료/정리했다. 개발용 assignment/.venv는 보존한다. 이번 요청에서는 Git 커밋·푸시를 수행하지 않았다.
