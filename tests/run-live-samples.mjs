import { execFileSync } from "node:child_process";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

if (!process.argv.includes("--confirm-live-model")) {
  throw new Error(
    "Configure a real server-side model first, then pass --confirm-live-model. This script never injects a mock.",
  );
}

const baseUrl = process.env.QA_BASE_URL || "http://127.0.0.1:3000";
const outputDir = resolve(process.env.QA_OUTPUT_DIR || "docs/qa-evidence/live-model");
const samples = JSON.parse(
  await readFile(new URL("./fixtures/live-samples.json", import.meta.url), "utf8"),
);
await mkdir(outputDir, { recursive: true });
const rows = [];
for (const sample of samples) {
  const { id, category, ...input } = sample;
  const raw = execFileSync(
    "curl",
    [
      "--silent",
      "--show-error",
      "-i",
      "--max-time",
      "70",
      "-X",
      "POST",
      `${baseUrl}/api/drafts`,
      "-H",
      "Content-Type: application/json",
      "--data-binary",
      "@-",
    ],
    { input: JSON.stringify(input), encoding: "utf8" },
  );
  await writeFile(resolve(outputDir, `${id}.http.txt`), raw);
  const bodyText = raw.slice(raw.indexOf("\r\n\r\n") + 4);
  const body = JSON.parse(bodyText);
  rows.push({
    id,
    category,
    status: body.status,
    code: body.code ?? null,
    characterCount:
      body.status === "ready" ? Array.from(body.draft.replace(/\r\n?/g, "\n")).length : null,
    generationCalls: body.generationCalls ?? null,
    experienceReflection: "AUTHOR_REVIEW_PENDING",
    questionFit: "AUTHOR_REVIEW_PENDING",
    inventedFacts: "AUTHOR_REVIEW_PENDING",
    artifact: `${id}.http.txt`,
  });
}
await writeFile(
  resolve(outputDir, "summary.json"),
  `${JSON.stringify({ executedAt: new Date().toISOString(), baseUrl, provider: "real server configuration; operator must confirm", rows }, null, 2)}\n`,
);
console.log(
  `Saved five real HTTP response artifacts to ${outputDir}. Human factual review remains pending.`,
);
