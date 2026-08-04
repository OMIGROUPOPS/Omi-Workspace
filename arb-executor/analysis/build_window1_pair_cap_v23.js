#!/usr/bin/env node
"use strict";

const childProcess = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { pairCapDecision, findStrictlyLaterReach } = require("./window1_pair_cap_v23_policy.js");

const args = process.argv.slice(2);
const value = (name, fallback) => { const index = args.indexOf(name); return index >= 0 ? args[index + 1] : fallback; };
const repo = path.resolve(value("--repo", "."));
const privateRoot = path.resolve(value("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const ticksRoot = path.join(privateRoot, "fit-local/ticks");
const artifactRel = ".claude/window1_live_v4_replay/pair_cap_v23_audited_close_20260804";
const out = path.resolve(value("--output", path.join(repo, artifactRel)));
const compare1 = value("--compare-run1", null);
const compare2 = value("--compare-run2", null);
const auditCommit = "50ce0f4940c461cf0b6fa1b79000d96b335cd601";
const auditCsvRel = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/INDEPENDENT_CLOSE_AUDIT_1608.csv";
const auditSummaryRel = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/CLOSE_AUDIT_AND_JOINT_CEILING_SUMMARY.json";
const v19Dir = path.join(repo, ".claude/window1_live_v4_replay/pair_couple_abstention_v19_20260803");
const aDir = path.join(repo, ".claude/window1_live_v4_replay/isolated_fix_a_anchor_freshness_v20_20260804");
const quotePath = path.join(repo, ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv");
const aggressorPath = path.join(repo, ".claude/window1_live_v4_replay/aggressor_ceiling_census_20260801/PER_LEG_AGGRESSOR_CENSUS.jsonl.gz");
const libraryPath = path.join(repo, ".claude/window1_live_v4_replay/interim_shape_v13_fit_20260803/INTERIM_SHAPE_LIBRARY_V13.json");
const timeFlowPath = path.join(repo, ".claude/window1_live_v4_replay/second_leg_x_pricer_v17_20260803/TIME_AND_FLOW_ROW_LEDGER.jsonl.gz");
const makerRulingCommit = "08fe622badbf92bb43a2f2acbd78b515a1ad5308";

function ensure(condition, message) { if (!condition) throw new Error(message); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function readRows(file) { const text = zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim(); return text ? text.split(/\r?\n/).map(JSON.parse) : []; }
function gzipRows(rows) { return zlib.gzipSync(Buffer.from(`${rows.map(JSON.stringify).join("\n")}\n`), { level: 9, mtime: 0 }); }
function parseCsv(text) { const lines = text.trimEnd().split(/\r?\n/); const header = lines.shift().split(","); return lines.filter(Boolean).map((line, index) => ({ row: Object.fromEntries(line.split(",").map((cell, i) => [header[i], cell])), ordinal: index + 2 })); }
function integer(value) { const parsed = Number(value); return Number.isInteger(parsed) ? parsed : null; }
function positive(value) { const parsed = Number(value); return Number.isFinite(parsed) && parsed > 0 ? parsed : null; }
function parseEt(value) { const match = String(value).match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2}) (AM|PM)$/); if (!match) return null; let hour = Number(match[4]); if (match[7] === "AM" && hour === 12) hour = 0; if (match[7] === "PM" && hour !== 12) hour += 12; return Date.parse(`${match[1]}-${match[2]}-${match[3]}T${String(hour).padStart(2, "0")}:${match[5]}:${match[6]}-04:00`) / 1000; }
function group(rows, keyFn) { const map = new Map(); for (const row of rows) { const key = keyFn(row); if (!map.has(key)) map.set(key, []); map.get(key).push(row); } return map; }
function countBy(rows, keyFn) { const counts = {}; for (const row of rows) { const key = String(keyFn(row)); counts[key] = (counts[key] || 0) + 1; } return Object.fromEntries(Object.entries(counts).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }
function quantile(values, p) { const xs = values.filter(Number.isFinite).sort((a, b) => a - b); return xs.length ? xs[Math.floor((xs.length - 1) * p)] : null; }
function distribution(values) { const xs = values.filter(Number.isFinite); return { denominator: values.length, numeric_n: xs.length, null_n: values.length - xs.length, min: xs.length ? Math.min(...xs) : null, p25: quantile(xs, .25), median: quantile(xs, .5), p75: quantile(xs, .75), p90: quantile(xs, .9), max: xs.length ? Math.max(...xs) : null, total_numeric_cents: xs.reduce((sum, value) => sum + value, 0) }; }
function gitShow(commit, rel) { return childProcess.execFileSync("git", ["show", `${commit}:${rel}`], { cwd: repo, maxBuffer: 64 * 1024 * 1024 }); }

function loadTickRows(source, sourceHashes) {
  const file = path.join(ticksRoot, `${source.ticker}.csv.gz`);
  ensure(fs.existsSync(file), `missing private tick source ${source.ticker}`);
  const bytes = fs.readFileSync(file);
  sourceHashes[source.ticker] = { sha256: sha256(bytes), bytes: bytes.length, source_class: "PRIVATE_FIT_LOCAL_TICK_CACHE; HASH_ONLY; NOT_PUBLIC" };
  const rows = [];
  for (const { row: raw, ordinal } of parseCsv(zlib.gunzipSync(bytes).toString("utf8"))) {
    const ts = parseEt(raw.ts_et);
    if (ts === null || ts < source.left_ts || ts > source.right_ts) continue;
    const bids = [], asks = [];
    for (let level = 1; level <= 5; level += 1) {
      const bp = integer(raw[`bid_${level}`]), bs = positive(raw[`bid_${level}_sz`]), ap = integer(raw[`ask_${level}`]), as = positive(raw[`ask_${level}_sz`]);
      if (bp !== null && bs !== null) bids.push([bp, bs]);
      if (ap !== null && as !== null) asks.push([ap, as]);
    }
    bids.sort((a, b) => b[0] - a[0]); asks.sort((a, b) => a[0] - b[0]);
    if (!bids.length || !asks.length || bids[0][0] > asks[0][0]) continue;
    rows.push({ ts, ordinal, receipt: `${path.basename(file)}#row-${ordinal}`, bid: bids[0][0], ask: asks[0][0], asks });
  }
  rows.sort((a, b) => a.ts - b.ts || a.ordinal - b.ordinal);
  return rows;
}

function normalizeCloseAudit() {
  const csvBytes = gitShow(auditCommit, auditCsvRel);
  const summaryBytes = gitShow(auditCommit, auditSummaryRel);
  ensure(sha256(csvBytes) === "51d542d9c1f18c6b30b6bb5e8f458d9cf3adeebf1895399f8f7b2ba416836303", "independent close CSV hash mismatch");
  ensure(sha256(summaryBytes) === "a1b9047684f2be1a1942d40cae9c326501fbe3ad4219852bfedf586e1ecb67cf", "independent close summary hash mismatch");
  const rows = parseCsv(csvBytes.toString("utf8")).map(({ row }) => ({
    ticker: row.ticker,
    event_id: row.event,
    category: row.category,
    price_region: row.price_region,
    audited_close_cents: row.audited_close_cents === "" ? null : integer(row.audited_close_cents),
    audited_close_ts_utc: row.audited_close_ts_utc || null,
    close_aggressor_side: row.close_aggressor_side || null,
    seconds_before_right_edge: row.seconds_before_right_edge === "" ? null : Number(row.seconds_before_right_edge),
    replay_close_cents: row.replay_close_cents === "" ? null : integer(row.replay_close_cents),
    divergence_class: row.divergence_class,
  }));
  ensure(rows.length === 1608, `close audit rows ${rows.length}`);
  return { rows, csvBytes, summaryBytes };
}

function metrics(events, closes) {
  const completed = events.filter((event) => Object.values(event.legs).every((leg) => leg.credited));
  let underPar = 0, bothBelow = 0, joint = 0, carried = 0, unavailable = 0;
  for (const event of completed) {
    const legs = Object.values(event.legs), combined = legs.reduce((sum, leg) => sum + leg.entry_cents, 0);
    const closeRows = legs.map((leg) => closes.get(leg.ticker));
    const available = closeRows.every((row) => Number.isInteger(row?.audited_close_cents));
    if (combined < 100) underPar += 1;
    if (!available) { unavailable += 1; continue; }
    const deltas = legs.map((leg, index) => leg.entry_cents - closeRows[index].audited_close_cents);
    const below = deltas.every((delta) => delta < 0);
    if (below) bothBelow += 1;
    if (below && combined < 100) joint += 1;
    if (deltas.some((delta) => delta > 0) && deltas.some((delta) => delta < 0)) carried += 1;
  }
  return {
    D: events.length,
    acted_legs: events.flatMap((event) => Object.values(event.legs)).filter((leg) => leg.acted).length,
    credited_legs: events.flatMap((event) => Object.values(event.legs)).filter((leg) => leg.credited).length,
    completed_pairs: completed.length,
    pairs_under_par: underPar,
    completed_pairs_with_both_audited_closes: completed.length - unavailable,
    completed_pairs_close_unavailable: unavailable,
    both_legs_strictly_below_audited_close: bothBelow,
    joint_objective_pairs: joint,
    strict_carried_pairs: carried,
  };
}

function frontier(events, closes) {
  const tiers = { LE_93: (sum) => sum <= 93, LE_95: (sum) => sum <= 95, LE_97: (sum) => sum <= 97, LT_100: (sum) => sum < 100, ANY_PRICE: () => true };
  const output = {};
  for (const [tier, qualifies] of Object.entries(tiers)) {
    const selected = events.filter((event) => {
      const legs = Object.values(event.legs);
      return legs.every((leg) => leg.credited) && qualifies(legs.reduce((sum, leg) => sum + leg.entry_cents, 0));
    });
    const score = metrics(selected.map((event) => event), closes);
    output[tier] = { fixed_denominator: events.length, completed_pairs: selected.length, raw_completion_rate: `${selected.length}/${events.length}`, pairs_both_legs_strictly_below_audited_close: score.both_legs_strictly_below_audited_close, joint_objective_pairs: score.joint_objective_pairs, close_unavailable_pairs: score.completed_pairs_close_unavailable };
  }
  return output;
}

function scoreVariant(name, events, closes) {
  const aggregate = metrics(events, closes);
  const partitions = [...group(events, (event) => `${event.category}|${event.starting_price_split}`)].sort(([a], [b]) => a.localeCompare(b)).map(([key, rows]) => ({ category: key.split("|")[0], starting_price_region: key.split("|")[1], D: rows.length, metrics: metrics(rows, closes), frontier: frontier(rows, closes) }));
  return { variant: name, audited_close_commit: auditCommit, aggregate, frontier: frontier(events, closes), category_x_starting_price_region: partitions };
}

function legacyReplayJoint(events) {
  return events.filter((event) => {
    const legs = Object.values(event.legs);
    return legs.every((leg) => leg.credited && Number.isInteger(leg.own_window1_close_cents) && leg.entry_cents < leg.own_window1_close_cents) && legs.reduce((sum, leg) => sum + leg.entry_cents, 0) < 100;
  }).length;
}

function buildV23(aEvents, quoteSources, sourceHashes) {
  const receipts = [];
  const events = aEvents.map((event) => {
    const legs = Object.values(event.legs).map((leg) => ({ ...leg }));
    if (!legs.every((leg) => leg.credited)) return { ...event, legs: Object.fromEntries(legs.map((leg) => [leg.leg_id, leg])), pair_cap_v23: { status: "NOT_APPLICABLE_PAIR_NOT_COMPLETED_IN_A" } };
    const ordered = [...legs].sort((a, b) => a.action_timestamp_epoch - b.action_timestamp_epoch || a.leg_id.localeCompare(b.leg_id));
    const first = ordered[0], second = ordered[1];
    if (first.action_timestamp_epoch === second.action_timestamp_epoch) {
      const receipt = { event_id: event.event_id, status: "NOT_ARMED_SIMULTANEOUS_ACTIONS_NO_STRICTLY_PRIOR_CREDITED_FILL", action_timestamp_epoch: first.action_timestamp_epoch, A_combined_entry_cents: first.entry_cents + second.entry_cents, leg_identities: ordered.map((leg) => leg.leg_identity) };
      receipts.push(receipt);
      return { ...event, legs: Object.fromEntries(legs.map((leg) => [leg.leg_id, leg])), pair_cap_v23: receipt };
    }
    const ownBook = second.placement?.pre_action_evidence?.own?.current_book;
    ensure(ownBook && Number.isInteger(ownBook.bid) && Number.isInteger(ownBook.ask), `missing action book ${second.leg_identity}`);
    const decision = pairCapDecision({ firstFillCents: first.entry_cents, originalSecondBidCents: second.entry_cents, liveBidCents: ownBook.bid, liveAskCents: ownBook.ask });
    const receipt = {
      event_id: event.event_id,
      status: decision.state,
      reason: decision.reason,
      first_leg_identity: first.leg_identity,
      first_leg_fill_cents: first.entry_cents,
      first_leg_fill_timestamp_epoch: first.action_timestamp_epoch,
      second_leg_identity: second.leg_identity,
      second_leg_action_timestamp_epoch: second.action_timestamp_epoch,
      second_leg_action_receipt: second.placement.action_receipt,
      live_book_at_leg2_decision: { bid: ownBook.bid, ask: ownBook.ask, spread: ownBook.spread, top_ask_size: ownBook.top_ask_size, receipt: ownBook.receipt, timestamp_epoch: ownBook.timestamp_epoch },
      A_leg2_bid_cents: second.entry_cents,
      pair_cap_formula: "99 - credited_leg1_fill_cents",
      pair_cap_cents: decision.cap_cents,
      selected_leg2_bid_cents: decision.selected_bid_cents,
      no_chase: true,
      later_fill_evidence: null,
    };
    if (decision.state === "UNCHANGED") {
      receipts.push(receipt);
      return { ...event, legs: Object.fromEntries(legs.map((leg) => [leg.leg_id, leg])), pair_cap_v23: receipt };
    }
    if (decision.state === "ABSTAIN") {
      Object.assign(second, { acted: false, credited: false, honest_fill_class: "UNPROVEN", entry_cents: null, terminal_reason: decision.reason, A_counterfactual_entry_cents: event.legs[second.leg_id].entry_cents, pair_cap_v23: receipt, placement: null });
      receipts.push(receipt);
      return { ...event, legs: Object.fromEntries(legs.map((leg) => [leg.leg_id, leg])), pair_cap_v23: receipt };
    }
    const source = quoteSources.get(second.ticker);
    ensure(source, `missing quote source ${second.ticker}`);
    const rows = loadTickRows(source, sourceHashes);
    const reach = findStrictlyLaterReach(rows, { actionTs: second.action_timestamp_epoch, targetCents: decision.selected_bid_cents, actionReceipt: second.placement.action_receipt });
    receipt.later_fill_evidence = reach;
    const originalPlacement = second.placement;
    second.placement = { ...originalPlacement, price_cents: decision.selected_bid_cents, pair_cap_v23: receipt };
    second.A_counterfactual_entry_cents = second.entry_cents;
    second.pair_cap_v23 = receipt;
    if (reach) {
      Object.assign(second, {
        acted: true,
        credited: true,
        honest_fill_class: "PROVEN_MAKER_BY_RESIDENCY_STRICTLY_LATER_QUALIFYING_ASK",
        entry_cents: decision.selected_bid_cents,
        terminal_reason: "PAIR_CAP_RESTED_AND_STRICTLY_LATER_QUALIFYING_ASK_REACHED_TARGET",
        fill: { price_cents: decision.selected_bid_cents, quantity: 5, evidence_type: "STRICTLY_LATER_ASK_DWELL_AND_DISPLAYED_CAPACITY_AFTER_PAIR_CAP_RESIDENCY", ...reach },
      });
    } else {
      Object.assign(second, { acted: true, credited: false, honest_fill_class: "UNPROVEN", entry_cents: null, terminal_reason: "PAIR_CAP_RESTED_UNFILLED_THROUGH_GUARDED_WINDOW_NO_CHASE", fill: null });
    }
    receipts.push(receipt);
    return { ...event, legs: Object.fromEntries(legs.map((leg) => [leg.leg_id, leg])), pair_cap_v23: receipt };
  });
  return { events, receipts };
}

function addDerivedFields(events, closes, aggressors) {
  return events.map((event) => {
    const legs = Object.fromEntries(Object.entries(event.legs).map(([legId, leg]) => {
      const close = closes.get(leg.ticker), aggressor = aggressors.get(leg.ticker);
      const sellerFloor = aggressor?.seller_aggressed_floor?.price_cents ?? null;
      const makerCandidates = [leg.qualifying_ask_floor_cents, sellerFloor].filter(Number.isInteger);
      const makerFloor = makerCandidates.length ? Math.min(...makerCandidates) : null;
      return [legId, {
        ...leg,
        audited_close_cents: close?.audited_close_cents ?? null,
        audited_close_ts_utc: close?.audited_close_ts_utc ?? null,
        audited_close_aggressor_side: close?.close_aggressor_side ?? null,
        audited_close_seconds_before_right_edge: close?.seconds_before_right_edge ?? null,
        entry_minus_audited_close_cents: leg.credited && Number.isInteger(close?.audited_close_cents) ? leg.entry_cents - close.audited_close_cents : null,
        maker_floor_cents: makerFloor,
        seller_aggressed_floor_cents: sellerFloor,
        maker_floor_law: "MIN(QUALIFYING_ASK_FLOOR, LOWEST_SELLER_AGGRESSED_TRUE_TRADE)",
        entry_minus_maker_floor_cents: leg.credited && Number.isInteger(makerFloor) ? leg.entry_cents - makerFloor : null,
        entry_minus_objective_traded_low_cents: leg.credited && Number.isInteger(leg.objective_traded_low_cents) ? leg.entry_cents - leg.objective_traded_low_cents : null,
      }];
    }));
    const xs = Object.values(legs), completed = xs.every((leg) => leg.credited), combined = completed ? xs.reduce((sum, leg) => sum + leg.entry_cents, 0) : null;
    const bothClose = completed && xs.every((leg) => Number.isInteger(leg.audited_close_cents));
    const bothBelow = bothClose && xs.every((leg) => leg.entry_cents < leg.audited_close_cents);
    return { ...event, legs, completed_pair: completed, combined_entry_cents: combined, pair_under_par: completed && combined < 100, both_legs_strictly_below_audited_close: bothBelow, joint_objective_pass_audited_close: bothBelow && combined < 100 };
  });
}

function regretGauge(variant, events) {
  const legs = events.flatMap((event) => Object.values(event.legs));
  const rows = legs.map((leg) => ({
    variant,
    leg_identity: leg.leg_identity,
    event_id: leg.event_id,
    category: leg.category,
    price_region: leg.price_region,
    credited: leg.credited,
    credited_entry_cents: leg.credited ? leg.entry_cents : null,
    qualifying_ask_floor_cents: leg.qualifying_ask_floor_cents,
    seller_aggressed_floor_cents: leg.seller_aggressed_floor_cents,
    corrected_maker_floor_cents: leg.maker_floor_cents,
    objective_print_backed_floor_cents: leg.objective_traded_low_cents,
    maker_floor_regret_cents: leg.entry_minus_maker_floor_cents,
    print_floor_regret_cents: leg.entry_minus_objective_traded_low_cents,
    primary_loss: !leg.credited ? `NOT_CREDITED:${leg.terminal_reason}` : leg.entry_minus_maker_floor_cents === 0 ? "ZERO_MAKER_FLOOR_REGRET" : leg.entry_minus_maker_floor_cents > 0 ? "COMPLETED_OVER_MAKER_FLOOR" : "BETTER_THAN_CORRECTED_MAKER_FLOOR",
  }));
  const partitions = [...group(rows, (row) => `${row.category}|${row.price_region}`)].sort(([a], [b]) => a.localeCompare(b)).map(([key, cell]) => ({ category: key.split("|")[0], price_region: key.split("|")[1], n: cell.length, credited: cell.filter((row) => row.credited).length, maker_floor_regret: distribution(cell.map((row) => row.maker_floor_regret_cents)), print_floor_regret: distribution(cell.map((row) => row.print_floor_regret_cents)), primary_loss: countBy(cell, (row) => row.primary_loss) }));
  return { variant, denominator_legs: rows.length, maker_floor_ruling_commit: makerRulingCommit, maker_floor_law: "MIN(QUALIFYING_ASK_FLOOR, LOWEST_SELLER_AGGRESSED_TRUE_TRADE)", objective_floor_law: "LOWEST_LAWFUL_TRUE_TRADE_IN_GUARDED_WINDOW1", aggregate: { maker_floor_regret: distribution(rows.map((row) => row.maker_floor_regret_cents)), print_floor_regret: distribution(rows.map((row) => row.print_floor_regret_cents)), primary_loss: countBy(rows, (row) => row.primary_loss) }, category_x_price_region: partitions, rows };
}

function landingSpec(library, aLegs, timeRows) {
  const shapes = new Map();
  for (const groupRow of Object.values(library.groups)) for (const shape of groupRow.shapes) shapes.set(shape.shape_id, shape);
  const perCategory = [];
  for (const [category, legs] of [...group(aLegs, (leg) => leg.category)].sort(([a], [b]) => a.localeCompare(b))) {
    const assigned = legs.filter((leg) => library.assignment[leg.leg_identity]);
    const signable = assigned.filter((leg) => shapes.get(library.assignment[leg.leg_identity])?.usable_for_signing);
    perCategory.push({ category, population_legs: legs.length, shape_assigned: assigned.length, signable_shape_assignment: signable.length, unusable_shape_assignment: assigned.length - signable.length, unassigned: legs.length - assigned.length, numeric_decision_time_close_landing_estimate_available: 0 });
  }
  const unresolved = timeRows.filter((row) => row.climber_first === "UNRESOLVED_DIRECTION");
  return {
    ruling: "SPEC_ONLY; V22_PHASE1_NOT_RUN",
    current_shape_surface: {
      path: ".claude/window1_live_v4_replay/interim_shape_v13_fit_20260803/INTERIM_SHAPE_LIBRARY_V13.json",
      shapes: library.census.shapes,
      signable_shapes: library.census.signable_shapes,
      available_training_legs: library.census.available_training_legs,
      signable_members: library.census.signable_members,
      emitted_runtime_values: ["surviving_shape_ids", "coherent qualified-ask descent ordinal distribution", "FLOOR/LOWER/UNKNOWN verdict", "fitted micro-micro READY/WAIT"],
      numeric_own_close_landing_distribution: "NOT_BOUND",
      numeric_own_close_landing_coverage_legs: 0,
      reason: "NO CURRENT SHAPE OBJECT CONTAINS A DECISION-TIME OWN-CLOSE PRICE OR DISTRIBUTION",
      category_coverage: perCategory,
    },
    identity_unresolved_hole: {
      source_surface: ".claude/window1_live_v4_replay/second_leg_x_pricer_v17_20260803/TIME_AND_FLOW_ROW_LEDGER.jsonl.gz",
      evaluated_async_floor_events: timeRows.length,
      climber_first_identity_unresolved: unresolved.length,
      category_counts: countBy(unresolved, (row) => row.category),
      interpretation: "THE 339 IS AN ORDERING/DIRECTION-IDENTITY HOLE, NOT AN EXISTING NUMERIC CLOSE-LANDING ESTIMATE",
    },
    ratification_candidate_interface: {
      status: "UNBUILT_AWAITING_OPERATOR_RATIFICATION",
      causal_input: "CURRENT SURVIVING SHAPE SET AND DECISION-TIME LIVE BOOK ONLY",
      required_new_fit: "FOR EACH CAUSAL SURVIVOR STATE, A TRAINING-ONLY DISTRIBUTION OF OWN_AUDITED_CLOSE_MINUS_CURRENT_QUALIFYING_ASK WITH DISJOINT VALIDATION AND NAMED THIN/UNRESOLVED ABSTENTION",
      aim_bar: "STRICTLY BELOW A CONSERVATIVELY SELECTED DECISION-TIME LANDING DISTRIBUTION QUANTILE; QUANTILE NOT YET AUTHORIZED",
      aim_floor: "CURRENT LIVE QUALIFYING ASK BY RESIDENCY; NEVER EX-POST MAKER FLOOR",
      prohibited: ["EX_POST_CLOSE_AS_POLICY_INPUT", "EX_POST_MAKER_FLOOR_AS_POLICY_INPUT", "V17_BUCKET_POINT_TARGET", "CELL_BEFORE_ENTRY"],
    },
  };
}

function compareBuilds(first, second) {
  const excluded = new Set(["ARTIFACT_HASH_MANIFEST.json", "DETERMINISM_RECEIPT.json"]);
  const names1 = fs.readdirSync(first).filter((name) => !excluded.has(name)).sort();
  const names2 = fs.readdirSync(second).filter((name) => !excluded.has(name)).sort();
  ensure(JSON.stringify(names1) === JSON.stringify(names2), "determinism build file census differs");
  const mismatches = names1.filter((name) => hashFile(path.join(first, name)) !== hashFile(path.join(second, name)));
  ensure(mismatches.length === 0, `determinism mismatch: ${mismatches.join(",")}`);
  return { clean_builds: 2, compared_files: names1.length, byte_identical: true, mismatches: [], run1_hash: sha256(Buffer.from(names1.map((name) => `${name}:${hashFile(path.join(first, name))}`).join("\n"))), run2_hash: sha256(Buffer.from(names2.map((name) => `${name}:${hashFile(path.join(second, name))}`).join("\n"))) };
}

function main() {
  for (const file of [quotePath, aggressorPath, libraryPath, timeFlowPath, path.join(v19Dir, "POPULATION_EVENT_LEDGER.jsonl.gz"), path.join(aDir, "POPULATION_EVENT_LEDGER.jsonl.gz")]) ensure(fs.existsSync(file), `missing ${file}`);
  childProcess.execFileSync("git", ["cat-file", "-e", `${auditCommit}^{commit}`], { cwd: repo });
  const audit = normalizeCloseAudit(), closeMap = new Map(audit.rows.map((row) => [row.ticker, row]));
  const quoteRows = parseCsv(fs.readFileSync(quotePath, "utf8")).map(({ row }) => ({ ticker: row.ticker, left_ts: Number(row.left_ts), right_ts: Number(row.right_ts) }));
  ensure(quoteRows.length === 1608, `quote rows ${quoteRows.length}`);
  const quoteSources = new Map(quoteRows.map((row) => [row.ticker, row]));
  const aggressorRows = readRows(aggressorPath), aggressors = new Map(aggressorRows.map((row) => [row.ticker, row]));
  ensure(aggressorRows.length === 1608, `aggressor rows ${aggressorRows.length}`);
  const v19Events = readRows(path.join(v19Dir, "POPULATION_EVENT_LEDGER.jsonl.gz"));
  const aEvents = readRows(path.join(aDir, "POPULATION_EVENT_LEDGER.jsonl.gz"));
  const aLegs = readRows(path.join(aDir, "POPULATION_LEG_LEDGER.jsonl.gz"));
  ensure(v19Events.length === 804 && aEvents.length === 804 && aLegs.length === 1608, "frozen population conservation");
  const sourceHashes = {};
  const v23Raw = buildV23(aEvents, quoteSources, sourceHashes);
  const v19 = addDerivedFields(v19Events, closeMap, aggressors), a = addDerivedFields(aEvents, closeMap, aggressors), v23 = addDerivedFields(v23Raw.events, closeMap, aggressors);
  const variants = [scoreVariant("V19", v19, closeMap), scoreVariant("A_V20", a, closeMap), scoreVariant("V23_PAIR_CAP_IMMEDIATE", v23, closeMap)];
  const legacy = { V19: legacyReplayJoint(v19Events), A_V20: legacyReplayJoint(aEvents), V23_PAIR_CAP_IMMEDIATE: legacyReplayJoint(v23) };
  const audited = Object.fromEntries(variants.map((variant) => [variant.variant, variant.aggregate.joint_objective_pairs]));
  const regrade = {
    audit_commit: auditCommit,
    audited_close_rows: audit.rows.length,
    audited_close_available: audit.rows.filter((row) => Number.isInteger(row.audited_close_cents)).length,
    replay_close_null_audit_recovers: audit.rows.filter((row) => row.divergence_class === "REPLAY_CLOSE_ABSENT_AUDIT_RECOVERS").length,
    no_in_window_print: audit.rows.filter((row) => row.divergence_class === "NO_INWINDOW_TRUE_PRINT").length,
    variants,
    joint_delta_from_frozen_replay_close: Object.fromEntries(Object.keys(audited).map((name) => [name, { frozen_replay_close_joint: legacy[name], audited_close_joint: audited[name], delta: audited[name] - legacy[name] }])),
    V23_vs_A_audited_joint_delta: audited.V23_PAIR_CAP_IMMEDIATE - audited.A_V20,
  };
  const v23Regret = regretGauge("V23_PAIR_CAP_IMMEDIATE", v23);
  const aRegret = regretGauge("A_V20", a);
  const v23ByEvent = new Map(v23.map((event) => [event.event_id, event]));
  const phase0ParFailures = aEvents.filter((event) => {
    const legs = Object.values(event.legs);
    return legs.every((leg) => leg.credited && Number.isInteger(leg.own_window1_close_cents) && leg.entry_cents < leg.own_window1_close_cents)
      && legs.reduce((sum, leg) => sum + leg.entry_cents, 0) >= 100;
  }).map((event) => {
    const originalLegs = Object.values(event.legs), v23Event = v23ByEvent.get(event.event_id);
    return {
      event_id: event.event_id,
      category: event.category,
      starting_price_split: event.starting_price_split,
      A_combined_entry_cents: originalLegs.reduce((sum, leg) => sum + leg.entry_cents, 0),
      A_entries: Object.fromEntries(originalLegs.map((leg) => [leg.leg_id, leg.entry_cents])),
      V23_pair_cap_status: v23Event.pair_cap_v23?.status ?? null,
      V23_pair_cap_reason: v23Event.pair_cap_v23?.reason ?? null,
      V23_completed: v23Event.completed_pair,
      V23_combined_entry_cents: v23Event.combined_entry_cents,
      V23_joint_on_audited_close: v23Event.joint_objective_pass_audited_close,
    };
  });
  ensure(phase0ParFailures.length === 25, `Phase-0 par-failure identity count ${phase0ParFailures.length}`);
  ensure(phase0ParFailures.every((row) => row.A_combined_entry_cents === 100 || row.A_combined_entry_cents === 101), "Phase-0 par failures not all 100/101");
  const library = JSON.parse(fs.readFileSync(libraryPath, "utf8"));
  const timeRows = readRows(timeFlowPath);
  const spec = landingSpec(library, aLegs, timeRows);
  ensure(spec.identity_unresolved_hole.climber_first_identity_unresolved === 339, "339 identity-unresolved hole mismatch");
  const unresolvedRows = timeRows.filter((row) => row.climber_first === "UNRESOLVED_DIRECTION").map((row) => ({ event_id: row.event_id, category: row.category, starting_price_split: row.starting_price_split, first_ticker: row.first_ticker, sibling_ticker: row.sibling_ticker, climber_first: row.climber_first, leg1_tminus_scheduled: row.leg1_tminus_scheduled, leg1_tminus_bell: row.leg1_tminus_bell, leg2_tminus_scheduled: row.leg2_tminus_scheduled, leg2_tminus_bell: row.leg2_tminus_bell }));
  const receiptCounts = countBy(v23Raw.receipts, (row) => `${row.status}:${row.reason || "NO_REASON"}`);
  ensure(v23.every((event) => !event.completed_pair || event.combined_entry_cents < 100 || event.pair_cap_v23?.status === "NOT_ARMED_SIMULTANEOUS_ACTIONS_NO_STRICTLY_PRIOR_CREDITED_FILL"), "strict-order completed V23 pair violates cap");
  fs.mkdirSync(out, { recursive: true });
  fs.writeFileSync(path.join(out, "V23_EVENT_LEDGER.jsonl.gz"), gzipRows(v23));
  fs.writeFileSync(path.join(out, "V23_LEG_LEDGER.jsonl.gz"), gzipRows(v23.flatMap((event) => Object.values(event.legs))));
  fs.writeFileSync(path.join(out, "PAIR_CAP_DECISION_RECEIPTS.jsonl.gz"), gzipRows(v23Raw.receipts));
  fs.writeFileSync(path.join(out, "AUDITED_CLOSE_REGRADE.json"), canonical(regrade));
  fs.writeFileSync(path.join(out, "FRONTIER.json"), canonical({ fixed_denominator: 804, JOINT_law: "COMPLETED_AND_SUM_LT_100_AND_EACH_LEG_ENTRY_STRICTLY_BELOW_ITS_INDEPENDENTLY_AUDITED_OWN_CLOSE", variants: Object.fromEntries(variants.map((variant) => [variant.variant, { aggregate: variant.aggregate, frontier: variant.frontier, category_x_starting_price_region: variant.category_x_starting_price_region }])) }));
  fs.writeFileSync(path.join(out, "REGRET_GAUGE.json"), canonical({ score: "REGRET_GAUGE", A_V20: { aggregate: aRegret.aggregate, category_x_price_region: aRegret.category_x_price_region }, V23_PAIR_CAP_IMMEDIATE: { aggregate: v23Regret.aggregate, category_x_price_region: v23Regret.category_x_price_region } }));
  fs.writeFileSync(path.join(out, "REGRET_LEG_LEDGER.jsonl.gz"), gzipRows(v23Regret.rows));
  fs.writeFileSync(path.join(out, "V23_VS_A.json"), canonical({ A_V20: variants[1].aggregate, V23_PAIR_CAP_IMMEDIATE: variants[2].aggregate, delta: Object.fromEntries(Object.keys(variants[1].aggregate).filter((key) => Number.isInteger(variants[1].aggregate[key])).map((key) => [key, variants[2].aggregate[key] - variants[1].aggregate[key]])), pair_cap_receipts: receiptCounts, receipt_rows: v23Raw.receipts.length, strict_order_receipts: v23Raw.receipts.filter((row) => row.status !== "NOT_ARMED_SIMULTANEOUS_ACTIONS_NO_STRICTLY_PRIOR_CREDITED_FILL").length, simultaneous_not_armed: v23Raw.receipts.filter((row) => row.status === "NOT_ARMED_SIMULTANEOUS_ACTIONS_NO_STRICTLY_PRIOR_CREDITED_FILL").length }));
  fs.writeFileSync(path.join(out, "PHASE0_25_PAR_FAILURE_DISPOSITION.json"), canonical({ law: "FROZEN_A_BOTH_LEGS_STRICTLY_BELOW_REPLAY_CLOSE_BUT_COMBINED_ENTRY_NOT_STRICTLY_UNDER_PAR", count: phase0ParFailures.length, A_combined_cost_distribution: countBy(phase0ParFailures, (row) => row.A_combined_entry_cents), V23_status: countBy(phase0ParFailures, (row) => row.V23_pair_cap_status), V23_completed: countBy(phase0ParFailures, (row) => row.V23_completed), rows: phase0ParFailures }));
  fs.writeFileSync(path.join(out, "V22_PHASE1_LANDING_ESTIMATOR_SPEC.json"), canonical(spec));
  fs.writeFileSync(path.join(out, "V22_IDENTITY_UNRESOLVED_339.jsonl.gz"), gzipRows(unresolvedRows));
  fs.writeFileSync(path.join(out, "CONTROL_BINDING.json"), canonical({ base_variant: "A_V20", pair_cap_law: "AT STRICTLY LATER LEG2 PLACEMENT, CAP=99-CREDITED_LEG1_FILL; CAP MAY REST ONLY AT/ABOVE CURRENT LIVE BID; BELOW LIVE BID ABSTAINS; STRICTLY LATER QUALIFYING ASK REQUIRED; NO CHASE", audit_commit: auditCommit, audit_csv_sha256: sha256(audit.csvBytes), audit_summary_sha256: sha256(audit.summaryBytes), V22_phase1_executed: false }));
  fs.writeFileSync(path.join(out, "FORBIDDEN_ACCESS_RECEIPT.json"), canonical({ development_population_only: true, D: 804, holdout: false, live: false, network: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, Window2: false, V22_phase1_execution: false }));
  const sourceFiles = [
    ["arb-executor/analysis/window1_pair_cap_v23_policy.js", path.join(repo, "arb-executor/analysis/window1_pair_cap_v23_policy.js")],
    ["arb-executor/analysis/build_window1_pair_cap_v23.js", __filename],
    ["arb-executor/tests/test_window1_pair_cap_v23.js", path.join(repo, "arb-executor/tests/test_window1_pair_cap_v23.js")],
    [path.relative(repo, path.join(v19Dir, "POPULATION_EVENT_LEDGER.jsonl.gz")).replaceAll("\\", "/"), path.join(v19Dir, "POPULATION_EVENT_LEDGER.jsonl.gz")],
    [path.relative(repo, path.join(aDir, "POPULATION_EVENT_LEDGER.jsonl.gz")).replaceAll("\\", "/"), path.join(aDir, "POPULATION_EVENT_LEDGER.jsonl.gz")],
    [path.relative(repo, path.join(aDir, "POPULATION_LEG_LEDGER.jsonl.gz")).replaceAll("\\", "/"), path.join(aDir, "POPULATION_LEG_LEDGER.jsonl.gz")],
    [path.relative(repo, quotePath).replaceAll("\\", "/"), quotePath],
    [path.relative(repo, aggressorPath).replaceAll("\\", "/"), aggressorPath],
    [path.relative(repo, libraryPath).replaceAll("\\", "/"), libraryPath],
    [path.relative(repo, timeFlowPath).replaceAll("\\", "/"), timeFlowPath],
  ];
  fs.writeFileSync(path.join(out, "SOURCE_HASH_MANIFEST.json"), canonical({ committed_files: Object.fromEntries(sourceFiles.map(([name, file]) => [name, { sha256: hashFile(file), bytes: fs.statSync(file).size }])), independent_close_audit: { commit: auditCommit, csv: { path: auditCsvRel, sha256: sha256(audit.csvBytes), bytes: audit.csvBytes.length }, summary: { path: auditSummaryRel, sha256: sha256(audit.summaryBytes), bytes: audit.summaryBytes.length } }, private_tick_sources_accessed_for_pair_cap: sourceHashes }));
  fs.writeFileSync(path.join(out, "REPORT.md"), `# Window-1 V23 pair-cap replay and audited-close regrade\n\nV23 is one isolated replay variant of frozen A. It adds only the immediate second-leg cap. V19, A, and V23 are regraded against the independently audited 1,608-leg close ruler. V22 Phase 1 is not built or run: the current shape library emits ordinal/verdict state but no numeric close landing distribution.\n\nArtifacts: AUDITED_CLOSE_REGRADE.json, FRONTIER.json, REGRET_GAUGE.json, V23_VS_A.json, PAIR_CAP_DECISION_RECEIPTS.jsonl.gz, V22_PHASE1_LANDING_ESTIMATOR_SPEC.json, and V22_IDENTITY_UNRESOLVED_339.jsonl.gz.\n`);
  if (compare1 && compare2) fs.writeFileSync(path.join(out, "DETERMINISM_RECEIPT.json"), canonical(compareBuilds(path.resolve(compare1), path.resolve(compare2))));
  const artifactNames = fs.readdirSync(out).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  fs.writeFileSync(path.join(out, "ARTIFACT_HASH_MANIFEST.json"), canonical({ files: Object.fromEntries(artifactNames.map((name) => [name, { sha256: hashFile(path.join(out, name)), bytes: fs.statSync(path.join(out, name)).size }])) }));
  process.stdout.write(canonical({ status: "BUILT", output: out, audited_joint: audited, V23_vs_A_joint_delta: regrade.V23_vs_A_audited_joint_delta, V23_metrics: variants[2].aggregate, pair_cap_receipts: receiptCounts, shape_numeric_landing_coverage: 0, identity_unresolved: unresolvedRows.length }));
}

main();
