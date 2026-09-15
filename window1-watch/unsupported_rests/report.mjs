import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import crypto from 'node:crypto';
import readline from 'node:readline';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {loadPolicy,validateDeterminism,verifySample} from './tune_policy.mjs';
import {buildScoreboard} from '../build_scoreboard.mjs';
import {readBidDetails} from '../bid_card_details.mjs';
const repo=path.resolve(import.meta.dirname,'../..'),root='C:/tmp/unsupported_rests_20260914',data=path.join(repo,'window1-watch/data');
const out=path.join(data,'unsupported-rests');fs.mkdirSync(out,{recursive:true});
const read=p=>JSON.parse(fs.readFileSync(p)),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const write=(name,value)=>fs.writeFileSync(path.join(out,name),JSON.stringify(value,null,2)+'\n');
const selection=read(path.join(root,'SELECTION.json')),pins=read(path.join(root,'RUN_INPUTS.json'));
const policy=loadPolicy(),sampleVerification=verifySample(policy);
const before=read(path.join(root,'BEFORE_FAULTS.json')),after=read(path.join(data,'tune-expansion/faults/index.json'));
assert.equal(before.selection_sha256,after.selection_sha256);assert.equal(after.os_sha256,pins.inputs['window1_v54_dual_belief_os.js']);
assert.deepEqual(before.thresholds,after.thresholds,'Thin-tape ruler changed');
for(const [name,pin] of Object.entries(pins.inputs))assert.equal(sha(path.join(repo,'arb-executor/analysis',name)),pin);
const output=[];const samples=[];const allEvents=[...selection.selected.map(r=>r.event_id),'KXATPMATCH-26JUL12ALTGAS'];
function card(g,credit){return {event:g.event,letter:g.LETTER.letter,sections:g.display?.sections,macro:g.MACRO?.operator_roles,
  fills:Object.fromEntries(Object.entries(g.OUTCOME.legs).map(([leg,v])=>[leg,{cents:v.cents,valid_span_fill:v.valid_span_fill,vs_floor_cents:v.vs_floor_cents}])),
  raw_outcome:g.OUTCOME,safety_audited_credit:credit??null};}
const cards=[];
for(const event of allEvents){
 const dir=path.join(root,'runs',event),r=read(path.join(dir,'REPLAY_RECEIPT.json')),det=read(path.join(dir,'DETERMINISM_RECEIPT.json')),input=read(path.join(dir,'INPUT_RECEIPT.json'));
 assert.deepEqual(r.inputs,pins.inputs);validateDeterminism(det,event,policy);assert.equal(sha(r.trace.path),r.trace.sha256);
 assert.equal(r.sentence_action_weld,true,`Sentence/action mismatch: ${event}`);
 assert.equal(r.citation_weld,true,`Citation mismatch: ${event}`);
 assert.equal(r.pair_conservation,true,`Pair conservation flag: ${event}`);
 let reviews=0,pulls=0,exact=0,replacements=0,newExpired=0;const reasons={};
 for await(const line of readline.createInterface({input:fs.createReadStream(r.trace.path).pipe(zlib.createGunzip()),crlfDelay:Infinity})){
  if(!line)continue;const row=JSON.parse(line);if(row.kind==='PULL_UNSUPPORTED'){
   pulls++;assert(row.support_review.pull);assert(!row.support_review.exact_rest_supported);assert(!row.support_review.replacement_supported);
   reasons[row.support_review.blocked_reason]=(reasons[row.support_review.blocked_reason]??0)+1;
   if(event.endsWith('GANZIN')||event.endsWith('ALTGAS'))if(samples.filter(s=>s.event_id===event).length<6)samples.push(row);
  }
  if(row.kind!=='DECISION_STAGE')continue;
  for(const d of row.derivations??[]){
   const c=d.derivation?.rest_support;
   if(c?.required){reviews++;
    if(c.pull){assert.equal(d.action.action,'CANCEL_REST');assert.equal(d.action.reason,'PULL_UNSUPPORTED');assert.equal(d.action.target_cents,null);}
    else if(c.exact_rest_supported){exact++;assert.equal(c.active_rest_cents,c.fresh_Q);assert(c.fresh_X_epoch>row.timestamp_epoch);}
    else {replacements++;assert(c.replacement_supported);assert(!c.review_only);assert.equal(d.action.target_cents,c.fresh_Q);assert(c.fresh_X_epoch>row.timestamp_epoch);}
   }
   if(['PLACE_REST','REPRICE_REST'].includes(d.action.action)){
    const b=row.layers.micro.context.beliefs[d.leg_id];if(Number.isFinite(b.deadline?.deadline_epoch)&&b.deadline.deadline_epoch<=row.timestamp_epoch)newExpired++;
   }
  }
 }
 assert.equal(pulls,r.counts.PULL_UNSUPPORTED??0);
 const grade=read(path.join(data,event+'.grade.json')),old=read(path.join(root,'before_compact',event+'.grade.json'));
 assert.equal(grade.provenance.os_sha256,pins.inputs['window1_v54_dual_belief_os.js']);assert.equal(grade.provenance.trace_sha256,r.trace.sha256);
 if(input.truth_status==='OK'){
  for(const k of ['rubric_sha256','grade_contract_sha256','grade_rulers_sha256','grade_measurements_sha256','grade_operator_standard_sha256'])assert.equal(grade.provenance[k],old.provenance[k],`Unchanged grader ${event}/${k}`);
  assert.equal(grade.provenance.effective_truth_sha256,old.provenance.effective_truth_sha256,'Corrected ruler changed');
 }
 cards.push({event,before:card(old,before.games.find(g=>g.event===event)?.credit),after:card(grade,after.games.find(g=>g.event===event)?.credit)});
 const faceBytes=fs.readFileSync(path.join(data,event+'.face.json')),face=JSON.parse(faceBytes);
 const transfer=zlib.gzipSync(faceBytes,{level:9});assert(transfer.length<2*1024*1024,'Face transfer exceeds cap: '+event);
 if(face.bid_card_details)readBidDetails(face,data); // hashes, provenance, counts, exact preview equality
 output.push({event,selected:selection.selected.some(s=>s.event_id===event),trace:r.trace,determinism_sha256:det.first.sha256,
  passes:det.passes,identical:det.all_byte_identical,sample_member:policy.sample_events.includes(event),bell_source_used:r.bell_source_used,bell_alignment:r.bell_alignment,verified_span_end_epoch:input.meta.span_end_epoch,
  reviews,pulls,exact_renewals:exact,replacements,pull_blocked_reasons:reasons,new_placements_with_nonfuture_deadline:newExpired,
  grade_sha256:sha(path.join(data,event+'.grade.json')),face_sha256:sha(path.join(data,event+'.face.json')),
  face_transfer_bytes:transfer.length,bid_card_details:face.bid_card_details??null,timeline:face.timeline??null});
}
const comparison=after.summary.map(a=>{const b=before.summary.find(x=>x.category===a.category);assert.equal(b.credit.offered_cents,a.credit.offered_cents);assert.equal(b.credit.offered_games,a.credit.offered_games);return {category:a.category,before:{...b.credit,class_A_sides:b.counts.A.failed_sides,class_A_games:b.counts.A.games},after:{...a.credit,class_A_sides:a.counts.A.failed_sides,class_A_games:a.counts.A.games}};});
const severity={F:0,D:1,C:2,B:3,A:4};
const worst=after.games.filter(g=>g.known_span&&g.credit.best_capturable_cents>0).map(g=>{
 const grade=read(path.join(data,g.event+'.grade.json'));
 return {event:g.event,category:g.category,letter:grade.LETTER.letter,captured:g.credit.captured_cents,offered:g.credit.best_capturable_cents,
   fault:g.sides.length?g.header:grade.display.governing,classes:g.classes};
}).sort((a,b)=>(severity[a.letter]??5)-(severity[b.letter]??5)||(b.offered-b.captured)-(a.offered-a.captured)||a.event.localeCompare(b.event)).slice(0,10);
const unit=JSON.parse(execFileSync(process.execPath,[path.join(import.meta.dirname,'test_support.cjs')],{encoding:'utf8'}));assert.equal(unit.passed,18);
const diff=execFileSync('git',['diff','--','arb-executor/analysis/window1_v54_dual_belief_os.js','arb-executor/analysis/build_window1_v54_dual_belief.js'],{cwd:repo,encoding:'utf8'});
const added=diff.split(/\r?\n/).filter(l=>l.startsWith('+')&&!l.startsWith('+++')).map(l=>l.slice(1));
const removed=diff.split(/\r?\n/).filter(l=>l.startsWith('-')&&!l.startsWith('---')).map(l=>l.slice(1));
const numericBag=lines=>lines.filter(l=>!/^\s*\/\//.test(l)).flatMap(l=>l.match(/\b\d+(?:\.\d+)?\b/g)??[]).reduce((a,n)=>(a[n]=(a[n]??0)+1,a),{});
const addedNumbers=numericBag(added),removedNumbers=numericBag(removed);
const literals=added.filter(l=>/^\s*[^/]/.test(l)&&/\b(?:true|false)\b/.test(l));
const audit={stage_A:'Only exact-level support/cancel logic, pre-print/BELL reviews, and corrected-bell metadata in engine/builder. Pool and price implementations unchanged.',
 no_new_numeric_policy_literals:Object.entries(addedNumbers).every(([n,count])=>count<=(removedNumbers[n]??0)),added_numeric_tokens:addedNumbers,removed_numeric_tokens:removedNumbers,
 no_game_or_leg_ids_in_policy_diff:!added.some(l=>/KX[A-Z]+MATCH|GANZIN|ALTGAS/.test(l)),new_literal_boolean_lines:literals,
 boolean_meaning:'Existing optional replay controls only; market claims are computed predicates. No asserted safety success.',
 functionable_sha256:pins.inputs['window1_v54_functionable_os.js'],diff_sha256:crypto.createHash('sha256').update(diff).digest('hex')};
assert(audit.no_new_numeric_policy_literals);assert(audit.no_game_or_leg_ids_in_policy_diff);
const receipt={schema:'UNSUPPORTED_RESTS_BELL_ALIGNMENT_V1',selection_sha256:after.selection_sha256,seed:selection.seed,inputs:pins.inputs,
 baseline:{os_sha256:before.os_sha256,fault_audit_sha256:sha(path.join(root,'BEFORE_FAULTS.json')),scoreboard_sha256:sha(path.join(root,'BEFORE_SCOREBOARD.json'))},
 rules:{conduct:'Missed or superseded standing assumption requires a fresh resolved sentence supporting its exact level and a future deadline; otherwise CANCEL_REST with PULL_UNSUPPORTED. A valid postable replacement may supersede it. Existing safety vetoes still apply.',
 pre_print:'Overdue review reads only previously observed state; it can renew exact price or cancel, never reprice to the incoming print. Equal-deadline print passes through the existing fill order.',
 bell:'Later corrected ruler bell extends replay. Earlier/absent bell and unknown span preserve previous behavior. Verified grading spans unchanged; out-of-span fills uncredited.',
 class_A:'Same stored-placement diagnostic as before, not just final rests. Pulling an unsupported bid does not erase a historical bid-below-path occurrence.',
 credit:'Safety-audited corrected-span credit, with raw grade OUTCOME retained separately. Unknown spans never counted as unfilled.',
 scope:`${policy.label}. All100 have full replay artifacts; fixed10 (ALT/GAS plus9 selected, including GANZIN) verified twice. Existing extra comparisons preserved. Remaining704 unrun. No pool, price, rubric or tuning changes. Not final organ acceptance.`,
 publication:'Compact face/grade/oracle/pressure/fault/picker/history/scoreboard and operator-approved hash-bound on-demand bid-card detail and receipt/chart-marker timeline chunks only; no raw prints, full stages or full per-tick renewal streams.'},
 verification:{status:'PASS',scope:'TUNE_ITERATION_ONLY',label:policy.label,selected:100,selected_passes:output.filter(r=>r.selected).reduce((n,r)=>n+r.passes,0),named_checks:1,named_check_passes:output.find(r=>!r.selected).passes,unit_tests:unit.passed,determinism_sample:sampleVerification,full_universe_determinism:output.every(r=>r.identical===true),final_organ_record:'PENDING_FULL_UNIVERSE_TWO_PASS'},audit,
 summary:comparison,games:output,worst_ten:worst};
buildScoreboard(data);
buildScoreboard(data,{events:selection.selected.map(r=>r.event_id),output:'scoreboard-tune-100.json',scope:`${policy.label}; frozen 100-game draw; safety-flagged fills excluded`,determinism:sampleVerification});
write('RECEIPT.json',receipt);write('BEFORE_AFTER_CARDS.json',cards);write('SAMPLE.json',samples);write('LITERAL_BOOLEAN_AUDIT.json',audit);write('BEFORE_FAULT_SUMMARY.json',{sha256:receipt.baseline.fault_audit_sha256,summary:before.summary});
write('TUNE_DETERMINISM_POLICY.json',policy);
const line=x=>`${x.complete} | ${x.one_sided} | ${x.unfilled} | ${x.unknown} | ${x.captured_cents}/${x.offered_cents} | ${x.class_A_sides}`;
const md=['# Unsupported rests + bell alignment','',`OS ${pins.inputs['window1_v54_dual_belief_os.js']}. Same frozen selection ${after.selection_sha256}.`,'',
'| Tour / run | Complete | One-sided | Unfilled | Unknown | Captured/offered ¢ | Class A sides |','|---|---:|---:|---:|---:|---:|---:|',
...comparison.flatMap(c=>[`| ${c.category} before | ${line(c.before)} |`,`| ${c.category} after | ${line(c.after)} |`]),'',
`${policy.label}. All100 have full first-pass artifacts; the fixed10 comparisons agree. Existing extra two-pass checks are retained. This is not full-universe determinism or final organ acceptance. Five unavailable spans remain unavailable. Grading spans and denominators unchanged. Full traces local.`,
'','## Named cards','',...cards.filter(c=>/ALTGAS|GANZIN/.test(c.event)).map(c=>`${c.event}: ${c.before.letter} → ${c.after.letter}; after fills ${JSON.stringify(c.after.fills)}; raw outcome ${c.after.raw_outcome.captured_cents}/${c.after.raw_outcome.best_capturable_cents}¢.`),
'','## Ten worst after','',...worst.map((r,i)=>`${i+1}. ${r.event} — ${r.letter}; ${r.captured}/${r.offered}¢. ${r.fault}`),
'','Class A counts historical failed price-setting actions, not only bids still standing. All raw grades and safety exclusions are retained beside credited outcomes. New placements whose deadlines are already nonfuture are counted in the receipt, not silently fixed by this narrowly scoped order.'];
fs.writeFileSync(path.join(out,'REPORT.md'),md.join('\n')+'\n');console.log(JSON.stringify({summary:comparison,worst,named:cards.filter(c=>/ALTGAS|GANZIN/.test(c.event))},null,2));
