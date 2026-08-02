#!/usr/bin/env node
"use strict";

// Reaccounts the frozen V7 policy stream against V8 dual floors and corrected closes.
// No policy decision, target, action, or fill classification is regenerated.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const args = process.argv.slice(2);
const value = (name, fallback) => { const index = args.indexOf(name); return index >= 0 ? args[index + 1] : fallback; };
const repo = path.resolve(value("--repo", "."));
const output = path.resolve(value("--output", path.join(repo, ".claude/window1_live_v4_replay/dynamic_renarrow_population_v9_20260802")));
const v7Dir = path.join(repo, ".claude/window1_live_v4_replay/dynamic_renarrow_population_v7_20260801");
const v8Dir = path.join(repo, ".claude/window1_live_v4_replay/trade_floor_correction_v8_20260802");
const v7LedgerPath = path.join(v7Dir, "EVENT_LEDGER.jsonl.gz");
const v7ConservationPath = path.join(v7Dir, "CONSERVATION_RECEIPT.json");
const v8LegPath = path.join(v8Dir, "DUAL_FLOOR_LEG_LEDGER.jsonl.gz");
const v8EventPath = path.join(v8Dir, "TRADE_FLOOR_EVENT_LEDGER.jsonl.gz");
const v8CeilingPath = path.join(v8Dir, "CEILING_RECOMPUTATION.json");
const lateCloseLawPath = path.join(repo, ".claude/window1_live_v4_replay/actual_bell_refit_20260729/ACTUAL_BELL_REFIT.json");
const testPath = path.join(repo, "arb-executor/tests/test_window1_dynamic_renarrow_population_v9.js");
const LATE_CLOSE_SECONDS = 300;

function canonical(item) { return `${JSON.stringify(item, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function relative(file) { return path.relative(repo, file).replace(/\\/g, "/"); }
function ensure(condition, message) { if (!condition) throw new Error(message); }
function json(file) { return JSON.parse(fs.readFileSync(file, "utf8")); }
function jsonlGz(file) { return zlib.gunzipSync(fs.readFileSync(file)).toString("utf8").trim().split(/\r?\n/).map(JSON.parse); }
function gzipJsonl(rows) { return zlib.gzipSync(Buffer.from(rows.map((row) => JSON.stringify(row)).join("\n") + "\n"), { level: 9, mtime: 0 }); }
function quantile(values, p) { const rows = [...values].sort((a, b) => a - b); return rows.length ? rows[Math.min(rows.length - 1, Math.floor(p * (rows.length - 1)))] : null; }
function distribution(values) { return { n: values.length, min: values.length ? Math.min(...values) : null, p25: quantile(values, .25), median: quantile(values, .5), p75: quantile(values, .75), p90: quantile(values, .9), max: values.length ? Math.max(...values) : null, counts: Object.fromEntries([...new Set(values)].sort((a, b) => a - b).map((item) => [String(item), values.filter((value) => value === item).length])) }; }
function countBy(values) { return Object.fromEntries([...values.reduce((map, value) => (map.set(value, (map.get(value) || 0) + 1), map), new Map())].sort((a, b) => b[1] - a[1] || String(a[0]).localeCompare(String(b[0])))); }

function noActionCause(terminal, evidence) {
  if (terminal === "SOURCE_UNAVAILABLE") return Number.isInteger(evidence.ask_capacity_floor_cents)
    ? { primary: "REPLAY_SOURCE_UNAVAILABLE_DESPITE_ASK_FLOOR", level: "SOURCE" }
    : { primary: "NO_FORMED_CAPACITY_QUALIFYING_ASK", level: "SOURCE" };
  const map = {
    SURVIVING_SHAPES_DISAGREE_OR_LIBRARY_GAP: ["SHAPE_SET_NEVER_COLLAPSED_OR_LIBRARY_GAP", "MACRO"],
    OBSERVED_DESCENT_OUTSIDE_SURVIVING_SHAPE_TRAINING_SUPPORT: ["OBSERVED_DESCENT_INVALIDATED_SURVIVING_LIBRARY_SUPPORT", "MACRO"],
    ALL_SURVIVING_SHAPES_SAY_LOWER: ["FLOOR_CONSENSUS_NEVER_REACHED", "MICRO"],
    FLOOR_CONSENSUS_BUT_CURRENT_ASK_IS_ABOVE_OBSERVED_LOW: ["ASK_DID_NOT_RETURN_AFTER_CONSENSUS", "MICRO_MICRO"],
    FLOOR_CONSENSUS_BUT_SIBLING_DIRECTION_NOT_INDEPENDENTLY_OBSERVED: ["PAIR_SIBLING_EVIDENCE_INSUFFICIENT", "PAIR_MICRO"],
    FLOOR_CONSENSUS_BUT_STABLE_SAME_PRICE_ASK_LACKS_SIGNING_SUPPORT: ["STABLE_ASK_SIGNING_SUPPORT_INSUFFICIENT", "MICRO"],
    FLOOR_CONSENSUS_BUT_MICRO_MICRO_NOT_READY: ["MICRO_MICRO_TRANSITION_NOT_READY", "MICRO_MICRO"],
    FLOOR_CONSENSUS_AWAITING_FRESH_OWN_BOOK_RECEIPT: ["FRESH_OWN_BOOK_NOT_RECEIVED", "MICRO_MICRO"],
  };
  const item = map[terminal] || [terminal || "UNNAMED_NO_ACTION", "UNRESOLVED"];
  return { primary: item[0], level: item[1] };
}

function ceilingCounts(events) {
  return {
    events: events.length,
    absolute_traded_low: events.filter((event) => event.ceilings.absolute_traded_low).length,
    traded_low_print_size_at_least_five: events.filter((event) => event.ceilings.traded_low_print_size_at_least_five).length,
    capacity_proven_ask_floor: events.filter((event) => event.ceilings.capacity_proven_ask_floor).length,
    lowest_seller_aggressed_trade_floor: events.filter((event) => event.ceilings.lowest_seller_aggressed_trade_floor).length,
    maker_reachable: events.filter((event) => event.ceilings.maker_reachable).length,
  };
}

function eventPerformance(events) {
  const completed = events.filter((event) => event.completed_pair);
  const underPar = completed.filter((event) => event.pair_under_par);
  const bothBelow = completed.filter((event) => event.both_legs_strictly_below_close);
  return {
    D: events.length,
    no_credited_leg_events: events.filter((event) => event.fill_pattern === "NO_CREDITED_LEG").length,
    naked_single_events: events.filter((event) => event.fill_pattern === "NAKED_SINGLE").length,
    completed_pairs: completed.length,
    pairs_under_par: underPar.length,
    both_legs_strictly_below_close: bothBelow.length,
    under_par_and_both_legs_strictly_below_close: events.filter((event) => event.pair_under_par && event.both_legs_strictly_below_close).length,
    both_closes_available: events.filter((event) => event.both_closes_available).length,
    both_closes_properly_late: events.filter((event) => event.both_closes_properly_late).length,
    completed_to_under_par_drop: completed.length - underPar.length,
    under_par_to_final_drop: underPar.length - events.filter((event) => event.pair_under_par && event.both_legs_strictly_below_close).length,
    under_par_final_drop_reasons: countBy(underPar.filter((event) => !event.both_legs_strictly_below_close).map((event) => event.both_closes_available ? event.close_failure_reason : "CLOSE_UNAVAILABLE")),
  };
}

function legSummary(legs) {
  const acted = legs.filter((leg) => leg.acted);
  const credited = legs.filter((leg) => leg.credited);
  const late = legs.filter((leg) => leg.close_status === "PROPERLY_LATE_CLOSE");
  return {
    legs: legs.length,
    close_available: legs.filter((leg) => Number.isInteger(leg.close_cents)).length,
    close_unavailable: legs.filter((leg) => !Number.isInteger(leg.close_cents)).length,
    properly_late_close: late.length,
    close_older_than_300_seconds: legs.filter((leg) => leg.close_status === "CLOSE_TOO_EARLY_FOR_STRICT_SLICE").length,
    acted: acted.length,
    credited: credited.length,
    no_action: legs.length - acted.length,
    entry_minus_ask_floor_cents: distribution(credited.map((leg) => leg.entry_minus_ask_floor_cents).filter(Number.isInteger)),
    entry_minus_traded_low_cents: distribution(credited.map((leg) => leg.entry_minus_traded_low_cents).filter(Number.isInteger)),
    entry_minus_close_cents: distribution(credited.map((leg) => leg.entry_minus_close_cents).filter(Number.isInteger)),
    properly_late_close_slice: {
      legs: late.length,
      acted: late.filter((leg) => leg.acted).length,
      credited: late.filter((leg) => leg.credited).length,
      entry_minus_ask_floor_cents: distribution(late.filter((leg) => leg.credited).map((leg) => leg.entry_minus_ask_floor_cents).filter(Number.isInteger)),
      entry_minus_traded_low_cents: distribution(late.filter((leg) => leg.credited).map((leg) => leg.entry_minus_traded_low_cents).filter(Number.isInteger)),
      entry_minus_close_cents: distribution(late.filter((leg) => leg.credited).map((leg) => leg.entry_minus_close_cents).filter(Number.isInteger)),
    },
    nonaction_primary_causes: countBy(legs.filter((leg) => !leg.acted).map((leg) => leg.nonaction_cause.primary)),
    nonaction_levels: countBy(legs.filter((leg) => !leg.acted).map((leg) => leg.nonaction_cause.level)),
  };
}

function main() {
  const v7 = jsonlGz(v7LedgerPath);
  const v8Legs = jsonlGz(v8LegPath);
  const v8Events = jsonlGz(v8EventPath);
  const ceilingSource = json(v8CeilingPath);
  const lateLaw = json(lateCloseLawPath);
  ensure(lateLaw.book_denominator_census.freshness_rule_seconds === LATE_CLOSE_SECONDS, "late-close threshold is not the inherited 300-second law");
  ensure(v7.length === 804 && v8Legs.length === 1608 && v8Events.length === 804, "population mismatch");
  const v8LegByKey = new Map(v8Legs.map((leg) => [leg.leg_identity, leg]));
  const v8EventById = new Map(v8Events.map((event) => [event.event_id, event]));
  const events = [];
  const legs = [];
  for (const prior of v7) {
    const floorEvent = v8EventById.get(prior.event_id);
    ensure(floorEvent, `missing V8 event ${prior.event_id}`);
    const eventLegs = [];
    for (const [legId, old] of Object.entries(prior.legs).sort(([a], [b]) => a.localeCompare(b))) {
      const evidence = v8LegByKey.get(`${prior.event_id}|${legId}`);
      ensure(evidence, `missing V8 leg ${prior.event_id}/${legId}`);
      const acted = old.proposed_entry_cents !== null;
      const credited = old.honest_credited_entry_cents !== null;
      const closeAge = evidence.latest_lawful_print?.seconds_before_guarded_right_edge ?? null;
      const closeAvailable = Number.isInteger(evidence.own_window1_close_cents);
      if (closeAvailable) {
        ensure(evidence.latest_lawful_print_matches_frozen_close === true, `close is not latest lawful print ${evidence.leg_identity}`);
        ensure(Number.isFinite(closeAge) && closeAge >= 0, `close age unavailable ${evidence.leg_identity}`);
      }
      const closeStatus = !closeAvailable ? "CLOSE_UNAVAILABLE" : closeAge <= LATE_CLOSE_SECONDS ? "PROPERLY_LATE_CLOSE" : "CLOSE_TOO_EARLY_FOR_STRICT_SLICE";
      const cause = acted ? { primary: "ACTED", level: "ACTION" } : noActionCause(old.terminal_reason, evidence);
      const row = {
        leg_identity: evidence.leg_identity,
        event_id: prior.event_id,
        category: prior.category,
        starting_price_split: prior.starting_price_split,
        price_region: old.price_region,
        leg_id: legId,
        ticker: old.ticker,
        acted,
        credited,
        fill_class: old.honest_fill_class,
        entry_cents: old.honest_credited_entry_cents,
        action_timestamp_epoch: old.action_timestamp_epoch,
        ask_capacity_floor_cents: evidence.ask_capacity_floor_cents,
        traded_low_cents: evidence.lowest_traded_price_cents,
        traded_low_proof: evidence.lowest_traded_price_proof,
        entry_minus_ask_floor_cents: credited && Number.isInteger(evidence.ask_capacity_floor_cents) ? old.honest_credited_entry_cents - evidence.ask_capacity_floor_cents : null,
        entry_minus_traded_low_cents: credited && Number.isInteger(evidence.lowest_traded_price_cents) ? old.honest_credited_entry_cents - evidence.lowest_traded_price_cents : null,
        close_cents: evidence.own_window1_close_cents,
        close_status: closeStatus,
        close_print: evidence.latest_lawful_print,
        close_seconds_before_guarded_right: closeAge,
        late_close_threshold_seconds: LATE_CLOSE_SECONDS,
        entry_minus_close_cents: credited && closeAvailable ? old.honest_credited_entry_cents - evidence.own_window1_close_cents : null,
        nonaction_terminal_reason: acted ? null : old.terminal_reason,
        nonaction_cause: cause,
        V7_policy_receipt: { action_book: old.action_book, placement: old.placement, predicates: old.predicates },
      };
      legs.push(row); eventLegs.push(row);
    }
    const completed = eventLegs.every((leg) => leg.credited);
    const combined = completed ? eventLegs.reduce((sum, leg) => sum + leg.entry_cents, 0) : null;
    const bothClose = eventLegs.every((leg) => Number.isInteger(leg.close_cents));
    const bothBelow = completed && bothClose && eventLegs.every((leg) => leg.entry_cents < leg.close_cents);
    const equal = eventLegs.filter((leg) => leg.credited && Number.isInteger(leg.close_cents) && leg.entry_cents === leg.close_cents).length;
    const above = eventLegs.filter((leg) => leg.credited && Number.isInteger(leg.close_cents) && leg.entry_cents > leg.close_cents).length;
    events.push({
      event_id: prior.event_id,
      category: prior.category,
      starting_price_split: prior.starting_price_split,
      leg_ids: eventLegs.map((leg) => leg.leg_identity),
      credited_leg_count: eventLegs.filter((leg) => leg.credited).length,
      fill_pattern: completed ? "COMPLETED_PAIR" : eventLegs.some((leg) => leg.credited) ? "NAKED_SINGLE" : "NO_CREDITED_LEG",
      completed_pair: completed,
      combined_entry_cents: combined,
      pair_under_par: combined !== null && combined < 100,
      both_closes_available: bothClose,
      both_closes_properly_late: eventLegs.every((leg) => leg.close_status === "PROPERLY_LATE_CLOSE"),
      both_legs_strictly_below_close: bothBelow,
      close_failure_reason: !completed ? "PAIR_INCOMPLETE" : !bothClose ? "CLOSE_UNAVAILABLE" : above > 0 ? "AT_LEAST_ONE_ENTRY_ABOVE_CLOSE" : equal > 0 ? "AT_LEAST_ONE_ENTRY_EQUALS_CLOSE" : "NONE",
      ceilings: {
        absolute_traded_low: floorEvent.any_trade_low_price_ceiling_member,
        traded_low_print_size_at_least_five: floorEvent.any_trade_size5_floor_ceiling_member,
        capacity_proven_ask_floor: floorEvent.ask_capacity_take_ceiling_member,
        lowest_seller_aggressed_trade_floor: floorEvent.seller_aggressed_trade_floor_ceiling_member,
        maker_reachable: floorEvent.ask_target_seller_print_maker_ceiling_member,
      },
    });
  }
  ensure(legs.length === 1608 && events.length === 804, "output population mismatch");
  ensure(legs.filter((leg) => leg.acted).length === 628 && legs.filter((leg) => !leg.acted).length === 980, "V7 action identity mismatch");
  ensure(legs.filter((leg) => Number.isInteger(leg.close_cents)).length === 1307, "corrected close availability mismatch");
  ensure(legs.filter((leg) => leg.close_status === "PROPERLY_LATE_CLOSE").length === 835, "late close leg count mismatch");
  ensure(events.filter((event) => event.both_closes_properly_late).length === 305, "late close pair count mismatch");
  const overallCeilings = ceilingCounts(events);
  ensure(overallCeilings.absolute_traded_low === 580 && overallCeilings.traded_low_print_size_at_least_five === 558 && overallCeilings.capacity_proven_ask_floor === 516 && overallCeilings.lowest_seller_aggressed_trade_floor === 371 && overallCeilings.maker_reachable === 253, "ceiling mismatch");
  const eventGroups = new Map();
  for (const event of events) { const key = `${event.category}|${event.starting_price_split}`; if (!eventGroups.has(key)) eventGroups.set(key, []); eventGroups.get(key).push(event); }
  const legGroups = new Map();
  for (const leg of legs) { const key = `${leg.category}|${leg.price_region}`; if (!legGroups.has(key)) legGroups.set(key, []); legGroups.get(key).push(leg); }
  const eventPartitions = [...eventGroups].sort(([a], [b]) => a.localeCompare(b)).map(([key, rows]) => { const [category, starting_price_split] = key.split("|"); const late = rows.filter((event) => event.both_closes_properly_late); return { category, starting_price_split, thin: rows.length < 10, all_population: { ...ceilingCounts(rows), ...eventPerformance(rows) }, properly_late_close_pair_cohort: { ...ceilingCounts(late), ...eventPerformance(late) } }; });
  const legPartitions = [...legGroups].sort(([a], [b]) => a.localeCompare(b)).map(([key, rows]) => { const [category, price_region] = key.split("|"); return { category, price_region, thin: rows.length < 10, ...legSummary(rows) }; });
  const lateEvents = events.filter((event) => event.both_closes_properly_late);
  const lateEventIds = new Set(lateEvents.map((event) => event.event_id));
  const latePairLegs = legs.filter((leg) => lateEventIds.has(leg.event_id));
  const lateIndividualLegs = legs.filter((leg) => leg.close_status === "PROPERLY_LATE_CLOSE");
  const closeAges = legs.filter((leg) => Number.isFinite(leg.close_seconds_before_guarded_right)).map((leg) => leg.close_seconds_before_guarded_right);
  const allPerformance = eventPerformance(events);
  const summary = {
    schema_version: "WINDOW1_DYNAMIC_RENARROW_POPULATION_V9_CORRECTED_DUAL_FLOOR",
    policy_stream: "BYTE_BOUND_TO_V7; NO DECISION OR FILL REPLAY",
    population: { events: 804, legs: 1608 },
    close_law: { unavailable_is_null_not_zero: true, properly_late_threshold_seconds: LATE_CLOSE_SECONDS, threshold_provenance: relative(lateCloseLawPath), threshold_role: "borrowed existing fresh-at-close evidence law; not newly fitted", close_available_legs: 1307, close_unavailable_legs: 301, properly_late_close_legs: 835, both_closes_available_events: events.filter((event) => event.both_closes_available).length, both_closes_properly_late_events: lateEvents.length, close_age_seconds_distribution: distribution(closeAges) },
    floor_law: { objective: "lowest lawful true traded price in guarded Window 1", execution: "lowest qualifying ask with inherited dwell and capacity law", report_both: true },
    all_population: { ceilings: overallCeilings, event_performance: allPerformance, leg_funnel: legSummary(legs) },
    properly_late_close_individual_leg_slice: legSummary(lateIndividualLegs),
    properly_late_close_pair_cohort: { ceilings: ceilingCounts(lateEvents), event_performance: eventPerformance(lateEvents), leg_funnel: legSummary(latePairLegs) },
    event_partitions_by_category_and_starting_price_split: eventPartitions,
    leg_partitions_by_category_and_price_region: legPartitions,
    scoring_exclusions: { forecast: false, fee_test: false, new_instrument: false, holdout: false, live: false },
  };
  const noActions = legs.filter((leg) => !leg.acted);
  const nonaction = { schema_version: "WINDOW1_DYNAMIC_RENARROW_V9_NONACTION_CAUSES", total_nonacting_legs: noActions.length, exact_terminal_reasons: countBy(noActions.map((leg) => leg.nonaction_terminal_reason)), primary_causes: countBy(noActions.map((leg) => leg.nonaction_cause.primary)), levels: countBy(noActions.map((leg) => leg.nonaction_cause.level)), by_category_and_price_region: legPartitions.map((cell) => ({ category: cell.category, price_region: cell.price_region, legs: cell.legs, no_action: cell.no_action, primary_causes: cell.nonaction_primary_causes, levels: cell.nonaction_levels })) };
  const funnel = { schema_version: "WINDOW1_DYNAMIC_RENARROW_V9_FUNNEL", all_population: { legs: 1608, acted: legs.filter((leg) => leg.acted).length, action_drop: noActions.length, action_drop_causes: nonaction.primary_causes, credited: legs.filter((leg) => leg.credited).length, acted_to_credited_drop: legs.filter((leg) => leg.acted && !leg.credited).length, event_patterns: countBy(events.map((event) => event.fill_pattern)), completed_pairs: allPerformance.completed_pairs, completed_to_under_par_drop: allPerformance.completed_to_under_par_drop, pairs_under_par: allPerformance.pairs_under_par, under_par_to_final_drop: allPerformance.under_par_to_final_drop, under_par_final_drop_reasons: allPerformance.under_par_final_drop_reasons, final_under_par_and_both_below_close: allPerformance.under_par_and_both_legs_strictly_below_close }, properly_late_close_pair_cohort: { eligible_events: lateEvents.length, eligible_legs: lateEvents.length * 2, ...eventPerformance(lateEvents) } };
  ensure(Object.values(nonaction.primary_causes).reduce((sum, count) => sum + count, 0) === 980, "nonaction cause conservation failed");
  ensure(Object.values(funnel.all_population.event_patterns).reduce((sum, count) => sum + count, 0) === 804, "event funnel conservation failed");
  fs.mkdirSync(output, { recursive: true });
  fs.writeFileSync(path.join(output, "POPULATION_LEG_LEDGER.jsonl.gz"), gzipJsonl(legs));
  fs.writeFileSync(path.join(output, "POPULATION_EVENT_LEDGER.jsonl.gz"), gzipJsonl(events));
  fs.writeFileSync(path.join(output, "POPULATION_SUMMARY.json"), canonical(summary));
  fs.writeFileSync(path.join(output, "NONACTION_CAUSE_CENSUS.json"), canonical(nonaction));
  fs.writeFileSync(path.join(output, "FUNNEL_RECEIPT.json"), canonical(funnel));
  fs.writeFileSync(path.join(output, "V7_SUPERSESSION_BINDING.json"), canonical({ v7_commit: "0ec177445c04709cb147617a6419c3ea981585e5", v7_ledger: { path: relative(v7LedgerPath), sha256: hashFile(v7LedgerPath) }, v7_conservation: { path: relative(v7ConservationPath), sha256: hashFile(v7ConservationPath) }, V7_policy_stream_preserved: true, superseded_fields: ["blank-close coercion", "ask floor used as objective traded floor", "floor-relative gaps and ceiling comparisons"], V9_change: "measurement-only reaccounting" }));
  fs.writeFileSync(path.join(output, "REPORT.md"), `# Window-1 V9 corrected-floor population reaccounting\n\nV7 policy actions and fill classes are frozen. V9 changes measurement only: blank closes remain unavailable, the 300-second inherited fresh-at-close law defines the strict late-close slice, and entries are compared separately with qualifying asks and true traded lows.\n\nSee POPULATION_SUMMARY.json, FUNNEL_RECEIPT.json, NONACTION_CAUSE_CENSUS.json and the two compressed ledgers in this directory.\n`);
  const sources = [v7LedgerPath, v7ConservationPath, v8LegPath, v8EventPath, v8CeilingPath, lateCloseLawPath, __filename, testPath];
  fs.writeFileSync(path.join(output, "SOURCE_HASH_MANIFEST.json"), canonical({ schema_version: "WINDOW1_DYNAMIC_RENARROW_V9_SOURCE_MANIFEST", files: Object.fromEntries(sources.map((file) => [relative(file), { sha256: hashFile(file), bytes: fs.statSync(file).size }])), forbidden_access: { holdout: false, live: false, network: false, orders: false, positions: false, exits: false, settlement: false, DCA: false, Window2: false } }));
  const artifacts = fs.readdirSync(output).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  fs.writeFileSync(path.join(output, "ARTIFACT_HASH_MANIFEST.json"), canonical({ schema_version: "WINDOW1_DYNAMIC_RENARROW_V9_ARTIFACT_MANIFEST", files: Object.fromEntries(artifacts.map((name) => [name, { sha256: hashFile(path.join(output, name)), bytes: fs.statSync(path.join(output, name)).size }])) }));
  process.stdout.write(canonical({ status: "BUILT", output: relative(output), all_population: summary.all_population, late_close: summary.properly_late_close_pair_cohort, nonaction: nonaction.primary_causes }));
}

try { main(); } catch (error) { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; }
