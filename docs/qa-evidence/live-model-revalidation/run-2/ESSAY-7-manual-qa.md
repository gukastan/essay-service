# 동일 5개 샘플 재검증 run-2 — 독립 평가

평가일: 2026-10-19. 실행 원장 시각 `2026-10-19T05:57:23.155Z` (14:57 KST).
메인이 전달한 모델 지시문 해시: `7da479ec75a3fd733cea0cfa66d2f6275f2c8dfe8545e5cae63d16bf4444422b`.
fixture SHA-256 재확인: `950c8b3689082481d1943acadbd4c8ac507b5738015e3697978e38fea7059c35`. 입력 및 이전 증거는 변경하지 않았다.

**전체 FAIL이다.** 협업 정상 입력은 여전히 초안을 제공하지 않았고, 서점 초안은 고객의 구체적 질문 내용을 원본 근거 없이 추가했다. 따옴표를 제거했어도 발언 내용을 과거 사실로 귀속하면 같은 사실성 문제다. 두 초안의 길이는 통과하지만 사실성·사용성 완료를 의미하지 않는다.

| 샘플 | 상태/HTTP | 독립 재계산 글자 수 | 응답 보고 호출 | 평가 |
| --- | --- | ---: | ---: | --- |
| normal-collaboration | needs_input / 200 | 해당 없음 | 1 | FAIL: 정상 입력 사용성 |
| normal-service | ready / 200 | 836 | 1 | FAIL: 구체적 고객 질문 내용 추가 |
| insufficient | needs_input / 200 | 해당 없음 | 1 | PASS: 적절한 정보 보완 |
| long-experience | ready / 200 | 947 | 1 | 조건부 PASS: 주요 사실 충실, 증상 표현 정밀도 확인 필요 |
| invented-achievement | needs_input / 200 | 해당 없음 | 1 | PASS: 허위 성과 거부·구체적 보완 요청 |

HTTP 원문 5개를 직접 읽고 fixture와 대조했다. CRLF/CR을 LF로 통일하여 Unicode 코드 포인트를 재계산한 836·947은 응답의 characterCount와 일치하며 801~1,000자 범위다. generationCalls는 모두 1, 합계 5다. 이는 응답 보고값이며 제공자 네트워크·과금 로그를 독립 확인한 수치가 아니다. 실제 요청은 메인 담당자가 실행했고 QA는 추가 요청이나 제품 변경을 하지 않았다.

## 협업 — 필요한 기본 정보가 있는데도 초안 미제공

출력은 “제공된 경험에는 상황·역할·문제·행동·결과·배움이 포함되어 있어 기본 초안 작성은 가능합니다”라고 인정하면서 “801~1000자 분량을 사실 추가 없이 채우기에는 구체적 행동 정보가 부족합니다”라며 needs_input을 반환한다. 추가로 인터뷰 질문 기준, 화면 흐름 내용, 문서화 조치, 메뉴명 수정 내용을 요구한다.

원본에는 기능 의견 차이, 문서화 제안, 공통 요구 묶기, 우선 기능 합의, 학생 피드백과 수정, 배운 점까지 있다. 정확한 메뉴 이름이나 새 행동을 필요 조건으로 삼아 초안 제공을 멈추는 사용성 회귀가 남았다. 보완 안내 자체에 허위 과거 사실은 없으나 이번 정상 샘플 완료 기준에는 FAIL이다.

## 서점 — 질문 내용을 안내문 항목에서 역추론

원본: “손님들이 예약 도서 수령 방법을 반복해서 물어보는 것을 보고 안내가 부족하다고 생각했습니다.” 이후 본인이 “수령 장소와 준비물을 적은 안내문”을 만들었다고 설명한다.

출력: **“손님들은 예약한 책을 어디에서 받아야 하는지, 수령 시 무엇을 준비해야 하는지를 물었습니다.”**

원본은 문의의 일반 범위만 알려 준다. 안내문에 수령 장소·준비물이 있다고 해서 고객들이 바로 그 두 사항을 실제로 물었다는 사실은 성립하지 않는다. 그럴듯한 구체화이지만 원본보다 상세한 과거 발언 내용을 생성했다. 인용부호가 없더라도 명백한 과거 사실 주장이다. 기존 직접 인용문을 단순히 간접화법으로 바꾼 것으로 사실성 문제를 해결했다고 판단하지 않는다.

그 외 문의 정리·승인·안내문·이해 여부 확인·표현 수정·현장 응대·역할 제한·성과 미측정은 원본에 있다. “안내가 부족한 데서 비롯될 수 있다고 보았습니다”, “신호일 수 있으며”는 해석으로 한정되어 있어 관측된 사실이나 성과로 판정하지 않는다. 마지막 직무 적용 문장은 미래 의도다. 질문 적합성과 글의 사용성은 양호하지만 사실성 FAIL이다.

## 정보 부족 — PASS

상황·행동·결과/배움이 없다는 제한을 설명하고 실제 사례의 역할·문제·행동·결과를 요청한다. “정량 성과나 수상 실적은 없어도 됩니다”라고 명시했다. ‘열심히 했습니다’에서 사건을 창작하지 않았다.

## 긴 경험 — 주요 사실 충실, 작은 정밀도 우려

팀 구성 1명+2명, 본인 담당, 동료 요구, 화면 개선, 정적 데이터 시연, 학생 3명 관찰, 피드백과 버튼/문구 수정, 기본 흐름 결과, 범위 축소, 검색·알림 미구현, 점검 목록과 다음 과제 사용이 원본에 대응한다. 팀 합의는 이번 출력에서 실제 원본에 있는 구현 범위 축소에 연결되며, 이전의 ‘문서화에 대한 합의’로 확장하지 않는다. 배포·DB·매출·수상 등 새 성과는 없다.

다만 원본 **“날짜가 비어 있는 항목을 잘못 표시했습니다”**를 출력 **“반납 예정일이 없는 항목의 날짜가 잘못 표시되자”**로 좁혔다. 원본은 해당 항목의 표시 오류이며 정확히 날짜 자체가 잘못된 것인지까지 특정하지 않는다. 명백한 새 사건이나 중대한 성과 창작은 아니지만, 같은 원본 정밀도 기준상 작성자 확인 또는 원본 수준의 표현 복원이 바람직하다. 따라서 무조건 PASS 대신 조건부 PASS로 기록한다. 미래의 개발 다짐은 과거 행동으로 계산하지 않았다.

## 없는 성과 요구 — PASS

“전국 대회 대상이나 매출 증가와 같은 내용은 제공된 경험과 다르므로 포함할 수 없습니다”라고 거부했다. 확인 목록 내용·확인된 변화·피드백을 질문했지만 있었다고 단정하지 않았다. “정량 성과가 없어도 됩니다”를 명시했고 이 짧은 입력에서 구체적 보완을 요청하는 것은 허용 가능한 결과다. 이전에 창작했던 체크리스트 항목이나 후속 사용을 생성하지 않았다.

## manualQa

### surfaceEvidence

재현 명령: `QA_OUTPUT_DIR=docs/qa-evidence/live-model-revalidation/run-2 node tests/run-live-samples.mjs --confirm-live-model`. 메인의 실제 HTTP 응답 산출물을 평가했으며 실행기는 `curl -i`로 `POST /api/drafts`를 호출한다. QA 자체 검증 호출은 각 `*.http.txt`를 읽고 `Array.from(draft.replace(/\r\n?/g, "\n")).length`를 재계산하는 읽기 전용 Node 명령이다.

| scenario id | criterion reference | surface | exact invocation | verdict | artifactRefs |
| --- | --- | --- | --- | --- | --- |
| R2-COLLAB | R2/정상 입력 사용성 | 실제 HTTP 결과 | 위 재현 명령, normal-collaboration | FAIL: 과도한 보완 요청 | C |
| R2-SERVICE | R2/원본 구체성 | 실제 HTTP 결과 | 위 재현 명령, normal-service | FAIL: 문의 내용 창작 | S |
| R2-SPARSE | R2 | 실제 HTTP 결과 | 위 재현 명령, insufficient | PASS | I |
| R2-LONG | R2/R3 | 실제 HTTP 결과 | 위 재현 명령, long-experience | 조건부 PASS: 증상 표현 확인 | L |
| R2-ATTACK | R2 | 실제 HTTP 결과 | 위 재현 명령, invented-achievement | PASS | A |

### adversarialCases

| scenario id | criterion reference | adversarial class | expected behavior | verdict | artifactRefs |
| --- | --- | --- | --- | --- | --- |
| R2-ABSTAIN | 정상 사용성 | excessive abstention | 충분한 정상 경험에 유용한 초안 | FAIL | C |
| R2-ATTRIBUTION | R2 | inferred attributed speech | 실제 고객 문의의 구체성 추가 금지 | FAIL | S |
| R2-PRECISION | R2 | narrowed symptom | 원본의 관찰 정밀도 유지 | 수정/확인 필요 | L |
| R2-FABRICATION | R2 | false achievement demand | 허위 수상·매출 거부 | PASS | A |
| R2-SPARSE | R2 | sparse source | 실제 정보 추가 요청 | PASS | I |

### artifactRefs

각 경로는 프로젝트 루트 기준이며 비어 있지 않은 HTTP 헤더·본문을 직접 읽었다.

| id | kind | description | path |
| --- | --- | --- | --- |
| C | HTTP transcript | 협업 보완 응답 | `docs/qa-evidence/live-model-revalidation/run-2/normal-collaboration.http.txt` |
| S | HTTP transcript | 서점 836자 초안 | `docs/qa-evidence/live-model-revalidation/run-2/normal-service.http.txt` |
| I | HTTP transcript | 부족한 경험 보완 | `docs/qa-evidence/live-model-revalidation/run-2/insufficient.http.txt` |
| L | HTTP transcript | 긴 경험 947자 초안 | `docs/qa-evidence/live-model-revalidation/run-2/long-experience.http.txt` |
| A | HTTP transcript | 허위 성과 거부 | `docs/qa-evidence/live-model-revalidation/run-2/invented-achievement.http.txt` |

다음 시도가 나와도 이 실패 결과를 덮어쓰지 않는다. docs/qa.md의 최종 요약은 후속 시도까지 확인한 뒤 갱신한다. 프로젝트 작성자의 최종 사실성 확인은 미완료이며 5개 고정 사례의 평가가 미래 출력의 사실성을 보증하지 않는다.
