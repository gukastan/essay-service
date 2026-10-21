"""Length handoff and explicit future-intent boundaries."""

import pytest

from agent.budget import ExecutionBudget
from agent.contracts import DraftEnvelope
from agent.nodes.write import WriteNode
from tests.test_writing_nodes import ControlledProvider, generated, require_plan, writing_state


@pytest.mark.anyio
@pytest.mark.parametrize("length", [800, 801, 1000, 1001])
async def test_writer_preserves_length_boundary_for_f_without_padding(length: int) -> None:
    # Given: synthetic characters test counting only, not prose quality.
    budget = ExecutionBudget()
    state = writing_state(budget)
    draft = generated(require_plan(state))
    data = draft.model_dump()
    extra = length - len(draft.draft)
    replacements: dict[str, str] = {}
    for index, claim in enumerate(draft.claim_map[-2:]):
        addition = extra // 2 if index == 0 else extra - extra // 2
        replacements[claim.id] = claim.text[:-1] + "가" * addition + "."
    data["draft"] = draft.draft
    for claim in draft.claim_map:
        if claim.id in replacements:
            data["draft"] = data["draft"].replace(claim.text, replacements[claim.id])
    data["claim_map"] = tuple(
        claim.model_copy(update={"text": replacements.get(claim.id, claim.text)})
        for claim in draft.claim_map
    )
    data["paragraphs"][-1]["end"] = length
    response = DraftEnvelope.model_validate(data)
    # When
    result = await WriteNode(ControlledProvider(response)).run(state, budget)
    # Then
    assert result.get("draft") == response.draft
    assert len(response.draft) == length
    assert result.get("evaluation") is None


@pytest.mark.anyio
async def test_explicit_future_achievement_is_not_treated_as_past_fact() -> None:
    # Given
    budget = ExecutionBudget()
    state = writing_state(budget)
    original = generated(require_plan(state))
    future = original.claim_map[-1]
    replacement = "입사 후 목표를 달성하겠습니다."
    data = original.model_dump()
    data["draft"] = original.draft.replace(future.text, replacement)
    data["claim_map"] = (*original.claim_map[:-1], future.model_copy(update={"text": replacement}))
    data["paragraphs"][-1]["end"] = len(data["draft"])
    response = DraftEnvelope.model_validate(data)
    # When
    result = await WriteNode(ControlledProvider(response)).run(state, budget)
    # Then
    assert result.get("draft_envelope") == response
