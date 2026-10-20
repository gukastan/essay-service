# ESSAY-18 원본 흐름 정적 감사

검토 원본: `/Users/jay/Downloads/all_total_vue_student` (읽기 전용). 제품 수정 없음. `.env`와 `session.db` 내용은 읽지 않았다. 이 문서는 소스에서 확인한 구조이며 실제 실행 결과는 `api-results.json`, `mcp-results.json`과 `report.md`를 별도로 참조한다.

| 흐름 | 소스 근거 | 확인한 동작과 한계 |
| --- | --- | --- |
| 요청/수명 | `server.py:63` lifespan, `server.py:94` health, `server.py:126` _handle_chat | 프로세스 lifespan에서 MCPClient·LLM·그래프를 만든다. 요청은 공유 deps/graph를 쓴다. health의 instance_id/creation_count가 동일 프로세스 내 재사용 관찰 지점이다. 재시작 후 재사용은 별개다. |
| 일반 대화 | `agent/fake_llm.py:27`, `agent/graph.py:76`, `agent/graph.py:86` | fake는 장애/진단/다운/지연/급증/incident/티켓 정규식으로 라우팅한다. chat은 route→chat_answer로 종료하며 plan/research/write/validate를 거치지 않는다. |
| 계획/게이트 | `agent/graph.py:102`, `agent/graph.py:123`, `agent/fake_llm.py:36` | 실제 MCP prompt를 이름으로 발견·조회한 뒤 plan 호출. fake는 needs_analysis=False인데 analysis task를 추가하고 gate가 그 task를 제거한다. 이는 교육용 자기모순 재현이다. |
| 병렬 조사 | `agent/graph.py:138` research, `agent/graph.py:172` gather, `agent/mcp_client.py:71` call_tool | pending research task들을 asyncio.gather로 스케줄하고 각 task에 0.35초 인위적 지연을 준다. 실제 MCP 요청은 공유 lock으로 직렬화된다. TaskCompleted는 gather 완료 뒤 입력 순서대로 기록되므로 완료 순서/실제 동시 처리 증거가 아니다. |
| 병렬 시간 | `agent/graph.py:185` 반환, `server.py:114` metadata | parallel_elapsed는 각 research 호출마다 덮어쓴다. 마지막 runbook 조사 시간만 최종 metadata에 남는다. 전체 병렬 조사의 성능이나 순차 실행 대비 속도 향상으로 해석하면 안 된다. |
| 재계획 | `agent/graph.py:216` replan_check | runbook이 없으면 gap runbook task 하나를 추가해 research로 돌아간다. rounds>=1이거나 runbook을 받으면 충분하다고 판단한다. 실제 검색이나 모델의 재계획이 아닌 코드 규칙이다. |
| 분석 | `agent/graph.py:233` analysis | 노드는 진입하지만 pending analysis task가 없으면 AnalysisSkipped를 반환한다. fake가 항상 needs_analysis=False이므로 이 모드에서 비교 분석 완료/분석 모델 호출을 주장할 수 없다. |
| 작성/검증 | `agent/fake_llm.py:94`, `agent/graph.py:254`, `agent/graph.py:274` | fake 첫 초안은 의도적으로 짧다. validator는 30자 이상과 `1)` 포함만 검사한다. 반려 후 두 번째 fake 초안이 통과한다. 세 번째 실패는 강제 통과하는 원본 코드가 있으나 이번 정상 fake 경로에서는 도달하지 않는다. 사실성 검증이나 신규 자기소개서 기준이 아니다. |
| 재시도 | `agent/mcp_client.py:72`, `agent/retry.py:11` | 프로세스 최초 get_monitoring_status는 실제 MCP 호출 전 TimeoutError를 의도적으로 발생시킨다. with_retry는 TimeoutError만 최대 3회 시도하고 0.3초×3^n 대기한다. 이 재현은 외부 장애 복구 성능 증거가 아니다. |
| MCP 역할 | `mcp_server.py:34`, `mcp_server.py:57`, `mcp_server.py:66`, `agent/mcp_client.py:105` | Tool은 JSON fixture를 읽고 jitter를 더한다. Resource는 로컬 runbook이다. Prompt는 진단 템플릿이다. 실제 stdio MCP 호출을 사용하지만 데이터와 모델이 실제 운영 모니터링/LLM이라는 뜻은 아니다. docs 서버는 decoy이다. |
| SSE | `server.py:148` chat_stream, `agent/graph.py:261`, `agent/fake_llm.py:68` | LangGraph updates/custom을 SSE로 전달하고 FinalAnswer, [DONE]으로 종료한다. updates의 node는 실제 완료 노드이며 AnalysisSkipped와 구분해야 한다. fake callback은 응답/초안 전체를 한 번에 전달한다. upstream 토큰 생성 스트리밍을 검증하는 경로가 아니다. |
| 민감정보 경계 | `server.py:166`, `server.py:187`, `agent/session_store.py` | 원본 SSE FinalAnswer에 prompt 필드가 있고 SQLite에 대화를 저장한다. 이번 증거는 공개 합성 입력만 사용하며 prompt/last_prompt는 저장 전에 제외한다. 새 서비스의 개인정보 설계 검증은 ESSAY-18 범위 밖이다. |

## 원본 문서와 fake 모드 차이

`doc/regression_test_queries.md`의 cache-service 메모리 문의 등에는 fake 라우팅 정규식 단어가 없다. fake에서는 chat으로 분기할 수 있으며, 이 문서의 모든 시나리오가 fake에서 장애 조사로 동작한다고 주장하지 않는다. `needs_analysis=true` 예시도 fake에서는 도달할 수 없다. 실제 모델을 호출하지 않고 이 점을 동작 관찰로 기록한다.

## 후속 전환에 전달할 사실

현재 모의 비용은 문자열 길이 기반 추정치이며 실제 과금이 아니다. 최종 답변의 모니터링값은 fixture와 난수다. 현재 validation 기준/강제 통과, 공유 SQLite/GET query/prompt 노출, 자동 도구 재시도는 후속 요구와 다르지만 ESSAY-18에서는 원본을 변경하지 않는다. 자료/정책 변경은 후속 작업의 소유권으로 넘긴다.
