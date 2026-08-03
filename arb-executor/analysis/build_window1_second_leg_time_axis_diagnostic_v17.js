#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");
const { EXCLUDED_EVENTS } = require("./build_window1_quote_shape_coherent_library_v12.js");

const args = process.argv.slice(2), value = (name, fallback) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
const repo = path.resolve(value("--repo", "."));
const privateRoot = path.resolve(value("--private-root", "C:/Users/omigr/OMI-Window1-private"));
const input = path.resolve(value("--events", path.join(repo, ".claude/window1_live_v4_replay/pair_coupling_diagnostic_v16_20260803/PAIR_FLOOR_COUPLING_EVENT_LEDGER.jsonl.gz")));
const output = path.resolve(value("--output", path.join(repo, ".claude/window1_live_v4_replay/second_leg_x_pricer_v17_20260803")));
const flowContractPath = path.join(repo, ".claude/window1_live_v4_replay/aim_contract_20260730/FLOW_STATE_ACTIVATION_CONTRACT.json");
const printsPath = path.join(privateRoot, "fit-local/prints.jsonl"), ticksRoot = path.join(privateRoot, "fit-local/ticks");
const MIN_N = 20, WINDOWS = [60, 300, 900, 1800];

function canonical(x) { return `${JSON.stringify(x, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function jsonlGz(file) { return zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim().split(/\r?\n/).map(JSON.parse); }
function quantile(values, p) { const x = values.filter(Number.isFinite).sort((a, b) => a - b); return x.length ? x[Math.floor((x.length - 1) * p)] : null; }
function dist(values) { const x = values.filter(Number.isFinite), p10 = quantile(x,.1), p90 = quantile(x,.9); return { n:x.length, unavailable:values.length-x.length, min:x.length?Math.min(...x):null, p10, p25:quantile(x,.25), median:quantile(x,.5), p75:quantile(x,.75), p90, max:x.length?Math.max(...x):null, p90_p10_width:p10===null?null:p90-p10 }; }
function solve(matrix, vector) { const n=vector.length, a=matrix.map((row,i)=>[...row,vector[i]]); for(let c=0;c<n;c++){let p=c;for(let r=c+1;r<n;r++)if(Math.abs(a[r][c])>Math.abs(a[p][c]))p=r;if(Math.abs(a[p][c])<1e-10)return null;[a[c],a[p]]=[a[p],a[c]];const d=a[c][c];for(let j=c;j<=n;j++)a[c][j]/=d;for(let r=0;r<n;r++)if(r!==c){const f=a[r][c];for(let j=c;j<=n;j++)a[r][j]-=f*a[c][j];}}return a.map(r=>r[n]); }
function fit(rows, features) { const clean=rows.filter(r=>Number.isFinite(r.target)&&features.every(f=>Number.isFinite(r[f]))); if(clean.length<features.length+2)return null; const p=features.length+1, xtx=Array.from({length:p},()=>Array(p).fill(0)), xty=Array(p).fill(0); for(const r of clean){const x=[1,...features.map(f=>r[f])];for(let i=0;i<p;i++){xty[i]+=x[i]*r.target;for(let j=0;j<p;j++)xtx[i][j]+=x[i]*x[j];}}const b=solve(xtx,xty);return b?{predict:r=>b[0]+features.reduce((s,f,i)=>s+b[i+1]*r[f],0),coefficients:Object.fromEntries([['intercept',b[0]],...features.map((f,i)=>[f,b[i+1]])]),n:clean.length}:null; }
function loo(rows, features) { const out=[];for(let i=0;i<rows.length;i++){const target=rows[i];if(!Number.isFinite(target.target)||features.some(f=>!Number.isFinite(target[f])))continue;const model=fit(rows.filter((_,j)=>j!==i),features);if(model)out.push(target.target-model.predict(target));}return out; }
function parseEt(v) { const m=String(v).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/);if(!m)return null;let h=+m[4];if(m[7]==='AM'&&h===12)h=0;if(m[7]==='PM'&&h!==12)h+=12;return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(h).padStart(2,'0')}:${m[5]}:${m[6]}-04:00`)/1000; }
function tickerFromReceipt(receipt) { const m=String(receipt||'').match(/([^/\\]+)\.csv\.gz#row-/); return m?m[1]:null; }
function parseCsv(text) { const lines=text.trimEnd().split(/\r?\n/),h=lines.shift().split(',');return lines.map(line=>Object.fromEntries(line.split(',').map((v,i)=>[h[i],v]))); }
function group(rows,key){const m=new Map();for(const r of rows){const k=key(r);if(!m.has(k))m.set(k,[]);m.get(k).push(r);}return m;}

async function hydratePrintFlow(rows) {
  const byTicker=new Map(); for(const r of rows)for(const role of ['first','sibling']){const ticker=r[`${role}_ticker`];if(!byTicker.has(ticker))byTicker.set(ticker,[]);byTicker.get(ticker).push({row:r,role});}
  for(const r of rows)for(const role of ['first','sibling']){for(const w of WINDOWS)r[`${role}_prints_${w}s`]=0;r[`_${role}_seen_trade_ids`]=new Set();}
  const stream=fs.createReadStream(printsPath,{encoding:'utf8'}), rl=readline.createInterface({input:stream,crlfDelay:Infinity});
  for await(const line of rl){const tm=line.match(/"ticker":"([^"]+)"/);if(!tm||!byTicker.has(tm[1]))continue;let p;try{p=JSON.parse(line);}catch{continue;}if(p.true_print!==true||!p.trade_id||!p.exchange_ts)continue;const ts=Date.parse(p.exchange_ts)/1000;if(!Number.isFinite(ts))continue;for(const q of byTicker.get(tm[1])){const key=`${q.role}|${p.trade_id}`,seen=q.row[`_${q.role}_seen_trade_ids`];if(seen.has(key)||ts>q.row.first_floor_ts||ts<q.row.first_floor_ts-1800)continue;seen.add(key);const age=q.row.first_floor_ts-ts;for(const w of WINDOWS)if(age<=w)q.row[`${q.role}_prints_${w}s`]+=1;}}
  for(const r of rows)for(const role of ['first','sibling'])delete r[`_${role}_seen_trade_ids`];
}

function hydrateSpreadFlow(rows) {
  for(const r of rows)for(const role of ['first','sibling']){
    const ticker=r[`${role}_ticker`],file=path.join(ticksRoot,`${ticker}.csv.gz`), values=[];
    if(!fs.existsSync(file)){r[`${role}_spread_status`]='TICK_SOURCE_UNAVAILABLE';continue;}
    for(const raw of parseCsv(zlib.gunzipSync(fs.readFileSync(file)).toString('utf8'))){const ts=parseEt(raw.ts_et),bid=Number(raw.bid_1),ask=Number(raw.ask_1);if(!Number.isFinite(ts)||ts>r.first_floor_ts||ts<r.first_floor_ts-1800||!Number.isInteger(bid)||!Number.isInteger(ask)||bid>ask)continue;values.push({ts,spread:ask-bid});}
    values.sort((a,b)=>a.ts-b.ts);const latest=values[values.length-1];r[`${role}_current_spread`]=latest?.spread??null;
    for(const w of [300,900,1800]){const x=values.filter(v=>r.first_floor_ts-v.ts<=w).map(v=>v.spread);r[`${role}_median_spread_${w}s`]=quantile(x,.5);r[`${role}_tightening_${w}s`]=Number.isFinite(r[`${role}_current_spread`])&&Number.isFinite(r[`${role}_median_spread_${w}s`])?r[`${role}_median_spread_${w}s`]-r[`${role}_current_spread`]:null;}
    r[`${role}_spread_status`]=values.length?'AVAILABLE':'NO_LAWFUL_BOOK_IN_FLOW_WINDOW';
  }
  for(const r of rows){for(const w of WINDOWS)r[`pair_prints_${w}s`]=r[`first_prints_${w}s`]+r[`sibling_prints_${w}s`];for(const w of [300,900,1800])r[`pair_tightening_${w}s`]=Number.isFinite(r[`first_tightening_${w}s`])&&Number.isFinite(r[`sibling_tightening_${w}s`])?r[`first_tightening_${w}s`]+r[`sibling_tightening_${w}s`]:null;}
}

function modelReceipt(cellRows, features) { const unconditional=dist(cellRows.map(r=>r.target)), residual=dist(loo(cellRows,features));return {features,n:cellRows.length,usable:cellRows.length>=MIN_N&&residual.n>=MIN_N,unconditional_target_distribution:unconditional,leave_one_event_out_residual_distribution:residual,p90_p10_uncertainty_reduction_cents:unconditional.p90_p10_width===null||residual.p90_p10_width===null?null:unconditional.p90_p10_width-residual.p90_p10_width,conclusion:cellRows.length<MIN_N||residual.n<MIN_N?'THIN_NOT_INTERPRETABLE':residual.p90_p10_width<unconditional.p90_p10_width?'TIGHTER':'NOT_TIGHTER'}; }
function partitions(rows,keyFn){return [...group(rows,keyFn)].sort(([a],[b])=>a.localeCompare(b)).map(([partition,x])=>({partition,n:x.length,tests:{leg_two_own_t_minus_scheduled:modelReceipt(x,['leg2_tminus_scheduled']),leg_two_own_t_minus_actual_bell:modelReceipt(x,['leg2_tminus_bell']),leg_one_floor_t_minus_scheduled:modelReceipt(x,['leg1_tminus_scheduled']),leg_one_floor_t_minus_actual_bell:modelReceipt(x,['leg1_tminus_bell']),climber_first_ordering:modelReceipt(x.filter(r=>Number.isFinite(r.climber_first_binary)),['climber_first_binary']),prints_per_interval:Object.fromEntries(WINDOWS.map(w=>[`${w}s`,modelReceipt(x,[`pair_prints_${w}s`])])),spread_tightening:Object.fromEntries([300,900,1800].map(w=>[`${w}s`,modelReceipt(x,[`pair_tightening_${w}s`])])),joint_flow_state:modelReceipt(x,[...WINDOWS.map(w=>`pair_prints_${w}s`),...[300,900,1800].map(w=>`pair_tightening_${w}s`)])}}));}

async function main(){
  const sourceBytes=fs.readFileSync(input), events=jsonlGz(input), rows=[];
  for(const event of events){const f=event.floors?.ASK_CAPACITY;if(f?.status!=='STRICTLY_ASYNCHRONOUS')continue;const p=f.prediction_row;rows.push({event_id:event.event_id,category:event.category,starting_price_split:event.starting_price_split,fit_excluded:EXCLUDED_EVENTS.includes(event.event_id),first_leg_price_region:p.first_leg_price_region,target:p.sibling_eventual_floor_cents,first_floor_ts:f.first.proof.evidence_ts,leg1_tminus_scheduled:f.first.clock.t_minus_scheduled_seconds,leg1_tminus_bell:f.first.clock.t_minus_actual_bell_seconds,leg2_tminus_scheduled:f.second.clock.t_minus_scheduled_seconds,leg2_tminus_bell:f.second.clock.t_minus_actual_bell_seconds,climber_first:f.climbing_leg_first,climber_first_binary:f.climbing_leg_first===true?1:f.climbing_leg_first===false?0:null,first_ticker:tickerFromReceipt(f.first.proof.receipt)||`${event.event_id}-${f.first.leg_id}`,sibling_ticker:tickerFromReceipt(f.sibling_state_at_first_floor?.receipt)||`${event.event_id}-${f.second.leg_id}`});}
  const fitRows=rows.filter(r=>!r.fit_excluded);await hydratePrintFlow(fitRows);hydrateSpreadFlow(fitRows);
  const receipt={schema_version:'WINDOW1_SECOND_LEG_TIME_AND_FLOW_DIAGNOSTIC_V17',score_free:true,behavior_consumed:false,fit_population:{strictly_asynchronous_ask_floor_rows:rows.length,fit_rows:fitRows.length,excluded_exact_start_events:EXCLUDED_EVENTS,minimum_interpretable_n:MIN_N},tests_are_separate_not_collapsed:true,climber_first_resolved:{true:fitRows.filter(r=>r.climber_first===true).length,false:fitRows.filter(r=>r.climber_first===false).length,unresolved:fitRows.filter(r=>r.climber_first==='UNRESOLVED_DIRECTION').length},flow_contract:{path:path.relative(repo,flowContractPath).replace(/\\/g,'/'),sha256:sha256(fs.readFileSync(flowContractPath)),trade_windows_seconds:WINDOWS,spread_windows_seconds:[300,900,1800],status:'DESCRIPTIVE_ONLY_NOT_POLICY'},by_category_and_starting_price_split:partitions(fitRows,r=>`${r.category}|${r.starting_price_split}`),by_category_and_first_leg_price_region:partitions(fitRows,r=>`${r.category}|${r.first_leg_price_region}`),interpretation_fence:'T-minus and flow are measured separately. None enters V17 behavior. Leg-two own floor T-minus is ex-post descriptive and cannot be a causal decision input.'};
  fs.mkdirSync(output,{recursive:true});fs.writeFileSync(path.join(output,'TIME_AND_FLOW_AXIS_DIAGNOSTIC.json'),canonical(receipt));const ledger=fitRows.map(r=>({...r}));fs.writeFileSync(path.join(output,'TIME_AND_FLOW_ROW_LEDGER.jsonl.gz'),zlib.gzipSync(Buffer.from(ledger.map(JSON.stringify).join('\n')+'\n'),{level:9,mtime:0}));process.stdout.write(canonical({status:'BUILT',rows:rows.length,fit_rows:fitRows.length,output}));
}
main().catch(e=>{process.stderr.write(`${e.stack||e}\n`);process.exitCode=1;});
