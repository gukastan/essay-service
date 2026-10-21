# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["anyio", "pydantic"]
# ///
# How to run: from assignment/, PYTHONPATH=. .venv/bin/python ../.omo/evidence/writing/replay.py
"""Replay synthetic role contracts only; no external model or graph execution."""

import json
from dataclasses import asdict
from pathlib import Path

import anyio

from agent.budget import ExecutionBudget
from agent.nodes.revise import RevisionNode, RevisionPatches
from agent.nodes.write import WriteNode
from tests.test_writing_nodes import (
    ControlledProvider, evaluated, generated, require_plan, writing_state,
)


async def main() -> None:
    budget = ExecutionBudget()
    state = writing_state(budget)
    plan = require_plan(state)
    result = await WriteNode(ControlledProvider(generated(plan))).run(state, budget)
    state.update(result)
    patch = evaluated(state)
    reservation = await budget.reserve_revision("I")
    revised = await RevisionNode(ControlledProvider(RevisionPatches(
        draft_version=1, plan_version=1, patches=(patch,),
    ))).run(state, budget, reservation)
    initial_draft, final_draft = result.get("draft_envelope"), revised.get("draft_envelope")
    assert initial_draft is not None and final_draft is not None
    artifact = {
        "scope": "synthetic role replay; controlled provider; no full graph or live model",
        "plan": plan.model_dump(mode="json", by_alias=True),
        "initial": initial_draft.model_dump(mode="json", by_alias=True),
        "revised": final_draft.model_dump(mode="json", by_alias=True),
        "budget": asdict(budget.snapshot()),
        "evaluationInvalidated": revised.get("evaluation") is None,
        "outsideRangePreserved": final_draft.draft == (
            initial_draft.draft[:patch.start] + patch.text + initial_draft.draft[patch.end:]
        ),
    }
    path = Path("../.omo/evidence/writing/role-replay.json")
    path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n")
    print(f"PASS: {path}; versions 1 -> 2; writer calls=2; revision count=1")


anyio.run(main)
