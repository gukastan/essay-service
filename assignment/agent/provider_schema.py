"""Translate Pydantic domain schemas into strict Responses wire schemas."""

# Keep an explicit exhaustive assertion for future JSON variants.
# pyright: reportUnnecessaryComparison=false
from typing import Final, assert_never

from openai.types.responses import ResponseFormatTextJSONSchemaConfigParam
from pydantic import BaseModel, JsonValue, TypeAdapter

from agent.providers import ProviderError

JSON: Final = TypeAdapter(JsonValue)


def strict_schema(schema: type[BaseModel]) -> dict[str, JsonValue]:
    """All object fields are required; nullable domain fields retain their null branch."""
    parsed = JSON.validate_python(schema.model_json_schema(by_alias=True))
    converted = _convert(parsed)
    if not isinstance(converted, dict):
        raise ProviderError("INVALID_RESPONSE")
    return converted


def _convert(value: JsonValue) -> JsonValue:
    match value:
        case dict():
            result = {
                ("anyOf" if key == "oneOf" else key): _convert(item)
                for key, item in value.items()
                if key not in {"default", "discriminator"}
            }
            properties = result.get("properties")
            if isinstance(properties, dict):
                result["required"] = list(properties)
                result["additionalProperties"] = False
            return result
        case list():
            return [_convert(item) for item in value]
        case str() | int() | float() | None:
            return value
        case unreachable:
            assert_never(unreachable)


def response_format(schema: type[BaseModel], name: str) -> ResponseFormatTextJSONSchemaConfigParam:
    """Bridge the SDK invariant dictionary type without widening domain values."""
    return {
        "type": "json_schema",
        "name": name,
        "strict": True,
        "schema": dict(strict_schema(schema).items()),
    }
