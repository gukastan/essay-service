from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

import anyio
import pytest
from pydantic import BaseModel

from agent.budget import ExecutionBudget, OperationContext
from agent.contracts import (
    DraftEnvelope,
    DraftRequest,
    EvaluationIssue,
    FitReason,
    JobRequirement,
    ParagraphSpan,
    PlanClaim,
    ResearchInput,
    ResearchResult,
    UserProvidedSource,
)
from agent.deps import WorkflowDeps, new_request
from agent.essay_graph import EssayWorkflow
from agent.essay_route import decide
from agent.flow_state import bind_evaluation
from agent.mcp_client import MCPClient
from agent.nodes.analyze import AnalysisOutcome, AnalyzeNode
from agent.nodes.research import ResearchNode, ResearchSuccess
from agent.nodes.revise import RevisionInput, RevisionPatches, SentencePatch
from agent.nodes.write import WritingInput
from agent.providers import ModelResult, StructuredModelRequest
from agent.validate_evidence import ReviewInput, evaluation_from_issues, general_issue
from tests.test_mcp import wire_client
from tests.test_personal_analysis import analysis, request
from tests.test_review_evidence import review_input
from tests.wire_fixture import HttpReply, response_body, serve_wire


def controlled_draft(plan: WritingInput, target_characters: int = 900) -> DraftEnvelope:
    original = {claim.id: claim.text for claim in plan.plan.claims}
    fixed = sum(
        len(value) for key, value in original.items() if key not in {"interpretation", "future"}
    )
    separators = sum(len(paragraph.claim_ids) - 1 for paragraph in plan.plan.paragraphs)
    separators += 2 * (len(plan.plan.paragraphs) - 1)
    room = (
        target_characters
        - fixed
        - separators
        - len("현재 라고 생각합니다.")
        - len("입사 후 를 실천하겠습니다.")
    )
    interpretation = "현재 " + "가" * (room // 2) + "라고 생각합니다."
    future = "입사 후 " + "나" * (room - room // 2) + "를 실천하겠습니다."
    claims = tuple(
        PlanClaim(
            id=claim.id,
            text=(
                interpretation
                if claim.id == "interpretation"
                else future
                if claim.id == "future"
                else claim.text
            ),
            kind=claim.kind,
            evidence_ids=claim.evidence_ids,
        )
        for claim in plan.plan.claims
    )
    by_id = {claim.id: claim.text for claim in claims}
    body = ""
    spans: list[ParagraphSpan] = []
    for paragraph in plan.plan.paragraphs:
        if body:
            body += "\n\n"
        start = len(body)
        body += " ".join(by_id[identifier] for identifier in paragraph.claim_ids)
        spans.append(ParagraphSpan(paragraph_id=paragraph.id, start=start, end=len(body)))
    return DraftEnvelope(
        version=plan.plan.version,
        plan_version=plan.plan.version,
        draft=body,
        paragraphs=tuple(spans),
        claim_map=claims,
        fit_reasons=(
            FitReason(
                experience_evidence_ids=("e1",),
                job_requirement_ids=tuple(item.id for item in plan.research.job_requirements),
                reason="경험과 직무 요건을 연결합니다.",
            ),
        ),
    )


class ControlledProvider:
    def __init__(
        self,
        source: DraftRequest,
        reviews: tuple[Literal["pass", "plan", "wording", "missing"], ...] = ("pass",),
        *,
        analysis_gap: bool = False,
        missing_experience: bool = False,
    ) -> None:
        self.source: DraftRequest = source
        self.roles: list[str] = []
        self.reviews: tuple[Literal["pass", "plan", "wording", "missing"], ...] = reviews
        self.analysis_gap: bool = analysis_gap
        self.missing_experience: bool = missing_experience

    def review_issues(self, context: ReviewInput) -> tuple[EvaluationIssue, ...]:
        index = self.roles.count("review") - 1
        mode = self.reviews[min(index, len(self.reviews) - 1)]
        match mode:
            case "pass":
                return ()
            case "plan":
                return (general_issue("question_coverage", "구성을 다시 검토해 주세요."),)
            case "missing":
                return (
                    general_issue("question_coverage", "경험 정보가 필요합니다.", ("experience",)),
                )
            case "wording":
                claim = next(
                    item for item in context.draft.claim_map if item.id == "interpretation"
                )
                start = context.draft.draft.index(claim.text)
                return (
                    EvaluationIssue(
                        id="expression-issue",
                        criterion_id="expression_kind",
                        claim_ids=(claim.id,),
                        paragraph_ids=(),
                        start=start,
                        end=start + len(claim.text),
                        reason="현재 해석을 명확히 표시해 주세요.",
                        scope="wording",
                        instruction="현재 해석만 고쳐 주세요.",
                        missing_fields=(),
                    ),
                )

    async def generate[T: BaseModel](
        self, request: StructuredModelRequest[T], budget: ExecutionBudget
    ) -> ModelResult[T]:
        async def invoke(_context: OperationContext) -> ModelResult[T]:
            self.roles.append(request.role)
            match request.role:
                case "analysis":
                    value = analysis(self.source)
                    if self.analysis_gap:
                        value = value.model_copy(update={"gaps": ("맡은 행동은 무엇인가요?",)})
                    if self.missing_experience:
                        value = value.model_copy(
                            update={
                                "requirements": tuple(
                                    item.model_copy(update={"candidate_evidence_ids": ()})
                                    for item in value.requirements
                                ),
                                "experience_evidence": (),
                            }
                        )
                case "writer":
                    if request.schema is RevisionPatches:
                        revision = RevisionInput.model_validate_json(request.input)
                        claim = next(
                            item for item in revision.draft.claim_map if item.id == "interpretation"
                        )
                        start = revision.draft.draft.index(claim.text)
                        replacement = (
                            "현재 "
                            + "다" * (len(claim.text) - len("현재 라고 생각합니다."))
                            + "라고 생각합니다."
                        )
                        value = RevisionPatches(
                            draft_version=revision.draft.version,
                            plan_version=revision.plan.version,
                            patches=(
                                SentencePatch(
                                    claim_id=claim.id,
                                    start=start,
                                    end=start + len(claim.text),
                                    text=replacement,
                                ),
                            ),
                        )
                    else:
                        value = controlled_draft(WritingInput.model_validate_json(request.input))
                case "review":
                    review = ReviewInput.model_validate_json(request.input)
                    value = evaluation_from_issues(review, self.review_issues(review))
                case "research":
                    raise AssertionError
            wire = value.model_dump_json(include=set(request.schema.model_fields))
            return ModelResult(request.schema.model_validate_json(wire), None)

        return await budget.run_model(request.role, invoke)


@pytest.fixture
def researched(monkeypatch: pytest.MonkeyPatch) -> list[ResearchInput]:
    calls: list[ResearchInput] = []

    async def research_stub(
        _self: ResearchNode,
        public: ResearchInput,
        budget: ExecutionBudget,
        _request_id: UUID,
    ) -> ResearchSuccess:
        calls.append(public)

        async def invoke(_context: OperationContext) -> ResearchSuccess:
            return ResearchSuccess(
                result=ResearchResult(
                    resolved_company="회사",
                    sources=(
                        UserProvidedSource(
                            id="s1",
                            kind="user_provided",
                            title="시험 공고",
                            checked_at=datetime.now(UTC),
                            excerpt="협업을 요구한다.",
                        ),
                    ),
                    company_facts=(),
                    job_requirements=(
                        JobRequirement(id="j1", text="협업을 요구한다.", source_ids=("s1",)),
                    ),
                    gaps=(),
                ),
                tool_calls_reported=0,
                usage=None,
            )

        return await budget.run_native_research(invoke)

    monkeypatch.setattr(ResearchNode, "run", research_stub)
    return calls


@pytest.mark.anyio
async def test_actual_role_nodes_join_into_reviewed_ready(
    researched: list[ResearchInput],
) -> None:
    source = request()
    provider = ControlledProvider(source)
    outcome = await EssayWorkflow(WorkflowDeps(provider, MCPClient())).run(source)
    assert outcome.status == "ready", (outcome, provider.roles)
    assert outcome.character_count == 900
    assert outcome.usage.model_calls == 4
    assert outcome.usage.revision_count == 0
    assert provider.roles == ["analysis", "writer", "review"]
    assert len(researched) == 1
    assert not hasattr(researched[0], "experience")
    assert not hasattr(researched[0], "question")


@pytest.mark.anyio
async def test_unknown_company_without_posting_writes_from_user_input() -> None:
    # Given
    source = request().model_copy(update={"company": "가상회사 새봄", "role": "서비스 기획"})
    provider = ControlledProvider(source)
    # When
    outcome = await EssayWorkflow(WorkflowDeps(provider, MCPClient())).run(source)
    # Then
    assert outcome.status == "ready", (outcome, provider.roles)
    assert outcome.sources == ()
    assert outcome.evidence.job_requirements == ()
    assert outcome.evidence.fit_reasons[0].job_requirement_ids == ()
    assert all(claim.kind != "company_fact" for claim in outcome.evidence.claim_map)


@pytest.mark.anyio
@pytest.mark.parametrize("route", ["plan", "wording"])
async def test_review_repair_runs_one_writer_and_full_second_review(
    researched: list[ResearchInput],
    route: Literal["plan", "wording"],
) -> None:
    source = request()
    provider = ControlledProvider(source, (route, "pass"))
    outcome = await EssayWorkflow(WorkflowDeps(provider, MCPClient())).run(source)
    assert outcome.status == "ready", (outcome, provider.roles)
    assert outcome.usage.model_calls == 6
    assert outcome.usage.revision_count == 1
    assert provider.roles == ["analysis", "writer", "review", "writer", "review"]
    assert len(researched) == 1


@pytest.mark.anyio
async def test_review_missing_information_returns_draft_without_revision(
    researched: list[ResearchInput],
) -> None:
    source = request()
    provider = ControlledProvider(source, ("missing",))
    outcome = await EssayWorkflow(WorkflowDeps(provider, MCPClient())).run(source)
    assert outcome.status == "review_needed", (outcome, provider.roles)
    assert outcome.draft
    assert outcome.review_issues[0].missing_fields == ("experience",)
    assert provider.roles == ["analysis", "writer", "review"]
    assert len(researched) == 1


@pytest.mark.anyio
async def test_failed_revision_returns_draft_and_issues_without_third_writer(
    researched: list[ResearchInput],
) -> None:
    source = request()
    provider = ControlledProvider(source, ("plan", "plan"))
    outcome = await EssayWorkflow(WorkflowDeps(provider, MCPClient())).run(source)
    assert outcome.status == "review_needed", (outcome, provider.roles)
    assert outcome.draft
    assert outcome.review_issues[0].criterion_id == "question_coverage"
    assert provider.roles == ["analysis", "writer", "review", "writer", "review"]
    assert len(researched) == 1


@pytest.mark.anyio
async def test_graph_uses_actual_stdio_mcp_and_verified_user_posting() -> None:
    posting = "회사 개발 requirements: 협업을 요구한다."
    source = request().model_copy(update={"job_posting_text": posting})
    provider = ControlledProvider(source)
    candidate = ResearchResult(
        resolved_company="회사",
        sources=(
            UserProvidedSource(
                id="model-source",
                kind="user_provided",
                title="시험 공고",
                checked_at=datetime.now(UTC),
                excerpt=posting,
            ),
        ),
        company_facts=(),
        job_requirements=(
            JobRequirement(id="j1", text="협업을 요구한다.", source_ids=("model-source",)),
        ),
        gaps=(),
    )
    body = response_body(candidate.model_dump_json(by_alias=True), search=True)
    with serve_wire(lambda _payload: HttpReply(body)) as wire:
        async with MCPClient(wire_client(wire.base_url)) as mcp:
            outcome = await EssayWorkflow(WorkflowDeps(provider, mcp)).run(source)
    assert outcome.status == "ready", (outcome, provider.roles)
    assert outcome.usage.model_calls == 4
    assert outcome.evidence.job_requirements[0].source_ids == ("user-posting",)
    assert wire.requests.qsize() == 1


@pytest.mark.anyio
async def test_mismatched_optional_posting_does_not_block_requested_role() -> None:
    # Given
    source = request().model_copy(
        update={"job_posting_text": "회사 운영 지원 requirements: 협업을 요구한다."}
    )
    provider = ControlledProvider(source)
    candidate = ResearchResult(
        resolved_company="회사",
        sources=(
            UserProvidedSource(
                id="model-source",
                kind="user_provided",
                title="다른 직무의 시험 공고",
                checked_at=datetime.now(UTC),
                excerpt=source.job_posting_text or "",
            ),
        ),
        company_facts=(),
        job_requirements=(
            JobRequirement(id="j1", text="협업을 요구한다.", source_ids=("model-source",)),
        ),
        gaps=(),
    )
    body = response_body(candidate.model_dump_json(by_alias=True), search=True)
    # When
    with serve_wire(lambda _payload: HttpReply(body)) as wire:
        async with MCPClient(wire_client(wire.base_url)) as mcp:
            outcome = await EssayWorkflow(WorkflowDeps(provider, mcp)).run(source)
    # Then
    assert outcome.status == "ready", (outcome, provider.roles)
    assert outcome.evidence.job_requirements == ()
    assert outcome.evidence.fit_reasons[0].job_requirement_ids == ()
    assert wire.requests.qsize() == 1


@pytest.mark.anyio
async def test_analysis_gap_cancels_parallel_research_before_writing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = request()
    provider = ControlledProvider(source, analysis_gap=True, missing_experience=True)
    started = anyio.Event()
    cancelled: list[bool] = []

    async def slow_research(
        _self: ResearchNode,
        _public: ResearchInput,
        budget: ExecutionBudget,
        _request_id: UUID,
    ) -> ResearchSuccess:
        async def wait_for_result(_context: OperationContext) -> ResearchSuccess:
            started.set()
            try:
                await anyio.sleep(5)
            except anyio.get_cancelled_exc_class():
                cancelled.append(True)
                raise
            raise AssertionError

        return await budget.run_native_research(wait_for_result)

    original_analysis = AnalyzeNode.run

    async def after_research_starts(
        node: AnalyzeNode,
        input: DraftRequest,
        budget: ExecutionBudget,
        request_id: UUID,
    ) -> AnalysisOutcome:
        await started.wait()
        return await original_analysis(node, input, budget, request_id)

    monkeypatch.setattr(AnalyzeNode, "run", after_research_starts)
    monkeypatch.setattr(ResearchNode, "run", slow_research)
    outcome = await EssayWorkflow(WorkflowDeps(provider, MCPClient())).run(source)
    assert started.is_set()
    assert outcome.status == "needs_input"
    assert cancelled == [True]
    assert provider.roles == ["analysis"]


def test_missing_information_wins_over_plan_issue_in_routing() -> None:
    reviewed = review_input()
    context = new_request(reviewed.request)
    evaluation = evaluation_from_issues(
        reviewed,
        (
            general_issue("question_coverage", "경험 정보가 필요합니다.", ("experience",)),
            general_issue("job_fit", "계획을 다시 세워야 합니다."),
        ),
    )
    state = context.state
    state["evaluation"] = bind_evaluation(
        context.request_id, evaluation, reviewed.draft, reviewed.plan
    )
    decision = decide(state, context)
    assert decision.get("route") == "U"
    terminal = decision.get("terminal_reason")
    assert terminal is not None
    assert terminal.kind == "review_needed"
    assert context.budget.snapshot().revision_count == 0
