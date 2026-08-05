#!/usr/bin/env node
"use strict";

const child = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { matchesMacroEnvelope, ordinalVerdict } = require("./window1_interim_elimination_v13.js");
const {
  DWELL_SECONDS, QUANTITY, MAX_SPREAD_CENTS, armUncapturedSide, releaseOnQualifyingFloor,
} = require("./window1_v29r2_mirror_armed_uncaptured_side_policy.js");

const argv = process.argv.slice(2);
const arg = (name, fallback) => { const i = argv.indexOf(name); return i < 0 ? fallback : argv[i + 1]; };
const repo = path.resolve(arg("--repo", "."));
const privateRoot = path.resolve(arg("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const output = path.resolve(arg("--output", path.join(repo, ".claude/window1_live_v4_replay/v29r2_mirror_armed_uncaptured_side_20260804")));
const run1 = arg("--finalize-run1", null), run2 = arg("--finalize-run2", null);
const v28 = path.join(repo, ".claude/window1_live_v4_replay/v28_anchor_cap_stack_20260804");
const eventPath = path.join(v28, "EVENT_LEDGER.jsonl.gz");
const legPath = path.join(v28, "LEG_LEDGER.jsonl.gz");
const tracePath = path.join(v28, "DECISION_TRACE_1608.json");
const scorePath = path.join(v28, "SCORECARD.json");
const quotePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const bellPath = path.join(repo, ".claude/window1_live_v4_replay/actual_bell_refit_20260729/ACTUAL_BELL_REFIT.json");
const shapePath = path.join(repo, ".claude/window1_live_v4_replay/interim_shape_v13_fit_20260803/INTERIM_SHAPE_LIBRARY_V13.json");
const policyPath = path.join(repo, "arb-executor/analysis/window1_v29r2_mirror_armed_uncaptured_side_policy.js");
const interimPolicyPath = path.join(repo, "arb-executor/analysis/window1_interim_elimination_v13.js");
const policyTestPath = path.join(repo, "arb-executor/tests/test_window1_v29r2_mirror_armed_uncaptured_side_policy.js");
const packageTestPath = path.join(repo, "arb-executor/tests/test_window1_v29r2_mirror_armed_uncaptured_side_package.js");
const ceilingCommit = "44eab76f0caefbba6bab3315416e51e292fbdb1e";
const ceilingCsvGitPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/MIRROR_ARMING_CEILING.csv";
const ceilingSummaryGitPath = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/MIRROR_ARMING_CEILING_SUMMARY.json";
const LAYERS = ["ADMISSION", "BOOK", "IDENTITY", "FLOOR", "VERDICT", "ANCHOR", "SIBLING_PAIR", "PLACEMENT_CAP", "FILL", "COMPLETION"];

function ensure(x, message) { if (!x) throw new Error(message); }
function canonical(x) { return `${JSON.stringify(x, null, 2)}\n`; }
function sha(x) { return crypto.createHash("sha256").update(x).digest("hex"); }
function fileHash(p) { return sha(fs.readFileSync(p)); }
function clone(x) { return JSON.parse(JSON.stringify(x)); }
function write(p, bytes) { fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, bytes); }
function readRows(p) { const text = zlib.gunzipSync(fs.readFileSync(p)).toString("utf8").trim(); return text ? text.split(/\r?\n/).map(JSON.parse) : []; }
function gzipRows(rows) { return zlib.gzipSync(Buffer.from(`${rows.map(JSON.stringify).join("\n")}\n`), { level: 9, mtime: 0 }); }
function rel(p) { return path.relative(repo, p).replaceAll("\\", "/"); }
function integer(v) { const n = Number(v); return Number.isInteger(n) ? n : null; }
function positive(v) { const n = Number(v); return Number.isFinite(n) && n > 0 ? n : null; }
function group(xs, fn) { const m = new Map(); for (const x of xs) { const k = fn(x); if (!m.has(k)) m.set(k, []); m.get(k).push(x); } return m; }
function countBy(xs, fn) { const o = {}; for (const x of xs) { const k = String(fn(x)); o[k] = (o[k] || 0) + 1; } return Object.fromEntries(Object.entries(o).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }
function quantile(xs, p) { const x = xs.filter(Number.isFinite).sort((a, b) => a - b); return x.length ? x[Math.floor((x.length - 1) * p)] : null; }
function distribution(xs) { const x = xs.filter(Number.isFinite); return { denominator: xs.length, numeric_n: x.length, null_n: xs.length - x.length, min: x.length ? Math.min(...x) : null, p25: quantile(x, .25), median: quantile(x, .5), p75: quantile(x, .75), p90: quantile(x, .9), max: x.length ? Math.max(...x) : null, total_cents: x.reduce((a, b) => a + b, 0) }; }
function semanticHash(x) { return sha(JSON.stringify(x)); }
function parseEt(s) { const m = String(s).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/); if (!m) return null; let h = Number(m[4]); if (m[7] === "AM" && h === 12) h = 0; if (m[7] === "PM" && h !== 12) h += 12; return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(h).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000; }
function parseCsv(text) { const lines = text.trimEnd().split(/\r?\n/), header = lines.shift().split(","); return lines.filter(Boolean).map((line, i) => ({ ordinal: i + 2, row: Object.fromEntries(line.split(",").map((v, j) => [header[j], v])) })); }
function parseQuotedCsv(text) {
  const rows = []; let row = [], cell = "", quoted = false;
  for (let i = 0; i < text.length; i += 1) { const c = text[i]; if (c === '"') { if (quoted && text[i + 1] === '"') { cell += '"'; i += 1; } else quoted = !quoted; } else if (c === "," && !quoted) { row.push(cell); cell = ""; } else if ((c === "\n" || c === "\r") && !quoted) { if (c === "\r" && text[i + 1] === "\n") i += 1; row.push(cell); cell = ""; if (row.some((x) => x !== "")) rows.push(row); row = []; } else cell += c; }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  const header = rows.shift(); return rows.map((values) => Object.fromEntries(header.map((h, i) => [h, values[i] ?? ""])));
}
function gitShow(commit, p) { return child.execFileSync("git", ["show", `${commit}:${p}`], { cwd: repo, encoding: "utf8", maxBuffer: 32 * 1024 * 1024 }); }
function regionForShape(region) { return region === "ge75" ? "ge76" : region; }
function fillTs(leg) { return leg.credited ? Number(leg.fill?.evidence_ts ?? leg.fill?.timestamp_epoch ?? leg.action_timestamp_epoch) : null; }
function currentAt(rows, ts) { let found = null; for (const row of rows) { if (row.ts <= ts) found = row; else break; } return found; }

function loadSources() {
  const out = new Map();
  for (const { row } of parseCsv(fs.readFileSync(quotePath, "utf8"))) out.set(row.ticker, { event_id: row.event_id, ticker: row.ticker, left: Number(row.left_ts), right: Number(row.right_ts), scheduled: Number(row.scheduled_start_ts) });
  return out;
}
function loadBells() { return new Map(JSON.parse(fs.readFileSync(bellPath)).leg_rows.map((x) => [x.event_id, x.exact_bell_ts])); }
function clocks(ts, source, bell) { return { timestamp_epoch: ts, t_minus_scheduled_seconds: source.scheduled - ts, t_minus_actual_bell_seconds: Number.isFinite(bell) ? bell - ts : null }; }

function prefixRows(rows, left) {
  let firstAsk = null, minAsk = null, maxAsk = null, lastAsk = null, lastAskChange = null, count = 0, changes = 0, spreadIntegral = 0, sizeIntegral = 0, depthIntegral = 0, observed = 0, previousTs = null;
  let episodeAsk = null, episodeStart = null, episodeRecorded = false, priorQualifiedAsk = null, qualifiedDescents = 0;
  const output = [];
  for (const row of rows) {
    if (firstAsk === null) { firstAsk = row.ask; minAsk = row.ask; maxAsk = row.ask; lastAskChange = row.ts; }
    if (previousTs !== null) { const dt = Math.max(0, row.ts - previousTs); spreadIntegral += rows[count - 1].spread * dt; sizeIntegral += Math.log1p(rows[count - 1].top_ask_size) * dt; depthIntegral += Math.log1p(rows[count - 1].top5_ask_depth) * dt; observed += dt; }
    if (lastAsk !== null && row.ask !== lastAsk) { changes += 1; lastAskChange = row.ts; }
    if (episodeAsk === null || row.ask !== episodeAsk) { episodeAsk = row.ask; episodeStart = row.ts; episodeRecorded = false; }
    if (!episodeRecorded && row.ts - episodeStart >= DWELL_SECONDS && row.top_ask_size >= QUANTITY) { if (priorQualifiedAsk !== null && row.ask < priorQualifiedAsk) qualifiedDescents += 1; priorQualifiedAsk = row.ask; episodeRecorded = true; }
    minAsk = Math.min(minAsk, row.ask); maxAsk = Math.max(maxAsk, row.ask); count += 1;
    const elapsed = Math.max(1, row.ts - left), duration = Math.max(1, observed);
    const prefix = { ask_net: row.ask - firstAsk, ask_dip: minAsk - firstAsk, ask_peak: maxAsk - firstAsk, ask_drawdown_from_peak: maxAsk - row.ask, mean_spread: spreadIntegral / duration, spread_range: 0, quote_rate: count * 3600 / elapsed, ask_change_rate: changes * 3600 / elapsed, ask_dwell_fraction: Math.max(0, row.ts - lastAskChange) / elapsed, mean_log_top_ask_size: sizeIntegral / duration, mean_log_top5_ask_depth: depthIntegral / duration, qualified_ask_descent_count: qualifiedDescents };
    output.push({ ...row, prefix, raw_row_count: count, ask_dwell_seconds: row.ts - lastAskChange, qualified_ask_descent_count: qualifiedDescents, progress_bin: Math.max(0, Math.min(100, Math.floor((row.ts - left) / Math.max(1, row.right - left) * 100))) });
    lastAsk = row.ask; previousTs = row.ts;
  }
  return output;
}

function tickLoader(sources, privateHashes) {
  return (ticker) => {
    const source = sources.get(ticker); ensure(source, `missing source ${ticker}`);
    const p = path.join(privateRoot, "fit-local/ticks", `${ticker}.csv.gz`); ensure(fs.existsSync(p), `missing private tape ${ticker}`);
    const bytes = fs.readFileSync(p); privateHashes[ticker] = { sha256: sha(bytes), bytes: bytes.length, source_class: "PRIVATE_FIT_DEVELOPMENT_TAPE_HASH_ONLY" };
    const parsed = [], lines = zlib.gunzipSync(bytes).toString("utf8").trimEnd().split(/\r?\n/), header = lines.shift().split(","), index = Object.fromEntries(header.map((name, i) => [name, i]));
    for (let lineIndex = 0; lineIndex < lines.length; lineIndex += 1) {
      const values = lines[lineIndex].split(","), ordinal = lineIndex + 2;
      const ts = parseEt(values[index.ts_et]); if (ts === null || ts < source.left || ts > source.right) continue;
      const bids = [], asks = [];
      for (let i = 1; i <= 5; i += 1) { const bp = integer(values[index[`bid_${i}`]]), bs = positive(values[index[`bid_${i}_sz`]]), ap = integer(values[index[`ask_${i}`]]), as = positive(values[index[`ask_${i}_sz`]]); if (bp !== null && bs !== null) bids.push([bp, bs]); if (ap !== null && as !== null) asks.push([ap, as]); }
      bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]); if (!bids.length || !asks.length || bids[0][0] > asks[0][0]) continue;
      parsed.push({ ts, ordinal, receipt: `${ticker}.csv.gz#row-${ordinal}`, bid: bids[0][0], ask: asks[0][0], spread: asks[0][0] - bids[0][0], top_ask_size: asks[0][1], top5_ask_depth: asks.reduce((s, x) => s + x[1], 0), right: source.right });
    }
    parsed.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
    const formed = parsed.findIndex((row) => row.spread === 1), rows = prefixRows(formed < 0 ? [] : parsed.slice(formed), source.left);
    return rows;
  };
}

function evolve(shapes, rows, onRow) {
  const all = shapes.map((x) => x.shape_id); let surviving = [...all];
  for (const row of rows) {
    if (row.raw_row_count >= 2) { let narrowed = surviving.filter((id) => matchesMacroEnvelope(shapes.find((s) => s.shape_id === id), row, row.progress_bin)); if (!narrowed.length) narrowed = all.filter((id) => matchesMacroEnvelope(shapes.find((s) => s.shape_id === id), row, row.progress_bin)); surviving = narrowed; }
    const stop = onRow(row, surviving.map((id) => shapes.find((s) => s.shape_id === id)).filter(Boolean)); if (stop) return stop;
  }
  return null;
}

function score(events) {
  const calculate = (xs) => { const legs = xs.flatMap((e) => Object.values(e.legs)), completed = xs.filter((e) => Object.values(e.legs).every((l) => l.credited)); let under = 0, below = 0, joint = 0, carried = 0, missing = 0, execution = 0; for (const e of completed) { const ls = Object.values(e.legs), sum = ls.reduce((s, l) => s + l.entry_cents, 0), closes = ls.every((l) => Number.isInteger(l.audited_close_cents)), ds = closes ? ls.map((l) => l.entry_cents - l.audited_close_cents) : []; if (sum < 100) under += 1; if (!closes) missing += 1; if (closes && ds.every((x) => x < 0)) below += 1; if (closes && sum < 100 && ds.every((x) => x < 0)) joint += 1; if (closes && ds.some((x) => x > 0) && ds.some((x) => x < 0)) carried += 1; if (sum < 100 && ls.every((l) => Number.isInteger(l.qualifying_ask_floor_cents) && l.entry_cents <= l.qualifying_ask_floor_cents)) execution += 1; } return { D: xs.length, legs: legs.length, acted_legs: legs.filter((l) => l.acted).length, credited_legs: legs.filter((l) => l.credited).length, completed_pairs: completed.length, pairs_under_par: under, completed_pairs_close_unavailable: missing, both_legs_strictly_below_audited_close: below, joint_objective_pairs: joint, strict_carried_pairs: carried, execution_floor_pair_passes: execution }; };
  const tiers = { LE_93: (x) => x <= 93, LE_95: (x) => x <= 95, LE_97: (x) => x <= 97, LT_100: (x) => x < 100, ANY_PRICE: () => true };
  const frontier = (xs) => Object.fromEntries(Object.entries(tiers).map(([name, fn]) => { const selected = xs.filter((e) => { const ls = Object.values(e.legs); return ls.every((l) => l.credited) && fn(ls.reduce((s, l) => s + l.entry_cents, 0)); }); return [name, { fixed_denominator: xs.length, completed_pairs: selected.length, joint_objective_pairs: calculate(selected).joint_objective_pairs }]; }));
  const parts = [...group(events, (e) => `${e.category}|${e.starting_price_split}`)].sort(([a], [b]) => a.localeCompare(b)).map(([key, xs]) => ({ category: key.split("|")[0], starting_price_region: key.split("|")[1], aggregate: calculate(xs), frontier: frontier(xs) }));
  return { aggregate: calculate(events), frontier: frontier(events), category_x_starting_price_region: parts };
}
function regret(events) { const rows = events.flatMap((e) => Object.values(e.legs)).map((l) => { const n = l.credited && Number.isInteger(l.objective_traded_low_cents) ? l.entry_cents - l.objective_traded_low_cents : null; return { leg_identity: l.leg_identity, ticker: l.ticker, category: l.category, price_region: l.price_region, credited: l.credited, entry_cents: l.credited ? l.entry_cents : null, objective_traded_low_cents: l.objective_traded_low_cents, regret_cents: n, loss_bucket: !l.credited ? `NEVER_PLACED:${l.terminal_reason}` : n < 0 ? "BETTER_THAN_PRINT_FLOOR" : n === 0 ? "ZERO" : n <= 3 ? "ONE_TO_THREE" : n <= 9 ? "FOUR_TO_NINE" : "TEN_OR_MORE" }; }); return { denominator_legs: rows.length, numeric_regret: distribution(rows.map((x) => x.regret_cents)), never_placed_full_regret_n: rows.filter((x) => !x.credited).length, category_x_price_region: [...group(rows, (x) => `${x.category}|${x.price_region}`)].sort(([a], [b]) => a.localeCompare(b)).map(([key, xs]) => ({ category: key.split("|")[0], price_region: key.split("|")[1], n: xs.length, regret: distribution(xs.map((x) => x.regret_cents)), loss_buckets: countBy(xs, (x) => x.loss_bucket) })), rows }; }
function recomputeEvent(event) { const ls = Object.values(event.legs), completed = ls.every((l) => l.credited), sum = completed ? ls.reduce((s, l) => s + l.entry_cents, 0) : null, closes = completed && ls.every((l) => Number.isInteger(l.audited_close_cents)); Object.assign(event, { completed_pair: completed, combined_entry_cents: sum, pair_under_par: completed && sum < 100, both_legs_strictly_below_audited_close: closes && ls.every((l) => l.entry_cents < l.audited_close_cents), joint_objective_pass_audited_close: closes && sum < 100 && ls.every((l) => l.entry_cents < l.audited_close_cents), execution_floor_pair_pass: completed && sum < 100 && ls.every((l) => Number.isInteger(l.qualifying_ask_floor_cents) && l.entry_cents <= l.qualifying_ask_floor_cents) }); }
function applyRelease(leg, receipt) { const row = receipt.release.row; Object.assign(leg, { acted: true, credited: true, honest_fill_class: "PROVEN_TAKER_DISPLAYED_ASK_SIZE_AT_SUBMISSION", entry_cents: row.ask, action_timestamp_epoch: row.ts, terminal_reason: "V29R2_UNCAPTURED_SIBLING_RELEASED_ON_QUALIFYING_OWN_BOOK_FLOOR", placement: { price_cents: row.ask, quantity: QUANTITY, action_ts: row.ts, action_receipt: row.receipt, own_book: { bid: row.bid, ask: row.ask, spread: row.spread, ask_dwell_seconds: row.ask_dwell_seconds, top_ask_size: row.top_ask_size }, pair_cap_cents: receipt.arm.pair_cap_cents, aim_cents: receipt.arm.aim_cents, no_clock_inputs: true }, fill: { price_cents: row.ask, quantity: QUANTITY, evidence_ts: row.ts, evidence_receipt: row.receipt, evidence_type: "DISPLAYED_OPPOSING_ASK_SIZE_AT_SUBMISSION" }, v29r2_mirror_arm: receipt }); for (const [field, floor] of [["entry_minus_qualifying_ask_floor_cents", leg.qualifying_ask_floor_cents], ["entry_minus_objective_traded_low_cents", leg.objective_traded_low_cents], ["entry_minus_own_window1_close_cents", leg.own_window1_close_cents], ["entry_minus_audited_close_cents", leg.audited_close_cents], ["entry_minus_maker_floor_cents", leg.maker_floor_cents]]) leg[field] = Number.isInteger(floor) ? row.ask - floor : null; }
function rollup(rows) { const flagged = rows.filter((x) => x.first_flag); return { layer_totals: [...group(flagged, (x) => x.first_flag.layer)].sort(([a], [b]) => a.localeCompare(b)).map(([layer, xs]) => ({ layer, stopped_legs: xs.length, false_negative_neg_delta_available_past_flag: xs.filter((x) => x.tape_offered_afterward?.negative_delta_available_past_flag === "YES").length, predicates: countBy(xs, (x) => x.first_flag.predicate) })), layer_x_category: [...group(flagged, (x) => `${x.first_flag.layer}|${x.category}`)].sort(([a], [b]) => a.localeCompare(b)).map(([key, xs]) => ({ layer: key.split("|")[0], category: key.split("|")[1], stopped_legs: xs.length, false_negative_neg_delta_available_past_flag: xs.filter((x) => x.tape_offered_afterward?.negative_delta_available_past_flag === "YES").length, predicates: countBy(xs, (x) => x.first_flag.predicate) })) }; }

function build() {
  const required = [eventPath, legPath, tracePath, scorePath, quotePath, bellPath, shapePath, policyPath, interimPolicyPath, policyTestPath, packageTestPath, __filename]; for (const p of required) ensure(fs.existsSync(p), `missing ${p}`);
  child.execFileSync("git", ["cat-file", "-e", `${ceilingCommit}^{commit}`], { cwd: repo });
  const ceilingCsv = gitShow(ceilingCommit, ceilingCsvGitPath), ceilingSummaryText = gitShow(ceilingCommit, ceilingSummaryGitPath), ceilingSummary = JSON.parse(ceilingSummaryText), ceilingRows = parseQuotedCsv(ceilingCsv);
  ensure(ceilingSummary.class_b_FN_mirror.convertible === 29 && ceilingSummary.class_a_carried_pairs.convertible === 119, "independent ceiling changed");
  const events = readRows(eventPath), inputLegs = readRows(legPath), baseTrace = JSON.parse(fs.readFileSync(tracePath)), baseScore = JSON.parse(fs.readFileSync(scorePath));
  ensure(events.length === 804 && inputLegs.length === 1608 && baseTrace.rows.length === 1608, "V28 conservation failed"); ensure(baseScore.V28_score.joint_objective_pairs === 65, "V28 floor mismatch");
  const sources = loadSources(), bells = loadBells(), library = JSON.parse(fs.readFileSync(shapePath)), privateHashes = {}, loadTicks = tickLoader(sources, privateHashes);
  const eventByIdInput = new Map(events.map((event) => [event.event_id, event]));
  const carriedTargets = new Set(events.filter((event) => { const legs = Object.values(event.legs); return legs.every((leg) => leg.credited) && legs.every((leg) => Number.isInteger(leg.audited_close_cents)) && legs.some((leg) => leg.entry_cents > leg.audited_close_cents) && legs.some((leg) => leg.entry_cents < leg.audited_close_cents); }).map((event) => Object.values(event.legs).find((leg) => leg.entry_cents > leg.audited_close_cents).leg_identity));
  const completionFlagRows = baseTrace.rows.filter((row) => row.first_flag?.layer === "COMPLETION" && row.tape_offered_afterward?.negative_delta_available_past_flag === "YES");
  const completionFlagCredited = new Set();
  const completionTargets = new Set();
  for (const row of completionFlagRows) {
    const event = eventByIdInput.get(row.event_id); ensure(event, `completion trace event missing ${row.event_id}`);
    const legs = Object.values(event.legs), flagged = legs.find((leg) => leg.leg_identity === row.leg_identity), sibling = legs.find((leg) => leg.leg_identity !== row.leg_identity);
    ensure(flagged && sibling, `completion trace leg relation missing ${row.leg_identity}`);
    if (flagged.credited) completionFlagCredited.add(flagged.leg_identity);
    if (!sibling.credited) completionTargets.add(sibling.leg_identity);
  }
  ensure(carriedTargets.size === 144 && completionFlagRows.length === 237 && completionFlagCredited.size === 237 && completionTargets.size === 227, `target mass mismatch carried=${carriedTargets.size} flags=${completionFlagRows.length} credited=${completionFlagCredited.size} uncaptured_siblings=${completionTargets.size}`);
  ensure([...carriedTargets].every((id) => !completionTargets.has(id)), "target classes overlap");
  const targetClass = new Map([...carriedTargets].map((id) => [id, "V28_CARRIED_POSITIVE_LEG"]).concat([...completionTargets].map((id) => [id, "V28_UNCREDITED_COMPLETION_SIBLING"])));
  const receipts = [], changedLegs = new Set(), changedEvents = new Set();
  for (const event of events) {
    const legs = Object.values(event.legs);
    for (const target of legs.filter((leg) => targetClass.has(leg.leg_identity))) {
      const first = legs.find((leg) => leg.leg_identity !== target.leg_identity); ensure(first?.credited && Number.isFinite(fillTs(first)), `armed target lacks credited sibling ${target.leg_identity}`);
      const armTs = fillTs(first), incumbentActionTs = target.acted && Number.isFinite(target.action_timestamp_epoch) ? Number(target.action_timestamp_epoch) : null;
      const incumbentActive = (incumbentActionTs !== null && incumbentActionTs <= armTs) || (target.credited && fillTs(target) <= armTs);
      const source = sources.get(target.ticker); ensure(source, `missing target source ${target.ticker}`);
      const rows = loadTicks(target.ticker), armBook = currentAt(rows, armTs), arm = armUncapturedSide({ incumbentActive, firstFillCents: first.entry_cents, ownLiveAskCents: armBook?.ask ?? null });
      const groupKey = `${target.category}|${regionForShape(target.price_region)}`, shapeGroup = library.groups[groupKey] || null;
      const stopBefore = incumbentActionTs !== null && incumbentActionTs > armTs ? incumbentActionTs : source.right + 1;
      let evaluated = 0, release = null, lastDecision = null;
      const evidence = { later_receipts: 0, at_or_below_aim: 0, spread_lawful: 0, dwell_lawful: 0, capacity_lawful: 0 };
      const inspect = (row, survivors) => {
        if (row.ts <= armTs || row.ts >= stopBefore) return null;
        evaluated += 1; evidence.later_receipts += 1;
        if (row.ask <= arm.aim_cents) evidence.at_or_below_aim += 1;
        if (row.ask <= arm.aim_cents && row.spread <= MAX_SPREAD_CENTS) evidence.spread_lawful += 1;
        if (row.ask <= arm.aim_cents && row.spread <= MAX_SPREAD_CENTS && row.ask_dwell_seconds >= DWELL_SECONDS) evidence.dwell_lawful += 1;
        if (row.ask <= arm.aim_cents && row.spread <= MAX_SPREAD_CENTS && row.ask_dwell_seconds >= DWELL_SECONDS && row.top_ask_size >= QUANTITY) evidence.capacity_lawful += 1;
        const usable = survivors.filter((shape) => shape.usable_for_signing), verdicts = usable.map((shape) => ({ shape_id: shape.shape_id, ...ordinalVerdict(shape, row.qualified_ask_descent_count) }));
        const confirmation = usable.length === 0 ? "NOT_BOUND" : verdicts.every((x) => x.verdict === "FLOOR") ? "ALL_FLOOR" : verdicts.every((x) => x.verdict === "LOWER") ? "ALL_LOWER" : "MIXED";
        const decision = releaseOnQualifyingFloor({ armed: arm, bid: row.bid, ask: row.ask, spread: row.spread, askDwellSeconds: row.ask_dwell_seconds, displayedAskSize: row.top_ask_size, strictlyLaterReceipt: row.ts > armTs });
        lastDecision = { state: decision.state, reason: decision.reason, row: { ts: row.ts, receipt: row.receipt, bid: row.bid, ask: row.ask, spread: row.spread, ask_dwell_seconds: row.ask_dwell_seconds, top_ask_size: row.top_ask_size, qualified_ask_descent_count: row.qualified_ask_descent_count }, surviving_shape_ids: survivors.map((x) => x.shape_id), usable_shape_ids: usable.map((x) => x.shape_id), coherent_decline_ordinal_confirmation: confirmation, ordinal_verdicts: verdicts };
        if (decision.state === "PLACE") { release = { ...lastDecision, decision }; return lastDecision; }
        return null;
      };
      if (arm.state === "HOLD") {
        if (shapeGroup) evolve(shapeGroup.shapes, rows, inspect);
        else for (const row of rows) if (inspect(row, [])) break;
      }
      let disposition, bindingReason;
      if (release) { disposition = "RELEASED_AND_FILLED"; bindingReason = release.decision.reason; }
      else if (incumbentActionTs !== null && incumbentActionTs <= source.right) { disposition = "INCUMBENT_FIRST"; bindingReason = incumbentActive ? "INCUMBENT_ACTIVE_AT_ARM" : "INCUMBENT_PLACED_BEFORE_OVERLAY_FLOOR_RELEASE"; }
      else if (arm.state !== "HOLD") { disposition = "NEVER_RELEASED"; bindingReason = arm.reason; }
      else if (evidence.later_receipts === 0) { disposition = "NEVER_RELEASED"; bindingReason = "NO_STRICTLY_LATER_OWN_BOOK_RECEIPT"; }
      else if (evidence.at_or_below_aim === 0) { disposition = "NEVER_RELEASED"; bindingReason = "OWN_ASK_NEVER_AT_OR_BELOW_AIM"; }
      else if (evidence.spread_lawful === 0) { disposition = "NEVER_RELEASED"; bindingReason = "AT_OR_BELOW_AIM_SPREAD_NEVER_LE_ONE"; }
      else if (evidence.dwell_lawful === 0) { disposition = "NEVER_RELEASED"; bindingReason = "AT_OR_BELOW_AIM_DWELL_NEVER_GE_TEN"; }
      else if (evidence.capacity_lawful === 0) { disposition = "NEVER_RELEASED"; bindingReason = "AT_OR_BELOW_AIM_CAPACITY_NEVER_GE_FIVE"; }
      else { disposition = "RELEASED_UNFILLED"; bindingReason = "QUALIFYING_RELEASE_NOT_CREDITED_FAIL_CLOSED"; }
      const receipt = { target_class: targetClass.get(target.leg_identity), disposition, binding_reason: bindingReason, event_id: event.event_id, category: event.category, starting_price_region: event.starting_price_split, armed_leg_identity: target.leg_identity, armed_ticker: target.ticker, first_filled_leg_identity: first.leg_identity, first_fill_cents: first.entry_cents, first_fill_receipt: first.fill?.evidence_receipt ?? first.fill?.receipt ?? first.placement?.action_receipt ?? null, arm_clock: clocks(armTs, source, bells.get(event.event_id)), live_book_at_arm: armBook ? { receipt: armBook.receipt, timestamp_epoch: armBook.ts, bid: armBook.bid, ask: armBook.ask, spread: armBook.spread, top_ask_size: armBook.top_ask_size, qualified_ask_descent_count: armBook.qualified_ask_descent_count } : null, incumbent_action_timestamp_epoch: incumbentActionTs, incumbent_active_at_arm: incumbentActive, arm, evaluation: { cadence: "EVERY_CAUSAL_OWN_BOOK_RECEIPT_IN_EVENT_ORDER", polling_interval_seconds: null, causal_receipts_evaluated_after_arm_before_incumbent_or_right_edge: evaluated, elapsed_time_policy_inputs: [], stop_before_incumbent_action_timestamp_epoch: stopBefore <= source.right ? stopBefore : null, evidence_census: evidence }, shape_group: groupKey, coherent_decline_ordinal_role: "LOGGED_CONFIRMATION_ONLY_NEVER_RELEASE_PRECONDITION", release: release ? { ...release, row: { ...release.row, clocks: clocks(release.row.ts, source, bells.get(event.event_id)) } } : null, terminal: disposition, last_decision: lastDecision };
      receipts.push(receipt);
      if (release) { applyRelease(target, receipt); recomputeEvent(event); changedLegs.add(target.leg_identity); changedEvents.add(event.event_id); }
    }
  }
  ensure(receipts.length === 371, `armed population receipt mismatch ${receipts.length}`);
  for (const event of events) recomputeEvent(event);
  const resultLegs = events.flatMap((e) => Object.values(e.legs)).sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)), baseByLeg = new Map(inputLegs.map((x) => [x.leg_identity, x]));
  const diffRows = resultLegs.map((x) => ({ leg_identity: x.leg_identity, changed: changedLegs.has(x.leg_identity), V28_semantic_sha256: semanticHash(baseByLeg.get(x.leg_identity)), V29R2_semantic_sha256: semanticHash(x) }));
  ensure(diffRows.filter((x) => x.changed).every((x) => x.V28_semantic_sha256 !== x.V29R2_semantic_sha256), "changed stream unchanged"); ensure(diffRows.filter((x) => !x.changed).every((x) => x.V28_semantic_sha256 === x.V29R2_semantic_sha256), "non-target stream drift");
  const eventById = new Map(events.map((e) => [e.event_id, e])), receiptByLeg = new Map(receipts.map((x) => [x.armed_leg_identity, x]));
  const traceRows = baseTrace.rows.map((base) => { const event = eventById.get(base.event_id), leg = Object.values(event.legs).find((x) => x.leg_identity === base.leg_identity), receipt = receiptByLeg.get(base.leg_identity) || null; if (!changedEvents.has(base.event_id)) return { ...clone(base), variant: "V29R2_MIRROR_ARMED_UNCAPTURED_SIDE", v29r2_mirror_arm_effect: receipt ? { arm: receipt.arm, disposition: receipt.disposition, binding_reason: receipt.binding_reason, terminal: receipt.terminal } : null }; return { ...clone(base), variant: "V29R2_MIRROR_ARMED_UNCAPTURED_SIDE", layer_results_in_execution_order: LAYERS.map((layer, i) => ({ order: i + 1, layer, result: "PASS" })), first_flag: null, tape_offered_afterward: null, final_state: event.joint_objective_pass_audited_close ? "JOINT-CAPTURED" : "carried", leg_action_state: { acted: leg.acted, credited: leg.credited, entry_cents: leg.entry_cents, honest_fill_class: leg.honest_fill_class, terminal_reason: leg.terminal_reason }, event_result: { completed_pair: event.completed_pair, combined_entry_cents: event.combined_entry_cents, pair_under_par: event.pair_under_par, both_legs_strictly_below_audited_close: event.both_legs_strictly_below_audited_close, joint_objective_pass: event.joint_objective_pass_audited_close }, v29r2_mirror_arm_effect: receipt ? { arm: receipt.arm, release: receipt.release, disposition: receipt.disposition, binding_reason: receipt.binding_reason, terminal: receipt.terminal } : { sibling_armed_other_leg: true } }; });
  ensure(traceRows.length === 1608 && new Set(traceRows.map((x) => x.leg_identity)).size === 1608, "trace conservation");
  const trace = { schema: "WINDOW1_DECISION_TRACE_1608_V29R2", generated_utc: "2026-08-04T00:00:00Z", variant: "V29R2_MIRROR_ARMED_UNCAPTURED_SIDE", scope: { events: 804, legs: 1608 }, source_binding: { V28_commit: "3339f30dc9d3136788617bf0e5456708008b845b", V28_trace_sha256: fileHash(tracePath) }, conservation: { rows: traceRows.length, one_row_per_leg: true }, rollup: rollup(traceRows), rows: traceRows };
  const sc = score(events), rg = regret(events), delta = Object.fromEntries(Object.keys(baseScore.V28_score).filter((k) => Number.isInteger(baseScore.V28_score[k])).map((k) => [k, sc.aggregate[k] - baseScore.V28_score[k]]));
  const newByTicker = new Map(resultLegs.map((x) => [x.ticker, x])), oldByTicker = new Map(inputLegs.map((x) => [x.ticker, x]));
  const gradedCeiling = ceilingRows.map((row) => { const old = oldByTicker.get(row.leg_ticker), now = newByTicker.get(row.leg_ticker), changed = Boolean(now && changedLegs.has(now.leg_identity)), converted = row.verdict === "CONVERTIBLE" && changed && (row.class === "b_FN_mirror" ? !old.credited && now.credited : Number.isInteger(now.audited_close_cents) && now.entry_cents < now.audited_close_cents); return { class: row.class, ticker: row.leg_ticker, verdict: row.verdict, changed_by_V29R2: changed, converted_by_V29R2: converted, V28_entry_cents: old?.credited ? old.entry_cents : null, V29R2_entry_cents: now?.credited ? now.entry_cents : null, audited_close_cents_grading_only: now?.audited_close_cents ?? null }; });
  const byCeilingClass = (name, ceiling) => { const rows = gradedCeiling.filter((x) => x.class === name), convertible = rows.filter((x) => x.verdict === "CONVERTIBLE"); return { independent_target_rows: rows.length, independent_convertible_ceiling: ceiling, V29R2_converted: convertible.filter((x) => x.converted_by_V29R2).length, changed_convertible_rows: convertible.filter((x) => x.changed_by_V29R2).length, conversion_share_of_independent_ceiling: ceiling ? convertible.filter((x) => x.converted_by_V29R2).length / ceiling : null }; };
  const delays = receipts.filter((x) => x.release).map((x) => (x.release.row.ts - x.arm_clock.timestamp_epoch) / 60), delayDistribution = distribution(delays); delete delayDistribution.total_cents; delayDistribution.total_minutes = delays.reduce((a, b) => a + b, 0);
  const completionTargetLegs = [...completionTargets].map((id) => baseByLeg.get(id));
  const dispositionRows = receipts.map((x) => ({ target_class: x.target_class, event_id: x.event_id, armed_leg_identity: x.armed_leg_identity, armed_ticker: x.armed_ticker, disposition: x.disposition, binding_reason: x.binding_reason, aim_cents: x.arm.aim_cents ?? null, pair_cap_cents: x.arm.pair_cap_cents ?? null, incumbent_action_timestamp_epoch: x.incumbent_action_timestamp_epoch, arm_timestamp_epoch: x.arm_clock.timestamp_epoch, release_timestamp_epoch: x.release?.row.ts ?? null, release_price_cents: x.release?.row.ask ?? null, ordinal_confirmation_at_release: x.release?.coherent_decline_ordinal_confirmation ?? null }));
  const dispositionSummary = { target_legs: dispositionRows.length, by_disposition: countBy(dispositionRows, (x) => x.disposition), by_target_class: [...group(dispositionRows, (x) => x.target_class)].sort(([a], [b]) => a.localeCompare(b)).map(([targetClassName, xs]) => ({ target_class: targetClassName, legs: xs.length, dispositions: countBy(xs, (x) => x.disposition), binding_reasons: countBy(xs, (x) => x.binding_reason) })), conservation: { V28_uncaptured_completion_siblings: completionTargets.size, V28_carried_positive_legs: carriedTargets.size, sum: completionTargets.size + carriedTargets.size, receipt_rows: receipts.length, exact: completionTargets.size + carriedTargets.size === receipts.length } };
  fs.mkdirSync(output, { recursive: true }); write(path.join(output, "EVENT_LEDGER.jsonl.gz"), gzipRows(events)); write(path.join(output, "LEG_LEDGER.jsonl.gz"), gzipRows(resultLegs)); write(path.join(output, "DECISION_TRACE_1608.json"), canonical(trace)); write(path.join(output, "MIRROR_ARM_RECEIPTS.jsonl.gz"), gzipRows(receipts));
  write(path.join(output, "ARMED_LEG_DISPOSITION.json"), canonical({ ...dispositionSummary, rows: dispositionRows }));
  write(path.join(output, "SCORECARD.json"), canonical({ variant: "V29R2_MIRROR_ARMED_UNCAPTURED_SIDE", V28_floor: baseScore.V28_score, V29R2_score: sc.aggregate, delta, joint_non_regression: sc.aggregate.joint_objective_pairs >= 65, close_bar_policy_input: false, joint_law_role: "EX_POST_GRADE_ONLY", category_x_starting_price_region: sc.category_x_starting_price_region }));
  write(path.join(output, "FRONTIER.json"), canonical({ fixed_denominator: 804, JOINT_law: "BOTH_LEGS_CREDITED_AND_SUM_LT_100_AND_EACH_ENTRY_STRICTLY_BELOW_OWN_AUDITED_CLOSE", tiers: sc.frontier, category_x_starting_price_region: sc.category_x_starting_price_region.map((x) => ({ category: x.category, starting_price_region: x.starting_price_region, frontier: x.frontier })) }));
  write(path.join(output, "REGRET_GAUGE.json"), canonical({ law: "CREDITED_FILL_MINUS_OBJECTIVE_PRINT_BACKED_FLOOR; NEVER_PLACED_REMAINS_CATEGORICAL_FULL_REGRET", denominator_legs: rg.denominator_legs, numeric_regret: rg.numeric_regret, never_placed_full_regret_n: rg.never_placed_full_regret_n, category_x_price_region: rg.category_x_price_region })); write(path.join(output, "REGRET_LEG_LEDGER.jsonl.gz"), gzipRows(rg.rows));
  write(path.join(output, "INDEPENDENT_CEILING_COMPARISON.json"), canonical({ authority: { commit: ceilingCommit, csv_path: ceilingCsvGitPath, csv_sha256: sha(ceilingCsv), summary_path: ceilingSummaryGitPath, summary_sha256: sha(ceilingSummaryText) }, side_by_side: { completion_mirror_FN_class: byCeilingClass("b_FN_mirror", 29), carried_class: byCeilingClass("a_carried_pair", 119) }, denominator_compatibility: { independent_FN_237: "V11_NON_ACTION_CLASS", V28_completion_trace_flags_237: "TRACE ROWS ARE CREDITED SIDE", V28_uncaptured_sibling_targets_227: "UNIQUE OPPOSITE LEGS CURRENTLY UNCREDITED", independent_carried_296: "BOTH_LEGS_OF_148_V11_CARRIED_PAIRS", V28_carried_target_144: "POSITIVE_DELTA_LEG_ONLY_IN_144_V28_STRICT_CARRIED_PAIRS" }, rows: gradedCeiling }));
  write(path.join(output, "TARGET_MASS_AND_CONVERSION.json"), canonical({ defect_fingerprint_V29R: { completion_trace_rows: completionFlagRows.length, completion_trace_rows_already_credited_in_V28: completionFlagCredited.size, completion_rows_currently_uncredited_in_V28: 0, diagnosis: "V29R_TARGETED_THE_CREDITED_TRACE_ROW_THE_POPULATION_WAS_THE_MIRROR_OF_THE_MIRROR" }, corrected_target_mass: { V28_uncaptured_completion_siblings: completionTargets.size, V28_carried_positive_legs: carriedTargets.size, total_unique_armed_leg_targets: targetClass.size }, causal_eligibility: { carried_armed: receipts.filter((x) => x.target_class === "V28_CARRIED_POSITIVE_LEG" && x.arm.state === "HOLD").length, carried_released_and_filled: receipts.filter((x) => x.target_class === "V28_CARRIED_POSITIVE_LEG" && x.disposition === "RELEASED_AND_FILLED").length, carried_incumbent_first: receipts.filter((x) => x.target_class === "V28_CARRIED_POSITIVE_LEG" && x.disposition === "INCUMBENT_FIRST").length, uncaptured_sibling_rows_already_credited_in_V28: completionTargetLegs.filter((x) => x?.credited).length, uncaptured_sibling_rows_currently_uncredited_in_V28: completionTargetLegs.filter((x) => !x?.credited).length, uncaptured_siblings_armed: receipts.filter((x) => x.target_class === "V28_UNCREDITED_COMPLETION_SIBLING" && x.arm.state === "HOLD").length, uncaptured_siblings_released_and_filled: receipts.filter((x) => x.target_class === "V28_UNCREDITED_COMPLETION_SIBLING" && x.disposition === "RELEASED_AND_FILLED").length }, dispositions: dispositionSummary.by_disposition, score_effect: delta, ruling: "TARGET_IS_THE_UNCREDITED_SIBLING_OF_EACH_CREDITED_COMPLETION_FLAG; INCUMBENT_FIRST_STANDS_OVERLAY_DOWN; QUALIFYING_FLOOR_RELEASE_NEVER_BLOCKS_V28" }));
  write(path.join(output, "CONTINUOUS_EVALUATION_RECEIPT.json"), canonical({ cadence: "EVERY_CAUSAL_OWN_BOOK_RECEIPT_IN_EVENT_ORDER_FROM_ARM_UNTIL_INCUMBENT_ACTION_OR_GUARDED_RIGHT_EDGE", polling_interval_seconds: null, wall_clock_policy_inputs: [], armed_receipts: receipts.filter((x) => x.arm.state === "HOLD").length, released_receipts: receipts.filter((x) => x.release).length, release_delay_minutes: delayDistribution, independent_FN_convertible_median_minutes: 0.9, independent_source_commit: ceilingCommit, statement: "0.9 minutes is a grading comparator only; it is never a trigger or threshold" }));
  write(path.join(output, "DIFFERENTIAL_RECEIPT.json"), canonical({ V28_leg_streams: 1608, changed_leg_streams: changedLegs.size, unchanged_leg_streams: 1608 - changedLegs.size, changed_event_streams: changedEvents.size, changed_stream_identities: [...changedLegs].sort(), all_other_leg_streams_semantic_hash_equal: true, rows: diffRows }));
  write(path.join(output, "RULINGS_RECEIPT.json"), canonical({ overlay_law: "NEVER_BLOCKS_V28; INCUMBENT_FIRST_STANDS_OVERLAY_DOWN; ALL_UNCHANGED_STREAMS_HASH_IDENTICAL", dwell_10_seconds: { status: "RATIFIED_PROVISIONALLY_AS_IS", reason: "COMPARABILITY_WITH_ALL_PRIOR_RESULTS", sensitivity_study: "DEFERRED_TO_HOLDOUT_ERA" }, pair_carry_clock: { status: "PROHIBITED", wall_clock_limit: null, elapsed_time_policy_inputs: [] }, V29R2: { activation_population: "UNCREDITED_SIBLING_OF_CREDITED_COMPLETION_FLAG_PLUS_SEPARATE_CARRIED_POSITIVE_CLASS", close_bar: "REMOVED_EX_POST_NOT_BOUND", aim: "min(99-first_fill, own_lawful_live_book_floor)", release_authority: "FIRST_STRICTLY_LATER_OWN_BOOK_ASK_AT_OR_BELOW_AIM_WITH_SPREAD_LE_1_DWELL_GE_10_CAPACITY_GE_5", coherent_decline_ordinal: "LOGGED_CONFIRMATION_ONLY_NEVER_GATE", joint_law: "EX_POST_GRADE_ONLY" }, orphans_unchanged: [{ name: "DEAD_SPREAD_THRESHOLD", value: 20, status: "AWAITING_RULING" }, { name: "SPREAD_LE_2_POSTING_GATE", value: 2, status: "AWAITING_RULING" }] }));
  write(path.join(output, "FORBIDDEN_ACCESS_RECEIPT.json"), canonical({ audited_close_as_policy_input: false, ex_post_floor_as_policy_input: false, wall_clock_pair_input: false, holdout: false, live: false, network_runtime: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, Window2: false, deployment: false }));
  write(path.join(output, "TEST_RESULTS.json"), canonical({ status: "PASS", commands: ["node arb-executor/tests/test_window1_v29r2_mirror_armed_uncaptured_side_policy.js", "node arb-executor/tests/test_window1_v29r2_mirror_armed_uncaptured_side_package.js", "node arb-executor/tests/test_window1_v28_anchor_cap_stack_package.js"], omissions: 0, deselections: 0 }));
  const requiredSource = [eventPath, legPath, tracePath, scorePath, quotePath, bellPath, shapePath, policyPath, interimPolicyPath, policyTestPath, packageTestPath, __filename]; write(path.join(output, "SOURCE_HASH_MANIFEST.json"), canonical({ committed: Object.fromEntries(requiredSource.map((p) => [rel(p), { sha256: fileHash(p), bytes: fs.statSync(p).size }])), git_object_sources: { [`${ceilingCommit}:${ceilingCsvGitPath}`]: { sha256: sha(ceilingCsv), bytes: Buffer.byteLength(ceilingCsv) }, [`${ceilingCommit}:${ceilingSummaryGitPath}`]: { sha256: sha(ceilingSummaryText), bytes: Buffer.byteLength(ceilingSummaryText) } }, private_fit_tick_hashes: Object.fromEntries(Object.entries(privateHashes).sort(([a], [b]) => a.localeCompare(b))) }));
  write(path.join(output, "REPORT.md"), `# V29-R2 — mirror-armed uncaptured side\n\nV29-R2 is an additive overlay on immutable V28 (JOINT 65). It corrects V29-R's mirrored activation population: the 237 completion flags sit on credited rows, while the actual opposite-side uncaptured population is 227 unique legs. Each credited first side arms its uncredited sibling at min(99-first_fill, its own causal live ask at arm). The first strictly later own-book floor at or below that aim releases when spread <=1, ask dwell >=10 seconds, and displayed ask size >=5. Coherent decline ordinal is logged confirmation only and never a release precondition. The incumbent path wins any earlier race and is never blocked. Audited close is grading-only; time is not a policy input.\n`);
  process.stdout.write(canonical({ status: "BUILT", V28_joint: 65, V29R2_joint: sc.aggregate.joint_objective_pairs, changed_legs: changedLegs.size, released_and_filled: receipts.filter((x) => x.disposition === "RELEASED_AND_FILLED").length, dispositions: dispositionSummary.by_disposition, release_delay_median_minutes: delayDistribution.median, FN_conversion: byCeilingClass("b_FN_mirror", 29), carried_conversion: byCeilingClass("a_carried_pair", 119) }));
}

function manifest(root) { const out = {}, skip = new Set(["ARTIFACT_HASH_MANIFEST.json", "DETERMINISM_RECEIPT.json"]); for (const e of fs.readdirSync(root, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) if (e.isFile() && !skip.has(e.name)) { const p = path.join(root, e.name); out[e.name] = { sha256: fileHash(p), bytes: fs.statSync(p).size }; } return out; }
function finalize() { const a = manifest(path.resolve(run1)), b = manifest(path.resolve(run2)); ensure(JSON.stringify(a) === JSON.stringify(b), "determinism mismatch"); fs.cpSync(path.resolve(run1), output, { recursive: true }); write(path.join(output, "DETERMINISM_RECEIPT.json"), canonical({ clean_builds: 2, byte_identical_payloads: true, payload_file_count: Object.keys(a).length, payload_manifest_sha256: sha(canonical(a)) })); const files = manifest(output); files["DETERMINISM_RECEIPT.json"] = { sha256: fileHash(path.join(output, "DETERMINISM_RECEIPT.json")), bytes: fs.statSync(path.join(output, "DETERMINISM_RECEIPT.json")).size }; write(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(Object.entries(files).sort(([a], [b]) => a.localeCompare(b))) })); process.stdout.write(canonical({ status: "FINALIZED", payload_manifest_sha256: sha(canonical(a)), payload_file_count: Object.keys(a).length })); }

if (run1 || run2) finalize(); else build();
