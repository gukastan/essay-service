"""Validate the SDK's permissively constructed response before using its fields."""

from typing import Annotated, ClassVar, Literal

from openai.types.responses import Response, ResponseOutputItem
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from agent.providers import ProviderError


class WireUsage(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    input_tokens: Annotated[int, Field(strict=True, ge=0)]
    output_tokens: Annotated[int, Field(strict=True, ge=0)]


class ResponseEnvelope(BaseModel):
    """Only fields consumed by our adapters; SDK output variants are revalidated."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    status: Literal["completed", "failed", "in_progress", "cancelled", "queued", "incomplete"]
    output: tuple[ResponseOutputItem, ...]
    usage: WireUsage | None = None


def validate_response(response: Response) -> ResponseEnvelope:
    """No SDK coercion, serializer warnings or raw validation errors escape this seam."""
    try:
        return ResponseEnvelope.model_validate(response.model_dump(warnings=False))
    except ValidationError:
        raise ProviderError("INVALID_RESPONSE") from None
