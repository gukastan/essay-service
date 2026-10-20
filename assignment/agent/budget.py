"""Request-local atomic reservations and cancellable monotonic deadlines."""

import time
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Literal, final

import anyio

from agent.limits import (
    MAX_MODEL_CALLS,
    MAX_NATIVE_TOOL_CALLS,
    MAX_OUTPUT_TOKENS,
    ROLE_CALL_LIMITS,
    ROLE_OUTPUT_TOKENS,
    ModelRole,
)


@final
class ExecutionBudgetError(Exception):
    def __init__(
        self,
        code: Literal[
            "LIMIT_EXCEEDED",
            "DEADLINE_EXCEEDED",
            "CANCELLED",
        ],
    ) -> None:
        self.code = code
        super().__init__(code)


@final
class RevisionReservationError(Exception):
    def __init__(self, code: Literal["REVISION_EXHAUSTED", "INVALID_REVISION_ROUTE"]) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class OperationContext:
    timeout_seconds: float
    max_output_tokens: int = 0
    max_tool_calls: int = 0


@dataclass(frozen=True, slots=True)
class BudgetSnapshot:
    model_calls: int
    searches: int
    page_reads: int
    native_tool_calls_reserved: int
    output_tokens_reserved: int
    deadline: float
    revision_count: Literal[0, 1] = 0
    revision_route: Literal["D", "I"] | None = None


@dataclass(frozen=True, slots=True)
class RevisionReservation:
    route: Literal["D", "I"]
    revision_count: Literal[1] = 1


@final
class ExecutionBudget:
    """Mutable request accumulator; one lock owns every no-refund reservation."""

    def __init__(self, now: Callable[[], float] = time.monotonic) -> None:
        self._now = now
        self.deadline = now() + 180.0
        self._research_deadline: float | None = None
        self._lock = anyio.Lock()
        self._roles: dict[ModelRole, int] = dict.fromkeys(ROLE_CALL_LIMITS, 0)
        self._counts: dict[Literal["search", "page"], int] = {"search": 0, "page": 0}
        self._native_reserved = 0
        self._tokens_reserved = 0
        self._stopped: ExecutionBudgetError | None = None
        self._active: set[anyio.CancelScope] = set()
        self._revision: RevisionReservation | None = None

    @asynccontextmanager
    async def _reservation(self) -> AsyncGenerator[None]:
        try:
            async with self._lock:
                yield
        except anyio.get_cancelled_exc_class():
            self.cancel()
            raise

    def snapshot(self) -> BudgetSnapshot:
        return BudgetSnapshot(
            sum(self._roles.values()),
            self._counts["search"],
            self._counts["page"],
            self._native_reserved,
            self._tokens_reserved,
            self.deadline,
            0 if self._revision is None else self._revision.revision_count,
            None if self._revision is None else self._revision.route,
        )

    async def reserve_revision(self, route: str) -> RevisionReservation:
        """Consume the shared D/I opportunity before work; never refund it."""
        async with self._reservation():
            self._check(self.deadline)
            if route not in ("D", "I"):
                raise RevisionReservationError("INVALID_REVISION_ROUTE")
            if self._revision is not None:
                raise RevisionReservationError("REVISION_EXHAUSTED")
            self._revision = RevisionReservation(route)
            return self._revision

    def _check(self, deadline: float) -> None:
        if self._stopped is not None:
            raise self._stopped
        if self._now() >= deadline:
            self._stop(ExecutionBudgetError("DEADLINE_EXCEEDED"))
            raise ExecutionBudgetError("DEADLINE_EXCEEDED")

    def _research_end(self) -> float:
        self._check(self.deadline)
        if self._research_deadline is None:
            self._research_deadline = min(self.deadline, self._now() + 45.0)
        self._check(self._research_deadline)
        return self._research_deadline

    async def run_model[T](
        self,
        role: ModelRole,
        operation: Callable[[OperationContext], Awaitable[T]],
    ) -> T:
        async with self._reservation():
            end = self._research_end() if role == "research" else self.deadline
            self._check(end)
            tokens = ROLE_OUTPUT_TOKENS[role]
            self._reserve_model(role, tokens)
            end = min(end, self._now() + 30.0)
        return await self._execute(end, operation, OperationContext(end - self._now(), tokens))

    def _reserve_model(self, role: ModelRole, tokens: int) -> None:
        if (
            sum(self._roles.values()) >= MAX_MODEL_CALLS
            or self._roles[role] >= ROLE_CALL_LIMITS[role]
            or self._tokens_reserved + tokens > MAX_OUTPUT_TOKENS
        ):
            raise ExecutionBudgetError("LIMIT_EXCEEDED")
        self._roles[role] += 1
        self._tokens_reserved += tokens

    async def run_native_research[T](
        self,
        operation: Callable[[OperationContext], Awaitable[T]],
    ) -> T:
        async with self._reservation():
            end = min(self._research_end(), self._now() + 30.0)
            self._check(end)
            if self._native_reserved + MAX_NATIVE_TOOL_CALLS > MAX_NATIVE_TOOL_CALLS:
                raise ExecutionBudgetError("LIMIT_EXCEEDED")
            self._reserve_model("research", 3000)
            self._native_reserved += 2
        return await self._execute(end, operation, OperationContext(end - self._now(), 3000, 2))

    async def run[T](
        self,
        kind: Literal["search", "page"],
        operation: Callable[[OperationContext], Awaitable[T]],
    ) -> T:
        async with self._reservation():
            end = self._research_end()
            if self._counts[kind] >= {"search": 2, "page": 3}[kind]:
                raise ExecutionBudgetError("LIMIT_EXCEEDED")
            self._counts[kind] += 1
        return await self._execute(end, operation, OperationContext(end - self._now()))

    async def run_request[T](
        self,
        operation: Callable[[OperationContext], Awaitable[T]],
    ) -> T:
        return await self._execute(
            self.deadline,
            operation,
            OperationContext(self.deadline - self._now()),
        )

    async def run_research[T](
        self,
        operation: Callable[[OperationContext], Awaitable[T]],
    ) -> T:
        end = self._research_end()
        return await self._execute(end, operation, OperationContext(end - self._now()))

    def _stop(self, error: ExecutionBudgetError) -> None:
        self._stopped = self._stopped or error
        for scope in self._active:
            scope.cancel()

    def cancel(self) -> None:
        self._stop(ExecutionBudgetError("CANCELLED"))

    async def _execute[T](
        self,
        end: float,
        operation: Callable[[OperationContext], Awaitable[T]],
        context: OperationContext,
    ) -> T:
        self._check(end)
        completed: list[T] = []
        try:
            with anyio.CancelScope(deadline=anyio.current_time() + end - self._now()) as scope:
                self._active.add(scope)
                try:
                    await anyio.lowlevel.checkpoint()
                    self._check(end)
                    completed.append(await operation(context))
                    self._check(end)
                finally:
                    self._active.remove(scope)
            if scope.cancel_called:
                self._stop(self._stopped or ExecutionBudgetError("DEADLINE_EXCEEDED"))
                raise self._stopped or ExecutionBudgetError("DEADLINE_EXCEEDED")
            return completed[0]
        except anyio.get_cancelled_exc_class():
            self.cancel()
            raise
