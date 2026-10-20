"""Conservative conflict checks for explicit negation and changed numeric requirements."""

import re
from collections.abc import Sequence

from agent.contracts import CompanyFact, JobRequirement


def disputed_ids(records: Sequence[CompanyFact | JobRequirement]) -> frozenset[str]:
    """Block identical claim frames with differing numbers or polarity, not infer semantics."""
    frames: dict[str, list[tuple[str, str]]] = {}
    for record in records:
        normalized = " ".join(record.text.casefold().split())
        frame = re.sub(r"\b(?:not|never|no)\s+", "", normalized)
        frame = re.sub(r"\d+(?:\.\d+)?", "#", frame)
        frames.setdefault(frame, []).append((record.id, normalized))
    return frozenset(
        identifier
        for group in frames.values()
        if len({text for _, text in group}) > 1
        for identifier, _ in group
    )
