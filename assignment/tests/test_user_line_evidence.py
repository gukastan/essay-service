import pytest

from agent.budget import ExecutionBudget
from agent.contracts import ResearchInput
from agent.source_verify import SourceVerifier
from tests.research_fixture import MemoryPages, candidate


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("posting_lines", "quote", "accepted"),
    [
        (
            "Software Engineer requirements: experience writing Python tests.",
            "experience writing Python tests.",
            True,
        ),
        (
            "Software Engineer requirements:\nexperience writing Python tests.",
            "experience writing Python tests.",
            False,
        ),
        (
            "Software Engineer values: experience writing Python tests.",
            "experience writing Python tests.",
            False,
        ),
        (
            "Software Engineer requirements: experience writing Python tests.",
            "Experience writing Python tests.",
            False,
        ),
        (
            (
                "Software Engineer requirements: build products.\n"
                "Designer requirements: experience writing Python tests."
            ),
            "experience writing Python tests.",
            False,
        ),
        (
            "Software Engineer requirements: experience  writing Python tests.",
            "experience  writing Python tests.",
            True,
        ),
        (
            "Software Engineer requirements: No experience writing Python tests.",
            "experience writing Python tests.",
            False,
        ),
        (
            "Software Engineer requirements: experience writing Python tests is optional.",
            "experience writing Python tests",
            False,
        ),
    ],
)
async def test_partial_user_quote_requires_same_line_role_and_requirement_context(
    posting_lines: str, quote: str, *, accepted: bool
) -> None:
    # Given
    supplied = f"Example Fixture Company\n{posting_lines}"
    request = ResearchInput(
        company="Example Fixture Company", role="Software Engineer", job_posting_text=supplied
    )
    report = candidate(text=quote).model_copy(
        update={"resolved_company": "Example Fixture Company"}
    )
    # When
    result = await SourceVerifier(MemoryPages(()), None).verify(report, request, ExecutionBudget())
    # Then
    assert bool(result.job_requirements) is accepted
    if accepted:
        assert result.job_requirements[0].text == quote
        assert result.sources[0].excerpt == supplied
        assert result.job_requirements[0].source_ids == ("user-posting",)
