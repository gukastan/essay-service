import json

import pytest

from agent.budget import ExecutionBudget
from agent.contracts import ResearchInput
from agent.source_page import extract_page
from agent.source_trust import DEFAULT_ANCHORS
from agent.source_verify import SourceVerifier
from tests.research_fixture import CHECKED, JOB, MemoryPages, candidate, source


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("company", "employer", "url", "accepted"),
    [
        ("NAVER", "NAVER", "https://recruit.navercorp.com/rcrt/view.do?annoId=42", True),
        ("네이버", "NAVER", "https://recruit.navercorp.com/rcrt/view.do?annoId=42", True),
        ("NAVER", "NAVER Cloud", "https://recruit.navercorp.com/rcrt/view.do?annoId=42", False),
        ("네이버", "NAVER WEBTOON", "https://recruit.navercorp.com/rcrt/view.do?annoId=42", False),
        ("Kakao", "Kakao", "https://careers.kakao.com/jobs/42", True),
        ("카카오", "카카오", "https://careers.kakao.com/jobs/42", True),
        ("Kakao", "Kakao Pay", "https://careers.kakao.com/jobs/42", False),
        ("카카오", "카카오뱅크", "https://careers.kakao.com/jobs/42", False),
    ],
)
async def test_shared_recruiting_host_requires_exact_posting_employer(
    company: str, employer: str, url: str, *, accepted: bool
) -> None:
    # Given: navigation contains every company and role, but JobPosting has one employer.
    posting = json.dumps(
        {
            "@type": "JobPosting",
            "title": "Engineer",
            "hiringOrganization": {"@type": "Organization", "name": employer},
        }
    )
    html = (
        "<nav>NAVER 네이버 Kakao 카카오 NAVER Cloud Kakao Pay Engineer Designer</nav>"
        f'<script type="application/ld+json">{posting}</script><h1>Engineer</h1><p>{JOB}</p>'
    )
    page = extract_page(url, html.encode(), CHECKED)
    anchors = tuple(anchor for anchor in DEFAULT_ANCHORS if company in anchor.aliases)
    assert len(anchors) == 1
    report = candidate(source(url)).model_copy(update={"resolved_company": company})
    # When
    result = await SourceVerifier(MemoryPages((page,)), anchors[0]).verify(
        report, ResearchInput(company=company, role="Engineer"), ExecutionBudget()
    )
    # Then
    assert bool(result.job_requirements) is accepted


@pytest.mark.anyio
async def test_navigation_role_cannot_override_actual_posting_title() -> None:
    # Given
    url = "https://recruit.navercorp.com/rcrt/view.do?annoId=42"
    page = extract_page(
        url,
        f"<nav>Engineer requirements {JOB}</nav><h1>N배송 운영 지원</h1>".encode(),
        CHECKED,
    )
    anchor = next(anchor for anchor in DEFAULT_ANCHORS if anchor.company == "NAVER")
    report = candidate(source(url)).model_copy(update={"resolved_company": "NAVER"})
    # When
    result = await SourceVerifier(MemoryPages((page,)), anchor).verify(
        report, ResearchInput(company="NAVER", role="Engineer"), ExecutionBudget()
    )
    # Then
    assert result.job_requirements == ()


@pytest.mark.anyio
async def test_javascript_shell_does_not_promote_model_source_excerpt() -> None:
    # Given
    url = "https://careers.kakao.com/jobs/42"
    shell = extract_page(url, b"<div>Loading</div><script>renderJob()</script>", CHECKED)
    anchor = next(anchor for anchor in DEFAULT_ANCHORS if anchor.company == "Kakao")
    report = candidate(source(url)).model_copy(update={"resolved_company": "Kakao"})
    # When
    result = await SourceVerifier(MemoryPages((shell,)), anchor).verify(
        report, ResearchInput(company="Kakao", role="Engineer"), ExecutionBudget()
    )
    # Then
    assert result.sources == ()
    assert result.job_requirements == ()


@pytest.mark.anyio
async def test_employer_and_role_cannot_be_combined_across_distinct_postings() -> None:
    # Given
    url = "https://recruit.navercorp.com/rcrt/view.do?annoId=42"
    postings = [
        {
            "@type": "JobPosting",
            "title": "Engineer",
            "hiringOrganization": {"@type": "Organization", "name": "NAVER Cloud"},
        },
        {
            "@type": "JobPosting",
            "title": "Designer",
            "hiringOrganization": {"@type": "Organization", "name": "NAVER"},
        },
    ]
    html = f'<script type="application/ld+json">{json.dumps(postings)}</script><p>{JOB}</p>'
    page = extract_page(url, html.encode(), CHECKED)
    anchor = next(anchor for anchor in DEFAULT_ANCHORS if anchor.company == "NAVER")
    report = candidate(source(url)).model_copy(update={"resolved_company": "NAVER"})
    # When
    result = await SourceVerifier(MemoryPages((page,)), anchor).verify(
        report, ResearchInput(company="NAVER", role="Engineer"), ExecutionBudget()
    )
    # Then
    assert result.job_requirements == ()
