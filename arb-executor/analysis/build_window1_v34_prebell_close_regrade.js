#!/usr/bin/env node
"use strict";

const child = require("child_process");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const argv = process.argv.slice(2);
const arg = (name, fallback) => { const i = argv.indexOf(name); return i < 0 ? fallback : argv[i + 1]; };
const repo = path.resolve(arg("--repo", "."));
const output = path.resolve(arg("--output", path.join(repo, ".claude/window1_live_v4_replay/v34_prebell_close_regrade_20260805")));
const compare = arg("--compare", null);

const V34_COMMIT = "b430bcfff51f89c9466e77b798d4ac5d9fff15ea";
const CC_COMMIT = "50ce0f4940c461cf0b6fa1b79000d96b335cd601";
const FLOOR_COMMIT = "452eb3354ee08afe0c94cfa3bedb996f73d8b248";
const BASE = ".claude/window1_live_v4_replay/v34_dual_side_residency_machine_trading_phase_20260805";
const STRICT_PATH = `${BASE}/STRICT_EVENT_LEDGER.jsonl.gz`;
const CENSUS_PATH = `${BASE}/CENSUS_PRICED_EVENT_LEDGER.jsonl.gz`;
const CLOSE_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/INDEPENDENT_CLOSE_AUDIT_1608.csv";
const OFFER_PATH = ".claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/CLOSE_AUDIT_AND_JOINT_CEILING_SUMMARY.json";
const FLOOR_PATH = ".claude/window1_live_v4_replay/trade_floor_correction_v8_20260802/DUAL_FLOOR_LEG_LEDGER.jsonl.gz";
const R3_JOINT = 68;

function ensure(value, message) { if (!value) throw new Error(message); }
function sha(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function gitShow(commit, rel) { return child.execFileSync("git", ["show", `${commit}:${rel}`], { cwd: repo, maxBuffer: 256 * 1024 * 1024 }); }
function requireCommit(commit) { ensure(child.execFileSync("git", ["rev-parse", "--verify", `${commit}^{commit}`], { cwd: repo, encoding: "utf8" }).trim() === commit, `missing commit ${commit}`); child.execFileSync("git", ["cat-file", "-e", `${commit}^{commit}`], { cwd: repo }); }
function gunzipRows(bytes) { const text = zlib.gunzipSync(bytes).toString("utf8").trim(); return text ? text.split(/\r?\n/).map(JSON.parse) : []; }
function gzipRows(rows) { return zlib.gzipSync(Buffer.from(`${rows.map(JSON.stringify).join("\n")}\n`), { level: 9, mtime: 0 }); }
function parseCsv(bytes) { const lines = bytes.toString("utf8").trimEnd().split(/\r?\n/), header = lines.shift().split(","); return lines.filter(Boolean).map((line) => Object.fromEntries(line.split(",").map((value, index) => [header[index], value]))); }
function integer(value) { if (value === "" || value === null || value === undefined) return null; const n = Number(value); return Number.isInteger(n) ? n : null; }
function group(rows, fn) { const out = new Map(); for (const row of rows) { const key = fn(row); if (!out.has(key)) out.set(key, []); out.get(key).push(row); } return out; }
function countBy(rows, fn) { const out = {}; for (const row of rows) { const key = String(fn(row)); out[key] = (out[key] || 0) + 1; } return Object.fromEntries(Object.entries(out).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))); }
function quantile(values, p) { const x = values.filter(Number.isFinite).sort((a, b) => a - b); return x.length ? x[Math.floor((x.length - 1) * p)] : null; }
function distribution(values) { const x = values.filter(Number.isFinite); return { denominator: values.length, numeric_n: x.length, null_n: values.length - x.length, min: x.length ? Math.min(...x) : null, p25: quantile(x, .25), median: quantile(x, .5), p75: quantile(x, .75), p90: quantile(x, .9), max: x.length ? Math.max(...x) : null, total_cents: x.reduce((sum, value) => sum + value, 0) }; }
function safeClean(dir) { const resolved = path.resolve(dir); ensure(path.basename(resolved).toLowerCase().includes("v34"), `unsafe output ${resolved}`); ensure(resolved !== repo && resolved !== path.parse(resolved).root, `unsafe output ${resolved}`); fs.rmSync(resolved, { recursive: true, force: true }); fs.mkdirSync(resolved, { recursive: true }); }
function write(name, bytes) { fs.writeFileSync(path.join(output, name), bytes); }
function fileHash(file) { return sha(fs.readFileSync(file)); }

function sellerFloor(row) {
  const value = row.seller_aggressed_trade_floor;
  if (Number.isInteger(value)) return value;
  if (Number.isInteger(value?.price_cents)) return value.price_cents;
  return null;
}

function makerFloor(row) {
  const values = [integer(row.ask_capacity_floor_cents), sellerFloor(row)].filter(Number.isInteger);
  return values.length ? Math.min(...values) : null;
}

function buildOffer(events, closeByTicker, floorByLeg) {
  return events.map((event) => {
    const legs = Object.values(event.legs).map((leg) => {
      const close = closeByTicker.get(leg.ticker), floor = floorByLeg.get(leg.leg_identity), maker = makerFloor(floor);
      return { leg_identity: leg.leg_identity, ticker: leg.ticker, prebell_close_cents: close?.audited_close_cents ?? null, maker_floor_cents: maker, floor_strictly_below_close: Number.isInteger(maker) && Number.isInteger(close?.audited_close_cents) ? maker < close.audited_close_cents : null };
    });
    const ready = legs.every((leg) => Number.isInteger(leg.prebell_close_cents) && Number.isInteger(leg.maker_floor_cents));
    const sum = ready ? legs.reduce((value, leg) => value + leg.maker_floor_cents, 0) : null;
    return { event_id: event.event_id, category: event.category, starting_price_split: event.starting_price_split, legs, both_close_and_floor_available: ready, both_floors_strictly_below_close: ready && legs.every((leg) => leg.floor_strictly_below_close), maker_floor_sum_cents: sum };
  });
}

function offerMetrics(rows) {
  const eligible = rows.filter((row) => row.both_floors_strictly_below_close);
  return { D: rows.length, both_close_and_floor_available: rows.filter((row) => row.both_close_and_floor_available).length, both_floors_strictly_below_close_any_price: eligible.length, LE_93: eligible.filter((row) => row.maker_floor_sum_cents <= 93).length, LE_95: eligible.filter((row) => row.maker_floor_sum_cents <= 95).length, LE_97: eligible.filter((row) => row.maker_floor_sum_cents <= 97).length, LT_100: eligible.filter((row) => row.maker_floor_sum_cents < 100).length };
}

function regrade(events, closeByTicker, floorByLeg, label) {
  return events.map((event) => {
    const legs = Object.fromEntries(Object.entries(event.legs).map(([id, leg]) => {
      const close = closeByTicker.get(leg.ticker), floor = floorByLeg.get(leg.leg_identity), maker = makerFloor(floor);
      const delta = leg.credited && Number.isInteger(close?.audited_close_cents) ? leg.entry_cents - close.audited_close_cents : null;
      const regret = leg.credited && Number.isInteger(maker) ? leg.entry_cents - maker : null;
      return [id, { leg_identity: leg.leg_identity, ticker: leg.ticker, category: leg.category, price_region: leg.price_region, acted: leg.acted, credited: leg.credited, entry_cents: leg.entry_cents, fill_class: leg.fill_class, action_timestamp_epoch: leg.action_timestamp_epoch, fill_timestamp_epoch: leg.fill_timestamp_epoch, frozen_v34_semantics: "BYTE_IDENTICAL_SOURCE_ROW", prebell_close_cents: close?.audited_close_cents ?? null, prebell_close_timestamp_utc: close?.audited_close_ts_utc || null, prebell_close_aggressor_side: close?.close_aggressor_side || null, guarded_right_ts: floor.guarded_right_ts, entry_minus_prebell_close_cents: delta, maker_floor_cents: maker, entry_minus_prebell_maker_floor_cents: regret, fill_after_guarded_right_edge: leg.credited && Number.isFinite(leg.fill_timestamp_epoch) ? leg.fill_timestamp_epoch > floor.guarded_right_ts : null }];
    }));
    const values = Object.values(legs), completed = values.every((leg) => leg.credited), combined = completed ? values.reduce((sum, leg) => sum + leg.entry_cents, 0) : null, closesAvailable = values.every((leg) => Number.isInteger(leg.prebell_close_cents)), bothBelow = completed && closesAvailable && values.every((leg) => leg.entry_cents < leg.prebell_close_cents), underPar = completed && combined < 100, deltas = values.map((leg) => leg.entry_minus_prebell_close_cents);
    return { event_id: event.event_id, category: event.category, starting_price_split: event.starting_price_split, mode: label, frozen_source_mode: event.mode, legs, completed_pair: completed, combined_entry_cents: combined, pair_under_par: underPar, both_prebell_closes_available: closesAvailable, both_legs_strictly_below_prebell_close: bothBelow, joint_objective_pass: underPar && bothBelow, carried_pair: completed && closesAvailable && deltas.some((value) => value > 0) && deltas.some((value) => value < 0), close_equal_pair: completed && closesAvailable && deltas.some((value) => value === 0), any_fill_after_guarded_right_edge: values.some((leg) => leg.fill_after_guarded_right_edge === true) };
  });
}

function metrics(events, offer) {
  const legs = events.flatMap((event) => Object.values(event.legs)), joint = events.filter((event) => event.joint_objective_pass).length;
  return { D: events.length, legs: legs.length, R3_joint_floor: R3_JOINT, recut_map_LT_100_offer: offer.LT_100, acted_legs: legs.filter((leg) => leg.acted).length, credited_legs: legs.filter((leg) => leg.credited).length, completed_pairs: events.filter((event) => event.completed_pair).length, gradeable_completed_pairs: events.filter((event) => event.completed_pair && event.both_prebell_closes_available).length, completed_pairs_close_unavailable: events.filter((event) => event.completed_pair && !event.both_prebell_closes_available).length, pairs_under_par: events.filter((event) => event.pair_under_par).length, both_legs_strictly_below_prebell_close: events.filter((event) => event.both_legs_strictly_below_prebell_close).length, joint_objective_pairs: joint, delta_joint_vs_R3_68: joint - R3_JOINT, gap_to_recut_map_LT_100_offer: offer.LT_100 - joint, carried_pairs: events.filter((event) => event.carried_pair).length, close_equal_pairs: events.filter((event) => event.close_equal_pair).length, credited_legs_after_guarded_right_edge: legs.filter((leg) => leg.fill_after_guarded_right_edge === true).length, events_with_fill_after_guarded_right_edge: events.filter((event) => event.any_fill_after_guarded_right_edge).length };
}

const TIERS = [{ id: "LE_93", test: (value) => value <= 93 }, { id: "LE_95", test: (value) => value <= 95 }, { id: "LE_97", test: (value) => value <= 97 }, { id: "LT_100", test: (value) => value < 100 }, { id: "ANY_PRICE", test: () => true }];
function frontierRows(events, offerRows) {
  return Object.fromEntries(TIERS.map((tier) => {
    const offer = tier.id === "ANY_PRICE" ? offerRows.filter((row) => row.both_floors_strictly_below_close).length : offerRows.filter((row) => row.both_floors_strictly_below_close && tier.test(row.maker_floor_sum_cents)).length;
    const completed = events.filter((event) => event.completed_pair && tier.test(event.combined_entry_cents)).length, joint = events.filter((event) => event.joint_objective_pass && tier.test(event.combined_entry_cents)).length;
    return [tier.id, { fixed_denominator: events.length, completed_pairs: completed, joint_objective_pairs: joint, recut_map_offer: offer, joint_gap_to_offer: offer - joint, joint_capture_of_offer_rate: offer ? joint / offer : null }];
  }));
}

function score(events, offers, label) {
  const offer = offerMetrics(offers), byOfferCell = group(offers, (row) => `${row.category}|${row.starting_price_split}`);
  return { label, aggregate: metrics(events, offer), category_x_starting_price_region: [...group(events, (event) => `${event.category}|${event.starting_price_split}`).entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([cell, rows]) => ({ cell, metrics: metrics(rows, offerMetrics(byOfferCell.get(cell) || [])) })) };
}

function frontier(events, offers, label) {
  const byOfferCell = group(offers, (row) => `${row.category}|${row.starting_price_split}`);
  return { label, R3_joint_floor: R3_JOINT, recut_map_offer: offerMetrics(offers), aggregate: frontierRows(events, offers), category_x_starting_price_region: [...group(events, (event) => `${event.category}|${event.starting_price_split}`).entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([cell, rows]) => ({ cell, frontier: frontierRows(rows, byOfferCell.get(cell) || []) })) };
}

function regret(events, label) {
  const rows = events.flatMap((event) => Object.values(event.legs).map((leg) => ({ mode: label, event_id: event.event_id, leg_identity: leg.leg_identity, category: leg.category, price_region: leg.price_region, credited: leg.credited, entry_cents: leg.entry_cents, prebell_maker_floor_cents: leg.maker_floor_cents, regret_cents: leg.entry_minus_prebell_maker_floor_cents, loss_attribution: leg.credited ? Number.isInteger(leg.maker_floor_cents) ? leg.entry_minus_prebell_maker_floor_cents < 0 ? "CREDITED_BETTER_THAN_RECORDED_PREBELL_MAKER_FLOOR" : "CREDITED_VS_PREBELL_MAKER_FLOOR" : "CREDITED_PREBELL_FLOOR_UNAVAILABLE" : leg.acted ? "RESTED_UNFILLED" : "NEVER_ACTED" })));
  return { label, law: "grade-only regret = frozen credited entry minus pre-bell maker_floor=min(qualifying ask floor,seller-aggressed traded low); uncredited legs remain null; no fill or policy reconstruction", aggregate: distribution(rows.map((row) => row.regret_cents)), loss_attribution: countBy(rows, (row) => row.loss_attribution), category_x_price_region: [...group(rows, (row) => `${row.category}|${row.price_region}`).entries()].sort((a, b) => a[0].localeCompare(b[0])).map(([cell, values]) => ({ cell, regret: distribution(values.map((row) => row.regret_cents)), loss_attribution: countBy(values, (row) => row.loss_attribution) })), rows };
}

async function main() {
  for (const commit of [V34_COMMIT, CC_COMMIT, FLOOR_COMMIT]) requireCommit(commit);
  safeClean(output);
  const strictBytes = gitShow(V34_COMMIT, STRICT_PATH), censusBytes = gitShow(V34_COMMIT, CENSUS_PATH), closeBytes = gitShow(CC_COMMIT, CLOSE_PATH), offerBytes = gitShow(CC_COMMIT, OFFER_PATH), floorBytes = gitShow(FLOOR_COMMIT, FLOOR_PATH);
  const strictSource = gunzipRows(strictBytes), censusSource = gunzipRows(censusBytes), closeSource = parseCsv(closeBytes), floorSource = gunzipRows(floorBytes), offerSource = JSON.parse(offerBytes);
  ensure(strictSource.length === 804 && censusSource.length === 804, "frozen V34 D mismatch"); ensure(closeSource.length === 1608 && floorSource.length === 1608, "leg source denominator mismatch");
  const closeByTicker = new Map(closeSource.map((row) => [row.ticker, { ...row, audited_close_cents: integer(row.audited_close_cents) }])), floorByLeg = new Map(floorSource.map((row) => [row.leg_identity, row]));
  ensure(closeByTicker.size === 1608 && floorByLeg.size === 1608, "unique leg identity mismatch");
  const offers = buildOffer(strictSource, closeByTicker, floorByLeg), offered = offerMetrics(offers), expected = offerSource.item2_joint_achievable_ceiling;
  ensure(offered.LE_93 === expected.by_tier["<=93"] && offered.LE_95 === expected.by_tier["<=95"] && offered.LE_97 === expected.by_tier["<=97"] && offered.LT_100 === expected.by_tier["<100"] && offered.LT_100 === expected.total_events, "CC re-cut offer reproduction mismatch");
  const strict = regrade(strictSource, closeByTicker, floorByLeg, "STRICT_LAW"), census = regrade(censusSource, closeByTicker, floorByLeg, "CENSUS_PRICED");
  const strictScore = score(strict, offers, "STRICT_LAW"), censusScore = score(census, offers, "CENSUS_PRICED"), strictFrontier = frontier(strict, offers, "STRICT_LAW"), censusFrontier = frontier(census, offers, "CENSUS_PRICED"), strictRegret = regret(strict, "STRICT_LAW"), censusRegret = regret(census, "CENSUS_PRICED");
  const identity = { source_commit: V34_COMMIT, strict_source: { path: STRICT_PATH, sha256: sha(strictBytes), bytes: strictBytes.length, events: strictSource.length }, census_source: { path: CENSUS_PATH, sha256: sha(censusBytes), bytes: censusBytes.length, events: censusSource.length }, policy_replay_invocations: 0, tape_reads: 0, action_changes: 0, fill_changes: 0, fill_class_changes: 0, event_identity_changes: 0, strict_source_semantic_hash: sha(Buffer.from(JSON.stringify(strictSource))), census_source_semantic_hash: sha(Buffer.from(JSON.stringify(censusSource))), rule: "GRADE_ONLY; FROZEN_B430BCF_ACTIONS_FILLS_PRICES_TIMESTAMPS_AND_CLASSES" };
  const binding = { close: { commit: CC_COMMIT, path: CLOSE_PATH, sha256: sha(closeBytes), bytes: closeBytes.length, rows: closeSource.length, available: closeSource.filter((row) => integer(row.audited_close_cents) !== null).length, unavailable: closeSource.filter((row) => integer(row.audited_close_cents) === null).length, law: "last true print inside guarded pre-bell Window 1 [left,right]" }, recut_offer: { commit: CC_COMMIT, path: OFFER_PATH, sha256: sha(offerBytes), bytes: offerBytes.length, reproduced_from_bound_rows: offered, expected_summary: { LE_93: expected.by_tier["<=93"], LE_95: expected.by_tier["<=95"], LE_97: expected.by_tier["<=97"], LT_100: expected.by_tier["<100"] }, mismatches: 0 }, maker_floor: { commit: FLOOR_COMMIT, path: FLOOR_PATH, sha256: sha(floorBytes), bytes: floorBytes.length, rows: floorSource.length, law: "min(qualifying ask floor,seller-aggressed traded low)" } };
  const result = { schema_version: "window1-v34-prebell-close-regrade-v1", grading_only: true, fill_source: V34_COMMIT, R3_joint_floor: R3_JOINT, recut_map_offer_LT_100: offered.LT_100, STRICT_LAW: strictScore, CENSUS_PRICED: censusScore };
  const forbidden = { policy_replay_invocations: 0, fill_model_invocations: 0, tape_reads: 0, private_input_reads: 0, holdout_accesses: 0, live_accesses: 0, network_runtime_accesses: 0, order_accesses: 0, position_accesses: 0, settlement_basis_close_reads: 0, decision_or_fill_mutations: 0 };
  const core = {
    "CONTROL_BINDING.json": canonical({ V34_source: V34_COMMIT, close_source: CC_COMMIT, floor_source: FLOOR_COMMIT, operation: "REGRADE_ONLY_NO_REBUILD", R3_joint_floor: R3_JOINT, comparison_offer: offered }),
    "FROZEN_FILL_IDENTITY_RECEIPT.json": canonical(identity),
    "PREBELL_CLOSE_AND_OFFER_BINDING.json": canonical(binding),
    "SCORECARD_TWO_COLUMN.json": canonical(result),
    "FRONTIER_TWO_COLUMN.json": canonical({ STRICT_LAW: strictFrontier, CENSUS_PRICED: censusFrontier }),
    "REGRET_GAUGE_TWO_COLUMN.json": canonical({ STRICT_LAW: { ...strictRegret, rows: undefined }, CENSUS_PRICED: { ...censusRegret, rows: undefined } }),
    "STRICT_REGRADE_EVENT_LEDGER.jsonl.gz": gzipRows(strict),
    "CENSUS_PRICED_REGRADE_EVENT_LEDGER.jsonl.gz": gzipRows(census),
    "STRICT_REGRET_LEDGER.jsonl.gz": gzipRows(strictRegret.rows),
    "CENSUS_PRICED_REGRET_LEDGER.jsonl.gz": gzipRows(censusRegret.rows),
    "CLAIM_FENCE.json": canonical({ frozen_fills_not_replayed: true, grading_ruler_changed_only: true, prebell_close_is_ex_post_grade_only: true, recut_offer_is_benchmark_not_candidate_capture: true, fill_admissibility_not_revisited: true, full_life_V34_fill_horizon_and_guarded_prebell_offer_have_different_horizons: true, category_and_price_region_partitions_preserved: true }),
    "FORBIDDEN_ACCESS_RECEIPT.json": canonical(forbidden),
    "SOURCE_HASH_MANIFEST.json": canonical({ git_bound: { [STRICT_PATH]: identity.strict_source, [CENSUS_PATH]: identity.census_source, [CLOSE_PATH]: binding.close, [OFFER_PATH]: binding.recut_offer, [FLOOR_PATH]: binding.maker_floor }, local_sources: { "arb-executor/analysis/build_window1_v34_prebell_close_regrade.js": { sha256: fileHash(__filename), bytes: fs.statSync(__filename).size }, "arb-executor/tests/test_window1_v34_prebell_close_regrade.js": { sha256: fileHash(path.join(repo, "arb-executor/tests/test_window1_v34_prebell_close_regrade.js")), bytes: fs.statSync(path.join(repo, "arb-executor/tests/test_window1_v34_prebell_close_regrade.js")).size } } }),
    "REPORT.md": `# V34 frozen-fill pre-bell close re-grade\n\nNo V34 policy, action, order, fill, price, timestamp, or fill class was rebuilt. Frozen ${V34_COMMIT} event ledgers were joined to CC's ${CC_COMMIT} independently audited pre-bell closes.\n\n- R3 comparison: ${R3_JOINT} JOINT.\n- Re-cut map offer: ${offered.LE_93} / ${offered.LE_95} / ${offered.LE_97} / ${offered.LT_100} at <=93 / <=95 / <=97 / <100.\n- STRICT: ${strictScore.aggregate.completed_pairs} completed, ${strictScore.aggregate.joint_objective_pairs} JOINT, delta vs R3 ${strictScore.aggregate.delta_joint_vs_R3_68}, gap to offer ${strictScore.aggregate.gap_to_recut_map_LT_100_offer}.\n- CENSUS: ${censusScore.aggregate.completed_pairs} completed, ${censusScore.aggregate.joint_objective_pairs} JOINT, delta vs R3 ${censusScore.aggregate.delta_joint_vs_R3_68}, gap to offer ${censusScore.aggregate.gap_to_recut_map_LT_100_offer}.\n\nThis is a grade-only cross-ruler comparison. The frozen V34 full-life fill horizon and the guarded pre-bell offer horizon differ; no causal W1 replay claim is made.\n`,
  };
  for (const [name, bytes] of Object.entries(core)) write(name, bytes);
  const compareNames = Object.keys(core).sort();
  if (compare) { const mismatches = compareNames.filter((name) => !fs.existsSync(path.join(compare, name)) || fileHash(path.join(compare, name)) !== fileHash(path.join(output, name))); ensure(!mismatches.length, `determinism mismatch ${mismatches.join(",")}`); write("DETERMINISM_RECEIPT.json", canonical({ builds: 2, byte_identical: true, compared_files: compareNames.length, mismatches: [] })); }
  else write("DETERMINISM_RECEIPT.json", canonical({ builds: 1, byte_identical: null, role: "FIRST_BUILD" }));
  const names = fs.readdirSync(output).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort(); write("ARTIFACT_HASH_MANIFEST.json", canonical({ files: Object.fromEntries(names.map((name) => [name, { sha256: fileHash(path.join(output, name)), bytes: fs.statSync(path.join(output, name)).size }])) }));
  process.stdout.write(canonical({ output, STRICT_LAW: strictScore.aggregate, CENSUS_PRICED: censusScore.aggregate, recut_offer: offered }));
}

main().catch((error) => { process.stderr.write(`${error.stack || error}\n`); process.exitCode = 1; });
