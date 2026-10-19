import { afterEach, describe, expect, it, vi } from "vitest";

const provider = vi.hoisted(() => vi.fn());
vi.mock("./model", () => ({ generateModelOutput: provider, MODEL_TIMEOUT_MS: 30000 }));

import { createDraft } from "./drafts";

const input = { company: "회사", role: "개발", question: "경험", experience: "팀 프로젝트" };
const config = { apiKey: "unit-test-only", model: "gpt-5.6-terra" };
afterEach(() => {
  vi.resetAllMocks();
  vi.useRealTimers();
});

describe("bounded drafting pipeline", () => {
  it.each([801, 1000])("accepts %i code points after one call", async (count) => {
    provider.mockResolvedValue({ status: "draft", draft: "😀".repeat(count) });
    const result = await createDraft(input, config);
    expect(result.httpStatus).toBe(200);
    expect(result.body).toMatchObject({
      status: "ready",
      characterCount: count,
      generationCalls: 1,
    });
    expect(provider).toHaveBeenCalledTimes(1);
  });

  it.each([800, 1001])(
    "rewrites %i once using normalized original and actual count",
    async (count) => {
      const original = `${"가".repeat(count - 1)}\r\n`;
      provider
        .mockResolvedValueOnce({ status: "draft", draft: original })
        .mockResolvedValueOnce({ status: "draft", draft: "나".repeat(801) });
      expect((await createDraft(input, config)).body).toMatchObject({
        status: "ready",
        generationCalls: 2,
      });
      expect(provider).toHaveBeenCalledTimes(2);
      expect(provider).toHaveBeenNthCalledWith(
        2,
        { input, rewrite: { draft: `${"가".repeat(count - 1)}\n`, characterCount: count } },
        expect.any(AbortSignal),
        config,
      );
    },
  );

  it("fails after two invalid drafts without leaking the draft", async () => {
    provider.mockResolvedValue({ status: "draft", draft: "가".repeat(800) });
    const result = await createDraft(input, config);
    expect(result).toMatchObject({ httpStatus: 422, body: { code: "LENGTH_RETRY_EXHAUSTED" } });
    expect(result.body).not.toHaveProperty("draft");
    expect(provider).toHaveBeenCalledTimes(2);
  });

  it.each([1, 2])("returns needs_input on call %i without length retry", async (calls) => {
    if (calls === 2) provider.mockResolvedValueOnce({ status: "draft", draft: "가".repeat(800) });
    provider.mockResolvedValueOnce({ status: "needs_input", message: "행동을 더 알려 주세요." });
    expect((await createDraft(input, config)).body).toEqual({
      status: "needs_input",
      message: "행동을 더 알려 주세요.",
      generationCalls: calls,
    });
    expect(provider).toHaveBeenCalledTimes(calls);
  });

  it.each([null, {}, { status: "draft", draft: " " }, { status: "needs_input", message: 3 }])(
    "rejects malformed model output %j without retry",
    async (output) => {
      provider.mockResolvedValue(output);
      expect(await createDraft(input, config)).toMatchObject({
        httpStatus: 502,
        body: { code: "MODEL_ERROR" },
      });
      expect(provider).toHaveBeenCalledTimes(1);
    },
  );

  it("aborts at 30 seconds and stops even when provider ignores cancellation", async () => {
    vi.useFakeTimers();
    let signal: AbortSignal | undefined;
    provider.mockImplementation((_request, callSignal: AbortSignal) => {
      signal = callSignal;
      return new Promise(() => {});
    });
    const pending = createDraft(input, config);
    await vi.advanceTimersByTimeAsync(29999);
    expect(signal?.aborted).toBe(false);
    await vi.advanceTimersByTimeAsync(1);
    expect(await pending).toMatchObject({ httpStatus: 504, body: { code: "MODEL_TIMEOUT" } });
    expect(signal?.aborted).toBe(true);
    expect(provider).toHaveBeenCalledTimes(1);
    expect(vi.getTimerCount()).toBe(0);
  });

  it("redacts provider failures and clears its deadline", async () => {
    vi.useFakeTimers();
    provider.mockRejectedValue(new Error("private-provider-details"));
    const result = await createDraft(input, config);
    expect(result).toMatchObject({ httpStatus: 502, body: { code: "MODEL_ERROR" } });
    expect(JSON.stringify(result)).not.toContain("private-provider-details");
    expect(provider).toHaveBeenCalledTimes(1);
    expect(vi.getTimerCount()).toBe(0);
  });
});
