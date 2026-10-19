import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ExecutionBudget } from "./budget";

beforeEach(() => {
  vi.useFakeTimers();
  vi.setSystemTime(0);
});
afterEach(() => vi.useRealTimers());
const pending = () => new Promise<never>(() => {});

describe("native research reservations", () => {
  it("dispatches one Responses request when native reservations race", async () => {
    // Given
    const budget = new ExecutionBudget();
    let dispatched = 0;
    const capacities: number[] = [];
    // When
    const results = await Promise.allSettled(
      Array.from({ length: 4 }, () =>
        budget.runNativeResearch(async ({ maxToolCalls }) => {
          dispatched += 1;
          capacities.push(maxToolCalls);
          return "result";
        }),
      ),
    );
    // Then
    expect(dispatched).toBe(1);
    expect(capacities).toEqual([2]);
    expect(results.filter((result) => result.status === "rejected")).toHaveLength(3);
    expect(budget.snapshot()).toMatchObject({
      modelCalls: 1,
      nativeToolCallsReserved: 2,
      searches: 0,
      pageReads: 0,
    });
    expect(vi.getTimerCount()).toBe(0);
  });

  it("reserves no hosted tools when ordinary models already consumed the model cap", async () => {
    // Given
    const budget = new ExecutionBudget();
    await Promise.all(Array.from({ length: 6 }, () => budget.run("model", async () => "model")));
    let dispatched = 0;
    // When
    const result = budget.runNativeResearch(async () => ++dispatched);
    // Then
    await expect(result).rejects.toMatchObject({ code: "LIMIT_EXCEEDED" });
    expect(dispatched).toBe(0);
    expect(budget.snapshot()).toMatchObject({ modelCalls: 6, nativeToolCallsReserved: 0 });
  });

  it("keeps the combined model cap when native and ordinary calls race", async () => {
    // Given
    const budget = new ExecutionBudget();
    await Promise.all(Array.from({ length: 5 }, () => budget.run("model", async () => "model")));
    // When
    const results = await Promise.allSettled([
      budget.runNativeResearch(async () => "native"),
      budget.run("model", async () => "model"),
    ]);
    // Then
    expect(results).toMatchObject([
      { status: "fulfilled", value: "native" },
      { status: "rejected", reason: { code: "LIMIT_EXCEEDED" } },
    ]);
    expect(budget.snapshot()).toMatchObject({ modelCalls: 6, nativeToolCallsReserved: 2 });
  });

  it.each([false, true])("retains full reservations after provider failure=%s", async (fails) => {
    // Given
    const budget = new ExecutionBudget();
    const first = await Promise.allSettled([
      budget.runNativeResearch(async () => {
        if (fails) throw new Error("provider failed");
        return "zero hosted tools actually used";
      }),
    ]);
    let dispatched = 0;
    // When
    const next = budget.runNativeResearch(async () => ++dispatched);
    // Then
    expect(first[0]?.status).toBe(fails ? "rejected" : "fulfilled");
    await expect(next).rejects.toMatchObject({ code: "LIMIT_EXCEEDED" });
    expect(dispatched).toBe(0);
    expect(budget.snapshot()).toMatchObject({ modelCalls: 1, nativeToolCallsReserved: 2 });
  });

  it("retains both reservations when external cancellation interrupts dispatch", async () => {
    // Given
    const controller = new AbortController();
    const budget = new ExecutionBudget({ signal: controller.signal });
    let providerSignal: AbortSignal | undefined;
    const result = budget.runNativeResearch(({ signal }) => {
      providerSignal = signal;
      return pending();
    });
    const observed = expect(result).rejects.toMatchObject({ code: "CANCELLED" });
    // When
    controller.abort();
    // Then
    await observed;
    expect(providerSignal?.aborted).toBe(true);
    expect(budget.snapshot()).toMatchObject({ modelCalls: 1, nativeToolCallsReserved: 2 });
    expect(vi.getTimerCount()).toBe(0);
  });

  it.each([
    { start: 0, researchStart: 0, remaining: 30_000 },
    { start: 40_000, researchStart: 0, remaining: 5_000 },
    { start: 179_000, researchStart: 179_000, remaining: 1_000 },
  ])(
    "bounds native dispatch to $remaining ms when starting at $start",
    async ({ start, researchStart, remaining }) => {
      // Given
      const budget = new ExecutionBudget();
      vi.setSystemTime(researchStart);
      budget.startResearch();
      vi.setSystemTime(start);
      let allotted = 0;
      const result = budget.runNativeResearch(({ timeoutMs }) => {
        allotted = timeoutMs;
        return pending();
      });
      const observed = expect(result).rejects.toMatchObject({ code: "DEADLINE_EXCEEDED" });
      // When
      await vi.advanceTimersByTimeAsync(remaining);
      // Then
      await observed;
      expect(allotted).toBe(remaining);
      expect(budget.snapshot()).toMatchObject({ modelCalls: 1, nativeToolCallsReserved: 2 });
      expect(vi.getTimerCount()).toBe(0);
    },
  );

  it("reserves nothing when research has already expired", async () => {
    // Given
    const budget = new ExecutionBudget();
    budget.startResearch();
    vi.setSystemTime(45_000);
    let dispatched = 0;
    // When
    const result = budget.runNativeResearch(async () => ++dispatched);
    // Then
    await expect(result).rejects.toMatchObject({ code: "DEADLINE_EXCEEDED" });
    expect(dispatched).toBe(0);
    expect(budget.snapshot()).toMatchObject({ modelCalls: 0, nativeToolCallsReserved: 0 });
  });
});
