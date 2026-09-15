import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {loadPolicy,validateDeterminism} from './tune_policy.mjs';
import {gunzipSync} from 'node:zlib';
const root='C:/tmp/unsupported_rests_20260914',oldRoot='C:/tmp/tune_expansion_20260914',repo='C:/Users/omigr/omi-w1-face',data=path.join(repo,'window1-watch/data');
const selection=JSON.parse(fs.readFileSync(path.join(root,'SELECTION.json')));
const inputs=JSON.parse(fs.readFileSync(path.join(root,'RUN_INPUTS.json'))).inputs;
const extract=JSON.parse(fs.readFileSync(path.join(oldRoot,'SELECTED_PRINTS_RECEIPT.json')));
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const write=(file,value)=>{fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file+'.tmp',JSON.stringify(value,null,2)+'\n');fs.renameSync(file+'.tmp',file);};
const skipEvents=new Set(process.argv.slice(2).filter(a=>a.startsWith('--skip-event=')).map(a=>a.slice('--skip-event='.length)));
const onlyEvent=process.argv.slice(2).find(a=>!a.startsWith('--'));
for(const event of skipEvents)assert(selection.selected.some(r=>r.event_id===event),'Skip outside frozen draw');
const policy=loadPolicy();
const pending=new Set((onlyEvent?[onlyEvent]:selection.selected.map(r=>r.event_id)).filter(event=>!skipEvents.has(event)));
while(pending.size){
 let work=false;
 for(const event of [...pending]){
  const dir=path.join(root,'runs',event),replayFile=path.join(dir,'REPLAY_RECEIPT.json'),done=path.join(dir,'FACE_COMPLETE.json');
  if(fs.existsSync(done)){
   const saved=JSON.parse(fs.readFileSync(done));
   assert.equal(hash(path.join(data,event+'.face.json')),saved.face_sha256,'Saved face changed: '+event);
   assert.equal(hash(path.join(data,event+'.grade.json')),saved.grade_sha256,'Saved grade changed: '+event);
   pending.delete(event);continue;
  }
  if(!fs.existsSync(replayFile))continue;
  work=true;const replay=JSON.parse(fs.readFileSync(replayFile)),input=JSON.parse(fs.readFileSync(path.join(dir,'INPUT_RECEIPT.json')));
  validateDeterminism(JSON.parse(fs.readFileSync(path.join(dir,'DETERMINISM_RECEIPT.json'))),event,policy,{requireSample:false});
  assert.deepEqual(replay.inputs,inputs);assert.equal(hash(replay.trace.path),replay.trace.sha256);
  const prints=extract.outputs.find(r=>r.event===event)??JSON.parse(fs.readFileSync(path.join(root,'ALT_PRINTS_RECEIPT.json')));assert.equal(hash(prints.path),prints.sha256);
  if(input.truth_status!=='OK'){
   write(path.join(dir,'FACE_UNAVAILABLE.json'),{event,status:'UNGRADABLE',reason:input.truth_status,trace_sha256:replay.trace.sha256,os_sha256:inputs['window1_v54_dual_belief_os.js'],rule:'No invented bell/span, grade, floor or offered denominator. Retained in the selected-100 denominator.'});
   pending.delete(event);console.log('FACE_UNAVAILABLE',event,input.truth_status);continue;
  }
  write(path.join(root,'FACE_STATE.json'),{status:'BUILDING',event,remaining:pending.size,pid:process.pid,at:new Date().toISOString()});
  const calls=[['window1-watch/build_face_data.mjs','--event',event,'--trace',replay.trace.path,'--tape-dir','C:/Users/omigr/OMI-Window1-private/fit-local/ticks','--prints',prints.path,'--out',path.join(data,event+'.face.json')],['window1-watch/build_grade.mjs','--event',event,'--prints',prints.path]];
  const oversized=path.join(dir,'FACE_OVERSIZE.json.gz');
  if(fs.existsSync(oversized)&&JSON.parse(gunzipSync(fs.readFileSync(oversized))).timeline)
    calls[0]=['window1-watch/unsupported_rests/resume_timeline_face.mjs',event,dir];
  for(const [i,args] of calls.entries()){
   const result=spawnSync(process.execPath,['--max-old-space-size=8192',...args],{cwd:repo,encoding:'utf8',maxBuffer:16*1024*1024,windowsHide:true});
   fs.writeFileSync(path.join(dir,`FACE_${i}.stdout.log`),result.stdout??'');fs.writeFileSync(path.join(dir,`FACE_${i}.stderr.log`),result.stderr??'');
   if(result.status!==0){write(path.join(dir,'FACE_FAILURE.json'),{event,status:result.status,error:result.error?.message??result.stderr});throw Error(`Face failed ${event}: ${result.stderr}`);}
  }
  const gradePath=path.join(data,event+'.grade.json'),grade=JSON.parse(fs.readFileSync(gradePath));
  assert.equal(grade.provenance.os_sha256,inputs['window1_v54_dual_belief_os.js']);assert.equal(grade.provenance.trace_sha256,replay.trace.sha256);
  write(done,{event,at:new Date().toISOString(),face_sha256:hash(path.join(data,event+'.face.json')),grade_sha256:hash(gradePath),letter:grade.LETTER.letter});
  console.log('FACE_COMPLETE',event,grade.LETTER.letter);pending.delete(event);
 }
 if(pending.size){
  const state=JSON.parse(fs.readFileSync(path.join(root,'WORKER_0.json')));
  if(state.status==='FAILED')throw Error('Replay worker failed: '+JSON.stringify(state));
  if(state.status==='COMPLETE'&&!work&&onlyEvent)throw Error('Replay ended with missing selected face: '+[...pending].join(','));
  await new Promise(resolve=>setTimeout(resolve,5000));
 }
}
write(path.join(root,'FACE_STATE.json'),{status:skipEvents.size?'COMPLETE_PARTIAL':'COMPLETE',games:onlyEvent?1:selection.selected.length-skipEvents.size,event:onlyEvent??null,skipped_pending_packaging:[...skipEvents],at:new Date().toISOString()});
