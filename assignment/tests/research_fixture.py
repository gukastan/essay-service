"""Finite independent company evidence fixtures; no external calls or paid model."""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final

from agent.budget import ExecutionBudget, OperationContext
from agent.contracts import JobRequirement, OfficialSource, ResearchResult
from agent.source_page import FetchedPage, PageReadError
from agent.source_structured import Posting
from agent.source_trust import CompanyAnchor

CHECKED: Final = datetime(2026, 10, 20, tzinfo=UTC)
CLAIMED: Final = datetime(2099, 1, 1, tzinfo=UTC)
JOB: Final = "Engineer requirements: experience building reliable systems."
URL: Final = "https://acme.example/jobs/1"
ANCHOR: Final = CompanyAnchor("Acme", ("Acme",), ("acme.example",), "https://acme.example/careers")


def source(url: str = URL, *, excerpt: str = JOB, id: str = "s1") -> OfficialSource:
    return OfficialSource(
        id=id,
        kind="official",
        title="MODEL SAYS OFFICIAL",
        url=url,
        checked_at=CLAIMED,
        published_at="2099-01-01",
        closing_at="2099-12-31",
        excerpt=excerpt,
    )


def candidate(*sources: OfficialSource, text: str = JOB) -> ResearchResult:
    selected = sources or (source(),)
    return ResearchResult(
        resolved_company="Acme",
        sources=selected,
        company_facts=(),
        job_requirements=(JobRequirement(id="j1", text=text, source_ids=(selected[0].id,)),),
        gaps=(),
    )


@dataclass(frozen=True, slots=True)
class MemoryPages:
    pages: tuple[FetchedPage, ...]

    async def read(self, url: str, budget: ExecutionBudget) -> FetchedPage:
        async def fetch(_context: OperationContext) -> FetchedPage:
            for page in self.pages:
                if page.url == url:
                    return page
            raise PageReadError("ACCESS_DENIED")

        return await budget.run("page", fetch)


def fetched(url: str = URL, *, text: str = JOB, links: tuple[str, ...] = ()) -> FetchedPage:
    return FetchedPage(
        url,
        text,
        links,
        CHECKED,
        postings=(Posting.model_validate({"@type": "JobPosting", "title": "Engineer"}),),
    )
