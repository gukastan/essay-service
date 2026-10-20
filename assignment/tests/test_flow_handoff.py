"""Synthetic typed examples for ESSAY-11/12/13/15; no generated essay or business node."""

from dataclasses import dataclass
from typing import Literal
from uuid import UUID

import pytest
from pydantic import ValidationError

from agent.contracts import (
    Claim,
    DraftEnvelope,
    DraftResponse,
    ErrorResponse,
    Evaluation,
    Evidence,
    FlowAnalysisResult,
    NeedsInputResponse,
    ReadyResponse,
    Usage,
    WritingPlan,
)
from agent.flow_state import bind_evaluation, require_ready_evaluation
from tests.flow_fixture import analysis, draft, evaluation, plan


@dataclass(frozen=True, slots=True)
class FlowExample:
    analysis: FlowAnalysisResult
    plan: WritingPlan
    draft: DraftEnvelope
    evaluation: Evaluation


def flow_example() -> FlowExample:
    return FlowExample(analysis(), plan(), draft(), evaluation())


def ready_fixture() -> ReadyResponse:
    example = flow_example()
    return ReadyResponse(
        status="ready",
        request_id=UUID("5e7fd874-1d5a-4540-9cf4-37f9e842823d"),
        draft=example.draft.draft,
        character_count=len(example.draft.draft),
        sources=(),
        evidence=Evidence(
            company_facts=(),
            job_requirements=(),
            experience_evidence=example.analysis.experience_evidence,
            claim_map=tuple(
                Claim(id=item.id, text=item.text, kind=item.kind, evidence_ids=item.evidence_ids)
                for item in example.draft.claim_map
            ),
            fit_reasons=example.draft.fit_reasons,
        ),
        review_summary="생성 당시 검토 통과",
        usage=Usage(model_calls=4, revision_count=0),
    )


def needs_input_fixture() -> NeedsInputResponse:
    return NeedsInputResponse(
        status="needs_input",
        request_id=UUID("5e7fd874-1d5a-4540-9cf4-37f9e842823d"),
        message="Describe a concrete action.",
        missing_fields=("experience",),
        questions=("What action did you personally take?",),
        reason_code="EXPERIENCE_INSUFFICIENT",
    )


def quality_failure_fixture(
    code: Literal["QUALITY_CHECK_FAILED", "LENGTH_VALIDATION_FAILED"] = "QUALITY_CHECK_FAILED",
) -> ErrorResponse:
    return ErrorResponse(
        status="error",
        request_id=UUID("5e7fd874-1d5a-4540-9cf4-37f9e842823d"),
        message="The generation did not meet the required checks.",
        code=code,
    )


def test_typed_stage_fixture_can_bind_a_reviewed_ready_response() -> None:
    # Given
    example = flow_example()
    response = ready_fixture()
    binding = bind_evaluation(
        response.request_id,
        example.evaluation,
        example.draft,
        example.plan,
    )
    # When
    require_ready_evaluation(binding, response.request_id, example.draft, example.plan)
    # Then
    assert DraftResponse.validate_json(response.model_dump_json(by_alias=True)) == response
    assert response.evidence.experience_evidence[0].id == "e1"
    assert response.usage.model_calls == 4


def test_sentence_revision_fixture_uses_new_draft_and_evaluation_versions() -> None:
    # Given
    example = flow_example()
    revised = DraftEnvelope.model_validate({**example.draft.model_dump(), "version": 2})
    reviewed = Evaluation.model_validate(
        {
            **example.evaluation.model_dump(),
            "draft_version": 2,
        }
    )
    request_id = ready_fixture().request_id
    binding = bind_evaluation(request_id, reviewed, revised, example.plan)
    # When
    require_ready_evaluation(binding, request_id, revised, example.plan)
    # Then
    assert revised.plan_version == 1
    assert reviewed.draft_version == 2


def test_missing_input_fixture_preserves_existing_wire_fields() -> None:
    # Given
    response = needs_input_fixture()
    # When
    parsed = DraftResponse.validate_json(response.model_dump_json(by_alias=True))
    # Then
    assert isinstance(parsed, NeedsInputResponse)
    assert parsed.missing_fields == ("experience",)
    assert parsed.reason_code == "EXPERIENCE_INSUFFICIENT"


@pytest.mark.parametrize("code", ["QUALITY_CHECK_FAILED", "LENGTH_VALIDATION_FAILED"])
def test_quality_failure_fixture_does_not_request_invented_information(
    code: Literal["QUALITY_CHECK_FAILED", "LENGTH_VALIDATION_FAILED"],
) -> None:
    # Given
    response = quality_failure_fixture(code)
    # When
    parsed = DraftResponse.validate_json(response.model_dump_json(by_alias=True))
    # Then
    assert isinstance(parsed, ErrorResponse)
    assert parsed.code == code
    assert set(parsed.model_dump(by_alias=True)) == {"status", "requestId", "message", "code"}


def test_quality_failure_cannot_be_disguised_as_missing_information() -> None:
    # Given
    payload = needs_input_fixture().model_dump(by_alias=True)
    payload["reasonCode"] = "QUALITY_CHECK_FAILED"
    # When / Then
    with pytest.raises(ValidationError):
        _ = DraftResponse.validate_python(payload)


def test_quality_failure_cannot_add_missing_fields() -> None:
    # Given
    payload = quality_failure_fixture().model_dump(by_alias=True)
    payload["missingFields"] = ["experience"]
    # When / Then
    with pytest.raises(ValidationError):
        _ = DraftResponse.validate_python(payload)
