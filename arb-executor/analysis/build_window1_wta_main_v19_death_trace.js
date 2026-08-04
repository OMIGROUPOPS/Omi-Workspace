#!/usr/bin/env node
"use strict";

const crypto = require("crypto"), fs = require("fs"), path = require("path"), zlib = require("zlib");
const args = process.argv.slice(2), value = (name, fallback) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
const repo = path.resolve(value("--repo", "."));
const out = path.resolve(value("--output", path.join(repo, ".claude/window1_live_v4_replay/wta_main_v19_death_trace_20260804")));
const source = path.join(repo, ".claude/window1_live_v4_replay/pair_couple_abstention_v19_20260803/POPULATION_EVENT_LEDGER.jsonl.gz");
const raw = "https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated";
function canonical(x) { return `${JSON.stringify(x, null, 2)}\n`; }
function sha256(x) { return crypto.createHash("sha256").update(x).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function readRows(file) { return zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim().split(/\r?\n/).map(JSON.parse); }
function gzipRows(rows) { return zlib.gzipSync(Buffer.from(`${rows.map(JSON.stringify).join("\n")}\n`), { level: 9, mtime: 0 }); }
function countBy(rows, key) { const out = {}; for (const row of rows) { const k = key(row); out[k] = (out[k] || 0) + 1; } return Object.fromEntries(Object.entries(out).sort()); }
function classify(event) {
  const legs = Object.values(event.legs), closesAvailable = legs.every((leg) => Number.isInteger(leg.own_window1_close_cents));
  if (!event.completed_pair) return "NO_COMPLETION";
  if (event.combined_entry_cents >= 100) return "COMPLETION_AT_OR_ABOVE_100";
  if (!closesAvailable) return "OWN_CLOSE_UNAVAILABLE";
  if (!legs.every((leg) => leg.entry_cents < leg.own_window1_close_cents)) return "ONE_OR_BOTH_LEGS_AT_OR_ABOVE_OWN_CLOSE";
  return "JOINT_OBJECTIVE_PASS";
}
function main() {
  const rows = readRows(source).filter((event) => event.category === "WTA_MAIN");
  if (rows.length !== 152) throw new Error(`expected 152 WTA_MAIN events, got ${rows.length}`);
  const ledger = rows.map((event) => ({ event_id: event.event_id, category: event.category, starting_price_region: event.starting_price_split, death_stage: classify(event), completed_pair: event.completed_pair, combined_entry_cents: event.combined_entry_cents, pair_under_par: event.pair_under_par, both_legs_strictly_below_close: event.both_legs_strictly_below_close, legs: Object.fromEntries(Object.entries(event.legs).map(([id, leg]) => [id, { acted: leg.acted, credited: leg.credited, entry_cents: leg.entry_cents, own_window1_close_cents: leg.own_window1_close_cents, entry_minus_own_window1_close_cents: leg.entry_minus_own_window1_close_cents, terminal_reason: leg.terminal_reason }])) })).sort((a, b) => a.event_id.localeCompare(b.event_id));
  const regions = [...new Set(ledger.map((row) => row.starting_price_region))].sort().map((region) => { const xs = ledger.filter((row) => row.starting_price_region === region); return { category: "WTA_MAIN", starting_price_region: region, D: xs.length, death_stages: countBy(xs, (row) => row.death_stage), event_ids_by_stage: Object.fromEntries([...new Set(xs.map((row) => row.death_stage))].sort().map((stage) => [stage, xs.filter((row) => row.death_stage === stage).map((row) => row.event_id).sort()])) }; });
  const census = { schema_version: "WINDOW1_WTA_MAIN_V19_DEATH_TRACE_20260804", D: 152, category: "WTA_MAIN", death_stages: countBy(ledger, (row) => row.death_stage), joint_objective_law: "PAIR_STRICTLY_UNDER_PAR_AND_BOTH_LEGS_STRICTLY_BELOW_OWN_W1_CLOSE", joint_objective_pairs: ledger.filter((row) => row.death_stage === "JOINT_OBJECTIVE_PASS").length, conservation: ledger.length, category_and_starting_price_region: regions };
  if (census.joint_objective_pairs !== 0 || Object.values(census.death_stages).reduce((a, b) => a + b, 0) !== 152) throw new Error("WTA_MAIN conservation or expected zero-JOINT mismatch");
  fs.mkdirSync(out, { recursive: true });
  fs.writeFileSync(path.join(out, "WTA_MAIN_EVENT_DEATH_LEDGER.jsonl.gz"), gzipRows(ledger));
  fs.writeFileSync(path.join(out, "WTA_MAIN_DEATH_CENSUS.json"), canonical(census));
  const artifactRel = ".claude/window1_live_v4_replay/wta_main_v19_death_trace_20260804";
  fs.writeFileSync(path.join(out, "REPORT.md"), `# WTA_MAIN V19 death trace\n\n- Census: ${raw}/${artifactRel}/WTA_MAIN_DEATH_CENSUS.json\n- Per-event ledger: ${raw}/${artifactRel}/WTA_MAIN_EVENT_DEATH_LEDGER.jsonl.gz\n`);
  fs.writeFileSync(path.join(out, "SOURCE_HASH_MANIFEST.json"), canonical({ files: { ".claude/window1_live_v4_replay/pair_couple_abstention_v19_20260803/POPULATION_EVENT_LEDGER.jsonl.gz": { sha256: hashFile(source), bytes: fs.statSync(source).size }, "arb-executor/analysis/build_window1_wta_main_v19_death_trace.js": { sha256: hashFile(__filename), bytes: fs.statSync(__filename).size } } }));
  const names = fs.readdirSync(out).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort(); fs.writeFileSync(path.join(out, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(names.map((name) => [name, { sha256: hashFile(path.join(out, name)), bytes: fs.statSync(path.join(out, name)).size }])) }));
  process.stdout.write(canonical(census));
}
main();
