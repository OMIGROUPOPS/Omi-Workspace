#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { runColdReplay } = require("./nikvrb_sibling_shape_cold_replay.js");

const repo = path.resolve(process.argv[2] || ".");
const checkOnly = process.argv.includes("--check");
const outDir = path.join(repo, ".claude/window1_live_v4_replay/nikvrb_live_book_breathing_20260731");
const reportPath = path.join(repo, "arb-executor/docs/research/window1/NIKVRB_LIVE_BOOK_BREATHING_REPLAY.md");
const htmlPath = path.join(repo, "arb-executor/docs/research/window1/NIKVRB_LIVE_BOOK_BREATHING_TABLE_CHARTS.html");
const specPath = path.join(repo, "arb-executor/docs/research/window1/NIKVRB_LIVE_BOOK_BREATHING_SPEC.json");

const SOURCES = {
  clock: ".claude/window1_live_v4_replay/nikvrb_coupling_20260730/NIKVRB_DUAL_BOOK_CLOCK.csv",
  trace: ".claude/window1_live_v4_replay/one_game_nikvrb_20260730/NIKVRB_DECISION_TRACE.json",
  replay: "arb-executor/analysis/nikvrb_sibling_shape_cold_replay.js",
  live: "arb-executor/live_v4.py",
  config: "arb-executor/config/deploy_v5_live.json",
  sharp_quote: "arb-executor/analysis/fv_quote.py",
};

const EXPECTED = {
  clock: "9ec9ef0fab27cd750a7d3fba1407bc6c6a8955104071f27b67dac6bd7f8965e5",
  trace: "cf3ecdafc43ff0305ae95addd5a98fc1d53695dbbeae6c7080ad79de0fae1b42",
};

function bytes(rel) { return fs.readFileSync(path.join(repo, rel)); }
function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function packedJson(value) {
  return {
    encoding: "deterministic_gzip_base64",
    uncompressed_sha256: sha256(Buffer.from(JSON.stringify(value))),
    gzip_base64: zlib.gzipSync(Buffer.from(JSON.stringify(value)), { level: 9, mtime: 0 }).toString("base64"),
  };
}
function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>\"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));
}

function parseCsv(text) {
  const matrix = [];
  let row = [], field = "", quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') { field += '"'; i += 1; }
      else if (ch === '"') quoted = false;
      else field += ch;
    } else if (ch === '"') quoted = true;
    else if (ch === ",") { row.push(field); field = ""; }
    else if (ch === "\n") { row.push(field.replace(/\r$/, "")); matrix.push(row); row = []; field = ""; }
    else field += ch;
  }
  if (field || row.length) { row.push(field.replace(/\r$/, "")); matrix.push(row); }
  const headers = matrix.shift();
  return matrix.filter((values) => values.length === headers.length)
    .map((values) => Object.fromEntries(headers.map((name, index) => [name, values[index]])));
}

function lineOf(text, needle) {
  const index = text.split(/\r?\n/).findIndex((line) => line.includes(needle));
  if (index < 0) throw new Error(`missing code needle: ${needle}`);
  return index + 1;
}

function orderState(intervals, leg, sequence, after) {
  const matches = intervals.filter((order) => order.leg === leg && (
    after
      ? order.action_sequence <= sequence && (order.end_sequence === null || order.end_sequence > sequence)
      : order.action_sequence < sequence && (order.end_sequence === null || order.end_sequence >= sequence)
  ));
  if (!matches.length) return null;
  matches.sort((a, b) => b.action_sequence - a.action_sequence);
  return matches[0].price;
}

function buildDecisionRows(rawRows, replay, branch, leg) {
  const ledger = new Map(replay.decision_ledger.map((row) => [row.sequence, row]));
  let ceiling = null;
  const out = [];
  for (const raw of rawRows) {
    const seq = Number(raw.sequence);
    const t = Number(raw.tminus_scheduled_min);
    if (!Number.isFinite(t) || t > 375.45 || t < -5.01) continue;
    const record = ledger.get(seq);
    if (branch === "corrected" && record?.target_ceilings_after) ceiling = record.target_ceilings_after[leg];
    const affectsLeg = raw.event_kind === `BBO_${leg}` || raw.event_kind === `PRINT_${leg}`
      || record?.leg === leg || (record?.action || "").includes(`_${leg}_`);
    if (!affectsLeg) continue;
    const before = orderState(replay.order_intervals, leg, seq, false);
    const after = orderState(replay.order_intervals, leg, seq, true);
    const bid = raw[`${leg}_bid`] === "" ? null : Number(raw[`${leg}_bid`]);
    const ask = raw[`${leg}_ask`] === "" ? null : Number(raw[`${leg}_ask`]);
    const last = raw[`${leg}_last`] === "" ? null : Number(raw[`${leg}_last`]);
    let fired = record ? `${record.organ} · ${record.action}` : "STATE_REVIEW";
    let input = `order=${before ?? "∅"}; bid=${bid ?? "∅"}; ask=${ask ?? "∅"}; last=${last ?? "∅"}`;
    let operation;
    if (record?.arithmetic) operation = record.arithmetic;
    else if (branch === "corrected" && before !== null && Number.isInteger(ceiling) && Number.isInteger(bid) && Number.isInteger(ask)) {
      operation = `min(ceiling ${ceiling}, bid ${bid}, ask-1 ${ask - 1})=${after ?? "∅"}`;
      input += `; ceiling=${ceiling}`;
    } else if (before !== null) operation = `identity(${before})=${after ?? "∅"}`;
    else operation = `NO_CALL(∅)=${after ?? "∅"}`;
    out.push({
      branch, leg, sequence: seq,
      tminus_scheduled: raw.tminus_scheduled,
      tminus_bell: raw.tminus_actual_bell,
      best_bid: bid, best_ask: ask, last_traded: last,
      spread: Number.isInteger(bid) && Number.isInteger(ask) ? ask - bid : null,
      what_fired: fired, input_value: input, operation,
      output_value: after, order_before: before, order_after: after,
      changed: before !== after || Boolean(record?.material),
    });
  }
  return out;
}

function chartSeries(rawRows, replay, leg) {
  return rawRows.filter((raw) => {
    const t = Number(raw.tminus_scheduled_min);
    return Number.isFinite(t) && t <= 375.45 && t >= -5.01;
  }).map((raw) => {
    const seq = Number(raw.sequence);
    const value = (name) => raw[`${leg}_${name}`] === "" ? null : Number(raw[`${leg}_${name}`]);
    return {
      sequence: seq,
      tminus_scheduled: Number(raw.tminus_scheduled_min),
      tminus_bell: Number(raw.tminus_actual_bell_min),
      bid: value("bid"), ask: value("ask"), last: value("last"),
      order: orderState(replay.order_intervals, leg, seq, true),
    };
  });
}

function htmlDocument(payload) {
  const payloadB64 = zlib.gzipSync(Buffer.from(JSON.stringify(payload)), { level: 9, mtime: 0 }).toString("base64");
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NIKVRB live-book breathing replay</title>
<style>
:root{--bg:#07101d;--panel:#0c1728;--grid:#263952;--text:#edf5ff;--muted:#91a7c2;--bid:#39c6f4;--ask:#ffd166;--last:#f5f7fa;--ours:#ff4d67;--accent:#73e2a7}*{box-sizing:border-box}body{margin:0;background:linear-gradient(160deg,#07101d,#10192b);color:var(--text);font:14px/1.45 ui-monospace,SFMono-Regular,Consolas,monospace}.wrap{max-width:1500px;margin:auto;padding:24px}.head{display:flex;justify-content:space-between;gap:20px;align-items:flex-end}.eyebrow{color:var(--accent);letter-spacing:.14em;text-transform:uppercase}.badges{display:flex;gap:8px;flex-wrap:wrap}.badge{border:1px solid #35506e;border-radius:999px;padding:5px 9px;background:#0b1728}.ok{color:var(--accent)}h1{font:700 28px/1.1 system-ui;margin:5px 0}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:18px}.card{background:rgba(12,23,40,.94);border:1px solid #203654;border-radius:12px;padding:14px;box-shadow:0 14px 40px #0007}.card h2{font:700 17px system-ui;margin:0 0 8px}.chart{width:100%;height:330px;display:block}.legend{display:flex;gap:14px;color:var(--muted);font-size:12px}.sw{display:inline-block;width:13px;height:3px;vertical-align:middle;margin-right:5px}.table-card{margin-top:18px}.controls{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-bottom:10px}select,button,label{background:#0a1423;color:var(--text);border:1px solid #304966;border-radius:6px;padding:6px}table{width:100%;border-collapse:collapse;font-size:11px}th{position:sticky;top:0;background:#14243a;color:#b8cae1;text-align:left}th,td{padding:6px;border-bottom:1px solid #1c3049;vertical-align:top}td:nth-child(8),td:nth-child(9){min-width:250px}.scroll{max-height:640px;overflow:auto;border:1px solid #223a57;border-radius:8px}.foot{color:var(--muted);margin-top:8px;font-size:12px}@media(max-width:950px){.grid{grid-template-columns:1fr}.head{display:block}}
</style></head><body><div class="wrap"><div class="head"><div><div class="eyebrow">Window 1 · cold replay · score free</div><h1>NIKVRB — live-book breathing</h1></div><div class="badges"><span class="badge">VRB corrected fill <b class="ok">68</b></span><span class="badge">NIK corrected fill <b class="ok">19</b></span><span class="badge">external sharp specimen input <b>NO_CALL</b></span><span class="badge">own BBO anchor <b class="ok">BOUND</b></span></div></div>
<div class="legend"><span><i class="sw" style="background:var(--bid)"></i>best bid</span><span><i class="sw" style="background:var(--ask)"></i>best ask</span><span><i class="sw" style="background:var(--last)"></i>last traded</span><span><i class="sw" style="background:var(--ours)"></i>our order</span></div>
<div class="grid" id="charts"></div>
<div class="card table-card"><div class="controls"><b>Arithmetic decision table</b><select id="branch"><option value="current">current</option><option value="corrected">corrected</option></select><select id="leg"><option>VRB</option><option>NIK</option></select><label><input id="changes" type="checkbox" checked> state changes/material only</label><button id="prev">previous</button><button id="next">next</button><span id="page"></span></div><div class="scroll"><table><thead><tr><th>T−scheduled</th><th>T−bell</th><th>best bid</th><th>best ask</th><th>last traded</th><th>spread</th><th>what fired</th><th>input value</th><th>operation</th><th>output</th><th>order before</th><th>order after</th></tr></thead><tbody id="rows"></tbody></table></div><div class="foot">The embedded table contains every own-leg BBO/print decision tick. The default filter shows changes and material calls; clear it to inspect identity HOLD/NO_CALL rows. Every row is input → operation → output.</div></div>
</div><script>const DATA_GZIP_BASE64="${payloadB64}";
async function boot(){const packed=Uint8Array.from(atob(DATA_GZIP_BASE64),c=>c.charCodeAt(0));const stream=new Blob([packed]).stream().pipeThrough(new DecompressionStream('gzip'));const DATA=JSON.parse(await new Response(stream).text());
const NS='http://www.w3.org/2000/svg';function el(n,a={}){const e=document.createElementNS(NS,n);for(const[k,v]of Object.entries(a))e.setAttribute(k,v);return e}function chart(branch,leg){const card=document.createElement('div');card.className='card';card.innerHTML='<h2>'+branch.toUpperCase()+' · '+leg+'</h2>';const svg=el('svg',{viewBox:'0 0 720 330',class:'chart'});card.appendChild(svg);const pts=DATA.series[branch][leg],m={l:42,r:14,t:12,b:38},W=720-m.l-m.r,H=330-m.t-m.b;const vals=pts.flatMap(p=>[p.bid,p.ask,p.last,p.order]).filter(Number.isFinite),lo=Math.floor(Math.min(...vals)-2),hi=Math.ceil(Math.max(...vals)+2),maxT=Math.max(...pts.map(p=>p.tminus_scheduled)),minT=Math.min(...pts.map(p=>p.tminus_scheduled));const X=t=>m.l+(maxT-t)/(maxT-minT)*W,Y=v=>m.t+(hi-v)/(hi-lo)*H;for(let v=Math.ceil(lo/5)*5;v<=hi;v+=5){svg.appendChild(el('line',{x1:m.l,x2:720-m.r,y1:Y(v),y2:Y(v),stroke:'#263952','stroke-width':1}));const tx=el('text',{x:5,y:Y(v)+4,fill:'#91a7c2','font-size':10});tx.textContent=v;svg.appendChild(tx)}for(const t of [360,300,240,180,120,60,0]){if(t>maxT||t<minT)continue;svg.appendChild(el('line',{x1:X(t),x2:X(t),y1:m.t,y2:330-m.b,stroke:'#1a2d45','stroke-width':1}));const tx=el('text',{x:X(t),y:315,fill:'#91a7c2','font-size':9,'text-anchor':'middle'});tx.textContent='T−'+t+' / bell '+(t+5);svg.appendChild(tx)}for(const[key,color]of [['bid','#39c6f4'],['ask','#ffd166'],['last','#f5f7fa'],['order','#ff4d67']]){let d='',open=false;for(const p of pts){if(!Number.isFinite(p[key])){open=false;continue}d+=(open?' L ':' M ')+X(p.tminus_scheduled).toFixed(2)+' '+Y(p[key]).toFixed(2);open=true}svg.appendChild(el('path',{d,fill:'none',stroke:color,'stroke-width':key==='order'?2.8:1.35,'stroke-linejoin':'round'}))}const marks=DATA.markers[branch][leg];marks.forEach((p,i)=>{if(!Number.isFinite(p.order_after))return;svg.appendChild(el('circle',{cx:X(p.tminus_numeric),cy:Y(p.order_after),r:3.5,fill:'#ff4d67',stroke:'#07101d'}));const tx=el('text',{x:X(p.tminus_numeric)+4,y:Y(p.order_after)-5,fill:'#ff9bad','font-size':8});tx.textContent=i+1;svg.appendChild(tx)});document.getElementById('charts').appendChild(card)}for(const leg of ['VRB','NIK'])chart('current',leg);for(const leg of ['VRB','NIK'])chart('corrected',leg);
let page=0;const size=250;function render(){const b=document.getElementById('branch').value,l=document.getElementById('leg').value,c=document.getElementById('changes').checked;let rows=DATA.rows.filter(r=>r.branch===b&&r.leg===l&&(!c||r.changed));const pages=Math.max(1,Math.ceil(rows.length/size));page=Math.min(page,pages-1);const slice=rows.slice(page*size,(page+1)*size);document.getElementById('rows').innerHTML=slice.map(r=>'<tr>'+['tminus_scheduled','tminus_bell','best_bid','best_ask','last_traded','spread','what_fired','input_value','operation','output_value','order_before','order_after'].map(k=>'<td>'+((r[k]??'∅').toString().replace(/&/g,'&amp;').replace(/</g,'&lt;'))+'</td>').join('')+'</tr>').join('');document.getElementById('page').textContent='page '+(page+1)+' / '+pages+' · '+rows.length+' rows'}for(const id of ['branch','leg','changes'])document.getElementById(id).onchange=()=>{page=0;render()};document.getElementById('prev').onclick=()=>{page=Math.max(0,page-1);render()};document.getElementById('next').onclick=()=>{page+=1;render()};render()}boot().catch(error=>{document.getElementById('charts').textContent='Render error: '+error.message});</script></body></html>\n`;
}

function main() {
  for (const [key, expected] of Object.entries(EXPECTED)) {
    const actual = sha256(bytes(SOURCES[key]));
    if (actual !== expected) throw new Error(`${key} source hash changed: ${actual}`);
  }
  const rawRows = parseCsv(bytes(SOURCES.clock).toString("utf8"));
  const trace = JSON.parse(bytes(SOURCES.trace).toString("utf8"));
  const current = runColdReplay({ rawRows, trace, scenario: "current" });
  const corrected = runColdReplay({ rawRows, trace, scenario: "breathing" });
  if (corrected.fills.VRB?.price !== 68 || corrected.fills.NIK?.price !== 19) {
    throw new Error(`visual acceptance failed: ${JSON.stringify(corrected.fills)}`);
  }
  const live = bytes(SOURCES.live).toString("utf8");
  const config = JSON.parse(bytes(SOURCES.config).toString("utf8"));
  const codeAudit = {
    schema_version: "NIKVRB_LIVE_BOOK_BREATHING_CODE_PATH_AUDIT_V1",
    fv_anchor_placement_config: config.fv_anchor_placement,
    exact_gate: {
      definition: "When true, the non-engagement placement block may replace its already-resolved target with _fv_anchor_price(ticker).",
      actual_source: "latest fresh positive true-print price in self._trade_prices",
      not_sources: ["Pinnacle", "Betfair", "Matchbook", "own BBO"],
      no_trade_effect_when_false: "None: _v4_entry_anchor returns None before the placement hook is reachable.",
      no_trade_effect_when_true: "Still none: _fv_anchor_price also returns None without a true print, and the hook remains downstream of the failed _v4_entry_anchor call.",
      lines: {
        flag_load: lineOf(live, "self.fv_anchor_placement = self.config.get"),
        trade_tape_helper: lineOf(live, "def _fv_anchor_price"),
        no_trade_return: lineOf(live, "no fresh print -> skip (no BBO-mid fallback by design)"),
        downstream_hook: lineOf(live, "_fv = self._fv_anchor_price(tk) if self.fv_anchor_placement else None"),
      },
    },
    external_sharp_path: {
      implementation: SOURCES.sharp_quote,
      books: ["pinnacle", "betfair_ex_eu", "matchbook"],
      production_anchor_resolver_line: lineOf(live, "def _resolve_anchor"),
      production_dispatch_gate_line: lineOf(live, "if self.fv_scenarios_enabled:"),
      current_dispatch_status: "legacy fv_anchor_scenarios_enabled route only; not the active v4 quiet-tape anchor",
      specimen_receipts: 0,
      specimen_result: "NO_CALL; own lawful 67/68 BBO supplied the causal quiet-book anchor instead",
    },
    stale_order_paths: [
      { path: "_resting_cancel_reason", would_fire: "target >= ask-1", why_not: "placement-time intended_join and intended_clamp exemptions clear bid_marketable_stale before cancellation", line: lineOf(live, "if should_cancel and creason == \"bid_marketable_stale\" and pos.intended_join") },
      { path: "cadence gate", would_fire: "resting-manager review", why_not: "all ordinary walk decisions are suppressed for 60 seconds after a repost", line: lineOf(live, "if now - pos.last_cancel_repost_ts < 60:") },
      { path: "staircase hold", would_fire: "volatility trail only", why_not: "staircase_hold returns unconditionally when its optional trail is disabled", line: lineOf(live, "if not self.staircase_hold_volatility_trail:") },
      { path: "best-bid-aware repost", would_fire: "best bid mismatch", why_not: "deep-cast orders below touch return when the regime is unchanged; the old replay had no equivalent tick branch", line: lineOf(live, "if int(pos.target_price) < int(book.best_bid):") },
      { path: "midpoint deadband", would_fire: "absolute midpoint move > five cents", why_not: "69.5 to 67.5 is only two cents", line: lineOf(live, "elif abs(current_price - price_basis) <= V4_REPRICE_MOVE_CENTS:") },
      { path: "cold replay resting hold", would_fire: "only a named state transition", why_not: "ColdReplay.process:restingHold preserved the selected number and never recomputed it from BBO" },
    ],
  };
  const summary = {
    schema_version: "NIKVRB_LIVE_BOOK_BREATHING_REPLAY_V1",
    source_rows: rawRows.length,
    population_run: false,
    live_execution: false,
    external_sharp_receipts_on_specimen: 0,
    current_fills: Object.fromEntries(Object.entries(current.fills).map(([leg, fill]) => [leg, fill?.price ?? null])),
    corrected_fills: Object.fromEntries(Object.entries(corrected.fills).map(([leg, fill]) => [leg, fill?.price ?? null])),
    quiet_anchors: corrected.quiet_anchors,
    acceptance: {
      VRB_fill_68_or_better: corrected.fills.VRB.price <= 68,
      NIK_fill_at_live_touch_19: corrected.fills.NIK.price === 19,
      no_same_receipt_action_fill: corrected.material_decisions.every((row) => !row.action.startsWith("CREDIT_") || row.trigger !== "LIVE_TOUCH_EXECUTION_ARM"),
    },
  };
  const rows = [
    ...buildDecisionRows(rawRows, current, "current", "VRB"),
    ...buildDecisionRows(rawRows, current, "current", "NIK"),
    ...buildDecisionRows(rawRows, corrected, "corrected", "VRB"),
    ...buildDecisionRows(rawRows, corrected, "corrected", "NIK"),
  ];
  const series = { current: {}, corrected: {} };
  for (const leg of ["VRB", "NIK"]) {
    series.current[leg] = chartSeries(rawRows, current, leg);
    series.corrected[leg] = chartSeries(rawRows, corrected, leg);
  }
  const markers = { current: {}, corrected: {} };
  for (const branch of ["current", "corrected"]) for (const leg of ["VRB", "NIK"]) {
    markers[branch][leg] = rows.filter((row) => row.branch === branch && row.leg === leg && row.changed)
      .map((row) => ({ ...row, tminus_numeric: Number(row.tminus_scheduled.slice(2)) }));
  }
  const spec = {
    schema_version: "NIKVRB_LIVE_BOOK_BREATHING_SPEC_V1",
    scope: "one-event score-free cold replay; no deployment",
    anchor_priority: ["precomputed three-book sharp blend when complete/fresh", "own lawful one-cent BBO midpoint", "NO_CALL"],
    external_sharp_books: ["pinnacle", "betfair_ex_eu", "matchbook"],
    price_law: "resting_price = max(1, min(causal_maximum_payable, external_best_bid, external_best_ask - 1)); recompute on every own-leg BBO",
    faller_law: "after sibling riser resolves, maximum payable ratchets down and never rises on quote-only recovery",
    exact_touch_law: "a first ask-equals-order receipt arms an active ask lift; only a strictly later confirming receipt executes at the already-resting price",
    fences: ["no fabricated external sharp price", "no future observation", "no same-receipt action/fill", "no population score", "no live or network access"],
  };
  const report = `# NIKVRB live-book breathing replay\n\n` +
    `Current: VRB ${summary.current_fills.VRB}, NIK ${summary.current_fills.NIK}. Corrected: VRB ${summary.corrected_fills.VRB}, NIK ${summary.corrected_fills.NIK}.\n\n` +
    `## fv_anchor_placement truth\n\n` +
    `The deployed value is \`${config.fv_anchor_placement}\`. It gates only the downstream \`_fv_anchor_price\` placement override, whose source is the latest fresh true print. It does not call Pinnacle, Betfair, Matchbook, or the own BBO. With no print, \`_v4_entry_anchor\` returns before that hook is reachable; setting the flag true therefore leaves the T−317.817 no-print NO_CALL unchanged. The exact production lines are frozen in CODE_PATH_AUDIT.json.\n\n` +
    `The correction uses a separate quiet-book anchor contract. A complete fresh three-book sharp blend has first authority when it exists. NIKVRB contains no such historical external receipts, so the replay records that mechanism as NO_CALL and uses the lawful 67/68 own BBO midpoint: round((67+68)/2)=68. It initially rests maker-safe at 67, then recomputes min(ceiling 68, bid 69)=68 before the later 68 ask recurrence.\n\n` +
    `## Reprice-path autopsy\n\n` + codeAudit.stale_order_paths.map((row) => `- **${row.path}:** ${row.why_not}.`).join("\n") + `\n\n` +
    `## Acceptance\n\n- VRB: 68.\n- NIK: 19.\n- External sharp prices fabricated: 0.\n- Population scoring/live execution: none.\n- Full arithmetic table and four charts: \`NIKVRB_LIVE_BOOK_BREATHING_TABLE_CHARTS.html\`.\n`;
  const payload = { summary, rows, series, markers };
  const outputs = new Map([
    [path.join(outDir, "REPLAY_SUMMARY.json"), canonical(summary)],
    [path.join(outDir, "CODE_PATH_AUDIT.json"), canonical(codeAudit)],
    [path.join(outDir, "CURRENT_ORDER_INTERVALS.json"), canonical(current.order_intervals)],
    [path.join(outDir, "CORRECTED_ORDER_INTERVALS.json"), canonical(corrected.order_intervals)],
    [path.join(outDir, "CORRECTED_MATERIAL_DECISIONS.json"), canonical(corrected.material_decisions)],
    [path.join(outDir, "ARITHMETIC_DECISION_ROWS.json"), canonical({
      schema_version: "NIKVRB_ARITHMETIC_DECISION_ROWS_PACKED_V1",
      row_count: rows.length,
      ...packedJson(rows),
    })],
    [reportPath, report],
    [htmlPath, htmlDocument(payload)],
    [specPath, canonical(spec)],
  ]);
  const sourceManifest = Object.entries(SOURCES).map(([role, rel]) => ({ role, path: rel, sha256: sha256(bytes(rel)), size: bytes(rel).length }));
  outputs.set(path.join(outDir, "SOURCE_HASH_MANIFEST.json"), canonical({ schema_version: "NIKVRB_LIVE_BOOK_BREATHING_SOURCE_MANIFEST_V1", sources: sourceManifest }));
  outputs.set(path.join(outDir, "FORBIDDEN_ACCESS_RECEIPT.json"), canonical({ schema_version: "NIKVRB_LIVE_BOOK_BREATHING_FORBIDDEN_ACCESS_V1", population_scoring: false, live_access: false, network_access: false, order_mutation: false, position_mutation: false, holdout_access: false }));
  const preManifest = [...outputs.entries()].map(([name, value]) => ({ path: path.relative(repo, name).replace(/\\/g, "/"), sha256: sha256(Buffer.from(value)), size: Buffer.byteLength(value) }));
  outputs.set(path.join(outDir, "ARTIFACT_HASH_MANIFEST.json"), canonical({ schema_version: "NIKVRB_LIVE_BOOK_BREATHING_ARTIFACT_MANIFEST_V1", artifacts: preManifest }));
  outputs.set(path.join(outDir, "DETERMINISM_RECEIPT.json"), canonical({ schema_version: "NIKVRB_LIVE_BOOK_BREATHING_DETERMINISM_V1", method: "builder --check regenerates every byte in memory and compares to the committed file", expected_files: outputs.size + 1, byte_identical: true }));

  let mismatches = [];
  for (const [name, value] of outputs) {
    if (checkOnly) {
      if (!fs.existsSync(name) || !fs.readFileSync(name).equals(Buffer.from(value))) mismatches.push(path.relative(repo, name));
    } else {
      fs.mkdirSync(path.dirname(name), { recursive: true });
      fs.writeFileSync(name, value, "utf8");
    }
  }
  if (mismatches.length) throw new Error(`determinism mismatch: ${mismatches.join(", ")}`);
  process.stdout.write(canonical({ status: checkOnly ? "CHECK_PASS" : "BUILD_PASS", source_rows: rawRows.length, decision_rows: rows.length, current: summary.current_fills, corrected: summary.corrected_fills, files: outputs.size }));
}

main();
