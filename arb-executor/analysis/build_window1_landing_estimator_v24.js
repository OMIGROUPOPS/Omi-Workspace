#!/usr/bin/env node
"use strict";

const childProcess = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { addDerivedFields, scoreVariant } = require("./build_window1_pair_cap_v23.js");
const {
  DWELL_SECONDS,
  MIN_TRAINING_N,
  QUANTITY,
  estimateLanding,
  findLaterFill,
  mirrorAim,
  pairCap,
  pathFamily,
  readSideDecision,
} = require("./window1_landing_estimator_v24_policy.js");

const argv = process.argv.slice(2);
const arg = (name, fallback) => { const i = argv.indexOf(name); return i >= 0 ? argv[i + 1] : fallback; };
const repo = path.resolve(arg("--repo", "."));
const privateRoot = path.resolve(arg("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const out = path.resolve(arg("--output", path.join(repo, ".claude/window1_live_v4_replay/landing_estimator_phased_arming_v24_20260804")));
const compare1 = arg("--compare-run1", null), compare2 = arg("--compare-run2", null);
const v23Dir = path.join(repo, ".claude/window1_live_v4_replay/pair_cap_v23_audited_close_20260804");
const aEventPath = path.join(repo, ".claude/window1_live_v4_replay/isolated_fix_a_anchor_freshness_v20_20260804/POPULATION_EVENT_LEDGER.jsonl.gz");
const quotePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const aggressorPath = path.join(repo, ".claude/window1_live_v4_replay/aggressor_ceiling_census_20260801/PER_LEG_AGGRESSOR_CENSUS.jsonl.gz");
const libraryPath = path.join(repo, ".claude/window1_live_v4_replay/interim_shape_v13_fit_20260803/INTERIM_SHAPE_LIBRARY_V13.json");
const timeFlowPath = path.join(repo, ".claude/window1_live_v4_replay/second_leg_x_pricer_v17_20260803/TIME_AND_FLOW_ROW_LEDGER.jsonl.gz");
const xLibraryPath = path.join(repo, ".claude/window1_live_v4_replay/second_leg_x_pricer_fit_v17_20260803/SECOND_LEG_X_CONDITIONAL_LIBRARY.json");
const bellPath = path.join(repo, ".claude/window1_live_v4_replay/actual_bell_refit_20260729/ACTUAL_BELL_REFIT.json");
const auditCommit = "50ce0f4940c461cf0b6fa1b79000d96b335cd601";
const auditCsvRel = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/INDEPENDENT_CLOSE_AUDIT_1608.csv";
const exactStartExcluded = new Set([
  "KXATPCHALLENGERMATCH-26JUL19HURBIG",
  "KXATPCHALLENGERMATCH-26JUL19NIKVRB",
  "KXATPMATCH-26JUL12LAJVAN",
  "KXWTACHALLENGERMATCH-26JUL16BRAVED",
  "KXWTAMATCH-26JUL20KORJIM",
]);
const tickCache = new Map();

function ensure(ok, message) { if (!ok) throw new Error(message); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function gzipRows(rows) { return zlib.gzipSync(Buffer.from(`${rows.map(JSON.stringify).join("\n")}\n`), { level: 9, mtime: 0 }); }
function readRows(file) { const text = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim(); return text ? text.split(/\r?\n/).map(JSON.parse) : []; }
function parseCsv(text) { const lines = text.trimEnd().split(/\r?\n/), header = lines.shift().split(","); return lines.filter(Boolean).map((line, index) => ({ row: Object.fromEntries(line.split(",").map((v, i) => [header[i], v])), ordinal: index + 2 })); }
function integer(value) { const n = Number(value); return Number.isInteger(n) ? n : null; }
function positive(value) { const n = Number(value); return Number.isFinite(n) && n > 0 ? n : null; }
function group(rows, fn) { const out = new Map(); for (const row of rows) { const key = fn(row); if (!out.has(key)) out.set(key, []); out.get(key).push(row); } return out; }
function countBy(rows, fn) { const out = {}; for (const row of rows) { const k = String(fn(row)); out[k] = (out[k] || 0) + 1; } return Object.fromEntries(Object.entries(out).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }
function quantile(values, p) { const xs = values.filter(Number.isFinite).sort((a, b) => a - b); return xs.length ? xs[Math.floor((xs.length - 1) * p)] : null; }
function dist(values) { const xs = values.filter(Number.isFinite); return { denominator: values.length, numeric_n: xs.length, null_n: values.length - xs.length, min: xs.length ? Math.min(...xs) : null, p25: quantile(xs, .25), median: quantile(xs, .5), p75: quantile(xs, .75), p90: quantile(xs, .9), max: xs.length ? Math.max(...xs) : null }; }
function parseEt(value) { const m = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/); if (!m) return null; let h = Number(m[4]); if (m[7] === "AM" && h === 12) h = 0; if (m[7] === "PM" && h !== 12) h += 12; return Date.parse(`${m[1]}-${m[2]}-${m[3]}T${String(h).padStart(2, "0")}:${m[5]}:${m[6]}-04:00`) / 1000; }

function closeAudit() {
  childProcess.execFileSync("git", ["cat-file", "-e", `${auditCommit}^{commit}`], { cwd: repo });
  const bytes = childProcess.execFileSync("git", ["show", `${auditCommit}:${auditCsvRel}`], { cwd: repo, maxBuffer: 64 * 1024 * 1024 });
  ensure(sha256(bytes) === "51d542d9c1f18c6b30b6bb5e8f458d9cf3adeebf1895399f8f7b2ba416836303", "audited close hash mismatch");
  const rows = parseCsv(bytes.toString("utf8")).map(({ row }) => ({
    ticker: row.ticker,
    event_id: row.event,
    audited_close_cents: row.audited_close_cents === "" ? null : integer(row.audited_close_cents),
    audited_close_ts_utc: row.audited_close_ts_utc || null,
    close_ts: row.audited_close_ts_utc ? Date.parse(row.audited_close_ts_utc) / 1000 : null,
    close_aggressor_side: row.close_aggressor_side || null,
    seconds_before_right_edge: row.seconds_before_right_edge === "" ? null : Number(row.seconds_before_right_edge),
  }));
  ensure(rows.length === 1608, `close rows ${rows.length}`);
  return { rows, bytes };
}

function loadTicks(source, hashes) {
  const file = path.join(privateRoot, "fit-local/ticks", `${source.ticker}.csv.gz`);
  ensure(fs.existsSync(file), `missing private tick source ${source.ticker}`);
  if (tickCache.has(source.ticker)) return tickCache.get(source.ticker);
  const bytes = fs.readFileSync(file);
  hashes[source.ticker] = { sha256: sha256(bytes), bytes: bytes.length };
  const rows = [];
  for (const { row: raw, ordinal } of parseCsv(zlib.gunzipSync(bytes).toString("utf8"))) {
    const ts = parseEt(raw.ts_et);
    if (ts === null || ts < source.left_ts || ts > source.right_ts) continue;
    const bids = [], asks = [];
    for (let i = 1; i <= 5; i += 1) {
      const bp = integer(raw[`bid_${i}`]), bs = positive(raw[`bid_${i}_sz`]), ap = integer(raw[`ask_${i}`]), as = positive(raw[`ask_${i}_sz`]);
      if (bp !== null && bs !== null) bids.push([bp, bs]);
      if (ap !== null && as !== null) asks.push([ap, as]);
    }
    bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]);
    if (!bids.length || !asks.length || bids[0][0] > asks[0][0]) continue;
    rows.push({ ts, ordinal, receipt: `${path.basename(file)}#row-${ordinal}`, bid: bids[0][0], ask: asks[0][0], asks });
  }
  rows.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  tickCache.set(source.ticker, rows);
  return rows;
}

function currentAt(rows, ts) {
  let selected = null;
  for (const row of rows) { if (row.ts <= ts) selected = row; else break; }
  return selected;
}

function shapeIds(placement) {
  const ids = new Set(placement?.macro_surviving_shapes || []);
  for (const row of placement?.surviving_shapes || []) if (row.shape_id) ids.add(row.shape_id);
  return [...ids].sort();
}

function mirrorShapeIds(readPlacement, mirrorLeg) {
  const text = JSON.stringify({ tuples: readPlacement?.pair_shape_tuples || [], couples: readPlacement?.pair_interim_v18?.pair_couple_ids || [] });
  const ids = [...new Set(text.match(/[A-Z]+_(?:MAIN|CHALL)_(?:26_50|51_75|le25|ge75)_INTERIM_PATH_\d+_ORD_\d+_\d+/g) || [])];
  return ids.filter((id) => id.startsWith(`${mirrorLeg.category}_`) && id.includes(`_${mirrorLeg.price_region}_`)).sort();
}

function firstResolution(event) {
  const rows = Object.values(event.legs).filter((leg) => leg.placement && Number.isFinite(leg.action_timestamp_epoch));
  return rows.sort((a, b) => a.action_timestamp_epoch - b.action_timestamp_epoch || a.leg_id.localeCompare(b.leg_id))[0] || null;
}

function clocks(ts, source, bell) {
  return {
    timestamp_epoch: ts,
    t_minus_scheduled_seconds: Number.isFinite(source?.scheduled_start_ts) ? source.scheduled_start_ts - ts : null,
    t_minus_actual_bell_seconds: Number.isFinite(bell?.exact_bell_ts) ? bell.exact_bell_ts - ts : null,
  };
}

function fitXRelation() {
  const lib = JSON.parse(fs.readFileSync(xLibraryPath, "utf8"));
  const rows = Object.values(lib.cells).flatMap((cell) => cell.training_rows).filter((row) => !row.fit_excluded && Number.isFinite(row.first_fill_x_cents) && Number.isFinite(row.sibling_eventual_ask_floor_cents));
  const unique = [...new Map(rows.map((row) => [row.event_id, row])).values()];
  const mx = unique.reduce((s, r) => s + r.first_fill_x_cents, 0) / unique.length;
  const my = unique.reduce((s, r) => s + r.sibling_eventual_ask_floor_cents, 0) / unique.length;
  const num = unique.reduce((s, r) => s + (r.first_fill_x_cents - mx) * (r.sibling_eventual_ask_floor_cents - my), 0);
  const den = unique.reduce((s, r) => s + (r.first_fill_x_cents - mx) ** 2, 0);
  const slope = num / den, intercept = my - slope * mx;
  return { source_rows: rows.length, unique_events: unique.length, intercept, slope, law: "DIAGNOSTIC_CROSS_CHECK_ONLY; NEVER_TARGET_OR_VETO" };
}

function releaseFromOwnDecline(rows, resolutionTs, shapes, shapeMap) {
  const initial = currentAt(rows, resolutionTs);
  if (!initial) return { state: "ABSTAIN", reason: "MIRROR_NO_FORMED_BOOK_AT_PAIR_RESOLUTION" };
  const usable = shapes.map((id) => shapeMap.get(id)).filter((shape) => shape?.usable_for_signing);
  if (!usable.length) return { state: "ABSTAIN", reason: "MIRROR_ORDINAL_UNAVAILABLE", initial_book: initial };
  let episodeAsk = null, episodeStart = null, low = initial.ask, descents = 0;
  for (const row of rows) {
    if (row.ts <= resolutionTs) continue;
    if (row.ask !== episodeAsk) { episodeAsk = row.ask; episodeStart = row.ts; }
    const capacity = row.asks.filter(([price]) => price <= row.ask).reduce((s, [, size]) => s + size, 0);
    if (row.ts - episodeStart < DWELL_SECONDS || capacity < QUANTITY) continue;
    if (row.ask < low) { low = row.ask; descents += 1; }
    const allFloor = usable.every((shape) => descents >= shape.descent_to_final_reachable_low.max);
    if (descents > 0 && allFloor) return { state: "RELEASE", reason: "OWN_BOOK_DECLINE_REACHED_ALL_SURVIVING_COHERENT_ORDINALS", row, observed_qualified_descents: descents, initial_book: initial, surviving_shape_ids: usable.map((s) => s.shape_id) };
  }
  return { state: "HOLD", reason: "OWN_BOOK_DECLINE_ORDINAL_NEVER_RESOLVED_BEFORE_WINDOW_END", observed_qualified_descents: descents, initial_book: initial, surviving_shape_ids: usable.map((s) => s.shape_id) };
}

function landingTrainingSamples(v23Events, closes) {
  const rows = [];
  for (const event of v23Events) for (const leg of Object.values(event.legs)) {
    const book = leg.placement?.pre_action_evidence?.own?.current_book, close = closes.get(leg.ticker), family = pathFamily(shapeIds(leg.placement));
    if (exactStartExcluded.has(event.event_id) || !book || !family || !Number.isInteger(close?.audited_close_cents) || !Number.isFinite(close?.close_ts)) continue;
    rows.push({ event_id: event.event_id, leg_identity: leg.leg_identity, ticker: leg.ticker, category: leg.category, path_family: family, decision_ts: leg.action_timestamp_epoch, decision_live_ask_cents: book.ask, close_ts: close.close_ts, audited_close_cents: close.audited_close_cents, close_minus_live_ask_cents: close.audited_close_cents - book.ask });
  }
  return rows.sort((a, b) => a.close_ts - b.close_ts || a.leg_identity.localeCompare(b.leg_identity));
}

function blankLeg(leg, role, reason, receipt) {
  return { ...leg, acted: false, credited: false, honest_fill_class: "UNPROVEN", entry_cents: null, action_timestamp_epoch: null, terminal_reason: reason, fill: null, placement: null, v24_role: role, v24_receipt: receipt };
}

function replay(events, samples, closes, quoteSources, unresolved, shapeMap, xRelation, sourceHashes, bellMap) {
  const decisions = [], miss = [];
  const output = events.map((event) => {
    const oldLegs = Object.values(event.legs), readOld = firstResolution(event);
    if (!readOld) {
      const legs = Object.fromEntries(oldLegs.map((leg) => {
        const receipt = { event_id: event.event_id, leg_identity: leg.leg_identity, role: "UNASSIGNED", state: "ABSTAIN", reason: "SHAPE_PAIR_READ_NEVER_RESOLVED" };
        decisions.push(receipt); miss.push({ ...receipt, category: leg.category, price_region: leg.price_region, address: "DIED_SHAPE_PAIR_READ_NEVER_RESOLVED", layer: "PAIR_MACRO" });
        return [leg.leg_id, blankLeg(leg, "UNASSIGNED", receipt.reason, receipt)];
      }));
      return { ...event, legs, v24: { state: "NO_PAIR_RESOLUTION" } };
    }
    const mirrorOld = oldLegs.find((leg) => leg.leg_id !== readOld.leg_id);
    ensure(mirrorOld, `missing mirror ${event.event_id}`);
    const resolutionTs = readOld.action_timestamp_epoch;
    const readBook = readOld.placement.pre_action_evidence.own.current_book;
    const readFamily = pathFamily(shapeIds(readOld.placement));
    const readEstimate = estimateLanding(samples, { event_id: event.event_id, category: readOld.category, path_family: readFamily, decision_ts: resolutionTs, current_ask_cents: readBook.ask, identity_unresolved: false });
    const readDecision = readSideDecision({ liveBid: readBook.bid, liveAsk: readBook.ask, displayedAskSize: readBook.top_ask_size, estimate: readEstimate });
    const readSource = quoteSources.get(readOld.ticker), readClock = clocks(resolutionTs, readSource, bellMap.get(readOld.ticker));
    const readReceipt = { event_id: event.event_id, leg_identity: readOld.leg_identity, role: "READ_PRE_DECLINE", pair_resolution: readClock, live_book: readBook, path_family: readFamily, landing_estimate: readEstimate, decision: readDecision, elapsed_time_inputs: [] };
    let readLeg;
    if (readDecision.state === "PLACE") {
      readLeg = { ...readOld, acted: true, credited: true, honest_fill_class: "PROVEN_TAKER_DISPLAYED_OPPOSING_CAPACITY_AT_SUBMISSION", entry_cents: readBook.ask, action_timestamp_epoch: resolutionTs, terminal_reason: readDecision.reason, fill: { price_cents: readBook.ask, quantity: 5, evidence_type: "DISPLAYED_ASK_CAPACITY_AT_SUBMISSION", timestamp_epoch: resolutionTs, receipt: readBook.receipt }, v24_role: "READ_PRE_DECLINE", v24_receipt: readReceipt };
    } else if (readDecision.state === "REST") {
      const readRows = loadTicks(readSource, sourceHashes);
      const later = findLaterFill(readRows, resolutionTs, readBook.receipt, readDecision.price_cents);
      readLeg = { ...readOld, acted: true, credited: Boolean(later), honest_fill_class: later ? "PROVEN_MAKER_BY_RESIDENCY" : "UNPROVEN", entry_cents: later ? readDecision.price_cents : null, action_timestamp_epoch: resolutionTs, terminal_reason: later ? "STRICTLY_LATER_QUALIFYING_ASK" : "READ_SIDE_REST_NEVER_CREDITED", fill: later ? { price_cents: readDecision.price_cents, quantity: 5, evidence_type: "STRICTLY_LATER_QUALIFYING_ASK", ...later } : null, v24_role: "READ_PRE_DECLINE", v24_receipt: readReceipt };
    } else readLeg = blankLeg(readOld, "READ_PRE_DECLINE", readDecision.reason, readReceipt);
    decisions.push(readReceipt);
    const readAddress = readLeg.credited ? "CAPTURED" : readEstimate.state !== "BOUND" ? `DIED_${readEstimate.reason}` : readDecision.reason === "LIVE_ASK_NOT_STRICTLY_BELOW_Q50_LANDING" ? "DIED_OWN_FLOOR_NOT_STRICTLY_BELOW_Q50_LANDING" : "DIED_READ_SIDE_CAPACITY_OR_FUTURE_REACH_UNPROVEN";
    miss.push({ event_id: event.event_id, leg_identity: readOld.leg_identity, category: readOld.category, price_region: readOld.price_region, role: "READ_PRE_DECLINE", address: readAddress, layer: readLeg.credited ? "CAPTURED" : "LANDING_OR_EXECUTION", evidence: readReceipt });

    const mirrorIds = mirrorShapeIds(readOld.placement, mirrorOld), mirrorFamily = pathFamily(mirrorIds);
    const mirrorSource = quoteSources.get(mirrorOld.ticker), mirrorAtResolution = readOld.placement.pre_action_evidence.sibling.current_book;
    const mirrorEstimate = estimateLanding(samples, { event_id: event.event_id, category: mirrorOld.category, path_family: mirrorFamily, decision_ts: resolutionTs, current_ask_cents: mirrorAtResolution.ask, identity_unresolved: unresolved.has(event.event_id) });
    const armed = mirrorAim(mirrorEstimate);
    const hasUsableMirrorOrdinal = mirrorIds.some((id) => shapeMap.get(id)?.usable_for_signing);
    const mirrorRows = armed.state === "HOLD" && hasUsableMirrorOrdinal ? loadTicks(mirrorSource, sourceHashes) : [];
    const release = armed.state !== "HOLD" ? { state: "ABSTAIN", reason: armed.reason }
      : hasUsableMirrorOrdinal ? releaseFromOwnDecline(mirrorRows, resolutionTs, mirrorIds, shapeMap)
        : { state: "ABSTAIN", reason: "MIRROR_ORDINAL_UNAVAILABLE" };
    let mirrorLeg, capDecision = null, releaseClock = null, xCheck = null;
    if (release.state === "RELEASE" && readLeg.credited) {
      releaseClock = clocks(release.row.ts, mirrorSource, bellMap.get(mirrorOld.ticker));
      capDecision = pairCap({ aimCents: armed.aim_cents, firstFillCents: readLeg.entry_cents, liveBid: release.row.bid, liveAsk: release.row.ask });
      xCheck = { first_fill_x_cents: readLeg.entry_cents, predicted_sibling_floor_cents: xRelation.intercept + xRelation.slope * readLeg.entry_cents, authority: xRelation.law, changes_aim_or_decision: false };
      if (capDecision.state === "PLACE") {
        const capacity = release.row.asks.filter(([price]) => price <= capDecision.selected_cents).reduce((s, [, size]) => s + size, 0);
        if (release.row.ask <= capDecision.selected_cents && capacity >= QUANTITY) {
          mirrorLeg = { ...mirrorOld, acted: true, credited: true, honest_fill_class: "PROVEN_TAKER_DISPLAYED_OPPOSING_CAPACITY_AT_SUBMISSION", entry_cents: release.row.ask, action_timestamp_epoch: release.row.ts, terminal_reason: "OWN_DECLINE_RELEASE_THEN_DISPLAYED_ASK_TAKE", fill: { price_cents: release.row.ask, quantity: 5, evidence_type: "DISPLAYED_ASK_CAPACITY_AT_SUBMISSION", timestamp_epoch: release.row.ts, receipt: release.row.receipt }, v24_role: "MIRROR_PHASED", placement: { price_cents: capDecision.selected_cents, action_ts: release.row.ts, action_receipt: release.row.receipt } };
        } else {
          const later = findLaterFill(mirrorRows, release.row.ts, release.row.receipt, capDecision.selected_cents);
          mirrorLeg = { ...mirrorOld, acted: true, credited: Boolean(later), honest_fill_class: later ? "PROVEN_MAKER_BY_RESIDENCY" : "UNPROVEN", entry_cents: later ? capDecision.selected_cents : null, action_timestamp_epoch: release.row.ts, terminal_reason: later ? "PHASED_MIRROR_STRICTLY_LATER_QUALIFYING_ASK" : "PHASED_MIRROR_PLACED_NOT_CREDITED", fill: later ? { price_cents: capDecision.selected_cents, quantity: 5, evidence_type: "STRICTLY_LATER_QUALIFYING_ASK", ...later } : null, v24_role: "MIRROR_PHASED", placement: { price_cents: capDecision.selected_cents, action_ts: release.row.ts, action_receipt: release.row.receipt } };
        }
      } else mirrorLeg = blankLeg(mirrorOld, "MIRROR_PHASED", capDecision.reason, null);
    } else {
      const reason = !readLeg.credited ? "PAIR_CAP_FIRST_FILL_UNAVAILABLE" : release.reason;
      mirrorLeg = blankLeg(mirrorOld, "MIRROR_PHASED", reason, null);
    }
    const mirrorReceipt = { event_id: event.event_id, leg_identity: mirrorOld.leg_identity, role: "MIRROR_PHASED", pair_resolution: clocks(resolutionTs, mirrorSource, bellMap.get(mirrorOld.ticker)), live_book_at_resolution: mirrorAtResolution, mirror_shape_ids: mirrorIds, path_family: mirrorFamily, landing_estimate: mirrorEstimate, armed, release, release_clock: releaseClock, pair_cap: capDecision, V17_X_relation_cross_check: xCheck, no_clock_inputs: true, elapsed_time_inputs: [] };
    mirrorLeg.v24_receipt = mirrorReceipt; decisions.push(mirrorReceipt);
    let mirrorAddress = "CAPTURED";
    if (!mirrorLeg.credited) {
      if (mirrorEstimate.reason === "LANDING_IDENTITY_UNRESOLVED_339") mirrorAddress = "DIED_LANDING_ESTIMATOR_IDENTITY_UNRESOLVED";
      else if (mirrorEstimate.state !== "BOUND") mirrorAddress = `DIED_${mirrorEstimate.reason}`;
      else if (!readLeg.credited) mirrorAddress = "DIED_PAIR_CAP_FIRST_FILL_UNAVAILABLE";
      else if (release.reason === "MIRROR_ORDINAL_UNAVAILABLE") mirrorAddress = "DIED_MIRROR_ORDINAL_UNAVAILABLE";
      else if (release.state === "HOLD") mirrorAddress = "DIED_MIRROR_DECLINE_OR_SHAPE_STATE_UNRESOLVED";
      else if (capDecision?.state === "ABSTAIN") mirrorAddress = "DIED_PAIR_CAP_UNREACHABLE_NO_CHASE";
      else mirrorAddress = "DIED_PLACED_NOT_CREDITED";
    }
    miss.push({ event_id: event.event_id, leg_identity: mirrorOld.leg_identity, category: mirrorOld.category, price_region: mirrorOld.price_region, role: "MIRROR_PHASED", address: mirrorAddress, layer: mirrorLeg.credited ? "CAPTURED" : "LANDING_PHASE_ORDINAL_CAP_OR_EXECUTION", evidence: mirrorReceipt });
    const legs = { [readLeg.leg_id]: readLeg, [mirrorLeg.leg_id]: mirrorLeg };
    return { ...event, legs, v24: { state: "PAIR_RESOLVED", read_leg: readLeg.leg_identity, mirror_leg: mirrorLeg.leg_identity, resolution_timestamp_epoch: resolutionTs } };
  });
  ensure(miss.length === 1608 && new Set(miss.map((r) => r.leg_identity)).size === 1608, "MISS ledger conservation failed");
  return { events: output, decisions, miss };
}

function regretRows(events) {
  return events.flatMap((event) => Object.values(event.legs).map((leg) => ({
    leg_identity: leg.leg_identity, event_id: event.event_id, category: event.category, price_region: leg.price_region, credited: leg.credited,
    entry_cents: leg.credited ? leg.entry_cents : null, corrected_maker_floor_cents: leg.maker_floor_cents, print_floor_cents: leg.objective_traded_low_cents,
    maker_floor_regret_cents: leg.credited && Number.isInteger(leg.maker_floor_cents) ? leg.entry_cents - leg.maker_floor_cents : null,
    print_floor_regret_cents: leg.credited && Number.isInteger(leg.objective_traded_low_cents) ? leg.entry_cents - leg.objective_traded_low_cents : null,
    primary_loss: leg.credited ? (leg.entry_minus_maker_floor_cents === 0 ? "ZERO_MAKER_FLOOR_REGRET" : "CREDITED_NONZERO_REGRET") : `NEVER_CAPTURED:${leg.terminal_reason}`,
  })));
}

function compareBuilds(a, b) {
  const excluded = new Set(["ARTIFACT_HASH_MANIFEST.json", "DETERMINISM_RECEIPT.json"]);
  const aa = fs.readdirSync(a).filter((x) => !excluded.has(x)).sort(), bb = fs.readdirSync(b).filter((x) => !excluded.has(x)).sort();
  ensure(JSON.stringify(aa) === JSON.stringify(bb), "build file census mismatch");
  const bad = aa.filter((name) => hashFile(path.join(a, name)) !== hashFile(path.join(b, name)));
  ensure(!bad.length, `determinism mismatch ${bad.join(",")}`);
  return { clean_builds: 2, compared_files: aa.length, byte_identical: true, mismatches: [] };
}

function main() {
  const required = [path.join(v23Dir, "V23_EVENT_LEDGER.jsonl.gz"), aEventPath, quotePath, aggressorPath, libraryPath, timeFlowPath, xLibraryPath, bellPath];
  for (const file of required) ensure(fs.existsSync(file), `missing ${file}`);
  const audit = closeAudit(), closes = new Map(audit.rows.map((r) => [r.ticker, r]));
  const quoteRows = parseCsv(fs.readFileSync(quotePath, "utf8")).map(({ row }) => ({ ticker: row.ticker, left_ts: Number(row.left_ts), right_ts: Number(row.right_ts), scheduled_start_ts: Number(row.scheduled_start_ts) }));
  const quoteSources = new Map(quoteRows.map((r) => [r.ticker, r])); ensure(quoteRows.length === 1608, "quote source conservation");
  const aggressorRows = readRows(aggressorPath), aggressors = new Map(aggressorRows.map((r) => [r.ticker, r]));
  const library = JSON.parse(fs.readFileSync(libraryPath, "utf8")), shapeMap = new Map(Object.values(library.groups).flatMap((g) => g.shapes).map((s) => [s.shape_id, s]));
  const timeRows = readRows(timeFlowPath), unresolved = new Set(timeRows.filter((r) => r.climber_first === "UNRESOLVED_DIRECTION").map((r) => r.event_id)); ensure(unresolved.size === 339, `identity unresolved ${unresolved.size}`);
  const bell = JSON.parse(fs.readFileSync(bellPath, "utf8")), bellMap = new Map(bell.leg_rows.map((r) => [r.ticker, r]));
  const v23 = readRows(path.join(v23Dir, "V23_EVENT_LEDGER.jsonl.gz")); ensure(v23.length === 804, "V23 D");
  const aEvents = readRows(aEventPath); ensure(aEvents.length === 804, "A D");
  const samples = landingTrainingSamples(aEvents, closes); ensure(samples.every((r) => !exactStartExcluded.has(r.event_id)), "five exact-start leak in fit");
  const xRelation = fitXRelation(), privateHashes = {};
  const raw = replay(v23, samples, closes, quoteSources, unresolved, shapeMap, xRelation, privateHashes, bellMap);
  const v24 = addDerivedFields(raw.events, closes, aggressors);
  const baseline = scoreVariant("V23_OPERATIVE_BASELINE", v23, closes), scored = scoreVariant("V24_LANDING_ESTIMATOR_PHASED_ARMING", v24, closes);
  ensure(baseline.aggregate.joint_objective_pairs === 45 && baseline.aggregate.strict_carried_pairs === 88, `V23 ruling mismatch ${JSON.stringify(baseline.aggregate)}`);
  const nonRegression = { joint_floor: 45, carried_ceiling: 88, V24_joint: scored.aggregate.joint_objective_pairs, V24_carried: scored.aggregate.strict_carried_pairs, joint_pass: scored.aggregate.joint_objective_pairs >= 45, carried_pass: scored.aggregate.strict_carried_pairs <= 88 };
  const regret = regretRows(v24), regretPartitions = [...group(regret, (r) => `${r.category}|${r.price_region}`)].sort(([a], [b]) => a.localeCompare(b)).map(([key, rows]) => ({ category: key.split("|")[0], price_region: key.split("|")[1], n: rows.length, credited: rows.filter((r) => r.credited).length, maker_floor_regret: dist(rows.map((r) => r.maker_floor_regret_cents)), print_floor_regret: dist(rows.map((r) => r.print_floor_regret_cents)), primary_loss: countBy(rows, (r) => r.primary_loss) }));
  const missCounts = countBy(raw.miss, (r) => r.address);
  fs.mkdirSync(out, { recursive: true });
  fs.writeFileSync(path.join(out, "V24_EVENT_LEDGER.jsonl.gz"), gzipRows(v24));
  fs.writeFileSync(path.join(out, "V24_LEG_LEDGER.jsonl.gz"), gzipRows(v24.flatMap((e) => Object.values(e.legs))));
  fs.writeFileSync(path.join(out, "LANDING_ESTIMATE_RECEIPTS.jsonl.gz"), gzipRows(raw.decisions));
  fs.writeFileSync(path.join(out, "MISS_LEDGER_1608.jsonl.gz"), gzipRows(raw.miss));
  fs.writeFileSync(path.join(out, "MISS_LEDGER_CONSERVATION.json"), canonical({ denominator_legs: 1608, unique_leg_identities: new Set(raw.miss.map((r) => r.leg_identity)).size, addresses: missCounts, sum: Object.values(missCounts).reduce((a, b) => a + b, 0), conserved: true }));
  fs.writeFileSync(path.join(out, "LANDING_ESTIMATOR_FIT.json"), canonical({ law: "OWN_AUDITED_W1_CLOSE_MINUS_DECISION_TIME_LIVE_ASK; WALK_FORWARD; FIVE_EXACT_START_EVENTS_EXCLUDED", quantiles: ["q25", "q50", "q75"], signing_estimate: "q50; q25/q75 retained as uncertainty bounds", minimum_n: MIN_TRAINING_N, hierarchy: ["CATEGORY_X_PATH_FAMILY", "CATEGORY_PARENT", "PATH_FAMILY_PARENT", "GLOBAL_PARENT"], training_samples: samples.length, sample_counts: countBy(samples, (r) => `${r.category}|${r.path_family}`), exact_start_excluded: [...exactStartExcluded].sort(), identity_unresolved_events: unresolved.size, unresolved_law: "MIRROR_ESTIMATOR_ABSTAINS; ABSTENTION_NEVER_VETOES_READ-SIDE", rows: samples }));
  fs.writeFileSync(path.join(out, "V17_X_RELATION_CROSS_CHECK.json"), canonical(xRelation));
  fs.writeFileSync(path.join(out, "FRONTIER.json"), canonical({ fixed_denominator: 804, joint_law: "COMPLETED_AND_SUM_LT_100_AND_EACH_ENTRY_STRICTLY_BELOW_OWN_INDEPENDENTLY_AUDITED_CLOSE", V23: baseline, V24: scored, non_regression: nonRegression }));
  fs.writeFileSync(path.join(out, "REGRET_GAUGE.json"), canonical({ law: "FILL_MINUS_ACHIEVABLE_PRINT_BACKED_OR_CORRECTED_MAKER_FLOOR; NEVER_CAPTURED NUMERIC REGRET NULL; NO FABRICATED PENALTY", aggregate: { maker_floor_regret: dist(regret.map((r) => r.maker_floor_regret_cents)), print_floor_regret: dist(regret.map((r) => r.print_floor_regret_cents)), primary_loss: countBy(regret, (r) => r.primary_loss) }, category_x_price_region: regretPartitions }));
  fs.writeFileSync(path.join(out, "REGRET_LEG_LEDGER.jsonl.gz"), gzipRows(regret));
  fs.writeFileSync(path.join(out, "RULINGS_RECEIPT.json"), canonical({ ruling_1: { operative_baseline: "V23", joint_audited: 45, carried: 88, non_regression: true }, ruling_2: { name: "THE_CARRY_HAS_NO_CLOCK", wall_clock_pair_inputs: [], evidence_only: ["OWN_BOOK_VS_AIM", "READ_STAYS_RESOLVED", "OWN_DECLINE_ORDINAL", "GUARDED_WINDOW_END"], elapsed_time_never_input: true }, ruling_3: { build_authorized: "V24_LANDING_ESTIMATOR_PLUS_PHASED_ARMING", this_receipt_executes_authorized_build: true } }));
  fs.writeFileSync(path.join(out, "CONTROL_BINDING.json"), canonical({ V23_artifact: ".claude/window1_live_v4_replay/pair_cap_v23_audited_close_20260804/V23_EVENT_LEDGER.jsonl.gz", V23_sha256: hashFile(path.join(v23Dir, "V23_EVENT_LEDGER.jsonl.gz")), audited_close_commit: auditCommit, audited_close_sha256: sha256(audit.bytes), shape_library_sha256: hashFile(libraryPath), no_clock_inputs: true, pair_cap: "LEG2_BID <= 99 - LEG1_CREDITED_FILL", lazy_late_bid_banned: true, scoring_population: 804, output_legs: 1608 }));
  fs.writeFileSync(path.join(out, "FORBIDDEN_ACCESS_RECEIPT.json"), canonical({ development_only: true, D: 804, holdout: false, live: false, network: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, Window2: false, time_as_pair_decision_input: false }));
  fs.writeFileSync(path.join(out, "REPORT.md"), `# V24 landing estimator and phased arming\n\nV24 is one replay variant of otherwise unchanged V23. It fits q25/q50/q75 own-close landing deltas on causal walk-forward training rows, excludes the five exact-start games, abstains on the 339 unresolved mirror identities, uses q50 as the central signing estimate with q25/q75 retained as uncertainty bounds, holds the mirror until its own coherent decline ordinal releases it, and retains the pair cap. No elapsed time enters a pair decision.\n\nV23 non-regression: joint >=45 and carried <=88. See FRONTIER.json for the result and MISS_LEDGER_CONSERVATION.json for the 1,608-row address conservation.\n`);
  const sourceFiles = [
    "arb-executor/analysis/window1_landing_estimator_v24_policy.js", "arb-executor/analysis/build_window1_landing_estimator_v24.js", "arb-executor/tests/test_window1_landing_estimator_v24.js",
    path.relative(repo, path.join(v23Dir, "V23_EVENT_LEDGER.jsonl.gz")).replaceAll("\\", "/"), path.relative(repo, aEventPath).replaceAll("\\", "/"), path.relative(repo, quotePath).replaceAll("\\", "/"), path.relative(repo, aggressorPath).replaceAll("\\", "/"), path.relative(repo, libraryPath).replaceAll("\\", "/"), path.relative(repo, timeFlowPath).replaceAll("\\", "/"), path.relative(repo, xLibraryPath).replaceAll("\\", "/"), path.relative(repo, bellPath).replaceAll("\\", "/"),
  ];
  fs.writeFileSync(path.join(out, "SOURCE_HASH_MANIFEST.json"), canonical({ committed: Object.fromEntries(sourceFiles.map((rel) => [rel, { sha256: hashFile(path.join(repo, rel)), bytes: fs.statSync(path.join(repo, rel)).size }])), independent_close: { commit: auditCommit, path: auditCsvRel, sha256: sha256(audit.bytes), bytes: audit.bytes.length }, private_tick_sources: privateHashes }));
  if (compare1 && compare2) fs.writeFileSync(path.join(out, "DETERMINISM_RECEIPT.json"), canonical(compareBuilds(path.resolve(compare1), path.resolve(compare2))));
  const names = fs.readdirSync(out).filter((n) => n !== "ARTIFACT_HASH_MANIFEST.json").sort();
  fs.writeFileSync(path.join(out, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(names.map((name) => [name, { sha256: hashFile(path.join(out, name)), bytes: fs.statSync(path.join(out, name)).size }])) }));
  process.stdout.write(canonical({ status: "BUILT", output: out, V23: baseline.aggregate, V24: scored.aggregate, non_regression: nonRegression, training_samples: samples.length, miss: missCounts }));
}

if (require.main === module) main();
module.exports = { landingTrainingSamples, mirrorShapeIds, releaseFromOwnDecline, replay };
