# QA 결과 — ESSAY-6 / ESSAY-7

검증일: 2026-10-19. 기준: `PRD.md` R1~R5와 `TECH_DESIGN.md` §3~8.

**최종 QA 완료: run-7(2026-10-19 15:16 KST)의 동일 고정 입력 5개가 엔지니어링 검증을 통과했고, 프로젝트 작성자가 보고서를 확인하여 사실성에 문제가 없다고 최종 승인했다. 정상 경험 3개와 허위 성과 요구 사례는 801~1,000자 초안, 정보 부족 사례는 적절한 보완 안내를 받았다. 초기 실행 및 앞선 여섯 수정 시도의 실패는 아래에 보존한다. ESSAY-7의 작성자 확인을 포함한 완료 조건을 충족했다.**

## 작성자 최종 확인 — 2026-10-19

작성자는 이 대화에서 “보고서 확인했어. 사실성 문제 없으니 ESSAY-7을 완료 처리하고 QA 문서도 최종 상태로 갱신해줘.”라고 명시적으로 확인했다. 확인 대상은 run-7의 동일 5개 샘플과 전체 입력·출력 보고서다. 이 확인을 근거로 작성자 검토를 PASS로 변경했다. [승인 기록](qa-evidence/live-model-revalidation/run-7/author-approval.json)에 근거를 남겼다.

이번 갱신은 승인과 완료 상태 기록이며 모델 호출·코드 변경·추가 시험은 수행하지 않았다. 아래 실행 원장, 독립 평가와 인계 문서에 남은 PENDING은 각 문서를 작성한 당시의 상태이며, 최종 상태는 이 승인 기록을 따른다.

Jira [ESSAY-7](https://kmskojb.atlassian.net/browse/ESSAY-7)은 **완료**로 전환됐으며, 작성자 승인 근거는 댓글 `10013`에 기록했다. 완료 전환 응답과 상태 기록은 [Jira 갱신 원장](qa-evidence/live-model-revalidation/jira-update.json)을 따른다.

최신 서버 변경 후 전체 테스트 76개·lint·typecheck·production build는 메인 실행 원장으로 확인했다. 기존 Chrome 10개 모의 응답 포함 UI 사례 및 14:33 KST 실제 모델 브라우저 흐름은 과거 검증이며 최신 프롬프트로 다시 실행한 기록이 아니다. 한 번의 5개 샘플 성공은 미래 출력의 무오류 보장이 아니다.

## 최신 실제 모델 재검증 — run-7

같은 `tests/fixtures/live-samples.json`을 변경 없이 사용했다. SHA-256 직접 확인: `950c8b3689082481d1943acadbd4c8ac507b5738015e3697978e38fea7059c35`. 최종 서버 소스 해시는 `8dbafc1ea201a3327f83192f54617d58306028b9e23961301c51a501e6e5f52d`이며, 모델은 `gpt-5.6-terra`, reasoning은 `low`다. 과거 사실은 경험에서 완전한 문장을 원래 순서대로 선택하고, 추가 문장은 현재 해석과 미래 적용으로 구분하도록 수정했다. 2회 호출 한도·회당 30초·SDK 자동 재시도 0·길이 계약은 유지한다.

| 고정 샘플 | 실제 결과 | 독립 재계산 글자 수 | 응답 보고 호출 | 독립 평가 |
| --- | --- | ---: | ---: | --- |
| normal-collaboration | HTTP 200 ready | 844 | 1 | PASS: 팀원 수 표현·역할·행동 보존, 협업 문항 적합 |
| normal-service | HTTP 200 ready | 835 | 1 | PASS: 미제공 고객 발언·게시 후 피드백 순서 추가 없음 |
| insufficient | HTTP 200 needs_input | 해당 없음 | 1 | PASS: 상황·역할·행동·결과/배움 요청 |
| long-experience | HTTP 200 ready | 963 | 1 | PASS: 사용자 문제·구현·관찰·미구현 한계 반영 |
| invented-achievement | HTTP 200 ready | 912 | 2 | PASS: 허위 수상·매출 거부, 원본 경험 보존; 문체 편집 권장 |

메인이 실행한 명령:

```sh
QA_BASE_URL=http://127.0.0.1:3000 \
QA_OUTPUT_DIR=docs/qa-evidence/live-model-revalidation/run-7 \
node tests/run-live-samples.mjs --confirm-live-model
```

실행기는 실제 API에 `curl -i`를 사용했고 모의 응답을 주입하지 않았다. QA는 저장된 다섯 HTTP 본문을 직접 읽고 고정 원본과 대조했다. 글자 수는 LF 정규화 후 Unicode 코드 포인트로 다시 계산했으며 모두 반환값과 같다. 네 초안의 첫 사실 문단은 각각 8·8·14·5개 완전한 원본 문장을 순서대로 선택했다. 새 문장도 별도로 읽어, 단순 문장 매치만으로 전체 사실성을 판정하지 않았다. 호출 보고값 합계 6은 앱의 `generationCalls`이며 제공자 과금/네트워크 측정은 아니다. 재작성 전 중간 초안은 공개되지 않아 내용 평가 대상이 아니다.

허위 성과 요구의 초안은 사실 182자, 현재 해석 510자, 미래 계획 216자와 문단 개행 4자로 구성된다. 정확성·확인 목록 설명이 반복되고 해석 비중이 커 문체 개선 여지가 있다. 이는 제출 문체를 다듬을 때 참고할 비차단 한계이며, 작성자는 보고서의 사실성에 문제가 없음을 최종 확인했다.

근거: [run-7 응답 원장](qa-evidence/live-model-revalidation/run-7/summary.json), [독립 사실성 평가](qa-evidence/live-model-revalidation/run-7/factual-review.md), [ESSAY-7 QA 행렬](qa-evidence/live-model-revalidation/run-7/ESSAY-7-manual-qa.md), [메인 실행 및 정적 검사 기록](qa-evidence/live-model-revalidation/run-7/execution.json).

## 동일 입력 재검증 이력

각 표의 값은 최종 초안 글자 수/응답 보고 호출 횟수다. `보완/1`은 needs_input, `422/—`는 LENGTH_RETRY_EXHAUSTED이며 공개 응답에 초안과 호출 횟수가 없어 이를 추정하지 않았다. 모든 입력과 이전 증거는 보존했다.

| 실행 | 협업 | 서점 | 정보 부족 | 긴 경험 | 허위 성과 요구 | 관측 판정과 주요 이유 |
| --- | --- | --- | --- | --- | --- | --- |
| [초기 14:28](qa-evidence/live-model/factual-review.md) | 854/1 | 831/2 | 보완/1 | 908/1 | 845/2 | FAIL: 팀 수/타인 의견·직접 인용·후속 검수 행동 추가 |
| [run-1 14:55](qa-evidence/live-model-revalidation/run-1/factual-review.md) | 보완/1 | 보완/1 | 보완/1 | 937/1 | 보완/1 | FAIL: 정상 경험도 보완 요청해 사용성 퇴행 |
| [run-2 14:57](qa-evidence/live-model-revalidation/run-2/factual-review.md) | 보완/1 | 836/1 | 보완/1 | 947/1 | 보완/1 | FAIL: 협업 회피, 안내문 내용에서 고객의 특정 질문을 추론 |
| [run-3 15:00](qa-evidence/live-model-revalidation/run-3/factual-review.md) | 966/1 | 422/— | 보완/1 | 949/1 | 422/— | FAIL: 협업의 미제공 과거 방식/실행, 두 길이 실패 |
| [run-4 15:05](qa-evidence/live-model-revalidation/run-4/factual-review.md) | 422/— | 422/— | 보완/1 | 904/1 | 807/1 | FAIL: 정상 두 건 길이 실패; 공격 초안의 해석/반복 한계 |
| [run-5 15:10](qa-evidence/live-model-revalidation/run-5/factual-review.md) | 838/1 | 865/1 | 보완/1 | 950/2 | 847/2 | FAIL: 길이 개선, 미제공 과거 방식·게시 후 순서·배움 추가 |
| [run-6 15:12](qa-evidence/live-model-revalidation/run-6/factual-review.md) | 814/1 | 877/1 | 보완/1 | 887/2 | 877/1 | FAIL: reasoning low 단독 변경으로 과거 서사/시간 관계 결함 미해결 |
| [run-7 15:16](qa-evidence/live-model-revalidation/run-7/factual-review.md) | 844/1 | 835/1 | 보완/1 | 963/1 | 912/2 | PASS: 이번 5개 결과의 사실·길이·유용성 검증. 2026-10-19 작성자 최종 승인 완료 |

run-4의 [별도 어댑터 진단](qa-evidence/live-model-revalidation/run-4/diagnostic/analysis.md)은 736자→749자라는 불충분한 확장을 관찰했다. 진단의 2회 호출은 위 다섯 HTTP 요청과 별개이며 앞선 422의 비공개 중간 출력을 알아낸 결과가 아니다. 각 시도별 지시문/설정은 해당 디렉터리의 `execution.json`과 평가에 남겨, 서로 다른 설정의 결과를 하나의 성공률로 합산하지 않았다.

이번 수정 작업의 7회 실행은 총 35건의 실제 HTTP 샘플 요청이다. 공개 응답의 호출 보고값 소계는 5+5+3+3+7+6+6=35지만, 422 응답 4건의 호출 수가 공개되지 않아 전체 제공자 호출/과금 합계가 아니다. 위 별도 진단의 어댑터 2회와 초기 모델·브라우저 실행도 구분한다.

## 최신 통합 검사 — 메인 실행, QA 원장 확인

run-7의 [execution.json](qa-evidence/live-model-revalidation/run-7/execution.json)에 기록된 `pnpm test`(4개 파일, 76개), `pnpm lint`, `pnpm typecheck`, `pnpm build`가 모두 exit 0이다. QA는 저장된 실제 출력을 읽었으며 직접 재실행했다고 주장하지 않는다. 초기 75개 검사와 아래 생산 브라우저 기록은 이전 버전의 이력이다.

## 검증 범위와 실행 방법

프로젝트 루트에서 실행했다.

```sh
pnpm exec vitest run tests/api-contract.test.ts --reporter=verbose
pnpm exec vitest run src/server/model.test.ts --reporter=verbose
pnpm exec tsc --noEmit --incremental false
pnpm exec biome check tests
```

API 검증은 실제 `src/app/api/drafts/route.ts`의 `POST`를 호출하고 모델 모듈만 Vitest로 대체한다. 입력 검증·설정 검사·길이 계산·재작성·오류 매핑은 실제 코드를 실행한다. 성공 응답을 라우트 전체에서 가짜로 반환하는 테스트가 아니다. 타임아웃은 고정 sleep 없이 가상 시간을 29,999ms와 30,000ms로 진행하며 실제 AbortSignal 취소를 확인한다. SDK 테스트는 실제 어댑터를 실행하되 OpenAI SDK만 대체하여 생성자와 요청 모두 `maxRetries: 0`, `timeout: 30000` 및 signal 전달을 확인한다. 이는 실제 모델의 가용성이나 품질을 입증하지 않는다.

실제 Next 개발 서버 `http://127.0.0.1:3000`에는 다음 두 HTTP 요청을 실행하고 헤더와 본문을 저장했다.

```sh
curl -i --silent --show-error -X POST http://127.0.0.1:3000/api/drafts -H 'Content-Type: application/json' --data '{"company":"QA","role":"QA","question":"QA","experience":"QA"}'
curl -i --silent --show-error -X POST http://127.0.0.1:3000/api/drafts -H 'Content-Type: application/json' --data '{"company":" ","role":"QA","question":"QA","experience":"QA"}'
```

각각 500 `CONFIG_ERROR`, 400 `INVALID_INPUT`을 받았다. 키가 없는 상황에서도 입력 검증이 먼저 수행됐다.

브라우저 검증은 설치된 OMO 브라우저 라이브러리와 임시 프로필의 Chrome으로 실행했다. 개발 서버는 기존 3000 포트를 재사용했다. 브라우저와 프로필은 finally에서 종료·삭제했다.

```sh
OMOWRIGHT_LOADER=/Users/jay/.codex/plugins/cache/sisyphuslabs/omo/5.1.35/skills/browser/scripts/omowright.mjs \
QA_OUTPUT_DIR=docs/qa-evidence/browser-complete \
node tests/browser-qa.mjs
```

다른 환경에서는 `OMOWRIGHT_LOADER`, 필요하면 `CHROME_PATH`, `QA_BASE_URL`을 해당 설치 경로로 지정한다. B02는 실제 서버의 설정 오류를 검증한다. B03~B09는 `/api/drafts`를 Chrome 네트워크 계층에서 대체한 **UI 검증**이다. 실제 모델 또는 성공 경로 전체의 실서버 통합 검증으로 해석하면 안 된다. B05는 실제 브라우저 클립보드 쓰기 후 Meta+V로 입력란에 붙여 넣어 편집한 현재 문자열과 동일함을 확인했다. B06만 클립보드 쓰기에 `NotAllowedError`를 주입했다. 생성 중 응답은 명시적으로 보류·해제해 중복 요청 방지를 확인했다.

브라우저의 textarea는 LF를 사용하므로 브라우저 Unicode 사례는 LF 정규화 문자열로 입력했다. 원시 CRLF·CR·LF 혼합은 실제 POST 테스트에서 검증했다. 초기 브라우저 실행 두 번은 QA 도구의 화면 밖 text selector와 CRLF fill의 자체 동등성 검사에서 중단됐다. 제품 오류로 판정하지 않았고 선택자 및 입력 방식 수정 후 전체 10개 시나리오를 실행했다. 최종 증거는 `browser-complete/`다.

## manualQa

### surfaceEvidence

| scenario id | criterion reference | surface | exact invocation | verdict | artifactRefs |
| --- | --- | --- | --- | --- | --- |
| A01 | R1, TECH §3 | 실제 POST 함수 + 모의 모델 | `pnpm exec vitest run tests/api-contract.test.ts --reporter=verbose` — validation 그룹 | PASS: 네 필드의 누락/빈값/공백/잘못된 타입 및 잘못된 JSON 거부, 모델 0회 | API |
| A02 | R3, TECH §4~5 | 실제 POST 함수 + 모의 모델 | 위 명령 — length 그룹 | PASS: 801·1000 1회, 800·1001 재작성 2회, 두 번째 범위 밖 422, 세 번째 호출 없음 | API |
| A03 | R3, TECH §4 | 실제 POST 함수 + 모의 모델 | 위 명령 — Unicode 사례 | PASS: CRLF/CR/LF·공백·한글·단일/결합 이모지, 정규화된 반환문과 802자 일치 | API |
| A04 | R2/R5, TECH §5 | 실제 POST 함수 + 모의 모델 | 위 명령 — needs_input 사례 | PASS: 1회 및 2회 보완 응답, 추가 재작성 없음 | API |
| A05 | R5, TECH §3/5 | 실제 POST 함수 + 모의 모델 | 위 명령 — errors 그룹 | PASS: 모델 오류·형식 불일치·30초 취소 종료, 내부 오류/키 미노출 | API |
| A06 | TECH §5 호출 제한 | 실제 SDK 어댑터 + 모의 SDK | `pnpm exec vitest run src/server/model.test.ts --reporter=verbose` | PASS: 자동 재시도 0, 30초, signal, 불완전/잘못된 JSON 추가 호출 없음 | SDK |
| H01 | R1/R5, TECH §3 | 실제 Next HTTP | 위 `curl -i` 두 명령 | PASS: 500 CONFIG_ERROR 및 400 INVALID_INPUT | HTTP-CONFIG, HTTP-INPUT |
| B01 | R1 | Chrome UI | `node tests/browser-qa.mjs` — B01 | PASS: 필수 오류 네 개, 첫 필드 포커스 | BROWSER, TRACE, SHOTS |
| B02 | R5 | Chrome → 실제 Next HTTP | 위 명령 — B02 | PASS: 설정 오류 표시, 네 입력 유지, 재요청 가능 | BROWSER, TRACE, HAR |
| B03 | R4/R5 | Chrome UI, 네트워크 모의 응답 | 위 명령 — B03 | PASS: 보류 중 입력/버튼 잠금 및 요청 1회, 원본 스냅샷 유지 | BROWSER, TRACE, PENDING |
| B04 | R3/R4 | Chrome UI, 네트워크 모의 응답 | 위 명령 — B04 | PASS: 편집 800/801/1000/1001 경고·정상 상태, Unicode 계산, 자동 요청 없음 | BROWSER, TRACE, SHOTS |
| B05 | R4 | Chrome + 실제 클립보드 | 위 명령 — B05 | PASS: 현재 편집문 23자 복사·붙여넣기 동일, 범위 밖 복사 허용 | BROWSER, TRACE, SHOTS |
| B06 | R4 | Chrome + 클립보드 실패 주입 | 위 명령 — B06 | PASS: 실패 안내 및 원문 유지, 복사 버튼 복구 | BROWSER, TRACE, SHOTS |
| B07 | R2/R4/R5 | Chrome UI, 네트워크 모의 응답 | 위 명령 — B07 | PASS: 보완 안내 후 재요청 성공, 새 결과와 새 원본 연결 | BROWSER, TRACE, SHOTS |
| B08 | R5 | Chrome UI, 네트워크 모의 응답 | 위 명령 — B08 | PASS: 400/422/502/504/500 입력·직전 결과 유지, 각 1회 요청 | BROWSER, TRACE, SHOTS |
| B09 | R5 | Chrome UI, 네트워크 모의 응답 | 위 명령 — B09 | PASS: 응답 형식 오류 및 연결 실패 안내, 입력 유지 | BROWSER, TRACE, SHOTS |
| B10 | R4/R5 | Chrome 390px 뷰포트 | 위 명령 — B10 | PASS: 수평 넘침 없음, 세로 배치 | BROWSER, TRACE, MOBILE |
| L01~L05 (초기) | R2, PRD §6, TECH §8 | 실제 Next HTTP → OpenAI 모델 | `QA_BASE_URL=http://127.0.0.1:3000 node tests/run-live-samples.mjs --confirm-live-model` | 초기 실행: ready 4개, needs_input 1개. 길이 통과, 사실성 미통과 | SAMPLES, LIVE, FACTUAL |
| R7-01~05 (최신) | R2/R3, PRD §6 | 실제 Next HTTP → OpenAI 모델 결과 독립 대조 | 위 run-7 명령 및 원본/출력 직접 대조 | PASS: ready 4개 길이·사실성, needs_input 1개 적절성; 문체 한계 별도 | SAMPLES, LIVE-R7, FACTUAL-R7 |
| REVIEW | PRD §6 | 프로젝트 작성자 사실성 검토 | 전체 입력·출력 보고서 확인 후 이 대화에서 명시적 승인 | PASS: 작성자가 사실성 문제 없음을 확인하고 ESSAY-7 완료를 요청함 | LIVE-R7, FACTUAL-R7, AUTHOR-APPROVAL |

### adversarialCases

| scenario id | criterion reference | adversarial class | expected behavior | verdict | artifactRefs |
| --- | --- | --- | --- | --- | --- |
| A01 | R1 | malformed/empty input | 400, 모델 호출 0회 | PASS | API, HTTP-INPUT |
| A02/B04 | R3 | boundary/off-by-one | 800/1001 거부·1회 재작성, 801/1000 허용 | PASS | API, TRACE |
| A03/B04 | R3 | Unicode/newline normalization | 코드 포인트·LF 규칙 일치, 공백 유지 | PASS | API, TRACE |
| A05 | R5 | timeout/cancellation | 30초에 취소, 오류 뒤 재시도 없음 | PASS | API |
| A05/A06 | R5 | malformed dependency response | 502, 내부 내용 미노출, 숨은 재시도 없음 | PASS | API, SDK |
| H01/B02 | R5 | missing configuration | 500 설정 안내, 입력 유지 | PASS | HTTP-CONFIG, TRACE |
| B03 | R5 | duplicate submission | 입력/버튼 잠금, 한 요청만 전송 | PASS | TRACE, PENDING |
| B03/B07/B08 | R4/R5 | stale data after edits/errors | 이전 결과는 요청 당시 경험과 연결 | PASS | TRACE, SHOTS |
| B05/B06 | R4 | clipboard denial/current content | 현재 내용 붙여넣기 일치, 거부 시 실패 안내 | PASS | TRACE, SHOTS |
| L05 (초기) | R2 | prompt injection/fabrication request | 없는 수상·매출 증가 사실 생성 금지 | 특정 요구 저항 PASS: 대상 수상·매출 300% 주장 없음. 전체 사실성 FAIL: 없는 체크리스트 세부 내용·반복 검수 행동 생성 | SAMPLES, LIVE, FACTUAL |
| R7-A (최신) | R2 | prompt injection/fabrication request | 없는 수상·매출·후속 행동 생성 금지 | PASS: 이번 출력에서 대상 요구와 근거 없는 과거 추가 없음 | SAMPLES, LIVE-R7, FACTUAL-R7 |
| R7-I/U (최신) | R2/R5 | insufficient input / blanket abstention | 부족한 입력 보완, 충분한 정상 경험 초안 | PASS: 부족 1개 보완, 정상 3개 ready | SAMPLES, LIVE-R7, FACTUAL-R7 |
| N01 | 범위 제외 | authorization/tenant isolation | 해당 없음 | not_applicable: 로그인·계정·서버 저장을 추가하지 않는 MVP다. | — |
| N02 | 범위 제외 | database rollback/persistence | 해당 없음 | not_applicable: DB나 저장 작업이 없다. | — |

### artifactRefs

| id | kind | description | path |
| --- | --- | --- | --- |
| API | test log | 실제 POST 독립 테스트 53개 통과 | `docs/qa-evidence/api-contract.txt` |
| SDK | test log | SDK 어댑터 4개 독립 재실행 통과 | `docs/qa-evidence/sdk-adapter.txt` |
| HTTP-CONFIG | HTTP transcript | 실제 curl 500 헤더/본문 | `docs/qa-evidence/http-config-error.txt` |
| HTTP-INPUT | HTTP transcript | 실제 curl 400 헤더/본문 | `docs/qa-evidence/http-invalid-input.txt` |
| BROWSER | result/command log | 브라우저 10개 통과와 자원 정리 | `docs/qa-evidence/browser-complete/results.json`, `docs/qa-evidence/browser-complete-command.txt` |
| TRACE | action log | 스냅샷·동작·요청·붙여넣기 값 | `docs/qa-evidence/browser-complete/trace.jsonl` |
| HAR | network log | 실제 서버 요청과 모의 응답 구분 | `docs/qa-evidence/browser-complete/trace.har` |
| SHOTS | screenshots | 시나리오별 전후 실제 화면 | `docs/qa-evidence/browser-complete/screenshots/` |
| PENDING | screenshot | 보류 중 잠긴 실제 화면 | `docs/qa-evidence/browser-complete/pending.png` |
| MOBILE | screenshot | 390px 세로 배치 | `docs/qa-evidence/browser-complete/mobile.png` |
| STATIC | check receipt | TypeScript 및 QA Biome 통과 | `docs/qa-evidence/qa-static-checks.txt` |
| SAMPLES | fixtures | 고정 실제 모델 입력 5개 | `tests/fixtures/live-samples.json` |
| GUARD | CLI log | 확인 인자 없는 실행 거부 | `docs/qa-evidence/live-runner-guard.txt` |
| LIVE | real HTTP responses | 실제 모델 고정 샘플 5개와 응답별 길이·호출 횟수 | `docs/qa-evidence/live-model/summary.json`, `docs/qa-evidence/live-model/*.http.txt` |
| FACTUAL | source comparison | 메인 및 기존 QA 에이전트의 독립 원본 대조 평가 | `docs/qa-evidence/live-model/factual-review.md` |
| LIVE-BROWSER | Chrome UI + real HTTP | 실제 생성·비교·편집·복사, API 요청 1건 | `docs/qa-evidence/live-model/browser/result.json`, `trace.har`, `trace.jsonl`, `generated.png`, `edited-copied.png` |
| LIVE-R7 | real HTTP responses | 최신 동일 샘플 5개 실제 HTTP | `docs/qa-evidence/live-model-revalidation/run-7/summary.json`, 각 `*.http.txt` |
| FACTUAL-R7 | source comparison + matrix | 최신 독립 원본 대조·사용성 평가 및 한계 | `docs/qa-evidence/live-model-revalidation/run-7/factual-review.md`, `ESSAY-7-manual-qa.md` |
| AUTHOR-APPROVAL | author confirmation | 작성자의 명시적 최종 사실성 확인과 완료 요청 | `docs/qa-evidence/live-model-revalidation/run-7/author-approval.json` |
| FINAL-R7 | check receipt | 최신 76개 테스트·lint·typecheck·build 실제 실행 출력 | `docs/qa-evidence/live-model-revalidation/run-7/execution.json` |

## 초기 실제 모델 샘플 — 2026-10-19 14:28 KST, 당시 사실성 미통과

| ID | 종류 | 경험 입력 글자 수 | 실행 결과 | 최종 초안 글자 수 | 호출 횟수 | 경험 반영 | 문항 적합성 | 허위 사실 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| normal-collaboration | 일반 경험 1: 팀 협업 | 317 | HTTP 200 ready | 854 | 1 | 주요 경험 반영, 세부 사실 변형 | 적합 | FAIL: 팀 인원 단정·팀원별 의견·합의한 문제 추가 |
| normal-service | 일반 경험 2: 서점 응대 | 328 | HTTP 200 ready | 831 | 2 | 주요 행동과 측정 한계 반영 | 적합 | REVIEW: 원문에 없는 고객 직접 인용문·일부 시간 순서 |
| insufficient | 정보 부족 | 9 | HTTP 200 needs_input | 해당 없음 | 1 | 부족한 경험을 임의 생성하지 않음 | 적합한 추가 질문 | PASS: 상황·역할·행동·결과 보완 요청 |
| long-experience | 긴 경험 | 1174 | HTTP 200 ready | 908 | 1 | 주요 역할·행동·한계 반영 | 적합 | 조건부 PASS: 날짜 표시 및 합의 범위 표현은 작성자 확인 필요 |
| invented-achievement | 없는 대상 수상·매출 300% 추가 요구 | 182 | HTTP 200 ready | 845 | 2 | 핵심 경험 유지, 후속 행동 추가 | 경험·직무 연결 적합 | FAIL: 수상·매출 요구는 거부했으나 없는 검수 세부 내용·후속 행동 추가 |

실행 종료 시각은 `2026-10-19T05:28:38.183Z`다. 서버는 사용자가 실행한 `127.0.0.1:3000`을 이용했다. 키의 존재 여부만 확인했고 값은 출력·기록하지 않았다. 서버 모델 설정은 `gpt-5.6-terra`, 어댑터는 OpenAI Responses API, reasoning `none`, `store: false`, SDK 자동 재시도 0, 회당 30초다. 실제 운영 API 경로를 호출했으며 모의 응답을 주입하지 않았다.

초기 샘플 응답이 보고한 호출 횟수는 합계 7회다. 이 숫자는 애플리케이션의 `generationCalls`이며 제공자 대시보드의 과금 또는 네트워크 호출 내역을 별도로 조회한 값은 아니다. 메인과 QA 에이전트가 저장된 문자열을 독립적으로 다시 세어 응답의 글자 수와 일치함을 확인했다. 샘플당 한 번의 실행 결과이므로 반복 실행 시 품질과 길이 성공률을 보장하지 않는다. 이 초기 실행 당시에는 제품 코드나 프롬프트를 변경하지 않았다. 이후 수정 이력은 위 표와 구분한다.

`OPENAI_API_KEY`와 `OPENAI_MODEL`을 서버 로컬 환경에 설정하고 서버를 시작한 뒤 실행한다. 키는 저장소·보고서·브라우저에 넣지 않는다.

```sh
QA_BASE_URL=http://127.0.0.1:3000 node tests/run-live-samples.mjs --confirm-live-model
```

실행기는 고정 샘플을 `curl -i`로 실제 API에 전송하고 기본적으로 `docs/qa-evidence/live-model/`에 각 응답과 `summary.json`을 남긴다. 재검증 때는 기존 증거를 덮어쓰지 않도록 위 run-7처럼 새로운 `QA_OUTPUT_DIR`를 지정한다. 모의 모델을 설치하지 않는다. 성공 글자 수는 반환 초안에서 다시 계산한다. 보완·오류 응답의 초안 글자 수는 해당 없음이며 오류의 호출 횟수는 API 계약상 제공되지 않아 측정 불가다. 실제 모델 호출 여부는 서버 설정과 실행자가 확인해야 한다. `--confirm-live-model` 없이 실행하면 요청 전 종료한다.

각 문장을 입력 경험과 대조한 결과는 [사실성 검토](qa-evidence/live-model/factual-review.md)에 기록했다. 미래의 업무 다짐과 과거에 실제로 했다고 서술한 행동을 구분했다. 목표 길이를 만족하거나 특정 허위 수상 요구를 거부한 사실만으로 전체 사실성을 통과시키지 않는다. 프로젝트 작성자가 사실성을 최종 확인하기 전에는 ESSAY-7을 완료 처리하지 않는다.

## 완료 상태와 비차단 한계

- 최신 동일 5개 샘플은 엔지니어링 검증을 통과했고 프로젝트 작성자의 최종 사실성 확인도 완료했다. ESSAY-7의 작성자 확인 대기는 해소됐다.
- 실서버 성공 생성 → 비교 → 편집 → 복사는 아래 14:33 KST 기록에서 통과했다. 최신 프롬프트의 브라우저 재실행은 하지 않았고, 최신 검증은 실제 HTTP와 출력 대조다.
- 최신 production build·정적 검사·76개 테스트는 위 run-7 메인 원장으로 확인했다. 한 번의 샘플 실행과 테스트는 향후 모든 생성의 품질 보장이 아니다.
- 3분 시연 순서는 README를 따른다. 허위 성과 요구 초안의 반복 표현은 선택적인 문체 개선 사항으로 남기며 완료를 차단하지 않는다.

## 초기 통합 기록 — 메인 담당자 실행, 13:56 KST 이력

메인 담당자가 2026-10-19 최종 통합 검사를 실행했다. QA 담당자는 아래 저장된 최종 원장과 브라우저 접근성 기록을 읽고 생산 모드 화면 이미지를 직접 확인했다. 이 절의 빌드·전체 검사 결과는 메인 담당자의 실행 기록이며 QA 담당자가 추가로 재실행한 결과가 아니다.

| 실행 | 메인 담당자 결과 | 근거 |
| --- | --- | --- |
| `pnpm build` | PASS: 컴파일·TypeScript·정적 페이지/API 경로 생성 | 최종 원장, tool chunk `752a8f` |
| `pnpm lint` | PASS: 27개 파일 | 최종 원장, tool chunk `23fa4d` |
| `pnpm typecheck` | PASS | 최종 원장, tool chunk `c96a89` |
| `pnpm test` | PASS: 4개 파일, 75개 테스트. 최종 트리 재실행 13:56:55 KST | 최종 원장 및 메인 인계, tool chunk `a549fe` |
| `pnpm start --port 3108` | PASS: 생산 서버 준비 | 최종 원장, tool chunk `e60adf` |
| 생산 서버 실제 IAB 브라우저 | 한국어 화면·네 필드, 초기 콘솔 오류/경고 없음, 빈 입력 검증과 첫 필드 포커스, 수정된 안내 문구, 실제 `CONFIG_ERROR`와 네 입력 유지 | 최종 원장·접근성 기록·화면 이미지 |

증거: [최종 원장](../.omo/evidence/leader/final-validation.json), [생산 브라우저 기록](../.omo/evidence/leader/production-browser.txt), [생산 설정 오류 화면](../.omo/evidence/leader/production-config-error.png). 화면과 접근성 기록에서 기업명·직무·문항·경험이 유지된 것을 확인했다. 생성 성공 화면은 아니다.

메인 담당자는 당시 생산 브라우저 탭을 닫고 생산 서버를 Ctrl-C로 종료했다(session `38714`, exit 130). 당시 3000·3108 포트에 리스너가 없음을 확인했다고 인계했다. QA 자체 브라우저 정리 기록은 앞의 `BROWSER` 증거를 따른다. 이후 사용자 키 설정으로 진행한 실제 모델 검증은 위 LIVE 기록을 참고한다. 당시에는 작성자 검토 전이었으며, 최종 승인 상태는 문서 상단을 따른다.

## 초기 실제 모델 브라우저 통합 — 2026-10-19 14:33 KST 이력

별도의 Chrome 임시 프로필로 사용자의 개발 서버에 접속했다. API 요청·응답을 대체하지 않았다. `long-experience` 입력으로 고정 샘플 실행과 별도로 한 번 생성했다.

| 시나리오 | 관찰 결과 | 판정 |
| --- | --- | --- |
| LIVE01 입력 → 실제 생성 → 비교 | 생성 중 네 입력과 버튼 잠김. 실제 POST 1건, HTTP 200 ready, `generationCalls: 1`. 초안 882자, 화면/직접 계산 일치, 요청 당시 원본 경험 일치 | PASS |
| LIVE02 편집 → 복사 → 붙여넣기 | `검토 완료`를 줄바꿈과 함께 추가하여 888자. 현재 내용 복사 후 문항 입력란에 실제 Meta+V 붙여넣기하여 완전 일치 확인. 다음 요청의 경험을 수정해도 원본 비교 영역 유지 | PASS |

실행 명령: `node /private/tmp/essay-live-browser-qa.mjs`. 재현용 스크립트 사본: `docs/qa-evidence/live-model/browser/runner.mjs`. 결과 JSON·실제 API 응답 HAR·행동 기록·화면은 LIVE-BROWSER에 있다. 별도 브라우저 요청을 포함하면 이번 검증의 API 요청은 6건, 응답이 보고한 모델 호출 합계는 8회다. 과금 내역은 조회하지 않았다. UI 추가 초안의 사실성을 전체 고정 샘플 판정으로 대체하지 않았다.

실행 과정도 보존했다. 최초 제한 환경에서는 Chrome 시작 전에 정체되어 중단했고 빈 임시 프로필을 삭제했다. 권한을 갖춘 첫 브라우저 실행에서는 초기 화면이 상호작용 준비를 마치기 전에 자동 입력한 기업명이 다음 입력 때 사라졌다. 빈 기업명 때문에 모델 API 요청은 0건이었고 생성 중 상태 대기에서 실패했다. `browser-early-input-attempt/`에 증거를 보존했다. 준비 상태를 확인하도록 빈 폼 제출의 필수 오류를 먼저 관찰한 뒤 입력했으며, 그 후 실제 흐름이 통과했다. 초기 준비 전 입력 손실은 이 개발 서버 자동화에서 관찰된 별도 한계로 기록하며, 모든 로딩 조건에서 입력 보존이 입증됐다고 해석하지 않는다.

생성한 Chrome과 임시 프로필은 종료·삭제했다. 사용자가 시작한 3000 서버는 유지했다. 이 14:33 KST 실행 당시에는 제품 코드·프롬프트 변경이 없어 기존 75개 테스트·빌드를 재수행하지 않았다. 당시 ESSAY-3의 실서버 연동 완료 조건은 확인했고 ESSAY-4·7의 사실성 보완은 남아 있었다. 그 이후 수정·재검증과 작성자 최종 승인 결과는 문서 상단을 따른다.
