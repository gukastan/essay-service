# ESSAY-18 원본 보존·실행 검증

- 판정: **완료**, 2026-10-20 KST.
- Jira: [ESSAY-18](https://kmskojb.atlassian.net/browse/ESSAY-18).
- 범위: 제공 프로젝트의 원본 복사·Mac 설치·실제 실행·처리 흐름 관찰. 자기소개서 기능 이식은 미착수.
- 기준 커밋: `c5299e954d0ff1b0848dad238e7b731ef078bb51`. 이번 작업은 아직 커밋·푸시하지 않았다.
- 원본: `/Users/jay/Downloads/all_total_vue_student` → 복사본: `/Users/jay/Projects/essay-service/assignment`.

원본의 실행 코드 수정 없이 FastAPI·Python LangGraph·stdio MCP·Vue 화면이 동작했다. **추론은 FakeLLM이고 모니터링은 JSON fixture**다. 실제 OpenAI/Ollama 모델·검색·운영 시스템을 검증한 결과가 아니다. API 키를 주입하거나 유료 모델을 호출하지 않았다.

## 완료 조건과 증거

| 조건 | 관찰 결과 | 근거 |
| --- | --- | --- |
| 기존 코드와 원본 보존 | HEAD 불변. 작업 시작 당시 추적 파일 349개 중 승인된 상태 문서 8개를 제외한 341개가 바이트 동일하다. 기존 src/·tests/·샘플·QA를 수정하지 않았다. 원본의 포함 파일 46개도 종료 후 해시가 같다. | [기존 파일 보존](repository-preservation.json), [시작 해시](repository-start-hashes.json), [종료 후 원본 해시](source-runtime/post-shutdown-source-hashes.json) |
| 원본 소스 복사와 제외 | 소스·문서·자산 46개를 최초 동일 해시로 복사했다. .env·가상환경·DB·캐시·로그 등 10,444개 파일은 제외했다. 이후 복사본 .gitignore만 보강했다. | [복사·제외 명세](source-runtime/source-provenance.json), [복사본 차이](source-runtime/source-reverification.json) |
| 별도 Mac 설치와 실행 | macOS 26.6.2 arm64, CPython 3.11.15의 새 환경에 원본 requirements 설치. 95개 패키지 호환 검사 통과. API/UI/프록시 health HTTP 200, localhost 바인딩, 실제 화면 확인. | [설치·실행 보고서](source-runtime/README.md), [정확한 명령](source-runtime/commands.txt), [설치 버전](source-runtime/installed-requirements.txt), [초기 화면](browser/01-initial.png) |
| 일반/장애 처리와 MCP·재작성 | 일반 대화 direct 종료, 장애 계획·게이트·모니터링·추가 매뉴얼·분석 노드 skip·첫 초안 반려·두 번째 초안 통과 확인. 실제 MCP Tool/Resource/Prompt 호출 성공. | [API/MCP 보고서](flow/report.md), [API 원자료](flow/api-results.json), [MCP 원자료](flow/mcp-results.json), [최종 화면](browser/09-incident-result.png) |
| 실행 결과·한계 기록과 인계 | 실행 소스 수정 불필요. run.sh 누락·모의 동작·검증 한계를 기록했다. 실행 시 전체 프롬프트를 증거에 저장하지 않았다. 후속은 ESSAY-19이며 이번에 시작하지 않았다. | 이 문서, [소스 감사](flow/source-audit.md), [증거 검사](flow/artifact-validation.json), [브라우저 보고서](browser/README.md) |

원본의 제공 스크린샷은 `assignment/doc/`의 상속 자료다. 이번 실행 증거는 이 폴더의 `browser/` 아래에 새로 촬영한 네 장이다. 기존 v1/ESSAY-9 테스트 결과도 새 Python 실행의 통과 수로 세지 않았다.

## 실행 및 확인 결과

| 계층 | 통과 수 | 검사 내용 | 결과 파일 |
| --- | --- | --- | --- |
| 설치·실행 환경 | 13 | 스크립트 차이, 원본 UI 바이트, HTTP 상태, 모드·공유 객체, 비밀/가상환경 제외 | [runtime-checks.json](source-runtime/runtime-checks.json) |
| 실제 API·SSE | 25 | route, 게이트, 조사·재계획, 수정 루프, 세션 예시, 입력 누락 422, SSE 종료, fake 제한 재현 | [api-results.json](flow/api-results.json) |
| 독립 실제 MCP | 8 | 두 stdio 세션, 도구·리소스·프롬프트, 없는 서비스/매뉴얼, 정상 종료 | [mcp-results.json](flow/mcp-results.json) |
| 실제 브라우저 | 5 | 초기 화면, 빈 입력, 일반 대화, 처리 중 버튼 비활성화, 장애 결과 | [result.json](browser/result.json) |

총 51개는 위 검증의 검사 항목 수다. 별도의 새 서비스 단위 테스트 51개를 구현했다는 뜻은 아니다. 기존 Node 회귀 검사는 재실행하지 않았으며 해당 코드·기존 증거 보존은 해시로 확인했다.

API 검사는 14:31 KST, 독립 MCP 검사는 14:33 KST, 브라우저 검사는 14:37 KST에 실행했다. 구체 시각·입력·기대/실제 결과는 각 원자료에 남겼다.

실제로 관찰한 장애 흐름은 다음과 같다.

`route → plan → gate → research → replan_check → research → replan_check → analysis(skip) → write → validate(반려) → write → validate(통과) → finalize`

일반 대화는 `route → chat_answer`로 끝났다. MCP 두 서버가 API의 실제 자식 프로세스로 실행됐고 독립 probe에서도 같은 프로토콜 경계를 통과했다.

## 실행 안내 차이와 발견 사항

1. **실행 진입점:** 제공물에 루트 run.sh와 .env.example이 없다. 기존 sh 스크립트는 임의 포트 프로세스 강제 종료·DB 삭제·.env 로딩을 포함한다. 이를 실행하지 않고 새 환경에서 원본 Uvicorn API/UI를 직접 띄웠다. 제출용 run.sh·빈 설정 예시·고정 의존성은 ESSAY-19의 작업이다.
2. **분석과 재시도:** FakeLLM은 항상 needs_analysis=false라서 게이트가 분석 작업을 제거한다. analysis 노드 진입과 AnalysisSkipped를 확인했으며 실제 분석 모델 호출은 없었다. 첫 monitoring timeout은 클라이언트가 MCP 호출 전에 의도적으로 만든 오류이고 이후 재시도에서 실제 MCP를 호출했다.
3. **검토 한계:** 원본 validator는 30자 이상·`1)` 포함만 확인한다. 두 번째 초안에서 통과한 것을 관찰했다. 세 번째 실패를 강제로 통과시키는 코드는 정적으로 확인했으나 해당 경로를 실행하지 않았다. 새 사실성 검토 기준은 ESSAY-13에서 구현한다.
4. **병렬/스트리밍 한계:** 조사 task는 gather로 스케줄되지만 MCP lock은 전송을 직렬화한다. 최종 parallel_elapsed는 마지막 조사 시간이며 전체 속도 개선의 증거가 아니다. SSE는 실제 전달했지만 fake callback은 초안 전체를 보내므로 상위 모델 토큰 스트리밍 검증은 아니다.
5. **화면과 분류:** fake에도 `실모델`이라고 표시하고 반려 초안을 대화에 남기는 원본 UI를 관찰했다. 제공된 cache-service 메모리 문의는 fake 정규식 때문에 일반 대화로 분기한다. 한계 재현 검사의 통과를 장애 진단 품질 합격으로 해석하지 않는다. ESSAY-14/15에서 새 계약과 화면에 맞게 변경한다.
6. **저장과 노출:** 원본은 SQLite 대화 저장·GET 쿼리·전체 프롬프트 반환 경로를 갖는다. 이번에는 공개 합성 입력만 사용하고 증거의 prompt/last_prompt를 제거했다. 기존 Downloads DB는 읽거나 복사하지 않았다. 새 서비스의 비저장·POST·로그 정책은 ESSAY-19/14에서 구현한다.

첫 API 도구 시도는 localhost 연결 권한에서 거부됐고, 첫 브라우저 도구 시도는 시작 단계에서 응답하지 않았다. 허용된 환경에서 같은 검사를 재실행해 통과했다. 실패 시도는 API 실패 파일과 브라우저 보고서에 남겼으며 이를 제품 결함이나 성공한 검사로 세지 않았다.

## 종료 및 인계

14:40 KST에 이번 작업이 시작한 API/UI를 정상 종료했다. 두 MCP 자식까지 네 PID가 사라졌고 두 포트를 다시 사용할 수 있음을 확인했다. 다른 프로세스를 종료하지 않았다. [종료 기록](source-runtime/shutdown.json)을 보존했다. 성공한 브라우저 실행은 자신의 임시 프로필을 삭제했고, 중단한 첫 시도의 프로필도 정리했다.

별도 Python 환경은 `.omo/runtime/essay18/venv`에 남겨 재현할 수 있다. 새로 생성된 assignment/session.db와 런타임 로그는 Git 제외 상태이며 원본에서 복사한 자료가 아니다. 런타임/비밀 경로가 제출 후보 목록에 나오지 않는지 [보존 검사](repository-preservation.json)에서도 확인했다.

OMO 팀 `team-522c4869`는 원본/환경 담당과 흐름/MCP 담당의 최종 보고 후 종료했다. 리더가 브라우저 화면과 보존 결과를 확인했다. 팀 상태를 보관한 뒤 활성 상태 폴더를 정리했으며 [보관 상태](team/team.json)와 [담당자 보고](team/artifacts/)가 남아 있다. MultiAgentV2에는 실행 에이전트 보관 API가 없으므로 보관된 것은 팀의 디스크 기록이다.

다음 작업은 **ESSAY-19 Python 공통 계약·예산·MCP 기반 이식**이다. 현재 패키지 조합의 원본 실행 성공은 구조화 출력·OpenAI 검색 호환성이나 네 역할 자기소개서 서비스의 완성을 뜻하지 않는다. ESSAY-10~17·19·20은 할 일, ESSAY-8은 진행 중으로 유지한다.
