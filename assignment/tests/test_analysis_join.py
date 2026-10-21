from datetime import UTC, datetime
from uuid import uuid4

import pytest

from agent.contracts import ErrorResponse, JobRequirement, ResearchResult, UserProvidedSource
from agent.flow_state import FlowStateError
from agent.nodes.analysis_evidence import AnalysisJoin, EvidenceBundle
from agent.nodes.analyze import AnalysisSuccess, experience_gap
from agent.nodes.research import ResearchSuccess
from tests.test_personal_analysis import analysis, request


def research() -> ResearchSuccess:
    return ResearchSuccess(
        result=ResearchResult(
            resolved_company="회사",
            sources=(
                UserProvidedSource(
                    id="s1",
                    kind="user_provided",
                    title="시험 공고",
                    checked_at=datetime.now(UTC),
                    excerpt="회사 개발: 점검 수행",
                ),
            ),
            company_facts=(),
            job_requirements=(JobRequirement(id="j1", text="점검 수행", source_ids=("s1",)),),
            gaps=("VALUES_MISSING",),
        ),
        tool_calls_reported=0,
        usage=None,
    )


def test_analysis_join_requires_both_branches_and_keeps_sources_separate() -> None:
    source = request()
    personal = AnalysisSuccess(result=analysis(source), usage=None)
    company = research()
    join = AnalysisJoin(source, uuid4())
    assert join.run(None, company) is None
    assert join.run(personal, None) is None
    result = join.run(personal, company)
    assert isinstance(result, EvidenceBundle)
    assert result.analysis == personal.result
    assert result.research == company.result
    assert result.research.company_facts == ()


@pytest.mark.parametrize("missing", ["company", "job"])
def test_analysis_join_core_gaps_stop(missing: str) -> None:
    source = request()
    company = research()
    changes = {"resolved_company": None} if missing == "company" else {"job_requirements": ()}
    company = company.model_copy(update={"result": company.result.model_copy(update=changes)})
    result = AnalysisJoin(source, uuid4()).run(
        AnalysisSuccess(result=analysis(source), usage=None), company
    )
    assert result is not None
    assert not isinstance(result, EvidenceBundle)
    assert result.status == "needs_input"


@pytest.mark.parametrize(("identifier", "source_id"), [("e1", "s1"), ("j1", "absent")])
def test_analysis_join_rejects_collisions_and_missing_sources(
    identifier: str, source_id: str
) -> None:
    source = request()
    company = research()
    result = company.result.model_copy(
        update={
            "job_requirements": (
                JobRequirement(id=identifier, text="점검", source_ids=(source_id,)),
            )
        }
    )
    with pytest.raises(FlowStateError, match="INVALID_REFERENCE"):
        _ = AnalysisJoin(source, uuid4()).run(
            AnalysisSuccess(result=analysis(source), usage=None),
            company.model_copy(update={"result": result}),
        )


def test_analysis_join_propagates_early_terminal() -> None:
    source = request()
    request_id = uuid4()
    join = AnalysisJoin(source, request_id)
    gap = experience_gap(
        analysis(source).model_copy(update={"gaps": ("맡은 역할은 무엇인가요?",)}), request_id
    )
    assert gap is not None
    assert join.run(gap, None) == gap
    error = ErrorResponse(status="error", request_id=request_id, message="실패", code="TIMEOUT")
    assert join.run(None, error) == error
