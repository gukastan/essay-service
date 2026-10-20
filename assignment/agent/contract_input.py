"""Public input parsing and Unicode code-point boundaries."""

from functools import partial
from typing import Annotated, ClassVar
from urllib.parse import urlsplit

from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, Field, JsonValue
from pydantic.alias_generators import to_camel
from pydantic_core import PydanticCustomError


def normalize_text(value: str) -> str:
    """Normalize line endings without changing user wording or whitespace."""
    return value.replace("\r\n", "\n").replace("\r", "\n")


def count_characters(value: str) -> int:
    return len(normalize_text(value))


def nonblank(value: str) -> str:
    if not value.strip():
        raise PydanticCustomError("blank_text", "Text must not be blank")
    return value


def http_url(value: str) -> str:
    try:
        parsed = urlsplit(value)
        valid = parsed.scheme in {"http", "https"} and bool(parsed.hostname)
        _ = parsed.port
        valid = valid and parsed.username is None and parsed.password is None
    except ValueError:
        valid = False
    if not valid or any(char.isspace() for char in value):
        raise PydanticCustomError("http_url", "A valid HTTP(S) URL is required")
    return value


def optional_text(value: JsonValue) -> JsonValue:
    return None if isinstance(value, str) and not value.strip() else value


Text = Annotated[str, AfterValidator(nonblank)]
NormalizedText = Annotated[str, AfterValidator(normalize_text), AfterValidator(nonblank)]
HttpUrl = Annotated[str, Field(max_length=2048), AfterValidator(http_url)]


def bounded(value: str, limit: int) -> str:
    if len(value) > limit:
        raise PydanticCustomError("text_length", "Text exceeds code-point limit")
    return value


Company = Annotated[NormalizedText, AfterValidator(partial(bounded, limit=120))]
Role = Annotated[NormalizedText, AfterValidator(partial(bounded, limit=160))]


class Contract(BaseModel):
    """Frozen boundary values with camelCase JSON and strict unknown-field rejection."""

    model_config: ClassVar[ConfigDict] = ConfigDict(
        frozen=True,
        extra="forbid",
        alias_generator=to_camel,
        populate_by_name=True,
    )


def optional_bounded(value: str | None) -> str | None:
    return bounded(value, 16000) if value is not None else None


class ResearchInput(Contract):
    company: Company
    role: Role
    job_posting_url: Annotated[HttpUrl | None, BeforeValidator(optional_text)] = None
    job_posting_text: Annotated[
        NormalizedText | None,
        BeforeValidator(optional_text),
        AfterValidator(optional_bounded),
    ] = None


class DraftRequest(ResearchInput):
    question: Annotated[NormalizedText, AfterValidator(partial(bounded, limit=3000))]
    experience: Annotated[NormalizedText, AfterValidator(partial(bounded, limit=12000))]

    def research_input(self) -> ResearchInput:
        """Project only public company/job information into the research boundary."""
        return ResearchInput(
            company=self.company,
            role=self.role,
            job_posting_url=self.job_posting_url,
            job_posting_text=self.job_posting_text,
        )
