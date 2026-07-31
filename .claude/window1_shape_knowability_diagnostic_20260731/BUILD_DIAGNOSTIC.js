"use strict";

const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const crypto = require("crypto");

const REPO = process.argv[2];
const PRIVATE = process.argv[3];
const OUT = process.argv[4];
if (!REPO || !PRIVATE || !OUT) throw new Error("usage: node script REPO PRIVATE OUT");

const EVENT_LEDGER = path.join(REPO, ".claude/window1_t2_scoring_package_prerun_20260728/IMMUTABLE_EVENT_LEDGER.jsonl");
const QUOTE_CSV = path.join(REPO, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const BAND_MAP_PATH = path.join(REPO, "arb-executor/state/band_map_v1.json");
const DRIFT_PATH = path.join(REPO, "arb-executor/state/drift_surfaces_v1.json");
const CACHE_DIR = path.join(PRIVATE, "guarded-cache-v3");
const FIVE_LEDGER = path.join(REPO, ".claude/window1_live_v4_replay/five_exact_full_stack_capacity_20260731/PER_EVENT_DECISION_LEDGER.json");

function readJson(p) { return JSON.parse(fs.readFileSync(p, "utf8")); }
function readJsonl(p) { return fs.readFileSync(p, "utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse); }
function sha256(p) { return crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex"); }
function round(v, d = 6) { if (v === null || v === undefined || !Number.isFinite(v)) return null; const m = 10 ** d; return Math.round(v * m) / m; }
function median(values) { const a = values.filter(Number.isFinite).sort((x,y)=>x-y); if (!a.length) return null; const n=a.length; return n%2?a[(n-1)/2]:(a[n/2-1]+a[n/2])/2; }
function quantiles(values) {
  const a = values.filter(Number.isFinite).sort((x,y)=>x-y);
  if (!a.length) return null;
  const at = p => a[Math.min(a.length-1, Math.floor(p*a.length))];
  return {q25:round(at(.25),3), median:round(at(.5),3), q75:round(at(.75),3), p90:round(at(.9),3)};
}
function weightedMedian(rows, valueKey, weightKey) {
  const a = rows.filter(r=>Number.isFinite(r[valueKey]) && r[weightKey]>0).sort((x,y)=>x[valueKey]-y[valueKey]);
  const total=a.reduce((s,r)=>s+r[weightKey],0); if (!total) return null;
  let acc=0; for (const r of a) { acc+=r[weightKey]; if (acc>=total/2) return r[valueKey]; }
  return a[a.length-1][valueKey];
}
function priceRegion(p) { return !Number.isInteger(p)?"UNAVAILABLE":p<=25?"le25":p<=50?"26_50":p<=75?"51_75":"ge76"; }
function netBucket(v) { return v<=-10?"dn10":v<=-3?"dn3":v<3?"flat":v<10?"up3":"up10"; }
function dipBucket(v) { return v<=2?"d0":v<=9?"d3":"d10"; }
function anchorBucket(v) { return v<=25?"a25":v<=50?"a50":v<=75?"a75":"a95"; }
function fingerprint(anchor, net, dip) { return `${anchorBucket(anchor)}|${netBucket(net)}|${dipBucket(dip)}`; }

function parseCsvSimple(p) {
  const lines=fs.readFileSync(p,"utf8").trim().split(/\r?\n/); const h=lines.shift().split(",");
  return lines.map(line=>Object.fromEntries(line.split(",").map((v,i)=>[h[i],v])));
}

const bandMap=readJson(BAND_MAP_PATH);
function assignBand(cat, anchor, net, dip) {
  const c=bandMap.cats[cat]; if (!c || c.thin || ![anchor,net,dip].every(Number.isFinite)) return null;
  const z=[anchor,net,dip].map((v,i)=>(v-c.feature_mus[i])/c.feature_sds[i]);
  let j=0,best=Infinity;
  c.centroids_z.forEach((cent,i)=>{const d=cent.reduce((s,v,k)=>s+(z[k]-v)**2,0); if(d<best){best=d;j=i;}});
  const amed=c.centroids_z[j][0]*c.feature_sds[0]+c.feature_mus[0];
  return c.bands.reduce((a,b)=>Math.abs(b.anchor_med-amed)<Math.abs(a.anchor_med-amed)?b:a).band;
}
function bandDirection(cat, band) { const c=bandMap.cats[cat]; const b=c&&c.bands.find(x=>x.band===band); return b?b.direction:null; }

const quoteRows=parseCsvSimple(QUOTE_CSV);
const qmap=new Map(quoteRows.map(r=>[`${r.event_id}/${r.leg}`,r]));
const events=readJsonl(EVENT_LEDGER);

function validSnapshot(s) {
  return s && Number.isFinite(s.ts) && Number.isInteger(s.best_bid) && Number.isInteger(s.best_ask) && s.best_bid>=1 && s.best_ask<=99 && s.best_bid<s.best_ask && Array.isArray(s.bids) && Array.isArray(s.asks) && s.bids.some(x=>x[0]===s.best_bid&&x[1]>0) && s.asks.some(x=>x[0]===s.best_ask&&x[1]>0);
}
function snapshotTimeline(raw) {
  return raw.map((s,i)=>({...s,_ordinal:i})).filter(validSnapshot).sort((a,b)=>a.ts-b.ts||a._ordinal-b._ordinal);
}
function currentAt(snaps, ts) {
  let lo=0,hi=snaps.length-1,ans=null;
  while(lo<=hi){const m=(lo+hi)>>1;if(snaps[m].ts<=ts){ans=snaps[m];lo=m+1;}else hi=m-1;} return ans;
}
function runsFor(snaps,left,cut) {
  const candidates=[]; const prior=currentAt(snaps,left); if(prior)candidates.push({...prior,_effective:left});
  for(const s of snaps){if(s.ts>left&&s.ts<=cut)candidates.push({...s,_effective:s.ts});}
  if(!candidates.length)return [];
  candidates.sort((a,b)=>a._effective-b._effective||a._ordinal-b._ordinal);
  const collapsed=[]; for(const s of candidates){if(collapsed.length&&collapsed[collapsed.length-1]._effective===s._effective)collapsed[collapsed.length-1]=s;else collapsed.push(s);}
  const intervals=[];
  for(let i=0;i<collapsed.length;i++){
    const s=collapsed[i],end=i+1<collapsed.length?collapsed[i+1]._effective:cut;
    if(end>s._effective)intervals.push({start:s._effective,end,duration:end-s._effective,bid:s.best_bid,ask:s.best_ask,last:s.last_trade>0?s.last_trade:null,spread:s.best_ask-s.best_bid,ask_depth:s.asks.reduce((a,x)=>a+(Number(x[1])||0),0),bid_depth:s.bids.reduce((a,x)=>a+(Number(x[1])||0),0),receipt:`snapshot#${s._ordinal}`});
  }
  return intervals;
}
function mergeAskRuns(intervals) {
  const out=[]; for(const r of intervals){const last=out[out.length-1];if(last&&last.ask===r.ask&&last.end===r.start){last.end=r.end;last.duration+=r.duration;}else out.push({...r});}return out;
}
function quoteFeatures(snaps,left,right) {
  const cut=Math.min(right,left+1800); const intervals=runsFor(snaps,left,cut); const askRuns=mergeAskRuns(intervals);
  if(!intervals.length)return {available:false,window_seconds:cut-left,covered_seconds:0};
  const first=intervals[0],last=intervals[intervals.length-1];
  const topChanges=intervals.slice(1).filter((r,i)=>r.bid!==intervals[i].bid||r.ask!==intervals[i].ask).length;
  const askChanges=askRuns.length-1;
  const covered=intervals.reduce((s,r)=>s+r.duration,0);
  return {available:true,window_seconds:cut-left,covered_seconds:covered,coverage_fraction:round(covered/Math.max(1,cut-left),6),first_bid:first.bid,first_ask:first.ask,last_bid:last.bid,last_ask:last.ask,last_trade:last.last,ask_net:last.ask-first.ask,ask_dip:first.ask-Math.min(...intervals.map(r=>r.ask)),ask_range:Math.max(...intervals.map(r=>r.ask))-Math.min(...intervals.map(r=>r.ask)),bid_net:last.bid-first.bid,bid_range:Math.max(...intervals.map(r=>r.bid))-Math.min(...intervals.map(r=>r.bid)),top_state_changes:topChanges,ask_changes:askChanges,state_changes_per_minute:round(topChanges/(covered/60),6),ask_max_dwell_seconds:round(Math.max(...askRuns.map(r=>r.duration)),3),ask_runs_ge10_seconds:askRuns.filter(r=>r.duration>=10).length,spread_dwell_median_cents:weightedMedian(intervals,"spread","duration"),top5_ask_depth_dwell_median:weightedMedian(intervals,"ask_depth","duration"),top5_bid_depth_dwell_median:weightedMedian(intervals,"bid_depth","duration"),first_receipt:first.receipt,last_receipt:last.receipt,quote_fingerprint:fingerprint(first.ask,last.ask-first.ask,first.ask-Math.min(...intervals.map(r=>r.ask)))};
}
function lawfulPrints(raw,left,right) {
  const seen=new Set(),out=[];
  raw.forEach((p,i)=>{const id=p.trade_id||`ordinal-${i}`; if(seen.has(id))return; seen.add(id); if(Number.isFinite(p.ts)&&p.ts>=left&&p.ts<=right&&Number.isInteger(p.price)&&p.price>=1&&p.price<=99&&Number(p.size)>0)out.push({...p,_ordinal:i});});
  return out.sort((a,b)=>a.ts-b.ts||a._ordinal-b._ordinal);
}
function printShape(cat,anchor,prints) {
  if(!prints.length||!Number.isFinite(anchor))return null;
  const first=prints[0].price; let low=Infinity; const calls=[];
  for(let i=0;i<prints.length;i++){low=Math.min(low,prints[i].price); const net=prints[i].price-first,dip=anchor-low; calls.push({print_count:i+1,ts:prints[i].ts,band:assignBand(cat,anchor,net,dip),net,dip,price:prints[i].price,trade_id:prints[i].trade_id});}
  const final=calls[calls.length-1].band; let stable=null;
  for(let i=0;i<calls.length;i++){if(calls[i].band===final&&calls.slice(i).every(x=>x.band===final)){stable=calls[i];break;}}
  return {first_print:prints[0],last_print:prints[prints.length-1],print_count:prints.length,final_band:final,final_direction:bandDirection(cat,final),final_net:calls[calls.length-1].net,final_dip:calls[calls.length-1].dip,stable,call_changes:calls.slice(1).filter((x,i)=>x.band!==calls[i].band).length,calls};
}

const replayEventNames=new Set([
  "KXATPCHALLENGERMATCH-26JUL19HURBIG",
  "KXATPCHALLENGERMATCH-26JUL19NIKVRB",
  "KXATPMATCH-26JUL12LAJVAN",
  "KXWTACHALLENGERMATCH-26JUL16BRAVED",
  "KXWTAMATCH-26JUL20KORJIM",
]);
const legs=[]; const eventCache=new Map(); const eventMeta=new Map(events.map(e=>[e.event_id,e]));
for(let ei=0;ei<events.length;ei++){
  const e=events[ei]; const cp=path.join(CACHE_DIR,`${e.event_id}.json.gz`); if(!fs.existsSync(cp))throw new Error(`missing cache ${e.event_id}`);
  const cache=JSON.parse(zlib.gunzipSync(fs.readFileSync(cp))); if(replayEventNames.has(e.event_id))eventCache.set(e.event_id,cache);
  for(const leg of e.legs){const q=qmap.get(`${e.event_id}/${leg.leg}`);if(!q)throw new Error(`missing quote row ${e.event_id}/${leg.leg}`);const raw=cache.legs.find(x=>x.leg===leg.leg);if(!raw)throw new Error(`missing cache leg ${e.event_id}/${leg.leg}`);
    const left=Number(q.left_ts),right=Number(q.right_ts),scheduled=Number(q.scheduled_start_ts);const snaps=snapshotTimeline(raw.snapshots||[]);const discovery=snaps.find(s=>s.ts>=left&&s.ts<=right)||null;const gate=discovery?discovery.ts:null;const prints=lawfulPrints(raw.prints||[],left,right);const anchor=q.window1_open_cents===""?null:Number(q.window1_open_cents);const shape=printShape(e.category,anchor,prints);const prints30=gate===null?[]:prints.filter(p=>p.ts<=Math.min(right,gate+1800));const shape30=printShape(e.category,anchor,prints30);const quotes=gate===null?{available:false,window_seconds:null,covered_seconds:0}:quoteFeatures(snaps,gate,right);const firstBid=discovery?discovery.best_bid:null;const region=priceRegion(firstBid);
    legs.push({event_id:e.event_id,event_date:e.event_date,category:e.category,leg_id:leg.leg,ticker:leg.ticker,left_ts:left,right_ts:right,scheduled_start_ts:scheduled,discovery_gate_ts:gate,discovery_tminus_scheduled_minutes:gate===null?null:round((scheduled-gate)/60,6),discovery_tminus_bell_minutes:gate===null?null:round((right-gate)/60,6),discovery_receipt:discovery?`guarded-cache-v3/${e.event_id}.json.gz#${leg.leg}/snapshot-${discovery._ordinal}`:null,price_region:region,price_region_source:"first lawful positive-size non-crossed guarded-cache V3 BBO at or after the Window-1 left edge",anchor_cents:anchor,anchor_source:"frozen Window-1 price-path open",lawful_true_print_count:prints.length,prints_available_at_discovery:gate===null?0:prints.filter(p=>p.ts<=gate).length,first_30m_print_count:prints30.length,first_30m_provisional_band:shape30?shape30.final_band:null,first_print_ts:shape?shape.first_print.ts:null,first_print_trade_id:shape?shape.first_print.trade_id:null,first_print_lag_seconds:shape&&gate!==null?round(Math.max(0,shape.first_print.ts-gate),6):null,first_print_was_available_at_gate:Boolean(shape&&gate!==null&&shape.first_print.ts<=gate),first_print_tminus_scheduled_minutes:shape?round((scheduled-shape.first_print.ts)/60,6):null,first_print_tminus_bell_minutes:shape?round((right-shape.first_print.ts)/60,6):null,final_band:shape?shape.final_band:null,final_direction:shape?shape.final_direction:null,final_net_cents:shape?shape.final_net:null,final_dip_cents:shape?shape.final_dip:null,band_call_changes:shape?shape.call_changes:null,first_call_matches_final:shape?shape.calls[0].band===shape.final_band:null,stable_print_count:shape?shape.stable.print_count:null,stable_ts:shape?shape.stable.ts:null,stable_lag_seconds:shape&&gate!==null?round(Math.max(0,shape.stable.ts-gate),6):null,stable_was_available_at_gate:Boolean(shape&&gate!==null&&shape.stable.ts<=gate),stable_tminus_scheduled_minutes:shape?round((scheduled-shape.stable.ts)/60,6):null,stable_tminus_bell_minutes:shape?round((right-shape.stable.ts)/60,6):null,stable_band:shape?shape.stable.band:null,quote_first_30m:quotes,cache_path:`guarded-cache-v3/${e.event_id}.json.gz`});
  }
  if((ei+1)%100===0)console.error(`processed ${ei+1}/${events.length}`);
}

function groupBy(rows,keyfn){const m=new Map();for(const r of rows){const k=keyfn(r);if(!m.has(k))m.set(k,[]);m.get(k).push(r);}return m;}
const timingCells={};
for(const [key,rows] of groupBy(legs,r=>`${r.category}|${r.price_region}`)){
  const printed=rows.filter(r=>r.first_print_ts!==null),stable=rows.filter(r=>r.stable_ts!==null);
  const printedWithGate=printed.filter(r=>r.first_print_lag_seconds!==null),stableWithGate=stable.filter(r=>r.stable_lag_seconds!==null);
  timingCells[key]={category:rows[0].category,price_region:rows[0].price_region,leg_count:rows.length,thin:rows.length<10,with_discovery_gate:rows.filter(r=>r.discovery_gate_ts!==null).length,no_discovery_bbo:rows.filter(r=>r.discovery_gate_ts===null).length,with_lawful_print:printed.length,no_lawful_print:rows.length-printed.length,first_print_available_at_gate:printed.filter(r=>r.first_print_was_available_at_gate).length,first_print_within_30m:printedWithGate.filter(r=>r.first_print_lag_seconds<=1800).length,first_print_within_60m:printedWithGate.filter(r=>r.first_print_lag_seconds<=3600).length,first_print_lag_minutes:quantiles(printedWithGate.map(r=>r.first_print_lag_seconds/60)),first_call_matches_final:printed.filter(r=>r.first_call_matches_final).length,first_call_matches_final_rate:printed.length?round(printed.filter(r=>r.first_call_matches_final).length/printed.length,6):null,stable_already_available_at_gate:stable.filter(r=>r.stable_was_available_at_gate).length,stable_print_count:quantiles(stable.map(r=>r.stable_print_count)),stable_lag_minutes:quantiles(stableWithGate.map(r=>r.stable_lag_seconds/60)),band_call_change_count:quantiles(stable.map(r=>r.band_call_changes)),final_band_counts:Object.fromEntries([...groupBy(printed,r=>r.final_band).entries()].map(([b,x])=>[b,x.length]).sort())};
}

const quoteEligible=legs.filter(r=>r.final_band&&r.quote_first_30m.available&&r.quote_first_30m.coverage_fraction===1);
const quoteCells={};
for(const [key,rows] of groupBy(quoteEligible,r=>`${r.category}|${r.price_region}|${r.quote_first_30m.quote_fingerprint}`)){
  const counts=Object.fromEntries([...groupBy(rows,r=>r.final_band).entries()].map(([b,x])=>[b,x.length]).sort());const sorted=Object.entries(counts).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]));
  quoteCells[key]={category:rows[0].category,price_region:rows[0].price_region,quote_fingerprint:rows[0].quote_first_30m.quote_fingerprint,n:rows.length,final_band_counts:counts,modal_band:sorted[0][0],purity:round(sorted[0][1]/rows.length,6),callable_under_existing_recognition_law:rows.length>=10&&sorted[0][1]/rows.length>=.6};
}
const quoteSummary={};
for(const [key,rows] of groupBy(quoteEligible,r=>`${r.category}|${r.price_region}`)){
  let callable=0,correct=0,baseCorrect=0;
  for(const r of rows){const peers=rows.filter(x=>x.event_id!==r.event_id);const baseCounts=[...groupBy(peers,x=>x.final_band).entries()].map(([b,x])=>[b,x.length]).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]));if(baseCounts.length&&baseCounts[0][0]===r.final_band)baseCorrect++;
    const cellPeers=peers.filter(x=>x.quote_first_30m.quote_fingerprint===r.quote_first_30m.quote_fingerprint);const counts=[...groupBy(cellPeers,x=>x.final_band).entries()].map(([b,x])=>[b,x.length]).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]));if(cellPeers.length>=10&&counts.length&&counts[0][1]/cellPeers.length>=.6){callable++;if(counts[0][0]===r.final_band)correct++;}}
  quoteSummary[key]={category:rows[0].category,price_region:rows[0].price_region,n:rows.length,thin:rows.length<10,loo_quote_cell_callable:callable,loo_quote_cell_correct:correct,loo_quote_cell_accuracy:callable?round(correct/callable,6):null,loo_category_region_majority_correct:baseCorrect,loo_category_region_majority_accuracy:rows.length?round(baseCorrect/rows.length,6):null};
}
const quoteFeatureByBand={};
for(const [key,rows] of groupBy(quoteEligible,r=>`${r.category}|${r.price_region}|${r.final_band}`)){
  const f=rows.map(r=>r.quote_first_30m);quoteFeatureByBand[key]={category:rows[0].category,price_region:rows[0].price_region,final_band:rows[0].final_band,n:rows.length,thin:rows.length<10,ask_net_cents:quantiles(f.map(x=>x.ask_net)),ask_dip_cents:quantiles(f.map(x=>x.ask_dip)),ask_changes:quantiles(f.map(x=>x.ask_changes)),state_changes_per_minute:quantiles(f.map(x=>x.state_changes_per_minute)),ask_max_dwell_seconds:quantiles(f.map(x=>x.ask_max_dwell_seconds)),spread_dwell_median_cents:quantiles(f.map(x=>x.spread_dwell_median_cents)),top5_ask_depth_dwell_median:quantiles(f.map(x=>x.top5_ask_depth_dwell_median))};
}

const byEvent=groupBy(legs,r=>r.event_id);const silentRows=[];
for(const [eventId,pair] of byEvent){if(pair.length!==2)continue;for(let i=0;i<2;i++){const printed=pair[i],silent=pair[1-i];if(printed.first_30m_print_count>0&&silent.first_30m_print_count===0&&silent.final_band){silentRows.push({event_id:eventId,category:printed.category,printed_leg:printed.leg_id,silent_leg:silent.leg_id,silent_price_region:silent.price_region,printed_30m_print_count:printed.first_30m_print_count,printed_30m_band:printed.first_30m_provisional_band,silent_final_band:silent.final_band,printed_first_ts:printed.first_print_ts,silent_first_ts:silent.first_print_ts});}}
}
const siblingCells={};for(const [key,rows] of groupBy(silentRows,r=>`${r.category}|${r.silent_price_region}|${r.printed_30m_band}`)){const counts=Object.fromEntries([...groupBy(rows,r=>r.silent_final_band).entries()].map(([b,x])=>[b,x.length]).sort());const sorted=Object.entries(counts).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]));siblingCells[key]={category:rows[0].category,silent_price_region:rows[0].silent_price_region,printed_30m_band:rows[0].printed_30m_band,n:rows.length,silent_final_band_counts:counts,modal_band:sorted[0][0],purity:round(sorted[0][1]/rows.length,6),callable_under_existing_recognition_law:rows.length>=10&&sorted[0][1]/rows.length>=.6};}
const siblingSummary={};for(const [key,rows] of groupBy(silentRows,r=>`${r.category}|${r.silent_price_region}`)){let callable=0,correct=0,baseCorrect=0;for(const r of rows){const peers=rows.filter(x=>x.event_id!==r.event_id);const bc=[...groupBy(peers,x=>x.silent_final_band).entries()].map(([b,x])=>[b,x.length]).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]));if(bc.length&&bc[0][0]===r.silent_final_band)baseCorrect++;const cp=peers.filter(x=>x.printed_30m_band===r.printed_30m_band);const cc=[...groupBy(cp,x=>x.silent_final_band).entries()].map(([b,x])=>[b,x.length]).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]));if(cp.length>=10&&cc.length&&cc[0][1]/cp.length>=.6){callable++;if(cc[0][0]===r.silent_final_band)correct++;}}siblingSummary[key]={category:rows[0].category,silent_price_region:rows[0].silent_price_region,n:rows.length,thin:rows.length<10,loo_sibling_cell_callable:callable,loo_sibling_cell_correct:correct,loo_sibling_cell_accuracy:callable?round(correct/callable,6):null,loo_category_region_majority_accuracy:rows.length?round(baseCorrect/rows.length,6):null};}

const wrapper=readJson(FIVE_LEDGER);const replay=JSON.parse(zlib.gunzipSync(Buffer.from(wrapper.gzip_base64,"base64")));const wantedPlacement=new Set(["LAJ","JIM","VED"]),wantedRest=new Set(["BIG","VAN","BRA","KOR"]);const placement=[];const resting=[];
function bookReceipt(eventId,legId,ts){const raw=eventCache.get(eventId).legs.find(x=>x.leg===legId);const snaps=snapshotTimeline(raw.snapshots||[]);const s=currentAt(snaps,ts);if(!s)return null;let start=s.ts,end=null;for(let i=s._ordinal-1;i>=0;i--){const x=raw.snapshots[i];if(!validSnapshot(x))continue;if(x.best_ask!==s.best_ask)break;start=x.ts;}for(let i=s._ordinal+1;i<raw.snapshots.length;i++){const x=raw.snapshots[i];if(validSnapshot(x)&&x.best_ask!==s.best_ask){end=x.ts;break;}}return {ts:s.ts,best_bid:s.best_bid,best_ask:s.best_ask,last_traded:s.last_trade>0?s.last_trade:null,spread:s.best_ask-s.best_bid,ask_dwell_start_ts:start,ask_dwell_end_ts:end,ask_dwell_seconds:end===null?null:round(end-start,3),top5_bid_depth:s.bids.reduce((a,x)=>a+(Number(x[1])||0),0),top5_ask_depth:s.asks.reduce((a,x)=>a+(Number(x[1])||0),0),source_receipt:`guarded-cache-v3/${eventId}.json.gz#${legId}/snapshot-${s._ordinal}`};}
for(const e of replay){for(const [legId,l] of Object.entries(e.legs)){if(wantedPlacement.has(legId)){const placementActions=l.actions.filter(x=>["QUIET_BOOK_ANCHOR","PER_TICK_ASK_BREATHING","ORIENTATION_CONDITIONED_INITIAL_TREE"].includes(x.rule));const fillLeadingTs=l.fill?Math.max(...placementActions.filter(x=>x.ts<=l.fill.evidence_ts&&x.after===l.fill.price).map(x=>x.ts)):-Infinity;for(const a of placementActions){const book=bookReceipt(e.event_id,legId,a.ts);placement.push({event_id:e.event_id,category:e.category,leg_id:legId,credited_fill_price:l.fill&&l.fill.price,fill_leading_placement:Boolean(l.fill&&a.after===l.fill.price&&a.ts===fillLeadingTs),decision:a,book_observation:book,one_cent_spread_gate:{applies:a.rule==="QUIET_BOOK_ANCHOR",required:a.rule==="QUIET_BOOK_ANCHOR"?true:false,observed_spread:book&&book.spread,enforced:a.rule==="QUIET_BOOK_ANCHOR"?Boolean(book&&book.spread===1):"NOT_APPLICABLE",source:"arb-executor/analysis/build_window1_five_exact_full_stack.js#quiet-anchor-condition"}});}}
    if(wantedRest.has(legId)){const priceActions=l.actions.filter(x=>Number.isInteger(x.after)&&["QUIET_BOOK_ANCHOR","PER_TICK_ASK_BREATHING","ORIENTATION_CONDITIONED_INITIAL_TREE","FALLER_PATIENCE_RELEASE"].includes(x.rule));const final=priceActions[priceActions.length-1]||null;resting.push({event_id:e.event_id,category:e.category,leg_id:legId,resting_price_history:priceActions.map(a=>({ts:a.ts,tminus_scheduled_minutes:a.tminus_scheduled_minutes,tminus_bell_minutes:a.tminus_bell_minutes,rule:a.rule,before:a.before,after:a.after,book_observation:bookReceipt(e.event_id,legId,a.ts),source:a.source})),final_resting_price_cents:final?final.after:null,lowest_ask_held_10s_cents:l.own_ask_reachable_low_cents,resting_minus_lowest_10s_ask_cents:final?final.after-l.own_ask_reachable_low_cents:null,cents_below_lowest_10s_ask:final?l.own_ask_reachable_low_cents-final.after:null,accounting_status:l.accounting_status});}}
}

const nikvrb=legs.filter(r=>r.event_id.includes("NIKVRB"));
fs.mkdirSync(OUT,{recursive:true});
const outputs={
  "LEG_SHAPE_TIMING_LEDGER.json":legs,
  "SHAPE_KNOWABILITY_BY_CATEGORY_PRICE_REGION.json":{schema_version:"WINDOW1_SHAPE_KNOWABILITY_V1",population:{events:events.length,legs:legs.length},laws:{discovery_gate:"first lawful positive-size non-crossed guarded-cache V3 BBO at or after the Window-1 left edge",shape_features:"frozen traded-price anchor, signed net, and dip; quotes excluded",first_callable:"one lawful positive-size true print permits a provisional nearest-centroid call",stable_definition:"earliest print after which every later cumulative nearest-centroid assignment through guarded Window 1 equals the final assignment; ex-post diagnostic, not causally knowable at that instant",quantile:"sorted value at floor(p*n), matching frozen drift-surface convention",price_region:"discovery-gate bid: <=25 le25; <=50 26_50; <=75 51_75; otherwise ge76",thin:"n<10"},cells:timingCells,nikvrb},
  "QUOTE_ONLY_PREPRINT_DIAGNOSTIC.json":{schema_version:"WINDOW1_QUOTE_ONLY_PREPRINT_DIAGNOSTIC_V1",window:"first 30 minutes after guarded gate",evidence:"BBO only; no print field participates in quote fingerprint",recognition_law:"existing anchor/net/dip bins; cells require leave-one-event-out n>=10 and modal purity>=60%; descriptive development recut, not a frozen executable classifier",summary_by_category_price_region:quoteSummary,fingerprint_cells:quoteCells,feature_distributions_by_final_band:quoteFeatureByBand,existing_system_fit_status:{band_taxonomy:"PRINT_DERIVED_ONLY",range_spectrum_quote_fields:"STORED_DESCRIPTIVE_SPREAD_AND_WAKE; NOT_BAND_INPUT",drift_surface_quote_paths:"OUTCOME_CONDITIONED_BY_EX_POST_PRINT_BAND; NOT_PREPRINT_CLASSIFIER",quote_reachability:"ASK_DWELL_REACHABILITY; NOT_SHAPE_CLASSIFIER",down_resume_census:"QUOTE_EPISODES; NOT_BAND_CLASSIFIER"}},
  "SIBLING_SILENT_LEG_DIAGNOSTIC.json":{schema_version:"WINDOW1_SIBLING_SILENT_LEG_DIAGNOSTIC_V1",definition:"during first 30 minutes after guarded gate, exactly one leg has lawful true prints; printed leg provisional band is tested as a descriptor of silent sibling final print-derived band",rows:silentRows,summary_by_category_silent_price_region:siblingSummary,cells:siblingCells,historical_full_corpus_pair_mirror_by_category:Object.fromEntries(Object.entries(bandMap.cats).map(([cat,v])=>[cat,{n:v.n,thin:Boolean(v.thin),pair_mirror:v.pair_mirror||{}}]))},
  "ANCHOR_PLACEMENT_DIAGNOSTIC.json":{schema_version:"WINDOW1_ANCHOR_PLACEMENT_DIAGNOSTIC_V1",placement_rows:placement,resting_vs_10s_ask_rows:resting,gate_law:{quiet_book_anchor:"requires no last print and exactly one-cent BBO spread; target=min(round(mid),ask-1)",per_tick_ask_breathing:"does not require one-cent spread; target=min(frozen ceiling,ask-1), except stale marketable order follows ask",orientation_initial:"does not require one-cent spread; target=min(existing ceiling,orientation aim,ask-1)"}},
};
for(const [name,data] of Object.entries(outputs))fs.writeFileSync(path.join(OUT,name),JSON.stringify(data,null,2)+"\n");
const duplicateLegKeys=legs.length-new Set(legs.map(r=>`${r.event_id}/${r.leg_id}`)).size;
const timingLegConservation=Object.values(timingCells).reduce((s,r)=>s+r.leg_count,0);
const validation={schema_version:"WINDOW1_SHAPE_DIAGNOSTIC_VALIDATION_V1",passed:duplicateLegKeys===0&&timingLegConservation===1608&&events.length===804&&legs.length===1608&&placement.length===6&&resting.length===4,checks:{event_count:{expected:804,actual:events.length},leg_count:{expected:1608,actual:legs.length},duplicate_event_leg_keys:{expected:0,actual:duplicateLegKeys},timing_cell_leg_conservation:{expected:1608,actual:timingLegConservation},timing_cell_count:Object.keys(timingCells).length,quote_fingerprint_cell_count:Object.keys(quoteCells).length,silent_sibling_rows:silentRows.length,placement_diagnostic_rows:{expected:6,actual:placement.length},resting_vs_10s_ask_rows:{expected:4,actual:resting.length},stable_band_mismatches:legs.filter(r=>r.final_band!==r.stable_band).map(r=>`${r.event_id}/${r.leg_id}`),negative_first_print_lags:legs.filter(r=>r.first_print_lag_seconds<0).map(r=>`${r.event_id}/${r.leg_id}`)},scope:"descriptive read-only development/backwalk census; no strategy/runtime/scorer change"};
if(!validation.passed||validation.checks.stable_band_mismatches.length||validation.checks.negative_first_print_lags.length)throw new Error(`validation failed ${JSON.stringify(validation)}`);
fs.writeFileSync(path.join(OUT,"VALIDATION_RECEIPT.json"),JSON.stringify(validation,null,2)+"\n");
fs.writeFileSync(path.join(OUT,"FORBIDDEN_ACCESS_RECEIPT.json"),JSON.stringify({schema_version:"WINDOW1_SHAPE_DIAGNOSTIC_FORBIDDEN_ACCESS_V1",development_dates:"2026-07-12..2026-07-20",holdout_access:false,live_access:false,production_access:false,network_access:false,order_access:false,position_access:false,scorer_imported:false,scorer_invoked:false,strategy_or_runtime_modified:false,quiet_book_anchor_modified:false,statement:"Only frozen local development event, boundary, guarded-cache V3 print/BBO, band-map, drift-surface, quote-reachability, and five-game replay artifacts were read."},null,2)+"\n");
const sourceFiles=[EVENT_LEDGER,QUOTE_CSV,BAND_MAP_PATH,DRIFT_PATH,FIVE_LEDGER,path.join(REPO,"arb-executor/analysis/band_taxonomy.py"),path.join(REPO,"arb-executor/analysis/drift_surfaces.py"),path.join(REPO,"arb-executor/analysis/range_spectrum_build.py"),path.join(REPO,"arb-executor/analysis/build_window1_five_exact_full_stack.js")];
const cacheNames=events.map(e=>`${e.event_id}.json.gz`);const cacheHashes=cacheNames.map(n=>({path:`guarded-cache-v3/${n}`,sha256:sha256(path.join(CACHE_DIR,n)),bytes:fs.statSync(path.join(CACHE_DIR,n)).size}));
fs.writeFileSync(path.join(OUT,"SOURCE_HASH_MANIFEST.json"),JSON.stringify({schema_version:"WINDOW1_SHAPE_DIAGNOSTIC_SOURCE_HASH_MANIFEST_V1",committed_sources:sourceFiles.map(p=>({path:path.relative(REPO,p).replaceAll("\\","/"),sha256:sha256(p),bytes:fs.statSync(p).size})),private_guarded_cache:{root_label:"OMI-Window1-private/fit-local/guarded-cache-v3",file_count:cacheHashes.length,files:cacheHashes}},null,2)+"\n");
const artifactFiles=fs.readdirSync(OUT).filter(n=>n!=="ARTIFACT_HASH_MANIFEST.json").sort();
fs.writeFileSync(path.join(OUT,"ARTIFACT_HASH_MANIFEST.json"),JSON.stringify({schema_version:"WINDOW1_SHAPE_DIAGNOSTIC_ARTIFACT_HASH_MANIFEST_V1",files:artifactFiles.map(n=>({path:n,sha256:sha256(path.join(OUT,n)),bytes:fs.statSync(path.join(OUT,n)).size}))},null,2)+"\n");
console.log(JSON.stringify({events:events.length,legs:legs.length,timing_cells:Object.keys(timingCells).length,quote_cells:Object.keys(quoteCells).length,silent_rows:silentRows.length,placement_rows:placement.length,resting_rows:resting.length,output:OUT},null,2));
