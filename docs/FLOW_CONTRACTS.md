# ESSAY-21 공통 흐름 계약 인계

2026-10-20 구현·검증 완료. [최소 명세](NODE_MIN_SPEC.md) · [병렬 개발](PARALLEL_DEVELOPMENT.md) · [검증 보고서](qa-evidence/assignment/flow-foundation/verification.md).

## 2026-10-21 실제 역할 구현 인계

ESSAY-11·12·13·15의 독립 역할/화면 구현·검증을 완료했고 ESSAY-14에서 실제 역할을 연결했다. `essay_collect.py`가 `AnalyzeNode.run(request, budget, request_id)`과 기존 `ResearchNode.run`을 병렬 실행해 `AnalysisJoin.run`에서 개인/회사 근거를 한 번 합류시킨다. `EvidenceBundle`일 때만 D로 진행하고 조기 보완/운영 오류는 작성 전에 종료한다. `build_plan(state, budget)`은 모델 없이 초기 계획을 만들고, `WriteNode.run(state, budget)`이 E를 실행한다. G가 구조/주장 수정이면 `budget.reserve_revision("D")`→`build_plan(..., reservation)`→E, 문장 수정이면 `budget.reserve_revision("I")`→`RevisionNode.run(..., reservation)`으로 보낸다. 두 경로 모두 전체 `ReviewNode.run(state, budget)`을 다시 실행한다. F의 `ReviewAssessment`는 코드·모델 결과와 포착된 요청/초안/계획에 묶인 평가를 포함한다. `essay_route.py`가 G/H/J를 결정하고 `server.py`가 HTTP 상태를 조립한다.

새 Vue는 `web_chat.html`·`web_app.js`·`web_contract.js`·`web_style.css`와 `web_demo_server.py` 프록시에서 실행한다. 프록시는 기본 Python 서버 `127.0.0.1:8001`의 POST `/api/drafts`를 호출한다. API 연결은 ESSAY-14에서 통제 입력으로 확인했고 화면은 합성 응답으로 검증했다. 전체 브라우저 회귀는16, 실제 모델/사실성 검증은17에서 확인한다. [분석](qa-evidence/assignment/analysis/verification.md) · [작성](qa-evidence/assignment/writing/verification.md) · [평가](qa-evidence/assignment/evaluation/verification.md) · [Vue](qa-evidence/assignment/vue/verification.md) · [통합](qa-evidence/assignment/integration/verification.md) 보고서를 따른다.

## 계약과 소유권

공개 타입은 `agent.contracts`에서 가져온다. 기존 ResearchResult·AnalysisResult·WriterResult·ReviewResult와 HTTP 응답 계약은 보존했다. 새 타입은 frozen Pydantic 계약이며 camelCase 직렬화·미정의 필드 거부·컬렉션/문자 수 제한을 적용한다.

| 후속 담당 | 사용 계약 | 실제 책임 |
| --- | --- | --- |
| ESSAY-11 B/C | FlowRequirement, FlowAnalysisResult | requirements·experienceEvidence·gaps 생성과 원문 대조 |
| ESSAY-12 D/E/I | WritingPlan, PlanClaim, PlanParagraph, DraftEnvelope, ParagraphSpan | 계획 조립·본문·부분 수정. 의미 전략은 해당 티켓에서 구체화 |
| ESSAY-13 F | Evaluation, CriterionResult, EvaluationIssue | 모든 필수 기준의 실제 평가와 수정 범위 판정 |
| ESSAY-14 G/H/J | FlowRoute, TerminalReason, EvaluationBinding | 분기 우선순위·호출 연결·최종 HTTP 응답 조립 |
| ESSAY-15 Vue | 기존 DraftResponse와 합성 응답 fixture | ready/needs_input/error 화면. 내부 제어 계약을 HTTP 응답으로 오인하지 않음 |

7개 필수 criterionId는 `contract_evidence`, `user_factuality`, `company_factuality`, `question_coverage`, `job_fit`, `length`, `expression_kind`다. 누락·중복 결과, 실패 기준과 지적의 불일치를 거부한다. issue.scope는 `missing_info | plan_or_claim | wording`이며 wording은 위치가 필요하고 missing_info에만 missingFields가 허용된다.

WritingPlan은 선택 근거·주장 종류/근거·문단의 요구사항/주장 ID·순서·목표 분량·버전을 가진다. 목표 합계는801~1000, 초안은 길이 실패도 평가하도록1~4000 코드 포인트를 허용한다. 문단 범위는 LF 정규화한 본문의 반열린 [start,end) 코드 포인트다. 구조화 텍스트는 짧게 제한하고 숨은 추론 필드는 없다. 버전은 초기1·수정2다.

## 호출 경계

1. B/C 결과: `validate_analysis_context(analysis, request)`로 경험 인용과 실제 원문 위치를 대조한다.
2. D/E/I 결과: `validate_plan_context(plan, analysis, research)`, `validate_draft_context(draft, plan, analysis, research)`로 ID·개인/회사 근거 종류·필수 요구사항 대응·문단/주장 연결을 검사한다.
3. F 호출 **직전** 요청 ID·초안·계획을 포착한다. 응답 후 `bind_evaluation(request_id, evaluation, captured_draft, captured_plan)`으로 묶는다. 응답 도착 시점의 최신 초안으로 다시 묶으면 안 된다.
4. H 직전 `require_ready_evaluation(binding, current_request_id, current_draft, current_plan)`을 호출한다. 다른 요청·다른 버전·동일 버전의 내용 변경·실패 기준·801~1000 범위 밖 초안을 거부한다.

검사 함수와 EvaluationBinding은 `agent.flow_state`에 있다. WorkflowState는 `flow_analysis, plan, draft_envelope, evaluation, route, terminal_reason`을 추가했다. requirements는 flow_analysis 안에만 두고 버전은 각 envelope가 소유한다. EvaluationBinding은 모델 출력이 아닌 코드 소유 객체다. 구조 검사는 의미적 사실성 평가를 대신하지 않는다.

## 공통 수정 예약과 오류

G는 D/I 진입 **전에** `await budget.reserve_revision("D" 또는 "I")`를 실행한다. 기존 요청 잠금 아래 한 경로만 성공하며 실패·취소·시간 초과 후 환급하지 않는다. 성공 결과의 revision_count와 budget.snapshot()을 상태에 반영한다. 상태의 revision_count는 관측용 단조 증가 값이므로 그 값만 보고 수정 권한을 부여하면 안 된다. 사용한 budget으로 initial_state를 재구성해도 예약은 초기화되지 않는다.

`RevisionReservationError("REVISION_EXHAUSTED" | "INVALID_REVISION_ROUTE")`는 수정 제어 오류다. 잘못된 경로는 기회를 소비하지 않는다. 기존 `ExecutionBudgetError`의 LIMIT_EXCEEDED/DEADLINE_EXCEEDED/CANCELLED는 유지하며 기존 조사 오류 어댑터에 수정 오류를 전달하지 않는다.

TerminalReason은 ready(H), needs_input(J), quality_failure(J), operational_error를 구별한다. 정보 부족은 기존 missingFields/questions/reasonCode, 품질 실패는 QUALITY_CHECK_FAILED/LENGTH_VALIDATION_FAILED로 표현한다. 실제200/422 매핑·G 우선순위·전체 ready 조립은 ESSAY-14에서 구현했다.

## 병렬 검증 입력

`tests.flow_fixture`의 analysis()/research()/plan()/draft()/evaluation()과 `tests.test_flow_handoff`의 ready_fixture()/needs_input_fixture()/quality_failure_fixture()를 사용한다. 합성900자 초안은 계약 검사용이며 글 품질 증거가 아니다. F는 작성자의 실제 구현 없이 DraftEnvelope fixture로 검증하고, D/E/I는 FlowAnalysisResult/ResearchResult fixture로 검증할 수 있다. 실제 모듈 조합 검증은14, 전체 API/Vue는16, 유료 모델/사실성 승인은17이다.

정상 모델4회·최대6회·출력18,000토큰·수정1회·모델30초/조사45초/전체180초/클라이언트195초·재시도0을 유지한다. D/G는 코드 단계다. 공통 계약·내보내기·상태·예산·설정은 한 담당자가 수정하며 역할별 파일을 분리한다. 상세 경험 선택·문단 전개·프롬프트·의미 평가 점수/가중치는 후속 설계다.
