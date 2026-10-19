import { zodTextFormat } from "openai/helpers/zod";
import { afterEach, describe, expect, it, vi } from "vitest";
import { z } from "zod";
import {
  AnalysisResultSchema,
  ReviewResultSchema,
  WriterResultSchema,
} from "@/shared/contracts-v2";

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
import { normalizeResearchModelOutput, ResearchModelOutputSchema } from "./provider-schemas";
import { createOpenAIModelProvider, createResearchTools } from "./providers";

const schema = z.object({ ok: z.boolean() });
const request = {
  role: "analysis",
  instructions: "Return JSON",
  input: "public fixture",
  schema,
} as const;
const config = { apiKey: "test-only", model: "gpt-5.6-terra" };
afterEach(() => vi.resetAllMocks());

describe("v2 model adapter (mocked SDK, no paid traffic)", () => {
  it("uses strict JSON, role token limit, low reasoning, no storage or retry", async () => {
    sdk.create.mockResolvedValue({
      status: "completed",
      output_text: '{"ok":true}',
      usage: { input_tokens: 12, output_tokens: 8 },
    });
    const budget = new ExecutionBudget({ now: () => 0 });
    const result = await createOpenAIModelProvider(config).generate(request, budget);
    expect(result).toEqual({ value: { ok: true }, usage: { inputTokens: 12, outputTokens: 8 } });
    expect(sdk.constructor).toHaveBeenCalledWith({
      apiKey: "test-only",
      maxRetries: 0,
      timeout: 30000,
    });
    expect(sdk.create).toHaveBeenCalledWith(
      expect.objectContaining({
        model: config.model,
        reasoning: { effort: "low" },
        store: false,
        max_output_tokens: 3000,
        text: { format: expect.objectContaining({ type: "json_schema", strict: true }) },
      }),
      { signal: expect.any(AbortSignal), timeout: 30000, maxRetries: 0 },
    );
    expect(sdk.create.mock.calls[0]?.[0]).not.toHaveProperty("tools");
    expect(budget.snapshot().modelCalls).toBe(1);
    budget.dispose();
  });
  it.each([
    { status: "incomplete", output_text: '{"ok":true}', code: "incomplete" },
    { status: "completed", output_text: "SECRET malformed", code: "invalid_output" },
    { status: "completed", output_text: '{"ok":"SECRET"}', code: "invalid_output" },
    { status: "completed", output_text: "", code: "invalid_output" },
  ])("rejects invalid/incomplete output without retry ($code)", async ({ code, ...response }) => {
    sdk.create.mockResolvedValue(response);
    const budget = new ExecutionBudget({ now: () => 0 });
    await expect(createOpenAIModelProvider(config).generate(request, budget)).rejects.toMatchObject(
      { name: "ProviderResponseError", code, message: `Provider response: ${code}` },
    );
    expect(sdk.create).toHaveBeenCalledTimes(1);
    expect(budget.snapshot().modelCalls).toBe(1);
    budget.dispose();
  });
  it("retains consumed budget on network failure and does not retry", async () => {
    const failure = new TypeError("network failed");
    sdk.create.mockRejectedValue(failure);
    const budget = new ExecutionBudget({ now: () => 0 });
    await expect(createOpenAIModelProvider(config).generate(request, budget)).rejects.toBe(failure);
    expect(sdk.create).toHaveBeenCalledTimes(1);
    expect(budget.snapshot().modelCalls).toBe(1);
    budget.dispose();
  });
  it("blocks the seventh model request before SDK execution", async () => {
    sdk.create.mockResolvedValue({ status: "completed", output_text: '{"ok":true}' });
    const budget = new ExecutionBudget({ now: () => 0 });
    const provider = createOpenAIModelProvider(config);
    await Promise.all(Array.from({ length: 6 }, () => provider.generate(request, budget)));
    await expect(provider.generate(request, budget)).rejects.toMatchObject({
      code: "LIMIT_EXCEEDED",
    });
    expect(sdk.create).toHaveBeenCalledTimes(6);
    budget.dispose();
  });
  it("passes research remaining time while leaving analysis at 30 seconds", async () => {
    let now = 0;
    const budget = new ExecutionBudget({ now: () => now });
    budget.startResearch();
    now = 40000;
    sdk.create.mockResolvedValue({ status: "completed", output_text: '{"ok":true}' });
    const provider = createOpenAIModelProvider(config);
    await provider.generate({ ...request, role: "research" }, budget);
    await provider.generate(request, budget);
    expect(sdk.create.mock.calls[0]?.[1].timeout).toBe(5000);
    expect(sdk.create.mock.calls[1]?.[1].timeout).toBe(30000);
    budget.dispose();
  });
});

describe("replaceable research operations (injected fakes)", () => {
  it("projects only company/role, counts 2 searches and 3 reads, blocks excess", async () => {
    const search = vi
      .fn()
      .mockResolvedValue([
        { title: "Official", url: "https://openai.com/careers/", snippet: "Careers" },
      ]);
    const read = vi.fn().mockResolvedValue({
      url: "https://openai.com/careers/",
      text: "Careers",
      checkedAt: "2026-10-19T00:00:00Z",
    });
    const budget = new ExecutionBudget({ now: () => 0 });
    const tools = createResearchTools({ search: { search }, pages: { read } }, budget);
    const input = {
      company: "OpenAI",
      role: "Engineer",
      experience: "PRIVATE",
      question: "PRIVATE",
    };
    await Promise.all([tools.search(input), tools.search(input)]);
    await expect(tools.search(input)).rejects.toMatchObject({ code: "LIMIT_EXCEEDED" });
    expect(search).toHaveBeenCalledTimes(2);
    expect(search.mock.calls[0]?.[0]).toEqual({ company: "OpenAI", role: "Engineer" });
    await Promise.all(Array.from({ length: 3 }, () => tools.read("https://openai.com/careers/")));
    await expect(tools.read("https://openai.com/careers/")).rejects.toMatchObject({
      code: "LIMIT_EXCEEDED",
    });
    expect(read).toHaveBeenCalledTimes(3);
    expect(read.mock.calls[0]?.[1]).toMatchObject({
      signal: expect.any(AbortSignal),
      timeoutMs: expect.any(Number),
    });
    budget.dispose();
  });
  it("rejects invalid external results and unsupported URL schemes", async () => {
    const search = vi.fn().mockResolvedValue([{ url: "not a URL" }]);
    const read = vi.fn();
    const budget = new ExecutionBudget({ now: () => 0 });
    const tools = createResearchTools({ search: { search }, pages: { read } }, budget);
    await expect(tools.search({ company: "OpenAI", role: "Engineer" })).rejects.toBeInstanceOf(
      z.ZodError,
    );
    expect(() => tools.read("file:///etc/passwd")).toThrow(z.ZodError);
    expect(read).not.toHaveBeenCalled();
    budget.dispose();
  });
});

describe("role contract wire schemas", () => {
  it.each([
    ResearchModelOutputSchema,
    AnalysisResultSchema,
    WriterResultSchema,
    ReviewResultSchema,
  ])("converts role contract using installed OpenAI strict helper", (contract) => {
    expect(() => zodTextFormat(contract, "role")).not.toThrow();
  });
});

describe("research wire normalization", () => {
  it("omits null optional fields while preserving official required URL", () => {
    const source = {
      id: "s1",
      kind: "official",
      title: "Official",
      url: "https://openai.com/",
      excerpt: "Public",
      checkedAt: "2026-10-19T00:00:00Z",
      publishedAt: null,
      closingAt: null,
    };
    const output = ResearchModelOutputSchema.parse({
      resolvedCompany: "OpenAI",
      sources: [source, { ...source, id: "s2", kind: "user_provided", url: null }],
      companyFacts: [],
      jobRequirements: [],
      gaps: [],
    });
    const normalized = normalizeResearchModelOutput(output);
    expect(normalized.sources[0]).toHaveProperty("url", "https://openai.com/");
    expect(normalized.sources[0]).not.toHaveProperty("publishedAt");
    expect(normalized.sources[0]).not.toHaveProperty("closingAt");
    expect(normalized.sources[1]).not.toHaveProperty("url");
  });
});

describe("public provider input boundaries", () => {
  it("accepts full Unicode-code-point company/role limits", async () => {
    const search = vi.fn().mockResolvedValue([]);
    const budget = new ExecutionBudget({ now: () => 0 });
    const tools = createResearchTools({ search: { search }, pages: { read: vi.fn() } }, budget);
    const input = { company: "😀".repeat(120), role: "😀".repeat(160) };
    await tools.search(input);
    expect(search.mock.calls[0]?.[0]).toEqual(input);
    expect(() => tools.search({ ...input, company: input.company + "x" })).toThrow(z.ZodError);
    budget.dispose();
  });
  it.each(["ftp://openai.com/page", "javascript:alert(1)"])(
    "rejects non-HTTP provider URL %s",
    async (url) => {
      const search = vi.fn().mockResolvedValue([{ title: "bad", snippet: "bad", url }]);
      const read = vi
        .fn()
        .mockResolvedValue({ url, text: "bad", checkedAt: "2026-10-19T00:00:00Z" });
      const budget = new ExecutionBudget({ now: () => 0 });
      const tools = createResearchTools({ search: { search }, pages: { read } }, budget);
      await expect(tools.search({ company: "OpenAI", role: "Engineer" })).rejects.toBeInstanceOf(
        z.ZodError,
      );
      await expect(tools.read("https://openai.com/")).rejects.toBeInstanceOf(z.ZodError);
      budget.dispose();
    },
  );
});
