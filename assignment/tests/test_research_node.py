"""Research node via real stdio MCP, real SDK, synthetic local HTTP answers."""

from dataclasses import replace
from uuid import uuid4

import httpx
import pytest

from agent.budget import ExecutionBudget
from agent.contracts import DraftRequest, ResearchInput
from agent.mcp_client import MCPClient
from agent.nodes.research import ResearchNode
from agent.source_http import SafePageReader
from tests.naver_section_fixture import (
    MODEL_METADATA,
    NAVER_URL,
    QUOTE,
    ROLE,
    card,
    naver_page,
    section,
)
from tests.research_fixture import ANCHOR, JOB, MemoryPages, candidate, fetched, source
from tests.research_live_capture import ResearchCapture
from tests.test_mcp import wire_client
from tests.test_source_http import page, public_dns
from tests.wire_fixture import JSON, HttpReply, response_body, serve_wire


@pytest.mark.anyio
async def test_real_mcp_node_verifies_source_with_single_reserved_sdk_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given
    budget = ExecutionBudget()
    observed: list[tuple[int, int]] = []
    page_requests: list[httpx.Request] = []

    def model_answer(_payload: bytes) -> HttpReply:
        counters = budget.snapshot()
        observed.append((counters.model_calls, counters.native_tool_calls_reserved))
        return HttpReply(response_body(candidate().model_dump_json(by_alias=True), search=True))

    def website(request: httpx.Request) -> httpx.Response:
        page_requests.append(request)
        return page(
            (
                '<script type="application/ld+json">'
                '{"@type":"JobPosting","title":"Engineer"}</script>'
                f"<h1>Acme Engineer</h1><p>{JOB}</p>"
            ).encode()
        )

    request = DraftRequest(
        company="Acme",
        role="Engineer",
        question="PRIVATE_QUESTION_10",
        experience="PRIVATE_EXPERIENCE_10",
    )
    reader = SafePageReader(resolver=public_dns, transport=httpx.MockTransport(website))
    capture = ResearchCapture(reader)
    with serve_wire(model_answer) as wire:
        async with MCPClient(wire_client(wire.base_url)) as mcp:
            capture.instrument(monkeypatch, mcp)
            # When
            outcome = await ResearchNode(mcp, capture, (ANCHOR,)).run(request, budget, uuid4())
        # Then
        assert outcome.status == "research-success"
        assert outcome.result.job_requirements[0].text == JOB
        assert outcome.result.sources[0].kind == "official"
        assert outcome.tool_calls_reported == 1
        assert observed == [(1, 2)]
        assert wire.requests.qsize() == 1
        payload = wire.requests.get_nowait()
        assert b"PRIVATE_QUESTION_10" not in payload
        assert b"PRIVATE_EXPERIENCE_10" not in payload
        body = JSON.validate_json(payload)
        assert isinstance(body, dict)
        assert body["max_tool_calls"] == 2
        assert body["store"] is False
        assert len(page_requests) == budget.snapshot().page_reads == 1
        assert [event.event for event in capture.events] == ["candidate", "page", "verification"]
        assert capture.events[0].event == "candidate"
        assert capture.events[0].job_quotes == (JOB,)
        assert capture.events[-1].event == "verification"
        assert capture.events[-1].gaps == ()


@pytest.mark.anyio
@pytest.mark.parametrize(
    "scenario", ["unknown", "same-name", "missing-job", "conflict", "access-denied", "malformed-id"]
)
async def test_node_returns_typed_supplement_or_error_from_real_mcp(scenario: str) -> None:
    # Given
    report = candidate()
    anchors = (ANCHOR,)
    pages = (fetched(),)
    if scenario == "unknown":
        anchors = ()
    if scenario == "same-name":
        anchors = (ANCHOR, replace(ANCHOR, company="Acme other", hosts=("other.example",)))
    if scenario == "missing-job":
        report = report.model_copy(update={"job_requirements": ()})
    if scenario == "conflict":
        report = report.model_copy(update={"gaps": ("Conflicting core role requirements",)})
    if scenario == "access-denied":
        pages = ()
    if scenario == "malformed-id":
        report = report.model_copy(update={"sources": (*report.sources, *report.sources)})
    with serve_wire(
        lambda _: HttpReply(response_body(report.model_dump_json(by_alias=True), search=True))
    ) as wire:
        async with MCPClient(wire_client(wire.base_url)) as mcp:
            # When
            outcome = await ResearchNode(mcp, MemoryPages(pages), anchors).run(
                ResearchInput(company="Acme", role="Engineer"), ExecutionBudget(), uuid4()
            )
        # Then
        if scenario == "malformed-id":
            assert outcome.status == "error"
            assert outcome.code == "INVALID_RESPONSE"
        else:
            assert outcome.status == "research-success"
            if scenario in {"unknown", "same-name", "missing-job", "conflict", "access-denied"}:
                assert outcome.result.job_requirements == ()
        assert wire.requests.qsize() == (0 if scenario in {"unknown", "same-name"} else 1)


@pytest.mark.anyio
async def test_real_mcp_node_accepts_exact_korean_bullet_with_server_section_provenance() -> None:
    # Given
    report = candidate(source(NAVER_URL, excerpt=MODEL_METADATA), text=QUOTE).model_copy(
        update={"resolved_company": "NAVER"}
    )
    reader = MemoryPages((naver_page(card(section("Required Skills", QUOTE))),))
    budget = ExecutionBudget()
    with serve_wire(
        lambda _: HttpReply(response_body(report.model_dump_json(by_alias=True), search=True))
    ) as wire:
        async with MCPClient(wire_client(wire.base_url)) as mcp:
            # When
            outcome = await ResearchNode(mcp, reader).run(
                ResearchInput(company="네이버", role=ROLE), budget, uuid4()
            )
        # Then
        assert outcome.status == "research-success"
        assert outcome.result.job_requirements[0].text == QUOTE
        assert QUOTE in outcome.result.sources[0].excerpt
        assert MODEL_METADATA not in outcome.result.sources[0].excerpt
        assert budget.snapshot().model_calls == 1
        assert budget.snapshot().native_tool_calls_reserved == 2
        assert budget.snapshot().page_reads == 1
        assert wire.requests.qsize() == 1
