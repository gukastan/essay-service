"""Server-only settings and explicit trace suppression."""

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import ClassVar

from openai import AsyncOpenAI
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        extra="ignore",
        frozen=True,
    )
    openai_api_key: SecretStr | None = None
    openai_model: str | None = None

    @property
    def model_configured(self) -> bool:
        return bool(
            self.openai_api_key
            and self.openai_api_key.get_secret_value().strip()
            and self.openai_model
            and self.openai_model.strip()
        )


def disable_tracing() -> None:
    """Neutralize inherited tracing before libraries or subprocesses can activate it."""
    for key in tuple(os.environ):
        if key.startswith(("LANGCHAIN_", "LANGSMITH_", "OTEL_")) or key == "OPENAI_LOG":
            del os.environ[key]
    os.environ.update(
        LANGCHAIN_TRACING="false",
        LANGCHAIN_TRACING_V2="false",
        LANGSMITH_TRACING="false",
        OTEL_SDK_DISABLED="true",
    )
    for name in ("openai", "httpx", "httpx2", "httpcore", "httpcore2"):
        logging.getLogger(name).setLevel(logging.WARNING)


@asynccontextmanager
async def model_client(settings: Settings) -> AsyncGenerator[AsyncOpenAI | None]:
    """Own exactly one reusable SDK pool per server lifespan; never call a model here."""
    if not settings.model_configured or settings.openai_api_key is None:
        yield None
        return
    async with AsyncOpenAI(
        api_key=settings.openai_api_key.get_secret_value(),
        base_url="https://api.openai.com/v1",
        max_retries=0,
        timeout=30.0,
    ) as client:
        yield client
