// Single-game acceptance runner. Uses real builder/OS files; never reconstructs an engine in memory.
"use strict";
const fs=require('fs'),path=require('path'),zlib=require('zlib'),assert=require('node:assert/strict');
const b=require('../arb-executor/analysis/build_window1_v54_dual_belief.js');
const repo=path.resolve(__dirname,'..');
const args=Object.fromEntries(process.argv.slice(2).reduce((out,v,i,a)=>v.startsWith('--')?[...out,[v.slice(2),a[i+1]]]:out,[]));
const event=args.event, baseline=path.resolve(args.baseline), output=path.resolve(args.out);
const sha=b.fileHash, canonical=b.canonical;
function firstDiff(a,b,p='$'){
 if(JSON.stringify(a)===JSON.stringify(b))return null;
 if(a&&b&&typeof a==='object'&&typeof b==='object'){
  for(const k of new Set([...Object.keys(a),...Object.keys(b)])){const d=firstDiff(a[k],b[k],`${p}.${k}`);if(d)return d}
 }
 return {path:p,actual:a,expected:b};
}
const noAccounting=value=>Array.isArray(value)?value.map(noAccounting):value&&typeof value==='object'
 ?Object.fromEntries(Object.entries(value).filter(([key])=>key!=='bid_accountability').map(([key,v])=>[key,noAccounting(v)])):value;
async function main(){
 assert.ok(event);assert.ok(!fs.existsSync(output),'fresh custody required');fs.mkdirSync(output,{recursive:true});
 const oldSource=JSON.parse(fs.readFileSync(path.join(baseline,'receipts/SOURCE_RECEIPTS.json')));
 const foundation='C:/tmp/omi-v54-four-game-trace-92a4d839-retry-20260901/.claude/window1_live_v4_replay/v54_classifier_floor_print_wake_20260826';
 console.log('ACCOUNTABLE loading unchanged library/bounds');
 const corpus=await b.loadCorpus('C:/tmp/v54-corpus-cache-recovered-20260826',repo,
  path.join(foundation,'FOUNDATION_LIBRARY.jsonl.gz'),path.join(foundation,'FOUNDATION_LIBRARY_RECEIPT.json'),
  path.join(foundation,'FUTURE_LOW_RETURN_LIBRARY.jsonl.gz'),path.join(foundation,'FUTURE_LOW_RETURN_LIBRARY_RECEIPT.json'));
 const truth=b.loadGroundTruth(repo);b.bindCorpusFloorTiming(corpus.rows,truth.rows);
 const meta=b.targetMeta(truth.rows.find(r=>r.event_id===event));
 const privateRoot='C:/Users/omigr/OMI-Window1-private';
 console.log('ACCOUNTABLE reading original print source order (sorted custody subset is not the pool ingestion order)');
 const printLoad=await b.loadTargetPrints(privateRoot,[meta]), prints=printLoad.byEvent.get(event),printFile=printLoad.source.path;
 assert.equal(printLoad.source.sha256,oldSource.target_prints.sha256,'private print source changed');
 const rows=[...b.loadTicks(privateRoot,meta),...prints].filter(r=>r.timestamp_epoch<=meta.bell_epoch);
 const lineage=await b.loadLineage('C:/tmp/omi-v53-understanding-organ-20260819/.claude/window1_live_v4_replay/v54_walk5_repair_v6_20260821',[event]);
 const old=[];const baselineTrace=path.join(baseline,'REPAIR_FOUR_GAME_TRACE.jsonl.gz');
 await b.streamJsonl(baselineTrace,r=>{if(r.event_id===event)old.push(r)});
 const frozenSource=JSON.parse(fs.readFileSync(path.join(baseline,'FACE_RUN_PROVENANCE.json')));
 assert.equal(sha(baselineTrace),frozenSource.trace_sha256);
 const printSubsetSha=printLoad.source.sha256;
 let firstDigest,finalRun;
 for(const pass of ['first','second']){
  console.log(`ACCOUNTABLE ${pass} actual builder replay ${rows.length} ticks`);
  let run=b.replayEvent({meta,rows,corpus:corpus.rows,resources:oldSource.resources,lineage});
  const stages=old.filter(r=>r.kind==='DECISION_STAGE').map(({event_id,kind,...stage})=>stage);
  assert.equal(run.stage_reads.length,stages.length,'decision stage count');
  for(let i=0;i<stages.length;i++){
   const actual={...run.stage_reads[i],derivations:run.stage_reads[i].derivations.map(({bid_accountability,...d})=>d)};
   if(b.shaBytes(canonical(actual))!==b.shaBytes(canonical(stages[i]))){
    const difference=firstDiff(actual,stages[i]);
    fs.writeFileSync(path.join(output,'STAGE_DIFFERENCE.json'),canonical({i,receipt:stages[i].receipt,difference}));
    throw new Error(`decision changed at stage ${i}: ${JSON.stringify(difference)}`);
   }
  }
  assert.deepEqual(run.fill_events,old.filter(r=>r.kind==='FILL_EVENT').map(r=>r.fill_event_receipt),'fills changed');
  const digest=b.digestReplay(run);
  if(firstDigest)assert.deepEqual(digest,firstDigest,'determinism');else firstDigest=digest;
  console.log(`ACCOUNTABLE ${pass} identical original decisions/fills; ${run.bid_accountability.length} accountability lines; digest ${digest.sha256}`);
  if(pass==='second')finalRun=run;
  else {run=null;if(global.gc)global.gc()}
 }
 const run=finalRun, events=run.bid_accountability, renewals=events.filter(r=>r.kind==='BID_RENEWAL'&&r.phase==='TICK');
 const records=events.filter(r=>r.kind==='BID_ASSUMPTION').map(r=>r.assumption), byId=new Map(records.map(a=>[a.assumption_id,a]));
 assert.equal(byId.size,records.length,'unique immutable records');
 for(const a of records){const {assumption_id,...payload}=a;assert.equal(b.shaBytes(JSON.stringify(payload)),assumption_id)}
 // Independent tick coverage: walk the unchanged decisions and fills in causal receipt order.
 let expected=0; const keys=new Set(renewals.map(r=>`${r.leg_id}|${r.tick_receipt}`));
 assert.equal(keys.size,renewals.length,'one renewal per resting leg per tape receipt');
 for(const leg of meta.leg_ids){
  const transitions=run.derivations.filter(d=>d.leg_id===leg).map(d=>({epoch:d.timestamp_epoch,receipt:d.receipt,target:d.action.target_cents}));
  const fill=run.fill_events.find(f=>f.context.leg_id===leg)?.context;
  for(const tick of run.ordered_rows){
   if(fill&&tick.timestamp_epoch>fill.fill_timestamp_epoch)continue;
   const prior=transitions.findLast(d=>d.epoch<tick.timestamp_epoch);
   if(Number.isInteger(prior?.target)){expected++;assert.ok(keys.has(`${leg}|${tick.receipt}`),`missing renewal ${leg} ${tick.receipt}`)}
  }
 }
 assert.equal(renewals.length,expected,'no phantom tick renewals');
 for(const r of renewals){assert.ok(byId.has(r.assumption_id));assert.ok(r.hold_reason);assert.equal(r.conduct_changed,false)}
 const moves=run.derivations.filter(d=>d.action.action==='REPRICE_REST');
 assert.ok(moves.every(d=>d.bid_accountability.supersession?.reason),'every reprice superseded');
 const lines=[...run.stage_reads.map(stage=>({event_id:event,kind:'DECISION_STAGE',...stage})),
  ...run.rearm_attempts.map(row=>({kind:'REARM_ATTEMPT',...row})),
  ...run.floor_print_decision_instants.map(row=>({kind:'FLOOR_PRINT_DECISION_INSTANT',...row})),
  ...run.fill_events.map(fill=>({event_id:event,kind:'FILL_EVENT',fill_event_receipt:fill})),...events];
 const tracePath=path.join(output,'REPAIR_FOUR_GAME_TRACE.jsonl.gz');
 fs.writeFileSync(tracePath,zlib.gzipSync(lines.map(JSON.stringify).join('\n')+'\n'));
 const provenance={event,os_sha256:sha(path.join(repo,'arb-executor/analysis/window1_v54_dual_belief_os.js')),
  functionable_sha256:sha(path.join(repo,'arb-executor/analysis/window1_v54_functionable_os.js')),
  builder_sha256:sha(path.join(repo,'arb-executor/analysis/build_window1_v54_dual_belief.js')),trace_sha256:sha(tracePath)};
 provenance.os_sha256_after=provenance.os_sha256;
 fs.writeFileSync(path.join(output,'FACE_RUN_PROVENANCE.json'),canonical(provenance));
 const firstPlace=run.derivations.find(d=>d.action.action==='PLACE_REST');
 const firstRenewal=renewals.find(r=>r.leg_id===firstPlace.leg_id);
 const firstMove=moves.find(d=>d.leg_id===firstPlace.leg_id);
 const receipt={label:'ACCOUNTABLE_BIDS_NO_CONDUCT_POOL_PRICING_CHANGE',provenance,baseline:{...frozenSource,trace_path:baselineTrace},
  inputs:{print_subset:{path:printFile,sha256:printSubsetSha,rows:prints.length},lineage:lineage.receipt,
   books:meta.leg_ids.map(id=>b.receipt(path.join(privateRoot,'fit-local/ticks',`${event}-${id}.csv.gz`)))},
  prior_art:{first_bind_receipt_sha256:sha(path.join(repo,'arb-executor/analysis/first_bind_role_experiment/ATP_MAIN_parallel/FIRST_BIND_RECEIPT.json')),
   ruling:'Astra SIGN (a): immutable promise, explicit renewal/supersession; first-bind pool filter REJECTED and not installed'},
  rules:{renewal:'After every book/print observation, including fill tick, before any new decision; frozen Q/X, carry exact last executed hold reason with provenance; no fresh pricing/STEP calculation at non-decision ticks.',
   promise:'Later positive-size own true print <= frozen Q by frozen X, within formation/bell. Creation-time print cannot fulfil; superseded outcomes retained. Directional support is not fulfilment; books do not refute a future print promise; deadline is observed on first receipt at/past X.',
   supersession:'REPRICE, changed Q/X or authors; exact role/own-print/authority/deadline deltas, plus explicit same-author forecast-level/deadline change. No invented role-change rationale.',
   postability:'Strict fresh-posting test price < ask with unlocked known book. Existing-rest <= ask and pair-cap observation separate, null if unknown; telemetry never alters conduct.'},
  validation:{original_decision_stages_identical:true,original_fills_identical:true,determinism_x2:firstDigest,
   expected_tick_renewals:expected,actual_tick_renewals:renewals.length,assumptions:records.length,supersessions:events.filter(r=>r.kind==='SUPERSESSION').length,
   reprices_linked:moves.length,engine_thresholds_added:[],bed_games_rerun:false},
  fills:run.fill_events.map(f=>f.context),execution:run.execution,
  excerpt:{first_assumption:firstPlace.bid_accountability.assumption,first_renewal:firstRenewal,first_reprice:firstMove?.bid_accountability},
  builder_functions_touched:['replayEvent / evaluateStage (receipt observer only)','digestReplay (new receipt stream included)','main (append new trace rows only)','exports (existing runner functions)']};
 fs.writeFileSync(path.join(output,'ACCOUNTABLE_BIDS_RECEIPT.json'),canonical(receipt));
 console.log(canonical({output,...provenance,validation:receipt.validation,fills:receipt.fills}));
}
main().catch(e=>{console.error(e);process.exitCode=1});
