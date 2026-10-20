import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {mkdtempSync, mkdirSync, writeFileSync, readFileSync} from 'node:fs';
import {setTimeout as delay} from 'node:timers/promises';
import {resolve} from 'node:path';
const cwd=resolve(import.meta.dirname, '../../../../../assignment');
const temp=mkdtempSync('/tmp/essay19-install-signal.');
mkdirSync(`${temp}/bin`);
writeFileSync(`${temp}/bin/uv`, '#!/bin/bash\nprintf "%s" "$$" > "$INSTALL_PID_FILE"\nexec /bin/sleep 60\n', {mode:0o700});
const results=[];
for(const signal of ['SIGTERM','SIGINT']) {
 const pidFile=`${temp}/${signal}.pid`;
 const child=spawn('bash',['run.sh'],{cwd,env:{PATH:`${temp}/bin:/usr/bin:/bin`,INSTALL_PID_FILE:pidFile}});
 const done=new Promise(resolveExit=>child.on('exit',(code,exitSignal)=>resolveExit({code,signal:exitSignal})));
 let pid;
 for(let attempt=0;attempt<100;attempt++) {
  try { pid=Number(readFileSync(pidFile,'utf8')); break; }
  catch(error) { if(error.code!=='ENOENT') throw error; await delay(10); }
 }
 assert(pid>0);
 child.kill(signal);
 const exit=await done;
 assert.equal(exit.code,signal==='SIGTERM'?143:130);
 assert.throws(()=>process.kill(pid,0),{code:'ESRCH'});
 results.push({signal,invocation:'bash run.sh (controlled uv installer stub)',launcherPid:child.pid,installerPid:pid,exit,installerGone:true});
}
writeFileSync(`${temp}/bin/uv`,'#!/bin/bash\nexit 37\n',{mode:0o700});
const failure=spawn('bash',['run.sh'],{cwd,env:{PATH:`${temp}/bin:/usr/bin:/bin`}});
const failureExit=await new Promise(resolveExit=>failure.on('exit',(code,signal)=>resolveExit({code,signal})));
assert.equal(failureExit.code,37);
results.push({scenario:'installer-error-propagation',exit:failureExit});
writeFileSync(`${import.meta.dirname}/install-signals.json`,JSON.stringify({passed:true,results},null,2));
console.log(JSON.stringify({passed:true,scenarios:results.length}));
