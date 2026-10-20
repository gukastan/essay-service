"""Single-call OpenAI Responses adapter with strict output and sanitized errors."""

from dataclasses import dataclass

import anyio
from openai import APIError, APITimeoutError, AsyncOpenAI
from openai.types.responses import ResponseOutputMessage
from pydantic import BaseModel, ValidationError

from agent.budget import ExecutionBudget, OperationContext
from agent.provider_schema import response_format
from agent.providers import ModelResult, ProviderError, StructuredModelRequest, TokenUsage
from agent.response_wire import ResponseEnvelope, validate_response


def parse_response[T: BaseModel](response: ResponseEnvelope, schema: type[T]) -> ModelResult[T]:
    """Reject refusal/incomplete/invalid outputs without retaining provider text."""
    texts: list[str] = []
    for item in response.output:
        if isinstance(item, ResponseOutputMessage):
            for content in item.content:
                if content.type == "refusal":
                    raise ProviderError("REFUSAL")
                texts.append(content.text)
    if response.status != "completed":
        raise ProviderError("INCOMPLETE")
    try:
        value = schema.model_validate_json("".join(texts))
    except ValidationError:
        raise ProviderError("INVALID_RESPONSE") from None
    usage = response.usage
    return ModelResult(
        value, TokenUsage(usage.input_tokens, usage.output_tokens) if usage else None
    )


@dataclass(frozen=True, slots=True)
class OpenAIModelProvider:
    client: AsyncOpenAI | None
    model: str | None

    async def generate[T: BaseModel](
        self,
        request: StructuredModelRequest[T],
        budget: ExecutionBudget,
    ) -> ModelResult[T]:
        if self.client is None or not self.model:
            raise ProviderError("CONFIG_ERROR")
        client, model = self.client, self.model
        wire_format = response_format(request.schema, f"essay_{request.role}")

        async def invoke(context: OperationContext) -> ModelResult[T]:
            try:
                with anyio.fail_after(context.timeout_seconds):
                    response = await client.with_options(max_retries=0).responses.create(
                        model=model,
                        input=request.input,
                        instructions=request.instructions,
                        store=False,
                        reasoning={"effort": "low"},
                        max_output_tokens=context.max_output_tokens,
                        text={"format": wire_format},
                        timeout=context.timeout_seconds,
                    )
            except (APITimeoutError, TimeoutError):
                budget.cancel()
                raise ProviderError("TIMEOUT") from None
            except APIError:
                raise ProviderError("MODEL_ERROR") from None
            return parse_response(validate_response(response), request.schema)

        return await budget.run_model(request.role, invoke)
