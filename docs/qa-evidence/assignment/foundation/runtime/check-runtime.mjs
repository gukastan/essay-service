import assert from 'node:assert/strict';
import { spawn, execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { createServer } from 'node:net';
import { resolve } from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';

const root = resolve(import.meta.dirname, '../../../../..');
const cwd = resolve(root, 'assignment');
const out = import.meta.dirname;
const temp = readFileSync(`${out}/temp-root.txt`, 'utf8').trim();
const env = {
  HOME: process.env.HOME, PATH: process.env.PATH,
  UV_CACHE_DIR: `${temp}/cache`, UV_PYTHON_INSTALL_DIR: `${temp}/python`,
  UV_PROJECT_ENVIRONMENT: `${temp}/venv`,
  LANGCHAIN_TRACING: 'true', LANGCHAIN_TRACING_V2: 'true', LANGSMITH_TRACING: 'true',
};
const hash = path => createHash('sha256').update(readFileSync(path)).digest('hex');
const databaseBefore = hash(`${cwd}/session.db`);
const allSources = readdirSync(cwd, {recursive: true})
  .filter(path => /\.(py|mjs|sh)$/.test(path) && !path.includes('__pycache__') && !path.startsWith('tests/') && !path.split('/').some(part => part.startsWith('.')));
const sourceHashes = Object.fromEntries(allSources.map(path => [path, hash(`${cwd}/${path}`)]));
const results = [];
const owned = [];

function start(name, port) {
  const child = spawn('bash', ['run.sh'], {cwd, env: {...env, ESSAY_PORT: String(port)}});
  const record = {name, pid: child.pid, output: '', child, exit: null};
  record.done = new Promise((resolveExit, rejectExit) => {
    child.on('error', rejectExit);
    child.on('exit', (code, signal) => {
      record.exit = {code, signal};
      resolveExit(record.exit);
    });
  });
  for (const stream of [child.stdout, child.stderr]) stream.on('data', chunk => {
    record.output += chunk.toString();
    writeFileSync(`${out}/${name}.log`, record.output);
  });
  owned.push(record);
  return record;
}

async function ready(record) {
  for (let attempt = 0; attempt < 300; attempt++) {
    const match = record.output.match(/Uvicorn running on http:\/\/127\.0\.0\.1:(\d+)/);
    if (match) return Number(match[1]);
    assert.equal(record.exit, null, `${record.name} exited: ${record.output}`);
    await delay(100);
  }
  assert.fail(`Startup timed out: ${record.output}`);
}

function descendants(parent) {
  const rows = execFileSync('ps', ['-axo', 'pid=,ppid=,command='], {encoding: 'utf8'})
    .trim().split('\n').map(line => {
      const [, pid, ppid, command] = line.match(/^\s*(\d+)\s+(\d+)\s+(.*)$/);
      return {pid: Number(pid), ppid: Number(ppid), command};
    });
  const family = [parent];
  for (let index = 0; index < family.length; index++) {
    family.push(...rows.filter(row => row.ppid === family[index]).map(row => row.pid));
  }
  return rows.filter(row => family.includes(row.pid));
}

async function stop(record, signal) {
  const family = descendants(record.pid);
  record.child.kill(signal);
  const exit = await Promise.race([record.done, delay(10000).then(() => { throw new Error('Stop timed out'); })]);
  assert(exit.code === 0 || exit.signal === signal, 'Unexpected shutdown exit');
  const observations = [];
  for (let attempt = 0; attempt < 30; attempt++) {
    const live = execFileSync('ps', ['-axo', 'pid='], {encoding: 'utf8'}).trim().split(/\s+/).map(Number);
    const remaining = family.filter(row => live.includes(row.pid));
    observations.push({attempt, remaining});
    if (remaining.length === 0) return {signal, exit, family, observations, allGone: true};
    await delay(100);
  }
  writeFileSync(`${out}/${record.name}-leak.json`, JSON.stringify({family, observations}, null, 2));
  assert.fail('Owned descendant remained after 3s reap window');
}

try {
  const first = start('sigterm', 0);
  const port = await ready(first);
  const base = `http://127.0.0.1:${port}`;
  const health = await fetch(`${base}/health`).then(response => response.json());
  const again = await fetch(`${base}/health`).then(response => response.json());
  assert.equal(health.status, 'ok');
  assert.equal(health.modelConfigured, false);
  assert.equal(health.mcpConnected, true);
  assert.equal(health.pipelineAvailable, false);
  assert.equal(health.instanceId, again.instanceId);
  assert.equal(health.creationCount, 1);
  const responses = [];
  for (const path of ['/api/drafts', '/chat', '/chat/stream']) {
    const response = await fetch(`${base}${path}`, path === '/api/drafts' ? {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({company: '시험 기업', role: '시험 직무', question: 'runtime-marker-question', experience: 'runtime-marker-experience'}),
    } : {});
    const body = await response.text();
    assert.equal(response.status, 404);
    assert(!body.includes('runtime-marker'));
    responses.push({path, status: response.status, body});
  }
  const family = descendants(first.pid);
  assert(family.some(row => row.command.includes('mcp_server.py')), 'Actual MCP child absent');
  const handles = execFileSync('lsof', ['-p', family.map(row => row.pid).join(',')], {encoding: 'utf8'});
  writeFileSync(`${out}/open-files.txt`, handles);
  assert(!handles.includes('session.db'), 'Foundation opened baseline SQLite DB');
  assert(!first.output.includes('runtime-marker'), 'Request input leaked to logs');
  results.push({scenario: 'foundation-start-and-control-input', invocation: 'ESSAY_PORT=0 bash run.sh', port, health, again, responses, family, sqliteOpen: false, requestLeak: false});
  results.push({scenario: 'graceful-sigterm', ...await stop(first, 'SIGTERM')});
  const second = start('sigint', 0);
  await ready(second);
  results.push({scenario: 'graceful-sigint', ...await stop(second, 'SIGINT')});
  const listener = createServer(socket => socket.end('sentinel'));
  await new Promise(resolveListen => listener.listen(0, '127.0.0.1', resolveListen));
  try {
    const collisionPort = listener.address().port;
    const collision = start('collision', collisionPort);
    const observed = [];
    const collisionDeadline = performance.now() + 30000;
    while (collision.exit === null && performance.now() < collisionDeadline) {
      observed.push(...descendants(collision.pid));
      await delay(50);
    }
    const exit = await Promise.race([collision.done, delay(30000).then(() => { throw new Error('Collision did not exit'); })]);
    assert(exit.code !== null && exit.code !== 0, 'Occupied port must fail');
    assert.equal(listener.listening, true);
    const live = execFileSync('ps', ['-axo', 'pid='], {encoding: 'utf8'}).trim().split(/\s+/).map(Number);
    assert(observed.every(row => !live.includes(row.pid)), 'Collision leaked owned descendant');
    assert(collision.output.includes('address already in use'));
    results.push({scenario: 'occupied-port', invocation: `ESSAY_PORT=${collisionPort} bash run.sh`, exit, sentinelStillListening: listener.listening, observedFamily: observed.filter((row, index) => observed.findIndex(other => other.pid === row.pid) === index), allGone: true});
  } finally {
    await new Promise(resolveClose => listener.close(resolveClose));
  }
  const invalid = start('invalid-port', '65536');
  const invalidExit = await invalid.done;
  assert.equal(invalidExit.code, 64);
  results.push({scenario: 'invalid-port', invocation: 'ESSAY_PORT=65536 bash run.sh', exit: invalidExit});
  assert.equal(hash(`${cwd}/session.db`), databaseBefore);
  assert.deepEqual(Object.fromEntries(allSources.map(path => [path, hash(`${cwd}/${path}`)])), sourceHashes, 'Sources changed during run; repeat after stable state');
  writeFileSync(`${out}/runtime-result.json`, JSON.stringify({passed: true, checkedAt: new Date().toISOString(), env: {...env, HOME: '<user-home>', PATH: '<inherited-path>'}, python: execFileSync(`${temp}/venv/bin/python`, ['--version'], {encoding:'utf8'}).trim(), uv: execFileSync('uv', ['--version'], {encoding:'utf8'}).trim(), lockHash: hash(`${cwd}/uv.lock`), sourceHashes, databaseHash: databaseBefore, databaseUnchanged: true, results}, null, 2));
  console.log(JSON.stringify({passed: true, scenarios: results.length}));
} finally {
  writeFileSync(`${out}/latest-observations.json`, JSON.stringify(results, null, 2));
  for (const record of owned.filter(record => record.exit === null)) {
    record.child.kill('SIGTERM');
    await record.done;
  }
}
