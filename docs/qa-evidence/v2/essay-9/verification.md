# ESSAY-9 공통 기반 검증

- 완료일: 2026-10-19 17:36 KST
- 범위: 사용자가 지정한 ESSAY-9 구현·검증. 네 역할의 실제 업무 구현·API·화면·전체 QA는 ESSAY-10~17이다.
- 기준 커밋: `ba1713f65bde1c38afc7171c01fabd8ec581d011` 이후 로컬 변경. 이번 작업의 커밋·push는 수행하지 않았다.
- 검사한 코드: [SHA-256 목록](code-sha256.txt). 테스트 17:32 KST, HTTP 확인 17:36 KST.
- 판정: ESSAY-9 완료 조건 충족. 기존 v1과 원본 5개 샘플을 보존했다.

## 구현과 완료 조건

| 항목 | 구현 및 확인 |
| --- | --- |
| 공통 계약 | 필수4·선택 공고 URL/본문, 근거 ID, 네 역할 구조화 출력, ready/needs_input/error. Unicode 입력 경계와 실제 초안 801~1,000자 일치 검사 |
| LangGraph | 1.5.1 / core1.2.18 / Zod4.6.7 고정. 실제 StateGraph 병렬 분기에서 도착 순서를 바꾸어 합류1회·입력 불변·요청 격리 확인 |
| 상태 | requestId/input/deadline 불변, nullable 채널의 실제 null 초기값, 수정 횟수0/1과 감소 금지, coordinator 소유 usage |
| 예산 | 모델6회·모델30초·조사45초·요청180초, 동기 예약, 동시 호출·남은 시간·취소·실패 후 무환불, abort를 무시하는 작업에서도 호출자가 종료함 |
| 내장 검색 | 모델1+내장 도구 용량2를 함께 선예약. max_tool_calls=2, 재시도0. 네 동시 요청 중 하나만 전송되며 모델/도구 한도 실패 시 부분 예약 없음 |
| 제공자 | 일반 모델은 도구 없이 strict JSON. 기본 조사는 OpenAI 내장 검색+strict JSON. 경험/문항을 조사 입력에서 제거. 별도 검색/페이지 교체 인터페이스 유지 |
| 제공자 경계 | URL HTTP(S), Unicode 입력 계약 재사용, 불완전/잘못된 출력 차단, 파싱 오류에 원문 미포함, 선택 필드의 required/nullable wire 변환 |
| v1 보존 | 기존 src 파일의 Git 차이 없음. 기존76 테스트 통과. 원본5개 fixture SHA-256 `950c8b3689082481d1943acadbd4c8ac507b5738015e3697978e38fea7059c35` 유지 |

관련 코드: `src/shared/contracts-v2.ts`, `src/server/workflow/{state,budget,providers,native-provider,provider-schemas}.ts` 및 같은 폴더의 테스트.

## 자동 검사와 실제 표면

| 실행 | 결과 | 증거 |
| --- | --- | --- |
| pnpm test | 156 passed / 1 skipped, 10 test files passed. skipped는 별도 환경 플래그가 필요한 실제 유료 검사 | [tests.txt](tests.txt) |
| pnpm typecheck | 통과 | [typecheck.txt](typecheck.txt) |
| pnpm lint | 41개 파일 검사, 수정/경고 없음 | [lint.txt](lint.txt) |
| next build | Next16.4.2 Turbopack 빌드·타입·정적 페이지 생성 통과 | [build-direct.txt](build-direct.txt) |
| 운영 빌드 HTTP | GET / →200, POST /api/drafts {} →400 INVALID_INPUT/필수4필드, POST /api/v2/drafts {} →404 | [http-smoke.jsonl](http-smoke.jsonl) |

현재 개발 서버의 `.next`를 보존하기 위해 소스와 설치 의존성을 임시 폴더에 복사했다. `.env*`·Git·기존 빌드와 증거 폴더는 제외했다. 첫 `pnpm --dir <copy> build`는 복사된 pnpm 메타데이터에 따른 재설치 확인에서 비대화형 오류로 종료했다([원본 로그](build.txt)). 제품 컴파일 실패가 아니며 같은 복사본에서 package.json build의 실제 명령인 `node node_modules/next/dist/bin/next build`를 직접 실행해 통과했다. 이 빌드를 포트3019에 띄워 HTTP를 확인했고 모델 호출은 하지 않았다. 일반 sandbox의 포트 바인딩이 EPERM이라 승인된 실행 권한으로 임시 서버를 구동했다.

## 실제 OpenAI 연결

모델 `gpt-5.6-terra`, reasoning low, SDK7.39.0, store:false, 재시도0. 공개 OpenAI 회사/Software Engineer 직무만 사용했다. 키·사용자 경험·문항은 증거에 없다.

| 요청 | 소요 | 입력/출력 토큰 | 관찰 |
| --- | --- | --- | --- |
| strict JSON | 2,417ms | 33 / 13 | completed, ok:true |
| 내장 검색 | 3,315ms | 8,589 / 52 | search action1, max_tool_calls1 |
| 내장 검색+strict JSON | 3,492ms | 8,702 / 63 | 구조화 URL, search action1, max_tool_calls1 |
| 제품 native adapter+ExecutionBudget | 4,700ms | 8,626 / 97 | 서버 제한2 반환, 도구 보고1, 예약2, 모델1 |

원본: [호환성2회](../../../../.omo/evidence/essay9-providers/live-probe.json), [결합1회](../../../../.omo/evidence/essay9-providers/live-combined.json), [제품 어댑터1회](../../../../.omo/evidence/essay9-providers/live-adapter.json), [실행 로그](../../../../.omo/evidence/essay9-providers/live-adapter-run.txt).

총4회, 입력25,950/출력225토큰. 비용 금액은 청구 자료가 없어 산정하지 않았다. 도구 보고량은 관찰값이며 과금량과 동일하다고 주장하지 않는다. 검색 결과의 URL18개는 읽은 페이지18개라는 뜻이 아니다. 결과는 `verification: unverified`이며 공식 기업·직무 사실의 최종 확인 증거가 아니다.

사용자 승인으로 원래 독립 검색2/페이지3 제한 대신 기본 내장 도구 합계2를 적용했다. 제공자 내부 검색어·페이지 수·페이지 바이트를 앱에서 강제하지 못한다. 별도 주입 검색2/직접 읽기3 카운터는 해당 경로만 계수한다. `nativeToolCallsReserved`는 미사용분을 포함한 예약량이며 `toolCallsReported`와 구분한다.

## 발견·수정과 검토

1. LangGraph nullable 채널의 실제 초기값이 undefined일 수 있어 null/배열/usage 기본값과 런타임 검사를 추가했다. reducer 오류는 typed WorkflowStateError로 통일했다.
2. 검색 입력의 UTF-16 길이 검사와 공통 Unicode 코드 포인트 계약이 달라 공통 스키마를 재사용했다. 검색/페이지 반환 URL도 HTTP(S) 스키마로 검증한다.
3. ResearchResult 선택 URL/날짜가 OpenAI strict JSON helper에서 거절되어 required/nullable wire 스키마와 도메인 정상화를 추가했다. 실패 기록은 제공자 증거 폴더에 보존했다.
4. SDK HTTP 타입에서 max_tool_calls가 누락되어 공식 API에 맞는 intersection payload 타입으로 표현했다. 강제 단언 없이 컴파일하고 실제 API가 제한2를 반환함을 확인했다.
5. 네이티브 계수 통합 도중의 일시적 타입 실패 로그를 보존했다. 최종 전체 typecheck·lint·156테스트는 모두 통과했다.

메인이 계약·상태·예산·제공자 구현과 테스트를 직접 검토하고 실제 빌드/HTTP를 확인했다. 현재 ESSAY-9 범위의 남은 차단 결함은 없다. 개발 스킬의 별도 no-excuse checker는 Bun 부재/설치 TypeScript API 차이로 실행 호환성이 없었다. 대체 TypeScript AST 검사에서 계약/상태의 금지 노드0을 확인했고 전체 타입 검사·lint와 직접 검토를 수행했다. 별도 checker 통과로 보고하지 않는다.

작업자 증거: [계약/상태](../../../../.omo/evidence/essay9-contracts/README.md), [예산](../../../../.omo/evidence/essay9-budget/handoff.md), [제공자](../../../../.omo/evidence/essay9-providers/README.md). 팀 상태·인수인계는 `.omo/evidence/team-0ebb11e1/`에 보존한다.

## 후속 검증 범위

- ESSAY-10: 회사 신원·공식 출처 연결·근거 구절·날짜·직무 적합성. 직접 페이지 reader를 추가한다면 DNS/redirect·크기 제한 검증.
- ESSAY-11~15: 실제 네 역할 프롬프트, 결정적 근거 검사, 제한된 수정, 전체 그래프/API와 화면. 배포 환경의180초 요청 허용 확인.
- ESSAY-16~17: 전체 회귀, 원본5개+추가 공고 사례, 실제 기업2곳, 실제 브라우저, 작성자의 최종 사실성 승인.

ESSAY-9의 실연결과 HTTP 확인을 위 제품 전체 검증으로 간주하지 않는다. [ESSAY-9](https://kmskojb.atlassian.net/browse/ESSAY-9)는 17:39 KST 완료 전환을 확인했다(transition31, 완료 댓글10017). ESSAY-8은 진행 중, ESSAY-10~17은 할 일로 유지한다. 기존 ESSAY-7·v1 QA 승인 기록은 변경하지 않는다.
