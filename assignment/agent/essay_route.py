"""Code-owned review routing and terminal response construction."""

from typing import TYPE_CHECKING, Literal

from agent.budget import ExecutionBudget
from agent.contracts import (
    Claim,
    ErrorResponse,
    Evidence,
    MissingInputTerminal,
    NeedsInputResponse,
    QualityTerminal,
    ReadyResponse,
    ReadyTerminal,
    Usage,
)
from agent.deps import RequestContext
from agent.flow_state import require_ready_evaluation
from agent.providers import ProviderError
from agent.state import WorkflowState

if TYPE_CHECKING:
    from agent.contract_flow_evaluation import MissingField


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


def _missing_response(state: WorkflowState, context: RequestContext) -> NeedsInputResponse:
    binding = state.get("evaluation")
    if binding is None:
        raise ProviderError("INVALID_RESPONSE")
    missing = tuple(issue for issue in binding.evaluation.issues if issue.scope == "missing_info")
    fields: tuple[MissingField, ...] = tuple(
        dict.fromkeys(field for issue in missing for field in issue.missing_fields)
    )
    questions = tuple(dict.fromkeys(issue.instruction for issue in missing))
    if not fields or not questions:
        raise ProviderError("INVALID_RESPONSE")
    reason = (
        "EXPERIENCE_INSUFFICIENT"
        if "experience" in fields
        else "COMPANY_AMBIGUOUS"
        if "company" in fields
        else "JOB_EVIDENCE_MISSING"
        if "jobPostingText" in fields
        else "EVIDENCE_INSUFFICIENT"
    )
    return NeedsInputResponse(
        status="needs_input",
        request_id=context.request_id,
        message="초안 작성에 필요한 정보를 보완해 주세요.",
        missing_fields=fields,
        questions=questions,
        reason_code=reason,
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
        response = _missing_response(state, context)
        return WorkflowState(
            route="J",
            terminal_reason=MissingInputTerminal(
                kind="needs_input",
                route="J",
                reason="missing_required_information",
                missing_fields=response.missing_fields,
                questions=response.questions,
                reason_code=response.reason_code,
            ),
            outcome=response,
            usage=context.budget.snapshot(),
        )
    if context.budget.snapshot().revision_count == 1:
        failures = {item.criterion_id for item in evaluation.criteria if not item.passed}
        code: Literal["LENGTH_VALIDATION_FAILED", "QUALITY_CHECK_FAILED"] = (
            "LENGTH_VALIDATION_FAILED" if failures == {"length"} else "QUALITY_CHECK_FAILED"
        )
        return WorkflowState(
            route="J",
            terminal_reason=QualityTerminal(
                kind="quality_failure", route="J", reason="revision_limit", code=code
            ),
            outcome=ErrorResponse(
                status="error",
                request_id=context.request_id,
                code=code,
                message="이번 생성은 필수 품질 기준을 충족하지 못했습니다.",
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
        evidence=Evidence(
            company_facts=research.company_facts,
            job_requirements=research.job_requirements,
            experience_evidence=analysis.experience_evidence,
            claim_map=tuple(
                Claim(id=item.id, text=item.text, kind=item.kind, evidence_ids=item.evidence_ids)
                for item in draft.claim_map
            ),
            fit_reasons=draft.fit_reasons,
        ),
        review_summary="생성 당시 검토 통과",
        usage=Usage(
            model_calls=context.budget.snapshot().model_calls,
            revision_count=context.budget.snapshot().revision_count,
        ),
    )
    return WorkflowState(outcome=response, usage=context.budget.snapshot())
