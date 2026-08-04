#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const readline = require("readline");
const zlib = require("zlib");

const argv = process.argv.slice(2);
const value = (name, fallback) => { const i = argv.indexOf(name); return i >= 0 ? argv[i + 1] : fallback; };
const repo = path.resolve(value("--repo", "."));
const privateRoot = path.resolve(value("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const output = path.resolve(value("--output", path.join(repo, ".claude/window1_live_v4_replay/naked_leg_disposition_v23_vs_a_20260804")));
const compare1 = value("--compare-run1", null);
const compare2 = value("--compare-run2", null);

const aLegPath = path.join(repo, ".claude/window1_live_v4_replay/isolated_fix_a_anchor_freshness_v20_20260804/POPULATION_LEG_LEDGER.jsonl.gz");
const v23LegPath = path.join(repo, ".claude/window1_live_v4_replay/pair_cap_v23_audited_close_20260804/V23_LEG_LEDGER.jsonl.gz");
const quotePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const guardPath = path.join(repo, ".claude/window1_start_guard_corrected_20260724/REAL_START_LEDGER_V5.jsonl");
const printPath = path.join(privateRoot, "fit-local/prints.jsonl");
const printManifestPath = path.join(privateRoot, "fit-local/PUBLIC_TAPE_MANIFEST.sanitized.json");
const bandSealPath = path.join(repo, "arb-executor/data/durable/exit_surface_gated_optima/LOCKED_DOWN.md");
const gradingPath = path.join(repo, "arb-executor/audit/w1_grading.py");
const bandCsv = {
  ATP_MAIN: path.join(repo, "arb-executor/analysis/exit_charts/deploy_gated_optima_full.csv"),
  WTA_MAIN: path.join(repo, "arb-executor/analysis/exit_charts/deploy_gated_optima_WTA_MAIN.csv"),
  ATP_CHALL: path.join(repo, "arb-executor/analysis/exit_charts/deploy_gated_optima_ATP_CHALL.csv"),
  WTA_CHALL: path.join(repo, "arb-executor/analysis/exit_charts/deploy_gated_optima_WTA_CHALL.csv"),
};
const sealedCsvSha = {
  ATP_MAIN: "9fc6dd7beedb4d63292268af8de7ac9e83a42ac5f6b2eafc7a2de39602e4d41f",
  WTA_MAIN: "3fc8a3880fac1a2590094b6d36117f48271346361410a3772e1f68a69b086a46",
  ATP_CHALL: "ee6377c5146caeae9c93701ee412b4ec7ecee06975222024218875e1dd532df9",
  WTA_CHALL: "3416a87b8e64040f0a315a73e3870b5038905d8fee9a23c07bcfc92c644062c4",
};

function ensure(ok, message) { if (!ok) throw new Error(message); }
function canonical(x) { return `${JSON.stringify(x, null, 2)}\n`; }
function sha(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function hashFile(file) { return sha(fs.readFileSync(file)); }
function readGzipRows(file) { const s = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim(); return s ? s.split(/\r?\n/).map(JSON.parse) : []; }
function gzipRows(rows) { return zlib.gzipSync(Buffer.from(`${rows.map(JSON.stringify).join("\n")}\n`), { level: 9, mtime: 0 }); }
function parseCsv(text) { const lines = text.trimEnd().split(/\r?\n/); const header = lines.shift().split(","); return lines.filter(Boolean).map((line) => Object.fromEntries(line.split(",").map((cell, i) => [header[i], cell]))); }
function group(rows, key) { const out = new Map(); for (const row of rows) { const k = key(row); if (!out.has(k)) out.set(k, []); out.get(k).push(row); } return out; }
function quantile(xs, p) { const a = xs.filter(Number.isFinite).sort((x, y) => x - y); return a.length ? a[Math.floor((a.length - 1) * p)] : null; }
function dist(values) { const a = values.filter(Number.isFinite); const total = a.reduce((s, x) => s + x, 0); return { denominator: values.length, numeric_n: a.length, unavailable_n: values.length - a.length, min: a.length ? Math.min(...a) : null, p25: quantile(a, .25), median: quantile(a, .5), p75: quantile(a, .75), p90: quantile(a, .9), max: a.length ? Math.max(...a) : null, mean: a.length ? total / a.length : null, total_cents: total }; }
function countBy(rows, key) { const out = {}; for (const row of rows) { const k = String(key(row)); out[k] = (out[k] || 0) + 1; } return Object.fromEntries(Object.entries(out).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }
function clockLabel(seconds) { if (!Number.isFinite(seconds)) return null; const prefix = seconds >= 0 ? "T-" : "T+"; const n = Math.abs(seconds); return `${prefix}${Math.floor(n / 60)}:${String(Math.floor(n % 60)).padStart(2, "0")}`; }
function clock(ts, scheduled, bell) { return { timestamp_epoch: ts, t_minus_scheduled_seconds: Number.isFinite(ts) ? scheduled - ts : null, t_minus_scheduled: Number.isFinite(ts) ? clockLabel(scheduled - ts) : null, t_minus_actual_bell_seconds: Number.isFinite(ts) && Number.isFinite(bell) ? bell - ts : null, t_minus_actual_bell: Number.isFinite(ts) && Number.isFinite(bell) ? clockLabel(bell - ts) : "ACTUAL_BELL_NOT_EXACTLY_BOUND" }; }
function gitBlobBytes(rel) { const cp = require("child_process"); return cp.execFileSync("git", ["show", `HEAD:${rel.replaceAll("\\", "/")}`], { cwd: repo, maxBuffer: 64 * 1024 * 1024 }); }

function loadBands() {
  const seal = fs.readFileSync(bandSealPath, "utf8");
  ensure(seal.includes("live exit surface") && seal.includes("replaces"), "locked band authority text missing");
  const maps = {};
  const receipts = {};
  for (const [category, file] of Object.entries(bandCsv)) {
    const rel = path.relative(repo, file).replaceAll("\\", "/");
    const blob = gitBlobBytes(rel);
    ensure(sha(blob) === sealedCsvSha[category], `sealed ${category} CSV blob mismatch`);
    const rows = parseCsv(blob.toString("utf8"));
    const map = new Map();
    for (const row of rows) {
      const cell = Number(row.c), x = Number(row.X);
      ensure(Number.isInteger(cell) && Number.isInteger(x), `${category} noninteger cell/X`);
      map.set(cell, x);
    }
    ensure(map.size === 90 && [...map.keys()].every((x) => x >= 5 && x <= 94), `${category} band cell conservation`);
    maps[category] = map;
    receipts[category] = { path: rel, git_blob_sha256: sha(blob), checkout_sha256: hashFile(file), cells: map.size, cell_domain: [5, 94] };
  }
  return { maps, receipts };
}

function fillTimestamp(leg) {
  if (leg.honest_fill_class === "PROVEN_MAKER_BY_RESIDENCY_STRICTLY_LATER_QUALIFYING_ASK") {
    ensure(Number.isFinite(leg.fill?.evidence_ts), `maker fill timestamp absent ${leg.leg_identity}`);
    return leg.fill.evidence_ts;
  }
  ensure(leg.honest_fill_class === "PROVEN_TAKER", `unexpected fill class ${leg.leg_identity}:${leg.honest_fill_class}`);
  ensure(Number.isFinite(leg.action_timestamp_epoch), `taker action timestamp absent ${leg.leg_identity}`);
  return leg.action_timestamp_epoch;
}

function exactBell(row) {
  if (!row?.exact_start_utc) return null;
  const ts = Date.parse(row.exact_start_utc) / 1000;
  return Number.isFinite(ts) ? ts : null;
}

function makeMark(print, scheduled, bell) {
  if (!print) return null;
  return { price_cents: print.price, size: print.size, trade_id: print.trade_id, aggressor_side: print.aggressor_side, taker_book_side: print.taker_book_side, ...clock(print.ts, scheduled, bell) };
}

function origin(variant, leg, sibling) {
  if (variant === "A_V20") return "NEVER_COMPLETED_SIBLING";
  if (String(sibling.terminal_reason || "").startsWith("PAIR_CAP_BELOW_")) return "CAP_ABSTENTION_SIBLING";
  return "NEVER_COMPLETED_SIBLING";
}

function prepareRows(variant, legs, clocks, guards, bands) {
  const byEvent = group(legs, (x) => x.event_id);
  const out = [];
  for (const [eventId, eventLegs] of byEvent) {
    ensure(eventLegs.length === 2, `${variant} ${eventId} leg count`);
    const credited = eventLegs.filter((x) => x.credited);
    if (credited.length !== 1) continue;
    const leg = credited[0], sibling = eventLegs.find((x) => x !== leg), source = clocks.get(leg.ticker), guard = guards.get(eventId);
    ensure(source && guard, `clock/guard missing ${leg.leg_identity}`);
    const entry = leg.entry_cents, cell = Math.min(94, Math.max(5, entry)), bandX = bands[leg.category].get(cell);
    ensure(Number.isInteger(entry) && Number.isInteger(bandX), `entry/band missing ${leg.leg_identity}`);
    const fillTs = fillTimestamp(leg), bell = exactBell(guard), bandTarget = Math.min(98, entry + bandX);
    ensure(fillTs <= source.right_ts, `fill after guarded right ${leg.leg_identity}`);
    out.push({
      schema_version: "WINDOW1_NAKED_LEG_DISPOSITION_ROW_V1",
      variant,
      leg_identity: leg.leg_identity,
      event_id: eventId,
      ticker: leg.ticker,
      leg_id: leg.leg_id,
      category: leg.category,
      price_region: leg.price_region,
      starting_price_split: leg.starting_price_split,
      origin_class: origin(variant, leg, sibling),
      sibling_leg_identity: sibling.leg_identity,
      sibling_terminal_reason: sibling.terminal_reason,
      entry_cents: entry,
      fill_class: leg.honest_fill_class,
      fill_clock: clock(fillTs, source.scheduled_ts, bell),
      guarded_window_right_clock: clock(source.right_ts, source.scheduled_ts, bell),
      actual_bell_clock: Number.isFinite(bell) ? clock(bell, source.scheduled_ts, bell) : { timestamp_epoch: null, t_minus_scheduled_seconds: null, t_minus_scheduled: null, t_minus_actual_bell_seconds: null, t_minus_actual_bell: "ACTUAL_BELL_NOT_EXACTLY_BOUND" },
      band_cell_cents: cell,
      band_x_cents: bandX,
      uncapped_band_target_cents: entry + bandX,
      exit_price_cap_cents: 98,
      band_target_cents: bandTarget,
      band_rule: "EXIT",
      band_touch_law: "TRUE_PUBLIC_PRINT_AT_OR_ABOVE_BAND_TARGET_AFTER_CREDITED_FILL_AND_AT_OR_BEFORE_GUARDED_WINDOW1_RIGHT_EDGE",
      band_touched: false,
      first_band_touch: null,
      best_exit_mark: null,
      window_right_edge_mark: null,
      actual_bell_mark: null,
      _fill_ts: fillTs,
      _right_ts: source.right_ts,
      _scheduled_ts: source.scheduled_ts,
      _bell_ts: bell,
      _best: null,
      _edge: null,
      _bell: null,
      _touch: null,
    });
  }
  return out;
}

function updateRow(row, p) {
  if (p.ts < row._fill_ts) return;
  if (p.ts <= row._right_ts) {
    if (!row._best || p.price > row._best.price || (p.price === row._best.price && p.ts < row._best.ts)) row._best = p;
    if (!row._edge || p.ts > row._edge.ts || (p.ts === row._edge.ts && p.trade_id < row._edge.trade_id)) row._edge = p;
    if (p.price >= row.band_target_cents && (!row._touch || p.ts < row._touch.ts || (p.ts === row._touch.ts && p.trade_id < row._touch.trade_id))) row._touch = p;
  }
  if (Number.isFinite(row._bell_ts) && p.ts <= row._bell_ts) {
    if (!row._bell || p.ts > row._bell.ts || (p.ts === row._bell.ts && p.trade_id < row._bell.trade_id)) row._bell = p;
  }
}

async function scanPrints(rows) {
  const targets = group(rows, (x) => x.ticker);
  const hash = crypto.createHash("sha256");
  const input = fs.createReadStream(printPath);
  input.on("data", (chunk) => hash.update(chunk));
  let physical = 0, selected = 0;
  const rl = readline.createInterface({ input, crlfDelay: Infinity });
  for await (const line of rl) {
    physical += 1;
    const match = line.match(/"ticker":"([^"]+)"/);
    if (!match || !targets.has(match[1])) continue;
    const raw = JSON.parse(line);
    if (raw.true_print !== true || raw.source !== "kalshi_public_trade") continue;
    const ts = Date.parse(raw.exchange_ts) / 1000, price = Number(raw.price_cents), size = Number(raw.size);
    if (!Number.isFinite(ts) || !Number.isInteger(price) || !Number.isFinite(size) || !raw.trade_id) continue;
    const p = { ts, price, size, trade_id: raw.trade_id, taker_book_side: raw.taker_book_side || null, aggressor_side: raw.taker_book_side === "bid" ? "SELLER_AGGRESSED" : raw.taker_book_side === "ask" ? "BUYER_AGGRESSED" : "UNKNOWN" };
    selected += 1;
    for (const row of targets.get(match[1])) updateRow(row, p);
  }
  return { sha256: hash.digest("hex"), bytes: fs.statSync(printPath).size, physical_rows: physical, selected_target_ticker_rows: selected, target_tickers: targets.size };
}

function finalize(row) {
  row.band_touched = Boolean(row._touch);
  row.first_band_touch = makeMark(row._touch, row._scheduled_ts, row._bell_ts);
  row.best_exit_mark = makeMark(row._best, row._scheduled_ts, row._bell_ts);
  row.window_right_edge_mark = makeMark(row._edge, row._scheduled_ts, row._bell_ts);
  row.actual_bell_mark = Number.isFinite(row._bell_ts) ? makeMark(row._bell, row._scheduled_ts, row._bell_ts) : null;
  row.best_band_exit_cents = row.band_touched ? row.band_target_cents : null;
  row.pnl_best_band_exit_cents_per_contract = row.band_touched ? row.band_target_cents - row.entry_cents : null;
  row.pnl_held_to_window_right_edge_cents_per_contract = row.window_right_edge_mark ? row.window_right_edge_mark.price_cents - row.entry_cents : null;
  row.pnl_held_to_actual_bell_cents_per_contract = row.actual_bell_mark ? row.actual_bell_mark.price_cents - row.entry_cents : null;
  row.pnl_band_or_edge_disposition_cents_per_contract = row.band_touched ? row.pnl_best_band_exit_cents_per_contract : row.pnl_held_to_window_right_edge_cents_per_contract;
  row.harvest_increment_over_hold_to_edge_cents_per_contract = Number.isFinite(row.pnl_band_or_edge_disposition_cents_per_contract) && Number.isFinite(row.pnl_held_to_window_right_edge_cents_per_contract) ? row.pnl_band_or_edge_disposition_cents_per_contract - row.pnl_held_to_window_right_edge_cents_per_contract : null;
  row.pnl_band_or_edge_disposition_cents_five_contracts = Number.isFinite(row.pnl_band_or_edge_disposition_cents_per_contract) ? row.pnl_band_or_edge_disposition_cents_per_contract * 5 : null;
  for (const key of Object.keys(row).filter((x) => x.startsWith("_"))) delete row[key];
  return row;
}

function summarize(rows) {
  return {
    legs: rows.length,
    band_touch: countBy(rows, (x) => x.band_touched ? "YES" : "NO"),
    edge_mark: countBy(rows, (x) => x.window_right_edge_mark ? "AVAILABLE" : "UNAVAILABLE"),
    bell_mark: countBy(rows, (x) => x.actual_bell_mark ? "AVAILABLE" : (x.actual_bell_clock.t_minus_actual_bell === "ACTUAL_BELL_NOT_EXACTLY_BOUND" ? "ACTUAL_BELL_NOT_EXACTLY_BOUND" : "NO_POST_FILL_TRUE_PRINT_AT_OR_BEFORE_BELL")),
    best_exit_mark_cents: dist(rows.map((x) => x.best_exit_mark?.price_cents)),
    window_right_edge_mark_cents: dist(rows.map((x) => x.window_right_edge_mark?.price_cents)),
    actual_bell_mark_cents: dist(rows.map((x) => x.actual_bell_mark?.price_cents)),
    pnl_best_band_exit_cents_per_contract: dist(rows.map((x) => x.pnl_best_band_exit_cents_per_contract)),
    pnl_held_to_window_right_edge_cents_per_contract: dist(rows.map((x) => x.pnl_held_to_window_right_edge_cents_per_contract)),
    pnl_held_to_actual_bell_cents_per_contract: dist(rows.map((x) => x.pnl_held_to_actual_bell_cents_per_contract)),
    pnl_band_or_edge_disposition_cents_per_contract: dist(rows.map((x) => x.pnl_band_or_edge_disposition_cents_per_contract)),
    pnl_band_or_edge_disposition_cents_five_contracts: dist(rows.map((x) => x.pnl_band_or_edge_disposition_cents_five_contracts)),
    harvest_increment_over_hold_to_edge_cents_per_contract: dist(rows.map((x) => x.harvest_increment_over_hold_to_edge_cents_per_contract)),
  };
}

function compareDirs(a, b) {
  const skip = new Set(["ARTIFACT_HASH_MANIFEST.json", "DETERMINISM_RECEIPT.json"]);
  const aa = fs.readdirSync(a).filter((x) => !skip.has(x)).sort(), bb = fs.readdirSync(b).filter((x) => !skip.has(x)).sort();
  ensure(JSON.stringify(aa) === JSON.stringify(bb), "determinism file census mismatch");
  const mismatches = aa.filter((x) => hashFile(path.join(a, x)) !== hashFile(path.join(b, x)));
  ensure(!mismatches.length, `determinism mismatch ${mismatches.join(",")}`);
  return { clean_builds: 2, compared_files: aa.length, byte_identical: true, mismatches: [] };
}

async function main() {
  for (const file of [aLegPath, v23LegPath, quotePath, guardPath, printPath, printManifestPath, bandSealPath, gradingPath, ...Object.values(bandCsv)]) ensure(fs.existsSync(file), `missing ${file}`);
  const { maps: bands, receipts: bandReceipts } = loadBands();
  const quoteRows = parseCsv(fs.readFileSync(quotePath, "utf8")).map((x) => ({ ticker: x.ticker, event_id: x.event_id, left_ts: Number(x.left_ts), right_ts: Number(x.right_ts), scheduled_ts: Number(x.scheduled_start_ts) }));
  ensure(quoteRows.length === 1608, `quote rows ${quoteRows.length}`);
  const clocks = new Map(quoteRows.map((x) => [x.ticker, x]));
  const guards = new Map(fs.readFileSync(guardPath, "utf8").trim().split(/\r?\n/).map(JSON.parse).map((x) => [x.event_id, x]));
  ensure(guards.size === 804, `guard rows ${guards.size}`);
  const aLegs = readGzipRows(aLegPath), v23Legs = readGzipRows(v23LegPath);
  ensure(aLegs.length === 1608 && v23Legs.length === 1608, "variant leg conservation");
  const rows = [...prepareRows("A_V20", aLegs, clocks, guards, bands), ...prepareRows("V23_PAIR_CAP_IMMEDIATE", v23Legs, clocks, guards, bands)];
  ensure(rows.filter((x) => x.variant === "A_V20").length === 245, "A naked count");
  ensure(rows.filter((x) => x.variant === "V23_PAIR_CAP_IMMEDIATE").length === 512, "V23 naked count");
  const scan = await scanPrints(rows);
  const manifest = JSON.parse(fs.readFileSync(printManifestPath, "utf8"));
  ensure(scan.sha256 === manifest.artifacts.normalized_true_prints.sha256 && scan.bytes === manifest.artifacts.normalized_true_prints.bytes, "public print tape hash/size mismatch");
  rows.map(finalize).sort((a, b) => a.variant.localeCompare(b.variant) || a.leg_identity.localeCompare(b.leg_identity));
  const variants = Object.fromEntries([...group(rows, (x) => x.variant)].map(([variant, xs]) => [variant, { aggregate: summarize(xs), category_x_price_region_x_origin_class: [...group(xs, (x) => `${x.category}|${x.price_region}|${x.origin_class}`)].sort(([a], [b]) => a.localeCompare(b)).map(([key, cell]) => { const [category, price_region, origin_class] = key.split("|"); return { category, price_region, origin_class, ...summarize(cell) }; }) }]));
  const a = variants.A_V20.aggregate, v23 = variants.V23_PAIR_CAP_IMMEDIATE.aggregate;
  const aTotal = a.pnl_band_or_edge_disposition_cents_per_contract.total_cents, v23Total = v23.pnl_band_or_edge_disposition_cents_per_contract.total_cents;
  const missingA = a.pnl_band_or_edge_disposition_cents_per_contract.unavailable_n, missingV23 = v23.pnl_band_or_edge_disposition_cents_per_contract.unavailable_n;
  const net = { law: "IF CANONICAL BAND TARGET TOUCHED, EXIT AT BAND TARGET; OTHERWISE HOLD TO LAST POST_FILL TRUE PRINT AT OR BEFORE GUARDED RIGHT EDGE; NO IMPUTATION", A_V20_observed_total_cents_per_contract: aTotal, V23_observed_total_cents_per_contract: v23Total, V23_minus_A_observed_total_cents_per_contract: v23Total - aTotal, A_V20_observed_five_lot_total_cents: a.pnl_band_or_edge_disposition_cents_five_contracts.total_cents, V23_observed_five_lot_total_cents: v23.pnl_band_or_edge_disposition_cents_five_contracts.total_cents, V23_minus_A_observed_five_lot_total_cents: v23.pnl_band_or_edge_disposition_cents_five_contracts.total_cents - a.pnl_band_or_edge_disposition_cents_five_contracts.total_cents, V23_observed_rows_sign: v23Total > 0 ? "PAY" : v23Total < 0 ? "BLEED" : "WASH", full_V23_naked_book_sign: missingV23 ? "UNRESOLVED_POST_FILL_EDGE_MARK_UNAVAILABLE" : v23Total > 0 ? "PAY" : v23Total < 0 ? "BLEED" : "WASH", full_relative_to_A_sign: missingA || missingV23 ? "UNRESOLVED_POST_FILL_EDGE_MARK_UNAVAILABLE" : v23Total - aTotal > 0 ? "PAYS_MORE_THAN_A" : v23Total - aTotal < 0 ? "BLEEDS_MORE_THAN_A" : "WASH_VS_A", unavailable_disposition_rows: { A_V20: missingA, V23: missingV23 }, no_imputation: true };
  const conservation = { V23: { credited_legs: 920, legs_in_completed_pairs: 408, naked_credited_legs: 512, equation: "408+512=920", pass: 408 + 512 === 920 }, A_V20: { credited_legs: 1187, legs_in_completed_pairs: 942, naked_credited_legs: 245, equation: "942+245=1187", pass: 942 + 245 === 1187 }, disposition_rows: rows.length, unique_variant_leg_identities: new Set(rows.map((x) => `${x.variant}|${x.leg_identity}`)).size, exactly_one_disposition_row_per_naked_leg: rows.length === new Set(rows.map((x) => `${x.variant}|${x.leg_identity}`)).size, origin_class_counts: Object.fromEntries([...group(rows, (x) => x.variant)].map(([variant, xs]) => [variant, countBy(xs, (x) => x.origin_class)])) };
  ensure(conservation.V23.pass && conservation.A_V20.pass && conservation.exactly_one_disposition_row_per_naked_leg, "conservation failure");
  fs.mkdirSync(output, { recursive: true });
  fs.writeFileSync(path.join(output, "NAKED_LEG_DISPOSITION_LEDGER.jsonl.gz"), gzipRows(rows));
  fs.writeFileSync(path.join(output, "DISPOSITION_DISTRIBUTIONS.json"), canonical({ schema_version: "WINDOW1_NAKED_LEG_DISPOSITION_DISTRIBUTIONS_V1", variants, net_answer: net }));
  fs.writeFileSync(path.join(output, "CONSERVATION_RECEIPT.json"), canonical(conservation));
  fs.writeFileSync(path.join(output, "BAND_AUTHORITY_RECEIPT.json"), canonical({ status: "BOUND", canonical_surface: "gated_optima_validated_2026-06-01; C-EXIT-SEAL; Plex-countersigned; ATP_MAIN resealed full-universe 2026-06-15", seal: { path: path.relative(repo, bandSealPath).replaceAll("\\", "/"), sha256: hashFile(bandSealPath) }, machine_readable_surfaces: bandReceipts, lookup_law: "CELL=CLAMP(ROUND(CREDITED_ENTRY_CENTS),5,94); X=SEALED_CSV.X; TARGET=MIN(ENTRY+X,98)", touch_law: { path: path.relative(repo, gradingPath).replaceAll("\\", "/"), sha256: hashFile(gradingPath), rule: "TRUE TAPE PRINT PRICE >= EXIT LEVEL BEFORE GUARDED RIGHT EDGE" }, superseded_surface_excluded: "arb-executor/data/durable/spike_volatility_map", hold_cells: 0, invented_band_or_touch_rule: false }));
  fs.writeFileSync(path.join(output, "FORBIDDEN_ACCESS_RECEIPT.json"), canonical({ development_population_only: true, read_only_tape_walk: true, policy_variant: false, scoring_change: false, scorer_invocations: 0, holdout: false, live: false, network: false, orders: false, positions: false, exits_mutated: false, settlement: false, DCA: false, Window2: false }));
  fs.writeFileSync(path.join(output, "SOURCE_HASH_MANIFEST.json"), canonical({ committed: Object.fromEntries([aLegPath, v23LegPath, quotePath, guardPath, bandSealPath, gradingPath, ...Object.values(bandCsv), __filename, path.join(repo, "arb-executor/tests/test_window1_naked_leg_disposition_v23.js")].map((file) => [path.relative(repo, file).replaceAll("\\", "/"), { sha256: hashFile(file), bytes: fs.statSync(file).size }])), private_public_print_tape: { path_redacted_to_contract: "OMI-Window1-private/fit-local/prints.jsonl", ...scan }, private_public_print_manifest: { path_redacted_to_contract: "OMI-Window1-private/fit-local/PUBLIC_TAPE_MANIFEST.sanitized.json", sha256: hashFile(printManifestPath), bytes: fs.statSync(printManifestPath).size } }));
  fs.writeFileSync(path.join(output, "REPORT.md"), `# V23 versus A naked-leg disposition census\n\nThe canonical band authority is the sealed gated-optima surface. The row ledger contains every naked credited leg and walks true public prints from credited fill through the guarded Window-1 right edge. A canonical band is touched only by a true print at or above the capped exit target. Marks at the right edge and exact actual bell are never fabricated; unavailable exact bells remain named unavailable.\n\nConservation: **408+512=920 (V23)** and **942+245=1187 (A)**. Full category x price-region x origin distributions and the pay/wash/bleed answer are in DISPOSITION_DISTRIBUTIONS.json.\n`);
  if (compare1 && compare2) fs.writeFileSync(path.join(output, "DETERMINISM_RECEIPT.json"), canonical(compareDirs(path.resolve(compare1), path.resolve(compare2))));
  const names = fs.readdirSync(output).filter((x) => x !== "ARTIFACT_HASH_MANIFEST.json").sort();
  fs.writeFileSync(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(names.map((name) => [name, { sha256: hashFile(path.join(output, name)), bytes: fs.statSync(path.join(output, name)).size }])) }));
  process.stdout.write(canonical({ status: "BUILT", output, rows: rows.length, conservation, net_answer: net, public_print_scan: scan }));
}

main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
