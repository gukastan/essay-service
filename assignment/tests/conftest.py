"""Isolated pytest runtime for the asyncio-only SDK integrations."""

import pytest


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
