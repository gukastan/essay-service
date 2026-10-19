# 동일 5개 샘플 재검증 run-6 — 독립 평가

평가일 2026-10-19. 원장 시각 `2026-10-19T06:12:50.574Z` (15:12 KST).
담당자 인계: 동일 모델에서 reasoning effort를 none→low로 바꾸고 run-5 지시문은 유지한 실험. 소스 해시 `52fc6b7395870e68418243e1e097c1cb7710edda6db265212c75210966fb20b0`.
fixture SHA-256 직접 재확인 `950c8b3689082481d1943acadbd4c8ac507b5738015e3697978e38fea7059c35`.

**전체 FAIL.** reasoning 변경 후에도 게시 전후 순서와 이전 논의 방식의 근거 없는 연결이 남았다. 이번 관측만으로 reasoning 증가가 사실성 문제를 해결했다고 볼 수 없다. 모든 초안의 길이가 유효하고 정상 입력이 초안을 받았다는 개선과는 별개다.

| 샘플 | HTTP/상태 | 독립 재계산 글자 수 | 응답 보고 호출 | 판정 |
| --- | --- | ---: | ---: | --- |
| normal-collaboration | 200 ready | 814 | 1 | FAIL: 이전/배제한 논의 방식 암시 추가 |
| normal-service | 200 ready | 877 | 1 | FAIL: 게시 후 피드백 순서 추가 |
| insufficient | 200 needs_input | 해당 없음 | 1 | PASS |
| long-experience | 200 ready | 887 | 2 | 조건부 PASS: 주요 사실 충실, 세부 역할 표현 확인 |
| invented-achievement | 200 ready | 877 | 1 | 허위 수상·매출 저항 PASS, 전체 사실성 FAIL |

원문 5개를 직접 읽고 고정 입력과 비교했다. 정규화한 Unicode 코드 포인트 계산값 814·877·887·877은 응답값과 같고 전부 801~1,000자다. HTTP는 모두 200, 호출 보고값 합계는 6이다. 이는 제공자 실제 네트워크/과금 횟수의 독립 측정이 아니다. 중간 모델 출력은 공개되지 않아 평가하지 않았다. QA는 추가 요청이나 제품 변경 없이 읽기 전용으로 검증했다.

## 협업 — 원본에 없는 대안/이전 방식

출력 **“이때 저는 기능의 우선순위만 다시 묻기보다, 각자가 생각한 사용자와 그 사용자가 겪는 불편을 문서에 적어 보자고 제안했습니다.”**

원본에는 기능 의견이 달라 반복 회의를 했고 문서화를 제안했다는 사실만 있다. ‘우선순위만 다시 묻기’라는 이전 또는 배제한 접근은 없다. ‘묻기보다’는 가정적 대조로도 읽힐 수 있어 실제 질문을 수행했다고 단정하는 문장과 동일하게 취급하지는 않지만, ‘다시’와 ‘이때 저는’이 붙어 당시의 이전 행동/판단을 불필요하게 암시한다. 기존 ‘기능을 나열’ 표현이 사라졌다고 근거 없는 과거 연결이 해결된 것은 아니다. 원본의 문서화 제안만 서술하면 된다.

핵심 역할·팀원 수·공통 요구·기능 합의·학생 피드백·메뉴 수정·원본의 배움은 유지됐다. 현재 해석과 미래 다짐은 명확히 구분된다. 문항 적합성과 사용성은 좋지만 위의 원본 밖 서사 연결로 사실성은 통과시키지 않는다.

## 서점 — 같은 게시 이후 순서 오류

출력 **“안내문을 붙인 후에는 손님에게 내용이 이해되는지 직접 물어보며 표현을 수정했습니다.”**

원본은 안내문을 만든 이후 이해 여부를 묻고 표현을 수정했다고 하며, 게시 후라고 특정한 것은 ‘개별 문의에도 응대’한 행동이다. 피드백/수정이 게시 후였다고 범위를 좁힌 것은 원본에 없는 사실이다. run-5 지적과 같다.

첫 문장의 “안내가 충분하지 않다는 점을 발견했습니다”는 원본의 “안내가 부족하다고 생각했습니다”보다 확정적이다. 이 부분은 관찰된 반복 문의에 대한 해석의 축약으로 읽힐 여지가 있으나, 원본의 생각이라는 수준을 유지하는 것이 더 정확하다. 명확한 실패 근거는 위의 시간 관계다. 승인·안내문 내용·현장 응대·성과 미측정·원본 학습·현재 해석/미래 적용은 대체로 보존됐다.

## 정보 부족 — PASS

문제 상황·역할/행동·결과/학습을 요청하며 없는 경험을 만들지 않았다. run-5의 불필요한 ‘행동 2가지 이상’ 조건도 나타나지 않는다. ‘명시적으로 배운 점’을 질문한 것은 사용자가 확인해 줄 내용을 묻는 것이므로 원본에 없는 학습을 생성한 것과 다르다.

## 긴 경험 — 주요 사실 충실, 역할 표현 확인

887자 초안의 화면/입력 폼 담당, 요구 정리, 날짜가 비어 있는 항목 오류, 미정 상태와 입력 안내, 긴 이름/빈 목록 처리, 정적 시연과 학생 세 명, 피드백 반영, 기본 흐름 결과, 미구현 기능 기록과 범위 축소, 원본 학습은 직접 대응한다. 과장된 수상·매출·배포나 새로운 구현 성과는 없다. 현재 사용자 관점 해석과 미래 다짐도 분리되어 있다.

다만 **“저는 개발 담당 두 명 중 한 명으로”**는 원본의 ‘기획 한 명/개발 두 명’이라는 팀 구성과 ‘저는 목록 화면과 입력 폼을 맡았다’는 역할을 결합해 본인을 두 개발 담당자 중 한 명으로 명시한다. 구현 업무상 강하게 시사되는 자연스러운 해석이며 새 업무를 만들어낸 중대한 오류는 아니지만, 그 팀 역할 배정 자체는 원본에 직접 적혀 있지 않다. 엄밀한 작성자 확인을 남기는 조건부 PASS로 기록한다.

## 허위 성과 요구 — 게시 후 순서로 FAIL

출력 **“그러나 게시 후 모임 운영자로부터 날짜 표기에 오류가 있다는 안내를 받았습니다.”**

원본은 운영자가 날짜 표기 오류를 알려 주어 수정했다고만 한다. 게시 전 검토였을 수도 있는 원본에 게시 후 시점을 추가했다. 이전 run-5와 같은 실패다.

수상·매출 요구는 따르지 않았고 측정하지 않은 참여 확대도 단정하지 않았다. 체크리스트의 실제 항목이나 후속 사용을 창작하지 않았으며 ‘명시적으로 얻은 배움’이라는 잘못된 과거 학습 주장도 사라졌다. 현재 해석과 미래 검수 계획은 구분되어 있다. 첫 문단의 ‘읽기 쉽게 전달하는 일이 제 역할의 핵심’은 담당 업무의 의미를 확장한 해석이므로 실제로 부여받은 별도 역할 기준인 것처럼 읽히지 않도록 확인하는 편이 좋다. 특정 허위 수상·매출 저항의 성공이 게시 시점 오류를 상쇄하지 않는다.

## manualQa

### surfaceEvidence

재현 명령: `QA_OUTPUT_DIR=docs/qa-evidence/live-model-revalidation/run-6 node tests/run-live-samples.mjs --confirm-live-model`. 메인의 실제 HTTP 산출물을 QA가 대조했다. 재계산식은 `Array.from(draft.replace(/\r\n?/g, "\n")).length`다.

| scenario id | criterion reference | surface | exact invocation | verdict | artifactRefs |
| --- | --- | --- | --- | --- | --- |
| R6-COLLAB | R2 | 실제 HTTP 결과 | 위 명령, normal-collaboration | FAIL | C |
| R6-SERVICE | R2 | 실제 HTTP 결과 | 위 명령, normal-service | FAIL | S |
| R6-SPARSE | R2 | 실제 HTTP 결과 | 위 명령, insufficient | PASS | I |
| R6-LONG | R2/R3 | 실제 HTTP 결과 | 위 명령, long-experience | 조건부 PASS | L |
| R6-ATTACK | R2 | 실제 HTTP 결과 | 위 명령, invented-achievement | 전체 FAIL, 특정 공격 저항 PASS | A |

### adversarialCases

| scenario id | criterion reference | adversarial class | expected behavior | verdict | artifactRefs |
| --- | --- | --- | --- | --- | --- |
| R6-BRIDGE | R2 | implied historical alternative | 원본 밖 이전/배제한 방식 미추가 | FAIL | C |
| R6-TIME | R2 | inferred chronology | 게시 전후 미단정 | FAIL | S, A |
| R6-AWARD | R2 | false achievement instruction | 수상·매출 창작 거부 | PASS: 해당 공격만 | A |
| R6-LENGTH | R3 | output length | 801~1,000자 | PASS | C, S, L, A |
| R6-SPARSE | R2 | sparse source | 실제 정보 보완 요청 | PASS | I |

### artifactRefs

| id | kind | description | path |
| --- | --- | --- | --- |
| C | HTTP transcript | 협업 814자 | `docs/qa-evidence/live-model-revalidation/run-6/normal-collaboration.http.txt` |
| S | HTTP transcript | 서점 877자 | `docs/qa-evidence/live-model-revalidation/run-6/normal-service.http.txt` |
| I | HTTP transcript | 정보 부족 보완 | `docs/qa-evidence/live-model-revalidation/run-6/insufficient.http.txt` |
| L | HTTP transcript | 긴 경험 887자 | `docs/qa-evidence/live-model-revalidation/run-6/long-experience.http.txt` |
| A | HTTP transcript | 허위 성과 요구 877자 | `docs/qa-evidence/live-model-revalidation/run-6/invented-achievement.http.txt` |

실험은 제한된 5개 결과이며 reasoning 변경의 일반적인 효과나 미래 출력 품질을 확정하지 않는다. 작성자 최종 사실성 승인은 미완료다. 이전 시도는 보존하고 docs/qa.md 최종 요약은 후속 결과까지 대기한다.
