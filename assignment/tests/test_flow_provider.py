import pytest
from pydantic import BaseModel

from agent.contracts import (
    DraftEnvelope,
    Evaluation,
    FlowAnalysisResult,
    MissingInputTerminal,
    OperationalTerminal,
    ReadyTerminal,
    ReviewNeededTerminal,
    WritingPlan,
)
from agent.provider_schema import strict_schema
from tests.wire_fixture import assert_strict_schema


@pytest.mark.parametrize(
    "model",
    [
        FlowAnalysisResult,
        WritingPlan,
        DraftEnvelope,
        Evaluation,
        ReadyTerminal,
        MissingInputTerminal,
        ReviewNeededTerminal,
        OperationalTerminal,
    ],
)
def test_flow_models_have_recursively_strict_provider_schemas(model: type[BaseModel]) -> None:
    assert_strict_schema(strict_schema(model))
