import { afterEach, describe, expect, it, vi } from "vitest";
import { z } from "zod";

const sdk = vi.hoisted(() => ({ create: vi.fn(), constructor: vi.fn() }));
vi.mock("openai", () => ({
  default: class {
    constructor(options: unknown) {
      sdk.constructor(options);
    }
    responses = { create: sdk.create };
  },
}));

import { ExecutionBudget } from "./budget";
import { createOpenAINativeResearchProvider } from "./native-provider";

const config = { apiKey: "test-only", model: "gpt-5.6-terra" };
const request = {
  input: { company: "OpenAI", role: "Engineer" },
  schema: z.object({ url: z.string() }),
};
const response = {
  status: "completed",
  output_text: '{"url":"https://openai.com/careers/"}',
  usage: { input_tokens: 10, output_tokens: 8 },
  output: [
    {
      type: "web_search_call",
      status: "completed",
      action: {
        type: "search",
        queries: ["OpenAI Engineer"],
        sources: [{ type: "url", url: "https://openai.com/careers/" }],
      },
    },
  ],
};
afterEach(() => vi.resetAllMocks());
describe("native research provider (mocked SDK)", () => {
  it("reserves model1/hosted2 and projects only company/role/posting fields", async () => {
    sdk.create.mockResolvedValue(response);
    const budget = new ExecutionBudget({ now: () => 0 });
    const result = await createOpenAINativeResearchProvider(config).generate(
      {
        ...request,
        input: {
          ...request.input,
          jobPostingText: "Public job",
          ...{ experience: "PRIVATE", question: "PRIVATE" },
        },
      },
      budget,
    );
    expect(sdk.constructor).toHaveBeenCalledWith({
      apiKey: "test-only",
      timeout: 30000,
      maxRetries: 0,
    });
    expect(sdk.create).toHaveBeenCalledWith(
      expect.objectContaining({
        max_tool_calls: 2,
        tools: [{ type: "web_search", search_context_size: "low" }],
        tool_choice: "required",
        store: false,
        max_output_tokens: 3000,
        reasoning: { effort: "low" },
        input: JSON.stringify({ ...request.input, jobPostingText: "Public job" }),
        text: { format: expect.objectContaining({ type: "json_schema", strict: true }) },
      }),
      { signal: expect.any(AbortSignal), timeout: 30000, maxRetries: 0 },
    );
    expect(result.providerEvidence).toMatchObject({
      verification: "unverified",
      toolCallsReported: 1,
      toolCallsReserved: 2,
    });
    expect(result.usage).toEqual({ inputTokens: 10, outputTokens: 8 });
    expect(budget.snapshot()).toMatchObject({
      modelCalls: 1,
      nativeToolCallsReserved: 2,
      searches: 0,
      pageReads: 0,
    });
    await expect(
      createOpenAINativeResearchProvider(config).generate(request, budget),
    ).rejects.toMatchObject({ code: "LIMIT_EXCEEDED" });
    expect(sdk.create).toHaveBeenCalledTimes(1);
    budget.dispose();
  });
  it("clips SDK timeout to remaining research stage time", async () => {
    let now = 0;
    const budget = new ExecutionBudget({ now: () => now });
    budget.startResearch();
    now = 42000;
    sdk.create.mockResolvedValue(response);
    await createOpenAINativeResearchProvider(config).generate(request, budget);
    expect(sdk.create.mock.calls[0]?.[1].timeout).toBe(3000);
    budget.dispose();
  });
  it.each([
    { ...response, status: "incomplete" },
    { ...response, output_text: "PRIVATE invalid" },
    { ...response, output_text: '{"url":12}' },
    { ...response, output: [] },
    { ...response, output: Array.from({ length: 3 }, () => response.output[0]) },
    { ...response, output: [{ ...response.output[0], status: "failed" }] },
  ])("rejects incomplete/malformed/missing or excess tool output without retry", async (result) => {
    sdk.create.mockResolvedValue(result);
    const budget = new ExecutionBudget({ now: () => 0 });
    await expect(
      createOpenAINativeResearchProvider(config).generate(request, budget),
    ).rejects.toMatchObject({ name: "ProviderResponseError" });
    expect(sdk.create).toHaveBeenCalledTimes(1);
    expect(budget.snapshot()).toMatchObject({ modelCalls: 1, nativeToolCallsReserved: 2 });
    budget.dispose();
  });
  it("does not retry transport failures or refund reserved native capacity", async () => {
    const error = new TypeError("network failed");
    sdk.create.mockRejectedValue(error);
    const budget = new ExecutionBudget({ now: () => 0 });
    const provider = createOpenAINativeResearchProvider(config);
    await expect(provider.generate(request, budget)).rejects.toBe(error);
    await expect(provider.generate(request, budget)).rejects.toMatchObject({
      code: "LIMIT_EXCEEDED",
    });
    expect(sdk.create).toHaveBeenCalledTimes(1);
    budget.dispose();
  });
});
