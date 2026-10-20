from agent.contracts import (
    MANDATORY_CRITERIA,
    CriterionResult,
    DraftEnvelope,
    Evaluation,
    ExperienceEvidence,
    FlowAnalysisResult,
    FlowRequirement,
    ParagraphSpan,
    PlanClaim,
    PlanParagraph,
    ResearchResult,
    WritingPlan,
)


def analysis() -> FlowAnalysisResult:
    return FlowAnalysisResult(
        requirements=(
            FlowRequirement(
                id="r1",
                text="경험",
                mandatory=True,
                check_condition="경험을 설명",
                candidate_evidence_ids=("e1",),
            ),
        ),
        experience_evidence=(
            ExperienceEvidence(
                id="e1",
                quote="실행했다.",
                start=0,
                end=5,
                category="action",
            ),
        ),
        gaps=(),
    )


def research() -> ResearchResult:
    return ResearchResult(
        resolved_company="회사",
        sources=(),
        company_facts=(),
        job_requirements=(),
        gaps=(),
    )


def plan() -> WritingPlan:
    return WritingPlan(
        version=1,
        selected_evidence_ids=("e1",),
        claims=(PlanClaim(id="c1", text="실행했다.", kind="user_fact", evidence_ids=("e1",)),),
        paragraphs=(
            PlanParagraph(
                id="p1",
                purpose="경험 설명",
                order=1,
                target_characters=900,
                requirement_ids=("r1",),
                claim_ids=("c1",),
            ),
        ),
    )


def draft() -> DraftEnvelope:
    text = "실행했다." + "가" * 895
    return DraftEnvelope(
        version=1,
        plan_version=1,
        draft=text,
        paragraphs=(ParagraphSpan(paragraph_id="p1", start=0, end=len(text)),),
        claim_map=plan().claims,
        fit_reasons=(),
    )


def evaluation() -> Evaluation:
    return Evaluation(
        draft_version=1,
        plan_version=1,
        criteria=tuple(
            CriterionResult(criterion_id=item, passed=True) for item in MANDATORY_CRITERIA
        ),
        issues=(),
    )
