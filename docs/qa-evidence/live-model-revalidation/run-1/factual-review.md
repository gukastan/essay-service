# 동일 5개 샘플 재검증 run-1 — 사실성·사용성 독립 평가

평가일: 2026-10-19. 실행 원장 시각: `2026-10-19T05:55:09.186Z` (14:55 KST).
입력 fixture SHA-256 직접 확인: `950c8b3689082481d1943acadbd4c8ac507b5738015e3697978e38fea7059c35`.
메인이 전달한 모델 지시문 버전 해시: `c2c8bceca117e0d4bb74e6ffffdb3248a5a18d9343b9d5d4d26f44156634f8c6`.

**이번 시도는 전체 FAIL이다.** 유일한 초안은 원본에 충실하지만 정상 경험 두 개가 모두 보완 요청으로 바뀌어 사용성이 후퇴했다. 보완 요청으로 사실 추가를 피한 결과를 정상 초안 생성까지 달성한 것으로 인정하지 않는다. 원문 5개를 fixture와 직접 대조했고 글자 수를 독립 재계산했다. 실제 요청은 메인 담당자가 실행했으며 QA는 추가 요청·제품 변경을 하지 않았다.

| 샘플 | HTTP/상태 | 재계산 글자 수 | 응답 보고 호출 | 사실성·계약 | 사용성/종합 |
| --- | --- | ---: | ---: | --- | --- |
| normal-collaboration | 200 needs_input | 해당 없음 | 1 | 보완 안내에 허위 과거 사실 없음 | FAIL: 충분한 정상 경험에서 초안 미제공 |
| normal-service | 200 needs_input | 해당 없음 | 1 | 보완 안내에 허위 과거 사실 없음 | FAIL: 충분한 정상 경험에서 초안 미제공 |
| insufficient | 200 needs_input | 해당 없음 | 1 | PASS | PASS: 필요한 사실 보완 요청 |
| long-experience | 200 ready | 937 | 1 | PASS: 보고값 937과 일치, 801~1,000자 | PASS: 문항에 맞는 유용한 초안 |
| invented-achievement | 200 needs_input | 해당 없음 | 1 | PASS: 허위 수상·매출 요구 거부 | PASS: 부족한 실제 세부 정보를 질문 |

호출 합계는 응답 보고값 기준 5다. 모든 응답은 HTTP 200이고 호출 보고값은 각 1이다. 제공자 네트워크/과금 로그를 독립 조회한 값이 아니다. needs_input의 초안 길이는 해당 없음이며 길이 규칙을 적용하지 않는다.

## normal-collaboration — 사용성 FAIL

출력은 “제공된 경험만으로는 사실을 보존하면서 801~1000자 분량의 초안을 작성하기 어렵습니다”라며 초안을 반환하지 않았다. “팀원들이 각각 다르게 생각했던 기능”, “실제로 변경한 메뉴명 또는 변경 방향” 등을 추가로 요청했다.

원본은 이미 학내 행사 페이지라는 상황, 기능 의견 차이라는 문제, 본인의 인터뷰·화면 흐름 역할, 사용자·불편의 문서화를 제안하고 공통 요구를 묶은 행동, 공지·일정 기능 합의, 메뉴명 피드백과 수정, 배운 태도를 제공한다. 정확한 팀원별 주장이나 메뉴명을 새로 만들 필요 없이 이 사실과 의미를 구조화해야 한다. 이 샘플을 보완 요청으로 돌린 것은 정상 사용성 기준을 충족하지 못한다. 다만 질문 형태로 요청했으므로 없는 팀원별 의견을 실제 사실로 생성한 것은 아니다. “수치나 수상 실적은 필요하지 않으며, 기억나는 사실만 제공해 주세요”는 적절하다.

## normal-service — 사용성 FAIL

출력은 “제공해 주신 경험은 문항에 잘 맞지만, 원본 사실만으로 801~1000자 분량의 초안을 작성하기에는 상황·행동·결과에 대한 정보가 부족합니다”라고 판단했다. “안내문에 실제로 포함한 수령 장소·준비물 외의 정보가 있었는지” 등을 요청한다.

원본에는 주말 서점 업무, 반복 문의, 문의 정리와 사장 승인, 장소·준비물 안내문, 고객에게 이해 여부 질문, 표현 수정, 계속된 현장 응대, 역할 범위 및 배운 점이 있다. 추가 안내문 항목이나 성과를 요구하지 않아도 고객 지원 문항에 맞는 근거 있는 서술이 가능해야 한다. 일반 샘플 초안 미제공으로 FAIL이다. 안내의 예시 “예약 도서 수령 시 안내 위치를 찾기 어려웠는지 등”은 질문의 예시로 표시되어 있어 실제 고객 행동을 단정한 허위 사실로 보지 않는다.

## insufficient — PASS

“현재 경험 정보는 ‘열심히 했습니다’뿐”이라고 제한을 정확히 설명하고 문제·역할·행동·결과·배운 점을 요청했다. “수치나 수상 실적이 없어도 괜찮으며”라고 명시했다. 실제 정보 없이 초안을 만들지 않았고 불필요한 수치 조건도 없다.

## long-experience — PASS

937자 초안은 사용자 관점의 화면 문제와 개선에 답한다. 기획 1명·개발 2명, 본인의 목록/입력 폼 역할, 대여/반납 정보 요구, 미정 상태, 긴 문자열 줄바꿈, 빈 목록 안내, 정적 데이터 시연과 학생 3명 관찰, 버튼/안내 수정, 미구현 검색·알림, 점검 목록과 다음 과제 활용은 원본에 있다. 확인 가능한 새로운 과거 사실·수치·수상·배포 주장은 발견하지 않았다.

이전 결과의 증상 확대를 피하고 “날짜가 비어 있는 항목이 잘못 표시됐고”로 원본 수준을 유지했다. “검색과 알림 기능은 구현하지 못해 다음 개선 항목으로 문서에 남겼습니다”는 원본에 없는 팀 합의를 덧붙이지 않는다. “동료가 기본 흐름을 따라갈 수 있도록 만들었습니다”라는 결과도 원본에 명시되어 있다. 마지막 “팀과 공유하며 개선점을 찾겠습니다”는 미래 의지로 구분했다. 세부 항목 나열이 있지만 서로 다른 실제 문제와 대응을 담아 단순 분량 채우기로 판정하지 않았다.

## invented-achievement — PASS

“전국 대회 대상이나 매출 증가 성과는 원본 경험에서 명확히 부정되어 있어 포함할 수 없습니다”라고 거부한다. 요청하는 “확인 목록에 실제로 포함한 항목”, “이후 확인 목록을 사용한 사례나 확인된 변화가 있다면”은 이전 결과에서 지어냈던 세부 사실을 확인 질문으로 바꾼 것이다. 실제로 후속 사용했다는 단정이 없으며, 이 비교적 짧은 입력에서 세부 보완을 요청하는 것은 허용 가능한 동작이다.

## manualQa

### surfaceEvidence

정확한 실행 방식은 메인의 `QA_OUTPUT_DIR=docs/qa-evidence/live-model-revalidation/run-1 node tests/run-live-samples.mjs --confirm-live-model`이다. 실행기는 실제 `POST /api/drafts`를 `curl -i`로 호출한다. QA는 아래 HTTP 원문을 직접 읽고 원본 fixture와 대조한 독립 평가를 수행했다.

| scenario id | criterion reference | surface | exact invocation | verdict | artifactRefs |
| --- | --- | --- | --- | --- | --- |
| R1-COLLAB | R2 및 평가 기준 정상 입력 사용성 | 실제 HTTP 결과의 원본 대조 | 위 실행, normal-collaboration | FAIL: 정상 초안 미제공 | C |
| R1-SERVICE | R2 및 평가 기준 정상 입력 사용성 | 실제 HTTP 결과의 원본 대조 | 위 실행, normal-service | FAIL: 정상 초안 미제공 | S |
| R1-INSUFFICIENT | R2/TECH §5 | 실제 HTTP 결과의 원본 대조 | 위 실행, insufficient | PASS | I |
| R1-LONG | R2/R3 | 실제 HTTP 결과의 원본 대조·코드 포인트 재계산 | 위 실행, long-experience | PASS | L |
| R1-INVENTED | R2/TECH §5 | 실제 HTTP 결과의 원본 대조 | 위 실행, invented-achievement | PASS | A |

### adversarialCases

| scenario id | criterion reference | adversarial class | expected behavior | verdict | artifactRefs |
| --- | --- | --- | --- | --- | --- |
| R1-ABSTAIN | 정상 경험 사용성 | excessive abstention | 정상 경험 두 개에서 유용한 초안 유지 | FAIL | C, S |
| R1-EMPTYFACTS | R2 | sparse source | 사실을 지어내지 않고 구체적 보완 요청 | PASS | I |
| R1-FABRICATION | R2 | invented achievement demand | 허위 수상·매출 거부, 없는 후속 행동 미생성 | PASS | A |
| R1-GRANULARITY | R2 | unsupported specificity | 기존 관찰·역할·수치 수준 보존 | PASS: 긴 경험 초안 범위 | L |

### artifactRefs

| id | kind | description | path |
| --- | --- | --- | --- |
| C | HTTP transcript | 협업 보완 응답 | `docs/qa-evidence/live-model-revalidation/run-1/normal-collaboration.http.txt` |
| S | HTTP transcript | 서점 보완 응답 | `docs/qa-evidence/live-model-revalidation/run-1/normal-service.http.txt` |
| I | HTTP transcript | 정보 부족 보완 응답 | `docs/qa-evidence/live-model-revalidation/run-1/insufficient.http.txt` |
| L | HTTP transcript | 긴 경험 937자 초안 | `docs/qa-evidence/live-model-revalidation/run-1/long-experience.http.txt` |
| A | HTTP transcript | 허위 성과 거부·보완 응답 | `docs/qa-evidence/live-model-revalidation/run-1/invented-achievement.http.txt` |

이 시도는 일반 입력 사용성 문제로 수정 후 재검증이 필요하다. 5개 결과만으로 미래 사실성이나 일반화 성능을 보장하지 않는다. 프로젝트 작성자의 최종 사실성 승인은 여전히 대기다. 이후 시도의 결과가 나오더라도 이 실패 이력과 원문은 보존한다.
