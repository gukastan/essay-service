import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const model = vi.hoisted(() => ({ generateModelOutput: vi.fn() }));
vi.mock("@/server/model", () => ({ ...model, MODEL_TIMEOUT_MS: 30_000 }));

import { POST } from "@/app/api/drafts/route";

const validInput = {
  company: "테스트 기업",
  role: "서비스 기획",
  question: "문제 해결 경험을 설명해 주세요.",
  experience: "동아리 일정 안내문을 작성하고 피드백을 받아 수정했습니다.",
} as const;

function request(body: unknown): Request {
  return new Request("http://localhost/api/drafts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

function draft(length: number) {
  const text = "가".repeat(length);
  expect(Array.from(text.replace(/\r\n?/g, "\n"))).toHaveLength(length);
  return { status: "draft", draft: text };
}

beforeEach(() => {
  vi.stubEnv("OPENAI_API_KEY", "qa-not-a-real-key");
  vi.stubEnv("OPENAI_MODEL", "qa-model");
  model.generateModelOutput.mockReset();
});

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllEnvs();
});

describe("actual POST route: validation before model invocation", () => {
  for (const field of ["company", "role", "question", "experience"] as const) {
    it.each([undefined, "", " \n\t ", 123, null, [], {}].map((value) => ({ value })))(
      `rejects ${field}=%j with no model calls`,
      async ({ value }) => {
        const response = await POST(request({ ...validInput, [field]: value }));
        expect(response.status).toBe(400);
        expect(await response.json()).toMatchObject({
          status: "error",
          code: "INVALID_INPUT",
          fieldErrors: { [field]: expect.any(String) },
        });
        expect(model.generateModelOutput).not.toHaveBeenCalled();
      },
    );
  }

  it.each([null, [], "text", 42].map((body) => ({ body })))(
    "rejects non-object body %j",
    async ({ body }) => {
      const response = await POST(request(body));
      expect(response.status).toBe(400);
      expect(await response.json()).toMatchObject({ status: "error", code: "INVALID_INPUT" });
      expect(model.generateModelOutput).not.toHaveBeenCalled();
    },
  );

  it("rejects malformed JSON without model calls", async () => {
    const response = await POST(
      new Request("http://localhost/api/drafts", { method: "POST", body: "{" }),
    );
    expect(response.status).toBe(400);
    expect(await response.json()).toMatchObject({ status: "error", code: "INVALID_INPUT" });
    expect(model.generateModelOutput).not.toHaveBeenCalled();
  });

  it("returns CONFIG_ERROR with no key and zero model calls", async () => {
    vi.stubEnv("OPENAI_API_KEY", "");
    const response = await POST(request(validInput));
    expect(response.status).toBe(500);
    expect(await response.json()).toMatchObject({ status: "error", code: "CONFIG_ERROR" });
    expect(model.generateModelOutput).not.toHaveBeenCalled();
  });
});

describe("actual POST route: length and bounded rewriting", () => {
  it.each([801, 1000])("accepts %i characters in exactly one call", async (length) => {
    const output = draft(length);
    model.generateModelOutput.mockResolvedValue(output);
    const response = await POST(request(validInput));
    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({
      status: "ready",
      draft: output.draft,
      characterCount: length,
      generationCalls: 1,
    });
    expect(model.generateModelOutput).toHaveBeenCalledTimes(1);
  });

  it.each([800, 1001])("rewrites %i characters once with original context", async (length) => {
    const initial = draft(length);
    const final = draft(801);
    model.generateModelOutput.mockResolvedValueOnce(initial).mockResolvedValueOnce(final);
    const response = await POST(request(validInput));
    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({
      status: "ready",
      draft: final.draft,
      characterCount: 801,
      generationCalls: 2,
    });
    expect(model.generateModelOutput).toHaveBeenCalledTimes(2);
    expect(model.generateModelOutput.mock.calls[1]?.[0]).toMatchObject({
      input: validInput,
      rewrite: { draft: initial.draft, characterCount: length },
    });
  });

  it.each([800, 1001])("rejects second invalid length %i without a third call", async (length) => {
    model.generateModelOutput.mockResolvedValue(draft(length));
    const response = await POST(request(validInput));
    expect(response.status).toBe(422);
    const body = await response.json();
    expect(body).toMatchObject({ status: "error", code: "LENGTH_RETRY_EXHAUSTED" });
    expect(body).not.toHaveProperty("draft");
    expect(model.generateModelOutput).toHaveBeenCalledTimes(2);
  });

  it("normalizes CRLF and CR, preserves spaces and counts Unicode code points", async () => {
    const raw = `${"가".repeat(789)}\r\n\r \n😀 👨‍👩‍👧‍👦`;
    const normalized = raw.replace(/\r\n?/g, "\n");
    const expected = Array.from(normalized).length;
    expect(expected).toBe(802);
    model.generateModelOutput.mockResolvedValue({ status: "draft", draft: raw });
    const response = await POST(request(validInput));
    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({
      status: "ready",
      draft: normalized,
      characterCount: expected,
      generationCalls: 1,
    });
    expect(model.generateModelOutput).toHaveBeenCalledTimes(1);
  });

  it.each([1, 2])("ends needs_input on call %i without a length rewrite", async (calls) => {
    if (calls === 2) model.generateModelOutput.mockResolvedValueOnce(draft(800));
    model.generateModelOutput.mockResolvedValueOnce({
      status: "needs_input",
      message: "본인의 역할을 보완해 주세요.",
    });
    const response = await POST(request(validInput));
    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({
      status: "needs_input",
      message: "본인의 역할을 보완해 주세요.",
      generationCalls: calls,
    });
    expect(model.generateModelOutput).toHaveBeenCalledTimes(calls);
  });
});

describe("actual POST route: errors never trigger retries", () => {
  it.each([1, 2])("stops provider failure on call %i and hides internal details", async (calls) => {
    if (calls === 2) model.generateModelOutput.mockResolvedValueOnce(draft(800));
    model.generateModelOutput.mockRejectedValueOnce(
      new Error("secret-provider-detail qa-not-a-real-key"),
    );
    const response = await POST(request(validInput));
    expect(response.status).toBe(502);
    const body = await response.json();
    expect(body).toMatchObject({ status: "error", code: "MODEL_ERROR" });
    expect(JSON.stringify(body)).not.toMatch(/secret-provider-detail|qa-not-a-real-key/);
    expect(model.generateModelOutput).toHaveBeenCalledTimes(calls);
  });

  it.each([
    null,
    {},
    { status: "draft" },
    { status: "draft", draft: 123 },
    { status: "needs_input", message: "" },
    { status: "surprise", draft: "가".repeat(801) },
  ])("rejects malformed model output %j without rewrite", async (output) => {
    model.generateModelOutput.mockResolvedValue(output);
    const response = await POST(request(validInput));
    expect(response.status).toBe(502);
    expect(await response.json()).toMatchObject({ status: "error", code: "MODEL_ERROR" });
    expect(model.generateModelOutput).toHaveBeenCalledTimes(1);
  });

  it.each([1, 2])(
    "cancels call %i at 30 seconds and performs no additional calls",
    async (calls) => {
      vi.useFakeTimers();
      if (calls === 2) model.generateModelOutput.mockResolvedValueOnce(draft(800));
      const started = Promise.withResolvers<AbortSignal>();
      model.generateModelOutput.mockImplementationOnce((_request: unknown, signal: AbortSignal) => {
        started.resolve(signal);
        return new Promise<never>(() => {});
      });
      const pending = POST(request(validInput));
      const signal = await started.promise;
      expect(signal.aborted).toBe(false);
      await vi.advanceTimersByTimeAsync(29_999);
      expect(signal.aborted).toBe(false);
      await vi.advanceTimersByTimeAsync(1);
      const response = await pending;
      expect(signal.aborted).toBe(true);
      expect(response.status).toBe(504);
      expect(await response.json()).toMatchObject({ status: "error", code: "MODEL_TIMEOUT" });
      expect(model.generateModelOutput).toHaveBeenCalledTimes(calls);
    },
  );
});
