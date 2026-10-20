# ESSAY-19 Python 실행 기반

현재 구현은 Pydantic 계약, 요청별 상태·예산, 재사용 모델/MCP 연결, 텍스트·클라이언트 요청 도우미와 실행 기반이다. `GET /health`로 기반 상태를 조회한다. 자기소개서 생성 API `POST /api/drafts`, 네 업무 역할 및 새 Vue 화면은 후속 티켓에서 구현한다. 현재 `/api/drafts`, 원본 `/chat`, `/chat/stream`은 404다. 상태의 `pipelineAvailable: false`는 이 범위를 의미한다.

원본 복사본의 `web_chat.html`, `web_demo_server.py`, `sh/` 실행기는 보존 자료다. 아래 실행 방법은 이 파일들을 실행하지 않는다. `doc/`의 과거 화면과 ESSAY-18 기록은 새 자기소개서 서비스 검증 증거가 아니다. 루트 Next.js와 Downloads 원본은 별도로 보존한다.

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

다른 터미널에서 실행한다. 두 번째 요청은 미구현 API가 정직하게 404를 반환하는지 확인하는 제어 입력이다. 초안 결과가 아니다.

```bash
curl --fail --silent http://127.0.0.1:8001/health
curl --silent --output /dev/null --write-out '%{http_code}\n' \
  -H 'Content-Type: application/json' \
  -d '{"company":"시험 기업","role":"시험 직무","question":"시험 문항","experience":"시험 경험"}' \
  http://127.0.0.1:8001/api/drafts
uv run --frozen pytest
node --test tests/test_foundation.mjs
```

health는 `status: "ok"`, `mcpConnected: true`, `pipelineAvailable: false`를 표시한다. 키/모델이 없으면 `modelConfigured: false`다. `instanceId`와 `creationCount`는 여러 health 조회에서 연결을 다시 생성하지 않는지 확인하는 기반 진단이다. `modelConfigured: true`만으로 키 유효성이나 실제 모델 호환성을 입증하지 않는다.

브라우저 통합 준비용 `web/foundation.mjs`는 LF 정규화, Unicode 코드 포인트 수/슬라이스/근거 대조와 JSON 요청 도우미를 제공한다. 이모지의 UTF-16 길이나 화면상 글자 묶음 수를 사용하지 않는다. `requestJson`은 응답 본문까지 195초 제한을 적용하고 외부 취소를 연결하며 자동 재시도하지 않는다. 서버 요청 제한은 180초다. 후속 Vue 화면이 이 모듈을 연결하고 반환 JSON의 기능별 계약을 검증해야 한다.

## 실제 모델 확인과 한계

실제 OpenAI 구조화 출력·내장 검색 검사는 명시적으로 선택하는 별도 유료 검사다. 일상 시작·자동 테스트·health 조회에 포함하지 않으며 기본 테스트에서는 이 검사만 skip한다. 필요한 비용과 키 사용을 승인한 경우 assignment/에서 실행한다.

```bash
ESSAY_LIVE_COMPATIBILITY=1 uv run --frozen pytest tests/test_live_compatibility.py -q -s
```

이 전환 호환성 검사만 기존 저장소 루트 `.env.local`의 `OPENAI_API_KEY`와 `OPENAI_MODEL`을 내부에서 읽는다. 일반 서버/실행기의 설정 위치는 여전히 assignment/.env 또는 프로세스 환경이다. 검사는 구조화 출력 1회와 실제 MCP를 통한 내장 검색 1회를 실행한다(자동 재시도 0, 공개 시험 입력 OpenAI / Software Engineer). 키와 응답 원문을 출력하지 않고 `../docs/qa-evidence/assignment/foundation/checks/live-compatibility*.json`에 정제한 결과를 쓴다. 실제 수행 결과는 해당 기록을 확인한다. 모의 제공자 검사나 MCP 연결 성공을 실제 모델/검색 성공으로 해석하지 않는다.

현재 이 기반으로 자기소개서를 생성하거나 공식 출처·사실성·801~1000자 완성품을 검증할 수 없다. 원본 교육용 의도적 실패/재시도와 세 번째 강제 통과 흐름도 실행하지 않는다. 네 역할, 공식 근거 검증, 새 Vue 화면과 전체 서비스 QA는 후속 티켓 범위다.
