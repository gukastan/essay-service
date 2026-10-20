import assert from "node:assert/strict";
import { mkdtemp, mkdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { loadOmowright } from "/Users/jay/.codex/plugins/cache/sisyphuslabs/omo/5.1.38/skills/browser/scripts/omowright.mjs";

const output = dirname(fileURLToPath(import.meta.url));
const baseUrl = process.env.BASELINE_UI_URL ?? "http://127.0.0.1:8600";
const { omowright } = await loadOmowright();
const profile = await mkdtemp(join(tmpdir(), "essay18-browser-"));
const startedAt = new Date().toISOString();
const checks = [];
let browser;
let outcome = "failed";
let failure;

try {
  await mkdir(output, { recursive: true });
  browser = await omowright.connectPipe({
    browserPath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    browserArgs: ["--headless", "--no-first-run", `--user-data-dir=${profile}`],
    storageRoot: profile,
    dialogPolicy: { accept: false },
  });
  const page = await browser.newTab(baseUrl);
  await omowright.emulate(page, "desktop-1440");
  const ui = () => page.evaluate(() => ({
    title: document.title,
    header: document.querySelector("header")?.innerText ?? "",
    inputPresent: Boolean(document.querySelector("form input")),
    inputValue: document.querySelector("form input")?.value ?? "",
    buttonDisabled: document.querySelector("button[type=submit]")?.disabled,
    userMessages: [...document.querySelectorAll(".row.user .bubble")].map(e => e.innerText),
    agentMessages: [...document.querySelectorAll(".row.agent .bubble")].map(e => e.innerText),
    steps: [...document.querySelectorAll(".steps .step")].map(e => e.innerText),
    promptPanels: document.querySelectorAll("details.prompt-box").length,
    expandedPromptPanels: document.querySelectorAll("details.prompt-box[open]").length,
  }));
  const waitForUi = async (predicate, label) => {
    const deadline = Date.now() + 25_000;
    while (Date.now() < deadline) {
      const state = await ui();
      if (predicate(state)) return state;
      await new Promise(resolve => setTimeout(resolve, 150));
    }
    throw new Error(`UI timeout: ${label}`);
  };
  const observe = async name => {
    const snapshot = omowright.compactSnapshot(await page.snapshot());
    await writeFile(join(output, `${name}.snapshot.json`), JSON.stringify(snapshot, null, 2));
  };
  const initial = await waitForUi(s => s.inputPresent && s.header.includes("fake"), "Vue and fake health");
  assert.equal(initial.title, "운영 에이전트 채팅 (Vue)");
  await observe("01-initial");
  await writeFile(join(output, "01-initial.png"), await page.screenshot());
  checks.push({ name: "initial Vue render and health", passed: true, state: initial });

  await observe("02-before-empty-submit");
  await page.locator("button[type=submit]").click();
  const empty = await ui();
  assert.equal(empty.userMessages.length, 0);
  checks.push({ name: "empty input does not add conversation", passed: true });

  await observe("03-before-chat");
  await page.locator("form input").fill("안녕하세요");
  await observe("04-before-chat-submit");
  await page.locator("button[type=submit]").click();
  const chat = await waitForUi(s => !s.buttonDisabled && s.agentMessages.length >= 1, "chat final answer");
  assert.equal(chat.userMessages.at(-1), "안녕하세요");
  assert.ok(chat.agentMessages.at(-1).length > 0);
  await observe("05-chat-result");
  await writeFile(join(output, "05-chat-result.png"), await page.screenshot());
  checks.push({ name: "general chat via Vue SSE", passed: true, state: chat });

  const incidentInput = "auth-service 로그인 지연 장애 원인 진단해줘";
  await observe("06-before-incident");
  await page.locator("form input").fill(incidentInput);
  await observe("07-before-incident-submit");
  await page.locator("button[type=submit]").click();
  const pending = await waitForUi(s => s.buttonDisabled, "pending submit lock");
  await writeFile(join(output, "08-incident-pending.png"), await page.screenshot());
  checks.push({ name: "pending submit button disabled", passed: true, buttonDisabled: pending.buttonDisabled });
  const incident = await waitForUi(s =>
    !s.buttonDisabled && s.steps.includes("최종 답변 완성") &&
    s.agentMessages.length > chat.agentMessages.length, "incident final answer");
  assert.equal(incident.userMessages.at(-1), incidentInput);
  assert.ok(incident.steps.some(s => s.includes("계획 수립")));
  assert.ok(incident.steps.some(s => s.includes("모니터링 지표 확인")));
  assert.ok(incident.steps.some(s => s.includes("대응 매뉴얼")));
  assert.ok(incident.steps.includes("검수 반려 → 다시 작성"));
  assert.ok(incident.steps.includes("검수 통과"));
  assert.ok(incident.agentMessages.at(-1).includes("1)"));
  assert.equal(incident.expandedPromptPanels, 0);
  await observe("09-incident-result");
  await writeFile(join(output, "09-incident-result.png"), await page.screenshot());
  checks.push({ name: "incident progress, rewrite and final answer", passed: true, state: incident });
  outcome = "passed";
} catch (error) {
  failure = error instanceof Error ? { name: error.name, message: error.message } : { message: String(error) };
  process.exitCode = 1;
} finally {
  if (browser) await browser.close();
  await rm(profile, { recursive: true, force: true });
  const result = {
    startedAt,
    finishedAt: new Date().toISOString(),
    baseUrl,
    outcome,
    inference: "original FakeLLM; no OpenAI requests",
    transport: "real Vue, FastAPI proxy, SSE, LangGraph and MCP",
    limitations: [
      "Original header calls fake mode 실모델; this is inherited misleading wording.",
      "JSON monitoring is fixture telemetry, not a live monitored system.",
      "Closed prompt panels were not opened; full prompts are not captured.",
    ],
    checks,
    failure,
  };
  await writeFile(join(output, "result.json"), `${JSON.stringify(result, null, 2)}\n`);
  console.log(JSON.stringify({ outcome, checks: checks.length, failure }));
}
