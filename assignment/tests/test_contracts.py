"""Public JSON contract regressions, independent of role prompts."""

from typing import Final

import pytest
from pydantic import JsonValue, TypeAdapter, ValidationError

from agent.contracts import (
    Claim,
    DraftRequest,
    DraftResponse,
    ExperienceEvidence,
    ResearchInput,
    Source,
    Usage,
    count_characters,
    evidence_matches,
    normalize_text,
)

INPUT: Final = {
    "company": "회사",
    "role": "직무",
    "question": "문항",
    "experience": " 원문\r\n😀경험 ",
}
REQUEST_ID: Final = "60b490f2-3536-4b19-a89e-80808cd7cdb9"


@pytest.mark.parametrize("field", ["company", "role", "question", "experience"])
@pytest.mark.parametrize("value", [" \n", None, 123, True])
def test_required_text_rejects_blank_or_wrong_type(field: str, value: str | int | None) -> None:
    # Given / When / Then
    with pytest.raises(ValidationError):
        _ = DraftRequest.model_validate({**INPUT, field: value})


@pytest.mark.parametrize(
    ("field", "limit"),
    [
        ("company", 120),
        ("role", 160),
        ("question", 3000),
        ("experience", 12000),
        ("jobPostingText", 16000),
    ],
)
@pytest.mark.parametrize("extra", [0, 1])
def test_text_limit_counts_codepoints(field: str, limit: int, extra: int) -> None:
    # Given
    payload: dict[str, JsonValue] = {**INPUT, field: "😀" * (limit + extra)}
    # When / Then
    if extra:
        with pytest.raises(ValidationError):
            _ = DraftRequest.model_validate(payload)
    else:
        parsed = DraftRequest.model_validate(payload)
        assert parsed.model_dump(by_alias=True)[field] == "😀" * limit


def test_lf_normalization_preserves_experience_content_and_optional_absence() -> None:
    # Given / When
    parsed = DraftRequest.model_validate({**INPUT, "jobPostingUrl": "  ", "jobPostingText": "\n"})
    # Then
    assert parsed.experience == " 원문\n😀경험 "
    assert parsed.job_posting_url is None
    assert parsed.job_posting_text is None


@pytest.mark.parametrize(
    "url",
    ["file:///etc/passwd", "javascript:alert(1)", "https://", "https://example.com/" + "a" * 2048],
)
def test_url_rejects_invalid_or_oversized_values(url: str) -> None:
    # Given / When / Then
    with pytest.raises(ValidationError):
        _ = DraftRequest.model_validate({**INPUT, "jobPostingUrl": url})


@pytest.mark.parametrize("extra", ["secret", "timeoutSeconds", "maxToolCalls", "requestId"])
def test_input_rejects_untrusted_extra_fields(extra: str) -> None:
    # Given / When / Then
    with pytest.raises(ValidationError):
        _ = DraftRequest.model_validate({**INPUT, extra: "override"})


@pytest.mark.parametrize("extra", ["question", "experience", "timeoutSeconds", "maxToolCalls"])
def test_research_domain_rejects_private_input_and_budget_metadata(extra: str) -> None:
    # Given / When / Then
    with pytest.raises(ValidationError):
        _ = ResearchInput.model_validate({"company": "회사", "role": "직무", extra: "private"})


@pytest.mark.parametrize("kind", ["user_fact", "company_fact"])
def test_factual_claim_requires_evidence(kind: str) -> None:
    # Given / When / Then
    with pytest.raises(ValidationError):
        _ = Claim.model_validate({"id": "c1", "text": "성과", "kind": kind, "evidenceIds": []})


def test_official_source_requires_url_while_user_text_does_not() -> None:
    # Given
    source = {"id": "s1", "title": "공고", "checkedAt": "2026-10-20T00:00:00Z", "excerpt": "업무"}
    adapter = TypeAdapter(Source)
    # When / Then
    with pytest.raises(ValidationError):
        _ = adapter.validate_python({**source, "kind": "official"})
    assert adapter.validate_python({**source, "kind": "user_provided"}).kind == "user_provided"


@pytest.mark.parametrize(("start", "end"), [(-1, 2), (2, 2), (3, 2), (0.5, 2), (False, 2)])
def test_evidence_rejects_invalid_offsets(start: float, end: int) -> None:
    # Given / When / Then
    with pytest.raises(ValidationError):
        _ = ExperienceEvidence.model_validate(
            {"id": "e1", "quote": "경험", "start": start, "end": end, "category": "action"}
        )


def test_evidence_matches_lf_codepoints_including_emoji() -> None:
    # Given
    source = "가\r\n😀나👩‍💻끝"
    evidence = ExperienceEvidence.model_validate(
        {"id": "e1", "quote": "😀나👩‍💻", "start": 2, "end": 7, "category": "action"}
    )
    # When / Then
    assert normalize_text(source) == "가\n😀나👩‍💻끝"
    assert count_characters(source) == 8
    assert evidence_matches(source, evidence)
    assert not evidence_matches(source.replace("나", "다"), evidence)


@pytest.mark.parametrize("status", ["needs_input", "error"])
def test_nonready_response_rejects_draft_leakage(status: str) -> None:
    # Given
    payload: dict[str, JsonValue] = {
        "status": status,
        "requestId": REQUEST_ID,
        "message": "보완 필요",
    }
    if status == "needs_input":
        _ = payload.update(
            {
                "missingFields": ["experience"],
                "questions": ["어떤 경험?"],
                "reasonCode": "EXPERIENCE_INSUFFICIENT",
            }
        )
    else:
        _ = payload.update({"code": "MODEL_ERROR"})
    # When / Then
    parsed = DraftResponse.validate_python(payload)
    assert parsed.status == status
    with pytest.raises(ValidationError):
        _ = DraftResponse.validate_python({**payload, "draft": "private"})


@pytest.mark.parametrize("length", [800, 801, 1000, 1001])
@pytest.mark.parametrize("count_delta", [0, 1])
def test_ready_enforces_length_and_reported_count(length: int, count_delta: int) -> None:
    # Given
    payload: dict[str, JsonValue] = {
        "status": "ready",
        "requestId": REQUEST_ID,
        "draft": "😀" * length,
        "characterCount": length + count_delta,
        "sources": [],
        "evidence": {
            "companyFacts": [],
            "jobRequirements": [],
            "experienceEvidence": [],
            "claimMap": [],
            "fitReasons": [],
        },
        "reviewSummary": "생성 당시 검토 통과",
        "usage": {"modelCalls": 4, "revisionCount": 0},
    }
    # When / Then
    if 801 <= length <= 1000 and count_delta == 0:
        assert DraftResponse.validate_python(payload).status == "ready"
    else:
        with pytest.raises(ValidationError):
            _ = DraftResponse.validate_python(payload)


@pytest.mark.parametrize("field", ["jobPostingUrl", "jobPostingText"])
@pytest.mark.parametrize("value", [42, True, ["text"], {"text": "value"}])
def test_optional_text_nonstring_is_validation_error(
    field: str, value: int | list[str] | dict[str, str]
) -> None:
    # Given / When / Then
    with pytest.raises(ValidationError):
        _ = DraftRequest.model_validate({**INPUT, field: value})


@pytest.mark.parametrize("url", ["http://example.com:bad", "https://example.com:99999"])
def test_url_rejects_invalid_port(url: str) -> None:
    # Given / When / Then
    with pytest.raises(ValidationError):
        _ = DraftRequest.model_validate({**INPUT, "jobPostingUrl": url})


def test_evidence_rejects_slice_clamping_past_source_end() -> None:
    # Given
    evidence = ExperienceEvidence.model_validate(
        {"id": "e1", "quote": "가😀", "start": 0, "end": 99, "category": "action"}
    )
    # When / Then
    assert not evidence_matches("가😀", evidence)


@pytest.mark.parametrize("revision", [True, False, 2, -1, "1"])
def test_usage_rejects_non_integer_or_out_of_range_revision(*, revision: bool | int | str) -> None:
    # Given / When / Then
    with pytest.raises(ValidationError):
        _ = Usage.model_validate({"modelCalls": 4, "revisionCount": revision})
