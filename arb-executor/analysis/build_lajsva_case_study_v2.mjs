#!/usr/bin/env node
"use strict";

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";
import { execFileSync } from "node:child_process";

const EVENT_ID = "KXATPCHALLENGERMATCH-26JUL14LAJSVA";
const DISCOVERY = 1784007323;
const BELL = 1784078400;
const RAW_COMMIT = "ef6f3975";
const RAW_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/LAJSVA_RAW_TAPE.md";
const V1_COMMIT = "45ddd12bab57cc43ebf15eb288f9e08cc7d4487b";
const V1_ROOT = ".claude/window1_live_v4_replay/lajsva_case_study_v1_20260822";
const REPAIR_ROOT = ".claude/window1_live_v4_replay/v54_repair_pair_clean_diet_fill_handoff_20260822";
const OUT_ROOT = ".claude/window1_live_v4_replay/lajsva_case_study_v2_20260822";

function canonical(value) { return JSON.stringify(value, null, 2) + "\n"; }
function hash(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function ensure(condition, message) { if (!condition) throw new Error(message); }
function esc(value) { return String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;"); }
function md(value) { return String(value ?? "").replaceAll("|", "\\|").replaceAll("\n", " "); }
function gitShow(repo, commit, file) { return execFileSync("git", ["show", `${commit}:${file}`], { cwd: repo, maxBuffer: 128 * 1024 * 1024 }); }
function write(file, value) { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, value.endsWith("\n") ? value : `${value}\n`, "utf8"); }
function fileReceipt(repo, file) { const bytes = fs.readFileSync(file); return { path: path.relative(repo, file).replaceAll("\\", "/"), bytes: bytes.length, sha256: hash(bytes) }; }

function parseRaw(buffer) {
  const rows = [];
  for (const [index, line] of buffer.toString("utf8").split(/\r?\n/).entries()) {
    if (!/^\d+\.\d{3} \|/.test(line)) continue;
    const parts = line.split(" | ");
    const epoch = Number(parts[0]), leg = parts[2], bid = Number(parts[3]) || null, ask = Number(parts[4]) || null, last = Number(parts[5]) || null;
    const tradeMatch = parts[6].match(/^(\d+)c x ([0-9.]+).*trade_id=([a-f0-9-]+)$/);
    rows.push({ line: index + 1, epoch, hours: (epoch - DISCOVERY) / 3600, leg, bid, ask, last, trade: tradeMatch ? { price: Number(tradeMatch[1]), size: Number(tradeMatch[2]), trade_id: tradeMatch[3] } : null, marker: parts[7], receipt: `${RAW_COMMIT}:${RAW_PATH}#L${index + 1}` });
  }
  ensure(rows.length === 1876, `LAJSVA raw rows ${rows.length}`);
  return rows;
}

function parseTrace(file) {
  const lines = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim().split(/\r?\n/).map(JSON.parse);
  return lines.filter((row) => row.event_id === EVENT_ID);
}

function actionRows(stages) {
  return stages.flatMap((stage) => stage.derivations.map((row) => ({
    timestamp_epoch: stage.timestamp_epoch,
    hours: stage.hours_from_discovery,
    trigger: stage.trigger,
    receipt: stage.receipt,
    leg_id: row.leg_id,
    action: row.action.action,
    target_cents: row.action.target_cents,
    before_cents: row.sentence.match(/ACTIVE_TARGET_BEFORE_CENTS=([^.]+)/)?.[1] ?? null,
    query_fingerprint_sha256: row.neighborhood?.[0]?.query_fingerprint_sha256 ?? null,
    fill_handoff_receipt_id: row.derivation.fill_handoff_receipt_id,
    sentence: row.sentence,
  })));
}

function html(title, body, script = "") {
  return `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)}</title><style>
body{margin:0;background:#11161c;color:#edf3f7;font:13px/1.45 ui-monospace,Consolas,monospace}main{max-width:1600px;margin:auto;padding:22px}h1,h2{font-family:system-ui,sans-serif}.panel{background:#182029;border:1px solid #34404d;padding:14px;margin:14px 0}.bad{color:#ff8181}.good{color:#7ce3a8}.warn{color:#ffd166}.muted,.receipt{color:#9fb0c0}.receipt{overflow-wrap:anywhere}canvas{background:#0e1318;border:1px solid #34404d;width:100%;height:620px}table{border-collapse:collapse;width:100%;font-size:12px}th,td{border-bottom:1px solid #34404d;text-align:left;vertical-align:top;padding:6px}th{color:#9fb0c0}.scroll{max-height:620px;overflow:auto}code,pre{white-space:pre-wrap;overflow-wrap:anywhere}.flow{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}.node{border-top:3px solid #5c6b7a;padding:9px;background:#202a34}.node.pass{border-color:#7ce3a8}.node.fail{border-color:#ff8181}@media(max-width:800px){.flow{grid-template-columns:1fr}}
</style></head><body><main>${body}</main>${script ? `<script>${script}</script>` : ""}</body></html>`;
}

function panelA(raw, actions, receipts) {
  const plotRows = raw.filter((row) => row.bid || row.ask || row.last || row.trade).map((row) => ({ h: row.hours, leg: row.leg, bid: row.bid, ask: row.ask, last: row.last, trade: row.trade?.price ?? null }));
  const actionData = actions.map((row) => ({ h: row.hours, leg: row.leg_id, target: row.target_cents, action: row.action, receipt: row.receipt }));
  const body = `<h1>Panel A — LAJSVA repaired pair render</h1><p class="muted">CASE STUDY v2 · full lawful span · both books + repaired rests · gate result shown, not tuned</p><section class="panel"><canvas id="chart" width="1500" height="620"></canvas><p>Lines: bid green · ask red · last blue · repaired rest yellow. Vertical scale is cents; horizontal scale is hours from discovery.</p></section><section class="panel"><h2>Result</h2><p><span class="bad">Candidate safety failed:</span> LAJ credited 54¢; SVA remained uncredited at 40¢. The baseline spine remains SVA 41 + LAJ 53 = 94¢, Δ6.</p><p class="receipt">${esc(receipts.trace)} · ${esc(receipts.gate)}</p></section>`;
  const script = `const R=${JSON.stringify(plotRows)},A=${JSON.stringify(actionData)};const c=document.getElementById('chart'),x=c.getContext('2d'),W=c.width,H=c.height,p=50,split=H/2;const xmax=Math.max(...R.map(r=>r.h));function xx(h){return p+h/xmax*(W-2*p)}function yy(v,leg){const top=leg==='LAJ'?15:split+15,bot=leg==='LAJ'?split-25:H-25;return bot-(v/100)*(bot-top)}function line(rows,key,color,leg){x.strokeStyle=color;x.lineWidth=1.4;x.beginPath();let on=false;for(const r of rows.filter(q=>q.leg===leg)){if(r[key]==null)continue;const X=xx(r.h),Y=yy(r[key],leg);if(!on){x.moveTo(X,Y);on=true}else x.lineTo(X,Y)}x.stroke()}x.fillStyle='#edf3f7';x.font='14px monospace';for(const [leg,y] of [['LAJ',25],['SVA',split+25]])x.fillText(leg,8,y);for(const leg of ['LAJ','SVA']){const z=R.filter(r=>r.leg===leg);line(z,'bid','#61d0ad',leg);line(z,'ask','#ff8e7d',leg);line(z,'last','#73a7ff',leg);const aa=A.filter(a=>a.leg===leg&&a.target!=null);line(aa,'target','#ffd166',leg);for(const r of z.filter(q=>q.trade!=null)){x.fillStyle='#d5a6ff';x.fillRect(xx(r.h)-1,yy(r.trade,leg)-1,3,3)}}x.strokeStyle='#34404d';x.beginPath();x.moveTo(0,split);x.lineTo(W,split);x.stroke();`;
  return html("LAJSVA Case Study v2 — Panel A", body, script);
}

function panelB(stages, fillEvents, actions, receipts) {
  const laFill = fillEvents.find((row) => row.fill_event_receipt.context.leg_id === "LAJ")?.fill_event_receipt;
  const handoff = actions.find((row) => row.fill_handoff_receipt_id);
  const rows = stages.map((stage, index) => {
    const pos = stage.reads.half_pair_state.value;
    const perLeg = stage.derivations.map((row) => `${row.leg_id}:${row.action.action}@${row.action.target_cents ?? "—"}`).join(" · ");
    const hand = stage.derivations.map((row) => row.derivation.fill_handoff_receipt_id).filter(Boolean).join(", ") || "—";
    return `<tr><td>${index + 1}</td><td>${stage.hours_from_discovery.toFixed(6)}</td><td>${esc(stage.trigger)}</td><td>${pos.credited_count} / ${pos.entry_sum_cents}</td><td>${esc(perLeg)}</td><td>${esc(hand)}</td><td class="receipt">${esc(stage.receipt)}</td></tr>`;
  }).join("");
  const body = `<h1>Panel B — fill cascade as receipts</h1><p class="muted">CASE STUDY v2 · the handoff is mechanically present; the safety result is still broken.</p><section class="panel"><div class="flow"><div class="node pass"><b>L1 · fill</b><br>LAJ 54¢<br><span class="receipt">${esc(laFill?.receipt_id)}</span></div><div class="node pass"><b>L2 · half-pair flip</b><br>credited_count 0→1<br><span class="receipt">${esc(laFill?.captured_at_receipt)}</span></div><div class="node pass"><b>L3 · fingerprint</b><br>${esc(handoff?.query_fingerprint_sha256)}</div><div class="node pass"><b>L4 · re-derive</b><br>SVA ${esc(handoff?.target_cents)}¢ immediate<br>40¢ terminal<br><span class="receipt">${esc(handoff?.fill_handoff_receipt_id)}</span></div><div class="node fail"><b>L5 · outcome</b><br>SVA never credited<br>safety Δ6 not held</div></div></section><section class="panel"><h2>Every engagement stage</h2><div class="scroll"><table><thead><tr><th>#</th><th>H+</th><th>Trigger</th><th>Credited / sum</th><th>Actions</th><th>Fill handoff</th><th>Receipt</th></tr></thead><tbody>${rows}</tbody></table></div></section><p class="receipt">${esc(receipts.handoff)} · ${esc(receipts.trace)}</p>`;
  return html("LAJSVA Case Study v2 — Panel B", body);
}

function tradeReportRepair(stages, actions, fills, receipts) {
  const rows = actions.map((row, index) => `| ${index + 1} | ${row.hours.toFixed(6)} | ${row.leg_id} | ${row.action} | ${row.before_cents}→${row.target_cents ?? "NONE"} | ${md(row.fill_handoff_receipt_id ?? "—")} | ${md(row.receipt)} |`).join("\n");
  const laj = fills.find((row) => row.fill_event_receipt.context.leg_id === "LAJ")?.fill_event_receipt;
  const last = stages.at(-1);
  return `# TRADE REPORT — repaired pattern engine — LAJSVA\n\n## 1 — WHAT I BELIEVED AT OPEN\n\nThe engine asked a leave-self-out pattern question using bell-bounded lows only; unbounded path lows were unavailable. [receipt: ${receipts.library}]\n\n## 2 — WHAT I DECIDED PER SIDE AND WHY\n\nThe clean diet moved the old 47/36 terminal posture to LAJ 54 / SVA 40. No placement constant was added; the same derivation consumed rematerialized neighbor paths. [receipt: ${last.receipt}]\n\n## 3 — EACH ACTION AT EACH PRICE WITH ITS REASON AT THAT TIME\n\n| # | H+ | leg | action | before→target | handoff | receipt |\n|---:|---:|---|---|---:|---|---|\n${rows}\n\n## 4 — WHAT HAPPENED\n\nLAJ credited 54¢ on trade ${laj?.context?.original_fill_receipt ?? laj?.row_refs?.[0]}; the half-pair state flipped and SVA was re-derived on that receipt. SVA stood 40¢ and never credited. The repair therefore did not hold the certified Δ6 completion. [receipt: ${laj?.receipt_id}; ${receipts.handoff}]\n\n## 5 — MY GRADE OF MY OWN TRADE\n\nDecision grade: **MIXED** — diet and handoff defects are repaired mechanically, but the resulting first-side price and sibling level break the required safety floor. Outcome grade: **BAD — partial only**. [receipt: ${receipts.gate}]\n\n## 6 — WHAT I'D FLAG FOR THE LIBRARY\n\nThe bell-bound diet is now honest, and the fill cascade is now visible. The remaining miss is not authority to tune: SVA 41 was not reached by the repaired 40 rest, while LAJ credited first at 54. The self-stop is the filed outcome. [receipt: ${receipts.gate}]\n`;
}

function tradeReportBaseline(receipts) {
  return `# TRADE REPORT — certified baseline — LAJSVA\n\n## 1 — WHAT I BELIEVED AT OPEN\n\nThe baseline was a tracking reflex, not a pair belief. [receipt: ${V1_COMMIT}:${V1_ROOT}/TRADE_REPORT_REFLEX.md]\n\n## 2 — WHAT I DECIDED PER SIDE AND WHY\n\nIt tracked SVA to 41¢ and LAJ to 53¢ without a receipt-bearing fill handoff. [receipt: ${V1_COMMIT}:${V1_ROOT}/CASE_STUDY_RECEIPT.json]\n\n## 3 — EACH ACTION AT EACH PRICE WITH ITS REASON AT THAT TIME\n\nThe complete 54-action table is retained byte-for-byte in case-study v1. [receipt: ${V1_COMMIT}:${V1_ROOT}/TRADE_REPORT_REFLEX.md]\n\n## 4 — WHAT HAPPENED\n\nSVA 41 + LAJ 53 = 94¢, Δ6. [receipt: ${V1_COMMIT}:${V1_ROOT}/CASE_STUDY_RECEIPT.json]\n\n## 5 — MY GRADE OF MY OWN TRADE\n\nDecision **BAD** because no belief/handoff existed; outcome **GOOD, separately** because it completed at Δ6. [receipt: ${V1_COMMIT}:${V1_ROOT}/TRADE_REPORT_REFLEX.md]\n\n## 6 — WHAT I'D FLAG FOR THE LIBRARY\n\nThe certified v1 report flags both the unbounded low diet and absent fill handoff. [receipt: ${receipts.v1}]\n`;
}

function panelC(baseline, repair, receipts) {
  const body = `<h1>Panel C — trade reports</h1><p class="muted">F-VS-055 order · decision and outcome graded separately</p><section class="panel"><h2>Certified baseline</h2><pre>${esc(baseline)}</pre></section><section class="panel"><h2>Repair candidate</h2><pre>${esc(repair)}</pre></section><p class="receipt">${esc(receipts.v1)} · ${esc(receipts.gate)}</p>`;
  return html("LAJSVA Case Study v2 — Panel C", body);
}

function main() {
  const repo = path.resolve(process.argv[2] ?? process.cwd());
  const repairRoot = path.join(repo, REPAIR_ROOT), out = path.join(repo, OUT_ROOT);
  const rawBytes = gitShow(repo, RAW_COMMIT, RAW_PATH), raw = parseRaw(rawBytes);
  const traceFile = path.join(repairRoot, "REPAIR_FOUR_GAME_TRACE.jsonl.gz"), traceBytes = fs.readFileSync(traceFile), trace = parseTrace(traceFile);
  const stages = trace.filter((row) => row.kind === "DECISION_STAGE"), fillEvents = trace.filter((row) => row.kind === "FILL_EVENT"), actions = actionRows(stages);
  const gateFile = path.join(repairRoot, "REPAIR_GATE_RECEIPT.json"), handoffFile = path.join(repairRoot, "FILL_HANDOFF_RECEIPT.json"), libraryFile = path.join(repairRoot, "LIBRARY_BELL_BOUND_RECEIPT.json");
  const receipts = {
    trace: `${REPAIR_ROOT}/REPAIR_FOUR_GAME_TRACE.jsonl.gz@sha256:${hash(traceBytes)}`,
    gate: `${REPAIR_ROOT}/REPAIR_GATE_RECEIPT.json@sha256:${hash(fs.readFileSync(gateFile))}`,
    handoff: `${REPAIR_ROOT}/FILL_HANDOFF_RECEIPT.json@sha256:${hash(fs.readFileSync(handoffFile))}`,
    library: `${REPAIR_ROOT}/LIBRARY_BELL_BOUND_RECEIPT.json@sha256:${hash(fs.readFileSync(libraryFile))}`,
    v1: `${V1_COMMIT}:${V1_ROOT}/CASE_STUDY_RECEIPT.json`,
  };
  const repairReport = tradeReportRepair(stages, actions, fillEvents, receipts), baselineReport = tradeReportBaseline(receipts);
  const files = {
    panel_a: path.join(out, "PANEL_A_PAIR_RENDER.html"), panel_b: path.join(out, "PANEL_B_ENGAGEMENT.html"), panel_c: path.join(out, "PANEL_C_TRADE_REPORTS.html"),
    baseline: path.join(out, "TRADE_REPORT_BASELINE.md"), repair: path.join(out, "TRADE_REPORT_REPAIR.md"), compare: path.join(out, "V1_V2_SIDE_BY_SIDE.md"), receipt: path.join(out, "CASE_STUDY_RECEIPT.json"), manifest: path.join(out, "ARTIFACT_HASH_MANIFEST.json"),
  };
  write(files.panel_a, panelA(raw, actions, receipts));
  write(files.panel_b, panelB(stages, fillEvents, actions, receipts));
  write(files.panel_c, panelC(baselineReport, repairReport, receipts));
  write(files.baseline, baselineReport); write(files.repair, repairReport);
  write(files.compare, `# LAJSVA case study — v1 vs v2\n\n| spine | v1 certified as-occurred | v2 clean-diet + handoff candidate |\n|---|---|---|\n| Library diet | full path, lows contaminated by in-play tails | every served path bell-bounded; unbounded rows expose no low/reach/floor |\n| Fill handoff | absent; Panel B broken after SVA fill | present as receipt chain; LAJ fill re-poses query and re-derives SVA |\n| Outcome | SVA 41 + LAJ 53 = 94, Δ6 | LAJ 54 only; SVA 40 never credited |\n| Gate | certified baseline | **SELF-STOP: safety floor failed** |\n\nV1: ${receipts.v1}\n\nV2 gate: ${receipts.gate}\n`);
  const outputs = Object.entries(files).filter(([key]) => !["receipt", "manifest"].includes(key)).map(([, file]) => fileReceipt(repo, file));
  const lajFill = fillEvents.find((row) => row.fill_event_receipt.context.leg_id === "LAJ")?.fill_event_receipt;
  const handoff = actions.find((row) => row.fill_handoff_receipt_id);
  write(files.receipt, canonical({ label: "LAJSVA_CASE_STUDY_V2_CLEAN_DIET_FILL_HANDOFF", event_id: EVENT_ID, scope: { four_known_games_only: true, full_804_run: false, sealed_read: false, live_mutation: false }, sources: { raw: `${RAW_COMMIT}:${RAW_PATH}@sha256:${hash(rawBytes)}`, ...receipts }, panel_a: { full_span_rows: raw.length, repaired_action_rows: actions.length }, panel_b: { status: "FILL_HANDOFF_WIRED_BUT_SAFETY_GATE_BROKEN", fill_event_receipt_id: lajFill?.receipt_id, handoff_receipt_id: handoff?.fill_handoff_receipt_id, reposed_query_fingerprint_sha256: handoff?.query_fingerprint_sha256, open_side_target_cents: handoff?.target_cents, open_side_filled: false }, panel_c: { reports: 2, sections_each: 6, repair_decision_grade: "MIXED", repair_outcome_grade: "BAD_PARTIAL" }, v1_v2: { baseline: "COMPLETE_94_DELTA_6", repair: "PARTIAL_LAJ_54_SVA_UNCREDITED_40", accepted_repair: false, self_stop: true }, outputs }));
  const manifestRows = [...outputs, fileReceipt(repo, files.receipt)];
  write(files.manifest, canonical({ label: "LAJSVA_CASE_STUDY_V2_MANIFEST", root: OUT_ROOT, files: manifestRows, all_under_50_mb: manifestRows.every((row) => row.bytes <= 50 * 1024 * 1024) }));
  console.log(canonical({ output: OUT_ROOT, stages: stages.length, actions: actions.length, fill_events: fillEvents.length, gate: "SELF_STOP_SAFETY_FLOOR_BREAK" }));
}

main();
