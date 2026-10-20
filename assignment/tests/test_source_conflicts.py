import pytest

from agent.budget import ExecutionBudget
from agent.contracts import CompanyFact, JobRequirement, ResearchInput
from agent.source_verify import SourceVerifier
from tests.research_fixture import ANCHOR, JOB, MemoryPages, candidate, fetched, source


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("first", "second"),
    [
        (
            "Engineer requirements: 3 years experience.",
            "Engineer requirements: 5 years experience.",
        ),
        (
            "Engineer requirements: travel is required.",
            "Engineer requirements: travel is not required.",
        ),
    ],
)
async def test_conflicting_core_requirements_fail_closed_without_model_gap(
    first: str, second: str
) -> None:
    # Given
    text = f"{first} {second}"
    report = candidate(source(excerpt=text)).model_copy(
        update={
            "job_requirements": (
                JobRequirement(id="j1", text=first, source_ids=("s1",)),
                JobRequirement(id="j2", text=second, source_ids=("s1",)),
            )
        }
    )
    # When
    result = await SourceVerifier(MemoryPages((fetched(text=text),)), ANCHOR).verify(
        report, ResearchInput(company="Acme", role="Engineer"), ExecutionBudget()
    )
    # Then
    assert result.job_requirements == ()
    assert "CONFLICTING_EVIDENCE" in result.gaps


@pytest.mark.anyio
async def test_optional_conflicting_facts_are_dropped_while_agreeing_job_survives() -> None:
    # Given
    text = f"{JOB} Acme has 10 offices. Acme has 20 offices."
    report = candidate(source(excerpt=text)).model_copy(
        update={
            "company_facts": (
                CompanyFact(id="f1", text="Acme has 10 offices.", source_ids=("s1",)),
                CompanyFact(id="f2", text="Acme has 20 offices.", source_ids=("s1",)),
            )
        }
    )
    # When
    result = await SourceVerifier(MemoryPages((fetched(text=text),)), ANCHOR).verify(
        report, ResearchInput(company="Acme", role="Engineer"), ExecutionBudget()
    )
    # Then
    assert result.company_facts == ()
    assert len(result.job_requirements) == 1
