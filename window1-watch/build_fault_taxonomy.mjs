// Read-only replay audit. No engine execution, refit, selection change, or regrade.
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import crypto from 'node:crypto';
import readline from 'node:readline';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {unpackFace} from './face_encoding.mjs';
import {readBidDetails} from './bid_card_details.mjs';
import {readJsonBytes} from './json_storage.mjs';
import {readGradePrints} from './grade_prints.mjs';
const repo=path.resolve(import.meta.dirname,'..'),data=path.join(import.meta.dirname,'data');
const custody=process.argv[2]??'C:/tmp/tune_expansion_20260914';
const out=path.join(data,'tune-expansion/faults');
const read=p=>JSON.parse(readJsonBytes(p));
const sha=p=>crypto.createHash('sha256').update(readJsonBytes(p)).digest('hex');
const write=(p,v)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');};
const selection=read(path.join(custody,'SELECTION.json')),selectionSha=sha(path.join(custody,'SELECTION.json'));
const pinFile=path.join(custody,'RUN_INPUTS.json');
const inputs=fs.existsSync(pinFile)?read(pinFile).inputs:selection.inputs;
const printsRoot=process.argv[3]??custody;
const prior=read(path.join(data,'tune-expansion/SCOREBOARD.json'));
assert.equal(selectionSha,prior.selection_sha256);
for(const [name,pin] of Object.entries(inputs))assert.equal(sha(path.join(repo,'arb-executor/analysis',name)),pin);
const require=createRequire(import.meta.url),native=require(path.join(repo,'arb-executor/analysis/window1_v54_functionable_os.js'));
const binding=read(path.join(custody,'BINDING_0.json')).tick_library;
for(const source of Object.values(binding))assert.equal(sha(source.path),source.sha256);
const contract=read(binding.bench_receipt.path).organ_contract;
async function stream(file,callback){for await(const line of readline.createInterface({input:fs.createReadStream(file).pipe(zlib.createGunzip()),crlfDelay:Infinity})){if(line)callback(JSON.parse(line));}}
const counts=new Map();
await stream(binding.print_counts.path,r=>{if(!counts.has(r.ticker))counts.set(r.ticker,{seconds:[],counts:[]});const v=counts.get(r.ticker);v.seconds.push(r.second);v.counts.push(r.true_print_count_cum);});
const groups=new Map();
await stream(binding.index.path,r=>{if(!groups.has(r.event_id))groups.set(r.event_id,{identity:r.event_id,category:r.category,date:r.event_id.split('-').at(-1).slice(0,7),legs:[]});groups.get(r.event_id).legs.push(native.compactTickLeg(r,counts.get(r.ticker)));counts.delete(r.ticker);});
assert.equal(counts.size,0);
const pairs=[...groups.values()].sort((a,b)=>a.identity<b.identity?-1:a.identity>b.identity?1:0).map(g=>native.poolPair(g.legs,{identity:g.identity,category:g.category,date:g.date},contract)).filter(Boolean);
const ub=(a,x)=>{let l=0,h=a.length;while(l<h){const m=(l+h)>>>1;if(a[m]<=x)l=m+1;else h=m;}return l;};
const role=(last,open)=>!Number.isFinite(last)||!Number.isFinite(open)?'NOT_CALLABLE':last-open>=contract.role_drift_cents?'CLIMBER':last-open<=-contract.role_drift_cents?'FALLER':'NOT_CALLABLE';
const sample=(leg,epoch)=>{const i=ub(leg.epoch,epoch)-1;return i<0?{last:null,bid:null,ask:null}:{last:leg.last[i],bid:leg.bid[i],ask:leg.ask[i]};};
const sum=a=>a.reduce((s,x)=>s+x,0);
const close=(a,b)=>{assert(Number.isFinite(a)&&Number.isFinite(b));assert(Math.abs(a-b)<=Math.max(1,Math.abs(b))*1e-9,`Stored/reconstructed disagreement: ${a} vs ${b}`);};
const date=id=>{const c=id.split('-').at(-1),months=['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'];return `20${c.slice(0,2)}-${String(months.indexOf(c.slice(2,5))+1).padStart(2,'0')}-${c.slice(5,7)}`;};
function topMembers(stage,leg,meta){
 const pc=stage.layers.macro.context.pool_cascade,side=pc.sides[leg],layer=side.selected_layer,saved=side.layers[layer];
 assert(['FIRST-TICK-ONLY','BASE'].includes(layer),'Unimplemented author layer');
 const sideIndex=pc.first_tick.legs.indexOf(leg),formation=Math.max(...Object.values(meta.formation_end_epochs));
 const pool=pairs.filter(m=>m.category===meta.category&&m.identity!==meta.event_id&&m.date!==meta.event_date&&m.bell<formation);
 const weighted=pool.map(m=>{
  const epoch=m.bell-pc.minutes_to_bell*contract.minute_seconds,obs=sample(m.legs[sideIndex],epoch);
  const available=m.first_mtb>=pc.minutes_to_bell&&[obs.last,obs.bid,obs.ask].every(Number.isFinite)&&(saved.role==='NOT_CALLABLE'||role(obs.last,m.legs[sideIndex].open)===saved.role);
  const w=layer==='BASE'?(m.first.sides.every((s,i)=>(s.last>=contract.discovery_side_boundary_cents)===(pc.first_tick.prices[i]>=contract.discovery_side_boundary_cents))?contract.likelihood_unit:0):
   contract.likelihood_unit/(contract.likelihood_unit+sum(m.first.sides.map((s,i)=>Math.abs(s.last-pc.first_tick.prices[i]))))/(contract.likelihood_unit+Math.abs(m.first_mtb-pc.first_tick.mtb)/pc.first_tick.mtb);
  return {m,weight:available?w:0};
 }).filter(r=>r.weight>0);
 const total=sum(weighted.map(r=>r.weight)),ess=total*total/sum(weighted.map(r=>r.weight*r.weight));
 assert.equal(weighted.length,saved.member_count,`Member count ${meta.event_id}/${leg}`);close(total,saved.weight_sum);close(ess,saved.ess);
 return {layer,member_count:saved.member_count,ess:saved.ess,weight_sum:saved.weight_sum,verification:'Member count, weight sum and ESS reproduced from pinned library using stored receipt state; not a new OS replay.',top_five:weighted.sort((a,b)=>b.weight-a.weight||a.m.identity.localeCompare(b.m.identity)).slice(0,5).map(({m,weight})=>({event_id:m.identity,date:date(m.identity),weight,weight_share:weight/total,first_prices:Object.fromEntries(m.legs.map((l,i)=>[l.id,m.first.sides[i].last])),first_epoch:m.first_epoch,bell_epoch:m.bell}))};
}
const cached=[];
for(const s of selection.selected){
 const event=s.event_id,faceFile=path.join(data,event+'.face.json'),gradeFile=path.join(data,event+'.grade.json');
 // This pass only establishes the unchanged cohort-wide print-count ruler.
 // Hydrate one game's complete decision/grade records at a time below.
 const face=read(faceFile),input=read(path.join(custody,'runs',event,'INPUT_RECEIPT.json'));
 assert.equal(face.provenance.os_sha256,inputs['window1_v54_dual_belief_os.js']);
 const valid=face.truth?.status==='OK'&&Number.isFinite(face.truth.span_start_epoch)&&Number.isFinite(face.truth.span_end_epoch)&&face.truth.span_end_epoch>face.truth.span_start_epoch;
 const printFile=path.join(printsRoot,'selected_prints',event+'.jsonl');
 const extracted=await readGradePrints(printFile,[{event,legs:s.legs}]);
 const before=prior.rows.find(r=>r.event===event);assert.equal(sha(gradeFile),before.grade_sha256);
 const prints=Object.fromEntries(s.legs.map(l=>[l,valid?extracted[event].legs[l].filter(p=>p.epoch>=face.truth.span_start_epoch&&p.epoch<Math.min(face.truth.span_end_epoch,face.truth.bell_epoch)):null]));
 cached.push({s,event,faceFile,gradeFile,input,valid,prints,print_source:extracted[event].provenance,face_sha256:sha(faceFile),grade_sha256:sha(gradeFile)});
}
const thresholds=selection.quotas.map(q=>{const values=cached.filter(g=>g.s.category===q.category&&g.valid).flatMap(g=>g.s.legs.map(l=>g.prints[l].length)).sort((a,b)=>a-b),rank=Math.ceil(values.length/10);return {category:q.category,known_span_legs:values.length,decile_rank:rank,N:values[rank-1]??null,rule:'D iff positive accepted prints in corrected common span < N. N is empirical lower inverse-CDF 10th percentile (rank ceil(n/10)) among all known-span sides in this frozen draw, including zero counts; no minimum or interpolation.',sorted_counts:values};});
const names={A:'bid below path',B:'sentence far off',C:'safety failure',D:'thin tape',E:'other / missing evidence'};
const results=[];
for(const g of cached){
 const {s,event,input,valid,prints}=g,N=thresholds.find(q=>q.category===s.category).N;
 const face=readBidDetails(unpackFace(read(g.faceFile)),data),grade=read(g.gradeFile);
 assert.equal(grade.provenance.face_sha256,g.face_sha256);
 assert.equal(sha(g.faceFile),g.face_sha256);assert.equal(sha(g.gradeFile),g.grade_sha256);
 const safetyActions=(grade.HANDS.actions??[]).filter(a=>a.same_second_fill===true);
 const safetyLegs=new Set(safetyActions.map(a=>a.leg));
 const otherSafety=(grade.HANDS.violation_receipts??[]);
 if(otherSafety.length)for(const a of grade.HANDS.actions??[])if(otherSafety.includes(a.receipt))safetyLegs.add(a.leg);
 const safeFilled=Object.fromEntries(s.legs.map(l=>[l,valid?grade.OUTCOME.legs[l]?.valid_span_fill===true&&!safetyLegs.has(l):null]));
 const safeCount=valid?Object.values(safeFilled).filter(Boolean).length:null,completed=valid?safeCount===s.legs.length:null;
 const captured=valid?(completed?grade.OUTCOME.captured_cents:0):null;
 const records=[];
 for(const leg of s.legs){
  const failed=valid?safeFilled[leg]!==true:true;
  if(!failed)continue;
  const floor=face.truth?.legs?.[leg],first=grade.MICRO?.legs?.[leg]?.first_eligible_full_span??null;
  const actions=(face.render?.bid_actions??[]).filter(a=>a.leg===leg);
  const placements=actions.filter(a=>['PLACE','REPRICE'].includes(a.kind)&&Number.isFinite(a.new_cents));
  const A=[],unobserved=[];
  if(valid)for(const a of placements){
   if(a.timestamp_epoch<face.truth.span_start_epoch||a.timestamp_epoch>=Math.min(face.truth.span_end_epoch,face.truth.bell_epoch))continue;
   const later=prints[leg].slice(ub(prints[leg].map(p=>p.epoch),a.timestamp_epoch));
   if(!later.length){unobserved.push(a.receipt);continue;}
   const minimum=Math.min(...later.map(p=>p.price));
   if(minimum<=a.new_cents)continue;
   const floorKnown=Number.isFinite(floor?.floor_cents)&&Number.isFinite(floor?.floor_epoch);
   A.push({receipt:a.receipt,action:a.kind,placement_epoch:a.timestamp_epoch,bid_cents:a.new_cents,recorded_floor_cents:floor?.floor_cents??null,recorded_floor_epoch:floor?.floor_epoch??null,floor_minus_placement_minutes:floorKnown?(floor.floor_epoch-a.timestamp_epoch)/60:null,Q_at_placement:a.sentence?.Q??a.bid_accountability?.assumption?.Q??null,remaining_positive_print_floor:minimum,later_positive_prints:later.length,floor_before_placement:floorKnown?floor.floor_epoch<a.timestamp_epoch:null,bid_below_recorded_floor:floorKnown?a.new_cents<floor.floor_cents:null,at_floor_after_it_passed:floorKnown?a.new_cents===floor.floor_cents&&floor.floor_epoch<a.timestamp_epoch:null});
  }
  let B=null;
  if(valid&&Number.isFinite(first?.q50)&&Number.isFinite(floor?.floor_cents)&&Math.abs(first.q50-floor.floor_cents)>3){
   const receipt=face.os.find(r=>r.receipt===first.receipt);assert(receipt?.detail_url);
   const stageFile=path.join(import.meta.dirname,receipt.detail_url+'.gz'),envelope=JSON.parse(zlib.gunzipSync(fs.readFileSync(stageFile))),stage=envelope.row;
   const pc=stage.layers.micro.context.beliefs[leg].pool_cascade;
   B={first_eligible_receipt:first.receipt,epoch:first.epoch,Q:first.q50,floor:floor.floor_cents,signed_error_cents:first.q50-floor.floor_cents,...topMembers(stage,leg,input.meta),role_at_call:pc.roles.current_role,realized_role:grade.MACRO.operator_roles?.[leg]?.realized_role??null,role_at_call_right:pc.roles.current_role===grade.MACRO.operator_roles?.[leg]?.realized_role,grade_role_assessment:grade.MACRO.operator_roles?.[leg]??null,stage_sha256:sha(stageFile),source:'Existing grade MICRO first_eligible_full_span; immutable receipt. Member attribution reconstructed with count/ESS/weight-sum parity.'};
  }
  const C=safetyActions.filter(a=>a.leg===leg).map(a=>({receipt:a.receipt,kind:'SAME_SECOND_FILL',fill_epoch:a.timestamp_epoch,current_price_epoch:a.current_price_epoch??null,current_price_receipt:a.current_price_receipt,price_age_minutes:a.current_price_age_minutes,lineage_age_minutes:a.order_lineage_age_minutes}));
  if(safetyLegs.has(leg)&&!C.length)C.push({kind:'STORED_SAFETY_VIOLATION',receipts:otherSafety});
  const D=valid&&prints[leg].length<N?{positive_prints:prints[leg].length,N,category:s.category}:null;
  const classes=[...(A.length?['A']:[]),...(B?['B']:[]),...(C.length?['C']:[]),...(D?['D']:[])];
  let E=null;
  if(!classes.length){
   const old=prior.rows.find(r=>r.event===event)?.missing_sides.find(r=>r.leg===leg);
   E={reason:!valid?'No verified corrected span; A/B/D cannot be asserted.':!placements.length?'No recorded bid placement; '+(old?.last_action?.reason??'decision reason not stored'):old?.reason??'Miss not explained by A/B/C/D; see stored action history.',first_eligible_call_present:!!first,placements:placements.length,placements_without_later_positive_print:unobserved.length,last_action:old?.last_action??null};classes.push('E');
  }
  records.push({leg,scope:valid?'FAILED_SIDE':'UNKNOWN_SPAN_SIDE',raw_filled:grade.OUTCOME.legs[leg]?.valid_span_fill===true,safe_filled:safeFilled[leg],classes,A,B,C,D,E,positive_prints:valid?prints[leg].length:null,unobserved_placements:unobserved});
 }
 const classes=[...new Set(records.flatMap(r=>r.classes))].sort();
 const labels=records.map(r=>`${r.leg}: ${r.classes.map(c=>`${c} · ${names[c]}`).join(' + ')}`);
 const header=labels.length?labels.join(' | '):'Pair completed · no failed side';
 const result={schema:'TUNE_FAULT_TAXONOMY_V1',event,category:s.category,provenance:{face_sha256:g.face_sha256,grade_sha256:g.grade_sha256,os_sha256:face.provenance.os_sha256,trace_sha256:face.provenance.trace_sha256,selection_sha256:selectionSha,print_sha256:g.print_source.sha256},known_span:valid,classes,header,retrospective:true,credit:{raw_captured_cents:grade.OUTCOME.captured_cents,captured_cents:captured,best_capturable_cents:grade.OUTCOME.best_capturable_cents,pair_sum:completed?grade.OUTCOME.pair_sum:null,pair_completed:completed,valid_fills:safeCount,legs:safeFilled,safety_excluded:safetyLegs.size>0,note:safetyLegs.size?'Safety-flagged fills excluded. Original grade retained unchanged.':'Corrected-span fill eligibility; queue priority unknown.'},sides:records};
 results.push(result);write(path.join(out,event+'.json'),result);console.log('CLASSIFIED',event,classes.join('+')||'COMPLETE');
}
function summarize(rows,category){
 const sides=rows.flatMap(r=>r.sides),failed=sides.filter(r=>r.scope==='FAILED_SIDE'),A=failed.filter(r=>r.classes.includes('A'));
 const distribution={floor_before_only:0,bid_too_deep_only:0,both:0,neither_or_unknown:0};
 for(const r of A){const a=r.A[0],before=a.floor_before_placement,deep=a.bid_below_recorded_floor;distribution[before&&deep?'both':before?'floor_before_only':deep?'bid_too_deep_only':'neither_or_unknown']++;}
 const offered=rows.filter(r=>Number.isFinite(r.credit.best_capturable_cents)&&r.credit.best_capturable_cents>0);
 return {category,games:rows.length,failed_sides:failed.length,unknown_span_sides:sides.length-failed.length,counts:Object.fromEntries(Object.keys(names).map(c=>[c,{games:rows.filter(r=>r.classes.includes(c)).length,failed_sides:failed.filter(r=>r.classes.includes(c)).length,unknown_span_sides:sides.filter(r=>r.scope!=='FAILED_SIDE'&&r.classes.includes(c)).length}])),A_and_B:{same_failed_side:failed.filter(r=>r.classes.includes('A')&&r.classes.includes('B')).length,same_game:rows.filter(r=>r.classes.includes('A')&&r.classes.includes('B')).length},A_first_offending_placement_distribution:distribution,A_any_placement:{floor_before: A.filter(r=>r.A.some(a=>a.floor_before_placement)).length,bid_too_deep:A.filter(r=>r.A.some(a=>a.bid_below_recorded_floor)).length,at_recorded_floor_after_it_passed:A.filter(r=>r.A.some(a=>a.at_floor_after_it_passed)).length},credit:{complete:rows.filter(r=>r.credit.pair_completed===true).length,one_sided:rows.filter(r=>r.credit.valid_fills===1).length,unfilled:rows.filter(r=>r.credit.valid_fills===0).length,unknown:rows.filter(r=>r.credit.valid_fills===null).length,offered_games:offered.length,captured_cents:sum(offered.map(r=>r.credit.captured_cents??0)),offered_cents:sum(offered.map(r=>r.credit.best_capturable_cents))}};
}
const definitions={A:'Failed side: at least one actual PLACE or REPRICE inside the corrected span, with later accepted positive prints, and every such print strictly after that action and before min(corrected span end,bell) above the bid. No later prints is unobserved, not proof of A. Includes all price-setting actions; canonical distribution uses first qualifying action in receipt order. Q and full-span recorded floor retained separately. Delta=(floor_epoch-placement_epoch)/60; negative means floor came first. Later prints after cancellation count when distinguishing never-revisited from moved-off.',B:'Failed side: absolute difference of the existing first eligible Q and corrected full-span recorded floor strictly greater than 3 cents. No after-the-fact choice of forecast; no range rescue for this diagnostic. Top members are reconstructed, not falsely claimed to have been logged, with exact count and floating-point ESS/weight-sum parity.',C:'Any leg with stored HANDS.same_second_fill or a stored post-only/pre-formation violation. Exclude that leg from reachable-fill count and require two remaining eligible legs for pair credit; incomplete pair gets zero. Original grades/historical credits preserved as raw.',D:'Positive accepted prints in corrected common span fewer than tour-specific empirical bottom-decile N from all known-span selected sides; zeros included. Unknown spans not used in threshold and not labeled thin.',E:'Residual explanation for a failed side not in A/B/C/D, or explicit unknown span. Missing evidence never represented as zero or as an execution failure.',counts:'Multi-label. Report game incidence and failed-side incidence separately; E unknown spans separate. A and B overlap includes only failed sides, not successfully filled partners. Full original draw unchanged; no replay or tuning.',roles:'Role at the first eligible call versus realized role from existing corrected grade; original grade first-bind assessment also retained.',publication:'Only reviewed selected100 + the existing five demo games. No remaining704, raw prints, engine, full stages, renewal streams or local audit code in static assets.'};
const result={schema:'TUNE_FAULT_AUDIT_V1',selection_sha256:selectionSha,os_sha256:inputs['window1_v54_dual_belief_os.js'],definitions,thresholds,summary:[summarize(results,'ALL'),...selection.quotas.map(q=>summarize(results.filter(r=>r.category===q.category),q.category))],games:results};
write(path.join(out,'index.json'),result);
write(path.join(out,'RECEIPT.json'),{schema:result.schema,selection_sha256:selectionSha,source_inputs:inputs,library:binding,thresholds,definitions,script_sha256:sha(new URL(import.meta.url)),inputs:cached.map(g=>({event:g.event,face_sha256:g.face_sha256,grade_sha256:g.grade_sha256,print_source:g.print_source})),output:{path:'index.json',sha256:sha(path.join(out,'index.json'))}});
for(const [name,pin] of Object.entries(inputs))assert.equal(sha(path.join(repo,'arb-executor/analysis',name)),pin);
console.log(JSON.stringify({status:'PASS',thresholds:thresholds.map(({sorted_counts,...x})=>x),summary:result.summary},null,2));
