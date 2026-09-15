// Execution scheduling only: no engine, pool, price, grade or tape transformation.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {loadPolicy,verifySample,RUN_ROOT} from './tune_policy.mjs';
const repo=path.resolve(import.meta.dirname,'../..');
const arg=(n,f)=>{const i=process.argv.indexOf('--'+n);return i<0?f:process.argv[i+1];};
const workers=Number(arg('workers','2')),waitPids=arg('wait-pids','').split(',').filter(Boolean).map(Number);
assert(Number.isInteger(workers)&&workers>0);assert(waitPids.every(Number.isInteger));
const policy=loadPolicy(),stateFile=path.join(RUN_ROOT,'SCHEDULE_STATE.json');
const alive=pid=>{try{process.kill(pid,0);return true;}catch(e){if(e.code==='ESRCH')return false;throw e;}};
if(fs.existsSync(stateFile)){const old=JSON.parse(fs.readFileSync(stateFile));assert(!alive(old.pid),'A coordinator is already alive');}
const children=new Map(),started=new Date().toISOString();let failure=null;
function state(phase,extra={}){
 const value={phase:failure?'FAILED':phase,pid:process.pid,workers,started,at:new Date().toISOString(),free_ram_bytes:os.freemem(),label:policy.label,children:[...children].map(([worker,child])=>({worker,pid:child.pid})),...extra,...(failure?{error:failure}:{})};
 fs.writeFileSync(stateFile+'.tmp',JSON.stringify(value,null,2)+'\n');fs.renameSync(stateFile+'.tmp',stateFile);
}
try{
 state('WAITING_FOR_LEGACY_GAME_CHECKPOINTS',{legacy_pids:waitPids});
 assert(!waitPids.length||waitPids.length===workers,'Keep the existing shard count until all live shards checkpoint');
 for(const phase of ['pass1','sample']){
  state(phase.toUpperCase());
  await Promise.all(Array.from({length:workers},async(_,worker)=>{
   if(phase==='pass1'&&waitPids[worker]){
    while(alive(waitPids[worker]))await new Promise(r=>setTimeout(r,5000));
    const f=path.join(RUN_ROOT,`WORKER_${worker}.json`);
    if(fs.existsSync(f))assert.notEqual(JSON.parse(fs.readFileSync(f)).status,'FAILED','Legacy worker failed');
   }
   return new Promise((resolve,reject)=>{
   const prefix=path.join(RUN_ROOT,`tune-${phase}-worker${worker}-${Date.now()}`);
   const out=fs.openSync(prefix+'.stdout.log','a'),err=fs.openSync(prefix+'.stderr.log','a');
   const child=spawn(process.execPath,['--expose-gc','window1-watch/unsupported_rests/run.mjs','--worker',String(worker),'--workers',String(workers),'--phase',phase,...(phase==='pass1'&&waitPids.length?['--ignore-legacy-stop']:[])],{cwd:repo,windowsHide:true,stdio:['ignore',out,err]});
   children.set(worker,child);fs.closeSync(out);fs.closeSync(err);state(phase.toUpperCase(),{latest_log_prefix:prefix});
   child.once('error',reject);
   child.once('exit',(code,signal)=>{children.delete(worker);state(phase.toUpperCase(),{last_exit:{worker,code,signal}});code===0?resolve():reject(Error(`Worker ${worker} ${phase} exited ${code}/${signal}`));});
   });
  }));
  const selection=JSON.parse(fs.readFileSync(path.join(RUN_ROOT,'SELECTION.json')));
  for(const r of selection.selected)assert(fs.existsSync(path.join(RUN_ROOT,'runs',r.event_id,'REPLAY_RECEIPT.json')),`Missing full first-pass artifact: ${r.event_id}`);
  const stop=path.join(RUN_ROOT,'STOP_AT_GAME_BOUNDARY');
  if(fs.existsSync(stop))fs.renameSync(stop,path.join(RUN_ROOT,`STOP_ACKNOWLEDGED_${Date.now()}.txt`));
 }
 const verification=verifySample(policy);
 fs.writeFileSync(path.join(RUN_ROOT,'TUNE_SAMPLE_VERIFICATION.json'),JSON.stringify(verification,null,2)+'\n');
 state('REPLAYS_COMPLETE',{sample:verification,status:'PASS',next:'Sequential exports and unchanged grades; audit; tune-labeled publication only. Full organ record still requires all-game two-pass proof.'});
}catch(error){
 failure=error.stack;
 state('FAILED',{error:error.stack});console.error(error.stack);process.exitCode=1;
 // Other live workers may finish their current checkpoint; do not kill their state.
}
