import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
export const RUN_ROOT='C:/tmp/unsupported_rests_20260914';
export const LABEL='pass 1 + 10-game determinism sample';
export const POLICY_FILE=path.join(RUN_ROOT,'TUNE_DETERMINISM_POLICY.json');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const read=p=>JSON.parse(fs.readFileSync(p));
export function makePolicy(selection,selectionSha){
 const mandatory=['KXATPMATCH-26JUL12ALTGAS','KXATPCHALLENGERMATCH-26JUL14GANZIN'];
 assert(selection.selected.some(r=>r.event_id===mandatory[1]));
 const seed=sha(selection.seed+'\nunsupported-rests/tune-determinism-v1');
 const ranked=selection.selected.map(r=>r.event_id).filter(e=>!mandatory.includes(e))
  .map(event=>({event,key:sha(seed+'\n'+event)})).sort((a,b)=>a.key<b.key?-1:a.key>b.key?1:a.event.localeCompare(b.event));
 return {schema:'TUNE_DETERMINISM_POLICY_V1',label:LABEL,selection_sha256:selectionSha,
  seed,seed_source:'SHA256(original frozen draw seed + newline + unsupported-rests/tune-determinism-v1)',
  method:'Mandatory ALT/GAS and GANZIN, then eight lowest SHA256(seed + newline + event) among the remaining frozen selected100. No outcomes, availability or completed-pass status used for selection.',
  sample_events:[...mandatory,...ranked.slice(0,8).map(r=>r.event)],mandatory_events:mandatory,
  selected_games:selection.selected.length,sample_size:10,sample_selected_games:9,extra_named_checks:1,
  order:'Finish pass1 and persist a complete trace for every selected game before starting missing sample pass2s. Existing verified full comparisons are retained and reused.',
  scope:'TUNE ITERATION ONLY; ALT/GAS remains outside the selected100 denominator; remaining704 unrun.',
  final_record_rule:'Full two-pass determinism on every selected game is still required to finalize an organ change for the record; a passing sample does not establish that.',
  final_organ_acceptance:'NOT_ESTABLISHED_BY_SAMPLE'};
}
export function loadPolicy(){
 const selectionBytes=fs.readFileSync(path.join(RUN_ROOT,'SELECTION.json'));
 const expected=makePolicy(JSON.parse(selectionBytes),sha(selectionBytes));
 const policy=read(POLICY_FILE);assert.deepEqual(policy,expected,'Frozen determinism sample changed');return policy;
}
export function validateDeterminism(det,event,policy,{requireSample=true}={}){
 assert.equal(det.event,event);assert(det.first?.sha256);assert([1,2].includes(det.passes));
 if(det.passes===2){assert.deepEqual(det.first,det.second);assert.equal(det.all_byte_identical,true);}
 else{assert.equal(det.second,null);assert.equal(det.all_byte_identical,null);}
 if(requireSample&&policy.sample_events.includes(event))assert.equal(det.passes,2,`Sample second pass pending: ${event}`);
 return {passes:det.passes,identical:det.passes===2?true:null,sampled:policy.sample_events.includes(event)};
}
export function verifySample(policy=loadPolicy()){
 const games=policy.sample_events.map(event=>{
  const dir=path.join(RUN_ROOT,'runs',event),det=read(path.join(dir,'DETERMINISM_RECEIPT.json'));
  validateDeterminism(det,event,policy);const r=read(path.join(dir,'REPLAY_RECEIPT.json'));
  assert.equal(r.determinism_x2,true);assert.equal(sha(fs.readFileSync(r.trace.path)),r.trace.sha256);
  const pins=read(path.join(RUN_ROOT,'RUN_INPUTS.json')).inputs;assert.deepEqual(r.inputs,pins);
  return {event,decision_sha256:det.first.sha256,trace_sha256:r.trace.sha256,passes:2,identical:true};
 });
 return {label:LABEL,policy_sha256:sha(fs.readFileSync(POLICY_FILE)),seed:policy.seed,sample_size:games.length,status:'PASS',games,full_universe_determinism:'NOT_ESTABLISHED_BY_SAMPLE'};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(path.resolve(process.argv[1])).href){
 if(process.argv.includes('--freeze')){
  const bytes=fs.readFileSync(path.join(RUN_ROOT,'SELECTION.json')),policy=makePolicy(JSON.parse(bytes),sha(bytes));
  if(fs.existsSync(POLICY_FILE))assert.deepEqual(read(POLICY_FILE),policy);
  else fs.writeFileSync(POLICY_FILE,JSON.stringify(policy,null,2)+'\n',{flag:'wx'});
  console.log(JSON.stringify(loadPolicy(),null,2));
 }else console.log(JSON.stringify(verifySample(),null,2));
}
