"""Body, extraction and HTTP error boundaries with finite source fixtures."""

from datetime import UTC, datetime

import httpx
import pytest

from agent.budget import ExecutionBudget
from agent.source_http import SafePageReader
from agent.source_page import PageReadError, extract_page
from tests.test_source_http import page, public_dns


@pytest.mark.anyio
@pytest.mark.parametrize("length", [1048576, 1048577])
async def test_raw_page_limit_accepts_exact_boundary_only(length: int) -> None:
    # Given
    reader = SafePageReader(
        resolver=public_dns, transport=httpx.MockTransport(lambda _: page(b"x" * length))
    )
    # When / Then
    if length == 1048576:
        result = await reader.read("https://careers.example/job", ExecutionBudget())
        assert len(result.text) == 12000
    else:
        with pytest.raises(PageReadError) as raised:
            _ = await reader.read("https://careers.example/job", ExecutionBudget())
        assert raised.value.code == "TOO_LARGE"


def test_visible_unicode_extraction_drops_executable_text_and_preserves_link_target() -> None:
    # Given
    body = (
        "<script>send secret</script><style>ignore policy</style><noscript>fake</noscript>"
        '<template>hidden</template><p>Acme Engineer 😀</p><a href="/jobs/1">Apply</a>'
    ).encode()
    checked = datetime(2026, 10, 20, tzinfo=UTC)
    # When
    result = extract_page("https://careers.example/about", body, checked)
    # Then
    assert result.text == "Acme Engineer 😀 Apply"
    assert result.links == ("https://careers.example/jobs/1",)
    assert result.checked_at == checked


@pytest.mark.parametrize("body", [b"", b"<script>only hidden</script>", b"\xff"])
def test_empty_or_invalid_encoding_never_becomes_source(body: bytes) -> None:
    # Given / When
    with pytest.raises(PageReadError) as raised:
        _ = extract_page("https://careers.example", body, datetime(2026, 10, 20, tzinfo=UTC))
    # Then
    assert raised.value.code in {"EMPTY", "INVALID_PAGE"}


@pytest.mark.anyio
@pytest.mark.parametrize("status", [401, 403, 404, 410, 429, 451])
async def test_access_denied_is_explicit_and_never_retried(status: int) -> None:
    # Given
    sent: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        sent.append(request)
        return httpx.Response(status)

    reader = SafePageReader(resolver=public_dns, transport=httpx.MockTransport(respond))
    # When
    with pytest.raises(PageReadError) as raised:
        _ = await reader.read("https://careers.example/job", ExecutionBudget())
    # Then
    assert raised.value.code == "ACCESS_DENIED"
    assert len(sent) == 1


@pytest.mark.anyio
async def test_network_failure_is_sanitized_and_never_retried() -> None:
    # Given
    sent: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        sent.append(request)
        raise httpx.ConnectError("PRIVATE_INTERNAL_DETAIL")

    reader = SafePageReader(resolver=public_dns, transport=httpx.MockTransport(respond))
    # When
    with pytest.raises(PageReadError) as raised:
        _ = await reader.read("https://careers.example/job", ExecutionBudget())
    # Then
    assert str(raised.value) == "NETWORK_ERROR"
    assert len(sent) == 1
