import assert from "node:assert/strict";
import { createServer } from "node:http";
import { mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { once } from "node:events";
import { loadOmowright } from "/Users/jay/.codex/plugins/cache/sisyphuslabs/omo/5.1.38/skills/browser/scripts/omowright.mjs";

const output = dirname(fileURLToPath(import.meta.url));
const source = resolve(output, "../../../../../assignment/web/foundation.mjs");
const fixtures = [
  { id: "hangul", input: "한글 문장", normalized: "한글 문장", count: 5, quote: "문장", start: 3, end: 5 },
  { id: "emoji-crlf", input: "가😀\r\n나", normalized: "가😀\n나", count: 4, quote: "😀\n", start: 1, end: 3 },
  { id: "combining-zwj-cr", input: "가e\u0301🧑‍💻\r끝", normalized: "가e\u0301🧑‍💻\n끝", count: 8, quote: "🧑‍💻", start: 3, end: 6 },
];
const html = [
  '<!doctype html><html lang="ko"><meta charset="utf-8"><title>ESSAY-19 Vue 기반 도구 검사</title>',
  '<style>body{font:16px system-ui;max-width:960px;margin:40px auto;color:#172438;background:#f6f8fc}textarea{width:90%;height:100px;font:20px system-ui}td,th{padding:14px;border-bottom:1px solid #cad4e3;text-align:left}pre{background:white;padding:20px}small{color:#526278}</style>',
  '<main id="app"><h1>Vue 문자·근거 도구 검사</h1><p>ESSAY-19 검증용 화면 · 자기소개서 제품 화면 아님</p>',
  '<small>Vue {{ version }} · LF 정규화 · Unicode 코드 포인트</small>',
  '<table><thead><tr><th>입력 사례</th><th>글자 수</th><th>근거 일치</th><th>판정</th></tr></thead><tbody><tr v-for="row in rows" :key="row.id"><td>{{row.id}}</td><td>{{row.count}}</td><td>{{row.evidence}}</td><td>{{row.passed ? "PASS" : "FAIL"}}</td></tr></tbody></table>',
  '<p><label for="text">반응형 입력</label></p><textarea id="text" v-model="text"></textarea><pre id="reactive">{{ JSON.stringify({normalized, count}, null, 2) }}</pre></main>',
  '<script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>',
  '<script type="module">import * as f from "/foundation.mjs";const fixtures=' + JSON.stringify(fixtures) + ';',
  'const rows=fixtures.map(c=>({id:c.id,normalized:f.normalizeLf(c.input),count:f.codePointLength(c.input),quote:f.codePointSlice(c.input,c.start,c.end),evidence:f.evidenceMatches(c.input,c),passed:f.normalizeLf(c.input)===c.normalized&&f.codePointLength(c.input)===c.count&&f.codePointSlice(c.input,c.start,c.end)===c.quote&&f.evidenceMatches(c.input,c)}));',
  'Vue.createApp({setup(){const text=Vue.ref("");return {text,rows,version:Vue.version,normalized:Vue.computed(()=>f.normalizeLf(text.value)),count:Vue.computed(()=>f.codePointLength(text.value))};}}).mount("#app");',
  'window.foundation=f;window.fixtureResults=rows;window.vueVersion=Vue.version;window.probe={state:"idle"};',
  'window.startProbe=()=>{window.probeController=new AbortController();window.probe={state:"pending"};f.requestJson("/hold",{signal:window.probeController.signal}).then(()=>window.probe={state:"unexpected-success"},e=>window.probe={state:"cancelled",name:e.name});};',
  'window.probeError=async()=>{try{await f.requestJson("/reject");return {success:true};}catch(e){return {success:false,name:e.name,status:e.status,message:e.message};}};</script></html>',
].join("\n");

let requests = 0;
let markHeld;
const held = new Promise(resolveHeld => { markHeld = resolveHeld; });
const server = createServer(async (req, res) => {
  if (req.url === "/foundation.mjs") {
    res.writeHead(200, { "content-type": "text/javascript" });
    res.end(await readFile(source));
  } else if (req.url === "/hold") {
    requests += 1;
    markHeld();
    res.on("close", () => res.end());
  } else if (req.url === "/reject") {
    res.writeHead(422, { "content-type": "application/json" });
    res.end('{"detail":"PRIVATE_TEST_BODY"}');
  } else {
    res.writeHead(200, { "content-type": "text/html; charset=utf-8" });
    res.end(html);
  }
});
let browser;
const checks = [];
const startedAt = new Date().toISOString();
const profile = await mkdtemp(join(tmpdir(), "essay19-browser-"));
let failure;
try {
  await mkdir(output, { recursive: true });
  await writeFile(join(output, "fixtures.json"), JSON.stringify(fixtures, null, 2) + "\n");
  server.listen(0, "127.0.0.1");
  await once(server, "listening");
  const address = server.address();
  assert.equal(typeof address, "object");
  const { omowright } = await loadOmowright();
  browser = await omowright.connectPipe({
    browserPath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    browserArgs: ["--headless", "--no-first-run", "--user-data-dir=" + profile],
    storageRoot: profile,
    dialogPolicy: { accept: false },
  });
  const page = await browser.newTab("http://127.0.0.1:" + address.port);
  const waitFor = async probe => {
    const deadline = Date.now() + 20_000;
    while (Date.now() < deadline) {
      const state = await probe();
      if (state) return state;
      await new Promise(resolveWait => setTimeout(resolveWait, 100));
    }
    throw new Error("Vue fixture readiness timeout");
  };
  const observed = await waitFor(() => page.evaluate(() => window.fixtureResults ?? null));
  assert.equal(observed.length, fixtures.length);
  for (const row of observed) assert.equal(row.passed, true);
  checks.push({ name: "actual Vue LF/codepoint/evidence fixtures", passed: true, rows: observed });
  await writeFile(join(output, "before-input.snapshot.json"), JSON.stringify(omowright.compactSnapshot(await page.snapshot()), null, 2));
  await page.locator("textarea").fill("가😀\n나");
  const reactive = await waitFor(() => page.evaluate(() => {
    const value = JSON.parse(document.querySelector("#reactive").innerText);
    return value.count === 4 ? value : null;
  }));
  assert.equal(reactive.normalized, "가😀\n나");
  checks.push({ name: "Vue reactive input uses codepoints", passed: true, observed: reactive });
  await writeFile(join(output, "vue-foundation.png"), await page.screenshot());
  await writeFile(join(output, "before-request.snapshot.json"), JSON.stringify(omowright.compactSnapshot(await page.snapshot()), null, 2));
  await page.evaluate(() => { window.startProbe(); });
  await Promise.race([held, new Promise((_, reject) => setTimeout(() => reject(new Error("request did not reach local server")), 10_000))]);
  await writeFile(join(output, "before-cancel.snapshot.json"), JSON.stringify(omowright.compactSnapshot(await page.snapshot()), null, 2));
  await page.evaluate(() => window.probeController.abort());
  const cancelled = await waitFor(() => page.evaluate(() => window.probe.state === "cancelled" ? window.probe : null));
  assert.equal(cancelled.name, "AbortError");
  assert.equal(requests, 1);
  checks.push({ name: "external abort stops one actual request without retry", passed: true, requests, observed: cancelled });
  await writeFile(join(output, "before-http-error.snapshot.json"), JSON.stringify(omowright.compactSnapshot(await page.snapshot()), null, 2));
  const error = await page.evaluate(() => window.probeError());
  assert.equal(error.status, 422);
  assert.equal(error.name, "RequestError");
  assert.ok(!error.message.includes("PRIVATE_TEST_BODY"));
  checks.push({ name: "HTTP error status with sanitized message", passed: true, observed: error });
  const config = await page.evaluate(() => ({ clientTimeoutMs: window.foundation.CLIENT_TIMEOUT_MS, requestTimeoutMs: window.foundation.REQUEST_TIMEOUT_MS, vueVersion: window.vueVersion }));
  assert.equal(config.clientTimeoutMs, 195_000);
  assert.equal(config.requestTimeoutMs, 180_000);
  checks.push({ name: "client/request deadline configuration", passed: true, observed: config });
} catch (error) {
  failure = { name: error.name, message: error.message };
  process.exitCode = 1;
} finally {
  if (browser) await browser.close();
  server.closeAllConnections();
  if (server.listening) await new Promise(resolveClose => server.close(resolveClose));
  await rm(profile, { recursive: true, force: true });
  await writeFile(join(output, "result.json"), JSON.stringify({ startedAt, finishedAt: new Date().toISOString(), outcome: failure ? "failed" : "passed", scope: "actual Vue foundation utility harness, not essay UI", checks, failure, ownedBrowserClosed: true, temporaryProfileRemoved: true, localServerClosed: true }, null, 2) + "\n");
  console.log(JSON.stringify({ outcome: failure ? "failed" : "passed", checks: checks.length, failure }));
}
