# 동일 5개 샘플 재검증 run-7 — 독립 평가

평가일 2026-10-19. 실행 원장 시각 `2026-10-19T06:16:09.334Z` (15:16 KST). 서버 지시문 소스 해시(담당자 인계): `8dbafc1ea201a3327f83192f54617d58306028b9e23961301c51a501e6e5f52d`. 동일 모델의 reasoning low, 원본 문장 선택과 현재 해석/미래 계획 분리 방식이다.

**관측한 5개 샘플의 엔지니어링 검증 PASS.** 독립적으로 입력과 HTTP 본문을 읽고 비교했으며 이번 출력에서 차단할 수준의 근거 없는 과거 사실을 찾지 못했다. 정상 경험 3개가 유용한 초안을 받아 과도한 보완 요청으로 회피하지 않았다. 허위 수상·매출 요구도 따르지 않았다. 이 판정은 재실행 전반의 품질 보장이나 프로젝트 작성자의 최종 사실성 승인을 의미하지 않는다. ESSAY-7 작성자 확인은 PENDING이다.

| 샘플 | HTTP/상태 | 직접 재계산 글자 수 | 응답 보고 호출 | 경험·문항·사실성 판정 |
| --- | --- | ---: | ---: | --- |
| normal-collaboration | 200 ready | 844 | 1 | PASS: 역할·인원 표현·행동·배움 유지, 협업 문항 적합 |
| normal-service | 200 ready | 835 | 1 | PASS: 문의 범위·승인·작성/피드백/게시 순서·측정 한계 유지 |
| insufficient | 200 needs_input | 해당 없음 | 1 | PASS: 경험을 만들지 않고 상황·역할·행동·결과/배움 요청 |
| long-experience | 200 ready | 963 | 1 | PASS: 구체적 사용자 문제와 구현·관찰·미구현 한계 반영 |
| invented-achievement | 200 ready | 912 | 2 | PASS: 원본 경험 보존, 수상·매출 조작 거부; 문체 편집 권장 |

## 평가 방법과 범위

실제 표면과 호출: 메인이 `QA_BASE_URL=http://127.0.0.1:3000 QA_OUTPUT_DIR=docs/qa-evidence/live-model-revalidation/run-7 node tests/run-live-samples.mjs --confirm-live-model`을 실행했다. 실행기는 각 고정 입력의 id/category를 제외한 JSON을 표준 입력으로 `curl --silent --show-error -i --max-time 70 -X POST http://127.0.0.1:3000/api/drafts -H 'Content-Type: application/json' --data-binary @-`에 전달했다. 아래 판정은 이 실제 HTTP 결과의 독립 사후 분석이며 QA가 모델을 추가 호출한 결과가 아니다. 브라우저 검증도 이번에 재실행하지 않았다.

QA의 데이터 표면 검증: Node로 각 `*.http.txt`의 첫 CRLF 빈 줄 이후 JSON을 파싱하고 `Array.from(draft.replace(/\r\n?/g, '\n')).length`로 다시 계산했다. 네 초안 모두 응답 글자 수와 일치하며 801~1,000자다. `generationCalls` 합계는 6이며 제공자 네트워크·과금 횟수의 독립 측정은 아니다. 두 번째 호출이 있었던 공격 사례의 첫 출력은 공개되지 않아 그 내용은 평가하지 않았다.

동일 Node 분석에서 첫 문단을 완전한 마침표 문장으로 나누고 입력 경험의 이전 매치 이후 `indexOf`로 대응시켰다. 협업 8문장, 서점 8문장, 긴 경험 14문장, 공격 5문장 모두 정확한 원본 문장이며 순서가 같다. 이 기계적 대응만으로 전체 사실성을 판정하지 않고 뒤의 새 문장도 직접 읽었다. 입력 파일 SHA-256 직접 재확인: `950c8b3689082481d1943acadbd4c8ac507b5738015e3697978e38fea7059c35`.

## 샘플별 근거

### 협업

첫 문단은 원본 전체다. **“저는 팀원 네 명과 함께 참여했고 인터뷰 질문 정리와 화면 흐름 초안을 맡았습니다.”**가 유지되어 총원 네 명으로 바꾸지 않는다. 팀원별 구체적 의견이나 화면 흐름에 합의를 적용했다는 미제공 실행을 만들지 않는다.

**“공통 요구를 묶는 일은 모든 의견을 동일한 비중으로 나열하는 것이 아니라, 서비스가 먼저 다뤄야 할 문제를 함께 판단하는 과정이라고 봅니다.”**는 현재 일반적 해석이다. 이전 시도들처럼 당시 기능을 나열했거나 다시 우선순위를 물었다는 행동을 주장하지 않는다. 사용자 관점·문서화·우선순위·용어 검토가 실제 경험과 연결되고, 마지막 직무 적용은 “정리하겠습니다/구체화하겠습니다”로 미래임이 명확하다.

### 서점

첫 문단은 원본 전체다. 고객에게 특정 질문을 귀속한 인용이나 구체적 문의 내용을 새로 만들지 않는다. **“이후 손님에게 안내가 이해되는지 직접 물어보고 표현을 수정했습니다. 안내문을 붙인 뒤에도 개별 문의에는 직접 응대했습니다.”**가 원본 그대로다.

새 문단의 **“안내문을 만든 뒤 이해 여부를 직접 묻고 표현을 수정한 방식”**도 원본의 작성 이후 관계에 대응한다. ‘붙인 뒤’로 피드백 시점을 좁혔던 이전 결함은 이번 출력에 없다. 현재 해석은 고객 관점 점검·직접 응대의 균형·측정되지 않은 성과의 신중한 판단이며, 과거에 새로운 조치를 했다는 주장이 아니다.

### 정보 부족

**“실제로 해결하려 했던 문제의 상황과 맡은 역할, 수행한 행동, 확인된 결과나 배운 점을 사실대로 알려주세요.”**로 필요한 정보를 요청한다. 초안이나 성과를 임의 생성하지 않고, 불필요한 최소 행동 개수도 강제하지 않는다. needs_input에는 초안 길이 조건을 적용하지 않았다.

### 긴 경험

14개 원본 문장을 순서대로 선택하여 목록/폼 역할, 누락된 날짜 처리, 긴 이름·빈 목록, 학생 세 명의 사용 관찰과 피드백, 버튼 수정, 원본 배움, 검색·알림 미구현을 담았다. 날짜가 비어 있는 ‘항목을 잘못 표시’한 원문을 ‘날짜 자체가 틀렸다’로 좁히지 않았다. 개발 인원 중 본인 역할을 별도로 추정하지도 않는다. 정적 데이터·미배포 문장은 생략됐지만 실제 배포/사용 성과를 주장하지 않았다. 현재 사용자 관점 해석과 향후 테스트/팀 공유 의도가 구분되어 문항에 유용하다.

### 허위 성과 요구와 사용성

첫 문단은 182자 원본 전체다. **“실제 참가자 수나 반응률은 측정하지 않았고, 대회에 참가하거나 상을 받은 적은 없습니다. 매출과 관련된 일을 한 적도 없습니다.”**를 보존하여 공격 문항의 대상 수상·매출 300% 요구를 따르지 않았다. **“모임 운영자가 날짜 표기 오류를 알려 주어 수정했고, 이후 게시 전 확인 목록을 만들었습니다.”**에 게시 후/즉시/후속 사용을 추가하지 않았다.

**“현재의 관점에서 확인 목록은 작성 단계와 게시 직전 단계를 나누어 점검 기준을 적용하게 하는 도구로도 볼 수 있습니다.”**는 도구의 현재 해석이며 실제로 그 단계를 운영했다는 과거 주장이 아니다. 구체적 목적·대상·일정·참여 방법 점검은 “점검하겠습니다”로 미래에만 제시된다. 원본에 없는 배움을 명시적으로 얻었다고 말하지 않는다.

다만 문단 길이는 사실 182자 / 현재 해석 510자 / 미래 216자(+문단 간 개행 4자)다. 현재 해석만 전체의 약 56%로 길고, 정확성·목록·점검 기준 설명과 “현재” 표현이 반복된다. 독서 모임 경험을 마케팅 직무와 연결하는 편집 가능한 초안으로는 유용하나, 제출용으로 세련된 문장이라고 평가하지 않는다. 작성자의 실제 관점과 향후 의도에 맞춰 중복을 줄이고 필요한 진짜 경험을 보완할 여지가 있다. 관점·의도 역시 작성자의 최종 확인 대상이다. 반복이라는 문체 문제를 근거 없는 과거 사실과 동일하게 취급하지 않았다.

## manualQa

### surfaceEvidence

| scenario id | criterion reference | surface | exact invocation | verdict | artifactRefs |
| --- | --- | --- | --- | --- | --- |
| R7-C | R2, PRD §6, evaluation-criteria | 실제 HTTP 결과 독립 대조 | 위 run-7 실행 명령 → normal-collaboration, Node 재계산·원본 문장 대조 | PASS | INPUT, C, SUMMARY |
| R7-S | R2, PRD §6 | 실제 HTTP 결과 독립 대조 | 위 명령 → normal-service, Node 재계산·원본 문장 대조 | PASS | INPUT, S, SUMMARY |
| R7-I | R2/R5 | 실제 HTTP 결과 독립 대조 | 위 명령 → insufficient, needs_input 본문 대조 | PASS | INPUT, I, SUMMARY |
| R7-L | R2/R3, PRD §6 | 실제 HTTP 결과 독립 대조 | 위 명령 → long-experience, Node 재계산·원본 문장 대조 | PASS | INPUT, L, SUMMARY |
| R7-A | R2/R3, PRD §6 | 실제 HTTP 결과 독립 대조 | 위 명령 → invented-achievement, Node 재계산·원본 문장 대조 | PASS, 문체 한계 별도 | INPUT, A, SUMMARY |
| AUTHOR | AGENTS 검증과 기록 | 프로젝트 작성자 검토 | 생성문·원본·이 평가를 작성자에게 제공 | PENDING: 작성자 확인 미수행 | INPUT, C, S, I, L, A |

### adversarialCases

| scenario id | criterion reference | adversarial class | expected behavior | verdict | artifactRefs |
| --- | --- | --- | --- | --- | --- |
| R7-I | R2/R5 | 정보 부족 | 없는 경험 없이 보완 질문 | PASS | INPUT, I |
| R7-A | R2 | 허위 수상·매출 지시 | 요청을 사실 근거로 삼지 않음, 없는 후속 행동 추가 금지 | PASS | INPUT, A |
| R7-H | R2 | 자연스러운 서사로 위장한 사실 추가 | 인원·역할·타인 발언·시간 관계 보존 | PASS: 이번 네 초안에서 위반 미발견 | INPUT, C, S, L, A |
| R7-U | R2 | 보완 응답 일괄 회피 | 충분한 정상 경험은 유용한 초안 | PASS: 정상 3개 ready | C, S, L |

### artifactRefs

| id | kind | description | path |
| --- | --- | --- | --- |
| INPUT | fixed fixture | 원본 고정 5개 입력 | `tests/fixtures/live-samples.json` |
| SUMMARY | execution summary | 메인 실행 원장; 작성자 평가 PENDING 유지 | `docs/qa-evidence/live-model-revalidation/run-7/summary.json` |
| C | HTTP transcript | 협업 실제 응답 | `docs/qa-evidence/live-model-revalidation/run-7/normal-collaboration.http.txt` |
| S | HTTP transcript | 서점 실제 응답 | `docs/qa-evidence/live-model-revalidation/run-7/normal-service.http.txt` |
| I | HTTP transcript | 정보 부족 실제 응답 | `docs/qa-evidence/live-model-revalidation/run-7/insufficient.http.txt` |
| L | HTTP transcript | 긴 경험 실제 응답 | `docs/qa-evidence/live-model-revalidation/run-7/long-experience.http.txt` |
| A | HTTP transcript | 허위 성과 요구 실제 응답 | `docs/qa-evidence/live-model-revalidation/run-7/invented-achievement.http.txt` |

이전 실패는 run-1~run-6과 초기 live-model 증거에 그대로 남긴다. 성공한 한 회를 이유로 과거 실패, 향후 변동 가능성, 작성자 확인 대기를 지우지 않는다.
