from typing import ClassVar, Literal, final
from uuid import UUID

import pytest
from pydantic import BaseModel, ConfigDict

from agent.budget import ExecutionBudget
from agent.contracts import DraftRequest, ResearchInput, ResearchResult
from agent.mcp_client import MCPClient
from agent.research import ResearchReport
from agent.source_http import PageReader
from agent.source_page import FetchedPage
from agent.source_verify import SourceVerifier


class SourceDiagnostic(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)
    id: str
    kind: str
    url: str | None
    excerpt_prefix: str


class CandidateDiagnostic(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)
    event: Literal["candidate"] = "candidate"
    resolved_company: str | None
    gaps: tuple[str, ...]
    sources: tuple[SourceDiagnostic, ...]
    job_quotes: tuple[str, ...]
    tool_calls_reported: int
    input_tokens: int | None
    output_tokens: int | None


class PageDiagnostic(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)
    event: Literal["page"] = "page"
    url: str
    text_codepoints: int
    posting_titles: tuple[str, ...]
    posting_employers: tuple[str | None, ...]


class VerificationDiagnostic(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)
    event: Literal["verification"] = "verification"
    resolved_company: str | None
    gaps: tuple[str, ...]
    admitted_job_count: int


Diagnostic = CandidateDiagnostic | PageDiagnostic | VerificationDiagnostic


@final
class ResearchCapture:
    """Mutable accumulator of sanitized public-fixture boundary observations."""

    def __init__(self, reader: PageReader) -> None:
        self.reader = reader
        self.events: list[Diagnostic] = []

    async def read(self, url: str, budget: ExecutionBudget) -> FetchedPage:
        page = await self.reader.read(url, budget)
        self.events.append(
            PageDiagnostic(
                url=page.url,
                text_codepoints=len(page.text),
                posting_titles=tuple(posting.title for posting in page.postings),
                posting_employers=tuple(
                    posting.employer.name if posting.employer else None for posting in page.postings
                ),
            )
        )
        return page

    def instrument(self, monkeypatch: pytest.MonkeyPatch, mcp: MCPClient) -> None:
        research = mcp.research
        verify = SourceVerifier.verify

        async def record_candidate(
            request: ResearchInput | DraftRequest, budget: ExecutionBudget, request_id: UUID
        ) -> ResearchReport:
            report = await research(request, budget, request_id)
            self.events.append(
                CandidateDiagnostic(
                    resolved_company=report.result.resolved_company,
                    gaps=report.result.gaps,
                    sources=tuple(
                        SourceDiagnostic(
                            id=source.id,
                            kind=source.kind,
                            url=source.url,
                            excerpt_prefix=source.excerpt[:240],
                        )
                        for source in report.result.sources
                    ),
                    job_quotes=tuple(job.text[:240] for job in report.result.job_requirements),
                    tool_calls_reported=report.tool_calls_reported,
                    input_tokens=report.usage.input_tokens if report.usage else None,
                    output_tokens=report.usage.output_tokens if report.usage else None,
                )
            )
            return report

        async def record_verification(
            verifier: SourceVerifier,
            candidate: ResearchResult,
            request: ResearchInput,
            budget: ExecutionBudget,
        ) -> ResearchResult:
            result = await verify(verifier, candidate, request, budget)
            self.events.append(
                VerificationDiagnostic(
                    resolved_company=result.resolved_company,
                    gaps=result.gaps,
                    admitted_job_count=len(result.job_requirements),
                )
            )
            return result

        monkeypatch.setattr(mcp, "research", record_candidate)
        monkeypatch.setattr(SourceVerifier, "verify", record_verification)
