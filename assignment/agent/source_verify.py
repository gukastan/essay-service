"""Admit exact fetched quotations using explicit company identity anchors."""
# Exhaustiveness guard remains intentional when current variants are all covered.
# pyright: reportUnnecessaryComparison=false

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final, assert_never
from uuid import uuid4

from agent.budget import ExecutionBudget
from agent.contracts import (
    CompanyFact,
    JobRequirement,
    OfficialSource,
    ResearchInput,
    ResearchResult,
    Source,
    UserProvidedSource,
)
from agent.source_admission import (
    admitted_job,
    check_references,
    instruction_like,
    posting_identity,
    section_excerpt,
)
from agent.source_conflicts import disputed_ids
from agent.source_http import PageReader
from agent.source_page import MAX_PAGE_TEXT, FetchedPage, PageReadError
from agent.source_trust import CompanyAnchor, contains, trusted_url

MAX_DIRECT_READS: Final = 3


@dataclass(frozen=True, slots=True)
class SourceVerifier:
    reader: PageReader
    anchor: CompanyAnchor | None

    async def verify(
        self, candidate: ResearchResult, input: ResearchInput, budget: ExecutionBudget
    ) -> ResearchResult:
        check_references(candidate)
        admitted, issues, job_sources, section_ids = await self._sources(candidate, input, budget)
        facts: list[CompanyFact] = []
        jobs: list[JobRequirement] = []
        for fact in candidate.company_facts:
            text = " ".join(fact.text.split())
            refs = tuple(
                source.id
                for source in admitted
                if source.id in fact.source_ids
                and source.kind == "official"
                and text in source.excerpt
                and not instruction_like(fact.text)
            )
            if refs:
                facts.append(CompanyFact(id=fact.id, text=text, source_ids=refs))
        job_evidence = tuple(
            source
            for source in admitted
            if source.kind == "user_provided" or source.id in job_sources
        )
        for job in candidate.job_requirements:
            verified = admitted_job(job, job_evidence, input, self.anchor, frozenset(section_ids))
            if verified is not None:
                jobs.append(verified)
        supplied_identity = bool(
            input.job_posting_text
            and contains(input.job_posting_text, input.company)
            and contains(input.job_posting_text, input.role)
        )
        company = (
            self.anchor.company if self.anchor else input.company if supplied_identity else None
        )
        conflicts = tuple(
            gap
            for gap in candidate.gaps
            if not gap.casefold().startswith(("no conflict", "no contradict", "상충 없음"))
            and any(
                marker in gap.casefold()
                for marker in ("conflict", "contradict", "ambiguous", "상충", "모호", "불일치")
            )
        )
        identity_mismatch = candidate.resolved_company is not None and (
            candidate.resolved_company.casefold()
            not in {alias.casefold() for alias in self.anchor.aliases}
            if self.anchor
            else candidate.resolved_company.casefold() != input.company.casefold()
        )
        disputed_facts = disputed_ids(facts)
        facts = [fact for fact in facts if fact.id not in disputed_facts]
        if conflicts or identity_mismatch or disputed_ids(jobs):
            jobs = []
            issues.append("CONFLICTING_EVIDENCE")
        provenance = tuple(
            source.id for source in admitted if source.title == "공식 채용 연결 근거"
        )
        if provenance:
            jobs = [
                job.model_copy(update={"source_ids": (*job.source_ids, *provenance)})
                for job in jobs
            ]
        used = {ref for item in (*facts, *jobs) for ref in item.source_ids}
        return ResearchResult(
            resolved_company=company,
            sources=tuple(source for source in admitted if source.id in used),
            company_facts=tuple(facts),
            job_requirements=tuple(jobs),
            gaps=tuple(issues),
        )

    async def _sources(
        self, candidate: ResearchResult, input: ResearchInput, budget: ExecutionBudget
    ) -> tuple[list[Source], list[str], set[str], set[str]]:
        admitted: list[Source] = []
        job_sources: set[str] = set()
        section_ids: set[str] = set()
        pages: dict[str, FetchedPage] = {}
        issues: list[str] = []
        if input.job_posting_text and not instruction_like(input.job_posting_text):
            admitted.append(
                UserProvidedSource(
                    id="user-posting",
                    kind="user_provided",
                    title="사용자 제공 공고 본문",
                    checked_at=datetime.now(UTC),
                    url=input.job_posting_url,
                    excerpt=input.job_posting_text,
                )
            )
        ordered = sorted(
            candidate.sources,
            key=lambda source: (
                not any(source.id in job.source_ids for job in candidate.job_requirements),
                source.id,
            ),
        )
        for source in ordered:
            match source:
                case UserProvidedSource():
                    continue
                case OfficialSource():
                    if self.anchor is None or budget.snapshot().page_reads >= MAX_DIRECT_READS:
                        continue
                    try:
                        page = await self._official(source.url, pages, budget)
                    except PageReadError as error:
                        if error.code in {"NETWORK_ERROR", "TIMEOUT"}:
                            raise
                        issues.append(error.code)
                        continue
                    job_sources.update(
                        (source.id,) if posting_identity(page, input, self.anchor) else ()
                    )
                    section = (
                        section_excerpt(page, candidate, source)
                        if source.id in job_sources
                        else None
                    )
                    section_ids.update((source.id,) if section else ())
                    excerpt = section or " ".join(source.excerpt.split())
                    if excerpt in page.text and not instruction_like(excerpt):
                        admitted.append(
                            OfficialSource(
                                id=source.id,
                                kind="official",
                                title=self.anchor.company,
                                url=page.url,
                                checked_at=page.checked_at,
                                excerpt=excerpt,
                            )
                        )
                case unreachable:
                    assert_never(unreachable)
        if (
            self.anchor
            and self.anchor.provenance_url in pages
            and any(
                source.kind == "official"
                and source.url
                and not trusted_url(source.url, self.anchor)
                for source in admitted
            )
        ):
            root = pages[self.anchor.provenance_url]
            admitted.append(
                OfficialSource(
                    id=str(uuid4()),
                    kind="official",
                    title="공식 채용 연결 근거",
                    url=root.url,
                    checked_at=root.checked_at,
                    excerpt=root.text,
                )
            )
        return admitted, issues, job_sources, section_ids

    async def _official(
        self, url: str, pages: dict[str, FetchedPage], budget: ExecutionBudget
    ) -> FetchedPage:
        anchor = self.anchor
        if anchor is None:
            raise PageReadError("UNSAFE_URL")
        if url in pages:
            return pages[url]
        if trusted_url(url, anchor):
            page = await self.reader.read(url, budget)
            if not trusted_url(page.url, anchor):
                raise PageReadError("UNSAFE_URL")
        else:
            root = pages.get(anchor.provenance_url)
            if root is None:
                root = await self.reader.read(anchor.provenance_url, budget)
                if not trusted_url(root.url, anchor):
                    raise PageReadError("UNSAFE_URL")
                pages[anchor.provenance_url] = root
            if url not in root.links:
                raise PageReadError("UNSAFE_URL")
            page = await self.reader.read(url, budget)
            if page.url != url:
                raise PageReadError("UNSAFE_URL")
        if sum(len(item.text) for item in pages.values()) + len(page.text) > MAX_PAGE_TEXT:
            raise PageReadError("TOO_LARGE")
        pages[url] = page
        return page
