// Sequential local artifact pipeline. Publication remains a separately reviewed step.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {RUN_ROOT,loadPolicy,verifySample} from './tune_policy.mjs';
const repo=path.resolve(import.meta.dirname,'../..'),stateFile=path.join(RUN_ROOT,'POSTPROCESS_STATE.json');
const read=f=>JSON.parse(fs.readFileSync(f));
const alive=pid=>{try{process.kill(pid,0);return true;}catch(e){if(e.code==='ESRCH')return false;throw e;}};
if(fs.existsSync(stateFile))assert(!alive(read(stateFile).pid),'Artifact coordinator already alive');
const policy=loadPolicy(),pins=read(path.join(RUN_ROOT,'RUN_INPUTS.json')).inputs;
function guard(){for(const [name,pin] of Object.entries(pins))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(repo,'arb-executor/analysis',name))).digest('hex'),pin);}
function state(phase,extra={}){fs.writeFileSync(stateFile+'.tmp',JSON.stringify({phase,pid:process.pid,at:new Date().toISOString(),label:policy.label,...extra},null,2)+'\n');fs.renameSync(stateFile+'.tmp',stateFile);}
try{
 guard();
 const waitFacePid=Number(process.argv.find(a=>a.startsWith('--wait-face-pid='))?.split('=')[1]);
 if(waitFacePid){state('WAITING_FOR_EXISTING_FACE_WORKER',{waiting_for_pid:waitFacePid});while(alive(waitFacePid))await new Promise(r=>setTimeout(r,5000));}
 state('WAITING_FOR_REPLAYS_AND_SAMPLE');
 while(true){const replay=read(path.join(RUN_ROOT,'SCHEDULE_STATE.json'));if(replay.phase==='FAILED')throw Error(replay.error);if(replay.phase==='REPLAYS_COMPLETE')break;assert(alive(replay.pid),'Replay coordinator exited before completion');await new Promise(r=>setTimeout(r,5000));}
 const sample=verifySample(policy);state('SAMPLE_VERIFIED',{sample});
 const phases=[
  ['FACES',['window1-watch/unsupported_rests/build_faces.mjs']],
  ['FINALIZE',['window1-watch/unsupported_rests/finalize.mjs']],
  ['FAULTS',['window1-watch/build_fault_taxonomy.mjs',RUN_ROOT,'C:/tmp/tune_expansion_20260914']],
  ['REPORT',['window1-watch/unsupported_rests/report.mjs']],
 ];
 const resumeFrom=process.argv.find(a=>a.startsWith('--resume-from='))?.split('=')[1];
 if(resumeFrom){
  assert.equal(resumeFrom,'FAULTS','Only the completed-finalize checkpoint is resumable here');
  const completed=read(path.join(repo,'window1-watch/data/tune-expansion/VERIFICATION.json'));
  assert.equal(completed.status,'PASS');
  assert.deepEqual(completed.inputs,pins);
  assert.equal(completed.selected,policy.selected_games);
  assert.equal(completed.selection_sha256,policy.selection_sha256);
  assert.equal(completed.determinism_sample.status,'PASS');
 }
 for(const [phase,args] of phases.slice(resumeFrom?phases.findIndex(([p])=>p===resumeFrom):0)){
  guard();const prefix=path.join(RUN_ROOT,'postprocess-'+phase.toLowerCase());
  const out=fs.openSync(prefix+'.stdout.log','a'),err=fs.openSync(prefix+'.stderr.log','a');
  const child=spawn(process.execPath,['--max-old-space-size=8192',...args],{cwd:repo,windowsHide:true,stdio:['ignore',out,err]});fs.closeSync(out);fs.closeSync(err);
  state(phase,{child_pid:child.pid,log_prefix:prefix});
  await new Promise((resolve,reject)=>{child.once('error',reject);child.once('exit',(code,signal)=>code===0?resolve():reject(Error(`${phase} failed: ${code}/${signal}; see ${prefix}.stderr.log`)));});
  guard();state(phase+'_COMPLETE',{log_prefix:prefix});
 }
 state('READY_FOR_REVIEW',{next:'Inspect before/after, named cards, ten worst and scoped audit; only then commit/push and deploy tune-labeled compact assets. No full-organ acceptance.'});
}catch(error){state('FAILED',{error:error.stack});console.error(error.stack);process.exitCode=1;}
