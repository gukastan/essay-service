import pytest

from agent.budget import ExecutionBudget
from agent.contracts import ResearchInput
from agent.source_verify import SourceVerifier
from tests.research_fixture import ANCHOR, JOB, MemoryPages, candidate, fetched, source


@pytest.mark.anyio
async def test_official_whitespace_only_variation_returns_canonical_fetched_quote() -> None:
    # Given
    quoted = "Engineer requirements:\n\texperience building reliable systems."
    report = candidate(source(excerpt=quoted), text=quoted)
    # When
    result = await SourceVerifier(MemoryPages((fetched(),)), ANCHOR).verify(
        report, ResearchInput(company="Acme", role="Engineer"), ExecutionBudget()
    )
    # Then
    assert result.sources[0].excerpt == JOB
    assert result.job_requirements[0].text == JOB


@pytest.mark.anyio
@pytest.mark.parametrize(
    "quoted",
    [
        "Engineer requirements: 안정적인 시스템 구축 경험.",
        "Engineer **requirements**: experience building reliable systems.",
        "Engineer requirements: Experience building reliable systems.",
        "Engineer requirements: experience building secure systems.",
    ],
)
async def test_nonwhitespace_quote_changes_are_rejected(quoted: str) -> None:
    # Given
    report = candidate(source(excerpt=quoted), text=quoted)
    # When
    result = await SourceVerifier(MemoryPages((fetched(),)), ANCHOR).verify(
        report, ResearchInput(company="Acme", role="Engineer"), ExecutionBudget()
    )
    # Then
    assert result.sources == ()
    assert result.job_requirements == ()


@pytest.mark.anyio
async def test_user_posting_and_job_quote_preserve_original_internal_whitespace() -> None:
    # Given
    quoted = "Engineer requirements:\n\texperience building reliable systems."
    supplied = f"Acme\n{quoted}"
    request = ResearchInput(company="Acme", role="Engineer", job_posting_text=supplied)
    # When
    result = await SourceVerifier(MemoryPages(()), None).verify(
        candidate(source(excerpt=quoted), text=quoted), request, ExecutionBudget()
    )
    # Then
    assert result.sources[0].excerpt == supplied
    assert result.job_requirements[0].text == quoted
