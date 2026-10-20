# ESSAY-19 검증 범위

2026-10-20 사용자가 요청한 범위는 Python 공통 기반 구현·검증까지다. 이 표는 실행 전 완료 기준이며 실제 통과 결과는 최종 verification.md와 원자료로 확인한다.

| 완료 조건 | 관찰할 결과 | 담당 |
| --- | --- | --- |
| 계약·상태·호환 의존성 | 입력/출력·근거 스키마, 실제 LangGraph 주입 노드 검사, 고정 환경 설치 | core + checks |
| 수명과 요청 격리 | 재사용 의존성, 새 요청 예산/상태, SQLite·추적 비활성 | core + checks + runtime |
| 예산·취소 | 모델 최대6·출력예약18000, 30/45/180초, 실패/취소 무환불·추가 전송 차단 | core + checks |
| MCP 선예약 | 모델1/hosted2 예약 후 전송, 내부 Responses1회, store false/max_tool_calls2/재시도0 | core + checks |
| 입력 경계·프로토콜 | 경험/문항 제외, trusted 메타데이터, 오류·단절·취소·동시성 격리 | core + checks |
| 문자·근거 위치 | LF·코드 포인트, 한글/CRLF/이모지 Python/JS·실제 Vue 일치 | core + checks + runtime + leader |
| 실제 모델 호환 | 기존 키/모델의 구조화 출력1회와 실제 MCP 검색1회, 키/프롬프트 비공개 | leader, checks opt-in runner |
| 실행 진입점 | 빈 설정 예시, 깨끗한 고정 설치, bash run.sh 시작/정상 종료/포트 충돌 | runtime |

기존 Downloads 원본·루트 Next.js·기존 QA와 ESSAY-18 증거는 보존한다. ESSAY-10의 공식 출처 검증과 역할 업무 프롬프트, ESSAY-14의 전체 그래프/API, ESSAY-15의 자기소개서 화면은 후속 작업이다. 실제 MCP 연결 성공을 회사 출처 공식성이나 자기소개서 품질 검증으로 해석하지 않는다.

참고한 공식 문서:

- [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs): Pydantic 기반 Responses 구조화 출력, required/nullable JSON 스키마.
- [OpenAI 도구](https://developers.openai.com/api/docs/guides/tools): Responses web_search 사용.
- [Responses API](https://developers.openai.com/api/reference/resources/responses/methods/create): max_tool_calls는 내장 도구 호출 전체의 상한이다. 참조 본문 fetch는 생성 메타데이터만 반환해 실제 설치 SDK 타입도 확인한다.
- [FastMCP Client tools](https://github.com/prefecthq/fastmcp/blob/main/docs/clients/tools.mdx): 실제 도구 호출·결과·timeout.

문서 예제의 모델명으로 설정 모델을 바꾸지 않는다. 실제 연결은 별도 opt-in이며 기존 로컬 .env.local에서 필요한 변수만 프로세스 내부로 주입한다. 기본 자동 검사는 유료 호출을 하지 않는다.
