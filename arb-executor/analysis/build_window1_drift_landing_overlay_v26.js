#!/usr/bin/env node
"use strict";

const childProcess = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { scoreVariant } = require("./build_window1_pair_cap_v23.js");
const { findLaterFill } = require("./window1_landing_estimator_v24_policy.js");
const {
  ASYMMETRIC_QUANTILE,
  MIN_DWELL_SECONDS,
  MIN_TRAINING_N,
  asymmetricLoss,
  authority,
  estimateAtRead,
  overlayDecision,
  selectCellFit,
} = require("./window1_drift_landing_overlay_v26_policy.js");

const argv = process.argv.slice(2);
const arg = (name, fallback) => { const index = argv.indexOf(name); return index >= 0 ? argv[index + 1] : fallback; };
const repo = path.resolve(arg("--repo", "."));
const privateRoot = path.resolve(arg("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const out = path.resolve(arg("--output", path.join(repo, ".claude/window1_live_v4_replay/drift_landing_overlay_v26_20260804")));
const compare1 = arg("--compare-run1", null), compare2 = arg("--compare-run2", null);
const v23Dir = path.join(repo, ".claude/window1_live_v4_replay/pair_cap_v23_audited_close_20260804");
const v24Dir = path.join(repo, ".claude/window1_live_v4_replay/landing_estimator_phased_arming_v24_20260804");
const quotePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const analysisCommit = "d07a9813cf96f78631a2b22a6b11b95593742f61";
const analysisLandingRel = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/LANDING_PREDICTABILITY_LEGS.csv";
const analysisMissRel = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/MISS_LEDGER_V23_1608.csv";
const candidateCells = new Set(["ATP_CHALL|51_75", "ATP_MAIN|51_75", "WTA_MAIN|51_75", "WTA_CHALL|51_75", "WTA_CHALL|ge76"]);
const exactStartExcluded = new Set([
  "KXATPCHALLENGERMATCH-26JUL19HURBIG", "KXATPCHALLENGERMATCH-26JUL19NIKVRB",
  "KXATPMATCH-26JUL12LAJVAN", "KXWTACHALLENGERMATCH-26JUL16BRAVED", "KXWTAMATCH-26JUL20KORJIM",
]);

function ensure(ok, message) { if (!ok) throw new Error(message); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function readRows(file) { const text = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim(); return text ? text.split(/\r?\n/).map(JSON.parse) : []; }
function gzipRows(rows) { return zlib.gzipSync(Buffer.from(`${rows.map(JSON.stringify).join("\n")}\n`), { level: 9, mtime: 0 }); }
function parseCsv(text) { const lines = text.trimEnd().split(/\r?\n/), header = lines.shift().split(","); return lines.filter(Boolean).map((line, index) => ({ row: Object.fromEntries(line.split(",").map((value, i) => [header[i], value])), ordinal: index + 2 })); }
function integer(value) { const number = Number(value); return Number.isInteger(number) ? number : null; }
function positive(value) { const number = Number(value); return Number.isFinite(number) && number > 0 ? number : null; }
function group(rows, keyFn) { const output = new Map(); for (const row of rows) { const key = keyFn(row); if (!output.has(key)) output.set(key, []); output.get(key).push(row); } return output; }
function countBy(rows, keyFn) { const output = {}; for (const row of rows) { const key = String(keyFn(row)); output[key] = (output[key] || 0) + 1; } return Object.fromEntries(Object.entries(output).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }
function quantile(values, p) { const ordered = values.filter(Number.isFinite).sort((a, b) => a - b); return ordered.length ? ordered[Math.floor((ordered.length - 1) * p)] : null; }
function distribution(values) { const numeric = values.filter(Number.isFinite); return { denominator: values.length, numeric_n: numeric.length, null_n: values.length - numeric.length, min: numeric.length ? Math.min(...numeric) : null, p25: quantile(numeric, .25), median: quantile(numeric, .5), p75: quantile(numeric, .75), p90: quantile(numeric, .9), max: numeric.length ? Math.max(...numeric) : null }; }
function parseEt(value) { const match = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/); if (!match) return null; let hour = Number(match[4]); if (match[7] === "AM" && hour === 12) hour = 0; if (match[7] === "PM" && hour !== 12) hour += 12; return Date.parse(`${match[1]}-${match[2]}-${match[3]}T${String(hour).padStart(2, "0")}:${match[5]}:${match[6]}-04:00`) / 1000; }
function rowHash(row) { return sha256(Buffer.from(JSON.stringify(row))); }

function compareBuilds(a, b) {
  const excluded = new Set(["ARTIFACT_HASH_MANIFEST.json", "DETERMINISM_RECEIPT.json"]);
  const aa = fs.readdirSync(a).filter((name) => !excluded.has(name)).sort(), bb = fs.readdirSync(b).filter((name) => !excluded.has(name)).sort();
  ensure(JSON.stringify(aa) === JSON.stringify(bb), "determinism file census mismatch");
  const mismatches = aa.filter((name) => hashFile(path.join(a, name)) !== hashFile(path.join(b, name)));
  ensure(!mismatches.length, `determinism mismatch: ${mismatches.join(",")}`);
  return { clean_builds: 2, compared_files: aa.length, byte_identical: true, mismatches: [] };
}

function bindAnalysisSeat() {
  childProcess.execFileSync("git", ["rev-parse", "--verify", `${analysisCommit}^{commit}`], { cwd: repo });
  childProcess.execFileSync("git", ["cat-file", "-e", `${analysisCommit}^{commit}`], { cwd: repo });
  const landing = childProcess.execFileSync("git", ["show", `${analysisCommit}:${analysisLandingRel}`], { cwd: repo, maxBuffer: 64 * 1024 * 1024 });
  const miss = childProcess.execFileSync("git", ["show", `${analysisCommit}:${analysisMissRel}`], { cwd: repo, maxBuffer: 64 * 1024 * 1024 });
  const missRows = parseCsv(miss.toString("utf8")).map(({ row }) => row);
  const l9 = missRows.filter((row) => row.layer === "L9_carry" && row.tag === "FIXABLE" && row.category === "ATP_CHALL" && row.price_region === "51_75");
  ensure(l9.length === 77, `analysis-seat L9 ATP_CHALL 51_75 identity count ${l9.length}`);
  return { landing, miss, l9 };
}

function quoteSources() {
  const rows = parseCsv(fs.readFileSync(quotePath, "utf8")).map(({ row }) => ({
    event_id: row.event_id, category: row.category, leg_id: row.leg, ticker: row.ticker,
    left_ts: Number(row.left_ts), right_ts: Number(row.right_ts), scheduled_start_ts: Number(row.scheduled_start_ts),
  }));
  ensure(rows.length === 1608, `quote source rows ${rows.length}`);
  return new Map(rows.map((row) => [row.ticker, row]));
}

function loadTicks(source, privateHashes) {
  const file = path.join(privateRoot, "fit-local/ticks", `${source.ticker}.csv.gz`);
  ensure(fs.existsSync(file), `missing private tick source ${source.ticker}`);
  const bytes = fs.readFileSync(file); privateHashes[source.ticker] = { sha256: sha256(bytes), bytes: bytes.length };
  const rows = [];
  for (const { row: raw, ordinal } of parseCsv(zlib.gunzipSync(bytes).toString("utf8"))) {
    const ts = parseEt(raw.ts_et); if (ts === null || ts < source.left_ts || ts > source.right_ts) continue;
    const bids = [], asks = [];
    for (let i = 1; i <= 5; i += 1) {
      const bp = integer(raw[`bid_${i}`]), bs = positive(raw[`bid_${i}_sz`]), ap = integer(raw[`ask_${i}`]), as = positive(raw[`ask_${i}_sz`]);
      if (bp !== null && bs !== null) bids.push([bp, bs]); if (ap !== null && as !== null) asks.push([ap, as]);
    }
    bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]);
    if (!bids.length || !asks.length || bids[0][0] > asks[0][0]) continue;
    rows.push({ ts, ordinal, receipt: `${path.basename(file)}#row-${ordinal}`, bid: bids[0][0], ask: asks[0][0], spread: asks[0][0] - bids[0][0], top_ask_size: asks[0][1], top5_ask_depth: asks.reduce((sum, [, size]) => sum + size, 0), last_traded: integer(raw.last_trade), asks });
  }
  rows.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  return rows;
}

function firstQualifiedReads(rows) {
  const reads = { 1: null, 2: null, 3: null };
  let episodeAsk = null, episodeStart = null, runningLow = null;
  for (const row of rows) {
    if (row.ask !== episodeAsk) { episodeAsk = row.ask; episodeStart = row.ts; }
    if (runningLow === null || row.ask < runningLow) runningLow = row.ask;
    const dwell = row.ts - episodeStart;
    if (row.ask !== runningLow || dwell < MIN_DWELL_SECONDS || row.top_ask_size < 5) continue;
    for (const spread of [1, 2, 3]) if (!reads[spread] && row.spread <= spread) reads[spread] = { ...row, dwell_seconds: dwell, qualification_law: `BID_ASK_LAST_ONE_OBSERVATION; SPREAD_LE_${spread}C; DWELL_GE_10S; POSITIVE_SIZE_GE_5; CURRENT_RUNNING_ASK_LOW` };
    if (reads[1] && reads[2] && reads[3]) break;
  }
  return reads;
}

function firstQualifiedReadsFromFile(source, privateHashes) {
  const file = path.join(privateRoot, "fit-local/ticks", `${source.ticker}.csv.gz`);
  ensure(fs.existsSync(file), `missing private tick source ${source.ticker}`);
  const bytes = fs.readFileSync(file); privateHashes[source.ticker] = { sha256: sha256(bytes), bytes: bytes.length };
  const lines = zlib.gunzipSync(bytes).toString("utf8").split(/\r?\n/), header = lines.shift().split(","), index = Object.fromEntries(header.map((name, i) => [name, i]));
  const reads = { 1: null, 2: null, 3: null }; let episodeAsk = null, episodeStart = null, runningLow = null;
  for (let lineIndex = 0; lineIndex < lines.length; lineIndex += 1) {
    if (!lines[lineIndex]) continue; const values = lines[lineIndex].split(","), ts = parseEt(values[index.ts_et]);
    if (ts === null || ts < source.left_ts || ts > source.right_ts) continue;
    const bids = [], asks = [];
    for (let level = 1; level <= 5; level += 1) {
      const bp = integer(values[index[`bid_${level}`]]), bs = positive(values[index[`bid_${level}_sz`]]), ap = integer(values[index[`ask_${level}`]]), as = positive(values[index[`ask_${level}_sz`]]);
      if (bp !== null && bs !== null) bids.push([bp, bs]); if (ap !== null && as !== null) asks.push([ap, as]);
    }
    bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]); if (!bids.length || !asks.length || bids[0][0] > asks[0][0]) continue;
    const bid = bids[0][0], ask = asks[0][0], spread = ask - bid, topAskSize = asks[0][1];
    if (ask !== episodeAsk) { episodeAsk = ask; episodeStart = ts; }
    if (runningLow === null || ask < runningLow) runningLow = ask;
    const dwell = ts - episodeStart; if (ask !== runningLow || dwell < MIN_DWELL_SECONDS || topAskSize < 5) continue;
    for (const spreadLimit of [1, 2, 3]) if (!reads[spreadLimit] && spread <= spreadLimit) reads[spreadLimit] = {
      ts, ordinal: lineIndex + 2, receipt: `${path.basename(file)}#row-${lineIndex + 2}`, bid, ask, spread,
      top_ask_size: topAskSize, top5_ask_depth: asks.reduce((sum, [, size]) => sum + size, 0), last_traded: integer(values[index.last_trade]), asks,
      dwell_seconds: dwell, qualification_law: `BID_ASK_LAST_ONE_OBSERVATION; SPREAD_LE_${spreadLimit}C; DWELL_GE_10S; POSITIVE_SIZE_GE_5; CURRENT_RUNNING_ASK_LOW`,
    };
    if (reads[1] && reads[2] && reads[3]) break;
  }
  return reads;
}

function walkForwardPredictions(baseRows) {
  return baseRows.map((current) => {
    const training = baseRows.filter((row) => !exactStartExcluded.has(row.event_id)
      && row.event_id !== current.event_id && row.category === current.category && row.price_region === current.price_region
      && Number.isFinite(row.close_ts) && row.close_ts < current.left_ts);
    const fit = selectCellFit(training);
    const estimate = estimateAtRead(fit, current.reads);
    return { ...current, training_event_rows: new Set(training.map((row) => row.event_id)).size, fit, estimate };
  });
}

function authoritySurface(predictions) {
  const cells = [];
  for (const [key, rows] of [...group(predictions, (row) => `${row.category}|${row.price_region}`)].sort(([a], [b]) => a.localeCompare(b))) {
    const evaluated = rows.filter((row) => row.estimate.state === "BOUND" && Number.isInteger(row.audited_close_cents));
    const wrong = evaluated.filter((row) => row.estimate.landing_estimate_cents > row.audited_close_cents);
    const estimatorLosses = evaluated.map((row) => asymmetricLoss(row.audited_close_cents, row.estimate.landing_estimate_cents));
    const naiveLosses = evaluated.map((row) => asymmetricLoss(row.audited_close_cents, row.estimate.read.bid));
    const metrics = {
      population_legs: rows.length,
      validation_n: evaluated.length,
      qualified_read_coverage: rows.length ? evaluated.length / rows.length : 0,
      non_overestimate_rate: evaluated.length ? evaluated.filter((row) => row.estimate.landing_estimate_cents <= row.audited_close_cents).length / evaluated.length : null,
      wrong_n: wrong.length,
      mean_overestimate_when_wrong_cents: wrong.length ? wrong.reduce((sum, row) => sum + row.estimate.landing_estimate_cents - row.audited_close_cents, 0) / wrong.length : 0,
      estimator_asymmetric_loss: estimatorLosses.length ? estimatorLosses.reduce((a, b) => a + b, 0) / estimatorLosses.length : null,
      naive_bid_asymmetric_loss: naiveLosses.length ? naiveLosses.reduce((a, b) => a + b, 0) / naiveLosses.length : null,
      selected_spreads: countBy(evaluated, (row) => row.estimate.spread_cents),
      drift_distribution: distribution(evaluated.map((row) => row.estimate.cell_drift_cents)),
    };
    const decision = authority(metrics, candidateCells.has(key));
    cells.push({ category: key.split("|")[0], price_region: key.split("|")[1], candidate_cell_from_analysis_seat: candidateCells.has(key), ...metrics, authority: decision });
  }
  return cells;
}

function bookAt(rows, ts) { let result = null; for (const row of rows) { if (row.ts <= ts) result = row; else break; } return result; }
function changedLeg(leg, target, actionTs, actionReceipt, actionBook, ticks, reason, overlayReceipt) {
  ensure(Number.isInteger(target) && target >= 1 && target <= 99, `invalid target ${leg.leg_identity}`);
  const placement = { ...(leg.placement || {}), price_cents: target, action_ts: actionTs, action_receipt: actionReceipt, drift_landing_v26: overlayReceipt };
  const immediate = actionBook && actionBook.ask <= target && actionBook.top_ask_size >= 5;
  const later = immediate ? null : findLaterFill(ticks, actionTs, actionReceipt, target);
  if (immediate) return { ...leg, acted: true, credited: true, honest_fill_class: "PROVEN_TAKER_DISPLAYED_OPPOSING_CAPACITY_AT_SUBMISSION", entry_cents: target, action_timestamp_epoch: actionTs, terminal_reason: `${reason}:DISPLAYED_ASK_AT_OR_BELOW_TARGET`, placement, fill: { price_cents: target, quantity: 5, evidence_type: "DISPLAYED_ASK_CAPACITY_AT_SUBMISSION", timestamp_epoch: actionTs, receipt: actionReceipt } };
  if (later) return { ...leg, acted: true, credited: true, honest_fill_class: "PROVEN_MAKER_BY_RESIDENCY_STRICTLY_LATER_QUALIFYING_ASK", entry_cents: target, action_timestamp_epoch: actionTs, terminal_reason: `${reason}:STRICTLY_LATER_QUALIFYING_ASK`, placement, fill: { price_cents: target, quantity: 5, evidence_type: "STRICTLY_LATER_ASK_DWELL_AND_DISPLAYED_CAPACITY", ...later } };
  return { ...leg, acted: true, credited: false, honest_fill_class: "UNPROVEN", entry_cents: null, action_timestamp_epoch: actionTs, terminal_reason: `${reason}:RESTED_UNFILLED`, placement, fill: null };
}

function applyOverlay(events, predictions, authorityCells, sources, privateHashes, v24ByLeg) {
  const predictionByLeg = new Map(predictions.map((row) => [row.leg_identity, row]));
  const authorized = new Set(authorityCells.filter((cell) => cell.authority.authorized).map((cell) => `${cell.category}|${cell.price_region}`));
  const decisions = [], changed = [];
  const output = events.map((event) => {
    const originalLegs = Object.values(event.legs), next = {}, eventChanged = [];
    for (const leg of originalLegs) {
      const prediction = predictionByLeg.get(leg.leg_identity), cellAuthorized = authorized.has(`${leg.category}|${leg.price_region}`);
      const estimate = prediction?.estimate?.state === "BOUND" ? prediction.estimate : null;
      let decision = overlayDecision({ cellAuthorized, incumbentAction: leg.acted ? { price_cents: leg.entry_cents ?? leg.placement?.price_cents } : null, estimate, mirrorRelease: null });
      let nextLeg = leg;
      if (decision.state === "REFINE_EXISTING_AIM" && estimate.read.ts <= leg.action_timestamp_epoch && decision.price_cents < (leg.entry_cents ?? leg.placement.price_cents)) {
        const ticks = loadTicks(sources.get(leg.ticker), privateHashes), actionBook = bookAt(ticks, leg.action_timestamp_epoch);
        const receipt = { power: "REFINE_EXISTING_V23_AIM", estimate, original_price_cents: leg.entry_cents ?? leg.placement.price_cents, selected_price_cents: decision.price_cents, action_book: actionBook, never_block_v23_action: true };
        nextLeg = changedLeg(leg, decision.price_cents, leg.action_timestamp_epoch, leg.placement.action_receipt, actionBook, ticks, "AUTHORIZED_DRIFT_CLAMP", receipt);
      } else if (!leg.acted && cellAuthorized && estimate && v24ByLeg.get(leg.leg_identity)?.v24_role === "MIRROR_PHASED" && v24ByLeg.get(leg.leg_identity)?.acted) {
        const v24 = v24ByLeg.get(leg.leg_identity), actionTs = v24.action_timestamp_epoch, ticks = loadTicks(sources.get(leg.ticker), privateHashes), actionBook = bookAt(ticks, actionTs);
        const sibling = originalLegs.find((row) => row.leg_identity !== leg.leg_identity);
        if (estimate.read.ts <= actionTs && sibling?.credited && sibling.action_timestamp_epoch < actionTs && actionBook) {
          const proposed = Math.floor(estimate.landing_estimate_cents) - 1, capped = Math.min(proposed, 99 - sibling.entry_cents);
          if (capped >= actionBook.bid && capped >= 1) {
            decision = overlayDecision({ cellAuthorized, incumbentAction: null, estimate, mirrorRelease: { state: "RELEASE" } });
            const receipt = { power: "EARLY_MIRROR_HOLD_RELEASE", estimate, own_decline_and_coherent_ordinal: v24.v24_receipt?.release || v24.v24_receipt, pair_cap_cents: 99 - sibling.entry_cents, selected_price_cents: capped, action_book: actionBook, no_elapsed_time_input: true };
            nextLeg = changedLeg(leg, capped, actionTs, v24.placement?.action_receipt || actionBook.receipt, actionBook, ticks, "AUTHORIZED_MIRROR_RELEASE", receipt);
          }
        }
      }
      const equal = rowHash(leg) === rowHash(nextLeg); if (!equal) { changed.push(leg.leg_identity); eventChanged.push(leg.leg_identity); }
      decisions.push({ leg_identity: leg.leg_identity, event_id: event.event_id, category: leg.category, price_region: leg.price_region, cell_authorized: cellAuthorized, qualified_estimate: estimate, overlay_decision: decision, changed: !equal });
      next[leg.leg_id] = nextLeg;
    }
    if (!eventChanged.length) return event;
    const legs = Object.values(next), completed = legs.every((leg) => leg.credited), combined = completed ? legs.reduce((sum, leg) => sum + leg.entry_cents, 0) : null;
    const bothClose = completed && legs.every((leg) => Number.isInteger(leg.audited_close_cents));
    return { ...event, legs: next, completed_pair: completed, combined_entry_cents: combined, pair_under_par: completed && combined < 100, both_legs_strictly_below_audited_close: bothClose && legs.every((leg) => leg.entry_cents < leg.audited_close_cents), joint_objective_pass_audited_close: bothClose && combined < 100 && legs.every((leg) => leg.entry_cents < leg.audited_close_cents), drift_landing_v26_changed_legs: eventChanged };
  });
  return { events: output, decisions, changed: new Set(changed), authorized };
}

function regret(events) {
  const rows = events.flatMap((event) => Object.values(event.legs)).map((leg) => ({ leg_identity: leg.leg_identity, event_id: leg.event_id, category: leg.category, price_region: leg.price_region, credited: leg.credited, entry_cents: leg.credited ? leg.entry_cents : null, maker_floor_cents: leg.maker_floor_cents, traded_low_cents: leg.objective_traded_low_cents, maker_regret_cents: leg.credited && Number.isInteger(leg.maker_floor_cents) ? leg.entry_cents - leg.maker_floor_cents : null, traded_low_gap_cents: leg.credited && Number.isInteger(leg.objective_traded_low_cents) ? leg.entry_cents - leg.objective_traded_low_cents : null, primary_loss: !leg.credited ? `NOT_CREDITED:${leg.terminal_reason}` : leg.entry_cents === leg.maker_floor_cents ? "ZERO_MAKER_FLOOR_REGRET" : leg.entry_cents > leg.maker_floor_cents ? "COMPLETED_OVER_MAKER_FLOOR" : "BETTER_THAN_MAKER_FLOOR" }));
  const parts = [...group(rows, (row) => `${row.category}|${row.price_region}`)].sort(([a], [b]) => a.localeCompare(b)).map(([key, cell]) => ({ category: key.split("|")[0], price_region: key.split("|")[1], n: cell.length, credited: cell.filter((row) => row.credited).length, maker_regret: distribution(cell.map((row) => row.maker_regret_cents)), traded_low_gap: distribution(cell.map((row) => row.traded_low_gap_cents)), primary_loss: countBy(cell, (row) => row.primary_loss) }));
  return { rows, aggregate: { maker_regret: distribution(rows.map((row) => row.maker_regret_cents)), traded_low_gap: distribution(rows.map((row) => row.traded_low_gap_cents)), primary_loss: countBy(rows, (row) => row.primary_loss) }, category_x_price_region: parts };
}

function main() {
  const binding = bindAnalysisSeat();
  const eventPath = path.join(v23Dir, "V23_EVENT_LEDGER.jsonl.gz"), legPath = path.join(v23Dir, "V23_LEG_LEDGER.jsonl.gz"), v24LegPath = path.join(v24Dir, "V24_LEG_LEDGER.jsonl.gz");
  const events = readRows(eventPath), legs = readRows(legPath), v24Legs = readRows(v24LegPath); ensure(events.length === 804 && legs.length === 1608, "V23 conservation");
  const sources = quoteSources(), privateHashes = {}, baseRows = [];
  for (const leg of legs) {
    const source = sources.get(leg.ticker); ensure(source, `missing source ${leg.ticker}`);
    const closeTs = leg.audited_close_ts_utc ? Date.parse(leg.audited_close_ts_utc) / 1000 : null;
    baseRows.push({ leg_identity: leg.leg_identity, event_id: leg.event_id, leg_id: leg.leg_id, ticker: leg.ticker, category: leg.category, price_region: leg.price_region, left_ts: source.left_ts, right_ts: source.right_ts, audited_close_cents: leg.audited_close_cents, close_ts: closeTs, reads: firstQualifiedReadsFromFile(source, privateHashes) });
  }
  const predictions = walkForwardPredictions(baseRows), cells = authoritySurface(predictions), overlay = applyOverlay(events, predictions, cells, sources, privateHashes, new Map(v24Legs.map((leg) => [leg.leg_identity, leg])));
  const outputLegs = overlay.events.flatMap((event) => Object.values(event.legs)); ensure(outputLegs.length === 1608, "V26 leg conservation");
  const closes = new Map(legs.map((leg) => [leg.ticker, { audited_close_cents: leg.audited_close_cents }]));
  const v23Score = scoreVariant("V23_OPERATIVE_BASELINE", events, closes), v26Score = scoreVariant("V26_DRIFT_CORRECTED_LANDING_OVERLAY", overlay.events, closes);
  const v23Regret = regret(events), v26Regret = regret(overlay.events);
  const changedRows = outputLegs.map((leg, index) => ({ leg_identity: leg.leg_identity, V23_sha256: rowHash(legs[index]), V26_sha256: rowHash(leg), equal: rowHash(legs[index]) === rowHash(leg), authorized_cell: overlay.authorized.has(`${leg.category}|${leg.price_region}`) }));
  ensure(changedRows.filter((row) => !row.equal).length === overlay.changed.size, "changed stream census mismatch");
  ensure(changedRows.filter((row) => !row.equal).every((row) => row.authorized_cell), "unauthorized stream changed");
  const l9Ids = new Set(binding.l9.map((row) => row.leg_identity)), beforeL9 = legs.filter((leg) => l9Ids.has(leg.leg_identity)), afterL9 = outputLegs.filter((leg) => l9Ids.has(leg.leg_identity));
  const beforeEvent = new Map(events.map((event) => [event.event_id, event])), afterEvent = new Map(overlay.events.map((event) => [event.event_id, event]));
  ensure(beforeL9.length === 77 && afterL9.length === 77, "L9 identity conservation");
  const miss = outputLegs.map((leg) => ({ leg_identity: leg.leg_identity, event_id: leg.event_id, category: leg.category, price_region: leg.price_region, address: leg.credited ? "CAPTURED" : leg.acted ? "DIED_ACTED_NOT_CREDITED" : "DIED_INCUMBENT_NO_ACTION", V23_L9_ATP_CHALL_51_75: l9Ids.has(leg.leg_identity), overlay_changed: overlay.changed.has(leg.leg_identity), terminal_reason: leg.terminal_reason }));
  fs.mkdirSync(out, { recursive: true });
  fs.writeFileSync(path.join(out, "V26_EVENT_LEDGER.jsonl.gz"), gzipRows(overlay.events));
  fs.writeFileSync(path.join(out, "V26_LEG_LEDGER.jsonl.gz"), gzipRows(outputLegs));
  fs.writeFileSync(path.join(out, "SPREAD_QUALIFIED_READ_LEDGER.jsonl.gz"), gzipRows(predictions));
  fs.writeFileSync(path.join(out, "DRIFT_CELL_AUTHORITY.json"), canonical({ read_law: "BID_ASK_LAST_WITH_SPREAD_DWELL; QUALIFIED_IFF_SPREAD<=S_CELL_AND_DWELL>=10S_AND_DISPLAYED_CAPACITY>=5", fit_law: "LANDING_ESTIMATE=QUALIFIED_BID+TRAINING_ONLY_CELL_DRIFT; S_CELL WALK_FORWARD CHOSEN_FROM 1/2/3C BY Q30_PINBALL_LOSS; MIN_N=30; NO_POOLING", authority_bar: { non_overestimate_rate_min: .70, mean_overestimate_when_wrong_max_cents: 2, must_beat_naive_bid_same_asymmetric_loss: true, qualified_coverage_required: true }, analysis_candidate_cells: [...candidateCells].sort(), authorized_cells: [...overlay.authorized].sort(), cells }));
  fs.writeFileSync(path.join(out, "OVERLAY_DECISION_LEDGER.jsonl.gz"), gzipRows(overlay.decisions));
  fs.writeFileSync(path.join(out, "V23_TO_V26_DIFFERENTIAL.jsonl.gz"), gzipRows(changedRows));
  fs.writeFileSync(path.join(out, "DIFFERENTIAL_RECEIPT.json"), canonical({ overlay_law: "V23_BYTE_IDENTICAL_WHERE_AUTHORITY_ABSENT; OVERLAY_NEVER_BLOCKS_VETOES_OR_REPLACES_A_V23_ACTION", V23_event_sha256: hashFile(eventPath), V26_event_sha256: hashFile(path.join(out, "V26_EVENT_LEDGER.jsonl.gz")), V23_leg_sha256: hashFile(legPath), V26_leg_sha256: hashFile(path.join(out, "V26_LEG_LEDGER.jsonl.gz")), authorized_cells: [...overlay.authorized].sort(), changed_leg_streams: overlay.changed.size, identical_leg_streams: 1608 - overlay.changed.size, unauthorized_changed_streams: changedRows.filter((row) => !row.equal && !row.authorized_cell).length }));
  fs.writeFileSync(path.join(out, "FRONTIER.json"), canonical({ fixed_denominator: 804, JOINT_law: "COMPLETED_AND_SUM_LT_100_AND_EACH_LEG_ENTRY_STRICTLY_BELOW_OWN_AUDITED_CLOSE", V23: v23Score, V26: v26Score }));
  fs.writeFileSync(path.join(out, "REGRET_GAUGE.json"), canonical({ law: "FILL_MINUS_CORRECTED_MAKER_FLOOR_AND_OBJECTIVE_TRADED_LOW; NEVER_PLACED_NUMERIC_REGRET_NULL", V23: { aggregate: v23Regret.aggregate, category_x_price_region: v23Regret.category_x_price_region }, V26: { aggregate: v26Regret.aggregate, category_x_price_region: v26Regret.category_x_price_region } }));
  fs.writeFileSync(path.join(out, "MISS_LEDGER_1608.jsonl.gz"), gzipRows(miss));
  fs.writeFileSync(path.join(out, "MISS_LEDGER_CONSERVATION.json"), canonical({ denominator: 1608, rows: miss.length, unique_leg_identities: new Set(miss.map((row) => row.leg_identity)).size, addresses: countBy(miss, (row) => row.address), conserved: true }));
  fs.writeFileSync(path.join(out, "TOP_MISS_CELL_L9_ATP_CHALL_51_75.json"), canonical({ source_commit: analysisCommit, source_path: analysisMissRel, grain: "L9_carry|FIXABLE|ATP_CHALL|51_75", before: { legs: 77, credited_first_legs: beforeL9.filter((leg) => leg.credited).length, pair_completed: beforeL9.filter((leg) => beforeEvent.get(leg.event_id)?.completed_pair).length, unresolved_carry_losses: beforeL9.filter((leg) => !beforeEvent.get(leg.event_id)?.completed_pair).length }, after: { legs: 77, credited_first_legs: afterL9.filter((leg) => leg.credited).length, pair_completed: afterL9.filter((leg) => afterEvent.get(leg.event_id)?.completed_pair).length, unresolved_carry_losses: afterL9.filter((leg) => !afterEvent.get(leg.event_id)?.completed_pair).length, changed_streams: afterL9.filter((leg) => overlay.changed.has(leg.leg_identity)).length }, identities: [...l9Ids].sort() }));
  fs.writeFileSync(path.join(out, "CONTROL_BINDING.json"), canonical({ incumbent: "V23", incumbent_joint: 45, incumbent_carried: 88, analysis_seat_commit: analysisCommit, analysis_landing_path: analysisLandingRel, analysis_landing_sha256: sha256(binding.landing), analysis_miss_path: analysisMissRel, analysis_miss_sha256: sha256(binding.miss), exact_start_training_exclusions: [...exactStartExcluded].sort(), candidate_authority_cells: [...candidateCells].sort(), drift_sign_pooling: false, elapsed_time_pair_input: false }));
  fs.writeFileSync(path.join(out, "FORBIDDEN_ACCESS_RECEIPT.json"), canonical({ development_only: true, population_events: 804, holdout: false, live: false, network: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, Window2: false, forecast_regression: false, clock_trigger: false }));
  fs.writeFileSync(path.join(out, "REPORT.md"), `# V26 drift-corrected landing overlay\n\nV26 preserves V23 byte-identically wherever the causal spread-qualified drift organ lacks authority. Each read is one bid/ask/last observation with spread and dwell; it is silent unless spread is within the walk-forward fitted 1/2/3-cent cell law, dwell is at least ten seconds, and displayed ask capacity is at least five. The organ is qualified bid plus one training-only cell drift. Authorized cells may only lower an already-authorized V23 aim or release a mirror HOLD after its own coherent decline ordinal; neither power may block, veto, or replace a V23 action.\n\nSee DRIFT_CELL_AUTHORITY.json, DIFFERENTIAL_RECEIPT.json, FRONTIER.json, REGRET_GAUGE.json, MISS_LEDGER_1608.jsonl.gz, and TOP_MISS_CELL_L9_ATP_CHALL_51_75.json.\n`);
  const sourceFiles = [eventPath, legPath, v24LegPath, quotePath, path.join(repo, "arb-executor/analysis/window1_drift_landing_overlay_v26_policy.js"), __filename, path.join(repo, "arb-executor/tests/test_window1_drift_landing_overlay_v26.js")];
  fs.writeFileSync(path.join(out, "SOURCE_HASH_MANIFEST.json"), canonical({ committed: Object.fromEntries(sourceFiles.map((file) => [path.relative(repo, file).replaceAll("\\", "/"), { sha256: hashFile(file), bytes: fs.statSync(file).size }])), analysis_seat: { commit: analysisCommit, landing: { path: analysisLandingRel, sha256: sha256(binding.landing), bytes: binding.landing.length }, miss: { path: analysisMissRel, sha256: sha256(binding.miss), bytes: binding.miss.length } }, private_tick_sources: privateHashes }));
  if (compare1 && compare2) fs.writeFileSync(path.join(out, "DETERMINISM_RECEIPT.json"), canonical(compareBuilds(path.resolve(compare1), path.resolve(compare2))));
  const names = fs.readdirSync(out).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  fs.writeFileSync(path.join(out, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(names.map((name) => [name, { sha256: hashFile(path.join(out, name)), bytes: fs.statSync(path.join(out, name)).size }])) }));
  process.stdout.write(canonical({ status: "BUILT", V23: v23Score.aggregate, V26: v26Score.aggregate, authorized_cells: [...overlay.authorized].sort(), changed_streams: overlay.changed.size, L9: JSON.parse(fs.readFileSync(path.join(out, "TOP_MISS_CELL_L9_ATP_CHALL_51_75.json"), "utf8")) }));
}

if (require.main === module) main();
module.exports = { firstQualifiedReads, walkForwardPredictions, authoritySurface, applyOverlay };
