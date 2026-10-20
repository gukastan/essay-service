# Keep exhaustive match assertions when test-case literals expand.
# pyright: reportUnnecessaryComparison=false
from typing import Literal, assert_never

import pytest
from pydantic import JsonValue, ValidationError

from agent.contracts import (
    DraftEnvelope,
    Evaluation,
    EvaluationIssue,
    FlowAnalysisResult,
    WritingPlan,
)
from tests.flow_fixture import analysis, draft, evaluation, plan


def test_flow_roundtrip_and_frozen_contracts() -> None:
    for value in (analysis(), plan(), draft(), evaluation()):
        assert type(value).model_validate_json(value.model_dump_json(by_alias=True)) == value
        with pytest.raises(ValidationError, match="frozen_instance"):
            value.__setattr__("injected", 1)
    assert evaluation().all_passed


@pytest.mark.parametrize("version", [True, 0, 3, "1"])
def test_plan_version_is_strict_and_bounded(version: JsonValue) -> None:
    body = plan().model_dump()
    body["version"] = version
    with pytest.raises(ValidationError):
        _ = WritingPlan.model_validate(body)


@pytest.mark.parametrize("mutation", ["duplicate", "unknown", "order", "allocation"])
def test_plan_rejects_broken_local_links(
    mutation: Literal["duplicate", "unknown", "order", "allocation"],
) -> None:
    body = plan().model_dump()
    match mutation:
        case "duplicate":
            body["selected_evidence_ids"] = ["e1", "e1"]
        case "unknown":
            body["selected_evidence_ids"] = ["unknown"]
        case "order":
            body["paragraphs"][0]["order"] = 2
        case "allocation":
            body["paragraphs"][0]["target_characters"] = 800
        case unreachable:
            assert_never(unreachable)
    with pytest.raises(ValidationError):
        _ = WritingPlan.model_validate(body)


def test_analysis_rejects_dangling_candidate() -> None:
    body = analysis().model_dump()
    body["experience_evidence"] = []
    with pytest.raises(ValidationError, match="candidate"):
        _ = FlowAnalysisResult.model_validate(body)


@pytest.mark.parametrize(("start", "end"), [(1, 900), (0, 901), (900, 900)])
def test_draft_span_bounds_and_coverage(start: int, end: int) -> None:
    body = draft().model_dump()
    body["paragraphs"] = [{"paragraph_id": "p1", "start": start, "end": end}]
    with pytest.raises(ValidationError):
        _ = DraftEnvelope.model_validate(body)


@pytest.mark.parametrize("mutation", ["empty", "duplicate", "omitted", "failure_without_issue"])
def test_evaluation_never_infers_pass(
    mutation: Literal["empty", "duplicate", "omitted", "failure_without_issue"],
) -> None:
    body = evaluation().model_dump()
    match mutation:
        case "empty":
            body["criteria"] = []
        case "duplicate":
            body["criteria"] = [body["criteria"][0]] * 7
        case "omitted":
            body["criteria"] = body["criteria"][:-1]
        case "failure_without_issue":
            body["criteria"][0]["passed"] = False
        case unreachable:
            assert_never(unreachable)
    with pytest.raises(ValidationError):
        _ = Evaluation.model_validate(body)


def test_wording_requires_anchored_span_and_missing_info_requires_fields() -> None:
    for scope in ("wording", "missing_info", "invented"):
        with pytest.raises(ValidationError):
            _ = EvaluationIssue.model_validate(
                {
                    "id": "i1",
                    "criterionId": "length",
                    "claimIds": [],
                    "paragraphIds": [],
                    "start": None,
                    "end": None,
                    "reason": "짧음",
                    "scope": scope,
                    "instruction": "수정",
                    "missingFields": [],
                }
            )
