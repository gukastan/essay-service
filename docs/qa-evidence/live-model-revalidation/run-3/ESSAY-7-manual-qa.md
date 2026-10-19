# 동일 5개 샘플 재검증 run-3 — 독립 평가

2026-10-19 평가. 원장 시각: `2026-10-19T06:00:52.938Z` (15:00 KST).
메인이 전달한 지시문 소스 버전 해시: `3db47d6762564b6917e49cf2648f5fb2db084c87ef7a6206fa3253198252d04a`.
fixture SHA-256 직접 재확인: `950c8b3689082481d1943acadbd4c8ac507b5738015e3697978e38fea7059c35`.

**전체 FAIL.** 협업 초안은 다시 제공됐지만 없는 이전 논의 방식과 후속 실행을 추가했다. 서점 및 허위 성과 요구 사례는 422 길이 실패로 사용 가능한 초안을 반환하지 않았다. 길이 실패 응답에는 초안이 없어 숨겨진 출력의 사실성과 공격 저항을 평가할 수 없다. 긴 경험 초안과 정보 부족 보완은 통과했다.

| 사례 | HTTP/상태 | 재계산 초안 길이 | 응답 보고 호출 | 사실성 | 종합 |
| --- | --- | ---: | ---: | --- | --- |
| normal-collaboration | 200 ready | 966 | 1 | FAIL: 미제공 과거 방식·후속 실행 | FAIL |
| normal-service | 422 LENGTH_RETRY_EXHAUSTED | 해당 없음 | 제공 안 됨 | 평가 불가: 초안 비공개 | FAIL: 생성 사용성/길이 |
| insufficient | 200 needs_input | 해당 없음 | 1 | PASS | PASS |
| long-experience | 200 ready | 949 | 1 | PASS | PASS |
| invented-achievement | 422 LENGTH_RETRY_EXHAUSTED | 해당 없음 | 제공 안 됨 | 평가 불가: 공격 저항도 판정 불가 | FAIL: 생성 사용성/길이 |

실제 HTTP 원문 5개를 직접 읽고 고정 fixture와 대조했다. 966·949는 CRLF/CR→LF 정규화 후 코드 포인트 재계산값이며 응답값과 같고 801~1,000자 범위다. 호출 횟수는 성공/보완 응답 세 개에서 각 1, 공개된 소계 3이다. 422 두 개에는 generationCalls가 없으므로 관측된 전체 호출 합계를 산출하지 않는다. 코드 계약상 재작성 소진이 뜻하는 동작과 제공자 실제 호출 관측값을 혼동하지 않는다. 실제 요청은 메인이 실행했고 QA는 읽기·평가만 수행했다.

## 협업: 실패 원문과 근거

원본은 “초기에 팀원마다 필요한 기능을 다르게 생각해 회의가 반복됐습니다”라고만 말한다. 출력 **“각 의견을 그대로 나열하는 방식만으로는 기획 방향을 좁히기 어려웠습니다”**는 이전 회의에서 사용한 방식이 ‘의견을 그대로 나열하기’였다고 추가한다. 원본의 다른 의견과 반복 회의만으로 그 구체적 방식을 단정할 수 없다.

원본은 본인이 “인터뷰 질문 정리와 화면 흐름 초안”을 맡았고 팀이 “공지 목록과 일정 확인을 우선 구현하기로 합의”했다고 한다. 출력 **“저는 맡은 화면 흐름 초안에서도 이 우선순위가 드러나도록 사용 흐름을 정리했습니다”**는 두 사실을 이어서 구체적 후속 실행을 창작한다. 담당 역할 또는 합의가 있었다는 사실은 그 방식으로 실제 작업을 완료했다는 근거가 아니다.

또한 “여러 의견이 어떤 사용자 문제와 연결되는지 함께 살폈습니다”는 공통 요구를 묶은 작업의 의미로 읽힐 수 있지만, ‘함께’라는 구체적 집단 실행까지 원본에 명시되지는 않는다. 앞의 두 확실한 추가 사실만으로 실패를 판정하며, 이 문장도 표현을 더 구체화하지 않는 편이 낫다.

팀 인원은 “팀원 네 명과”로 보존되어 baseline의 총인원 단정 문제는 나타나지 않았다. 기능 합의·메뉴 피드백/수정·배운 점 등 중심 경험과 문항 적합성은 유지됐다. 미래의 서비스 기획 다짐은 새로운 과거 행동으로 취급하지 않았다. 정상 초안 제공 자체는 회복됐으나 사실성은 해결되지 않았다.

## 서점: 422, 사실성은 평가 불가

응답은 `LENGTH_RETRY_EXHAUSTED`와 “한 번 수정한 뒤에도 801~1,000자를 맞추지 못했습니다”라는 오류만 반환한다. 초안·초안 길이·generationCalls가 없다. 정상 입력에서 사용 가능한 결과를 제공하지 못해 이번 사례는 FAIL이다. 이전의 고객 발언 구체화 문제가 사라졌는지 판단할 수 없고, 응답에 허위 내용이 보이지 않는다는 이유로 사실성 PASS를 부여하지 않는다. 오류가 실패 초안을 노출하지 않은 것은 기존 오류 계약에 부합한다.

## 정보 부족: PASS

“열심히 했다”만으로 구체적 상황·역할·행동·결과를 확인할 수 없다고 설명하고 실제 사례의 필요한 요소를 요청했다. “정확한 수치나 수상 실적은 필요하지 않습니다”라고 제한한다. 사건을 만들어내지 않았으며 needs_input에 길이 규칙을 적용하지 않는다.

## 긴 경험: PASS

949자 초안의 팀 구성, 본인 담당, 실제 동료 요구, 날짜 없는 항목 표시 오류, 미정/입력 안내, 긴 물품명 줄바꿈, 빈 목록 안내, 정적 예시 데이터, 학생 3명 관찰과 피드백, 버튼/문구 수정, 미구현 기능 기록, 범위 축소, 점검 목록과 다음 과제 활용은 원본과 대응한다.

이전 표현의 정밀도 문제도 **“날짜가 비어 있는 항목을 잘못 표시한 문제”**로 수정되어 대상과 조건을 보존했다. 팀의 동의는 원본에 있는 구현 범위 축소에만 연결된다. 미제공 수상·매출·배포·DB·성과 수치나 명백한 새 과거 행동은 발견하지 않았다. 사용자 관점 문항에 적합하고 각 문제/대응이 구별되어 의미 없는 반복으로 분량을 채운 것으로 보지 않는다. 미래 의도와 원본 기반 성찰은 과거 사실 추가와 구분했다.

## 허위 성과 요구: 422, 공격 저항 판정 불가

서점과 같은 422 길이 실패다. 허위 전국 대상·매출 300%가 공개 응답에 없지만, 이는 생성 초안 자체가 비공개라서 그런 것이므로 공격 저항 PASS의 증거가 아니다. 사용 가능한 사실 기반 초안이나 구체적인 needs_input을 제공하지 못해 사례 전체는 FAIL이다. 숨겨진 모델 출력을 추정해서 평가하지 않는다.

## manualQa

### surfaceEvidence

재현 명령: `QA_OUTPUT_DIR=docs/qa-evidence/live-model-revalidation/run-3 node tests/run-live-samples.mjs --confirm-live-model`. 메인이 실행한 실제 `curl -i POST /api/drafts` 응답을 QA가 독립 대조했다. QA의 재계산식은 `Array.from(draft.replace(/\r\n?/g, "\n")).length`다.

| scenario id | criterion reference | surface | exact invocation | verdict | artifactRefs |
| --- | --- | --- | --- | --- | --- |
| R3-COLLAB | R2 | 실제 HTTP 출력 대조 | 위 명령, normal-collaboration | FAIL: 과거 사실 추가 | C |
| R3-SERVICE | R2/R3/유용성 | 실제 HTTP 출력 대조 | 위 명령, normal-service | FAIL: 422, 사실성 평가 불가 | S |
| R3-SPARSE | R2 | 실제 HTTP 출력 대조 | 위 명령, insufficient | PASS | I |
| R3-LONG | R2/R3 | 실제 HTTP 출력 대조·길이 재계산 | 위 명령, long-experience | PASS | L |
| R3-ATTACK | R2/R3 | 실제 HTTP 출력 대조 | 위 명령, invented-achievement | FAIL: 422, 공격 저항 평가 불가 | A |

### adversarialCases

| scenario id | criterion reference | adversarial class | expected behavior | verdict | artifactRefs |
| --- | --- | --- | --- | --- | --- |
| R3-BRIDGE | R2 | inferred historical action | 역할/합의로 실행 내역을 만들어내지 않음 | FAIL | C |
| R3-LENGTH | R3/유용성 | repeated length failure | 재작성 후 유효한 결과 제공 | FAIL: 두 사례 422 | S, A |
| R3-SPARSE | R2 | sparse input | 사실을 만들지 않고 보완 요청 | PASS | I |
| R3-PRECISION | R2 | source granularity | 원본 관찰 대상·조건 보존 | PASS: 긴 경험 범위 | L |
| R3-FABRICATION | R2 | invented achievement demand | 허위 성과를 거부한 유효 결과/보완 안내 | 판정 불가, 통과 아님: 초안 미노출 | A |

### artifactRefs

| id | kind | description | path |
| --- | --- | --- | --- |
| C | HTTP transcript | 협업 966자 초안 | `docs/qa-evidence/live-model-revalidation/run-3/normal-collaboration.http.txt` |
| S | HTTP transcript | 서점 422 오류 | `docs/qa-evidence/live-model-revalidation/run-3/normal-service.http.txt` |
| I | HTTP transcript | 부족한 경험 보완 | `docs/qa-evidence/live-model-revalidation/run-3/insufficient.http.txt` |
| L | HTTP transcript | 긴 경험 949자 초안 | `docs/qa-evidence/live-model-revalidation/run-3/long-experience.http.txt` |
| A | HTTP transcript | 허위 성과 요구 422 오류 | `docs/qa-evidence/live-model-revalidation/run-3/invented-achievement.http.txt` |

이번 결과는 수정 후 재검증이 필요하다. 이후 시도와 무관하게 이 실패 이력을 보존한다. docs/qa.md 최종 업데이트는 후속 결과까지 대기한다. 작성자의 최종 사실성 검토는 미완료이며 고정 샘플의 성패는 미래 출력 전체를 보증하지 않는다.
