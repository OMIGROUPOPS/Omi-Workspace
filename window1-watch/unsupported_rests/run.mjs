// Execution harness only. Frozen selection; independently pinned authorized changes.
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import assert from 'node:assert/strict';
import readline from 'node:readline';
import {once} from 'node:events';
import {finished} from 'node:stream/promises';
import {createRequire} from 'node:module';
import {loadPolicy,validateDeterminism} from './tune_policy.mjs';
const root='C:/tmp/unsupported_rests_20260914',repo='C:/Users/omigr/omi-w1-face';
const require=createRequire(import.meta.url),builder=require(path.join(repo,'arb-executor/analysis/build_window1_v54_dual_belief.js'));
const selection=JSON.parse(fs.readFileSync(path.join(root,'SELECTION.json')));
const runInputs=JSON.parse(fs.readFileSync(path.join(root,'RUN_INPUTS.json'))).inputs;
assert.equal(builder.fileHash(path.join(root,'SELECTION.json')),'c8d0710d1aab2b43e9cb9d9e2813fc9c38f233e8e4941e8647d347aa0a6e4c7b');
const selected=new Set(selection.selected.map(r=>r.event_id));
const arg=(name,otherwise)=>{const i=process.argv.indexOf('--'+name);return i<0?otherwise:process.argv[i+1];};
const worker=Number(arg('worker','0')),workers=Number(arg('workers','1')),limit=Number(arg('limit','100'));
const onlyEvent=arg('event',null);
const phase=arg('phase','pass1'),policy=loadPolicy();
assert(['pass1','sample','full'].includes(phase));
selected.add('KXATPMATCH-26JUL12ALTGAS');
if(phase==='sample')for(const r of selection.selected)assert(fs.existsSync(path.join(root,'runs',r.event_id,'REPLAY_RECEIPT.json')),`Pass1 not complete: ${r.event_id}`);
if(onlyEvent)assert(selected.has(onlyEvent)||onlyEvent==='KXATPMATCH-26JUL12ALTGAS');
if(onlyEvent==='KXATPMATCH-26JUL12ALTGAS')selected.add(onlyEvent);
const output=path.join(root,'runs');fs.mkdirSync(output,{recursive:true});
const write=(file,value)=>{fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file+'.tmp',JSON.stringify(value,null,2)+'\n');fs.renameSync(file+'.tmp',file);};
const state=(value)=>write(path.join(root,onlyEvent?`WORKER_${onlyEvent}.json`:`WORKER_${worker}.json`),{...value,pid:process.pid,at:new Date().toISOString()});
function guard(){for(const [name,sha] of Object.entries(runInputs))assert.equal(builder.fileHash(path.join(repo,'arb-executor/analysis',name)),sha,`Source changed: ${name}`);}
guard();state({status:'LOADING'});
const foundation='C:/tmp/v54_altgas_extra_2dfb5b0a_20260902_run2';
const resourcePath=path.join(foundation,'SOURCE_RECEIPTS.json');
const prior=JSON.parse(fs.readFileSync(resourcePath)),resources=prior.resources;
for(const [kind,name] of [['foundation','FOUNDATION'],['future_low_return','FUTURE_LOW_RETURN']]){
  assert.equal(builder.fileHash(path.join(foundation,name+'_LIBRARY.jsonl.gz')),prior.corpus_sources[kind].index.sha256);
}
const corpus=await builder.loadCorpus('C:/tmp/v54-corpus-cache-recovered-20260826',repo,
 path.join(foundation,'FOUNDATION_LIBRARY.jsonl.gz'),path.join(foundation,'FOUNDATION_LIBRARY_RECEIPT.json'),
 path.join(foundation,'FUTURE_LOW_RETURN_LIBRARY.jsonl.gz'),path.join(foundation,'FUTURE_LOW_RETURN_LIBRARY_RECEIPT.json'));
assert(corpus.tick_library);assert(!corpus.macro_library,'Minute rebind refused');
const truth=builder.loadGroundTruth(repo);
const roster=onlyEvent?[{event_id:onlyEvent}]:phase==='sample'?policy.sample_events.map(event_id=>({event_id})):selection.selected;
const metas=roster.map(r=>{const t=truth.rows.find(t=>t.event_id===r.event_id);assert(t);return builder.targetMeta(t);});
const privateRoot='C:/Users/omigr/OMI-Window1-private';
const prints=await builder.loadTargetPrints(privateRoot,metas);
const lineage=await builder.loadLineage('C:/tmp/omi-v53-understanding-organ-20260819/.claude/window1_live_v4_replay/v54_walk5_repair_v6_20260821',metas.map(m=>m.event_id));
const binding={selection_sha256:builder.fileHash(path.join(root,'SELECTION.json')),inputs:runInputs,
 tick_library:corpus.sources.tick_library,foundation:corpus.foundation,future_low:corpus.future_low_return,
 ground_truth:truth.receipt,target_prints:prints.source,lineage:lineage.receipt,
 diagnostic_resources:builder.receipt(resourcePath),scope:'Native tick library, unchanged exported replayEvent; no edits or TARGETS mutation. Metadata roster read for selection, only selected tape rows execute. Historical diagnostic resource receipts reused, not a new remote census.'};
write(path.join(root,onlyEvent?`BINDING_${onlyEvent}.json`:`BINDING_${worker}.json`),binding);
const jobs=metas.filter((m,i)=>i%workers===worker&&m.event_id!==arg('skip-event',null)).slice(0,limit);
for(const meta of jobs){
 const event=meta.event_id;assert(selected.has(event));const dir=path.join(output,event);fs.mkdirSync(dir,{recursive:true});
 const doneFile=path.join(dir,'REPLAY_RECEIPT.json');
 const priorDone=fs.existsSync(doneFile)?JSON.parse(fs.readFileSync(doneFile)):null;
 if(priorDone){assert.deepEqual(priorDone.inputs,runInputs);assert.equal(builder.fileHash(priorDone.trace.path),priorDone.trace.sha256);
  const det=JSON.parse(fs.readFileSync(path.join(dir,'DETERMINISM_RECEIPT.json')));validateDeterminism(det,event,policy,{requireSample:false});
  if(phase==='pass1'||det.passes===2)continue;
 }
 const started=new Date().toISOString();let result,firstDigest,secondDigest;
 try{
  guard();const rows=[...builder.loadTicks(privateRoot,meta),...(prints.byEvent.get(event)??[])].filter(r=>!Number.isFinite(meta.bell_epoch)||r.timestamp_epoch<=meta.bell_epoch);
  assert(rows.every(r=>r.event_id===event),'Unselected replay input');
  write(path.join(dir,'INPUT_RECEIPT.json'),{event,meta,truth_status:truth.rows.find(r=>r.event_id===event).verified_span,rows:rows.length,prints:prints.byEvent.get(event)?.length??0,tapes:meta.leg_ids.map(leg=>builder.receipt(`${privateRoot}/fit-local/ticks/${event}-${leg}.csv.gz`))});
  const wantedPasses=phase==='pass1'?[1]:priorDone?[2]:[1,2];
  if(priorDone)firstDigest=JSON.parse(fs.readFileSync(path.join(dir,'PASS_1.json'))).digest;
  for(const pass of wantedPasses){
   const checkpoint=path.join(dir,'PASS_1.json');
   if(pass===1&&phase!=='pass1'&&fs.existsSync(checkpoint)){
    const saved=JSON.parse(fs.readFileSync(checkpoint));assert.equal(saved.event,event);assert.equal(saved.pass,1);
    firstDigest=saved.digest;console.log('REUSE_PASS_1',event,firstDigest.sha256);continue;
   }
   state({status:'REPLAYING',event,pass,started,rows:rows.length,worker,workers});console.log('REPLAY_START',event,pass,rows.length);
   const passStarted=new Date().toISOString(),passClock=performance.now();
   result=builder.replayEvent({meta,rows,corpus:corpus.rows,resources,lineage,smokeOnly:false});
   const digest=builder.digestReplay(result);console.log('REPLAY_PASS',event,pass,JSON.stringify(digest));
   const measured={started_at:passStarted,elapsed_seconds:(performance.now()-passClock)/1000,input_rows:rows.length,rss_bytes_after:process.memoryUsage().rss,process_peak_rss_bytes:process.resourceUsage().maxRSS*1024};
   console.log('REPLAY_PERFORMANCE',event,pass,JSON.stringify(measured));
   if(pass===1&&fs.existsSync(checkpoint))assert.deepEqual(JSON.parse(fs.readFileSync(checkpoint)).digest,digest,'Pass1 artifact rematerialization mismatch');
   else write(path.join(dir,`PASS_${pass}.json`),{event,pass,digest,inputs:runInputs,performance:measured,completed_at:new Date().toISOString()});
   if(pass===1){firstDigest=digest;if(phase!=='pass1'){result=null;global.gc?.();}}else{secondDigest=digest;assert.deepEqual(secondDigest,firstDigest,'Determinism mismatch');}
  }
  const determinism={event,first:firstDigest,second:secondDigest??null,all_byte_identical:secondDigest?true:null,passes:secondDigest?2:1,
   sample_member:policy.sample_events.includes(event),policy_label:policy.label,
   scope:secondDigest?'Two full independent replays agree for this game; this does not assert full-universe determinism.':'One full replay; determinism not tested for this game.'};
  if(priorDone){
   guard();write(path.join(dir,'DETERMINISM_RECEIPT.json'),determinism);
   write(doneFile,{...priorDone,determinism_x2:true,determinism_checked_at:new Date().toISOString(),determinism_policy_label:policy.label});
   console.log('SAMPLE_COMPLETE',event,firstDigest.sha256);continue;
  }
  state({status:'WRITING',event,started});const tracePath=path.join(dir,'REPAIR_FOUR_GAME_TRACE.jsonl.gz');
  const gzip=zlib.createGzip({level:6}),file=fs.createWriteStream(tracePath+'.tmp');gzip.pipe(file);const done=finished(file);const counts={};
  async function emit(row){counts[row.kind]=(counts[row.kind]??0)+1;if(!gzip.write(JSON.stringify(row)+'\n'))await once(gzip,'drain');}
  for(const stage of result.stage_reads)await emit({event_id:event,kind:'DECISION_STAGE',...stage});
  for(const row of result.rearm_attempts)await emit({kind:'REARM_ATTEMPT',...row});
  for(const row of result.floor_print_decision_instants)await emit({kind:'FLOOR_PRINT_DECISION_INSTANT',...row});
  for(const fill of result.fill_events)await emit({event_id:event,kind:'FILL_EVENT',fill_event_receipt:fill});
  for(const row of result.bid_accountability)await emit(row);
  gzip.end();await done;fs.renameSync(tracePath+'.tmp',tracePath);guard();
  const trace=builder.receipt(tracePath);
  write(path.join(dir,'DETERMINISM_RECEIPT.json'),determinism);
  write(path.join(dir,'FACE_RUN_PROVENANCE.json'),{event,os_sha256:runInputs['window1_v54_dual_belief_os.js'],os_sha256_after:runInputs['window1_v54_dual_belief_os.js'],trace_sha256:trace.sha256,bell_source_used:meta.bell_source_used,bell_alignment:meta.bell_alignment,source:binding});
  write(doneFile,{event,started,finished:new Date().toISOString(),inputs:runInputs,trace,counts,execution:result.execution,fills:result.fill_events,bell_source_used:meta.bell_source_used,bell_alignment:meta.bell_alignment,determinism_x2:!!secondDigest,determinism_policy_label:policy.label,trace_pass:secondDigest?2:1,load_tick_issues:builder.LOAD_TICK_ISSUES,sentence_action_weld:result.derivations.every(r=>r.sentence_action_assertion.equal),citation_weld:result.derivations.every(r=>r.citation_receipt_assertion.equal),pair_conservation:result.derivations.every(r=>r.pair_conservation.at_or_below_99)});
  console.log('GAME_COMPLETE',event,JSON.stringify({trace_bytes:trace.bytes,fills:result.fill_events.length}));
 }catch(error){write(path.join(dir,'FAILURE.json'),{event,at:new Date().toISOString(),error:error.stack,inputs:runInputs});state({status:'FAILED',event,error:error.message});throw error;}
 finally{result=null;global.gc?.();}
 if(fs.existsSync(path.join(root,'STOP_AT_GAME_BOUNDARY'))&&!process.argv.includes('--ignore-legacy-stop')){state({status:'CHECKPOINTED',event,worker,workers});console.log('STOP_AT_GAME_BOUNDARY',event);process.exit(0);}
}
state({status:'COMPLETE',jobs:jobs.length,worker,workers});guard();
