# Python 자기소개서 역할 모듈과 Vue 화면

후속 구현 기준은 [A~J 노드별 최소 명세](../docs/NODE_MIN_SPEC.md)다. [ESSAY-21](https://kmskojb.atlassian.net/browse/ESSAY-21) 공통 계약과 [인계](../docs/FLOW_CONTRACTS.md)를 바탕으로 ESSAY-11 B/C 분석, ESSAY-12 D/E/I 작성, ESSAY-13 F 평가, ESSAY-15 Vue 화면을 독립 구현·검증했다. [병렬 개발과 완료 경계](../docs/PARALLEL_DEVELOPMENT.md)를 따른다. D의 최소 계획 조립은 코드로 처리한다. 신뢰할 조사 출처가 없는 경우 정상3회, 조사 포함 정상4회/최대6회·공통 수정1회를 유지한다. 내부 전략 디테일은 후속 설계다.

현재 구현은 Pydantic 계약, 근거/버전 검사, 공통 D/I 수정 예약, 요청별 상태·예산, 모델/MCP 연결, ESSAY-10 조사, B/C 분석, D/E/I 작성, F 평가, Vue 화면·제한된 프록시, ESSAY-14 LangGraph·FastAPI POST `/api/drafts` 연결이다. [QA](../docs/qa-v2.md)는 통제 입력·실제 stdio MCP·실제 브라우저·유료 모델 검증 범위를 구분한다. `GET /health`는 `pipelineAvailable: true`를 반환한다. 원본 `/chat`, `/chat/stream`은 제품 경로가 아니다.

결과는 `ready`(모든 기준 충족·초안 포함), `review_needed`(작성 후 기준 미충족·마지막 초안과 사유 포함), `needs_input`(작성 전 필수 경험 부족·초안 없음), `error`(운영/입력 오류)로 구분한다. 두 초안 결과 모두 HTTP 200이며 `review_needed`를 검토 통과로 표시하지 않는다. 문장만 수정할 때는 부분 수정, 경험 선택·주장·구성을 바꿔야 할 때는 재계획을 선택하며 두 경로는 수정 기회 1회를 공유한다.

`web_chat.html`·`web_demo_server.py`는 ESSAY-15의 Vue 제품 화면·프록시로 변경했다. 원본 화면 검증은 ESSAY-18 기록에 별도로 남아 있다. `sh/`와 `doc/`의 과거 자료, 루트 Next.js와 Downloads 원본은 별도로 보존한다.

## Mac 설치

Python은 uv가 관리하는 독립 3.12 환경을 사용한다. macOS 시스템 Python이나 원본 가상환경에 패키지를 설치하지 않는다. uv가 없으면 공식 설치 스크립트를 내려받아 확인한 뒤 실행한다(관리자 권한 불필요).

```bash
curl -LsSf https://astral.sh/uv/install.sh -o /tmp/essay-uv-install.sh
less /tmp/essay-uv-install.sh
sh /tmp/essay-uv-install.sh
export PATH="$HOME/.local/bin:$PATH"
uv --version
uv python install 3.12
cd /path/to/essay-service/assignment
uv sync --frozen
```

`uv.lock`과 `pyproject.toml`이 설치 계약이다. 잠금 파일을 다시 만들지 않고 설치한다. 기본 환경은 `assignment/.venv`다. 깨끗한 환경에서 확인하려면 `UV_PROJECT_ENVIRONMENT`에 새로운 절대 경로를 지정한다. 이후 실행·검사에도 같은 변수를 유지한다.

```bash
export UV_PROJECT_ENVIRONMENT="$(mktemp -d /tmp/essay19-env.XXXXXX)/venv"
uv sync --frozen
```

## 설정과 실행

키 없이도 실제 MCP stdio 연결과 기반 상태를 확인할 수 있다. 시작이나 health 조회는 유료 모델 요청을 보내지 않는다. 실제 호출을 선택할 때에만 `OPENAI_API_KEY`와 `OPENAI_MODEL`을 서버 프로세스 환경 또는 **assignment/.env**에 설정한다. `.env.example`은 빈 값의 이름 예시다. `.env`는 셸로 source하지 않으며 서버 설정 파서가 읽는다. 루트 `.env.local`이나 Downloads의 `.env`를 이 실행기가 읽거나 복사하지 않는다. 키를 브라우저, 명령 출력, Git, QA 증거에 넣지 않는다. 설정은 서버 수명 시작 시 읽으므로 변경한 뒤에는 서버를 종료하고 다시 시작한다.

```bash
bash run.sh
```

기본 주소는 `http://127.0.0.1:8001`이다. 다른 로컬 포트는 `ESSAY_PORT=8101 bash run.sh`, 임시 포트는 `ESSAY_PORT=0 bash run.sh`로 실행한다. 임시 포트는 uvicorn 시작 로그에서 확인한다. `ESSAY_PORT`는 셸 환경변수이며 `.env` 설정이 아니다. 외부 인터페이스에 바인딩하는 옵션은 없다.

종료는 실행 터미널에서 Ctrl-C다. 백그라운드 실행 시 시작할 때 기록한 자신의 PID에만 `kill -TERM "$launcher_pid"`를 보낸다. 실행기는 Python 프로세스로 교체되므로 같은 PID가 서버다. SIGINT/SIGTERM은 서버 lifespan과 MCP 자식 정리를 거친다. 설치 중 종료 신호를 받으면 자신이 시작한 uv 설치 프로세스만 정리하고 130(SIGINT)/143(SIGTERM)으로 종료한다. 포트가 점유돼 있으면 비정상 코드로 종료하며 기존 서비스를 중단하지 않는다. DB 삭제, 포트 점유 프로세스 검색·종료, 자동 재시작은 하지 않는다.

외부 LangChain/LangSmith 추적은 실행기와 서버에서 비활성화한다. 경험·초안용 SQLite/checkpointer는 연결하지 않는다. 이전 기준선의 로컬 `session.db`가 있어도 이 경로는 사용하지 않는다. access log를 끄고 요청 원문이나 전체 프롬프트를 health 응답에 넣지 않는다.

## 기반 확인

다른 터미널에서 실행한다. 두 번째 요청은 현재 API의 입력·설정 상태를 확인한다. 아래처럼 유효한 입력과 모델 키가 없으면 `500 CONFIG_ERROR`가 예상된다. 실제 생성에는 `assignment/.env` 설정과 직접 한 행동이 드러나는 경험이 필요하다. 공고 URL·본문은 선택 입력이다.

```bash
curl --fail --silent http://127.0.0.1:8001/health
curl --silent --output /dev/null --write-out '%{http_code}\n' \
  -H 'Content-Type: application/json' \
  -d '{"company":"시험 기업","role":"시험 직무","question":"시험 문항","experience":"시험 경험"}' \
  http://127.0.0.1:8001/api/drafts
uv run --frozen pytest
node --test tests/test_foundation.mjs
```

health는 `status: "ok"`, `mcpConnected: true`, `pipelineAvailable: true`를 표시한다. 키/모델이 없으면 `modelConfigured: false`이며 유효한 초안 요청은 `500 CONFIG_ERROR`로 종료한다. `instanceId`와 `creationCount`는 여러 health 조회에서 연결을 다시 생성하지 않는지 확인하는 기반 진단이다. `modelConfigured: true`만으로 키 유효성이나 실제 모델 호환성을 입증하지 않는다.

`web/foundation.mjs`는 기반 요청 도우미이며 새 Vue 화면은 `web_chat.html`·`web_app.js`·`web_contract.js`·`web_style.css`를 사용한다. 화면의 LF/Unicode 코드 포인트 계산, POST JSON, 195초 취소, 응답 계약 검사는 [ESSAY-15 보고서](../docs/qa-evidence/assignment/vue/verification.md)를 따른다. 별도 `web_demo_server.py` 프록시는 190초 전체 제한으로 실제 생성 API에 연결된다. 실제 Chrome→Vue→프록시→API→LangGraph 경로는 통제 모델로 [ESSAY-16 회귀](../docs/qa-evidence/assignment/automated/verification.md)에서 확인했다.

```bash
# 기반 서버와 다른 터미널에서 Vue 화면·프록시를 실행한다.
uv run --frozen uvicorn web_demo_server:app --host 127.0.0.1 --port 8600
# http://127.0.0.1:8600/ 를 연다.
```

## 실제 모델 확인과 한계

실제 OpenAI 구조화 출력·내장 검색 검사는 명시적으로 선택하는 별도 유료 검사다. 일상 시작·자동 테스트·health 조회에 포함하지 않으며 유료 검사들은 기본 테스트에서 skip한다. 필요한 비용과 키 사용을 승인한 경우 assignment/에서 실행한다.

```bash
ESSAY_LIVE_COMPATIBILITY=1 uv run --frozen pytest tests/test_live_compatibility.py -q -s
```

이 전환 호환성 검사만 기존 저장소 루트 `.env.local`의 `OPENAI_API_KEY`와 `OPENAI_MODEL`을 내부에서 읽는다. 일반 서버/실행기의 설정 위치는 여전히 assignment/.env 또는 프로세스 환경이다. 검사는 구조화 출력 1회와 실제 MCP를 통한 내장 검색 1회를 실행한다(자동 재시도 0, 공개 시험 입력 OpenAI / Software Engineer). 키와 응답 원문을 출력하지 않고 `../docs/qa-evidence/assignment/foundation/checks/live-compatibility*.json`에 정제한 결과를 쓴다. 실제 수행 결과는 해당 기록을 확인한다. 모의 제공자 검사나 MCP 연결 성공을 실제 모델/검색 성공으로 해석하지 않는다.

## 조사 역할 확인

`agent/nodes/research.py`는 조사할 자료가 있을 때 실제 MCP 후보 조사 뒤 공식 페이지 또는 사용자 원문을 대조한다. 초기 공식 기업 목록은 네이버·카카오·OpenAI·Anthropic이며 계열사와 임의 기업을 자동 승인하지 않는다. 신뢰 출처가 없고 공고 입력도 없으면 조사를 생략하고 기업·직무·문항·경험 입력으로 작성한다. 확인되지 않은 회사 사실이나 공고 요건은 사용하지 않는다. 공고가 다른 직무를 가리키면 해당 요건을 제외하고 작성하며 화면에 이를 알린다. 사용자 자료는 `user_provided`이며 공식 확인을 뜻하지 않는다.

아래 검사는 각각 유료 모델1회를 실행하며, 이 시험 도구만 루트 `.env.local`의 기존 키/모델을 내부에서 읽는다. 일반 서버의 설정 위치는 바뀌지 않는다. 공개 네이버 공고와 명시된 합성 공고를 사용하고 고유한 정제 JSON을 `../docs/qa-evidence/assignment/research/checks/`에 남긴다. 자동 재시도는 없다.

```bash
ESSAY_LIVE_RESEARCH=1 ESSAY_RESEARCH_CASE=naver uv run --frozen pytest tests/test_research_live.py -q -s
ESSAY_LIVE_RESEARCH=1 ESSAY_RESEARCH_CASE=synthetic uv run --frozen pytest tests/test_research_live.py -q -s
```

구현·실제 결과·실패 이력·지원 한계는 [조사 검증 보고서](../docs/qa-evidence/assignment/research/verification.md)를 따른다. 전체 그래프/API 연결의 통제 입력 시험은 [ESSAY-14 검증](../docs/qa-evidence/assignment/integration/verification.md), 화면을 포함한 통제 회귀는 [ESSAY-16 검증](../docs/qa-evidence/assignment/automated/verification.md)을 따른다. 실제 유료 모델의 자기소개서 품질·사실성과 기존 5개 샘플 재실행은 ESSAY-17에서 확인한다. 원본 교육용 의도적 실패/재시도·세 번째 강제 통과 흐름은 실행하지 않는다.
