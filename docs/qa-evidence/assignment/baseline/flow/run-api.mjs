// Run: node run-api.mjs http://127.0.0.1:8100 fresh|warm [output.json]
// fresh requires an untouched process; only its first incident must retry once.
import { writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { randomUUID } from 'node:crypto';
import assert from 'node:assert/strict';

const [base = 'http://127.0.0.1:8100', mode = 'warm', output = 'api-results.json'] = process.argv.slice(2);
assert(['fresh', 'warm'].includes(mode));
assert(['127.0.0.1', 'localhost'].includes(new URL(base).hostname));
const started = new Date().toISOString();
const prefix = `essay18-${randomUUID()}`;
const records = [];
const checks = [];
const allowed = new Set(['type', 'route', 'node', 'pipeline', 'task_count', 'targets', 'removed_analysis_tasks', 'id', 'source', 'target', 'retries', 'round', 'is_sufficient', 'gap_task', 'reason', 'attempt', 'length', 'verdict', 'delta', 'reply']);
const cleanEvent = event => Object.fromEntries(Object.entries(event).filter(([key]) => allowed.has(key)));
function check(name, condition, observed) {
  checks.push({ name, passed: Boolean(condition), observed });
}
async function request(name, path, options = {}) {
  const begin = performance.now();
  const response = await fetch(base + path, { ...options, signal: AbortSignal.timeout(20000) });
  const body = await response.json();
  const safe = { ...body, events: body.events?.map(cleanEvent) };
  delete safe.prompt;
  delete safe.last_prompt;
  records.push({ name, request: { method: options.method ?? 'GET', path, body: options.body ? JSON.parse(options.body) : undefined }, status: response.status, elapsed_ms: +(performance.now() - begin).toFixed(2), body: safe });
  return { status: response.status, body };
}
async function chat(name, message, thread = name) {
  return request(name, '/chat', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ message, thread_id: `${prefix}-${thread}` }) });
}
async function stream(name, message) {
  const path = '/chat/stream?' + new URLSearchParams({ message, thread_id: `${prefix}-${name}` });
  const response = await fetch(base + path, { signal: AbortSignal.timeout(20000) });
  const begin = performance.now();
  const events = [];
  const decoder = new TextDecoder();
  let buffer = '';
  let doneCount = 0;
  assert(response.body);
  for await (const chunk of response.body) {
    buffer += decoder.decode(chunk, { stream: true }).replaceAll('\r\n', '\n');
    let boundary;
    while ((boundary = buffer.indexOf('\n\n')) >= 0) {
      const frame = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);
      const data = frame.split('\n').filter(line => line.startsWith('data:')).map(line => line.slice(5).trimStart()).join('\n');
      if (data === '[DONE]') { doneCount++; continue; }
      if (data) events.push({ received_ms: +(performance.now() - begin).toFixed(2), ...cleanEvent(JSON.parse(data)) });
    }
  }
  records.push({ name, request: { method: 'GET', path }, status: response.status, content_type: response.headers.get('content-type'), done_count: doneCount, events });
  check(`${name}: SSE framing`, response.status === 200 && response.headers.get('content-type')?.includes('text/event-stream') && doneCount === 1 && buffer.trim() === '', { doneCount, remainder_length: buffer.length });
  return events;
}
function incidentChecks(name, events, retries) {
  const types = events.map(event => event.type);
  const expected = ['RouteDecided','PlanCreated','GateApplied','TaskCompleted','TaskCompleted','ReplanCheck','TaskCompleted','ReplanCheck','AnalysisSkipped','DraftWritten','Validation','DraftWritten','Validation','Finalize'];
  check(`${name}: ordered graph events`, JSON.stringify(types.filter(type => !['AnswerToken', 'FinalAnswer'].includes(type))) === JSON.stringify(expected), types);
  const tasks = events.filter(event => event.type === 'TaskCompleted');
  check(`${name}: two distinct monitoring tasks then runbook`, tasks.length === 3 && tasks[0].source === 'monitoring' && tasks[1].source === 'monitoring' && new Set(tasks.slice(0, 2).map(event => event.target)).size === 2 && tasks[2].source === 'runbook', tasks);
  check(`${name}: gate removes contradictory analysis`, events.find(event => event.type === 'GateApplied')?.removed_analysis_tasks === 1 && !types.includes('AnalysisCompleted'), events.find(event => event.type === 'GateApplied'));
  const replan = events.filter(event => event.type === 'ReplanCheck');
  check(`${name}: one replan`, replan.length === 2 && replan[0].is_sufficient === false && replan[0].round === 0 && replan[1].is_sufficient === true && replan[1].round === 1, replan);
  check(`${name}: expected retry total`, tasks.reduce((total, event) => total + event.retries, 0) === retries, tasks.map(event => event.retries));
  const validation = events.filter(event => event.type === 'Validation');
  check(`${name}: reject then rewrite acceptance`, validation.length === 2 && validation[0].attempt === 1 && validation[0].verdict === '불합격' && validation[1].attempt === 2 && validation[1].verdict === '합격', validation);
}
try {
  const health = await request('health-before', '/health');
  check('fake v2 process', health.status === 200 && health.body.llm_backend === 'fake' && health.body.supervisor_version === 'v2' && health.body.creation_count === 1, health.body);
  assert(checks.at(-1).passed, 'Refusing requests against non-fake/non-v2 runtime');
  const incident = await chat('incident-first', 'auth-service 장애를 진단해줘');
  incidentChecks('incident-first', incident.body.events, mode === 'fresh' ? 1 : 0);
  check('incident metadata', incident.body.metadata.route === 'incident' && incident.body.metadata.task_count === 3 && incident.body.metadata.gate_removed === 1 && incident.body.metadata.replan_rounds === 1 && incident.body.metadata.validation_attempts === 2 && incident.body.metadata.retry_count === (mode === 'fresh' ? 1 : 0), incident.body.metadata);
  const greeting = await chat('general-chat', '안녕, 너는 누구야?');
  check('general chat direct route', greeting.body.metadata.route === 'chat' && JSON.stringify(greeting.body.events.map(event => event.type)) === JSON.stringify(['RouteDecided', 'Finalize']) && greeting.body.metadata.task_count === 0, greeting.body.events);
  const chatSSE = await stream('chat-sse', '안녕, 너는 누구야?');
  check('chat SSE sequence', JSON.stringify(chatSSE.map(event => event.type)) === JSON.stringify(['RouteDecided','AnswerToken','Finalize','FinalAnswer']), chatSSE.map(event => event.type));
  const incidentSSE = await stream('incident-sse', 'web-01 CPU 급증, auth-service 커넥션 풀도 같이 확인해줘');
  incidentChecks('incident-sse', incidentSSE, 0);
  const tokens = incidentSSE.filter(event => event.type === 'AnswerToken');
  check('SSE rewrite chunks correlate with drafts', tokens.length === 2 && tokens[0].attempt === 1 && tokens[1].attempt === 2 && tokens[1].delta === incidentSSE.at(-1).reply, tokens.map(event => ({ attempt: event.attempt, length: [...event.delta].length })));
  check('SSE observed nodes', ['route','plan','gate','research','replan_check','analysis','write','validate','finalize'].every(node => incidentSSE.some(event => event.node === node)), [...new Set(incidentSSE.map(event => event.node).filter(Boolean))]);
  await chat('session-set', '제 이름은 민수입니다', 'memory');
  const recall = await chat('session-recall', '제 이름이 뭐였죠?', 'memory');
  check('same-process session recall', recall.body.reply.includes('민수'), recall.body.reply);
  const invalid = await request('missing-required-message', '/chat', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ thread_id: `${prefix}-invalid` }) });
  check('missing message HTTP 422', invalid.status === 422 && invalid.body.detail.some(error => error.loc.includes('message') && error.type === 'missing'), invalid.body);
  const fallback = await chat('documented-fake-limitation', 'cache-service 메모리 사용률이 계속 올라가고 있어요');
  check('documented fake routing limitation observed', fallback.body.metadata.route === 'chat', fallback.body.metadata.route);
  const after = await request('health-after', '/health');
  const version = await request('version', '/version');
  check('bundle reused across requests', after.body.instance_id === health.body.instance_id && after.body.creation_count === 1 && records.filter(record => record.body?.metadata).every(record => record.body.metadata.instance_id === health.body.instance_id), { before: health.body.instance_id, after: after.body.instance_id, creation_count: after.body.creation_count });
  check('version v2', version.body.supervisor_version === 'v2', version.body);
} finally {
  const report = { started_at: started, completed_at: new Date().toISOString(), invocation: process.argv, runtime: process.version, base_url: base, mode, model_mode: 'fake (mock)', monitoring_mode: 'JSON fixture with random jitter (mock)', protocol: 'real FastAPI/LangGraph/MCP; SSE callbacks do not prove upstream model token streaming', full_prompts_persisted: false, checks, records };
  await writeFile(resolve(output), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({ output: resolve(output), passed: checks.filter(check => check.passed).length, failed: checks.filter(check => !check.passed).map(check => check.name) }));
}
process.exitCode = checks.every(check => check.passed) ? 0 : 1;
