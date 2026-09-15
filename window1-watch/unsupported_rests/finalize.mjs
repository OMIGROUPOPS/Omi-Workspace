import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import crypto from 'node:crypto';
import readline from 'node:readline';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {readGradeRulers} from 'file:///C:/Users/omigr/omi-w1-face/window1-watch/grade_rulers.mjs';
import {unpackFace} from 'file:///C:/Users/omigr/omi-w1-face/window1-watch/face_encoding.mjs';
import {writeGameIndex} from 'file:///C:/Users/omigr/omi-w1-face/window1-watch/face_contract.mjs';
import {appendHistory} from 'file:///C:/Users/omigr/omi-w1-face/window1-watch/build_grade.mjs';
import {readGradePrints} from 'file:///C:/Users/omigr/omi-w1-face/window1-watch/grade_prints.mjs';
import {loadPolicy,validateDeterminism,verifySample} from './tune_policy.mjs';
import {readBidDetails} from '../bid_card_details.mjs';
import {compactCompletedFaces} from './compact_completed_faces.mjs';
const root='C:/tmp/unsupported_rests_20260914',oldRoot='C:/tmp/tune_expansion_20260914',repo='C:/Users/omigr/omi-w1-face',data=path.join(repo,'window1-watch/data'),report=path.join(data,'tune-expansion');
const require=createRequire(import.meta.url),b=require(path.join(repo,'arb-executor/analysis/build_window1_v54_dual_belief.js'));
const selection=JSON.parse(fs.readFileSync(path.join(root,'SELECTION.json'))),selectionSha=b.fileHash(path.join(root,'SELECTION.json'));
assert.equal(selectionSha,'c8d0710d1aab2b43e9cb9d9e2813fc9c38f233e8e4941e8647d347aa0a6e4c7b');
const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const write=(file,obj)=>{fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(obj,null,2)+'\n');};
const runInputs=JSON.parse(fs.readFileSync(path.join(root,'RUN_INPUTS.json'))).inputs;
const facts=[];const verification=[];
const policy=loadPolicy(),sampleVerification=verifySample(policy);
await compactCompletedFaces([...selection.selected.map(r=>r.event_id),'KXATPMATCH-26JUL12ALTGAS'],data,root,oldRoot);
function reachAudit(face,leg,prints){
 const events=(face.render?.bid_actions??[]).filter(a=>a.leg===leg).sort((a,b)=>a.timestamp_epoch-b.timestamp_epoch||a.trace_row-b.trace_row);
 const intervals=[];let active=null;
 for(const a of events){
  if(active){active.end_epoch=a.timestamp_epoch;intervals.push(active);active=null;}
  if(!['FILL','CANCEL'].includes(a.kind)&&Number.isFinite(a.new_cents))active={level:a.new_cents,start_epoch:a.timestamp_epoch,start_receipt:a.receipt,end_epoch:null};
 }
 if(active){active.end_epoch=face.truth.bell_epoch;intervals.push(active);}
 const crossings=[],boundary=[];
 for(const interval of intervals){
  for(const p of prints){
   if(p.epoch<face.truth.span_start_epoch||p.epoch>=face.truth.span_end_epoch||p.epoch>=face.truth.bell_epoch||p.price>interval.level)continue;
   if(p.epoch>interval.start_epoch&&p.epoch<interval.end_epoch)crossings.push({print:p,interval});
   else if(p.epoch===interval.start_epoch||p.epoch===interval.end_epoch)boundary.push({print:p,interval});
  }
 }
 return {rest_intervals:intervals.length,strictly_interior_crossings:crossings.length,first_interior_crossing:crossings[0]??null,same_timestamp_boundary_crossings:boundary.length,first_boundary_crossing:boundary[0]??null,rule:'Read-only diagnostic: positive-size accepted grade prints at/below a recorded resting level, strictly after action time and before next action/corrected bell. Equal action timestamps are unresolved here, never credited. Exact replay and grade remain authoritative.'};
}
for(const selected of selection.selected){
 const event=selected.event_id,dir=path.join(root,'runs',event),r=JSON.parse(fs.readFileSync(path.join(dir,'REPLAY_RECEIPT.json'))),input=JSON.parse(fs.readFileSync(path.join(dir,'INPUT_RECEIPT.json'))),det=JSON.parse(fs.readFileSync(path.join(dir,'DETERMINISM_RECEIPT.json')));
 assert.deepEqual(r.inputs,runInputs);assert.equal(b.fileHash(r.trace.path),r.trace.sha256);validateDeterminism(det,event,policy);
 const sentences=[],actions=[],stageSummaries=[],traceEvents=new Set();let traceRows=0;
 for await(const line of readline.createInterface({input:fs.createReadStream(r.trace.path).pipe(zlib.createGunzip()),crlfDelay:Infinity})){
  if(!line)continue;const row=JSON.parse(line);traceRows++;if(row.event_id)traceEvents.add(row.event_id);
  if(row.kind!=='DECISION_STAGE')continue;
  stageSummaries.push({kind:row.kind,receipt:row.receipt,timestamp_epoch:row.timestamp_epoch,legs:Object.fromEntries(Object.entries(row.layers?.micro?.context?.beliefs??{}).map(([leg,belief])=>[leg,{status:belief.status??null,plain_sentence:belief.plain_sentence??null}]))});
  for(const [leg,belief] of Object.entries(row.layers?.micro?.context?.beliefs??{}))sentences.push({event,receipt:row.receipt,timestamp_epoch:row.timestamp_epoch,leg,status:belief.status??null,P:belief.belief_price_cents??null,Q:belief.predicted_cents??null,X:belief.predicted_minutes_to_bell??null,q_author:belief.q_author??null,x_author:belief.x_author??null,plain_sentence:belief.plain_sentence??null});
  for(const d of row.derivations??[])actions.push({receipt:row.receipt,timestamp_epoch:row.timestamp_epoch,leg:d.leg_id,action:d.action?.action??null,target_cents:d.action?.target_cents??null,reason:d.action?.reason??null});
 }
 assert([...traceEvents].every(id=>id===event),'Other event in trace');
 assert(traceRows>0||Object.values(r.counts).every(n=>n===0),'Unexpected empty trace');
 write(path.join(report,'games',event+'.sentences.json'),{event,trace_sha256:r.trace.sha256,rows:sentences});
 let face,grade;
 if(input.truth_status!=='OK'){
  const reason=input.truth_status==='UNKNOWN'?'No verified replay span in the corrected truth table. A floor, offer and performance grade cannot be asserted.':'No verified replay span: the filed bell is before formation ends. A floor, offer and performance grade cannot be asserted.';
  face={version:2,availability:{status:'UNGRADABLE',reason,ruler_status:input.truth_status},provenance:{event_id:event,os_sha256:runInputs['window1_v54_dual_belief_os.js'],trace_sha256:r.trace.sha256,trace_path:r.trace.path,cohort:'TUNE_SAMPLE',selection_sha256:selectionSha},category:selected.category,legs:selected.legs,bell:{timestamp_epoch:null,source:input.meta.bell_source},os:stageSummaries,first_tick:null};
  const rulers=readGradeRulers(repo,event,face);face.truth=rulers.effective_truth;face.rulers=rulers;
  const bytes=JSON.stringify(face)+'\n';fs.writeFileSync(path.join(data,event+'.face.json'),bytes);fs.writeFileSync(path.join(data,event+'.face.json.gz'),zlib.gzipSync(bytes));
  const legs=Object.fromEntries(selected.legs.map(l=>[l,{filled:r.execution.legs[l]?.credited??false,cents:r.execution.legs[l]?.entry_cents??null,valid_span_fill:'STORE SILENT',reason:input.truth_status}]));
  grade={event,status:'UNGRADABLE',timestamp:r.finished,provenance:{...face.provenance,face_sha256:hash(bytes),truth_commit:selection.source.table_commit,truth_corrections_commit:selection.source.correction_commit},SENTENCE:{receipts_total:r.counts.DECISION_STAGE,sentences_url:`/data/tune-expansion/games/${event}.sentences.json`},MACRO:{status:'STORE SILENT',reason},MICRO:{status:'STORE SILENT',reason},HANDS:{actions,execution:r.execution},OUTCOME:{legs,pair_completed:r.execution.completed,valid_pair_completed:'STORE SILENT',pair_sum:null,captured_cents:null,best_capturable_cents:null,capture_ratio:null},LETTER:{letter:'STORE SILENT',governing_section:reason},display:{letter:'—',label:'UNGRADABLE',governing:reason,ruler_line:reason,sections:['MACRO','MICRO','TRADE','PAIR'].map(name=>({name,mark:'!',line:'— · '+reason,hover_lines:[reason]})),diagnostic_hover_lines:[reason]},RULER_COLUMNS:rulers};
  const previousGrade=path.join(data,event+'.grade.json');
  if(fs.existsSync(previousGrade)&&JSON.parse(fs.readFileSync(previousGrade)).provenance?.face_sha256===hash(bytes))grade=JSON.parse(fs.readFileSync(previousGrade));
  else grade=(await appendHistory(data,grade,r.finished)).snapshot;
 }else{
  const complete=JSON.parse(fs.readFileSync(path.join(dir,'FACE_COMPLETE.json')));
  assert.equal(b.fileHash(path.join(data,event+'.face.json')),complete.face_sha256);assert.equal(b.fileHash(path.join(data,event+'.grade.json')),complete.grade_sha256);
  face=readBidDetails(unpackFace(JSON.parse(fs.readFileSync(path.join(data,event+'.face.json')))),data);grade=JSON.parse(fs.readFileSync(path.join(data,event+'.grade.json')));
 }
 assert.equal(grade.provenance.trace_sha256,r.trace.sha256);assert.equal(grade.provenance.os_sha256,runInputs['window1_v54_dual_belief_os.js']);
 const o=grade.OUTCOME,valid=Object.values(o.legs).filter(l=>l.valid_span_fill===true).length,known=input.truth_status==='OK';
 const positive=known?await readGradePrints(path.join(oldRoot,'selected_prints',event+'.jsonl'),[{event,legs:selected.legs}]):null;
 const fillWitnesses=r.fills.map(fill=>{const c=fill.context,witness=positive?.[event]?.legs[c.leg_id]?.find(p=>p.receipt===fill.captured_at_receipt);return {leg:c.leg_id,receipt:fill.captured_at_receipt,positive_size_witness:!!witness,print_cents:witness?.price??null,rest_cents:c.entry_cents,at_or_below_rest:witness?witness.price<=c.entry_cents:null};});
 const misses=selected.legs.filter(l=>o.legs[l]?.valid_span_fill!==true).map(leg=>{
  const last=actions.filter(a=>a.leg===leg).at(-1),execution=r.execution.legs[leg];
  const floor=face.truth?.legs?.[leg]?.floor_cents,rest=execution?.standing_target_cents;
  const reach=known?reachAudit(face,leg,positive[event].legs[leg]):null;
  const reason=!known?`No verified span (${input.truth_status})`:o.legs[leg]?.reason??(!reach.rest_intervals?`No resting bid; final decision ${last?.action??'not stored'} (${last?.reason??'reason not stored'})`:reach.strictly_interior_crossings?`Positive-size crossing inside a reconstructed rest interval was not credited; exact receipt ordering needs review`:reach.same_timestamp_boundary_crossings?`No strictly later crossing inside a rest interval; crossing at an action timestamp needs receipt-order review`:`No later positive-size print reached a standing bid before the corrected bell`);
  return {leg,reason,last_action:last??null,final_rest_cents:rest??null,recorded_floor_cents:floor??null,reach_audit:reach,scope:'Stored execution plus explicit read-only crossing diagnostic; no invented intent or queue priority.'};
 });
 const fact={event,category:selected.category,status:known?'GRADED':'UNGRADABLE',letter:grade.LETTER.letter,section_lines:grade.display.sections,governing:grade.LETTER.governing_section,raw_engine_fills:r.fills.map(f=>f.context),raw_engine_completed:r.execution.completed,valid_fills:known?valid:null,completed:known?o.valid_pair_completed===true:null,one_sided:known?valid===1:null,pair_sum:o.pair_sum,captured_cents:o.captured_cents,offered_cents:o.best_capturable_cents,capture_ratio:o.capture_ratio,one_sided_reason:known&&valid===1?misses.map(m=>`${m.leg}: ${m.reason}`).join(' | '):null,missing_sides:misses,trace_sha256:r.trace.sha256,grade_sha256:b.fileHash(path.join(data,event+'.grade.json')),grade_url:`/data/${event}.grade.json`,face_url:`/data/${event}.face.json`,sentences_url:`/data/tune-expansion/games/${event}.sentences.json`};
 fact.fault=grade.LETTER.hard_failures?.length?grade.LETTER.hard_failures.join('; '):!known?`No verified span: ${input.truth_status}`:!fact.completed?misses.map(m=>`${m.leg}: ${m.reason}`).join(' | '):grade.display.sections.filter(s=>grade.LETTER.governing_section.includes(s.name)).map(s=>`${s.name}: ${s.line}`).join(' | ');
 fact.fill_witnesses=fillWitnesses;
 fact.hard_failures=grade.LETTER.hard_failures??[];
 fact.offer_issue=Number.isFinite(fact.offered_cents)?null:{reason:face.truth?.pair?.reason??input.truth_status,recorded_floors:Object.fromEntries(selected.legs.map(l=>[l,face.truth?.legs?.[l]?.floor_cents??null])),original_row_floor_sum:grade.RULER_COLUMNS?.original_table?.floor_sum_cents??null,note:face.truth?.pair?.reason==='FAVORITE/UNDERDOG NOT IDENTIFIABLE FROM TABLE OPENS'?'Both recorded floors exist. Equal opening prices prevent the current grader from identifying favorite/underdog and adding the floors. No grader repair or denominator substitution in this run.':'Missing offer retained from the unchanged grade; no unavailable floor or span invented.'};
 facts.push(fact);write(path.join(report,'games',event+'.json'),fact);
 verification.push({event,trace:r.trace,trace_rows:traceRows,passes:det.passes,sample_member:policy.sample_events.includes(event),decision_sha256:det.first.sha256,identical:det.all_byte_identical,face_sha256:b.fileHash(path.join(data,event+'.face.json')),grade_sha256:fact.grade_sha256,status:fact.status});
}
assert.equal(facts.length,100);assert.equal(new Set(facts.map(f=>f.event)).size,100);
const completedDirs=fs.readdirSync(path.join(root,'runs')).filter(event=>fs.existsSync(path.join(root,'runs',event,'REPLAY_RECEIPT.json')));
assert.deepEqual(completedDirs.filter(e=>e!=='KXATPMATCH-26JUL12ALTGAS').sort(),selection.selected.map(r=>r.event_id).sort(),'Extra or missing game executed');
const binding=JSON.parse(fs.readFileSync(path.join(root,'BINDING_0.json'))),extract=JSON.parse(fs.readFileSync(path.join(oldRoot,'SELECTED_PRINTS_RECEIPT.json')));
assert.equal(binding.target_prints.sha256,extract.source.sha256,'Replay and grading print sources differ');
for(const [file,sha] of Object.entries(runInputs))assert.equal(b.fileHash(path.join(repo,'arb-executor/analysis',file)),sha);
const gradedSnapshots=facts.filter(r=>r.status==='GRADED').map(r=>JSON.parse(fs.readFileSync(path.join(data,r.event+'.grade.json'))));
const rubricHashes=[...new Set(gradedSnapshots.map(g=>g.provenance.rubric_sha256))];
const gradeContractHashes=[...new Set(gradedSnapshots.map(g=>g.provenance.grade_contract_sha256))];
assert.equal(rubricHashes.length,1,'Rubric changed within run');assert.equal(gradeContractHashes.length,1,'Grade contract changed within run');
function summarize(rows,category){
 const eligible=rows.filter(r=>Number.isFinite(r.offered_cents)&&r.offered_cents>0),known=rows.filter(r=>r.status==='GRADED'),complete=rows.filter(r=>r.completed===true),one=rows.filter(r=>r.one_sided===true);
 const captureKnown=eligible.filter(r=>Number.isFinite(r.captured_cents));
 const captured=captureKnown.reduce((a,r)=>a+r.captured_cents,0),offered=eligible.reduce((a,r)=>a+r.offered_cents,0);
 return {category,selected:rows.length,graded:known.length,ungradable:rows.length-known.length,letters:rows.reduce((a,r)=>(a[r.status==='UNGRADABLE'?'UNGRADABLE':r.letter]=(a[r.status==='UNGRADABLE'?'UNGRADABLE':r.letter]??0)+1,a),{}),completed:complete.length,completion_per_selected:complete.length/rows.length,one_sided:one.length,one_sided_per_selected:one.length/rows.length,unfilled_known:known.filter(r=>r.valid_fills===0).length,offered_games:eligible.length,no_positive_offer:rows.filter(r=>Number.isFinite(r.offered_cents)&&r.offered_cents<=0).length,offer_unknown:rows.filter(r=>!Number.isFinite(r.offered_cents)).length,capture_unknown_on_offered:eligible.length-captureKnown.length,captured_cents:captured,offered_cents:offered,captured_per_game_offered:eligible.length&&captureKnown.length===eligible.length?captured/eligible.length:null,captured_per_selected_lower_bound:captured/rows.length,capture_share:offered>0&&captureKnown.length===eligible.length?captured/offered:null,completion_per_game_offered:eligible.length?eligible.filter(r=>r.completed).length/eligible.length:null};
}
const severity={F:0,D:1,C:2,B:3,A:4,'NOT OFFERED':5,'STORE SILENT':6};
const worst=facts.filter(r=>r.status==='GRADED'&&Number.isFinite(r.offered_cents)&&r.offered_cents>0).sort((a,b)=>(severity[a.letter]??6)-(severity[b.letter]??6)||((b.offered_cents-b.captured_cents)-(a.offered_cents-a.captured_cents))||a.event.localeCompare(b.event)).slice(0,10);
const result={schema:'TUNE_EXPANSION_SCOREBOARD_V1',selection_sha256:selectionSha,seed:selection.seed,os_sha256:runInputs['window1_v54_dual_belief_os.js'],created_at:new Date().toISOString(),definitions:{completion:'Both fills eligible in corrected span/bell. Denominator all 100 selected; offered-game denominator separate. This is the existing grade OUTCOME metric, not safety certification.',one_sided:'Exactly one corrected-span eligible fill. Unknown spans remain unknown, not unfilled.',captured:'Unchanged rubric OUTCOME credit: incomplete valid pairs get zero; positive corrected under-par completed pair discount. No credit for unverified span. Grade hard failures remain F and are reported separately, not silently repaired or redefined.',offered:'Positive corrected truth-table discount; unknown and nonpositive offers separated.',captured_per_game_offered:'Captured cents on verified positive-offer games divided by count of those games.',worst:'Among graded positive-offer games: worst current rubric letter first, then largest offered-minus-captured cents, then event ID. Unknown spans listed separately, not assigned performance failure.',fills:'Replay credits are maker-reach simulations; no real orders and no known queue priority.',seal:'Only the frozen selected100 ran; other704 unrun in this order. No historically-unseen assertion.'},summary:[summarize(facts,'ALL'),...selection.quotas.map(q=>summarize(facts.filter(f=>f.category===q.category),q.category))],safety_flags:facts.filter(f=>f.hard_failures.length).map(f=>({event:f.event,category:f.category,flags:f.hard_failures,grade:f.letter,reported_capture_cents:f.captured_cents})),worst_ten:worst,rows:facts};
result.determinism_label=policy.label;result.determinism=sampleVerification;
write(path.join(report,'SELECTION.json'),selection);write(path.join(report,'SCOREBOARD.json'),result);
write(path.join(report,'TUNE_DETERMINISM_POLICY.json'),policy);
write(path.join(report,'VERIFICATION.json'),{status:'PASS',scope:'TUNE_ITERATION_ONLY',label:policy.label,selected:100,executed:100,passes:verification.reduce((n,r)=>n+r.passes,0),determinism_sample:sampleVerification,full_universe_determinism:verification.every(r=>r.identical===true),organ_final_record_acceptance:'PENDING_FULL_UNIVERSE_TWO_PASS',other_selected_population_executed:0,inputs:runInputs,rubric_sha256:rubricHashes[0],grade_contract_sha256:gradeContractHashes[0],selection_sha256:selectionSha,games:verification});
write(path.join(report,'SOURCE_RECEIPT.json'),{binding,selected_prints:extract,code:['prepare.mjs','run.mjs','build_faces.mjs','finalize.mjs','test_support.cjs'].map(name=>({name,sha256:b.fileHash(path.join(import.meta.dirname,name))})),scope:'Authorized unsupported-rest conduct and corrected-bell replay of frozen 100; ALTGAS separately. No pool, price, selection, grading span or rubric change. Full traces remain local.'});
write(path.join(root,'SCOREBOARD.json'),result);
write(path.join(report,'DIAGNOSTIC_FLAGS.json'),{scope:'Read-only findings; pinned replay, grade contract and rubric unchanged.',safety:result.safety_flags,missing_offer:facts.filter(f=>f.offer_issue).map(f=>({event:f.event,grade:f.letter,...f.offer_issue})),fill_witness_missing:facts.flatMap(f=>f.fill_witnesses.filter(w=>!w.positive_size_witness||w.at_or_below_rest!==true).map(w=>({event:f.event,...w})))});
await writeGameIndex(data);const index=JSON.parse(fs.readFileSync(path.join(data,'index.json')));assert(selection.selected.every(r=>index.games.some(g=>g.event===r.event_id)));
// The served scoreboards are rebuilt by report.mjs only AFTER the new fault
// audit is hash-bound to the new faces/grades. Never reuse stale fault credits.
const lines=['# Tune expansion — 100 frozen games','',`OS ${result.os_sha256}. Seed ${selection.seed}. Selection ${selectionSha}.`,'','All 100 executed twice with only unsupported-rest conduct and corrected replay bell changed. Pool, prices, selection and rubric unchanged. Unknown spans are not redrawn.','', '| Tour | Selected | Graded | Complete | One-sided | Offered games | Captured / offered ¢ | Captured ¢ per offered game |','|---|---:|---:|---:|---:|---:|---:|---:|',...result.summary.map(r=>`| ${r.category} | ${r.selected} | ${r.graded} | ${r.completed} | ${r.one_sided} | ${r.offered_games} | ${r.captured_cents} / ${r.offered_cents} | ${r.captured_per_game_offered?.toFixed(3)??'unknown'} |`),'','## Letters','',...result.summary.map(r=>`${r.category}: ${JSON.stringify(r.letters)}`),'','## Ten worst positive-offer games','',...worst.map((r,i)=>`${i+1}. ${r.event} — ${r.letter}; ${r.captured_cents}/${r.offered_cents}¢. ${r.fault}`),'','## Unavailable rulers','',...facts.filter(r=>r.status==='UNGRADABLE').map(r=>`- ${r.event}: ${r.fault}`),'','See SCOREBOARD.json for definitions, per-game source hashes, all grade/sentence links, and before-credit fill eligibility.'];
lines.push('','## Credit and provenance','', 'The table is the raw unchanged-grade OUTCOME metric. The safety-audited before/after comparison and class-A counts are in ../unsupported-rests/REPORT.md; same-second or out-of-span fills receive no credit there.', '', 'Full traces and per-tick details stay local. The compact 100-game results are authorized for LAB deployment. ALTGAS is an additional named check, never part of the 100 denominators.');
const rendered=lines.join('\n').replace('All 100 executed twice with only unsupported-rest conduct and corrected replay bell changed.',`${policy.label}. Every selected game has a full replay; only the fixed sample is required to have two. Previously completed full comparisons are preserved. Full organ acceptance remains pending. Only unsupported-rest conduct and corrected replay bell changed.`)+'\n';
fs.writeFileSync(path.join(root,'REPORT.md'),rendered);fs.writeFileSync(path.join(report,'REPORT.md'),rendered);
console.log(JSON.stringify({status:'PASS',summary:result.summary,indexed_games:index.games.length},null,2));
