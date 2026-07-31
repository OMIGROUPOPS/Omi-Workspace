#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const {
  ASK_REACH_DWELL_SECONDS,
  runColdReplay,
} = require("./nikvrb_sibling_shape_cold_replay.js");

const repo = path.resolve(process.argv[2] || ".");
const checkOnly = process.argv.includes("--check");
const outDir = path.join(repo, ".claude/window1_live_v4_replay/nikvrb_ask_dwell_20260731");
const reportPath = path.join(repo, "arb-executor/docs/research/window1/NIKVRB_ASK_DWELL_REPLAY.md");
const htmlPath = path.join(repo, "arb-executor/docs/research/window1/NIKVRB_ASK_DWELL_TABLE_CHARTS.html");
const specPath = path.join(repo, "arb-executor/docs/research/window1/NIKVRB_ASK_DWELL_SPEC.json");

const SOURCES = {
  clock: ".claude/window1_live_v4_replay/nikvrb_coupling_20260730/NIKVRB_DUAL_BOOK_CLOCK.csv",
  trace: ".claude/window1_live_v4_replay/one_game_nikvrb_20260730/NIKVRB_DECISION_TRACE.json",
  episodes: ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_DIVOT_EPISODES.csv",
  reachability: ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_CENSUS.json",
  thresholdAuthority: "arb-executor/docs/research/window1/WINDOW1_ORGAN_SCORECARD_AND_DEFECT_LEDGER.md",
  priorSummary: ".claude/window1_live_v4_replay/nikvrb_live_book_breathing_20260731/REPLAY_SUMMARY.json",
  capacity: ".claude/window1_live_v4_replay/five_exact_full_stack_capacity_20260731/NIKVRB_CAPACITY_BY_SEQUENCE.json",
  replay: "arb-executor/analysis/nikvrb_sibling_shape_cold_replay.js",
  live: "arb-executor/live_v4.py",
};

const FROZEN_SOURCE_HASHES = {
  clock: "9ec9ef0fab27cd750a7d3fba1407bc6c6a8955104071f27b67dac6bd7f8965e5",
  trace: "cf3ecdafc43ff0305ae95addd5a98fc1d53695dbbeae6c7080ad79de0fae1b42",
  episodes: "973e4c3edf985cca55001407f06540415e53eb6b6c2babdc099193b082df65ef",
  reachability: "fd205926fed1a727e9029d02155f9eb718717af9f218713ecc4d16802e6027bc",
  thresholdAuthority: "403d64851e0fa95985ec5e65e63d3a6c784c46425f66e4b2aaa3e50837e383f6",
};

function read(rel) { return fs.readFileSync(path.join(repo, rel)); }
function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function gzipJson(value) {
  const raw = Buffer.from(JSON.stringify(value));
  return {
    encoding: "deterministic_gzip_base64",
    row_count: value.length,
    uncompressed_sha256: sha256(raw),
    gzip_base64: zlib.gzipSync(raw, { level: 9, mtime: 0 }).toString("base64"),
  };
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

function orderAt(intervals, leg, sequence, after) {
  const rows = intervals.filter((order) => order.leg === leg && (after
    ? order.action_sequence <= sequence && (order.end_sequence === null || order.end_sequence > sequence)
    : order.action_sequence < sequence && (order.end_sequence === null || order.end_sequence >= sequence)));
  rows.sort((a, b) => b.action_sequence - a.action_sequence);
  return rows.length ? rows[0].price : null;
}

function decisionRows(rawRows, replay, branch, leg) {
  const targetsLeg = (record) => {
    if (!record) return false;
    if (record.leg) return record.leg === leg;
    if (new RegExp(`(^|_)${leg}(_|$)`).test(record.action || "")) return true;
    return ["WINDOW_GATE", "DISCOVERY_GATE"].includes(record.organ);
  };
  const ledger = new Map();
  for (const record of replay.decision_ledger) {
    if (targetsLeg(record)) ledger.set(record.sequence, record);
  }
  return rawRows.filter((raw) => {
    const t = Number(raw.tminus_scheduled_min);
    return Number.isFinite(t) && t <= 375.45 && t >= -5.01
      && (raw.event_kind === `BBO_${leg}` || raw.event_kind === `PRINT_${leg}` || ledger.get(Number(raw.sequence))?.leg === leg);
  }).map((raw) => {
    const sequence = Number(raw.sequence);
    const record = ledger.get(sequence);
    const before = orderAt(replay.order_intervals, leg, sequence, false);
    const after = orderAt(replay.order_intervals, leg, sequence, true);
    const value = (name) => raw[`${leg}_${name}`] === "" ? null : Number(raw[`${leg}_${name}`]);
    const bid = value("bid"), ask = value("ask"), last = value("last");
    const input = `order=${before ?? "EMPTY"}; bid=${bid ?? "EMPTY"}; ask=${ask ?? "EMPTY"}; last=${last ?? "EMPTY"}`;
    const operation = record?.arithmetic || (before === null
      ? `NO_CALL(${input})=${after ?? "EMPTY"}`
      : `identity(${before})=${after ?? "EMPTY"}`);
    return {
      branch, leg, sequence,
      tminus_scheduled: raw.tminus_scheduled,
      tminus_bell: raw.tminus_actual_bell,
      best_bid: bid, best_ask: ask, last_traded: last,
      spread: Number.isInteger(bid) && Number.isInteger(ask) ? ask - bid : null,
      what_fired: record ? `${record.organ} | ${record.action}` : "STATE_REVIEW | NO_CHANGE",
      input_value: input,
      operation,
      output_value: after,
      order_before: before,
      order_after: after,
      changed: before !== after || Boolean(record?.material),
    };
  });
}

function chartSeries(rawRows, replay, leg) {
  return rawRows.filter((raw) => {
    const t = Number(raw.tminus_scheduled_min);
    return Number.isFinite(t) && t <= 375.45 && t >= -5.01;
  }).map((raw) => {
    const sequence = Number(raw.sequence);
    const value = (name) => raw[`${leg}_${name}`] === "" ? null : Number(raw[`${leg}_${name}`]);
    return {
      sequence,
      tminus_scheduled: Number(raw.tminus_scheduled_min),
      tminus_bell: Number(raw.tminus_actual_bell_min),
      bid: value("bid"), ask: value("ask"), last: value("last"),
      order: orderAt(replay.order_intervals, leg, sequence, true),
    };
  });
}

function aggregateAskEpisodes(csvText) {
  const lines = csvText.trimEnd().split(/\r?\n/);
  const headers = lines.shift().split(",");
  const at = Object.fromEntries(headers.map((name, index) => [name, index]));
  const bandSpecs = [
    ["ZERO_SECONDS", (x) => x === 0],
    ["ONE_TO_NINE_SECONDS", (x) => x >= 1 && x < 10],
    ["TEN_TO_TWENTY_NINE_SECONDS", (x) => x >= 10 && x < 30],
    ["THIRTY_TO_FIFTY_NINE_SECONDS", (x) => x >= 30 && x < 60],
    ["SIXTY_TO_299_SECONDS", (x) => x >= 60 && x < 300],
    ["AT_LEAST_300_SECONDS", (x) => x >= 300],
  ];
  const fresh = () => ({ episodes: 0, events: new Set(), legs: new Set() });
  const bands = Object.fromEntries(bandSpecs.map(([name]) => [name, fresh()]));
  const total = fresh();
  const nik = { bid: fresh(), ask: fresh(), bid_dwell_counts: {} };
  for (const line of lines) {
    const row = line.split(",");
    const side = row[at.side];
    const ticker = row[at.ticker];
    const eventId = row[at.event_id];
    const dwell = Number(row[at.seconds_at_trough_before_resume]);
    const tminus = Number(row[at.tminus_scheduled_at_trough_minutes]);
    const inNikWindow = ticker.endsWith("NIKVRB-NIK") && tminus >= 155.0665 && tminus <= 178.8675;
    if (inNikWindow) {
      nik[side].episodes += 1;
      nik[side].events.add(eventId);
      nik[side].legs.add(ticker);
      if (side === "bid") nik.bid_dwell_counts[String(dwell)] = (nik.bid_dwell_counts[String(dwell)] || 0) + 1;
    }
    if (side !== "ask") continue;
    total.episodes += 1; total.events.add(eventId); total.legs.add(ticker);
    const selected = bandSpecs.find(([, predicate]) => predicate(dwell));
    if (!selected) throw new Error(`unclassified ask dwell ${dwell}`);
    const bucket = bands[selected[0]];
    bucket.episodes += 1; bucket.events.add(eventId); bucket.legs.add(ticker);
  }
  const clean = (value) => ({ episodes: value.episodes, unique_events: value.events.size, unique_legs: value.legs.size });
  return {
    schema_version: "WINDOW1_ASK_ONLY_DIVOT_DWELL_CENSUS_V1",
    source_episode_rows: lines.length,
    source_sides: ["bid", "ask"],
    retained_side: "ask",
    reachability_direction: "external seller ask at or below a resting buy limit",
    total: clean(total),
    dwell_bands: Object.fromEntries(Object.entries(bands).map(([name, value]) => [name, clean(value)])),
    at_or_above_thresholds: {
      "10_seconds": clean({
        episodes: bands.TEN_TO_TWENTY_NINE_SECONDS.episodes + bands.THIRTY_TO_FIFTY_NINE_SECONDS.episodes + bands.SIXTY_TO_299_SECONDS.episodes + bands.AT_LEAST_300_SECONDS.episodes,
        events: new Set([...bands.TEN_TO_TWENTY_NINE_SECONDS.events, ...bands.THIRTY_TO_FIFTY_NINE_SECONDS.events, ...bands.SIXTY_TO_299_SECONDS.events, ...bands.AT_LEAST_300_SECONDS.events]),
        legs: new Set([...bands.TEN_TO_TWENTY_NINE_SECONDS.legs, ...bands.THIRTY_TO_FIFTY_NINE_SECONDS.legs, ...bands.SIXTY_TO_299_SECONDS.legs, ...bands.AT_LEAST_300_SECONDS.legs]),
      }),
      "30_seconds": clean({
        episodes: bands.THIRTY_TO_FIFTY_NINE_SECONDS.episodes + bands.SIXTY_TO_299_SECONDS.episodes + bands.AT_LEAST_300_SECONDS.episodes,
        events: new Set([...bands.THIRTY_TO_FIFTY_NINE_SECONDS.events, ...bands.SIXTY_TO_299_SECONDS.events, ...bands.AT_LEAST_300_SECONDS.events]),
        legs: new Set([...bands.THIRTY_TO_FIFTY_NINE_SECONDS.legs, ...bands.SIXTY_TO_299_SECONDS.legs, ...bands.AT_LEAST_300_SECONDS.legs]),
      }),
      "60_seconds": clean({
        episodes: bands.SIXTY_TO_299_SECONDS.episodes + bands.AT_LEAST_300_SECONDS.episodes,
        events: new Set([...bands.SIXTY_TO_299_SECONDS.events, ...bands.AT_LEAST_300_SECONDS.events]),
        legs: new Set([...bands.SIXTY_TO_299_SECONDS.legs, ...bands.AT_LEAST_300_SECONDS.legs]),
      }),
      "300_seconds": clean(bands.AT_LEAST_300_SECONDS),
    },
    nik_midwindow: {
      tminus_scheduled_inclusive_display_bounds: ["T-178.867", "T-155.067"],
      bid_side_episodes: nik.bid.episodes,
      ask_side_episodes: nik.ask.episodes,
      bid_dwell_counts: nik.bid_dwell_counts,
    },
  };
}

function nikMidwindowRawReceipt(rawRows) {
  const rows = rawRows.filter((row) => {
    const t = Number(row.tminus_scheduled_min);
    return Number.isFinite(t) && t >= 155.0665 && t <= 178.8675;
  });
  const bbo = rows.filter((row) => row.event_kind === "BBO_NIK");
  const bidValues = bbo.map((row) => Number(row.NIK_bid));
  const askValues = bbo.map((row) => Number(row.NIK_ask));
  const lastValues = bbo.map((row) => Number(row.NIK_last));
  let bidChanges = 0;
  for (let index = 1; index < bbo.length; index += 1) {
    if (Number(bbo[index].NIK_bid) !== Number(bbo[index - 1].NIK_bid)) bidChanges += 1;
  }
  return {
    schema_version: "NIKVRB_NIK_MIDWINDOW_ASK_AUTHORITY_RECEIPT_V1",
    display_interval: ["T-178.867", "T-155.067"],
    source_clock_rows: rows.length,
    NIK_BBO_receipts: bbo.length,
    distinct_BBO_timestamps: new Set(bbo.map((row) => row.timestamp_et)).size,
    bid_changes: bidChanges,
    bid_range: [Math.min(...bidValues), Math.max(...bidValues)],
    bid_receipt_frequency: Object.fromEntries([...new Set(bidValues)].sort((a, b) => a - b).map((price) => [String(price), bidValues.filter((value) => value === price).length])),
    ask_values: [...new Set(askValues)].sort((a, b) => a - b),
    last_trade_values: [...new Set(lastValues)].sort((a, b) => a - b),
    true_print_receipts: rows.filter((row) => row.event_kind === "PRINT_NIK").length,
    reachability_result: "NO_ASK_SIDE_EPISODE",
    decision_authority: "bid churn has zero buy-fill reachability authority",
  };
}

function opportunityReconciliation(reachability) {
  const thresholds = ["10", "30", "60", "300"];
  const rows = {};
  for (const threshold of thresholds) {
    const askOnly = [], union = [], comparable = [];
    for (const event of reachability.events) {
      const legs = Object.values(event.legs);
      if (legs.length !== 2) continue;
      const asks = legs.map((leg) => leg.quote_touch_floors?.[threshold]?.resting_bid_limit_cents ?? null);
      const prints = legs.map((leg) => leg.print_only_floor?.price_cents ?? null);
      const closes = legs.map((leg) => leg.window1_close_cents ?? null);
      if (!asks.every(Number.isFinite) || !closes.every(Number.isFinite)) continue;
      comparable.push(event.event_id);
      const askDelta = asks.reduce((sum, price, i) => sum + price - closes[i], 0);
      if (askDelta < 0) askOnly.push(event.event_id);
      const unionPrices = asks.map((ask, i) => Number.isFinite(prints[i]) ? Math.min(ask, prints[i]) : ask);
      const unionDelta = unionPrices.reduce((sum, price, i) => sum + price - closes[i], 0);
      if (unionDelta < 0) union.push(event.event_id);
    }
    const askSet = new Set(askOnly);
    rows[`${threshold}_seconds`] = {
      comparable_events_with_two_ask_floors: comparable.length,
      prior_true_print_or_ask_negative_pair_opportunities: union.length,
      corrected_ask_only_negative_pair_opportunities: askOnly.length,
      removed_print_dependent_opportunities: union.filter((id) => !askSet.has(id)),
      removed_count: union.length - askOnly.length,
    };
  }
  return {
    schema_version: "WINDOW1_ASK_ONLY_OPPORTUNITY_RECONCILIATION_V1",
    population: reachability.population,
    primary_threshold_seconds: ASK_REACH_DWELL_SECONDS,
    primary_prior_denominator: rows["10_seconds"].prior_true_print_or_ask_negative_pair_opportunities,
    primary_corrected_denominator: rows["10_seconds"].corrected_ask_only_negative_pair_opportunities,
    threshold_rows: rows,
  };
}

function html(payload) {
  const packed = zlib.gzipSync(Buffer.from(JSON.stringify(payload)), { level: 9, mtime: 0 }).toString("base64");
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NIKVRB ask-side dwell replay</title><style>
:root{--bg:#07101d;--panel:#0c1728;--grid:#263952;--text:#edf5ff;--muted:#91a7c2;--bid:#39c6f4;--ask:#ffd166;--last:#f5f7fa;--ours:#ff4d67;--ok:#73e2a7}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:14px/1.45 ui-monospace,Consolas,monospace}.wrap{max-width:1500px;margin:auto;padding:22px}h1{font:700 26px system-ui;margin:0 0 8px}.sub{color:var(--muted);margin-bottom:12px}.legend{display:flex;gap:14px;flex-wrap:wrap}.sw{display:inline-block;width:14px;border-top:3px solid;margin-right:5px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px}.card{background:var(--panel);border:1px solid #203654;border-radius:10px;padding:12px}.chart{width:100%;height:320px}.table-card{margin-top:14px}.controls{display:flex;gap:9px;align-items:center;flex-wrap:wrap;margin-bottom:9px}select,button,label{background:#0a1423;color:var(--text);border:1px solid #304966;border-radius:5px;padding:5px}.scroll{max-height:650px;overflow:auto}table{width:100%;border-collapse:collapse;font-size:11px}th{position:sticky;top:0;background:#14243a}th,td{text-align:left;padding:6px;border-bottom:1px solid #1c3049;vertical-align:top}td:nth-child(8),td:nth-child(9){min-width:250px}@media(max-width:900px){.grid{grid-template-columns:1fr}}</style></head><body><div class="wrap"><h1>NIKVRB — ask-side dwell correction</h1><div class="sub">Prior bid-reactive replay versus ask-only 10-second reachability. Corrected fills: VRB 68, NIK 18.</div><div class="legend"><span><i class="sw" style="border-color:var(--bid)"></i>best bid</span><span><i class="sw" style="border-color:var(--ask)"></i>best ask</span><span><i class="sw" style="border-color:var(--last)"></i>last traded</span><span><i class="sw" style="border-color:var(--ours)"></i>our resting bid</span></div><div id="charts" class="grid"></div><div class="card table-card"><div class="controls"><b>Arithmetic decision table</b><select id="branch"><option value="prior_bid_reactive">prior bid-reactive</option><option value="corrected_ask_dwell">corrected ask+dwell</option></select><select id="leg"><option>VRB</option><option>NIK</option></select><label><input type="checkbox" id="changes" checked>changes/material</label><button id="prev">previous</button><button id="next">next</button><span id="page"></span></div><div class="scroll"><table><thead><tr><th>T−scheduled</th><th>T−bell</th><th>bid</th><th>ask</th><th>last</th><th>spread</th><th>what fired</th><th>input</th><th>operation</th><th>output</th><th>before</th><th>after</th></tr></thead><tbody id="rows"></tbody></table></div></div></div><script>
const PACKED="${packed}";async function boot(){const bytes=Uint8Array.from(atob(PACKED),c=>c.charCodeAt(0));const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));const D=JSON.parse(await new Response(stream).text());const NS='http://www.w3.org/2000/svg';function E(n,a={}){const e=document.createElementNS(NS,n);for(const[k,v]of Object.entries(a))e.setAttribute(k,v);return e}function chart(branch,leg){const card=document.createElement('div');card.className='card';card.innerHTML='<b>'+branch.replaceAll('_',' ').toUpperCase()+' · '+leg+'</b>';const s=E('svg',{viewBox:'0 0 720 320',class:'chart',role:'img','aria-label':branch+' '+leg+' bid ask last and resting order'});card.appendChild(s);const p=D.series[branch][leg],m={l:40,r:12,t:10,b:35},W=668,H=275,vals=p.flatMap(x=>[x.bid,x.ask,x.last,x.order]).filter(Number.isFinite),lo=Math.floor(Math.min(...vals)-2),hi=Math.ceil(Math.max(...vals)+2),ma=Math.max(...p.map(x=>x.tminus_scheduled)),mi=Math.min(...p.map(x=>x.tminus_scheduled)),X=t=>m.l+(ma-t)/(ma-mi)*W,Y=v=>m.t+(hi-v)/(hi-lo)*H;for(let v=Math.ceil(lo/5)*5;v<=hi;v+=5){s.appendChild(E('line',{x1:m.l,x2:708,y1:Y(v),y2:Y(v),stroke:'#263952'}));const q=E('text',{x:4,y:Y(v)+4,fill:'#91a7c2','font-size':10});q.textContent=v;s.appendChild(q)}for(const t of [360,300,240,180,120,60,0]){if(t>ma||t<mi)continue;s.appendChild(E('line',{x1:X(t),x2:X(t),y1:10,y2:285,stroke:'#1a2d45'}));const q=E('text',{x:X(t),y:306,fill:'#91a7c2','font-size':9,'text-anchor':'middle'});q.textContent='T−'+t+' / bell '+(t+5);s.appendChild(q)}for(const[k,c]of [['bid','#39c6f4'],['ask','#ffd166'],['last','#f5f7fa'],['order','#ff4d67']]){let d='',open=false;for(const x of p){if(!Number.isFinite(x[k])){open=false;continue}d+=(open?' L ':' M ')+X(x.tminus_scheduled).toFixed(2)+' '+Y(x[k]).toFixed(2);open=true}s.appendChild(E('path',{d,fill:'none',stroke:c,'stroke-width':k==='order'?2.8:1.3}))}D.markers[branch][leg].forEach((x,i)=>{if(!Number.isFinite(x.order_after))return;const c=E('circle',{cx:X(x.tminus_numeric),cy:Y(x.order_after),r:3.3,fill:'#ff4d67'});s.appendChild(c);const q=E('text',{x:X(x.tminus_numeric)+4,y:Y(x.order_after)-4,fill:'#ff9bad','font-size':8});q.textContent=i+1;s.appendChild(q)});document.getElementById('charts').appendChild(card)}for(const b of ['prior_bid_reactive','corrected_ask_dwell'])for(const l of ['VRB','NIK'])chart(b,l);let page=0;const size=250;function render(){const b=document.getElementById('branch').value,l=document.getElementById('leg').value,only=document.getElementById('changes').checked;let rows=D.rows.filter(r=>r.branch===b&&r.leg===l&&(!only||r.changed)),pages=Math.max(1,Math.ceil(rows.length/size));page=Math.min(page,pages-1);document.getElementById('rows').innerHTML=rows.slice(page*size,(page+1)*size).map(r=>'<tr>'+['tminus_scheduled','tminus_bell','best_bid','best_ask','last_traded','spread','what_fired','input_value','operation','output_value','order_before','order_after'].map(k=>'<td>'+String(r[k]??'EMPTY').replaceAll('&','&amp;').replaceAll('<','&lt;')+'</td>').join('')+'</tr>').join('');document.getElementById('page').textContent=(page+1)+'/'+pages+' · '+rows.length+' rows'}for(const id of ['branch','leg','changes'])document.getElementById(id).onchange=()=>{page=0;render()};document.getElementById('prev').onclick=()=>{page=Math.max(0,page-1);render()};document.getElementById('next').onclick=()=>{page+=1;render()};render()}boot();</script></body></html>\n`;
}

function build() {
  for (const [name, expected] of Object.entries(FROZEN_SOURCE_HASHES)) {
    const actual = sha256(read(SOURCES[name]));
    if (actual !== expected) throw new Error(`${name} source hash changed: ${actual}`);
  }
  const rawRows = parseCsv(read(SOURCES.clock).toString("utf8"));
  const trace = JSON.parse(read(SOURCES.trace).toString("utf8"));
  const capacityBySequence = JSON.parse(read(SOURCES.capacity).toString("utf8")).capacity_by_sequence;
  const prior = runColdReplay({ rawRows, trace, scenario: "breathing" });
  const corrected = runColdReplay({ rawRows, trace, scenario: "ask_dwell", capacityBySequence });
  if (corrected.fills.VRB?.price !== 68 || corrected.fills.NIK?.price !== 18) {
    throw new Error(`ask-dwell acceptance failed ${JSON.stringify(corrected.fills)}`);
  }
  const corpus = aggregateAskEpisodes(read(SOURCES.episodes).toString("utf8"));
  const nikMidwindow = nikMidwindowRawReceipt(rawRows);
  const opportunity = opportunityReconciliation(JSON.parse(read(SOURCES.reachability).toString("utf8")));
  if (corpus.nik_midwindow.bid_side_episodes !== 63 || corpus.nik_midwindow.ask_side_episodes !== 0) throw new Error("NIK midwindow conservation failed");
  if (corpus.dwell_bands.ZERO_SECONDS.episodes !== 74391) throw new Error("ask zero-dwell census changed");
  if (opportunity.primary_prior_denominator !== 598 || opportunity.primary_corrected_denominator !== 532) throw new Error("598 reconciliation failed");

  const rows = [];
  for (const [branch, replay] of [["prior_bid_reactive", prior], ["corrected_ask_dwell", corrected]]) {
    for (const leg of ["VRB", "NIK"]) rows.push(...decisionRows(rawRows, replay, branch, leg));
  }
  const series = { prior_bid_reactive: {}, corrected_ask_dwell: {} };
  const markers = { prior_bid_reactive: {}, corrected_ask_dwell: {} };
  for (const [branch, replay] of [["prior_bid_reactive", prior], ["corrected_ask_dwell", corrected]]) {
    for (const leg of ["VRB", "NIK"]) {
      series[branch][leg] = chartSeries(rawRows, replay, leg);
      markers[branch][leg] = rows.filter((row) => row.branch === branch && row.leg === leg && row.changed)
        .map((row) => ({ ...row, tminus_numeric: Number(row.tminus_scheduled.slice(2)) }));
    }
  }
  const summary = {
    schema_version: "NIKVRB_ASK_DWELL_REPLAY_V1",
    scope: "one-event score-free cold replay",
    source_rows: rawRows.length,
    threshold_seconds: ASK_REACH_DWELL_SECONDS,
    threshold_authority: "pre-existing frozen primary quote-touch comparator; not selected from NIKVRB outcome",
    reachability_side: "ask_only",
    bid_side_entry_authority: false,
    prior_fills: Object.fromEntries(Object.entries(prior.fills).map(([leg, row]) => [leg, row?.price ?? null])),
    corrected_fills: Object.fromEntries(Object.entries(corrected.fills).map(([leg, row]) => [leg, row?.price ?? null])),
    corrected_fill_receipts: corrected.fills,
    capacity_law: "credit exactly five only when contemporaneous displayed external ask capacity at the reachable price is at least five",
    evidence_absent_count: corrected.capacity_evidence_absent.length,
    independent_pair_reference: "NOT_BOUND",
    nik_midwindow: {
      ...corpus.nik_midwindow,
      zero_second_bid_episodes: corpus.nik_midwindow.bid_dwell_counts["0"] || 0,
      positive_dwell_bid_episodes: Object.fromEntries(Object.entries(corpus.nik_midwindow.bid_dwell_counts).filter(([seconds]) => seconds !== "0").map(([seconds, count]) => [`${seconds}_seconds`, count])),
      opportunity: false,
      reason: "zero ask-side episodes; bid-side changes are other buyers and cannot reach a resting buy",
    },
    acceptance: {
      VRB_fill_68_after_ask_dwell: corrected.fills.VRB.price === 68 && corrected.fills.VRB.evidence.dwell_seconds >= ASK_REACH_DWELL_SECONDS,
      NIK_fill_18_after_ask_dwell: corrected.fills.NIK.price === 18 && corrected.fills.NIK.evidence.dwell_seconds >= ASK_REACH_DWELL_SECONDS,
      bid_churn_created_no_material_action: corrected.material_decisions.filter((row) => row.leg === "NIK" && row.sequence >= 1700 && row.sequence <= 2703 && ["LIVE_ASK_TOUCH", "ASK_DWELL_PATIENCE_RELEASE"].includes(row.organ)).length === 0,
      no_same_receipt_action_fill: corrected.fills.NIK.action_sequence < corrected.fills.NIK.evidence_sequence && corrected.fills.VRB.action_sequence < corrected.fills.VRB.evidence_sequence,
      displayed_capacity_proven: corrected.fills.NIK.evidence.evidence_size >= 5 && corrected.fills.VRB.evidence.evidence_size >= 5,
    },
    population_score_run: false,
    live_execution: false,
  };
  const spec = {
    schema_version: "NIKVRB_ASK_DWELL_SPEC_V1",
    scope: "one cold event plus descriptive corpus recut; no population candidate score",
    reachability_law: "For a resting buy, only the external ask at or below the resting limit can establish quote reachability.",
    dwell_law: `The ask must remain continuously at or below the resting limit for at least ${ASK_REACH_DWELL_SECONDS} seconds.`,
    decision_law: "Bid updates remain visible context but cannot release patience, change a target, or credit a fill.",
    threshold_authority: "QUOTE_OR_PRINT_DWELL_10 was the frozen primary comparator before this specimen; the recut removes print and bid-side authority rather than retuning the cutoff.",
    no_same_receipt_law: "An ask observation used to create an order cannot also fill it; fill evidence must be strictly later.",
    capacity_law: "A price-reachable ask receives five-contract accounting credit only when its contemporaneous displayed external ask capacity is at least five; unknown or sub-five capacity is EVIDENCE_ABSENT.",
    pair_reference_law: "No independent pair reference is bound. The report emits NOT_BOUND and forbids 100 minus sibling entry.",
  };
  const report = `# NIKVRB ask-side dwell replay\n\nThe corrected cold branch fills VRB at **68** and NIK at **18**. Both credits now have contemporaneous displayed capacity: VRB **110** and NIK **86** contracts. Unknown or sub-five capacity is \`EVIDENCE_ABSENT\` and cannot enter completion. Reachability is ask-only and the minimum continuous ask dwell is **10 seconds**. That value is inherited from the already-frozen primary quote-touch comparator in WINDOW1_ORGAN_SCORECARD_AND_DEFECT_LEDGER.md, which defined the 598-event baseline before this NIKVRB correction. It was not selected from this game's outcome.\n\nNo independent pair reference is bound. Pair reference and pair-reference delta are \`NOT_BOUND\`; the former proxy \`100 - sibling entry\` is forbidden.\n\n## NIK T-178.867 to T-155.067\n\nThe retained episode census contains 63 bid-side episodes and zero ask-side episodes. Fifty-nine bid episodes have zero-second trough dwell; the other four dwell 1, 1, 13, and 25 seconds. Because the ask remains 29 throughout, this interval contains zero buy-side reachability opportunities and causes zero corrected target changes. The raw clock also contains 841 NIK BBO receipts and 240 bid changes in this interval; none has reachability authority.\n\n## Corrected chronology\n\n- VRB rests at 68 before the ask returns to 68. The ask persists 32 seconds by receipt sequence 326; displayed ask size 110 proves five-contract capacity and credits 68.\n- NIK's 21 is cancelled after 66 completed ask-side recurrences when the sibling riser resolves. The 24 ask lasts 7 seconds and the 23 ask lasts 2 seconds, so neither releases patience. The 19 ask persists 11 seconds; ask-1 places 18 at sequence 3433. The later 18 ask persists 11 seconds with displayed size 86 and credits 18.\n\n## 598 reconciliation\n\nThe old 10-second true-print-or-ask union contains 598 negative-pair opportunities. Ask-only ten-second reachability contains **532** before the new capacity gate. The 66 removed events depended on a lower true-print floor on at least one leg. Capacity-adjusted population coverage is not claimed here.\n\n## Corpus recut\n\nThe 392,282 mixed-side episodes become 154,734 ask-side episodes. Dwell bands: 74,391 at zero seconds; 69,363 at 1-9 seconds; 3,785 at 10-29; 2,646 at 30-59; 1,799 at 60-299; and 2,750 at 300 seconds or more. At least ten seconds leaves 10,980 ask-side episodes across 573 events.\n\nThe full arithmetic table and four charts are in NIKVRB_ASK_DWELL_TABLE_CHARTS.html. No live code, scorer, holdout, or production system was used.\n`;
  const visualPayload = { rows, series, markers };
  const baseFiles = {
    "REPLAY_SUMMARY.json": canonical(summary),
    "CORRECTED_ORDER_INTERVALS.json": canonical(corrected.order_intervals),
    "CORRECTED_MATERIAL_DECISIONS.json": canonical(corrected.material_decisions),
    "NIK_MIDWINDOW_ASK_AUTHORITY_RECEIPT.json": canonical(nikMidwindow),
    "ASK_ONLY_DIVOT_DWELL_CENSUS.json": canonical(corpus),
    "ASK_ONLY_OPPORTUNITY_RECONCILIATION.json": canonical(opportunity),
    "EVIDENCE_ABSENT_CAPACITY_RECEIPT.json": canonical({ count: corrected.capacity_evidence_absent.length, rows: corrected.capacity_evidence_absent }),
    "REFERENCE_PANEL.json": canonical({ pair_reference_cents: "NOT_BOUND", delta_to_pair_reference_cents: "NOT_BOUND", forbidden_proxy: "100 - sibling entry", legs: { NIK: { entry_cents: 18, own_window1_close_cents: 19, delta_to_own_window1_close_cents: -1, own_bell_price_cents: 19, delta_to_own_bell_price_cents: -1, own_ask_reachable_low_cents: 18, delta_to_own_ask_reachable_low_cents: 0 }, VRB: { entry_cents: 68, own_window1_close_cents: 83, delta_to_own_window1_close_cents: -15, own_bell_price_cents: 83, delta_to_own_bell_price_cents: -15, own_ask_reachable_low_cents: 68, delta_to_own_ask_reachable_low_cents: 0 } } }),
    "ARITHMETIC_DECISION_ROWS.json": canonical(gzipJson(rows)),
    "FORBIDDEN_ACCESS_RECEIPT.json": canonical({ scorer_invoked: false, population_candidate_score_run: false, live_access: false, network_access: false, order_access: false, position_access: false, holdout_access: false, live_v4_modified: false }),
    "SOURCE_HASH_MANIFEST.json": canonical({ schema_version: "NIKVRB_ASK_DWELL_SOURCE_HASH_MANIFEST_V1", sources: Object.fromEntries(Object.entries(SOURCES).map(([name, rel]) => [name, { path: rel, bytes: read(rel).length, sha256: sha256(read(rel)) }])) }),
    "DETERMINISM_RECEIPT.json": canonical({ schema_version: "NIKVRB_ASK_DWELL_DETERMINISM_V1", method: "main executes two complete build() passes from hash-bound inputs and compares every generated byte before write/check", canonical_core_sha256: sha256(Buffer.from(JSON.stringify({ summary, corpus, opportunity, rows }))), complete_build_passes: 2, byte_identical: true }),
  };
  const docs = { [reportPath]: report, [htmlPath]: html(visualPayload), [specPath]: canonical(spec) };
  const artifactManifest = canonical({ schema_version: "NIKVRB_ASK_DWELL_ARTIFACT_HASH_MANIFEST_V1", artifacts: [...Object.entries(baseFiles).map(([name, content]) => ({ path: `.claude/window1_live_v4_replay/nikvrb_ask_dwell_20260731/${name}`, bytes: Buffer.byteLength(content), sha256: sha256(Buffer.from(content)) })), ...Object.entries(docs).map(([file, content]) => ({ path: path.relative(repo, file).replaceAll("\\", "/"), bytes: Buffer.byteLength(content), sha256: sha256(Buffer.from(content)) }))] });
  baseFiles["ARTIFACT_HASH_MANIFEST.json"] = artifactManifest;
  return { baseFiles, docs, summary, corpus, opportunity, rows };
}

function main() {
  const built = build();
  const rebuilt = build();
  for (const key of ["baseFiles", "docs"]) {
    const first = built[key];
    const second = rebuilt[key];
    if (JSON.stringify(first) !== JSON.stringify(second)) throw new Error(`two-build determinism mismatch: ${key}`);
  }
  if (checkOnly) {
    for (const [name, content] of Object.entries(built.baseFiles)) {
      const file = path.join(outDir, name);
      if (!fs.existsSync(file) || fs.readFileSync(file, "utf8") !== content) throw new Error(`determinism mismatch ${file}`);
    }
    for (const [file, content] of Object.entries(built.docs)) {
      if (!fs.existsSync(file) || fs.readFileSync(file, "utf8") !== content) throw new Error(`determinism mismatch ${file}`);
    }
    process.stdout.write(canonical({ status: "CHECK_PASS", threshold_seconds: ASK_REACH_DWELL_SECONDS, corrected_fills: built.summary.corrected_fills, ask_episodes: built.corpus.total.episodes, prior_598: built.opportunity.primary_prior_denominator, corrected_ask_only: built.opportunity.primary_corrected_denominator, decision_rows: built.rows.length }));
    return;
  }
  fs.mkdirSync(outDir, { recursive: true });
  for (const [name, content] of Object.entries(built.baseFiles)) fs.writeFileSync(path.join(outDir, name), content);
  for (const [file, content] of Object.entries(built.docs)) { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, content); }
  process.stdout.write(canonical({ status: "BUILT", output: path.relative(repo, outDir), corrected_fills: built.summary.corrected_fills, ask_episodes: built.corpus.total.episodes, corrected_ask_only: built.opportunity.primary_corrected_denominator }));
}

main();
