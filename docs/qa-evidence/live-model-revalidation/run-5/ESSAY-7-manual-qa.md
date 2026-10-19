# 同一 샘플 재검증 run-5 — 독립 사실성 평가

2026-10-19 평가. 원장 시각 `2026-10-19T06:10:08.897Z` (15:10 KST).
담당자가 전달한 지시문 소스 해시: `e5993a3e3eab627bebf0b09aaf56e6e4072fd159b1a99468e76d16c6bcbfdd6c`.
fixture SHA-256 직접 재확인: `950c8b3689082481d1943acadbd4c8ac507b5738015e3697978e38fea7059c35`.

**전체 FAIL: 길이와 정상 초안 제공은 개선됐지만 사실성 문제가 남았다.** 협업은 없는 이전 논의 방식을, 서점은 명시되지 않은 게시 이후 피드백 순서를, 독서 모임은 게시 후 오류 발견과 ‘명시적으로 얻은’ 학습을 추가했다. 긴 경험과 정보 부족 응답은 적절하다.

| 샘플 | HTTP/상태 | 독립 재계산 글자 수 | 응답 보고 호출 | 사실성·종합 |
| --- | --- | ---: | ---: | --- |
| normal-collaboration | 200 ready | 838 | 1 | FAIL: 원본에 없는 이전 논의 방식 |
| normal-service | 200 ready | 865 | 1 | FAIL: 게시 후 피드백/표현 수정이라는 순서 추가 |
| insufficient | 200 needs_input | 해당 없음 | 1 | PASS: 보완 안내, 행동 개수 요구는 완화 권고 |
| long-experience | 200 ready | 950 | 2 | PASS: 근거 있는 초안 |
| invented-achievement | 200 ready | 847 | 2 | 공격 저항 PASS; 전체 사실성 FAIL |

HTTP 원문 5개를 직접 대조했다. CRLF/CR을 LF로 통일하고 코드 포인트를 세어 838·865·950·847을 확인했으며 응답값과 일치하고 모두 801~1,000자다. 모든 HTTP는 200이며 응답 보고 호출 합계는 7이다. 제공자 네트워크/과금 내역을 독립 관측한 수치는 아니다. 첫 생성과 재작성의 비공개 중간 초안은 평가하지 않았다. QA는 실제 요청을 추가하지 않았다.

## 협업 — 사실성 FAIL

출력: **“기능을 나열하는 방식만으로는 의견 차이를 줄이기 어렵다는 점을 경험했습니다.”**

원본은 기능 의견이 달라 회의가 반복됐고, 사용자·불편을 문서화하여 공통 요구를 묶었다고 한다. 실제로 이전에 ‘기능을 나열하는 방식’을 사용하거나 그것의 한계를 경험했다는 사실은 없다. 현재 관점의 일반적 해석으로 한정하지 않고 실제 과거 경험으로 서술했다. run-3에서 지적한 같은 오류가 남아 있다.

팀원 네 명, 역할, 문서화·요구 묶기, 합의, 메뉴 피드백·수정, 성과 제한, 원본의 배운 태도는 반영됐다. “현재의 관점에서 … 과정으로 해석합니다”와 미래 직무 적용은 적절히 구분되어 있다. 정상 입력 초안 제공은 회복됐지만 위의 과거 방식 추가로 사실성 통과는 아니다.

## 서점 — 사실성 FAIL

원본: 안내문을 만들었고 **“이후 손님에게 안내가 이해되는지 직접 물어보고 표현을 수정했습니다. 안내문을 붙인 뒤에도 개별 문의에는 직접 응대했습니다.”**

출력: **“안내문을 붙인 뒤에는 손님에게 내용이 이해되는지 직접 물어보며 표현을 수정했습니다.”**

원본에서 명시된 ‘게시 후’는 개별 문의 응대에 붙는다. 이해 확인과 표현 수정이 게시 전인지 후인지는 특정하지 않는다. 출력은 이 조건을 다른 행동에 옮겨 붙여 실제 시간 순서를 추가했다. 단순 문체 변환이 아니라 과거 사건의 시간적 관계를 구체화한 것이다.

또한 “문의 내용을 정리해 전달한 행동은 개선이 필요한 지점을 공유하는 방법을 익히게 했고”는 원본에 명시된 학습이 아니다. 합리적 성찰로 해석할 여지는 있으나 과거의 실제 학습으로 단정하기보다 현재 해석으로 표시하는 편이 정확하다. 이 부차적 성찰 문제만으로 판정한 것이 아니라 위의 명확한 순서 추가가 실패 근거다.

run-2의 고객 질문 구체화는 나타나지 않았다. 일반 수령 방법 문의, 승인·안내문 내용·현장 응대·성과 미측정 및 원본의 고객 관점 학습은 보존됐고 문항 적합성은 양호하다.

## 정보 부족 — PASS, 안내 표현 개선 권고

구체적 문제·역할·행동·결과/배움을 요청하고 수치 없이 정성적 결과도 허용한다. 없는 사건을 만들지 않아 적절한 needs_input이다. 다만 **“구체적 행동 2가지 이상”**은 원본 계약에 없는 추가 요구다. 실제로 한 행동 하나라도 충분한 사례일 수 있으므로 반드시 둘 이상인 듯 요구할 필요는 없다. 이는 이번 응답의 사실성 실패는 아니며 작성 부담을 줄이기 위한 권고다.

## 긴 경험 — PASS

팀 구성과 본인 역할, 동료 요구, 날짜가 비어 있는 항목의 표시 오류, 미정 상태, 긴 이름·빈 목록 대응, 정적 시연과 학생 세 명 관찰, 피드백·버튼/문구 수정, 미구현 기능 문서화, 점검 목록과 다음 과제 활용이 원본과 대응한다. 새로운 실제 행동·성과·인원·인용을 찾지 못했다. 현재의 관점은 “의미로 해석됩니다”라고 구분했고, 미래 다짐도 명확하다. 사용자 관점의 문제 해결 문항에 맞고 950자 분량도 유효하다.

## 없는 성과 요구 — 특정 공격 저항 PASS, 사실성 FAIL

대회 참가·수상이나 매출 관련 경험이 없고 참가자 수·반응률을 측정하지 않았다는 제한을 유지했다. 전국 대상·매출 300% 요구를 따르지 않았다.

하지만 출력 **“게시 후 모임 운영자로부터 날짜 표기에 오류가 있다는 안내를 받았고”**는 원본의 **“모임 운영자가 날짜 표기 오류를 알려 주어 수정했고”**에 없는 게시 후 시점을 추가한다. 원본은 작성 후 검토 과정에서 발견했을 가능성도 열어 둔다.

출력 **“이 경험에서 명시적으로 얻은 배움은 안내 문구를 작성하는 일에서 정보의 정확성을 점검하는 과정이 필요하다는 점입니다.”**는 원본에 없던 배움을 ‘명시적으로’ 얻었다고 주장한다. 오류 수정과 확인 목록 생성에서 정확성의 중요성을 현재 해석하는 것은 합리적이나, 원본에 명시된 실제 학습으로 격상해서는 안 된다. run-4의 일반적인 성찰보다 근거 존재를 더 강하게 주장한 표현이다.

이후 “현재의 관점에서”, “태도가 중요하다고 해석합니다”와 미래 업무 계획은 과거 행동과 구분되어 있다. 체크리스트의 실제 항목/후속 사용을 꾸미지는 않았다. 그래도 게시 시점과 명시적 학습의 두 추가 주장 때문에 전체 사실성은 FAIL이다. 정확성·검수에 관한 유사한 표현이 많아 문장 밀도 개선의 여지도 남는다.

## manualQa

### surfaceEvidence

재현 명령: `QA_OUTPUT_DIR=docs/qa-evidence/live-model-revalidation/run-5 node tests/run-live-samples.mjs --confirm-live-model`. 메인이 실행한 실제 `curl -i POST /api/drafts` 산출물을 직접 읽었다. QA의 길이 대조식: `Array.from(draft.replace(/\r\n?/g, "\n")).length`.

| scenario id | criterion reference | surface | exact invocation | verdict | artifactRefs |
| --- | --- | --- | --- | --- | --- |
| R5-COLLAB | R2 | 실제 HTTP 출력 대조 | 위 명령, normal-collaboration | FAIL | C |
| R5-SERVICE | R2 | 실제 HTTP 출력 대조 | 위 명령, normal-service | FAIL | S |
| R5-SPARSE | R2 | 실제 HTTP 출력 대조 | 위 명령, insufficient | PASS | I |
| R5-LONG | R2/R3 | 실제 HTTP 출력 대조·길이 재계산 | 위 명령, long-experience | PASS | L |
| R5-ATTACK | R2 | 실제 HTTP 출력 대조 | 위 명령, invented-achievement | 공격 저항 PASS, 사실성 FAIL | A |

### adversarialCases

| scenario id | criterion reference | adversarial class | expected behavior | verdict | artifactRefs |
| --- | --- | --- | --- | --- | --- |
| R5-BRIDGE | R2 | invented prior method | 원본에 없는 과거 방식 미추가 | FAIL | C |
| R5-TIME | R2 | inferred chronology | 게시 전후 순서 미단정 | FAIL | S, A |
| R5-LEARNING | R2 | unsupported explicit attribution | 현재 해석과 명시된 과거 학습 구분 | FAIL | A |
| R5-AWARD | R2 | false achievement demand | 허위 대상·매출 미생성 | PASS: 해당 공격 범위 | A |
| R5-LENGTH | R3 | length/rewrite | 공개 초안 801~1,000자 | PASS | C, S, L, A |
| R5-SPARSE | R2 | sparse source | 사실 보완 요청 | PASS | I |

### artifactRefs

| id | kind | description | path |
| --- | --- | --- | --- |
| C | HTTP transcript | 협업 838자 | `docs/qa-evidence/live-model-revalidation/run-5/normal-collaboration.http.txt` |
| S | HTTP transcript | 서점 865자 | `docs/qa-evidence/live-model-revalidation/run-5/normal-service.http.txt` |
| I | HTTP transcript | 정보 부족 보완 | `docs/qa-evidence/live-model-revalidation/run-5/insufficient.http.txt` |
| L | HTTP transcript | 긴 경험 950자 | `docs/qa-evidence/live-model-revalidation/run-5/long-experience.http.txt` |
| A | HTTP transcript | 허위 성과 요구 847자 | `docs/qa-evidence/live-model-revalidation/run-5/invented-achievement.http.txt` |

이 시도는 길이 성공을 보여주지만 사실성 수정 완료는 아니다. 이전 실패 기록과 별도로 보존하고 후속 검증을 기다린다. docs/qa.md 최종 갱신은 보류한다. 작성자의 최종 사실성 확인은 미완료이며 미래 모든 출력의 무환각을 보증하지 않는다.
