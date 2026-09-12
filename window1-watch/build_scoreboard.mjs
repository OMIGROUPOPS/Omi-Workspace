import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
const sha=b=>createHash('sha256').update(b).digest('hex');
export function buildScoreboard(root=resolve(import.meta.dirname,'data')){
 const indexBytes=readFileSync(resolve(root,'index.json')),index=JSON.parse(indexBytes),inputs=[];
 const rows=index.games.map(entry=>{
  if(!/^[A-Z0-9-]+$/.test(entry.event))throw Error('Invalid event in game index');
  const fb=readFileSync(resolve(root,entry.event+'.face.json')),gb=readFileSync(resolve(root,entry.event+'.grade.json')),f=JSON.parse(fb),g=JSON.parse(gb);
  if(g.event!==entry.event||g.provenance.face_sha256!==sha(fb)||g.provenance.trace_sha256!==f.provenance.trace_sha256||g.provenance.os_sha256!==f.provenance.os_sha256)throw Error('Unbound scoreboard grade '+entry.event);
  const source={face_sha256:sha(fb),grade_sha256:sha(gb),os_sha256:g.provenance.os_sha256,trace_sha256:g.provenance.trace_sha256,truth_commit:g.provenance.truth_commit??f.truth?.table_commit,corrections_commit:f.truth?.corrections_commit??null};inputs.push({event:entry.event,...source});
  const o=g.OUTCOME, actions=g.HANDS?.actions, fills=Object.values(o.legs).filter(l=>l.valid_span_fill===true).length;
  const hasBid=Array.isArray(actions)?actions.some(a=>a.action==='PLACE_REST'||a.action==='REPRICE_REST'):null;
  const missing=f.legs.filter(l=>!o.legs[l]?.valid_span_fill).map(l=>{const last=actions?.filter(a=>a.leg===l).at(-1);return {side:l,disposition:'UNFILLED_IN_CORRECTED_SPAN',reason:o.legs[l]?.reason??'STORE SILENT — no filed miss cause',last_action:last?.action??null,last_action_tokens:last?.tokens??null,receipt:last?.receipt??null};});
  return {event:entry.event,game:f.legs.join(' / '),category:f.category,mode:'LAB',timestamp:g.timestamp,letter:g.display.letter,sections:g.display.sections,governing:g.display.governing,source,
   called_by_os:f.os.length>0,any_bid:hasBid,valid_fills:fills,side_count:f.legs.length,completed:o.valid_pair_completed===true,pair_sum:o.pair_sum,captured_cents:o.captured_cents,offered_cents:o.best_capturable_cents,capture_ratio:o.capture_ratio,
   missing_sides:missing,legs:o.legs,grade_url:`/data/${entry.event}.grade.json`,ruler_line:g.display.ruler_line,diagnostic_lines:g.display.diagnostic_hover_lines};
 });
 if(new Set(rows.map(r=>r.event)).size!==rows.length)throw Error('Duplicate event would multiply denominator');
 function summarize(list,category){const eligible=list.filter(r=>Number.isFinite(r.offered_cents)&&r.offered_cents>0),known=list.filter(r=>Number.isFinite(r.offered_cents)&&Number.isFinite(r.captured_cents));const captured=known.reduce((s,r)=>s+r.captured_cents,0),offered=known.reduce((s,r)=>s+r.offered_cents,0);return {category,games:list.length,considered:list.filter(r=>r.called_by_os).length,bid:list.filter(r=>r.any_bid===true).length,participation_unknown:list.filter(r=>r.any_bid==null).length,complete:list.filter(r=>r.completed).length,one_sided:list.filter(r=>r.valid_fills>0&&r.valid_fills<r.side_count).length,unfilled:list.filter(r=>r.valid_fills===0).length,offer_eligible:eligible.length,no_offer:list.filter(r=>r.offered_cents===0).length,outcome_known:known.length,outcome_missing:list.length-known.length,eligible_complete:eligible.filter(r=>r.completed).length,captured_cents:captured,offered_cents:offered,capture_ratio:offered>0?captured/offered:null,completion_rate:list.length?list.filter(r=>r.completed).length/list.length:null,eligible_completion_rate:eligible.length?eligible.filter(r=>r.completed).length/eligible.length:null};}
 const historyBytes=readFileSync(resolve(root,'grades/index.json')),history=JSON.parse(historyBytes).grades.filter(h=>rows.some(r=>r.event===h.event));
 const contract={latest:'Each indexed game exactly once, current grade only. Historical revisions never enter aggregate game counts.',completion:'Valid corrected-span pairs / all indexed games; offer-eligible denominator also shown.',capture:'Sum of stored OUTCOME.captured_cents; incomplete pairs remain zero as graded. No regrading.',offer:'Sum of stored OUTCOME.best_capturable_cents, with known/missing and zero-offer counts.',participation:'Considered = face.os nonempty. Bid = a stored PLACE_REST or REPRICE_REST in HANDS.actions. This is not an exchange-listed-universe denominator.',missing_side:'Show stored unfilled outcome, latest recorded action/tokens and explicit missing cause; do not infer intent.',history:'All stored indexed revisions, with their original rubric/letter/source. Old rules are not silently regraded.',prior_art:'Day Sheet 439695d9 / 155a1d6b; Performance & Grading 281bce1f; current operator rubric unchanged.'};
 const result={schema:'FACE_SCOREBOARD_V1',scope:'Loaded LAB games, not live trading or the entire library',contract,inputs,index_sha256:sha(indexBytes),history_sha256:sha(historyBytes),rows,summaries:[summarize(rows,'ALL'),...[...new Set(rows.map(r=>r.category))].sort().map(c=>summarize(rows.filter(r=>r.category===c),c))],history};
 const bytes=JSON.stringify(result,null,2)+'\n';writeFileSync(resolve(root,'scoreboard.json'),bytes);return {sha256:sha(bytes),bytes:Buffer.byteLength(bytes),summaries:result.summaries};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href)console.log(JSON.stringify(buildScoreboard(),null,2));
