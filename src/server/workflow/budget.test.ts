import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ExecutionBudget, type OperationKind } from "./budget";

beforeEach(() => {
  vi.useFakeTimers();
  vi.setSystemTime(0);
});
afterEach(() => vi.useRealTimers());
const pending = () => new Promise<never>(() => {});

describe("request execution budget", () => {
  it.each<{ kind: OperationKind; cap: number }>([
    { kind: "model", cap: 6 },
    { kind: "search", cap: 2 },
    { kind: "page", cap: 3 },
  ])(
    "dispatches only $cap parallel $kind attempts when the cap is raced",
    async ({ kind, cap }) => {
      // Given
      const budget = new ExecutionBudget();
      let dispatched = 0;
      const operation = async () => ++dispatched;
      // When
      const results = await Promise.allSettled(
        Array.from({ length: cap + 4 }, () => budget.run(kind, operation)),
      );
      // Then
      expect(dispatched).toBe(cap);
      expect(results.filter((result) => result.status === "fulfilled")).toHaveLength(cap);
      expect(results.filter((result) => result.status === "rejected")).toHaveLength(4);
      expect(vi.getTimerCount()).toBe(0);
    },
  );

  it("consumes failed attempts without retry when the provider rejects", async () => {
    // Given
    const budget = new ExecutionBudget();
    let dispatched = 0;
    const failure = new Error("provider unavailable");
    const operation = async () => {
      dispatched += 1;
      throw failure;
    };
    // When
    const results = await Promise.allSettled(
      Array.from({ length: 7 }, () => budget.run("model", operation)),
    );
    // Then
    expect(dispatched).toBe(6);
    expect(results[0]).toEqual({ status: "rejected", reason: failure });
    expect(results[6]).toMatchObject({ status: "rejected", reason: { code: "LIMIT_EXCEEDED" } });
    expect(budget.snapshot().modelCalls).toBe(6);
    expect(vi.getTimerCount()).toBe(0);
  });

  it("settles and aborts all work when a model ignores its 30 second signal", async () => {
    // Given
    const budget = new ExecutionBudget();
    const signals: AbortSignal[] = [];
    const operation = ({ signal }: { signal: AbortSignal }) => {
      signals.push(signal);
      return pending();
    };
    const result = Promise.allSettled([
      budget.run("model", operation),
      budget.run("search", operation),
    ]);
    // When
    await vi.advanceTimersByTimeAsync(30_000);
    // Then
    expect(await result).toMatchObject([
      { status: "rejected", reason: { code: "DEADLINE_EXCEEDED" } },
      { status: "rejected", reason: { code: "DEADLINE_EXCEEDED" } },
    ]);
    expect(signals.every((signal) => signal.aborted)).toBe(true);
    expect(vi.getTimerCount()).toBe(0);
  });

  it("uses the remaining research deadline when search precedes model summarization", async () => {
    // Given
    const budget = new ExecutionBudget();
    await budget.run("search", async () => "found");
    vi.setSystemTime(40_000);
    let timeout = 0;
    const result = budget.run(
      "model",
      ({ timeoutMs }) => {
        timeout = timeoutMs;
        return pending();
      },
      "research",
    );
    const observed = expect(result).rejects.toMatchObject({ code: "DEADLINE_EXCEEDED" });
    // When
    await vi.advanceTimersByTimeAsync(5_000);
    // Then
    await observed;
    expect(timeout).toBe(5_000);
    expect(vi.getTimerCount()).toBe(0);
  });

  it("bounds the entire research callback when no provider operation is active", async () => {
    // Given
    const budget = new ExecutionBudget();
    const observed = expect(budget.runResearch(pending)).rejects.toMatchObject({
      code: "DEADLINE_EXCEEDED",
    });
    // When
    await vi.advanceTimersByTimeAsync(45_000);
    // Then
    await observed;
    expect(vi.getTimerCount()).toBe(0);
  });

  it("uses the shared request remainder when a model begins near 180 seconds", async () => {
    // Given
    const budget = new ExecutionBudget();
    vi.setSystemTime(179_000);
    let timeout = 0;
    const result = budget.run("model", ({ timeoutMs }) => {
      timeout = timeoutMs;
      return pending();
    });
    const observed = expect(result).rejects.toMatchObject({ code: "DEADLINE_EXCEEDED" });
    // When
    await vi.advanceTimersByTimeAsync(1_000);
    // Then
    await observed;
    expect(timeout).toBe(1_000);
    expect(vi.getTimerCount()).toBe(0);
  });

  it.each(["request", "research"] as const)(
    "dispatches nothing when the %s deadline expired while idle",
    async (scope) => {
      // Given
      const budget = new ExecutionBudget();
      budget.startResearch();
      vi.setSystemTime(scope === "research" ? 45_000 : 180_000);
      let dispatched = 0;
      // When
      const result = budget.run("model", async () => ++dispatched, scope);
      // Then
      await expect(result).rejects.toMatchObject({ code: "DEADLINE_EXCEEDED" });
      expect(dispatched).toBe(0);
      expect(budget.snapshot().modelCalls).toBe(0);
    },
  );

  it("rejects active and future work when externally aborted without refunding attempts", async () => {
    // Given
    const controller = new AbortController();
    const budget = new ExecutionBudget({ signal: controller.signal });
    let signal: AbortSignal | undefined;
    const result = budget.run("model", (context) => {
      signal = context.signal;
      return pending();
    });
    const observed = expect(result).rejects.toMatchObject({ code: "CANCELLED" });
    // When
    controller.abort();
    // Then
    await observed;
    expect(signal?.aborted).toBe(true);
    expect(budget.snapshot().modelCalls).toBe(1);
    await expect(budget.run("model", async () => "unexpected")).rejects.toMatchObject({
      code: "CANCELLED",
    });
    expect(budget.snapshot().modelCalls).toBe(1);
    expect(vi.getTimerCount()).toBe(0);
  });

  it("dispatches nothing when the external signal was already aborted", async () => {
    // Given
    const controller = new AbortController();
    controller.abort();
    const budget = new ExecutionBudget({ signal: controller.signal });
    let dispatched = 0;
    // When
    const result = budget.run("page", async () => ++dispatched);
    // Then
    await expect(result).rejects.toMatchObject({ code: "CANCELLED" });
    expect(dispatched).toBe(0);
  });

  it("removes external listeners and timers when successful work settles", async () => {
    // Given
    const controller = new AbortController();
    const remove = vi.spyOn(controller.signal, "removeEventListener");
    const budget = new ExecutionBudget({ signal: controller.signal });
    // When
    const result = await budget.run("model", async () => "value");
    // Then
    expect(result).toBe("value");
    expect(remove).toHaveBeenCalledWith("abort", expect.any(Function));
    expect(vi.getTimerCount()).toBe(0);
  });

  it("cancels pending work when the owning request disposes the budget", async () => {
    // Given
    const budget = new ExecutionBudget();
    const observed = expect(budget.run("model", pending)).rejects.toMatchObject({
      code: "CANCELLED",
    });
    // When
    budget.dispose();
    // Then
    await observed;
    expect(vi.getTimerCount()).toBe(0);
  });

  it("bounds request orchestration when no provider call is active", async () => {
    // Given
    const budget = new ExecutionBudget();
    const observed = expect(budget.runRequest(pending)).rejects.toMatchObject({
      code: "DEADLINE_EXCEEDED",
    });
    // When
    await vi.advanceTimersByTimeAsync(180_000);
    // Then
    await observed;
    expect(vi.getTimerCount()).toBe(0);
  });

  it("rejects late completion when synchronous provider work passes the deadline", async () => {
    // Given
    const budget = new ExecutionBudget();
    // When
    const result = budget.run("model", async () => {
      vi.setSystemTime(30_000);
      return "late";
    });
    // Then
    await expect(result).rejects.toMatchObject({ code: "DEADLINE_EXCEEDED" });
    expect(vi.getTimerCount()).toBe(0);
  });

  it("keeps model reservations isolated when separate requests run concurrently", async () => {
    // Given
    const first = new ExecutionBudget();
    const second = new ExecutionBudget();
    // When
    const results = await Promise.all(
      Array.from({ length: 6 }, () =>
        Promise.all([first.run("model", async () => "a"), second.run("model", async () => "b")]),
      ),
    );
    // Then
    expect(results).toHaveLength(6);
    expect(first.snapshot().modelCalls).toBe(6);
    expect(second.snapshot().modelCalls).toBe(6);
  });
});
