"""Deterministic candidate admission rules; source text never becomes instructions."""

# Retain explicit exhaustiveness guards for future source variants.
# pyright: reportUnnecessaryComparison=false
import re
from typing import assert_never
from urllib.parse import urlsplit

from agent.contracts import (
    JobRequirement,
    OfficialSource,
    ResearchInput,
    ResearchResult,
    Source,
    UserProvidedSource,
)
from agent.mcp_client import MCPError
from agent.source_page import FetchedPage
from agent.source_trust import CompanyAnchor, contains, trusted_url


def check_references(result: ResearchResult) -> None:
    sources = {source.id for source in result.sources}
    records = (*result.company_facts, *result.job_requirements)
    ids = [source.id for source in result.sources] + [record.id for record in records]
    if (
        len(ids) != len(set(ids))
        or "user-posting" in ids
        or any(ref not in sources for record in records for ref in record.source_ids)
    ):
        raise MCPError("INVALID_RESPONSE")


def instruction_like(text: str) -> bool:
    return any(
        marker in text.casefold()
        for marker in (
            "ignore previous",
            "ignore all",
            "system prompt",
            "developer message",
            "이전 지시",
            "시스템 프롬프트",
            "지시를 무시",
        )
    )


def job_supported(
    source: Source, job: JobRequirement, input: ResearchInput, anchor: CompanyAnchor | None
) -> bool:
    if (
        instruction_like(job.text)
        or not contains(job.text, input.role)
        or job.text not in source.excerpt
    ):
        return False
    if not any(
        marker in job.text.casefold()
        for marker in (
            "requirements",
            "required skills",
            "what you'll do",
            "you may be a good fit",
            "responsibilities",
            "qualifications",
            "자격",
            "요건",
            "담당",
        )
    ):
        return False
    match source:
        case OfficialSource():
            career_path = any(
                part in urlsplit(source.url).path.casefold().split("/")
                for part in ("jobs", "job", "채용", "rcrt")
            )
            role_path = (
                input.role.casefold().replace(" ", "-") in urlsplit(source.url).path.casefold()
            )
            career_path = career_path or (
                role_path and "careers" in urlsplit(source.url).path.split("/")
            )
            external_link = anchor is not None and not trusted_url(source.url, anchor)
            return source.id in job.source_ids and (career_path or external_link)
        case UserProvidedSource():
            return contains(source.excerpt, input.company)
        case unreachable:
            assert_never(unreachable)


def posting_identity(page: FetchedPage, input: ResearchInput, anchor: CompanyAnchor) -> bool:
    if len(page.postings) != 1:
        return False
    posting = page.postings[0]
    employer_matches = not anchor.require_employer or (
        posting.employer is not None
        and posting.employer.name.casefold() in {alias.casefold() for alias in anchor.aliases}
    )
    return employer_matches and contains(posting.title, input.role)


def admitted_job(
    job: JobRequirement,
    sources: tuple[Source, ...],
    input: ResearchInput,
    anchor: CompanyAnchor | None,
    section_ids: frozenset[str],
) -> JobRequirement | None:
    """Prefer exact supplied text; only official page quotations normalize whitespace."""
    user_refs = tuple(
        source.id
        for source in sources
        if source.kind == "user_provided"
        and (job_supported(source, job, input, anchor) or user_line_support(source, job, input))
    )
    if user_refs:
        return JobRequirement(id=job.id, text=job.text, source_ids=user_refs)
    rendered = job.model_copy(update={"text": " ".join(job.text.split())})
    refs = tuple(
        source.id
        for source in sources
        if source.kind == "official"
        and (
            (
                source.id in section_ids
                and source.id in job.source_ids
                and rendered.text in source.excerpt
                and not instruction_like(rendered.text)
            )
            or job_supported(source, rendered, input, anchor)
        )
    )
    return JobRequirement(id=job.id, text=rendered.text, source_ids=refs) if refs else None


def section_excerpt(
    page: FetchedPage, candidate: ResearchResult, source: OfficialSource
) -> str | None:
    """Use one fetched section only when an associated literal requirement occurs inside it."""
    if len(page.postings) != 1:
        return None
    title = " ".join(page.postings[0].title.split())
    for section in page.requirement_sections:
        if section.posting_title != title or instruction_like(section.text):
            continue
        if any(
            source.id in job.source_ids and " ".join(job.text.split()) in section.text
            for job in candidate.job_requirements
        ):
            return section.text
    return None


def user_line_support(
    source: UserProvidedSource, job: JobRequirement, input: ResearchInput
) -> bool:
    """Bind a raw quote to an explicit role/requirements heading on its original LF line."""
    if instruction_like(job.text) or not contains(source.excerpt, input.company):
        return False
    heading = re.compile(
        r"(?<!\w)"
        + re.escape(input.role)
        + r"\s+(?:requirements|qualifications|responsibilities|자격요건|담당업무|요건)"
        + r"\s*[:\uff1a]\s*",
        re.IGNORECASE,
    )
    for line in source.excerpt.split("\n"):
        context = heading.search(line)
        if context and job.text == line[context.end() :]:
            return True
    return False
