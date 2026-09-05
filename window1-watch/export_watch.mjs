#!/usr/bin/env node
// export_watch.mjs v2 — Window-1 Watch exporter. Trace + tape in, face data out. Invents nothing.
//
// node window1-watch/export_watch.mjs --event KXATPMATCH-26JUL12ALTGAS \
//   --trace "C:\tmp\v54_altgas_extra_2dfb5b0a_20260902_run2_custody\REPAIR_FOUR_GAME_TRACE.jsonl.gz" \
//   --tape-dir "<dir holding KXATPMATCH-26JUL12ALTGAS-ALT.csv.gz and -GAS.csv.gz>"   (optional on the first pass) \
//   --out window1-watch/data/altgas.json
//
// Schema learned from the c2fe78f2 trace (pair-level rows):
//   row.kind ("DECISION_STAGE" | ...), row.trigger, row.receipt, row.timestamp_epoch, row.hours_from_discovery,
//   row.reads.<reader>.value  (books, lows_travel, drift, shape_survival, half_pair_state, time_in_window, ...),
//   row.layers.{macro,micro,micro_micro}.context  (status, beliefs, survivor_shapes, families),
//   row.coherence, row.derivations[ per leg ], row.credited_leg_streams
// Everything below is copied from those objects as stored. Missing => {"stamp":"STORE SILENT"}.

import fs from "node:fs";
import zlib from "node:zlib";
import crypto from "node:crypto";
import readline from "node:readline";
import path from "node:path";

const args = Object.fromEntries(process.argv.slice(2).reduce((acc, a, i, arr) => {
  if (a.startsWith("--")) acc.push([a.slice(2), arr[i + 1] && !arr[i + 1].startsWith("--") ? arr[i + 1] : true]);
  return acc;
}, []));
const EVENT = args.event, TRACE = args.trace, TAPE_DIR = args["tape-dir"] || null;
const MANIFEST_ONLY = args["manifest-only"] === true;
const OUT = args.out || `window1-watch/data/${(EVENT || "event").split("-").pop().toLowerCase()}.json`;
if (!EVENT || !TRACE) { console.error("need --event <event_id> --trace <REPAIR_FOUR_GAME_TRACE.jsonl.gz> [--tape-dir <dir>]"); process.exit(2); }

const SILENT = (looked) => ({ stamp: "STORE SILENT", looked });
const get = (o, p) => p.split(".").reduce((c, k) => (c != null && typeof c === "object" && k in c ? c[k] : undefined), o);
const has = (v) => v !== undefined && v !== null;
const pick = (o, p) => (has(get(o, p)) ? get(o, p) : SILENT([p]));
function keyTree(obj, depth = 0, max = 4, prefix = "", out = []) {
  if (obj == null || typeof obj !== "object" || depth > max) return out;
  const entries = Array.isArray(obj) ? obj.slice(0, 2).map((v, i) => [String(i), v]) : Object.entries(obj).slice(0, 80);
  for (const [k, v] of entries) {
    const p = prefix ? `${prefix}.${k}` : k;
    if (v !== null && typeof v === "object") { out.push(p + (Array.isArray(v) ? `[${v.length}]` : "{}")); keyTree(v, depth + 1, max, p, out); }
    else out.push(`${p}=${JSON.stringify(v)?.slice(0, 60)}`);
  }
  return out;
}
async function sha256File(file) {
  const hash = crypto.createHash("sha256");
  for await (const chunk of fs.createReadStream(file)) hash.update(chunk);
  return hash.digest("hex");
}

// ---------- stream the trace ----------
async function* lines(file) {
  const raw = fs.createReadStream(file);
  const src = file.endsWith(".gz") ? raw.pipe(zlib.createGunzip()) : raw;
  for await (const line of readline.createInterface({ input: src, crlfDelay: Infinity })) if (line.trim()) yield line;
}

const kinds = {};
const stages = [];
const others = [];        // non-DECISION_STAGE rows for this event (fills, rearm attempts, floor-print instants, ...)
let firstStage = null, firstOther = {};
let total = 0, matched = 0;
for await (const line of lines(TRACE)) {
  total += 1;
  let row; try { row = JSON.parse(line); } catch (error) { if (MANIFEST_ONLY) throw error; continue; }
  const ev = row.event_id ?? get(row, "state.event_id");
  if (ev !== EVENT) continue;
  matched += 1;
  const kind = String(row.kind ?? row.row_type ?? row.event_type ?? "UNKNOWN");
  kinds[kind] = (kinds[kind] ?? 0) + 1;

  if (kind === "DECISION_STAGE") {
    if (!firstStage) firstStage = row;
    const legs = Object.keys(get(row, "reads.books.value") ?? get(row, "reads.drift.value") ?? {});
    if (MANIFEST_ONLY) { if (!stages.length) stages.push({ legs }); continue; }
    stages.push({
      kind, trigger: row.trigger ?? null, receipt: row.receipt ?? null,
      timestamp_epoch: row.timestamp_epoch ?? null, hours_from_discovery: row.hours_from_discovery ?? null,
      hours_to_truth_bell: pick(row, "reads.time_in_window.value.hours_to_truth_bell"),
      books: pick(row, "reads.books.value"),                       // per leg, as stored (bid/ask/last subkeys copied verbatim)
      lows_travel: pick(row, "reads.lows_travel.value"),           // per leg running low / travel as stored
      drift: pick(row, "reads.drift.value"),
      shape_survival: pick(row, "reads.shape_survival.value"),     // per leg survivor count / steps as stored
      half_pair_state: pick(row, "reads.half_pair_state.value"),   // standing / credited rests as stored
      macro: { status: pick(row, "layers.macro.context.status"), survivor_shapes: pick(row, "layers.macro.context.survivor_shapes"), families: pick(row, "layers.macro.context.families") },
      micro: { status: pick(row, "layers.micro.context.status"), beliefs: pick(row, "layers.micro.context.beliefs") },   // the sentence per leg, as stored
      micro_micro: { status: pick(row, "layers.micro_micro.context.status") },
      coherence: has(row.coherence) ? row.coherence : SILENT(["coherence"]),
      derivations: Array.isArray(row.derivations) ? row.derivations : SILENT(["derivations"]),  // per-leg action/target/winner, as stored
      credited_leg_streams: has(row.credited_leg_streams) ? row.credited_leg_streams : SILENT(["credited_leg_streams"]),
      legs,
    });
  } else {
    if (!firstOther[kind]) firstOther[kind] = row;
    if (!MANIFEST_ONLY) others.push(row);   // manifest mode is an index; builder streams the full source itself
  }
}
if (matched === 0) { console.error(`No rows for ${EVENT} in ${TRACE} (${total} lines).`); process.exit(3); }

// ---------- tape (optional): the two custody CSVs named in the receipts ----------
let tape = SILENT([`${TAPE_DIR ?? "<--tape-dir>"}/${EVENT}-<LEG>.csv.gz`]);
if (TAPE_DIR) {
  tape = {};
  const legs = firstStage ? Object.keys(get(firstStage, "reads.books.value") ?? {}) : [];
  for (const leg of legs) {
    const f = path.join(TAPE_DIR, `${EVENT}-${leg}.csv.gz`);
    if (!fs.existsSync(f)) { tape[leg] = SILENT([f]); continue; }
    const text = zlib.gunzipSync(fs.readFileSync(f)).toString("utf8").split(/\r?\n/).filter(Boolean);
    const header = text[0].split(",");
    tape[leg] = { file: f, sha256: await sha256File(f), header, rows: text.length - 1, sample: text.slice(1, 4) };
  }
}

const out = {
  provenance: { event_id: EVENT, trace_path: TRACE, trace_sha256: await sha256File(TRACE), trace_lines: total, rows_for_event: matched, kinds, exported_at: new Date().toISOString(), exporter: "export_watch.mjs v2", manifest_only: MANIFEST_ONLY },
  legs: stages[0]?.legs ?? [],
  bell: firstStage ? { hours_to_truth_bell_at_first_stage: get(firstStage, "reads.time_in_window.value.hours_to_truth_bell"), bell_source: get(firstStage, "reads.time_in_window.value.bell_source"), first_stage_epoch: firstStage.timestamp_epoch } : SILENT(["reads.time_in_window"]),
  stages,
  others,
  tape,
  schema_report: {
    first_stage_subtrees: {
      books: keyTree(get(firstStage, "reads.books.value"), 0, 3),
      lows_travel: keyTree(get(firstStage, "reads.lows_travel.value"), 0, 3),
      shape_survival: keyTree(get(firstStage, "reads.shape_survival.value"), 0, 3),
      half_pair_state: keyTree(get(firstStage, "reads.half_pair_state.value"), 0, 3),
      micro_beliefs: keyTree(get(firstStage, "layers.micro.context.beliefs"), 0, 3),
      macro_survivor_shapes: keyTree(get(firstStage, "layers.macro.context.survivor_shapes"), 0, 3),
      derivation0: keyTree(Array.isArray(firstStage?.derivations) ? firstStage.derivations[0] : null, 0, 2),
    },
    // a later stage with a resolved sentence, if any, so the belief subkeys show real values
    resolved_stage_micro_beliefs: keyTree(get(stages.find((s) => get(s, "micro.status") === "RESOLVED") ?? {}, "micro.beliefs"), 0, 3),
    other_kinds_first_row: Object.fromEntries(Object.entries(firstOther).map(([k, r]) => [k, keyTree(r, 0, 3)])),
  },
};
fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.writeFileSync(OUT, JSON.stringify(out, null, 1));

console.log(`wrote ${OUT}`);
console.log(`trace sha256 ${out.provenance.trace_sha256}  rows for ${EVENT}: ${matched} of ${total}  kinds: ${JSON.stringify(kinds)}  legs: ${out.legs.join(",")}`);
console.log(`bell: ${JSON.stringify(out.bell)}`);
console.log("SCHEMA REPORT — subkeys as stored on the first stage:");
for (const [k, v] of Object.entries(out.schema_report.first_stage_subtrees)) console.log(`\n[${k}]\n  ${v.join("\n  ")}`);
console.log(`\n[resolved stage micro.beliefs]\n  ${out.schema_report.resolved_stage_micro_beliefs.join("\n  ") || "(no RESOLVED stage)"}`);
for (const [k, v] of Object.entries(out.schema_report.other_kinds_first_row)) console.log(`\n[first ${k} row]\n  ${v.join("\n  ")}`);
console.log(`\ntape: ${TAPE_DIR ? JSON.stringify(Object.fromEntries(Object.entries(tape).map(([l, t]) => [l, t.header ? { rows: t.rows, header: t.header, sample: t.sample } : t]))) : "not requested (pass --tape-dir)"}`);
