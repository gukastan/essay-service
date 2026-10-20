"""Typed model boundary for future role nodes; no role business prompts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Protocol, final

from pydantic import BaseModel

if TYPE_CHECKING:
    from agent.budget import ExecutionBudget
from agent.limits import ROLE_OUTPUT_TOKENS as ROLE_OUTPUT_TOKENS
from agent.limits import ModelRole as ModelRole


@dataclass(frozen=True, slots=True)
class StructuredModelRequest[T: BaseModel]:
    role: ModelRole
    instructions: str
    input: str
    schema: type[T]


@dataclass(frozen=True, slots=True)
class TokenUsage:
    input_tokens: int
    output_tokens: int


@dataclass(frozen=True, slots=True)
class ModelResult[T: BaseModel]:
    value: T
    usage: TokenUsage | None


class ModelProvider(Protocol):
    async def generate[T: BaseModel](
        self,
        request: StructuredModelRequest[T],
        budget: ExecutionBudget,
    ) -> ModelResult[T]: ...


@final
class ProviderError(Exception):
    """Sanitized failure: never includes response bodies, input or SDK text."""

    def __init__(
        self,
        code: Literal[
            "CONFIG_ERROR",
            "MODEL_ERROR",
            "INVALID_RESPONSE",
            "REFUSAL",
            "INCOMPLETE",
            "TIMEOUT",
        ],
    ) -> None:
        self.code = code
        super().__init__(code)
