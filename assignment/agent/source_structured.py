"""Read explicit JobPosting identity data without executing page scripts."""
# Exhaustiveness guards retained for the recursive JSON union.
# pyright: reportUnnecessaryComparison=false

from typing import ClassVar, Literal, assert_never

from pydantic import BaseModel, ConfigDict, Field, JsonValue, TypeAdapter, ValidationError


class Employer(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)
    name: str


class Posting(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)
    kind: Literal["JobPosting"] = Field(alias="@type")
    title: str
    employer: Employer | None = Field(default=None, alias="hiringOrganization")


def postings(raw: str) -> tuple[Posting, ...]:
    try:
        value = TypeAdapter(JsonValue).validate_json(raw)
    except ValidationError:
        return ()
    pending = [value]
    found: list[Posting] = []
    while pending:
        item = pending.pop()
        match item:
            case dict():
                if item.get("@type") == "JobPosting":
                    try:
                        found.append(Posting.model_validate(item))
                    except ValidationError:
                        continue
                pending.extend(item.values())
            case list():
                pending.extend(item)
            case str() | int() | float() | None:
                continue
            case unreachable:
                assert_never(unreachable)
    return tuple(found)
