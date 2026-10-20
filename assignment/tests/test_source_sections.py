from dataclasses import replace

import pytest

from agent.budget import ExecutionBudget
from agent.contracts import ResearchInput, ResearchResult
from agent.source_page import FetchedPage
from agent.source_trust import DEFAULT_ANCHORS
from agent.source_verify import SourceVerifier
from tests.naver_section_fixture import (
    MODEL_METADATA,
    NAVER_URL,
    QUOTE,
    ROLE,
    card,
    naver_page,
    section,
)
from tests.research_fixture import CHECKED, MemoryPages, candidate, source


async def verify_section(page: FetchedPage, quote: str = QUOTE) -> ResearchResult:
    report = candidate(source(NAVER_URL, excerpt=MODEL_METADATA), text=quote).model_copy(
        update={"resolved_company": "NAVER"}
    )
    anchor = next(anchor for anchor in DEFAULT_ANCHORS if anchor.company == "NAVER")
    return await SourceVerifier(MemoryPages((page,)), anchor).verify(
        report, ResearchInput(company="네이버", role=ROLE), ExecutionBudget()
    )


@pytest.mark.anyio
@pytest.mark.parametrize("heading", ["Required Skills", "What You'll Do"])
async def test_exact_bullet_in_bound_posting_section_uses_fetched_section(heading: str) -> None:
    # Given
    page = naver_page(card(section("Who We Are", "회사 소개") + section(heading, QUOTE)))
    # When
    result = await verify_section(page)
    # Then
    assert len(result.job_requirements) == 1
    assert result.job_requirements[0].text == QUOTE
    assert result.job_requirements[0].source_ids == (result.sources[0].id,)
    assert QUOTE in result.sources[0].excerpt
    assert result.sources[0].excerpt in page.text
    assert MODEL_METADATA not in result.sources[0].excerpt
    assert result.sources[0].checked_at == CHECKED


@pytest.mark.anyio
@pytest.mark.parametrize("heading", ["Who We Are", "Our Values", "Culture"])
async def test_culture_and_values_sections_do_not_become_job_requirements(heading: str) -> None:
    # Given
    page = naver_page(card(section(heading, QUOTE)))
    # When
    result = await verify_section(page)
    # Then
    assert result.job_requirements == ()


@pytest.mark.anyio
async def test_requirement_heading_outside_posting_card_cannot_authorize_quote() -> None:
    # Given
    page = naver_page(
        card(section("Who We Are", "회사 소개"))
        + f"<footer>{section('Required Skills', QUOTE)}</footer>"
    )
    # When
    result = await verify_section(page)
    # Then
    assert result.job_requirements == ()


@pytest.mark.anyio
async def test_card_title_must_match_verified_structured_posting() -> None:
    # Given
    page = naver_page(card(section("Required Skills", QUOTE), title="다른 운영 직무"))
    # When
    result = await verify_section(page)
    # Then
    assert result.job_requirements == ()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "quote",
    [
        "고객·파트너사, 유관부서와의 원활한 커뮤니케이션이 불가능하신 분",
        "**고객·파트너사**, 유관부서와의 원활한 커뮤니케이션이 가능하신 분",
        "Ability to communicate with customers, partners and related departments.",
    ],
)
async def test_section_fallback_still_rejects_changed_or_translated_quote(quote: str) -> None:
    # Given
    page = naver_page(card(section("Required Skills", QUOTE)))
    # When
    result = await verify_section(page, quote)
    # Then
    assert result.job_requirements == ()


@pytest.mark.anyio
async def test_quote_cannot_stitch_text_from_two_requirement_sections() -> None:
    # Given
    page = naver_page(
        card(section("Required Skills", "고객·파트너사,") + section("What You'll Do", QUOTE[9:]))
    )
    # When
    result = await verify_section(page)
    # Then
    assert result.job_requirements == ()


@pytest.mark.anyio
async def test_explicit_section_does_not_override_affiliate_employer() -> None:
    # Given
    page = naver_page(card(section("Required Skills", QUOTE)), employer="NAVER Cloud")
    # When
    result = await verify_section(page)
    # Then
    assert result.job_requirements == ()


@pytest.mark.anyio
async def test_explicit_section_does_not_override_multiple_postings() -> None:
    # Given
    page = naver_page(card(section("Required Skills", QUOTE)))
    page = replace(page, postings=(*page.postings, *page.postings))
    # When
    result = await verify_section(page)
    # Then
    assert result.job_requirements == ()
