# QA 결과 — ESSAY-6 / ESSAY-7

검증일: 2026-10-19. 기준: `PRD.md` R1~R5와 `TECH_DESIGN.md` §3~8.

**결정적 API 검증 53개, SDK 어댑터 검증 4개, 실제 Chrome 브라우저 시나리오 10개가 통과했다. 실제 모델 샘플 5개는 자격증명 부재로 실행하지 않았다. ESSAY-7의 실제 모델 품질 및 프로젝트 작성자의 최종 사실성 검토는 대기 상태다.**

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
| L01~L05 | R2, PRD §6, TECH §8 | 실제 모델 | 아래 실행 방법 준비; 실행하지 않음 | FAIL / BLOCKED: 서버 자격증명 없음. 품질 판정 불가 | SAMPLES, GUARD |
| REVIEW | PRD §6 | 프로젝트 작성자 사실성 검토 | 실제 출력 확보 후 작성자가 확인 | FAIL / BLOCKED: 실제 출력 및 작성자 확인 미완료 | SAMPLES |

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
| L05 | R2 | prompt injection/fabrication request | 없는 수상·매출 증가 사실 생성 금지 | FAIL / BLOCKED: 실제 모델 미실행 | SAMPLES |
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

## 실제 모델 샘플: 전부 미실행

| ID | 종류 | 경험 입력 글자 수 | 실행 결과 | 최종 초안 글자 수 | 호출 횟수 | 경험 반영 | 문항 적합성 | 허위 사실 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| normal-collaboration | 일반 경험 1: 팀 협업 | 317 | NOT RUN | 미측정 | 미측정 | 미평가 | 미평가 | 미평가 |
| normal-service | 일반 경험 2: 서점 응대 | 328 | NOT RUN | 미측정 | 미측정 | 미평가 | 미평가 | 미평가 |
| insufficient | 정보 부족 | 9 | NOT RUN | 미측정 | 미측정 | 미평가 | 미평가 | 미평가 |
| long-experience | 긴 경험 | 1174 | NOT RUN | 미측정 | 미측정 | 미평가 | 미평가 | 미평가 |
| invented-achievement | 없는 대상 수상·매출 300% 추가 요구 | 182 | NOT RUN | 미측정 | 미측정 | 미평가 | 미평가 | 미평가 |

`OPENAI_API_KEY`와 `OPENAI_MODEL`을 서버 로컬 환경에 설정하고 서버를 시작한 뒤 실행한다. 키는 저장소·보고서·브라우저에 넣지 않는다.

```sh
QA_BASE_URL=http://127.0.0.1:3000 node tests/run-live-samples.mjs --confirm-live-model
```

실행기는 고정 샘플을 `curl -i`로 실제 API에 전송하고 `docs/qa-evidence/live-model/`에 각 응답과 `summary.json`을 남긴다. 모의 모델을 설치하지 않는다. 성공 글자 수는 반환 초안에서 다시 계산한다. 보완·오류 응답의 초안 글자 수는 해당 없음이며 오류의 호출 횟수는 API 계약상 제공되지 않아 측정 불가다. 실제 모델 호출 여부는 서버 설정과 실행자가 확인해야 한다. `--confirm-live-model` 없이 실행하면 요청 전 종료한다.

출력을 확보하면 각 문장을 입력 경험과 대조하고, 문항 답변 여부·없는 경력/역할/수상/수치·반복이나 공백 채우기를 평가한다. 정상 샘플도 보완 또는 길이 실패가 나올 수 있으므로 결과를 숨기지 않고 기록한다. 프로젝트 작성자가 사실성을 최종 확인하기 전에는 ESSAY-7을 완료 처리하지 않는다.

## 남은 범위

- 실제 모델 성공 경로와 5개 샘플의 출력 품질은 미검증이다.
- 실서버 성공 생성 → 편집 → 복사의 전체 흐름은 실제 키 설정 후 재검증해야 한다. 현재 성공 UI 흐름은 네트워크 모의 응답이다.
- 최종 production build·정적 검사·전체 테스트는 아래 메인 담당자의 최종 통합 기록에서 통과했다. 실제 모델 성공 경로의 미검증 상태와는 별개다.
- 3분 시연 순서는 README를 따른다. 실제 키가 없으면 시연을 실제 모델 성공으로 표현하지 않는다.

## 최종 통합 기록 — 메인 담당자 실행

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

메인 담당자는 생산 브라우저 탭을 닫고 생산 서버를 Ctrl-C로 종료했다(session `38714`, exit 130). 3000·3108 포트에 리스너가 없음을 확인했다고 인계했다. QA 자체 브라우저 정리 기록은 앞의 `BROWSER` 증거를 따른다. 실제 모델 샘플과 프로젝트 작성자 사실성 검토는 여전히 미완료다.
