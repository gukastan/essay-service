# ESSAY-10 기업·직무 조사 최종 검증

- 날짜: 2026-10-20 / 범위: 조사 역할 구현·검증 완료.
- 기준 커밋: `2da2c898f71120ce087963feae12727848f24b64`. 이번 변경은 로컬 상태이며 새 커밋/푸시는 수행하지 않았다.
- 최종 제품/설정12개 해시: [source-manifest.json](source-manifest.json). 실행별 해시는 각 실제 결과 JSON에 있다.
- 다음 기본 범위: ESSAY-11 분석. 전체 그래프/API·Vue·작성 품질·제출 검증은 후속 작업이다.

## 구현 결과

`assignment/agent/nodes/research.py`의 `ResearchNode.run`은 기업·직무·선택 공고만 실제 stdio MCP의 `research_company_role`에 전달한다. MCP 내부 Responses1회가 검색과 후보 구조화를 수행하고 Python 검증기가 회사 관계·실제 페이지·원문 인용을 대조한다. 성공은 검증된 `ResearchResult`, 부족한 자료는 `needs_input`, 제공자/프로토콜/시간 오류는 공통 `error`다. 원시 후보를 작성 역할에 넘기지 않는다. 원본 장애/decoy 도구·SQLite 이력·강제 통과 루프는 실행하지 않는다.

운영자가 검토한 정확한 기업명/별칭·공식 호스트가 신뢰의 출발점이다. 사용자 선택대로 네이버·카카오·OpenAI·Anthropic을 등록했다. 계열사를 자동 포함하지 않으며 외부 채용 플랫폼은 실제 공식 페이지의 정확한 공고 링크와 연결 근거를 보존한다. [출처 결정](../../../decisions/official-source-trust.md)을 따른다.

공식 공고는 단일 JobPosting의 직무와 고용주를 같은 레코드로 확인한다. 네이버 상세 페이지는 단일 공고 카드 제목을 이 레코드에 연결하고, 카드 안 실제 업무/필수 기술 구역에서 원문 인용을 대조한다. 반환 발췌는 서버가 실제 구역에서 만든다. 모델이 번역한 메타데이터를 출처로 승격하지 않는다. 구역 하나를 선택하므로 모든 요건의 수집을 보장하지 않는다.

사용자 본문은 서버 소유 `user-posting`/`user_provided`다. 짧은 인용은 같은 LF 줄의 요청 직무명·요건 표시·콜론 뒤 값 전체와 정확히 같아야 한다. 부정·조건을 잘라낸 인용은 거부한다. 사용자 원문 공백은 보존하며 공식 페이지 인용만 연속 공백을 정리한다. 번역·단어/문장부호 변경·Markdown 추가를 허용하는 근사 비교는 없다.

## 완료 조건과 증거

| 조건 | 실제 확인 | 근거 |
| --- | --- | --- |
| 실제 MCP 역할/원본 구조 활용 | stdio 도구 발견·실제 SDK 경계·typed node, 기존 장애/decoy 비실행 | `test_research_node.py`, [node-first.txt](checks/node-first.txt), 실제 결과8개 |
| 단일 모델/예산 | MCP 내부1회, 모델1/hosted2 선예약, 추가 요약/자동 재시도 없음 | 실제 최종 두 결과, 기반 예산 회귀 |
| 기업/출처/구절 | 정확한 기업 범위·같은 공고의 직무/고용주·ATS 연결 보존·원문/ID/확인 시각 | `test_source_verification.py`, `test_source_domestic.py`, `test_source_sections.py` |
| 사용자 자료/보완/오류 | 원문·user_provided 표시, 회사/직무 부족 보완, 파싱/제공자 오류 정규화 | `test_source_user.py`, 사용자 줄 회귀, 실제 합성 공고 |
| 적대/누락 자료·개인 입력 분리 | 동명/계열사·상충·지시문·변조·빈/JS/접근거부, 문항/경험 sentinel 비전송 | 독립 source/MCP 검사와 [검사 보고서](checks/verification.md) |
| 직접 HTTP 안전/상한 | DNS 전체·매 redirect·실제 숫자 IP 연결 고정, 원래 Host/SNI·TLS 유지 | HTTP/소켓/취소 회귀, 실제 네이버/Anthropic 연결 |

직접 읽기3회(redirect 포함)·페이지1MiB·정리 합계12000코드포인트·조사45초를 공유한다. 모델30초·요청180초·클라이언트195초·재시도0은 ESSAY-19 계약을 유지한다. hosted 내부 검색어·페이지/바이트 수를 앱에서 독립 통제하거나 계측했다고 주장하지 않는다.

## 최종 자동 검사와 독립 검토

- 통합 Python **242 passed, 2 skipped, 19.95초**: [leader-final-pytest.txt](leader-final-pytest.txt). 두 skip은 명시적 유료 opt-in이다.
- JavaScript 공통 도우미 **12 passed**: [javascript.txt](javascript.txt). 실제 Vue 화면 검증이 아니다.
- Ruff **exit0**, 포맷 **59파일/exit0**, basedpyright **0 errors, 0 warnings**: [Ruff](leader-post-concat-ruff.txt), [포맷](leader-post-concat-format.txt), [타입](leader-final-types.txt).
- 독립 검사17파일 품질 점검 통과. [독립 검사 보고서](checks/verification.md)와 [코어 인계](../../../../.omo/evidence/essay10-core/handoff.md).
- 최종 읽기 전용 신뢰 검토 **WATCH / APPROVE, blockers=[]**. 마지막35개 관련 검사를 독립 실행했고 최종 해시를 대조했다. [검토 보고서](team/artifacts/code-review-current.md), [검토 해시](team/artifacts/final-close-review-hashes.json).

초기242개 통합 실행 후 마지막 변경은 긴 정규식의 문자열 연결을 명시하는 표기뿐이다. 값/동작은 그대로이며 그 뒤 타입·Ruff·포맷을 다시 통과했다. 처음 포맷 검사의 캐시 생성 권한 오류는 no-cache로 해결했고, 두 E501 및 implicit-concat 오류도 수정 전 기록을 남겼다. 이전214/220/234개 결과는 해당 중간 구현의 기록이며 최종 수를 대신하지 않는다.

## 실제 모델 실행

모델은 기존 로컬 설정의 `gpt-5.6-terra`다. 공개 네이버 공고와 명시된 합성 사용자 공고만 사용했다. 자동 검사는 유료 실행을 하지 않는다. 별도 독립 요청 **8회 중3회 성공**, 성공 기대 검사 **5회 실패**를 보존했다. 각 요청은 모델1/hosted예약2이며 자동 재시도는0이다. [전체 실행 장부](live-summary.json), [초기 실패 기록](live-initial.txt).

| 최종 사례 | 실제 결과 | 시간/호출 | 원본 메타데이터 |
| --- | --- | --- | --- |
| 네이버 / N배송 운영 지원 / annoId30005457 | official source1개, 원문 업무4개 | 11.825초; 모델1·hosted보고1/예약2·직접읽기1 | [네이버 성공](checks/live-node-620b999e-3d4d-40ce-ac7b-1fc42d5cda3a.json) |
| Example Fixture Company / Software Engineer / 합성 공고 본문 | user_provided1개, 원문 요건 값1개 | 5.605초; 모델1·hosted보고1/예약2·직접읽기0 | [사용자 공고 성공](checks/live-node-2e80bf28-3442-4a38-9c16-c3e2d9de0235.json) |

네이버 성공 후 마지막 기능 수정은 사용자 제공 줄의 근거 연결이며 공식 페이지 분기는 바뀌지 않았다. 유료 실행 후 수행한 문자열 물리 줄바꿈은 요청 지시 내용과 같음을 [해시 비교](prompt-equivalence.json)로 확인했다. 개별 결과의 실행 시 코드 해시와 최종 소스 해시를 구분한다. 최초 실패1회의 실제 도구/토큰 수는 수집하지 않았으므로 미확인이고, 실제 비용도 확인하지 않았다.

독립 검사에서 문화 글 오인·다중 공고 교차 결합을 재현했다. 실제 모델에서는 번역 메타데이터·Markdown/전체 공고 인용·과도한 직무명 반복 요구·짧은 원문 요건의 맥락 손실을 발견했다. 실제 공고 구역/원문 줄과 인용을 연결해 수정했다. 캐시 상한 우회·ATS 연결 근거 누락·회사명 부분 일치·상충 부정문·HTTP timeout/포트/전환IP 문제의 red/green 기록도 보존한다.

## 보존과 한계

[보존 검사](preservation.json): 시작 추적 파일613개 중 허용된 기존 변경13개를 제외한 **600개 불변**, 제공 Downloads 원본 **46개 불변**. 기존 Next.js·원본5개·v1/ESSAY-9/18/19 증거를 덮어쓰지 않았다. 기존 Next.js156개 테스트는 이번에 재실행하지 않았으며 코드 불변과 과거 증거를 구분한다. 키·경험·초안·전체 프롬프트·제공자 전체 본문을 QA/운영 로그에 남기지 않았다.

OpenAI careers 직접 읽기는 ACCESS_DENIED였고, Anthropic careers는 실제 직접 연결만 확인했다([중간 HTTP](http-interim.json)). 카카오는 JavaScript 안내만 반환하는 제약을 기록했다. 네이버 중간 관찰은 [별도 기록](naver-http-interim.json)이다. 네 기업 모두의 실제 모델 성공을 주장하지 않는다. 등록되지 않은 기업, 지원하지 않는 페이지/인용 형식, 다중 공고, JS/접근 불가 자료는 표시된 사용자 본문 또는 보완으로 처리한다.

지시문 단어 검사와 제한된 상충 검사는 보조 수단이며 모든 프롬프트 삽입·의미적 모순·현재 모집 여부를 증명하지 않는다. 전체 그래프/작성/검토·FastAPI 업무 API·새 Vue 화면·기존5개 전환판 및 기업2곳 전체 QA·새 작성자 사실성 승인·제출 확인은 ESSAY-11~17·20의 남은 범위다. 서버 `pipelineAvailable:false`와 `/api/drafts`404를 전체 서비스 성공으로 소개하지 않는다.

## Jira와 팀 정리

ESSAY-10 완료와 여섯 조건 체크를 실제 Jira에서 읽어 확인했다. 20개 티켓·에픽 하위12개·의존16개가 유지됐고 상태가 바뀐 티켓은 ESSAY-10뿐이다. 에픽은 진행 중, ESSAY-11~17·20은 할 일이다. [Jira 확인](jira-completion.json).

세 팀원의 최종 인계·검토·상태18개 파일을 `team/`에 같은 해시로 보존하고 활성 팀 상태를 삭제했다. 네이티브 에이전트는 모두 완료/유휴 상태이며 MultiAgentV2에는 런타임 archive 기능이 없다. [정리 기록](cleanup.json). 최종12개 제품 해시·보호600개/원본46개·변경/추가161개 파일의 실제 설정 키 비노출·JSON/문서 링크 검사도 통과했다([마지막 확인](final-audit.json)).
