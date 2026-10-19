import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { parseEnv } from "node:util";
import OpenAI from "openai";

// Live probes are deliberately separate from the default unit-test command.
if (process.env.RUN_V2_PROVIDER_PROBE !== "1") {
  console.log("SKIPPED: set RUN_V2_PROVIDER_PROBE=1 for two billable compatibility requests");
  process.exit(0);
}
const env = parseEnv(readFileSync(".env.local", "utf8"));
const model = env.OPENAI_MODEL;
if (!model || !env.OPENAI_API_KEY) throw new Error("Missing model configuration");
const client = new OpenAI({ apiKey: env.OPENAI_API_KEY, timeout: 30000, maxRetries: 0 });
const records = [];
const combined = process.argv.includes("--combined");
const cases = [
  {
    name: "structured-output",
    input: 'Return {"ok":true}.',
    text: {
      format: {
        type: "json_schema",
        name: "compatibility",
        strict: true,
        schema: {
          type: "object",
          properties: { ok: { type: "boolean" } },
          required: ["ok"],
          additionalProperties: false,
        },
      },
    },
  },
  {
    name: "native-search-capability",
    input:
      "Find the official OpenAI careers page for software engineering roles. Make one search only. Return only the official careers URL; do not open pages.",
    tools: [
      {
        type: "web_search",
        search_context_size: "low",
        filters: { allowed_domains: ["openai.com"] },
      },
    ],
    tool_choice: "required",
    max_tool_calls: 1,
    include: ["web_search_call.action.sources"],
  },
];
if (combined)
  cases.splice(0, 2, {
    ...cases[1],
    name: "native-search-structured-output",
    text: {
      format: {
        type: "json_schema",
        name: "search_compatibility",
        strict: true,
        schema: {
          type: "object",
          properties: { url: { type: "string" } },
          required: ["url"],
          additionalProperties: false,
        },
      },
    },
  });
const evidencePath = combined
  ? ".omo/evidence/essay9-providers/live-combined.json"
  : ".omo/evidence/essay9-providers/live-probe.json";
mkdirSync(".omo/evidence/essay9-providers", { recursive: true });
for (const { name, ...params } of cases) {
  const started = Date.now();
  try {
    const response = await client.responses.create({
      model,
      reasoning: { effort: "low" },
      store: false,
      max_output_tokens: 400,
      ...params,
    });
    records.push({
      name,
      model,
      sdk: "7.39.0",
      startedAt: new Date(started).toISOString(),
      elapsedMs: Date.now() - started,
      status: response.status,
      usage: response.usage,
      outputText: response.output_text,
      actions: response.output
        .filter((item) => item.type === "web_search_call")
        .map((item) => ({ status: item.status, action: item.action })),
      retries: 0,
      maxToolCalls: params.max_tool_calls ?? 0,
    });
  } catch (error) {
    // Record only whitelisted metadata, never raw error bodies, headers or credentials.
    records.push({
      name,
      model,
      startedAt: new Date(started).toISOString(),
      elapsedMs: Date.now() - started,
      status: "failed",
      errorType: error instanceof Error ? error.name : "unknown",
      httpStatus: error instanceof OpenAI.APIError ? error.status : null,
      code: error instanceof OpenAI.APIError ? error.code : null,
      retries: 0,
    });
  }
  writeFileSync(evidencePath, JSON.stringify(records, null, 2) + "\n");
  console.log(JSON.stringify(records.at(-1)));
}
