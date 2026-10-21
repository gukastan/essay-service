"""Immutable role reservation policy."""

from typing import Final, Literal

ModelRole = Literal["research", "analysis", "writer", "review"]
ROLE_OUTPUT_TOKENS: Final[dict[ModelRole, int]] = {
    "research": 3000,
    "analysis": 3000,
    "writer": 4000,
    "review": 3000,
}
ROLE_CALL_LIMITS: Final[dict[ModelRole, int]] = {
    "research": 1,
    "analysis": 1,
    "writer": 2,
    "review": 2,
}

MAX_MODEL_CALLS: Final = 6
MAX_OUTPUT_TOKENS: Final = 20000
MAX_NATIVE_TOOL_CALLS: Final = 2
