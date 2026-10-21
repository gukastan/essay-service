from collections.abc import Awaitable, Callable, Mapping
from typing import Generic, TypeVar

_State = TypeVar("_State")

START: str
END: str

class CompiledStateGraph(Generic[_State]):
    async def ainvoke(self, input: _State) -> _State: ...

class StateGraph(Generic[_State]):
    def __init__(self, state_schema: type[_State]) -> None: ...
    def add_node(
        self, node: str, action: Callable[[_State], _State | Awaitable[_State]]
    ) -> StateGraph[_State]: ...
    def add_edge(self, start_key: str | list[str], end_key: str) -> StateGraph[_State]: ...
    def add_conditional_edges(
        self, source: str, path: Callable[[_State], str], path_map: Mapping[str, str]
    ) -> StateGraph[_State]: ...
    def compile(self) -> CompiledStateGraph[_State]: ...
