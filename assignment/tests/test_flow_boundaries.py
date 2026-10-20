"""Independent malformed handoffs; fixtures are not implemented business nodes."""

import json
import sys

import anyio
import pytest
from pydantic import ValidationError

from agent.contracts import DraftEnvelope, FlowAnalysisResult, FlowRequirement, WritingPlan
from tests.flow_fixture import draft, plan


@pytest.mark.parametrize("identifier", ["", " \n", "x" * 81])
def test_requirement_rejects_invalid_identifier(identifier: str) -> None:
    # Given / When / Then
    with pytest.raises(ValidationError):
        _ = FlowRequirement(
            id=identifier,
            text="Describe the action.",
            mandatory=True,
            check_condition="The action is present.",
            candidate_evidence_ids=(),
        )


@pytest.mark.parametrize("candidate_ids", [("unknown",), ("e1", "e1")])
def test_analysis_rejects_unknown_or_duplicate_candidates(
    candidate_ids: tuple[str, ...],
) -> None:
    # Given
    payload = {
        "requirements": [
            {
                "id": "r1",
                "text": "Describe an action.",
                "mandatory": True,
                "checkCondition": "The action is present.",
                "candidateEvidenceIds": candidate_ids,
            }
        ],
        "experienceEvidence": [
            {
                "id": "e1",
                "quote": "I tested it.",
                "start": 0,
                "end": 12,
                "category": "action",
            }
        ],
        "gaps": [],
    }
    # When / Then
    with pytest.raises(ValidationError):
        _ = FlowAnalysisResult.model_validate(payload)


@pytest.mark.parametrize("collection", ["claims", "paragraphs", "selected_evidence_ids"])
def test_plan_rejects_duplicate_identifiers(collection: str) -> None:
    # Given
    payload = plan().model_dump()
    payload[collection] = [payload[collection][0], payload[collection][0]]
    # When / Then
    with pytest.raises(ValidationError):
        _ = WritingPlan.model_validate(payload)


def test_plan_rejects_unknown_paragraph_claim() -> None:
    # Given
    payload = plan().model_dump()
    payload["paragraphs"][0]["claim_ids"] = ["missing-claim"]
    # When / Then
    with pytest.raises(ValidationError):
        _ = WritingPlan.model_validate(payload)


def test_plan_rejects_claim_using_unselected_evidence() -> None:
    # Given
    payload = plan().model_dump()
    payload["claims"][0]["evidence_ids"] = ["unselected-evidence"]
    # When / Then
    with pytest.raises(ValidationError):
        _ = WritingPlan.model_validate(payload)


@pytest.mark.parametrize("allocation", [800, 1001])
def test_plan_rejects_impossible_total_length(allocation: int) -> None:
    # Given
    payload = plan().model_dump()
    payload["paragraphs"][0]["target_characters"] = allocation
    # When / Then
    with pytest.raises(ValidationError):
        _ = WritingPlan.model_validate(payload)


@pytest.mark.parametrize("version", [0, 3, True, "1"])
def test_plan_rejects_invalid_or_coerced_version(version: int | str) -> None:
    # Given
    payload = plan().model_dump()
    payload["version"] = version
    # When / Then
    with pytest.raises(ValidationError):
        _ = WritingPlan.model_validate(payload)


@pytest.mark.parametrize("start", [-1, 1, True])
def test_draft_rejects_invalid_span_start(start: int) -> None:
    # Given
    payload = draft().model_dump()
    payload["paragraphs"][0]["start"] = start
    # When / Then
    with pytest.raises(ValidationError):
        _ = DraftEnvelope.model_validate(payload)


def test_draft_rejects_end_past_actual_text() -> None:
    # Given
    payload = draft().model_dump()
    payload["paragraphs"][-1]["end"] = len(draft().draft) + 1
    # When / Then
    with pytest.raises(ValidationError):
        _ = DraftEnvelope.model_validate(payload)


def test_draft_rejects_claim_absent_from_text() -> None:
    # Given
    payload = draft().model_dump()
    payload["claim_map"][0]["text"] = "A fabricated sentence absent from this fixture."
    # When / Then
    with pytest.raises(ValidationError):
        _ = DraftEnvelope.model_validate(payload)


@pytest.mark.anyio
@pytest.mark.parametrize("route", ["H", "J", "", None, 1, ["D"]])
async def test_untyped_invalid_revision_route_preserves_the_shared_opportunity(
    route: str | int | list[str] | None,
) -> None:
    # Given
    invocation = """
import anyio
import json
import sys
from agent.budget import ExecutionBudget, RevisionReservationError

async def probe():
    budget = ExecutionBudget()
    try:
        await budget.reserve_revision(json.loads(sys.argv[1]))
    except RevisionReservationError as error:
        assert error.code == "INVALID_REVISION_ROUTE"
    else:
        raise AssertionError("Invalid route accepted")
    assert budget.snapshot().revision_count == 0
    assert budget.snapshot().revision_route is None
    reservation = await budget.reserve_revision("I")
    assert reservation.route == "I"
    assert reservation.revision_count == 1
    assert budget.snapshot().model_calls == 0
    print("invalid-route-rejected;valid-I-reserved")

anyio.run(probe)
"""
    # When
    with anyio.fail_after(10):
        completed = await anyio.run_process(
            [sys.executable, "-c", invocation, json.dumps(route)],
            check=False,
        )
    # Then
    assert completed.returncode == 0, completed.stderr.decode()
    assert completed.stdout.strip() == b"invalid-route-rejected;valid-I-reserved"
