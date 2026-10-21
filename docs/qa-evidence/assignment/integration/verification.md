# ESSAY-14 LangGraph·FastAPI 통합 검증

- 검증일: 2026-10-21
- 위치: `assignment/`
- 대상: `agent/essay_collect.py`, `agent/essay_route.py`, `agent/essay_graph.py`, `server.py`
- 시험 성격: 통제된 모델 출력과 로컬 HTTP/MCP. 외부 유료 모델 호출 0회. 실제 생성 품질과 작성자 사실성 승인은 ESSAY-17 범위.

## 확인한 처리 흐름

| 입력·상황 | 관찰 결과 |
| --- | --- |
| 문항·경험·사용자 제공 직무 공고, 통제 모델 통과 | B/C와 조사를 한 번 합류한 뒤 D→E→F→G→H. 900 코드 포인트, 조사 포함 모델 예약 4회, 수정 0회 |
| 실제 stdio MCP의 사용자 제공 공고 후보 응답 | `ResearchNode`의 원문 검증 후 `user-posting` 출처에 연결된 직무 요건으로 같은 LangGraph ready. MCP 요청 1회·전체 모델 예약 4회 |
| F의 구성/주장 지적 | G→D 예약→E→전체 F→H, 총 6회·수정 1회 |
| F의 문장 지적 | G→I 예약→전체 F→H, 총 6회·수정 1회 |
| 수정 후에도 구성 기준 실패 | J `QUALITY_CHECK_FAILED`; 세 번째 작성 없음 |
| F의 필수 정보 부족 또는 정보 부족+구성 지적 | J `needs_input`; 정보 부족이 우선이며 수정 예약 없음 |
| B/C에서 경험 보완 필요, 다른 조사가 진행 중 | 조사 취소 관찰, E/F 호출 없음, J `needs_input` |
| HTTP 결과 대역 | ready/needs_input 200, 품질 실패 422, 설정 오류 500, 모델 오류 502, 시간 초과 504. 오류에는 원문·초안·키·전체 프롬프트를 넣지 않음 |
| 실제 Uvicorn 127.0.0.1:8001 | `GET /health` 200(`mcpConnected:true`, `pipelineAvailable:true`), 빈 `POST /api/drafts` 400 `INVALID_INPUT` |

새 통합 시험은 실제 `AnalyzeNode`, `build_plan`, `WriteNode`, `ReviewNode`, `RevisionNode`, LangGraph, FastAPI를 실행한다. 정상/수정 분기는 통제 `ModelProvider`로 예측 가능한 구조화 출력을 공급한다. 일반 통합 시험의 조사 결과는 예약을 수행하는 대역이며, 별도 시험에서 실제 `MCPClient` stdio 연결·후보 응답·`ResearchNode` 출처 검증을 전체 그래프에 연결했다. 로컬 MCP의 OpenAI Responses HTTP만 통제 응답이다. 공식 기업 2곳, 실제 유료 모델 초안, Vue→API 브라우저 전체 실행은 여기서 주장하지 않는다.

## 검사 명령과 결과

| 실행 | 결과 |
| --- | --- |
| `assignment/.venv/bin/python -m pytest -q` | 474 passed, 2 skipped (유료 연결 명시적 선택), 최종 재실행 26.74초. localhost 시험 포트 허용 환경 |
| `assignment/.venv/bin/ruff check .` | All checks passed |
| `assignment/.venv/bin/ruff format --check .` | 95 files already formatted |
| `assignment/.venv/bin/basedpyright` | 0 errors, 0 warnings, 0 notes |
| `node --test tests/test_foundation.mjs tests/test_web_contract.mjs` | 13 passed, 0 failed |
| 실제 Uvicorn + HTTP | health 200 / 빈 POST 400 / 정상 종료 |

격리된 첫 전체 실행의 20개 실패는 기존 localhost HTTP fixture의 포트 바인드가 `PermissionError: [Errno 1] Operation not permitted`로 막힌 결과다. 테스트를 생략하지 않고 같은 명령을 로컬 시험 포트 허용 환경에서 다시 실행해 전체 통과를 확인했다. 새 통합 시험에서도 처음에는 LangGraph가 비동기 람다의 coroutine을 상태로 받아 실패했고, 실제 async 노드 함수로 고쳤다. 취소 반례에서는 자식 조사 취소가 요청 예산을 정지시켜 보완 결과가 오류로 바뀌는 문제를 발견했다. 그래프 전체를 요청의 180초 deadline으로 감싸고 조기 종료 결과를 보존하도록 바꾼 후 같은 반례가 통과했다.

전체 deadline은 요청별 예산의 180초 값으로 설정해 AnyIO에서 강제한다. 기존 모델30초·조사45초·Vue/프록시195/190초 계약은 유지한다. 실제 HTTP 연결에서 180초를 통째로 기다리는 시험은 하지 않았으므로 네트워크 경계의 장시간 유지성은 ESSAY-16에서 다시 확인한다. 이번 ESSAY-14의 통합 결과는 통제 입력에서의 경로·계약·오류 구분을 입증한다.
