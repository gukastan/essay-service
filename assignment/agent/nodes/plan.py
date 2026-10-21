"""D assembles and revises bounded writing plans without a model call."""

from agent.budget import ExecutionBudget, RevisionReservation
from agent.contracts import PlanClaim, PlanParagraph, WritingPlan
from agent.flow_state import EvaluationBinding, validate_plan_context
from agent.nodes.writing_support import (
    WritingContext,
    WritingError,
    current_evaluation,
    require_reservation,
    sentence_spans,
)
from agent.state import WorkflowState


def build_plan(
    state: WorkflowState, budget: ExecutionBudget, reservation: RevisionReservation | None = None
) -> WorkflowState:
    context = WritingContext.from_state(state)
    version = 1
    issues = ()
    binding = None
    if reservation is not None:
        require_reservation(budget, reservation, "D")
        binding = current_evaluation(state)
        issues = binding.evaluation.issues
        if not issues or any(item.scope == "missing_info" for item in issues):
            raise WritingError("INVALID_REVISION")
        if not any(item.scope == "plan_or_claim" for item in issues):
            raise WritingError("INVALID_REVISION")
        version = 2
    elif state.get("plan") is not None or budget.snapshot().revision_count:
        raise WritingError("INVALID_REVISION")
    if (
        context.analysis.gaps
        or not context.analysis.experience_evidence
        or context.research.resolved_company is None
        or not context.research.job_requirements
    ):
        raise WritingError("MISSING_EVIDENCE")
    candidates = select_candidates(context, binding)
    if any(
        req.mandatory and not req.candidate_evidence_ids for req in context.analysis.requirements
    ):
        raise WritingError("MISSING_EVIDENCE")
    spans = sentence_spans(context.request.experience)
    selected = sorted(
        (item for item in context.analysis.experience_evidence if item.id in candidates),
        key=lambda item: item.start,
    )
    if not selected or any((item.start, item.end) not in spans for item in selected):
        raise WritingError("INVALID_SENTENCE")
    claims = [
        PlanClaim(
            id=f"personal-{index}", text=item.quote, kind="user_fact", evidence_ids=(item.id,)
        )
        for index, item in enumerate(selected, 1)
    ]
    # Job evidence takes precedence; optional company values are never fabricated.
    job = context.research.job_requirements[:1]
    claims.extend(
        PlanClaim(id=f"job-{index}", text=item.text, kind="company_fact", evidence_ids=(item.id,))
        for index, item in enumerate(job, 1)
    )
    claims.extend(
        (
            PlanClaim(
                id="interpretation",
                text="현재 관점에서 경험과 직무의 연결을 설명한다.",
                kind="interpretation",
                evidence_ids=(selected[0].id,),
            ),
            PlanClaim(
                id="future",
                text="입사 후의 구체적인 실행 계획을 설명한다.",
                kind="future_plan",
                evidence_ids=tuple(item.id for item in job),
            ),
        )
    )
    requirements = tuple(req.id for req in context.analysis.requirements)
    instruction = " ".join(item.instruction for item in issues)
    purpose = instruction[:200] if instruction else "원문 경험과 직무 근거를 순서대로 제시"
    paragraphs = (
        PlanParagraph(
            id="evidence",
            purpose=purpose,
            order=1,
            target_characters=450,
            requirement_ids=requirements,
            claim_ids=tuple(c.id for c in claims[:-2]),
        ),
        PlanParagraph(
            id="connection",
            purpose="현재 해석과 미래 계획을 구분하여 문항에 답변",
            order=2,
            target_characters=450,
            requirement_ids=requirements,
            claim_ids=("interpretation", "future"),
        ),
    )
    if issues:
        paragraphs = (
            PlanParagraph(
                id="evidence",
                purpose=purpose,
                order=1,
                target_characters=400,
                requirement_ids=requirements,
                claim_ids=tuple(c.id for c in claims[:-2]),
            ),
            PlanParagraph(
                id="interpretation",
                purpose="지적에 따라 현재 해석을 독립하여 설명",
                order=2,
                target_characters=250,
                requirement_ids=requirements,
                claim_ids=("interpretation",),
            ),
            PlanParagraph(
                id="future",
                purpose="지적에 따라 미래 실행 계획을 독립하여 설명",
                order=3,
                target_characters=250,
                requirement_ids=requirements,
                claim_ids=("future",),
            ),
        )
    plan = WritingPlan(
        version=version,
        selected_evidence_ids=tuple(item.id for item in selected) + tuple(item.id for item in job),
        claims=tuple(claims),
        paragraphs=paragraphs,
    )
    validate_plan_context(plan, context.analysis, context.research)
    return WorkflowState(
        plan=plan,
        evaluation=None,
        revision_count=budget.snapshot().revision_count,
        usage=budget.snapshot(),
    )


def select_candidates(context: WritingContext, binding: EvaluationBinding | None) -> set[str]:
    """Use B's ranked candidates; reconsider affected selections on a D revision."""
    affected: set[str] = set()
    previous: set[str] = set()
    if binding is not None:
        previous = set(binding.plan.selected_evidence_ids)
        for issue in binding.evaluation.issues:
            if issue.scope != "plan_or_claim":
                continue
            for paragraph in binding.plan.paragraphs:
                if (
                    (not issue.paragraph_ids and not issue.claim_ids)
                    or paragraph.id in issue.paragraph_ids
                    or set(paragraph.claim_ids).intersection(issue.claim_ids)
                ):
                    affected.update(paragraph.requirement_ids)
    selected: set[str] = set()
    for requirement in context.analysis.requirements:
        candidates = requirement.candidate_evidence_ids
        alternatives = tuple(identifier for identifier in candidates if identifier not in previous)
        if requirement.id in affected and alternatives:
            candidates = alternatives
        selected.update(candidates[:1])
    return selected
