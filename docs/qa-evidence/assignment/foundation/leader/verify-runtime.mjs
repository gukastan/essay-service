import assert from 'node:assert/strict';
import { spawn, execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { resolve } from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';

const cwd = resolve(import.meta.dirname, '../../../../../assignment');
const out = import.meta.dirname;
const hash = path => createHash('sha256').update(readFileSync(path)).digest('hex');
const files = readdirSync(cwd, {recursive:true}).filter(path =>
  /\.(py|mjs|sh)$/.test(path) && !path.includes('__pycache__') &&
  !path.split('/').some(part => part.startsWith('.')));
files.push('pyproject.toml', 'uv.lock');
const hashes = () => Object.fromEntries(files.map(path => [path, hash(`${cwd}/${path}`)]));
const sourceHashes = hashes();
const startedAt = new Date().toISOString();
const child = spawn('bash', ['run.sh'], {cwd, env:{
  PATH:process.env.PATH, LANG:'en_US.UTF-8', ESSAY_PORT:'0',
  OPENAI_API_KEY:'', OPENAI_MODEL:'', LANGCHAIN_TRACING:'true',
  LANGCHAIN_TRACING_V2:'true', LANGSMITH_TRACING:'true',
}});
let output = '', exit = null;
const done = new Promise((resolveExit, reject) => {
  child.once('error', reject);
  child.once('exit', (code, signal) => {exit={code,signal}; resolveExit(exit);});
});
for (const stream of [child.stdout, child.stderr]) stream.on('data', chunk => {
  output += chunk.toString();
  writeFileSync(`${out}/runtime.log`, output);
});
const rows = () => execFileSync('ps', ['-axo','pid=,ppid=,command='], {encoding:'utf8'})
  .trim().split('\n').map(line => {
    const [,pid,ppid,command] = line.match(/^\s*(\d+)\s+(\d+)\s+(.*)$/);
    return {pid:Number(pid),ppid:Number(ppid),command};
  });
let family = [];
try {
  let port;
  for (let attempt=0; attempt<300; attempt++) {
    assert.equal(exit,null,'Launcher exited before readiness');
    const match = output.match(/Uvicorn running on http:\/\/127\.0\.0\.1:(\d+)/);
    if (match) {port=Number(match[1]); break;}
    await delay(100);
  }
  assert(port,'Readiness timeout');
  const base=`http://127.0.0.1:${port}`;
  const health=await fetch(`${base}/health`).then(r=>r.json());
  const again=await fetch(`${base}/health`).then(r=>r.json());
  assert.equal(health.status,'ok');
  assert.equal(health.modelConfigured,false);
  assert.equal(health.mcpConnected,true);
  assert.equal(health.pipelineAvailable,false);
  assert.equal(health.creationCount,1);
  assert.equal(health.instanceId,again.instanceId);
  const controls=[];
  for (const path of ['/api/drafts','/chat','/chat/stream']) {
    const response=await fetch(`${base}${path}`,path==='/chat/stream'?{}:{
      method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({company:'시험 기업',role:'시험 직무',question:'leader-marker',experience:'leader-marker'}),
    });
    assert.equal(response.status,404);
    controls.push({path,status:response.status});
  }
  const current=rows(), owned=[child.pid];
  for(let i=0;i<owned.length;i++) owned.push(...current.filter(r=>r.ppid===owned[i]).map(r=>r.pid));
  family=current.filter(r=>owned.includes(r.pid));
  assert(family.some(r=>r.command.includes('mcp_server.py')));
  assert(!output.includes('leader-marker'));
  child.kill('SIGTERM');
  await Promise.race([done,delay(10000).then(()=>{throw new Error('Shutdown timeout');})]);
  assert(exit.code===0 || exit.signal==='SIGTERM');
  let remaining;
  for(let i=0;i<30;i++) {
    const live=rows().map(r=>r.pid);
    remaining=family.filter(r=>live.includes(r.pid));
    if(!remaining.length) break;
    await delay(100);
  }
  assert.equal(remaining.length,0,'Owned descendant leaked');
  assert.deepEqual(hashes(),sourceHashes,'Source bytes changed during smoke');
  writeFileSync(`${out}/runtime-result.json`,JSON.stringify({
    passed:true,startedAt,finishedAt:new Date().toISOString(),
    invocation:'ESSAY_PORT=0 bash run.sh; empty key/model; tracing sentinels true',
    health,again,controls,family,exit,allOwnedPidsGone:true,sourceHashes,
    scope:'Final-source localhost foundation smoke, no model call or essay business pipeline',
  },null,2)+'\n');
  console.log(JSON.stringify({passed:true,health:true,controls:controls.length,allOwnedPidsGone:true}));
} finally {
  if(exit===null) {child.kill('SIGTERM'); await done;}
}
