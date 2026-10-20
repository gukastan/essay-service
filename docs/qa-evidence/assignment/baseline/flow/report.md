# ESSAY-18 원본 실행: 흐름·MCP·SSE 증거

2026-10-20 UTC 기준, 원본을 복사한 `assignment/`의 **fake/v2 API 검증 25개와 독립 MCP 검증 8개가 통과**했다. FastAPI·LangGraph·stdio MCP는 실제 실행했고, LLM과 JSON 모니터링 자료는 모의다. 제품 코드 수정·유료 모델 호출·Jira 변경은 하지 않았다.

API 실행: `2026-10-20T05:31:55.864Z`~`05:31:57.909Z`. MCP 실행: `05:33:33.597409Z`~`05:33:35.837438Z`. API는 A 담당자가 시작한 `http://127.0.0.1:8100`이며 Node `v26.7.0`을 사용했다. MCP는 A의 별도 Python `3.11.15` 환경을 사용했다. 설치·시작·종료 및 화면 증거는 다른 담당자의 기록에 있다.

## 시나리오와 판정

명령 A는 아래 API 실행 명령, 명령 M은 아래 MCP 실행 명령이다. JSON의 `records[].name` 또는 `checks` 키로 해당 원자료를 찾을 수 있다.

| 기준 / 시나리오 | 호출 / 판정 가능한 관찰값 | 결과와 증거 |
| --- | --- | --- |
| v2 health·공유 객체 | A: 요청 전후 GET `/health`, GET `/version` | `llm_backend=fake`, version v2, `creation_count=1`, 동일 `instance_id=4501381712`. [api-results.json](api-results.json) health-before/health-after/version 및 bundle reused 검사 통과. 서버 재시작은 검증하지 않았다. |
| 첫 장애 문의·계획·게이트 | A: POST `/chat`, `auth-service 장애를 진단해줘` | route incident, 계획 생성 후 analysis task 1개 제거. monitoring auth-service/web-01 완료 후 runbook 완료. 최종 task_count=3. [api-results.json](api-results.json) incident-first와 검사 7개. |
| 재시도 | 같은 첫 요청 | 첫 monitoring TaskCompleted의 retries=1, metadata.retry_count=1. 후속 incident-sse의 합계는 0. 클라이언트가 MCP 호출 전에 발생시킨 교육용 TimeoutError다. 실제 네트워크 장애를 만들지 않았다. |
| 재계획 | 같은 첫 요청 및 SSE 문의 | ReplanCheck round0 false → runbook gap task → round1 true. metadata.replan_rounds=1. [api-results.json](api-results.json). |
| 조사 task 동작 | 같은 첫 요청 및 SSE 문의 | 서로 다른 monitoring target 2개와 runbook task 1개 완료. 소스는 gather 스케줄링을 사용하지만 MCP lock은 개별 요청을 직렬화한다. [source-audit.md](source-audit.md). 처리량·성능 향상은 측정하지 않았다. |
| 분석 진입 | A: GET `/chat/stream` 장애 문의 | `node=analysis`의 **AnalysisSkipped** 관찰. 비교 분석 작업이나 analyze LLM 호출을 완료했다고 주장하지 않는다. [api-results.json](api-results.json) incident-sse. |
| 작성·검증 수정 루프 | POST 및 SSE 장애 문의 | DraftWritten1 → Validation1 불합격 → DraftWritten2 → Validation2 합격 → Finalize. validation_attempts=2. [api-results.json](api-results.json). |
| 일반 대화 | A: POST `/chat`, `안녕, 너는 누구야?` | RouteDecided(chat)→Finalize(chat-direct), task_count=0. [api-results.json](api-results.json) general-chat. |
| 실제 SSE 반환 | A: GET `/chat/stream` 일반 대화 및 `web-01 CPU 급증, auth-service 커넥션 풀도 같이 확인해줘` | HTTP200/text-event-stream, JSON frame, FinalAnswer, 정확히 1개 [DONE]. 장애 SSE의 9종 node 확인. 2개 AnswerToken의 attempt=1/2이며 두 번째 delta=최종 답변. [api-results.json](api-results.json) chat-sse/incident-sse. 이는 전체 초안 callback이며 upstream 토큰 스트리밍 증거가 아니다. |
| 대화 이력 | A: 같은 고유 thread에 공개 예시 `제 이름은 민수입니다` 뒤 `제 이름이 뭐였죠?` | 후속 응답에 민수 포함. DB 파일 내용은 읽지 않았다. [api-results.json](api-results.json) session-set/session-recall. 재시작 후 영속성 미검증. |
| 입력 오류 | A: message 없는 POST `/chat` | HTTP422, missing/message 오류. [api-results.json](api-results.json) missing-required-message. |
| MCP 연결·Prompt | M: 독립 ops/docs stdio session 시작, find_prompt/get_prompt | 실제 세션 2개, ops의 incident_analysis_prompt 반환. 프롬프트는 길이와 SHA256만 기록. [mcp-results.json](mcp-results.json). |
| MCP Tool·Resource | M: get_monitoring_status(auth-service), get_incident_runbook(high-latency) | retry=1 뒤 typed telemetry(degraded); runbook은 복사된 공개 fixture와 동일. [mcp-results.json](mcp-results.json). |
| MCP 제한된 예외 | M: unknown-service, 없는 runbook, docs template list | unknown status/0 CPU/알림1개, Runbook Not Found 문자열, docs template 반환. 자신의 client sessions 정상 종료. [mcp-results.json](mcp-results.json). |
| 원본 fake 모드 제한 | A: 제공 예시 `cache-service 메모리 사용률이 계속 올라가고 있어요` | 기대 가능한 장애 의미와 달리 fake regex에서 chat 반환. 재현 성공을 검사 통과로 기록했으며 제품 의미상 정상 장애 진단으로 간주하지 않는다. [api-results.json](api-results.json) documented-fake-limitation. 원본 `agent/fake_llm.py:27` 근거. |

## 재현 명령

작업 디렉터리: `/Users/jay/Projects/essay-service`. API 소유자가 fake/v2 서버를 준비한 후 실행한다. 첫 명령의 `fresh`는 **첫 monitoring 호출이 아직 없는 프로세스**가 필요하다. 이미 실행한 프로세스의 재검사는 `warm`과 별도 결과 파일명을 사용한다. 이 스크립트는 health의 fake/v2 조건을 먼저 확인하며 각 HTTP 요청을 20초로 제한하고 UUID thread를 사용한다.

```bash
node docs/qa-evidence/assignment/baseline/flow/run-api.mjs http://127.0.0.1:8100 fresh docs/qa-evidence/assignment/baseline/flow/api-results.json > docs/qa-evidence/assignment/baseline/flow/api-run.log 2>&1
```

MCP probe는 공유 HTTP 서버와 독립된 subprocess를 생성하고 자신이 만든 client만 닫는다. 30초 전체 제한이다. 네트워크 모델을 호출하지 않는다.

```bash
env -i PATH=/usr/bin:/bin PYTHONDONTWRITEBYTECODE=1 PYTHON_DOTENV_DISABLED=1 LANGCHAIN_TRACING_V2=false LANGSMITH_TRACING=false LLM_BACKEND=fake /Users/jay/Projects/essay-service/.omo/runtime/essay18/venv/bin/python docs/qa-evidence/assignment/baseline/flow/probe-mcp.py /Users/jay/Projects/essay-service/assignment /Users/jay/Projects/essay-service/docs/qa-evidence/assignment/baseline/flow/mcp-results.json > docs/qa-evidence/assignment/baseline/flow/mcp-run.log 2>&1
```

첫 API 시도는 샌드박스의 localhost 연결 EPERM으로 요청 전에 실패했다. [api-sandbox-denied.log](api-sandbox-denied.log)와 [api-sandbox-denied.json](api-sandbox-denied.json)은 **실패한 환경 시도**다. 허용된 동일 로컬 호출을 다시 수행한 위 명령은 exit0이며 [api-run.log](api-run.log)에 25/25가 남아 있다. 첫 호출 상태는 실패한 샌드박스 시도에서 소모되지 않았다.

## 완료 조건 대응과 미검증

ESSAY-18의 일반/장애 경로·MCP·수정 루프 관찰 조건을 이 증거가 담당한다. analysis는 노드 진입/skip까지만 확인했다. 기준 커밋·원본 복사 해시·설치·패키지 버전·서버 수명은 A 담당, 실제 화면은 리더 담당이므로 이 보고서만으로 전체 티켓의 모든 조건을 통과했다고 판단하지 않는다.

실제 OpenAI/Ollama, 실제 운영 모니터링/검색, 실제 분석 모델 경로, 세 번째 검증 강제 통과, 영구 도구 실패·재시도 한도, 서버 재시작, 연결 취소/시간초과 부하 및 정량 병렬 성능은 실행하지 않았다. 새 자기소개서 서비스의 품질/예산/개인정보 계약은 이번 범위 밖이다.

`prompt`/`last_prompt`와 키 필드는 JSON 증거에 없다. 합성 사용자 입력·모의 답변만 보존했다. [artifact-validation.json](artifact-validation.json)은 JSON 검사 33개 통과와 금지 키 0개를 기록한다. [syntax-check.log](syntax-check.log), [python-audit.log](python-audit.log)는 runner 구문 및 Python 규칙 검사 결과다. [audited-source-sha256.txt](audited-source-sha256.txt), [source-symbol-lines.txt](source-symbol-lines.txt)는 읽은 소스 6개의 해시와 실제 함수 위치다.
