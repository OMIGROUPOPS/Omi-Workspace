#!/usr/bin/env node
"use strict";

// Receipt-only classification of the four NIKVRB/HURBIG replay credits.
// This builder never runs a scorer and never changes a replay decision.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const args = process.argv.slice(2);
const arg = (name, fallback) => {
  const index = args.indexOf(name);
  return index >= 0 ? args[index + 1] : fallback;
};
const repo = path.resolve(arg("--repo", "."));
const privateRoot = path.resolve(arg("--private-root", process.env.W1_PRIVATE_ROOT || "C:/Users/omigr/OMI-Window1-private"));
const output = path.resolve(arg("--output", path.join(repo, ".claude/window1_live_v4_replay/honest_fill_model_20260801")));
const makerReceiptPath = path.join(repo, ".claude/window1_live_v4_replay/quote_shape_maker_role_addendum_20260801/MAKER_ROLE_RECEIPT_AUDIT.json");
const fiveGamePath = path.join(repo, ".claude/window1_live_v4_replay/five_exact_full_stack_capacity_20260731/FIVE_GAME_FULL_STACK_RESULTS.json");
const sequencePath = path.join(repo, ".claude/window1_live_v4_replay/quote_shape_maker_role_addendum_20260801/EXACT_ACTION_TO_CREDIT_SEQUENCE.json");
const clockReceiptPath = path.join(repo, ".claude/window1_live_v4_replay/vrb_print_book_clock_correction_20260801/PRINT_BOOK_CLOCK_RECEIPT.json");
const makerTakerAuditPath = path.join(repo, ".claude/window1_live_v4_replay/quote_shape_maker_insufficient_diagnosis_20260801/MAKER_TAKER_FILL_AUDIT.json");
const QUANTITY = 5;

function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function hashFile(file) { return sha256(fs.readFileSync(file)); }
function clocks(ts, scheduled, bell) {
  return {
    timestamp_epoch: ts,
    t_minus_scheduled_seconds: scheduled - ts,
    t_minus_actual_bell_seconds: bell - ts,
  };
}
function tMinus(seconds) {
  const sign = seconds >= 0 ? "T-" : "T+";
  const value = Math.abs(seconds);
  const whole = Math.floor(value);
  return `${sign}${Math.floor(whole / 60)}:${String(whole % 60).padStart(2, "0")}`;
}
function loadPrints(eventId, legId, left, right, scheduled, bell) {
  const file = path.join(privateRoot, "fit-local/guarded-cache-v3", `${eventId}.json.gz`);
  const bytes = fs.readFileSync(file);
  const cache = JSON.parse(zlib.gunzipSync(bytes));
  const leg = cache.legs.find((row) => row.leg === legId);
  if (!leg) throw new Error(`missing guarded print leg ${eventId}/${legId}`);
  const seen = new Set();
  const rows = [];
  for (const row of leg.prints || []) {
    if (!(row.ts >= left && row.ts <= right) || !(row.size > 0) || !Number.isInteger(row.price) || !row.trade_id || seen.has(row.trade_id)) continue;
    seen.add(row.trade_id);
    rows.push({
      ...clocks(row.ts, scheduled, bell),
      price_cents: row.price,
      size: row.size,
      taker_side: row.taker_side,
      aggressor_side: row.taker_side === "yes" ? "BUY" : row.taker_side === "no" ? "SELL" : "UNKNOWN",
      trade_id: row.trade_id,
    });
  }
  rows.sort((leftRow, rightRow) => leftRow.timestamp_epoch - rightRow.timestamp_epoch || leftRow.trade_id.localeCompare(rightRow.trade_id));
  return {
    rows,
    source: {
      path: `fit-local/guarded-cache-v3/${path.basename(file)}`,
      bytes: bytes.length,
      sha256: sha256(bytes),
      cache_key: cache.cache_key,
      cache_version: cache.cache_version,
    },
  };
}
function regionRows(makerTakerAudit) {
  const result = {};
  for (const leg of makerTakerAudit.fills) {
    result[`${leg.event_id}|${leg.leg_id}`] = {
      price_region: leg.price_region,
      price_region_source: `.claude/window1_live_v4_replay/quote_shape_maker_insufficient_diagnosis_20260801/MAKER_TAKER_FILL_AUDIT.json#fills[${leg.event_id}/${leg.leg_id}]; formed action book ${leg.action_book.bid}/${leg.action_book.ask}; ${leg.action_receipt}`,
    };
  }
  return result;
}
function partition(rows) {
  const groups = new Map();
  for (const row of rows) {
    const key = `${row.category}|${row.price_region}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(row);
  }
  return [...groups.values()].map((members) => ({
    category: members[0].category,
    price_region: members[0].price_region,
    leg_count: members.length,
    legs: members.map((row) => `${row.event_id}|${row.leg_id}`),
    PROVEN_MAKER: members.filter((row) => row.fill_class === "PROVEN_MAKER").length,
    PROVEN_TAKER: members.filter((row) => row.fill_class === "PROVEN_TAKER").length,
    UNPROVEN: members.filter((row) => row.fill_class === "UNPROVEN").length,
    credited_under_honest_model: members.filter((row) => row.credited_under_honest_model).length,
  })).sort((left, right) => left.category.localeCompare(right.category) || left.price_region.localeCompare(right.price_region));
}

function main() {
  const maker = JSON.parse(fs.readFileSync(makerReceiptPath));
  const five = JSON.parse(fs.readFileSync(fiveGamePath));
  const sequences = JSON.parse(fs.readFileSync(sequencePath));
  const clock = JSON.parse(fs.readFileSync(clockReceiptPath));
  const makerTakerAudit = JSON.parse(fs.readFileSync(makerTakerAuditPath));
  const regions = regionRows(makerTakerAudit);
  const events = Object.fromEntries(five.events.map((event) => [event.event_id, event]));
  const privateSources = {};
  const rows = [];

  for (const fill of maker.fills) {
    const event = events[fill.event_id];
    if (!event) throw new Error(`missing five-game event ${fill.event_id}`);
    const region = regions[`${fill.event_id}|${fill.leg_id}`];
    if (!region) throw new Error(`missing region ${fill.event_id}/${fill.leg_id}`);
    const window = event.window;
    const prints = loadPrints(fill.event_id, fill.leg_id, window.left_ts, window.right_ts, window.scheduled_start_ts, window.actual_bell_ts);
    privateSources[`${fill.event_id}|${fill.leg_id}`] = prints.source;
    const actionTs = fill.action_clock.timestamp_epoch;
    const creditTs = fill.replay_credit_clock.timestamp_epoch;
    const sellerProofs = prints.rows.filter((row) => row.timestamp_epoch > actionTs && row.timestamp_epoch <= creditTs && row.aggressor_side === "SELL" && row.price_cents <= fill.x_cents);
    const exactBook = fill.exact_timestamp_own_book_snapshot_at_action === true;
    const displayedCapacity = Number(fill.own_book_at_action.displayed_ask_capacity_at_or_below_x);
    const provenOpposingSize = exactBook && fill.own_book_at_action.ask <= fill.x_cents && Number.isFinite(displayedCapacity) && displayedCapacity >= QUANTITY;
    const nonMarketableAtExactBook = exactBook && fill.x_cents < fill.own_book_at_action.ask;
    const restingPriceProvenBeforeSellerPrint = nonMarketableAtExactBook && sellerProofs.length > 0;
    let fillClass = "UNPROVEN";
    let reason = "No exact-timestamp opposing-size proof and no receipt-proven resting maker price followed by a seller-aggressed print at or through X.";
    if (provenOpposingSize) {
      fillClass = "PROVEN_TAKER";
      reason = "At submission timestamp, the authoritative own-leg BBO displayed at least five opposing contracts at or below X; an unchanged buy would cross.";
    } else if (restingPriceProvenBeforeSellerPrint) {
      fillClass = "PROVEN_MAKER";
      reason = "X was nonmarketable on the exact action book before a strictly later seller-aggressed print traded at or below X.";
    }
    const honestCreditClock = fillClass === "PROVEN_TAKER"
      ? fill.action_clock
      : fillClass === "PROVEN_MAKER"
        ? clocks(sellerProofs[0].timestamp_epoch, window.scheduled_start_ts, window.actual_bell_ts)
        : null;
    const sequence = sequences.sequences.find((candidate) => candidate.event_id === fill.event_id && candidate.leg_id === fill.leg_id);
    if (!sequence) throw new Error(`missing action sequence ${fill.event_id}/${fill.leg_id}`);
    rows.push({
      event_id: fill.event_id,
      category: fill.category,
      price_region: region.price_region,
      price_region_source: region.price_region_source,
      leg_id: fill.leg_id,
      ticker: fill.ticker,
      replay_x_cents: fill.x_cents,
      requested_quantity_contracts: QUANTITY,
      action_clock: fill.action_clock,
      action_trigger_receipt: fill.action_trigger_receipt,
      own_book_receipt_at_action: fill.own_book_at_action.source_receipt,
      own_book_receipt_age_at_action_seconds: fill.own_book_receipt_age_at_action_seconds,
      exact_timestamp_own_book_snapshot_at_action: exactBook,
      action_joint_observation: {
        bid_cents: fill.own_book_at_action.bid,
        ask_cents: fill.own_book_at_action.ask,
        last_traded_cents: fill.own_book_at_action.last_traded,
        spread_cents: fill.own_book_at_action.spread,
        ask_dwell_seconds: fill.own_book_at_action.ask_dwell_seconds,
        displayed_ask_size_at_x: fill.own_book_at_action.displayed_ask_size_at_x,
        displayed_ask_capacity_at_or_below_x: displayedCapacity,
        top_five_ask_depth: fill.own_book_at_action.top_five_ask_depth,
      },
      replay_credit_clock: fill.replay_credit_clock,
      replay_credit_receipt: fill.replay_credit_receipt,
      replay_same_receipt_credit: fill.replay_same_receipt_credit,
      action_to_replay_credit_seconds: fill.replay_action_to_credit_seconds,
      action_to_replay_credit_book_receipt_count: sequence.rows.length,
      seller_aggressed_prints_at_or_through_x_during_action_to_credit: sellerProofs,
      seller_aggressed_print_proof_count: sellerProofs.length,
      proven_taker_predicates: {
        exact_timestamp_own_book_snapshot: exactBook,
        displayed_best_ask_at_or_below_x: fill.own_book_at_action.ask <= fill.x_cents,
        displayed_capacity_at_or_below_x_at_least_five: displayedCapacity >= QUANTITY,
        all_required: provenOpposingSize,
      },
      proven_maker_predicates: {
        exact_timestamp_own_book_snapshot: exactBook,
        x_strictly_below_ask_at_action: nonMarketableAtExactBook,
        seller_aggressed_print_strictly_later_at_or_through_x_before_replay_credit: sellerProofs.length > 0,
        all_required: restingPriceProvenBeforeSellerPrint,
      },
      fill_class: fillClass,
      credited_under_honest_model: fillClass !== "UNPROVEN",
      credited_quantity_contracts_under_honest_model: fillClass !== "UNPROVEN" ? QUANTITY : null,
      honest_fill_price_cents: fillClass !== "UNPROVEN" ? fill.x_cents : null,
      honest_credit_clock: honestCreditClock,
      honest_credit_evidence_type: fillClass === "PROVEN_TAKER" ? "DISPLAYED_OPPOSING_ASK_CAPACITY_AT_SUBMISSION" : fillClass === "PROVEN_MAKER" ? "STRICTLY_LATER_SELL_AGGRESSOR_TRUE_PRINT" : null,
      honest_credit_receipts: fillClass === "PROVEN_TAKER" ? [fill.own_book_at_action.source_receipt] : fillClass === "PROVEN_MAKER" ? [sellerProofs[0].trade_id] : [],
      replay_later_receipt_used_as_honest_credit_evidence: false,
      applicable_fee_class: fillClass === "PROVEN_TAKER" ? "TAKER_FEE_REQUIRED_VALUE_NOT_COMPUTED_HERE" : fillClass === "PROVEN_MAKER" ? "MAKER_FEE_REQUIRED_VALUE_NOT_COMPUTED_HERE" : "NOT_APPLICABLE_UNPROVEN",
      classification_reason: reason,
    });
  }
  rows.sort((left, right) => left.event_id.localeCompare(right.event_id) || left.leg_id.localeCompare(right.leg_id));
  if (rows.length !== 4) throw new Error(`expected four replay credits, got ${rows.length}`);

  const pairRows = Object.values(events).filter((event) => /HURBIG|NIKVRB/.test(event.event_id)).map((event) => {
    const legs = rows.filter((row) => row.event_id === event.event_id);
    return {
      event_id: event.event_id,
      category: event.category,
      legs: legs.map((row) => ({ leg_id: row.leg_id, price_region: row.price_region, replay_x_cents: row.replay_x_cents, fill_class: row.fill_class, credited: row.credited_under_honest_model })),
      credited_leg_count: legs.filter((row) => row.credited_under_honest_model).length,
      completed_pair_under_honest_model: legs.length === 2 && legs.every((row) => row.credited_under_honest_model),
      pair_fee_class: legs.every((row) => row.fill_class === "PROVEN_TAKER") ? "TWO_TAKER_LEGS_FEE_ARITHMETIC_REQUIRED" : "INCOMPLETE_OR_MIXED",
    };
  }).sort((left, right) => left.event_id.localeCompare(right.event_id));

  const contract = {
    schema_version: "WINDOW1_HONEST_FILL_MODEL_CONTRACT_V1",
    score_free: true,
    quantity_contracts: QUANTITY,
    precedence: ["PROVEN_TAKER", "PROVEN_MAKER", "UNPROVEN"],
    classes: {
      PROVEN_MAKER: "Our nonmarketable resting price is proven on the exact action book before a strictly later positive-size SELL-aggressor true print trades at or through it during the action-to-credit interval.",
      PROVEN_TAKER: "At the exact submission timestamp, the authoritative own-leg BBO displays at least five opposing contracts at or below X, so an unchanged buy would cross.",
      UNPROVEN: "Every other replay credit, including carried/stale action books and later BBO-only simulator credits.",
    },
    exclusions: {
      later_book_receipt_alone: "Never proves maker execution.",
      carried_last_trade: "Never a true-print execution receipt.",
      ask_visit_without_sell_print: "Never proves a seller hit a resting bid.",
      stale_or_carried_action_book: "Cannot prove opposing size at the submission timestamp.",
    },
    unproven_credit_law: "UNPROVEN rows are not completions.",
    source_clock_binding: {
      books: "ET text normalized to Unix epoch seconds; preserved raw row ordinal resolves book rows at equal seconds.",
      prints: "Exchange UTC epoch with fractional-second precision and trade_id identity.",
      same_epoch_basis: clock.clock_binding.same_epoch_basis,
      directly_comparable_across_distinct_seconds: clock.clock_binding.directly_comparable_across_distinct_seconds,
      authoritative_cross_stream_order_within_same_second: clock.clock_binding.authoritative_cross_stream_order_within_same_second,
    },
  };
  const classification = {
    schema_version: "WINDOW1_FOUR_FILL_HONEST_CLASSIFICATION_V1",
    score_free: true,
    replay_credit_rows: rows.length,
    PROVEN_MAKER: rows.filter((row) => row.fill_class === "PROVEN_MAKER").length,
    PROVEN_TAKER: rows.filter((row) => row.fill_class === "PROVEN_TAKER").length,
    UNPROVEN: rows.filter((row) => row.fill_class === "UNPROVEN").length,
    credited_leg_rows_under_honest_model: rows.filter((row) => row.credited_under_honest_model).length,
    category_price_region_partitions: partition(rows),
    rows,
  };
  const rescoring = {
    schema_version: "WINDOW1_TWO_PAIR_HONEST_COMPLETION_RESCORING_V1",
    score_free: true,
    event_count: pairRows.length,
    completed_pair_count_under_honest_model: pairRows.filter((row) => row.completed_pair_under_honest_model).length,
    incomplete_pair_count_under_honest_model: pairRows.filter((row) => !row.completed_pair_under_honest_model).length,
    rows: pairRows,
    performance_metrics: null,
  };
  const report = [
    "# Honest fill-model receipt — NIKVRB and HURBIG",
    "",
    "This package replaces the replay's later-receipt convention with three receipt classes. It is score-free and does not rerun either game.",
    "",
    `Result: ${classification.PROVEN_MAKER} PROVEN_MAKER, ${classification.PROVEN_TAKER} PROVEN_TAKER, and ${classification.UNPROVEN} UNPROVEN leg rows. ${classification.credited_leg_rows_under_honest_model} of four leg credits survive. ${rescoring.completed_pair_count_under_honest_model} of two pairs remains complete.`,
    "",
    "| category | price region | event/leg | action scheduled / bell | bid/ask/last; spread; dwell | X / ask capacity | seller prints through X before replay credit | class | honest credit |",
    "|---|---|---|---|---|---|---:|---|---|",
    ...rows.map((row) => `| ${row.category} | ${row.price_region} | ${row.event_id}/${row.leg_id} | ${tMinus(row.action_clock.t_minus_scheduled_seconds)} / ${tMinus(row.action_clock.t_minus_actual_bell_seconds)} | ${row.action_joint_observation.bid_cents}/${row.action_joint_observation.ask_cents}/${row.action_joint_observation.last_traded_cents ?? "NULL"}; ${row.action_joint_observation.spread_cents}; ${row.action_joint_observation.ask_dwell_seconds}s | ${row.replay_x_cents} / ${row.action_joint_observation.displayed_ask_capacity_at_or_below_x} | ${row.seller_aggressed_print_proof_count} | ${row.fill_class} | ${row.credited_under_honest_model ? "YES" : "NO"} |`),
    "",
    "## Pair rescoring",
    "",
    "| event | leg classes | completed? |",
    "|---|---|---|",
    ...pairRows.map((row) => `| ${row.event_id} | ${row.legs.map((leg) => `${leg.leg_id}=${leg.fill_class}`).join(", ")} | ${row.completed_pair_under_honest_model ? "YES" : "NO"} |`),
    "",
    "No PROVEN_MAKER fill survives. NIKVRB survives only as two PROVEN_TAKER legs and therefore requires taker-fee arithmetic outside this score-free receipt. HURBIG does not complete because HUR's own-leg book was 43 seconds old at the sibling-triggered action timestamp, so opposing size at submission is not proven.",
    "",
    "The true-print and book clocks share normalized Unix epoch and are directly comparable across distinct seconds. Cross-stream order inside one second is not authoritative because the book stream has second precision while prints retain fractional seconds.",
  ].join("\n") + "\n";
  const sourceManifest = {
    schema_version: "WINDOW1_HONEST_FILL_SOURCE_MANIFEST_V1",
    committed: Object.fromEntries([makerReceiptPath, fiveGamePath, sequencePath, clockReceiptPath, makerTakerAuditPath, __filename].map((file) => [path.relative(repo, file).replaceAll("\\", "/"), { bytes: fs.statSync(file).size, sha256: hashFile(file) }])),
    private_guarded_prints: privateSources,
  };
  const files = {
    "HONEST_FILL_MODEL_CONTRACT.json": canonical(contract),
    "FOUR_FILL_CLASSIFICATION.json": canonical(classification),
    "PAIR_COMPLETION_RESCORING.json": canonical(rescoring),
    "SOURCE_HASH_MANIFEST.json": canonical(sourceManifest),
    "REPORT.md": report,
  };
  files["DETERMINISM_RECEIPT.json"] = canonical({
    schema_version: "WINDOW1_HONEST_FILL_DETERMINISM_RECEIPT_V1",
    builder: "arb-executor/analysis/build_window1_honest_fill_model_v1.js",
    canonical_json: "JSON.stringify(value, null, 2) plus one LF",
    output_ordering: "event_id then leg_id; category then price_region",
    gzip_output: false,
    volatile_fields: [],
    expected_core_artifact_hashes: Object.fromEntries(Object.entries(files).map(([name, content]) => [name, sha256(content)])),
    verification: "Run the builder twice from the same source hashes and compare every emitted byte.",
  });
  const artifacts = Object.entries(files).map(([name, content]) => ({ path: `.claude/window1_live_v4_replay/honest_fill_model_20260801/${name}`, bytes: Buffer.byteLength(content), sha256: sha256(content) }));
  files["ARTIFACT_HASH_MANIFEST.json"] = canonical({ schema_version: "WINDOW1_HONEST_FILL_ARTIFACT_MANIFEST_V1", artifacts });
  fs.mkdirSync(output, { recursive: true });
  for (const [name, content] of Object.entries(files)) fs.writeFileSync(path.join(output, name), content);
  process.stdout.write(canonical({ status: "BUILT", PROVEN_MAKER: classification.PROVEN_MAKER, PROVEN_TAKER: classification.PROVEN_TAKER, UNPROVEN: classification.UNPROVEN, completed_pairs: rescoring.completed_pair_count_under_honest_model }));
}

main();
