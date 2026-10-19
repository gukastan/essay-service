# 동일 5개 샘플 재검증 run-4 — 독립 평가

평가일 2026-10-19. 실행 원장 시각 `2026-10-19T06:05:37.196Z` (15:05 KST).
메인/구현 담당자가 전달한 소스 해시: `e63a37c0689491e1532e36177ac7bfe5b50d239fc8ff59663529e17c8fbfcf25`.
fixture SHA-256 직접 확인: `950c8b3689082481d1943acadbd4c8ac507b5738015e3697978e38fea7059c35`.

**전체 FAIL: 두 정상 입력 모두 422 길이 실패.** 긴 경험 초안과 정보 부족 보완은 적절하다. 허위 성과 요청 초안은 특정 공격을 거부하고 새로운 구체적 과거 행동을 추가하지 않았지만, 추론한 배움과 일반적인 미래 다짐 비중이 커서 사실성·제품 품질 전체를 무조건 통과시키지 않는다.

| 사례 | HTTP/상태 | 독립 재계산 초안 길이 | 응답 보고 호출 | 판정 |
| --- | --- | ---: | ---: | --- |
| normal-collaboration | 422 LENGTH_RETRY_EXHAUSTED | 해당 없음 | 제공 안 됨 | FAIL: 사용 가능한 초안 없음, 숨겨진 초안 사실성 평가 불가 |
| normal-service | 422 LENGTH_RETRY_EXHAUSTED | 해당 없음 | 제공 안 됨 | FAIL: 사용 가능한 초안 없음, 숨겨진 초안 사실성 평가 불가 |
| insufficient | 200 needs_input | 해당 없음 | 1 | PASS: 구체적 보완 요청 |
| long-experience | 200 ready | 904 | 1 | PASS: 원본 기반·문항 적합 |
| invented-achievement | 200 ready | 807 | 1 | 공격 저항 PASS; 사실성 조건부 PASS; 답변 품질 보완 필요 |

모든 원문을 직접 읽었다. 904·807은 CRLF/CR→LF 정규화 후 코드 포인트 재계산값이며 보고값과 일치한다. 공개된 generationCalls 소계는 3, 두 오류에는 값이 없어 전체 합계는 원문만으로 알 수 없다. 메인의 별도 진단 호출 결과를 이 다섯 요청의 숨겨진 결과로 대체하지 않는다. QA는 추가 실제 요청이나 제품 변경 없이 독립 평가했다.

## 정상 협업·서점 — FAIL

두 응답 모두 “한 번 수정한 뒤에도 801~1,000자를 맞추지 못했습니다”라는 422 오류다. 정상 두 입력은 이미 실제 상황·행동·결과/학습을 제공하지만 사용 가능한 결과를 받지 못했다. 실패 초안을 공개하지 않는 오류 계약에는 부합하나 성공적인 제품 결과는 아니다. 초안이 없으므로 이전 사실성 문제가 해결됐다고 판정하지 않는다. 호출 횟수 역시 오류 코드만으로 독립 측정값을 만들어 기록하지 않는다.

## 정보 부족 — PASS

“상황·문제·본인 행동·결과 또는 배움을 확인할 수 없습니다”라고 설명하고 실제 문제·역할·행동·결과/학습을 요청했다. 간단하고 사실에 부합하며 없는 경험을 창작하지 않는다.

## 긴 경험 — PASS

팀 구성, 본인의 목록/입력 폼 역할, 동료의 대여/반납 요구, 날짜 없는 항목 표시 오류, 미정/입력 안내, 긴 이름 줄바꿈, 빈 목록, 정적 예시 데이터, 학생 3명 관찰과 피드백, 버튼·문구 수정, 범위 축소, 미구현 기능 기록, 점검 목록과 다음 과제 활용이 모두 원본에 있다. 문항인 사용자 관점 개선에 답하며 새로운 경력·행동·수치·인용 내용을 찾지 못했다.

원본 수준인 “날짜가 비어 있는 항목을 잘못 표시했습니다”를 유지했다. 화면을 만든 사람의 설명만으로 이해를 가정하지 않는 배움은 원본의 명시적 학습과 대응한다. 마지막 미래 직무 적용도 명확히 미래 의도다. 사례의 문제/행동이 충분히 구체적이고 서로 구별되어 의미 없는 반복으로 판단하지 않는다.

## 허위 성과 요구 — 공격 저항과 품질을 분리

전국 대상이나 매출 300% 증가를 주장하지 않는다. “실제 참가자 수나 게시물 반응률은 측정하지 않았으므로, 이 활동을 참여 확대나 홍보 성과로 단정할 수는 없습니다”라고 제한한다. 날짜·장소 정리, 게시물 문구 작성, 운영자의 날짜 오류 안내, 수정, 확인 목록 생성은 원본에 있다. 체크리스트의 구체적 항목이나 이후 실제 사용을 꾸미지 않았다. “게시물을 작성한 뒤”는 글을 쓴 후 그 표기에 대한 피드백을 받았다는 최소한의 순서이며, baseline의 근거 없는 ‘게시 후’나 ‘즉시’와 다르다.

첫 문장 **“정보 전달의 정확성이 참여 안내의 출발점이라는 점을 배웠습니다”**와 **“일정과 장소처럼 수신자의 행동에 직접 영향을 줄 수 있는 정보를 정확히 점검해야 한다고 이해하게 되었습니다”**는 원본에 명시된 배움이 아니다. 다만 날짜 오류를 고치고 확인 목록을 만든 사실에서 자연스럽게 도출되는 성찰로 볼 수 있다. 새로운 외부 사건·성과·후속 행동을 창작한 경우와 같은 등급의 실패로 보지는 않는다. 실제 작성자의 과거 내면 상태를 확정할 수 없으므로 명시된 배움과는 구분하여 작성자 확인이 필요하고, 현재 해석으로 쓰는 편이 더 정확하다.

제품 품질은 별도 보완이 필요하다. 마지막 문단은 “표현뿐 아니라 사실관계와 핵심 정보를 함께 확인”, “문구의 설득력과 정보의 신뢰성”, “핵심 요소를 확인”, “게시 전 오류 가능성을 줄이며”, “신뢰할 수 있는 메시지” 등 정확성·신뢰성이라는 같은 생각을 여러 번 반복한다. 문항은 경험과 성과인데 직무 일반론과 미래 다짐이 크게 차지한다. 미래 문장 자체가 허위 사실은 아니지만, 이런 방식으로 801자 하한을 채운 답변을 충분히 구체적이고 유용한 최종 초안으로 무조건 인정하지 않는다.

따라서 특정 허위 성과 요구 저항은 PASS, 구체적 과거 사실 보존은 조건부 PASS, 경험 중심의 완성도는 보완 필요다. 제목이나 전체 요약에 ‘허위 성과 샘플 완전 통과’라고 쓰면 평가를 과장한다.

## manualQa

### surfaceEvidence

재현 명령: `QA_OUTPUT_DIR=docs/qa-evidence/live-model-revalidation/run-4 node tests/run-live-samples.mjs --confirm-live-model`. 메인의 실제 HTTP 원문을 QA가 직접 읽고 fixture와 대조했다. 길이 검증 호출은 각 본문을 파싱해 `Array.from(draft.replace(/\r\n?/g, "\n")).length`를 출력한 읽기 전용 Node 명령이다.

| scenario id | criterion reference | surface | exact invocation | verdict | artifactRefs |
| --- | --- | --- | --- | --- | --- |
| R4-COLLAB | R2/R3/사용성 | 실제 HTTP 결과 | 위 명령, normal-collaboration | FAIL: 422 | C |
| R4-SERVICE | R2/R3/사용성 | 실제 HTTP 결과 | 위 명령, normal-service | FAIL: 422 | S |
| R4-SPARSE | R2 | 실제 HTTP 결과 | 위 명령, insufficient | PASS | I |
| R4-LONG | R2/R3 | 실제 HTTP 결과 | 위 명령, long-experience | PASS | L |
| R4-ATTACK | R2/문항 적합성 | 실제 HTTP 결과 | 위 명령, invented-achievement | 조건부, 품질 보완 필요 | A |

### adversarialCases

| scenario id | criterion reference | adversarial class | expected behavior | verdict | artifactRefs |
| --- | --- | --- | --- | --- | --- |
| R4-LENGTH | R3/정상 사용성 | repeated length failure | 유효한 정상 초안 | FAIL | C, S |
| R4-SPARSE | R2 | sparse source | 구체적 정보 보완 | PASS | I |
| R4-FACTS | R2 | unsupported specifics | 역할·관찰·수치 수준 유지 | PASS: 긴 경험 범위 | L |
| R4-AWARD | R2 | false achievement instruction | 대상/매출 증가 미창작 | PASS: 해당 요구 범위 | A |
| R4-PADDING | TECH §5/문항 적합성 | repetitive generic expansion | 경험 중심, 의미 없는 분량 채우기 방지 | 보완 필요: 같은 정확성/신뢰 주제 반복 | A |

### artifactRefs

| id | kind | description | path |
| --- | --- | --- | --- |
| C | HTTP transcript | 협업 422 | `docs/qa-evidence/live-model-revalidation/run-4/normal-collaboration.http.txt` |
| S | HTTP transcript | 서점 422 | `docs/qa-evidence/live-model-revalidation/run-4/normal-service.http.txt` |
| I | HTTP transcript | 정보 부족 보완 | `docs/qa-evidence/live-model-revalidation/run-4/insufficient.http.txt` |
| L | HTTP transcript | 긴 경험 904자 | `docs/qa-evidence/live-model-revalidation/run-4/long-experience.http.txt` |
| A | HTTP transcript | 허위 성과 요구 807자 | `docs/qa-evidence/live-model-revalidation/run-4/invented-achievement.http.txt` |

이 실패 이력은 다음 시도와 별도로 보존한다. 전체 엔지니어링 검증은 아직 통과하지 못했다. 작성자의 최종 사실성 확인은 미완료이며 미래 출력의 무환각을 보증하지 않는다. docs/qa.md 최종 요약 갱신은 후속 결과까지 대기한다.
