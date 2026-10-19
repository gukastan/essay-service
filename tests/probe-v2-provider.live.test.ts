import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { parseEnv } from "node:util";
import OpenAI from "openai";
import { expect, it } from "vitest";
import { z } from "zod";
import { ExecutionBudget } from "@/server/workflow/budget";
import { createOpenAINativeResearchProvider } from "@/server/workflow/native-provider";

it.runIf(process.env["RUN_V2_NATIVE_ADAPTER_PROBE"] === "1")(
  "live production native adapter: one public company/role request",
  async () => {
    const env = parseEnv(readFileSync(".env.local", "utf8"));
    const config = z.object({ apiKey: z.string().min(1), model: z.string().min(1) }).parse({
      apiKey: env["OPENAI_API_KEY"],
      model: env["OPENAI_MODEL"],
    });
    const budget = new ExecutionBudget();
    const started = Date.now();
    const evidencePath = ".omo/evidence/essay9-providers/live-adapter.json";
    mkdirSync(".omo/evidence/essay9-providers", { recursive: true });
    try {
      const result = await createOpenAINativeResearchProvider(config).generate(
        {
          input: { company: "OpenAI", role: "Software Engineer" },
          schema: z.object({ officialCareersUrl: z.string() }),
        },
        budget,
      );
      writeFileSync(
        evidencePath,
        JSON.stringify(
          {
            status: "completed",
            startedAt: new Date(started).toISOString(),
            elapsedMs: Date.now() - started,
            model: config.model,
            reasoning: "low",
            sdk: "7.39.0",
            retries: 0,
            maxOutputTokens: 3000,
            result,
            budget: budget.snapshot(),
          },
          null,
          2,
        ),
      );
      expect(result.providerEvidence.toolCallsReported).toBeGreaterThan(0);
      expect(result.providerEvidence.toolCallsReported).toBeLessThanOrEqual(2);
      expect(result.providerEvidence.serverToolCallLimit).toBe(2);
      expect(result.value.officialCareersUrl).toMatch(/^https:\/\/(?:www\.)?openai\.com\//);
      expect(budget.snapshot()).toMatchObject({ modelCalls: 1, nativeToolCallsReserved: 2 });
    } catch (error) {
      if (error instanceof Error) {
        writeFileSync(
          `${evidencePath}.failure`,
          JSON.stringify(
            {
              status: "failed",
              errorType: error.name,
              httpStatus: error instanceof OpenAI.APIError ? error.status : null,
              elapsedMs: Date.now() - started,
              budget: budget.snapshot(),
            },
            null,
            2,
          ),
        );
      }
      throw new Error("Live provider verification failed; see sanitized evidence artifact");
    } finally {
      budget.dispose();
    }
  },
  35_000,
);
