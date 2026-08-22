#!/usr/bin/env node
"use strict";

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";
import { execFileSync } from "node:child_process";

const EVENT_ID = "KXATPCHALLENGERMATCH-26JUL14LAJSVA";
const DISCOVERY = 1784007323;
const RAW_COMMIT = "ef6f3975";
const RAW_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/LAJSVA_RAW_TAPE.md";
const V1_COMMIT = "45ddd12bab57cc43ebf15eb288f9e08cc7d4487b";
const V1_ROOT = ".claude/window1_live_v4_replay/lajsva_case_study_v1_20260822";
const V2_ROOT = ".claude/window1_live_v4_replay/lajsva_case_study_v2_20260822";
const REPAIR_ROOT = ".claude/window1_live_v4_replay/v54_repair_iteration2_foundation_conditional_dip_early_riser_20260822";
const OUT_ROOT = ".claude/window1_live_v4_replay/lajsva_case_study_v3_20260822";

function canonical(value) { return JSON.stringify(value, null, 2) + "\n"; }
function hash(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function esc(value) { return String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;"); }
function gitShow(repo, commit, file) { return execFileSync("git", ["show", `${commit}:${file}`], { cwd: repo, maxBuffer: 128 * 1024 * 1024 }); }
function write(file, value) { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, value.endsWith("\n") ? value : `${value}\n`, "utf8"); }
function fileReceipt(repo, file) { const bytes = fs.readFileSync(file); return { path: path.relative(repo, file).replaceAll("\\", "/"), bytes: bytes.length, sha256: hash(bytes) }; }
function html(title, body, script = "") { return `<!doctype html><html><head><meta charset="utf-8"><title>${esc(title)}</title><style>body{margin:0;background:#11161c;color:#edf3f7;font:13px/1.45 ui-monospace,Consolas,monospace}main{max-width:1600px;margin:auto;padding:22px}h1,h2{font-family:system-ui,sans-serif}.panel{background:#182029;border:1px solid #34404d;padding:14px;margin:14px 0}.good{color:#7ce3a8}.bad{color:#ff8181}.muted,.receipt{color:#9fb0c0}.receipt{overflow-wrap:anywhere}canvas{background:#0e1318;border:1px solid #34404d;width:100%;height:620px}table{border-collapse:collapse;width:100%;font-size:12px}th,td{border-bottom:1px solid #34404d;text-align:left;vertical-align:top;padding:6px}th{color:#9fb0c0}.scroll{max-height:620px;overflow:auto}pre{white-space:pre-wrap;overflow-wrap:anywhere}.flow{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}.node{border-top:3px solid #5c6b7a;padding:9px;background:#202a34}.node.pass{border-color:#7ce3a8}.node.fail{border-color:#ff8181}</style></head><body><main>${body}</main>${script ? `<script>${script}</script>` : ""}</body></html>`; }

function parseRaw(buffer) {
  const rows = [];
  for (const [index, line] of buffer.toString("utf8").split(/\r?\n/).entries()) {
    if (!/^\d+\.\d{3} \|/.test(line)) continue;
    const parts = line.split(" | "), epoch = Number(parts[0]);
    const trade = parts[6].match(/^(\d+)c x ([0-9.]+).*trade_id=([a-f0-9-]+)$/);
    rows.push({ epoch, hours: (epoch - DISCOVERY) / 3600, leg: parts[2], bid: Number(parts[3]) || null, ask: Number(parts[4]) || null, last: Number(parts[5]) || null, trade: trade ? Number(trade[1]) : null, receipt: `${RAW_COMMIT}:${RAW_PATH}#L${index + 1}` });
  }
  return rows;
}

function outcome(trace) {
  const last = trace.filter((row) => row.kind === "DECISION_STAGE").at(-1);
  const positions = last?.reads?.half_pair_state?.value?.legs ?? {};
  const entries = Object.values(positions).filter((row) => row.credited).map((row) => row.entry_cents);
  return { completed: entries.length === 2, pair_cents: entries.length === 2 ? entries.reduce((a, b) => a + b, 0) : null, delta_cents: entries.length === 2 ? 100 - entries.reduce((a, b) => a + b, 0) : null, positions };
}

function main() {
  const repo = path.resolve(process.argv[2] ?? process.cwd()), repair = path.join(repo, REPAIR_ROOT), out = path.join(repo, OUT_ROOT);
  const rawBytes = gitShow(repo, RAW_COMMIT, RAW_PATH), raw = parseRaw(rawBytes);
  const traceFile = path.join(repair, "REPAIR_FOUR_GAME_TRACE.jsonl.gz"), traceBytes = fs.readFileSync(traceFile);
  const trace = zlib.gunzipSync(traceBytes).toString("utf8").trim().split(/\r?\n/).filter(Boolean).map(JSON.parse).filter((row) => row.event_id === EVENT_ID);
  const stages = trace.filter((row) => row.kind === "DECISION_STAGE"), fills = trace.filter((row) => row.kind === "FILL_EVENT").map((row) => row.fill_event_receipt);
  const actions = stages.flatMap((stage) => stage.derivations.map((row) => ({ hours: stage.hours_from_discovery, timestamp_epoch: stage.timestamp_epoch, receipt: stage.receipt, trigger: stage.trigger, leg: row.leg_id, action: row.action.action, target: row.action.target_cents, authority: row.derivation.target_authority, evidence: row.derivation.neighbor_leg.own_evidence, distribution: row.derivation.neighbor_leg.conditional_remaining_dip_distribution_cents, handoff: row.derivation.fill_handoff_receipt_id, sentence: row.sentence })));
  const result = outcome(trace), gate = JSON.parse(fs.readFileSync(path.join(repair, "REPAIR_GATE_RECEIPT.json"), "utf8"));
  const receipts = { trace: `${REPAIR_ROOT}/REPAIR_FOUR_GAME_TRACE.jsonl.gz@sha256:${hash(traceBytes)}`, gate: `${REPAIR_ROOT}/REPAIR_GATE_RECEIPT.json@sha256:${hash(fs.readFileSync(path.join(repair, "REPAIR_GATE_RECEIPT.json")))}`, conditional: `${REPAIR_ROOT}/CONDITIONAL_DIP_RECEIPT.json@sha256:${hash(fs.readFileSync(path.join(repair, "CONDITIONAL_DIP_RECEIPT.json")))}`, foundation: `${REPAIR_ROOT}/FOUNDATION_LIBRARY_RECEIPT.json@sha256:${hash(fs.readFileSync(path.join(repair, "FOUNDATION_LIBRARY_RECEIPT.json")))}` };
  const files = { a: path.join(out, "PANEL_A_PAIR_RENDER.html"), b: path.join(out, "PANEL_B_ENGAGEMENT.html"), c: path.join(out, "PANEL_C_TRADE_REPORTS.html"), base: path.join(out, "TRADE_REPORT_BASELINE.md"), repair: path.join(out, "TRADE_REPORT_REPAIR.md"), spine: path.join(out, "V1_V2_V3_SIDE_BY_SIDE.md"), receipt: path.join(out, "CASE_STUDY_RECEIPT.json"), determinism: path.join(out, "DETERMINISM_RECEIPT.json"), manifest: path.join(out, "ARTIFACT_HASH_MANIFEST.json") };

  const plot = raw.map((row) => ({ h: row.hours, leg: row.leg, bid: row.bid, ask: row.ask, last: row.last, trade: row.trade }));
  const panelABody = `<h1>Panel A — LAJSVA repair iteration 2</h1><p class="muted">Full W1 pair tape; bids, asks, last, prints, and the conditional-dip rest.</p><section class="panel"><canvas id="chart" width="1500" height="620"></canvas></section><section class="panel"><h2>Outcome</h2><p class="${result.completed && result.delta_cents >= 6 ? "good" : "bad"}">${result.completed ? `${result.pair_cents}¢, Δ${result.delta_cents}` : "partial"}</p><p class="receipt">${esc(receipts.trace)} · ${esc(receipts.conditional)}</p></section>`;
  const panelAScript = `const R=${JSON.stringify(plot)},A=${JSON.stringify(actions)};const c=document.getElementById('chart'),x=c.getContext('2d'),W=c.width,H=c.height,p=50,s=H/2,m=Math.max(...R.map(r=>r.h));function xx(h){return p+h/m*(W-2*p)}function yy(v,l){const t=l==='LAJ'?15:s+15,b=l==='LAJ'?s-25:H-25;return b-v/100*(b-t)}function line(q,k,col,l){x.strokeStyle=col;x.beginPath();let z=0;for(const r of q.filter(r=>r.leg===l&&r[k]!=null)){const X=xx(r.h),Y=yy(r[k],l);z?x.lineTo(X,Y):x.moveTo(X,Y);z=1}x.stroke()}for(const l of ['LAJ','SVA']){line(R,'bid','#61d0ad',l);line(R,'ask','#ff8e7d',l);line(R,'last','#73a7ff',l);line(A,'target','#ffd166',l)}x.strokeStyle='#34404d';x.beginPath();x.moveTo(0,s);x.lineTo(W,s);x.stroke();`;
  write(files.a, html("LAJSVA v3 — Panel A", panelABody, panelAScript));

  const stageRows = stages.map((stage, index) => `<tr><td>${index + 1}</td><td>${stage.hours_from_discovery.toFixed(6)}</td><td>${esc(stage.trigger)}</td><td>${esc(stage.derivations.map((row) => `${row.leg_id}:${row.action.action}@${row.action.target_cents ?? "—"} via ${row.derivation.target_authority}`).join(" · "))}</td><td>${esc(stage.derivations.map((row) => row.derivation.fill_handoff_receipt_id).filter(Boolean).join(", ") || "—")}</td><td class="receipt">${esc(stage.receipt)}</td></tr>`).join("");
  const fillNodes = fills.map((fill) => `<div class="node pass"><b>${esc(fill.context.leg_id)} ${fill.context.entry_cents}¢</b><br>${esc(fill.context.transition)}<br><span class="receipt">${esc(fill.receipt_id)}</span></div>`).join("");
  write(files.b, html("LAJSVA v3 — Panel B", `<h1>Panel B — engagement and fill cascade</h1><section class="panel"><div class="flow">${fillNodes || '<div class="node fail">No fills</div>'}</div></section><section class="panel"><div class="scroll"><table><thead><tr><th>#</th><th>H+</th><th>trigger</th><th>actions</th><th>handoff</th><th>receipt</th></tr></thead><tbody>${stageRows}</tbody></table></div></section><p class="receipt">${esc(receipts.gate)}</p>`));

  const baselineReport = `# TRADE REPORT — certified baseline — LAJSVA\n\nDecision frame: tracking reflex. Outcome: SVA 41 + LAJ 53 = 94¢, Δ6.\n\nReceipt: ${V1_COMMIT}:${V1_ROOT}/CASE_STUDY_RECEIPT.json\n`;
  const actionTable = actions.map((row, index) => `| ${index + 1} | ${row.hours.toFixed(6)} | ${row.leg} | ${row.action} | ${row.target ?? "—"} | ${row.authority} | ${row.evidence.basis}:${row.evidence.observed_low_cents ?? "—"} | ${row.distribution.q25 ?? "—"}/${row.distribution.q50 ?? "—"}/${row.distribution.q75 ?? "—"} | ${row.receipt} |`).join("\n");
  const repairReport = `# TRADE REPORT — Foundation + conditional dip + early riser — LAJSVA\n\n## Decision\n\nThe level derives from this leg's own dip/no-dip state and the q50 remaining dip of same-state, native-bell-bounded MINUTE neighbors. No blanket ratio or placement constant is consumed.\n\n| # | H+ | leg | action | target | authority | own evidence | q25/q50/q75 | receipt |\n|---:|---:|---|---|---:|---|---|---|---|\n${actionTable}\n\n## Fill cascade\n\n${fills.map((fill) => `${fill.context.leg_id} ${fill.context.entry_cents}¢ at ${fill.captured_at_receipt} [${fill.receipt_id}]`).join("\n") || "No fill."}\n\n## Outcome\n\n${result.completed ? `${result.pair_cents}¢, Δ${result.delta_cents}.` : "Partial."}\n\nReceipts: ${receipts.foundation} · ${receipts.conditional} · ${receipts.gate}\n`;
  write(files.base, baselineReport); write(files.repair, repairReport);
  write(files.c, html("LAJSVA v3 — Panel C", `<h1>Panel C — both trade reports</h1><section class="panel"><h2>v1 certified baseline</h2><pre>${esc(baselineReport)}</pre></section><section class="panel"><h2>v3 repaired machine</h2><pre>${esc(repairReport)}</pre></section>`));
  write(files.spine, `# LAJSVA case-study spine — v1 / v2 / v3\n\n| version | library | fill handoff | outcome | status |\n|---|---|---|---|---|\n| v1 | future-contaminated path lows | absent | 41+53=94, Δ6 | certified outcome / broken reasoning |\n| v2 | 698 bounded; 11,811 unbounded | receipt chain repaired | LAJ 54 only; SVA 40 missed | self-stopped |\n| v3 | Foundation native-bell MINUTE store + descriptive spike atlas | receipt chain retained | ${result.completed ? `${result.pair_cents}, Δ${result.delta_cents}` : "partial"} | ${gate.self_stop ? `self-stop: ${gate.stop_reason}` : "gate pass"} |\n\nV1 receipt: ${V1_COMMIT}:${V1_ROOT}/CASE_STUDY_RECEIPT.json\n\nV2 receipt: ${V2_ROOT}/CASE_STUDY_RECEIPT.json\n\nV3 receipt: ${receipts.gate}\n`);
  const generated = [files.a, files.b, files.c, files.base, files.repair, files.spine].map((file) => fileReceipt(repo, file));
  write(files.receipt, canonical({ label: "LAJSVA_CASE_STUDY_V3_FOUNDATION_CONDITIONAL_DIP_EARLY_RISER", event_id: EVENT_ID, scope: { four_games_only: true, full_804_run: false, sealed_read: false, live_mutation: false }, sources: { raw: `${RAW_COMMIT}:${RAW_PATH}@sha256:${hash(rawBytes)}`, ...receipts }, panel_a: { full_span_rows: raw.length, action_rows: actions.length }, panel_b: { fill_events: fills, cascade_shown_as_receipts: true }, panel_c: { trade_reports: 2 }, v1_v2_v3: { v1: "COMPLETE_94_DELTA_6", v2: "PARTIAL", v3: result }, outputs: generated }));
  const manifestRows = [...generated, fileReceipt(repo, files.receipt)];
  write(files.manifest, canonical({ label: "LAJSVA_CASE_STUDY_V3_MANIFEST", files: manifestRows, all_under_50_mb: manifestRows.every((row) => row.bytes <= 50 * 1024 * 1024) }));
  const expectedFirstManifestHash = process.argv[3] ?? null;
  if (expectedFirstManifestHash) {
    const secondManifestHash = hash(fs.readFileSync(files.manifest));
    if (expectedFirstManifestHash !== secondManifestHash) throw new Error(`CASE_STUDY_V3_DETERMINISM_FAILED ${expectedFirstManifestHash} != ${secondManifestHash}`);
    write(files.determinism, canonical({ label: "LAJSVA_CASE_STUDY_V3_DETERMINISM_X2", two_clean_builds: true, first_manifest_sha256: expectedFirstManifestHash, second_manifest_sha256: secondManifestHash, byte_identical: true }));
    const withDeterminism = [...manifestRows, fileReceipt(repo, files.determinism)];
    write(files.manifest, canonical({ label: "LAJSVA_CASE_STUDY_V3_MANIFEST", files: withDeterminism, all_under_50_mb: withDeterminism.every((row) => row.bytes <= 50 * 1024 * 1024) }));
  }
  process.stdout.write(canonical({ output: OUT_ROOT, result, self_stop: gate.self_stop }));
}

main();
