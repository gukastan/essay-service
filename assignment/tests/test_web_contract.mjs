import assert from 'node:assert/strict';
import {normalize,count,parseResponse,safeUrl} from '../web_contract.js';
assert.equal(normalize('a\r\nb\rc'),'a\nb\nc');
assert.equal(count('😀\r\n가'),3);
for (const size of [800,801,1000,1001]) assert.equal(count('😀'.repeat(size)),size);
for (const url of ['javascript:alert(1)','data:text/html,hi','https://name:secret@example.com','https://example.com/a b']) assert.equal(safeUrl(url),false);
assert.equal(safeUrl('https://example.com/job'),true);
const requestId='5e7fd874-1d5a-4540-9cf4-37f9e842823d';
const input={experience:'😀\r\n행동'};
const ready={status:'ready',requestId,draft:'가'.repeat(900),characterCount:900,reviewSummary:'생성 당시 검토 통과',sources:[],evidence:{companyFacts:[],jobRequirements:[],claimMap:[],fitReasons:[],experienceEvidence:[{id:'e1',quote:'행동',start:2,end:4}]}};
assert.equal(parseResponse(ready,200,input),ready);
for(const mutate of [r=>{r.draft='가'.repeat(800)},r=>{r.status='unknown'},r=>{r.evidence.experienceEvidence[0].start=3},r=>{r.sources=[{id:'s',title:'title',excerpt:'x',kind:'official',checkedAt:'2026-10-20T00:00:00Z',url:'javascript:alert(1)'}]},r=>{r.evidence.fitReasons=null}]) {
 const value=structuredClone(ready);mutate(value);assert.throws(()=>parseResponse(value,200,input),/INVALID_RESPONSE/);
}
assert.throws(()=>parseResponse(ready,422,input),/INVALID_RESPONSE/);
assert.throws(()=>parseResponse({status:'error',requestId,code:'QUALITY_CHECK_FAILED',message:'failure'},200,input),/INVALID_RESPONSE/);
console.log('PASS: LF/code-point boundaries; safe links; malformed variants, evidence offsets, HTTP status rejected.');
