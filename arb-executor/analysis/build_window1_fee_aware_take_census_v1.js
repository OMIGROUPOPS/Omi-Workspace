#!/usr/bin/env node
"use strict";

// Score-free diagnostic over the already-frozen 804-event ask/capacity floor
// census.  This does not replay a candidate and cannot authorize a take: the
// lineage has no bound decision-time expected-close estimator.  Actual W1
// closes are used only as an explicitly ex-post oracle screen.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

function canonical(value) { return `${JSON.stringify(value, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function strictInteger(value, name) {
  if (typeof value !== "number" || !Number.isInteger(value)) throw new Error(`${name} must be an exact integer`);
  return value;
}
function takerFeeFiveLotCents(price) {
  strictInteger(price, "price");
  if (price < 1 || price > 99) throw new Error(`price out of fee range: ${price}`);
  // Frozen Kalshi taker receipt law already used by the five-game audit:
  // ceil(7*q*price*(100-price)/10000) cents, q=5.
  return Math.ceil((7 * 5 * price * (100 - price)) / 10000);
}
function region(price) { return price <= 25 ? "le25" : price <= 50 ? "26_50" : price <= 75 ? "51_75" : "ge75"; }

function main() {
  const args = process.argv.slice(2);
  const get = (name, fallback) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
  const repo = path.resolve(get("--repo", "."));
  const floorPath = path.join(repo, ".claude/window1_live_v4_replay/live_book_initial_aim_20260731/RAW_CAPACITY_FLOOR_SCAN.json");
  const ceilingPath = path.join(repo, ".claude/window1_live_v4_replay/live_book_initial_aim_20260731/ASK_10S_FIVE_CONTRACT_CEILING.json");
  const outDir = path.resolve(get("--output", path.join(repo, ".claude/window1_live_v4_replay/fee_aware_take_census_20260801")));
  const floor = JSON.parse(fs.readFileSync(floorPath));
  const ceiling = JSON.parse(fs.readFileSync(ceilingPath));
  if (floor.rows.length !== 1608 || ceiling.population_events !== 804 || ceiling.capacity_proven_ask_only_10s_negative_ceiling !== 516) throw new Error("frozen population/ceiling identity mismatch");
  const byEvent = new Map();
  for (const row of floor.rows) {
    if (!byEvent.has(row.event_id)) byEvent.set(row.event_id, []);
    byEvent.get(row.event_id).push(row);
  }
  const ceilingIds = new Set(ceiling.events.filter((row) => row.capacity_proven_negative).map((row) => row.event_id));
  if (ceilingIds.size !== 516) throw new Error(`expected 516 unique ceiling events, got ${ceilingIds.size}`);
  const rows = [];
  for (const eventId of [...ceilingIds].sort()) {
    const legs = (byEvent.get(eventId) || []).sort((a, b) => a.leg_id.localeCompare(b.leg_id));
    if (legs.length !== 2 || legs.some((leg) => !leg.capacity_proven_floor)) throw new Error(`missing two proven floors: ${eventId}`);
    const legRows = legs.map((leg) => {
      const ask = strictInteger(leg.capacity_proven_floor.limit_cents, `${eventId}/${leg.leg_id} ask`);
      const close = strictInteger(leg.window1_close_cents, `${eventId}/${leg.leg_id} close`);
      return {
        leg_id: leg.leg_id,
        price_region: region(ask),
        take_ask_cents: ask,
        actual_window1_close_cents: close,
        ex_post_edge_cents: close - ask,
        taker_fee_five_lot_cents: takerFeeFiveLotCents(ask),
        ask_dwell_seconds: leg.capacity_proven_floor.dwell_seconds,
        displayed_capacity: leg.capacity_proven_floor.displayed_capacity,
        evidence_ts: leg.capacity_proven_floor.evidence_ts,
        evidence_receipt: leg.capacity_proven_floor.source_receipt,
      };
    });
    const edge = legRows.reduce((sum, leg) => sum + leg.ex_post_edge_cents, 0);
    const fee = legRows.reduce((sum, leg) => sum + leg.taker_fee_five_lot_cents, 0);
    const pairRegion = legRows.map((leg) => leg.price_region).sort().join("+");
    rows.push({
      event_id: eventId,
      category: legs[0].category,
      price_region_pair: pairRegion,
      legs: legRows,
      ex_post_actual_close_edge_cents: edge,
      taker_fee_five_lot_pair_cents: fee,
      operator_fee_screen_margin_cents: edge - fee,
      clears_operator_fee_screen: edge > fee,
      executable_decision_time_ruling: "EXPECTED_CLOSE_NOT_BOUND",
    });
  }
  const partitions = {};
  for (const row of rows) {
    const key = `${row.category}|${row.price_region_pair}`;
    const bucket = partitions[key] ||= { category: row.category, price_region_pair: row.price_region_pair, denominator_516_rows: 0, ex_post_clears: 0, ex_post_fails: 0, event_ids_clearing: [], event_ids_failing: [] };
    bucket.denominator_516_rows += 1;
    bucket[row.clears_operator_fee_screen ? "ex_post_clears" : "ex_post_fails"] += 1;
    bucket[row.clears_operator_fee_screen ? "event_ids_clearing" : "event_ids_failing"].push(row.event_id);
  }
  const result = {
    schema_version: "WINDOW1_FEE_AWARE_TAKE_CENSUS_V1",
    score_free: true,
    population_events: 804,
    capacity_proven_negative_pair_ceiling: 516,
    decision_rule_contract: {
      formula: "cross only if SUM(expected_close_leg - current_ask_leg) > SUM(taker_fee_five_lot_cents(current_ask_leg))",
      expected_close_source: "NOT_BOUND",
      executable_now: false,
      fail_closed_reason: "No decision-time expected-close estimator is bound in the frozen lineage; actual W1 close is future information.",
    },
    diagnostic_contract: {
      mode: "EX_POST_ACTUAL_WINDOW1_CLOSE_ORACLE_ONLY",
      fee_formula_provenance: "ceil(7*q*price*(100-price)/10000) cents; q=5; inherited from MAKER_TAKER_FILL_AUDIT.json",
      comparison_convention: "operator-specified pair price-edge cents compared with total five-lot taker-fee cents",
      not_a_policy_result: true,
    },
    ex_post_clearing_count: rows.filter((row) => row.clears_operator_fee_screen).length,
    ex_post_failing_count: rows.filter((row) => !row.clears_operator_fee_screen).length,
    by_category_and_price_region: Object.fromEntries(Object.entries(partitions).sort(([a], [b]) => a.localeCompare(b))),
    rows,
    sources: {
      floor_scan: { path: path.relative(repo, floorPath).replaceAll("\\", "/"), sha256: sha256(fs.readFileSync(floorPath)) },
      ceiling: { path: path.relative(repo, ceilingPath).replaceAll("\\", "/"), sha256: sha256(fs.readFileSync(ceilingPath)) },
    },
  };
  fs.mkdirSync(outDir, { recursive: true });
  const out = path.join(outDir, "FEE_AWARE_TAKE_CENSUS.json");
  fs.writeFileSync(out, canonical(result));
  fs.writeFileSync(path.join(outDir, "SOURCE_HASH_MANIFEST.json"), canonical({ schema_version: "WINDOW1_FEE_AWARE_TAKE_SOURCE_MANIFEST_V1", sources: result.sources }));
  const rawBase = "https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/fee_aware_take_census_20260801";
  const partitionTable = Object.values(result.by_category_and_price_region).map((row) => `| ${row.category} | ${row.price_region_pair} | ${row.denominator_516_rows} | ${row.ex_post_clears} | ${row.ex_post_fails} |`).join("\n");
  fs.writeFileSync(path.join(outDir, "REPORT.md"), [
    "# Fee-aware take census — score-free diagnostic",
    "",
    `Raw receipt: ${rawBase}/FEE_AWARE_TAKE_CENSUS.json`,
    "",
    "The executable rule is fail-closed: `expected_close=NOT_BOUND`. The 5/516 value below is an ex-post actual-W1-close oracle screen, not a policy result or tradeable-population claim.",
    "",
    "| Category | Ask-price-region pair | Frozen 516 denominator | Ex-post clears | Ex-post fails |",
    "|---|---|---:|---:|---:|",
    partitionTable,
    "",
    "Fee law: `ceil(7 * 5 * price * (100-price) / 10000)` cents per leg. The comparison follows the operator-specified convention: pair price-edge cents versus total five-lot taker-fee cents.",
    "",
  ].join("\n"));
  fs.writeFileSync(path.join(outDir, "DETERMINISM_RECEIPT.json"), canonical({ schema_version: "WINDOW1_FEE_AWARE_TAKE_DETERMINISM_RECEIPT_V1", canonical_json_lf: true, input_hashes: result.sources, fee_census_sha256: sha256(fs.readFileSync(out)), expected_rebuild_identity: "BYTE_IDENTICAL" }));
  const artifactFiles = fs.readdirSync(outDir).filter((name) => name !== "ARTIFACT_HASH_MANIFEST.json").sort();
  fs.writeFileSync(path.join(outDir, "ARTIFACT_HASH_MANIFEST.json"), canonical({ schema_version: "WINDOW1_FEE_AWARE_TAKE_ARTIFACT_MANIFEST_V1", artifacts: artifactFiles.map((name) => { const bytes = fs.readFileSync(path.join(outDir, name)); return { path: name, bytes: bytes.length, sha256: sha256(bytes) }; }) }));
  process.stdout.write(canonical({ status: "BUILT", ex_post_clearing_count: result.ex_post_clearing_count, ex_post_failing_count: result.ex_post_failing_count, partition_count: Object.keys(partitions).length, output_sha256: sha256(fs.readFileSync(out)) }));
}

main();
