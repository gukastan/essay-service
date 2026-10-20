"""Foundation MCP server exposing one candidate-only company/job research tool."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastmcp import Context, FastMCP
from fastmcp.exceptions import ToolError
from pydantic import ValidationError

from agent.contracts import ResearchInput
from agent.provider_schema import JSON
from agent.providers import ProviderError
from agent.research import (
    OpenAIResearchProvider,
    ResearchMetadata,
    ResearchProvider,
    ResearchReport,
)
from agent.settings import Settings, disable_tracing, model_client


def create_mcp(provider: ResearchProvider | None = None) -> FastMCP:
    """Inject a research provider for protocol tests; production owns its SDK lifespan."""
    disable_tracing()
    active_provider = provider

    @asynccontextmanager
    async def lifespan(_: FastMCP) -> AsyncGenerator[dict[str, str]]:
        nonlocal active_provider
        if provider is not None:
            yield {}
            return
        settings = Settings()
        async with model_client(settings) as client:
            active_provider = OpenAIResearchProvider(client, settings.openai_model)
            try:
                yield {}
            finally:
                active_provider = None

    server = FastMCP(
        "essay-research-foundation",
        lifespan=lifespan,
        mask_error_details=True,
        strict_input_validation=True,
    )

    @server.tool
    async def research_company_role(input: ResearchInput, ctx: Context) -> ResearchReport:
        """Return unverified company/job research candidates with bounded hosted search."""
        context = ctx.request_context
        try:
            raw = JSON.validate_python(context.meta if context else None)
            if isinstance(raw, dict):
                raw = {
                    key: value
                    for key, value in raw.items()
                    if key
                    not in {
                        "progressToken",
                        "io.modelcontextprotocol/protocolVersion",
                        "io.modelcontextprotocol/clientInfo",
                        "io.modelcontextprotocol/clientCapabilities",
                        "io.modelcontextprotocol/logLevel",
                    }
                }
            metadata = ResearchMetadata.model_validate(raw)
        except ValidationError:
            raise ToolError("INVALID_METADATA") from None
        if active_provider is None:
            raise ToolError("CONFIG_ERROR")
        try:
            return await active_provider.research(input, metadata)
        except ProviderError as error:
            raise ToolError(error.code) from None

    return server


mcp = create_mcp()
if __name__ == "__main__":
    mcp.run(transport="stdio", show_banner=False)
