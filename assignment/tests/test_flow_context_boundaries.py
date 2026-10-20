from typing import Literal
from uuid import uuid4

import pytest

from agent.budget import ExecutionBudget, ExecutionBudgetError, RevisionReservationError
from agent.contracts import (
    DraftEnvelope,
    Evaluation,
    FlowAnalysisResult,
    ResearchResult,
    WritingPlan,
)
from agent.flow_state import (
    FlowStateError,
    bind_evaluation,
    require_ready_evaluation,
    validate_draft_context,
    validate_evaluation_context,
    validate_plan_context,
)
from agent.nodes.research import error_response
from tests.flow_fixture import analysis, draft, evaluation, plan, research


def company_research() -> ResearchResult:
    return ResearchResult.model_validate(
        {
            "resolvedCompany": "Fixture company",
            "sources": [
                {
                    "id": "s1",
                    "kind": "user_provided",
                    "title": "Synthetic posting",
                    "checkedAt": "2026-10-20T00:00:00Z",
                    "excerpt": "Testing is required.",
                }
            ],
            "companyFacts": [{"id": "f1", "text": "Company fact.", "sourceIds": ["s1"]}],
            "jobRequirements": [{"id": "j1", "text": "Testing.", "sourceIds": ["s1"]}],
            "gaps": [],
        }
    )


@pytest.mark.parametrize(("kind", "evidence_id"), [("user_fact", "f1"), ("company_fact", "e1")])
def test_plan_rejects_personal_company_provenance_swap(kind: str, evidence_id: str) -> None:
    # Given
    payload = plan().model_dump()
    payload["selected_evidence_ids"] = [evidence_id]
    payload["claims"][0]["kind"] = kind
    payload["claims"][0]["evidence_ids"] = [evidence_id]
    candidate = WritingPlan.model_validate(payload)
    # When / Then
    with pytest.raises(FlowStateError) as raised:
        validate_plan_context(candidate, analysis(), company_research())
    assert raised.value.code == "SOURCE_TYPE_MISMATCH"


def test_company_and_personal_evidence_cannot_share_an_id() -> None:
    # Given
    payload = company_research().model_dump()
    payload["company_facts"][0]["id"] = "e1"
    candidate = ResearchResult.model_validate(payload)
    # When / Then
    with pytest.raises(FlowStateError) as raised:
        validate_plan_context(plan(), analysis(), candidate)
    assert raised.value.code == "INVALID_REFERENCE"


def test_plan_rejects_nonexistent_selected_evidence() -> None:
    # Given
    payload = plan().model_dump()
    payload["selected_evidence_ids"] = [*payload["selected_evidence_ids"], "missing"]
    candidate = WritingPlan.model_validate(payload)
    # When / Then
    with pytest.raises(FlowStateError) as raised:
        validate_plan_context(candidate, analysis(), research())
    assert raised.value.code == "INVALID_REFERENCE"


def test_plan_rejects_omitted_mandatory_requirement() -> None:
    # Given
    payload = analysis().model_dump()
    payload["requirements"] = [
        *payload["requirements"],
        {
            "id": "r2",
            "text": "Outcome.",
            "mandatory": True,
            "check_condition": "An outcome is present.",
            "candidate_evidence_ids": ["e1"],
        },
    ]
    candidate = FlowAnalysisResult.model_validate(payload)
    # When / Then
    with pytest.raises(FlowStateError) as raised:
        validate_plan_context(plan(), candidate, research())
    assert raised.value.code == "INVALID_REFERENCE"


@pytest.mark.parametrize("requirement_id", ["f1", "unknown"])
def test_plan_rejects_unknown_requirement_mapping(requirement_id: str) -> None:
    # Given
    payload = plan().model_dump()
    payload["paragraphs"][0]["requirement_ids"] = [requirement_id]
    candidate = WritingPlan.model_validate(payload)
    # When / Then
    with pytest.raises(FlowStateError) as raised:
        validate_plan_context(candidate, analysis(), company_research())
    assert raised.value.code == "INVALID_REFERENCE"


@pytest.mark.parametrize(("personal", "job"), [("f1", "j1"), ("e1", "f1"), ("missing", "j1")])
def test_fit_reason_rejects_wrong_domain_or_unknown_reference(personal: str, job: str) -> None:
    # Given
    payload = draft().model_dump()
    payload["fit_reasons"] = [
        {
            "experience_evidence_ids": [personal],
            "job_requirement_ids": [job],
            "reason": "Synthetic connection.",
        }
    ]
    candidate = DraftEnvelope.model_validate(payload)
    # When / Then
    with pytest.raises(FlowStateError) as raised:
        validate_draft_context(candidate, plan(), analysis(), company_research())
    assert raised.value.code == "INVALID_REFERENCE"


@pytest.mark.parametrize(
    ("claim_id", "paragraph_id", "end", "expected"),
    [
        ("missing", "p1", 5, "INVALID_REFERENCE"),
        ("c1", "missing", 5, "INVALID_REFERENCE"),
        ("c1", "p1", 901, "INVALID_RANGE"),
    ],
)
def test_evaluation_rejects_unknown_anchor_or_stale_span(
    claim_id: str,
    paragraph_id: str,
    end: int,
    expected: str,
) -> None:
    # Given
    payload = evaluation().model_dump()
    payload["criteria"][0]["passed"] = False
    payload["issues"] = [
        {
            "id": "i1",
            "criterion_id": "contract_evidence",
            "claim_ids": [claim_id],
            "paragraph_ids": [paragraph_id],
            "start": 0,
            "end": end,
            "reason": "Invalid wording.",
            "scope": "wording",
            "instruction": "Repair the identified span.",
            "missing_fields": [],
        }
    ]
    candidate = Evaluation.model_validate(payload)
    # When / Then
    with pytest.raises(FlowStateError) as raised:
        validate_evaluation_context(candidate, draft(), plan())
    assert raised.value.code == expected


def test_model_pass_cannot_override_failed_code_length_check() -> None:
    # Given
    payload = draft().model_dump()
    payload["draft"] = "실행했다."
    payload["paragraphs"][0]["end"] = 5
    short_draft = DraftEnvelope.model_validate(payload)
    request_id = uuid4()
    binding = bind_evaluation(request_id, evaluation(), short_draft, plan())
    # When / Then
    with pytest.raises(FlowStateError) as raised:
        require_ready_evaluation(binding, request_id, short_draft, plan())
    assert raised.value.code == "INVALID_LENGTH"


def test_issue_claim_anchor_must_overlap_the_named_claim() -> None:
    # Given
    payload = evaluation().model_dump()
    payload["criteria"][0]["passed"] = False
    payload["issues"] = [
        {
            "id": "i1",
            "criterion_id": "contract_evidence",
            "claim_ids": ["c1"],
            "paragraph_ids": ["p1"],
            "start": 100,
            "end": 110,
            "reason": "Wrong claim range.",
            "scope": "wording",
            "instruction": "Repair this claim.",
            "missing_fields": [],
        }
    ]
    candidate = Evaluation.model_validate(payload)
    # When / Then
    with pytest.raises(FlowStateError) as raised:
        validate_evaluation_context(candidate, draft(), plan())
    assert raised.value.code == "INVALID_RANGE"


@pytest.mark.anyio
async def test_revision_exhaustion_uses_separate_control_error() -> None:
    # Given
    budget = ExecutionBudget()
    _ = await budget.reserve_revision("D")
    # When / Then
    with pytest.raises(RevisionReservationError) as raised:
        _ = await budget.reserve_revision("I")
    assert raised.value.code == "REVISION_EXHAUSTED"
    assert budget.snapshot().revision_count == 1


@pytest.mark.parametrize(
    ("code", "response_code"),
    [
        ("LIMIT_EXCEEDED", "BUDGET_EXCEEDED"),
        ("DEADLINE_EXCEEDED", "TIMEOUT"),
        ("CANCELLED", "CANCELLED"),
    ],
)
def test_research_retains_existing_execution_budget_error_mapping(
    code: Literal["LIMIT_EXCEEDED", "DEADLINE_EXCEEDED", "CANCELLED"],
    response_code: str,
) -> None:
    # Given
    error = ExecutionBudgetError(code)
    request_id = uuid4()
    # When
    response = error_response(error, request_id)
    # Then
    assert response.code == response_code
    assert response.request_id == request_id
