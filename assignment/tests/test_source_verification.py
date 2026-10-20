"""Official source identity and exact provenance independent of model assertions."""

import pytest

from agent.budget import ExecutionBudget
from agent.contracts import CompanyFact, JobRequirement, ResearchInput
from agent.mcp_client import MCPError
from agent.source_page import extract_page
from agent.source_verify import SourceVerifier
from tests.research_fixture import (
    ANCHOR,
    CHECKED,
    JOB,
    URL,
    MemoryPages,
    candidate,
    fetched,
    source,
)


@pytest.mark.anyio
async def test_official_evidence_uses_fetched_identity_quote_and_time_not_model_claims() -> None:
    # Given
    verifier = SourceVerifier(MemoryPages((fetched(),)), ANCHOR)
    # When
    result = await verifier.verify(
        candidate(), ResearchInput(company="Acme", role="Engineer"), ExecutionBudget()
    )
    # Then
    assert result.resolved_company == "Acme"
    assert len(result.job_requirements) == 1
    assert result.sources[0].url == URL
    assert result.sources[0].excerpt == JOB
    assert result.sources[0].checked_at == CHECKED
    assert result.sources[0].published_at is None
    assert result.sources[0].closing_at is None
    assert result.company_facts == ()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "host", ["acme.example.evil.test", "jobs.acme.example", "same-name.example"]
)
async def test_model_official_label_name_and_https_do_not_create_trust(host: str) -> None:
    # Given
    url = f"https://{host}/jobs/1"
    verifier = SourceVerifier(MemoryPages((fetched(url), fetched(ANCHOR.provenance_url))), ANCHOR)
    # When
    result = await verifier.verify(
        candidate(source(url)), ResearchInput(company="Acme", role="Engineer"), ExecutionBudget()
    )
    # Then
    assert result.sources == ()
    assert result.job_requirements == ()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "text",
    [
        "Engineer requirements: imaginary certification.",
        "Engineer requirements: Experience building reliable systems.",
    ],
)
async def test_fabricated_or_changed_quote_cannot_become_job_evidence(text: str) -> None:
    # Given
    verifier = SourceVerifier(MemoryPages((fetched(),)), ANCHOR)
    # When
    result = await verifier.verify(
        candidate(text=text), ResearchInput(company="Acme", role="Engineer"), ExecutionBudget()
    )
    # Then
    assert result.job_requirements == ()


@pytest.mark.anyio
async def test_role_elsewhere_on_page_does_not_promote_company_values_to_job_requirement() -> None:
    # Given
    values = "We value responsibility and integrity."
    verifier = SourceVerifier(MemoryPages((fetched(text=f"Engineer {values}"),)), ANCHOR)
    # When
    result = await verifier.verify(
        candidate(source(excerpt=values), text=values),
        ResearchInput(company="Acme", role="Engineer"),
        ExecutionBudget(),
    )
    # Then
    assert result.job_requirements == ()


@pytest.mark.anyio
@pytest.mark.parametrize("linked", [True, False])
async def test_external_ats_requires_exact_official_link_not_shared_host(*, linked: bool) -> None:
    # Given
    url = "https://jobs.ats.example/acme/123"
    wrong = "https://jobs.ats.example/other-company/123"
    root = fetched(
        ANCHOR.provenance_url,
        text=f"Acme careers: {url if linked else wrong}",
        links=(url if linked else wrong,),
    )
    verifier = SourceVerifier(MemoryPages((root, fetched(url))), ANCHOR)
    # When
    result = await verifier.verify(
        candidate(source(url)), ResearchInput(company="Acme", role="Engineer"), ExecutionBudget()
    )
    # Then
    assert bool(result.job_requirements) is linked
    if linked:
        assert {item.url for item in result.sources} == {url, ANCHOR.provenance_url}
        assert set(result.job_requirements[0].source_ids) == {item.id for item in result.sources}
    else:
        assert result.sources == ()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "problem", ["duplicate-source", "duplicate-record", "unknown-id", "reserved-id"]
)
async def test_invalid_evidence_ids_fail_closed(problem: str) -> None:
    # Given
    original = candidate()
    changes = {
        "duplicate-source": {"sources": (source(), source())},
        "duplicate-record": {
            "company_facts": (CompanyFact(id="j1", text=JOB, source_ids=("s1",)),)
        },
        "unknown-id": {
            "job_requirements": (JobRequirement(id="j1", text=JOB, source_ids=("missing",)),)
        },
        "reserved-id": {"sources": (source(id="user-posting"),)},
    }
    invalid = original.model_copy(update=changes[problem])
    verifier = SourceVerifier(MemoryPages((fetched(),)), ANCHOR)
    # When
    with pytest.raises(MCPError) as raised:
        _ = await verifier.verify(
            invalid, ResearchInput(company="Acme", role="Engineer"), ExecutionBudget()
        )
    # Then
    assert raised.value.code == "INVALID_RESPONSE"


@pytest.mark.anyio
async def test_reported_critical_conflict_suppresses_even_exact_evidence() -> None:
    # Given
    disputed = candidate().model_copy(update={"gaps": ("Conflicting core job requirements",)})
    verifier = SourceVerifier(MemoryPages((fetched(),)), ANCHOR)
    # When
    result = await verifier.verify(
        disputed, ResearchInput(company="Acme", role="Engineer"), ExecutionBudget()
    )
    # Then
    assert result.job_requirements == ()
    assert "CONFLICTING_EVIDENCE" in result.gaps


@pytest.mark.anyio
async def test_aggregate_page_text_cannot_reenter_via_cached_overflow_page() -> None:
    # Given: two sources share oversized second page, the second must not bypass aggregate cap.
    second = "https://acme.example/jobs/2"
    pages = MemoryPages((fetched(text="a" * 7000), fetched(second, text=JOB + "b" * 7000)))
    report = candidate(source(excerpt="a"), source(second, id="s2"), source(second, id="s3"))
    report = report.model_copy(
        update={
            "job_requirements": (JobRequirement(id="j1", text=JOB, source_ids=("s1", "s2", "s3")),)
        }
    )
    # When
    result = await SourceVerifier(pages, ANCHOR).verify(
        report, ResearchInput(company="Acme", role="Engineer"), ExecutionBudget()
    )
    # Then
    assert sum(len(item.text) for item in pages.pages) > 12000
    assert result.job_requirements == ()


@pytest.mark.anyio
async def test_incidental_role_and_requirements_in_official_blog_are_not_hiring_evidence() -> None:
    # Given
    url = "https://acme.example/blog/interview-with-engineer"
    verifier = SourceVerifier(MemoryPages((fetched(url),)), ANCHOR)
    # When
    result = await verifier.verify(
        candidate(source(url)), ResearchInput(company="Acme", role="Engineer"), ExecutionBudget()
    )
    # Then
    assert result.job_requirements == ()


@pytest.mark.anyio
async def test_role_heading_in_explicit_nonvacancy_culture_page_is_not_job_evidence() -> None:
    # Given
    url = "https://acme.example/careers/engineer-culture"
    text = "Engineer qualifications are discussed in our culture blog; this is not a vacancy."
    page = extract_page(url, f"<h1>Engineer culture</h1><p>{text}</p>".encode(), CHECKED)
    report = candidate(source(url, excerpt=text), text=text)
    # When
    result = await SourceVerifier(MemoryPages((page,)), ANCHOR).verify(
        report, ResearchInput(company="Acme", role="Engineer"), ExecutionBudget()
    )
    # Then
    assert result.job_requirements == ()
