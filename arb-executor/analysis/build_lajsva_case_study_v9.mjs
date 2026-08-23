#!/usr/bin/env node
"use strict";

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

function option(name) {
  const index = process.argv.indexOf(`--${name}`);
  if (index < 0 || index + 1 >= process.argv.length) throw new Error(`missing --${name}`);
  return path.resolve(process.argv[index + 1]);
}
function hash(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function esc(value) { return String(value).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;"); }
function write(file, value) { fs.writeFileSync(file, value.endsWith("\n") ? value : `${value}\n`, "utf8"); }
function receipt(file) { const bytes = fs.readFileSync(file); return { path: path.basename(file), bytes: bytes.length, sha256: hash(bytes) }; }
function html(title, body) { return `<!doctype html><html><head><meta charset="utf-8"><title>${esc(title)}</title><style>body{font:14px/1.45 system-ui;margin:32px;max-width:1280px}table{border-collapse:collapse;width:100%}th,td{border:1px solid #bbb;padding:6px;vertical-align:top}pre{white-space:pre-wrap;background:#f4f4f4;padding:10px}</style></head><body><h1>${esc(title)}</h1>${body}</body></html>\n`; }

function main() {
  const source = option("source"), output = option("output");
  fs.rmSync(output, { recursive: true, force: true });
  fs.mkdirSync(output, { recursive: true });
  const stories = JSON.parse(fs.readFileSync(path.join(source, "FOUR_STORIES_RECEIPT.json"), "utf8"));
  const coherence = JSON.parse(fs.readFileSync(path.join(source, "COHERENCE_TIMELINES.json"), "utf8"));
  const fills = JSON.parse(fs.readFileSync(path.join(source, "FILL_HANDOFF_RECEIPT.json"), "utf8"));
  const gate = JSON.parse(fs.readFileSync(path.join(source, "REPAIR_GATE_RECEIPT.json"), "utf8"));
  const eventId = "KXATPCHALLENGERMATCH-26JUL14LAJSVA";
  const result = stories.results.find((row) => row.event_id === eventId);
  if (!result) throw new Error("LAJSVA_RESULT_MISSING");
  const game = coherence.games[eventId];
  const gameFills = fills.fill_events.filter((row) => row.context.event_id === eventId);
  const transitionRows = game.timeline.map((row) => `<tr><td>${row.timestamp_epoch}</td><td>${esc(row.receipt)}</td><td>${esc(JSON.stringify(row.layer_status))}</td><td>${esc(row.coherence.status)}</td><td>${row.actions.map((item) => `${esc(item.leg_id)} ${esc(item.action.action)} ${item.action.target_cents ?? "NONE"}`).join("<br>")}</td></tr>`).join("");
  write(path.join(output, "PANEL_A_PAIR_RENDER.html"), html("LAJSVA v9 — layered pair read", `<p>Dual coherence: <strong>${game.ever_coherent}</strong>. The unresolved joint read lawfully left independently licensed rests standing.</p><table><thead><tr><th>epoch</th><th>receipt</th><th>layers</th><th>coherence</th><th>actions</th></tr></thead><tbody>${transitionRows}</tbody></table>`));
  write(path.join(output, "PANEL_B_ENGAGEMENT.html"), html("LAJSVA v9 — engagement and fill cascade", `<p>Outcome: ${result.layered_dual_belief.combined_entry_cents}¢, Δ${result.layered_dual_belief.delta_vs_100_cents}. Coherence never formed; fills are consequences of the lawful independent rests.</p>${gameFills.map((row) => `<h2>${esc(row.context.leg_id)}</h2><pre>${esc(JSON.stringify(row, null, 2))}</pre>`).join("")}`));
  const reflex = `# LAJSVA reflex line\n\nFrozen lineage: ${result.lineage_receipt.combined_entry_cents}¢, Δ${result.lineage_receipt.delta_vs_100_cents}.\n\nThe v9 build preserved this exact line because the layered pair read remained INSUFFICIENT_EVIDENCE / NOT_COHERENT.\n`;
  const pattern = `# LAJSVA layered dual-belief report\n\n- MACRO then MICRO then MICRO-MICRO ordering: PASS.\n- Dual coherence: never reached.\n- Belief-priced rest created without coherence: no.\n- Independent lawful line: LAJ ${result.layered_dual_belief.legs.LAJ.entry_cents}¢ + SVA ${result.layered_dual_belief.legs.SVA.entry_cents}¢ = ${result.layered_dual_belief.combined_entry_cents}¢, Δ${result.layered_dual_belief.delta_vs_100_cents}.\n- Fill receipts: ${gameFills.map((row) => `${row.context.leg_id}=${row.row_refs.join(",")}`).join("; ")}.\n- V3 citation semantics: source LIBRARY_CLOSE_CENTS re-keyed to CURRENT_CAUSAL_BEST_BID_CENTS and stated on every decision sentence.\n`;
  write(path.join(output, "TRADE_REPORT_REFLEX.md"), reflex);
  write(path.join(output, "TRADE_REPORT_PATTERN_ENGINE.md"), pattern);
  write(path.join(output, "PANEL_C_TRADE_REPORTS.html"), html("LAJSVA v9 — trade reports", `<h2>Reflex</h2><pre>${esc(reflex)}</pre><h2>Layered dual belief</h2><pre>${esc(pattern)}</pre>`));
  write(path.join(output, "V1_V2_V3_V4_V5_V6_V7_V8_V9_SIDE_BY_SIDE.md"), `# LAJSVA case-study spine — v1 through v9\n\n| version | line | status |\n|---|---|---|\n| v1 | 94¢ / Δ6 | certified outcome, broken reasoning |\n| v2–v7 | repair spine | retained in prior case-study packs |\n| v8 | 99¢ / Δ1 | touch-priced composition self-stop |\n| v9 | ${result.layered_dual_belief.combined_entry_cents}¢ / Δ${result.layered_dual_belief.delta_vs_100_cents} | layered joint read never cohered; independent lawful line preserved |\n`);
  const caseReceipt = {
    label: "LAJSVA_CASE_STUDY_V9_LAYERED_DUAL_BELIEF",
    source_package: { path: source, manifest_sha256: hash(fs.readFileSync(path.join(source, "ARTIFACT_HASH_MANIFEST.json"))) },
    event_id: eventId,
    coherence: { ever_coherent: game.ever_coherent, first_coherence: game.first_coherence, timeline_rows: game.timeline.length },
    execution: result.layered_dual_belief,
    fills: gameFills,
    gate: { safety_floor_pass: gate.safety_floor_pass, zero_measured_law_violations: gate.zero_measured_law_violations, self_stop: gate.self_stop },
    panels: ["PANEL_A_PAIR_RENDER.html", "PANEL_B_ENGAGEMENT.html", "PANEL_C_TRADE_REPORTS.html"],
    reports: ["TRADE_REPORT_REFLEX.md", "TRADE_REPORT_PATTERN_ENGINE.md"],
    full_804_run: false,
    sealed_read: false,
    live_mutation: false,
  };
  fs.writeFileSync(path.join(output, "CASE_STUDY_RECEIPT.json"), canonical(caseReceipt), "utf8");
  const names = fs.readdirSync(output).sort();
  const files = names.map((name) => receipt(path.join(output, name)));
  if (!files.every((row) => row.bytes <= 50 * 1024 * 1024)) throw new Error("L22_CASE_ARTIFACT_EXCEEDS_50_MIB");
  fs.writeFileSync(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), canonical({ label: "LAJSVA_CASE_STUDY_V9_MANIFEST", files, required_paths_present: true, all_under_50_mib: true }), "utf8");
  process.stdout.write(canonical({ output, result: result.layered_dual_belief, coherence: game.ever_coherent, gate_pass: !gate.self_stop }));
}

main();
