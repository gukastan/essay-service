"""Code-owned review routing and terminal response construction."""

from typing import Literal

from agent.budget import ExecutionBudget
from agent.contracts import (
    Claim,
    DraftEnvelope,
    ErrorResponse,
    Evidence,
    FlowAnalysisResult,
    ReadyResponse,
    ReadyTerminal,
    ResearchResult,
    ReviewNeededResponse,
    ReviewNeededTerminal,
    ReviewNotice,
    Usage,
)
from agent.deps import RequestContext
from agent.flow_state import require_current_evaluation, require_ready_evaluation
from agent.providers import ProviderError
from agent.state import WorkflowState


def error_result(context: RequestContext, code: str) -> ErrorResponse:
    match code:
        case "CONFIG_ERROR":
            safe = "CONFIG_ERROR"
        case "TIMEOUT" | "DEADLINE_EXCEEDED":
            safe = "TIMEOUT"
        case "CANCELLED":
            safe = "CANCELLED"
        case "LIMIT_EXCEEDED":
            safe = "BUDGET_EXCEEDED"
        case "MODEL_ERROR" | "REFUSAL" | "INCOMPLETE":
            safe = "MODEL_ERROR"
        case _:
            safe = "INVALID_RESPONSE"
    return ErrorResponse(
        status="error",
        request_id=context.request_id,
        code=safe,
        message="초안 생성 요청을 완료하지 못했습니다.",
    )


def decide(state: WorkflowState, context: RequestContext) -> WorkflowState:
    binding = state.get("evaluation")
    if binding is None:
        raise ProviderError("INVALID_RESPONSE")
    evaluation = binding.evaluation
    if evaluation.all_passed:
        return WorkflowState(
            route="H",
            terminal_reason=ReadyTerminal(kind="ready", route="H", reason="all_criteria_passed"),
            usage=context.budget.snapshot(),
        )
    if any(issue.scope == "missing_info" for issue in evaluation.issues):
        return WorkflowState(
            route="U",
            terminal_reason=ReviewNeededTerminal(
                kind="review_needed",
                route="U",
                reason="missing_required_information",
            ),
            usage=context.budget.snapshot(),
        )
    if context.budget.snapshot().revision_count == 1:
        return WorkflowState(
            route="U",
            terminal_reason=ReviewNeededTerminal(
                kind="review_needed", route="U", reason="revision_limit"
            ),
            usage=context.budget.snapshot(),
        )
    if any(issue.scope == "plan_or_claim" for issue in evaluation.issues):
        route: Literal["D", "I"] = "D"
    elif evaluation.issues and all(issue.scope == "wording" for issue in evaluation.issues):
        route = "I"
    else:
        raise ProviderError("INVALID_RESPONSE")
    return WorkflowState(route=route, usage=context.budget.snapshot())


async def reserve_route(state: WorkflowState, budget: ExecutionBudget) -> WorkflowState:
    route = state.get("route")
    if route not in ("D", "I"):
        raise ProviderError("INVALID_RESPONSE")
    _ = await budget.reserve_revision(route)
    return WorkflowState(revision_count=1, usage=budget.snapshot())


def ready(state: WorkflowState, context: RequestContext) -> WorkflowState:
    binding = state.get("evaluation")
    draft = state.get("draft_envelope")
    plan = state.get("plan")
    analysis = state.get("flow_analysis")
    research = state.get("research")
    if binding is None or draft is None or plan is None or analysis is None or research is None:
        raise ProviderError("INVALID_RESPONSE")
    require_ready_evaluation(binding, context.request_id, draft, plan)
    response = ReadyResponse(
        status="ready",
        request_id=context.request_id,
        draft=draft.draft,
        character_count=len(draft.draft),
        sources=research.sources,
        evidence=_evidence(analysis, research, draft),
        review_summary="생성 당시 검토 통과",
        usage=Usage(
            model_calls=context.budget.snapshot().model_calls,
            revision_count=context.budget.snapshot().revision_count,
        ),
    )
    return WorkflowState(outcome=response, usage=context.budget.snapshot())


def review_needed(state: WorkflowState, context: RequestContext) -> WorkflowState:
    binding = state.get("evaluation")
    draft = state.get("draft_envelope")
    plan = state.get("plan")
    analysis = state.get("flow_analysis")
    research = state.get("research")
    if binding is None or draft is None or plan is None or analysis is None or research is None:
        raise ProviderError("INVALID_RESPONSE")
    require_current_evaluation(binding, context.request_id, draft, plan)
    if binding.evaluation.all_passed:
        raise ProviderError("INVALID_RESPONSE")
    response = ReviewNeededResponse(
        status="review_needed",
        request_id=context.request_id,
        draft=draft.draft,
        character_count=len(draft.draft),
        sources=research.sources,
        evidence=_evidence(analysis, research, draft),
        review_summary="생성 당시 기준 미충족 · 직접 검토 필요",
        review_issues=tuple(
            ReviewNotice(
                criterion_id=issue.criterion_id,
                reason=issue.reason,
                instruction=issue.instruction,
                missing_fields=issue.missing_fields,
            )
            for issue in binding.evaluation.issues
        ),
        usage=Usage(
            model_calls=context.budget.snapshot().model_calls,
            revision_count=context.budget.snapshot().revision_count,
        ),
    )
    return WorkflowState(outcome=response, usage=context.budget.snapshot())


def _evidence(
    analysis: FlowAnalysisResult, research: ResearchResult, draft: DraftEnvelope
) -> Evidence:
    return Evidence(
        company_facts=research.company_facts,
        job_requirements=research.job_requirements,
        experience_evidence=analysis.experience_evidence,
        claim_map=tuple(
            Claim(id=item.id, text=item.text, kind=item.kind, evidence_ids=item.evidence_ids)
            for item in draft.claim_map
        ),
        fit_reasons=draft.fit_reasons,
    )
