#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { EXCLUDED_EVENTS, MIN_CLASS_N } = require("./build_window1_quote_shape_coherent_library_v12.js");
const { distribution, leaveOneOutResiduals, linearFit } = require("./window1_second_leg_x_pricer_v17.js");

const args = process.argv.slice(2);
const value = (name, fallback) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : fallback; };
const repo = path.resolve(value("--repo", "."));
const input = path.resolve(value("--events", path.join(repo, ".claude/window1_live_v4_replay/persistence_floor_repair_v11_20260802/POPULATION_EVENT_LEDGER.jsonl.gz")));
const shapeLibraryPath = path.resolve(value("--shape-library", path.join(repo, ".claude/window1_live_v4_replay/five_exact_dynamic_renarrow_v6_20260801/QUOTE_SHAPE_LIBRARY_DYNAMIC_RENARROW_V6.json")));
const output = path.resolve(value("--output", path.join(repo, ".claude/window1_live_v4_replay/second_leg_x_pricer_fit_v17_20260803/SECOND_LEG_X_CONDITIONAL_LIBRARY.json")));

function canonical(x) { return `${JSON.stringify(x, null, 2)}\n`; }
function sha256(bytes) { return crypto.createHash("sha256").update(bytes).digest("hex"); }
function group(rows, key) { const out = new Map(); for (const row of rows) { const k = key(row); if (!out.has(k)) out.set(k, []); out.get(k).push(row); } return out; }
function ensure(ok, message) { if (!ok) throw new Error(message); }

function main() {
  const bytes = fs.readFileSync(input);
  const shapeBytes = fs.readFileSync(shapeLibraryPath), shapeLibrary = JSON.parse(shapeBytes);
  const events = zlib.gunzipSync(bytes).toString("utf8").trim().split(/\r?\n/).map(JSON.parse);
  ensure(events.length === 804, "V11 event population must be 804");
  const rows = [], eventStartingPriceSplit = {};
  for (const event of events) {
    eventStartingPriceSplit[event.event_id] = event.starting_price_split;
    const credited = event.legs.filter((leg) => leg.credited && Number.isInteger(leg.entry_cents) && Number.isFinite(leg.action_timestamp_epoch)).sort((a, b) => a.action_timestamp_epoch - b.action_timestamp_epoch || a.leg_id.localeCompare(b.leg_id));
    if (!credited.length || (credited.length > 1 && credited[0].action_timestamp_epoch === credited[1].action_timestamp_epoch)) continue;
    const first = credited[0], sibling = event.legs.find((leg) => leg.leg_id !== first.leg_id);
    if (!sibling || !Number.isInteger(sibling.qualifying_ask_floor_cents)) continue;
    rows.push({
      event_id: event.event_id,
      category: event.category,
      starting_price_split: event.starting_price_split,
      fit_excluded: EXCLUDED_EVENTS.includes(event.event_id),
      first_leg_identity: first.leg_identity,
      first_leg_id: first.leg_id,
      first_fill_x_cents: first.entry_cents,
      first_fill_timestamp_epoch: first.action_timestamp_epoch,
      sibling_leg_identity: sibling.leg_identity,
      sibling_leg_id: sibling.leg_id,
      sibling_eventual_ask_floor_cents: sibling.qualifying_ask_floor_cents,
    });
  }
  const fitRows = rows.filter((row) => !row.fit_excluded), cells = {};
  for (const [cellKey, cellRows] of [...group(fitRows, (row) => `${row.category}|${row.starting_price_split}`)].sort(([a], [b]) => a.localeCompare(b))) {
    const fit = linearFit(cellRows), residual = distribution(leaveOneOutResiduals(cellRows)), target = distribution(cellRows.map((row) => row.sibling_eventual_ask_floor_cents));
    cells[cellKey] = {
      cell_key: cellKey,
      support_n: cellRows.length,
      usable: cellRows.length >= MIN_CLASS_N && Boolean(fit) && residual.n >= MIN_CLASS_N,
      unusable_reason: cellRows.length < MIN_CLASS_N ? "CELL_N_BELOW_EXISTING_COHERENCE_MINIMUM" : !fit ? "LINEAR_X_FIT_UNAVAILABLE" : residual.n < MIN_CLASS_N ? "LEAVE_ONE_OUT_RESIDUAL_N_BELOW_MINIMUM" : null,
      minimum_support_n: MIN_CLASS_N,
      unconditional_sibling_floor_distribution: target,
      leave_one_event_out_x_residual_distribution: residual,
      p90_p10_spread_reduction_cents: target.p90_p10_width === null || residual.p90_p10_width === null ? null : target.p90_p10_width - residual.p90_p10_width,
      fitted_model: fit ? { intercept: fit.intercept, slope: fit.slope } : null,
      training_rows: cellRows.sort((a, b) => a.event_id.localeCompare(b.event_id)),
    };
  }
  const legRows = events.flatMap((event) => event.legs.map((leg) => ({ event_id: event.event_id, leg_identity: leg.leg_identity, qualifying_ask_floor_cents: leg.qualifying_ask_floor_cents })));
  const shapeFloorSupport = {};
  for (const leg of legRows) {
    const shapeId = shapeLibrary.assignment?.[leg.leg_identity];
    if (!shapeId || !Number.isInteger(leg.qualifying_ask_floor_cents) || EXCLUDED_EVENTS.includes(leg.event_id)) continue;
    if (!shapeFloorSupport[shapeId]) shapeFloorSupport[shapeId] = { shape_id: shapeId, rows: [] };
    shapeFloorSupport[shapeId].rows.push({ event_id: leg.event_id, leg_identity: leg.leg_identity, qualifying_ask_floor_cents: leg.qualifying_ask_floor_cents });
  }
  for (const support of Object.values(shapeFloorSupport)) { support.rows.sort((a, b) => a.leg_identity.localeCompare(b.leg_identity)); support.distribution = distribution(support.rows.map((row) => row.qualifying_ask_floor_cents)); }
  const library = {
    schema_version: "WINDOW1_SECOND_LEG_X_CONDITIONAL_LIBRARY_V17",
    score_free: true,
    source_v11_sha256: sha256(bytes),
    source_shape_library_sha256: sha256(shapeBytes),
    population: { events: 804, causal_first_fill_rows: rows.length, fit_rows: fitRows.length, excluded_exact_start_events: EXCLUDED_EVENTS },
    fit_law: "First credited fill X predicts sibling eventual ten-second/exact-five ask floor within category+frozen starting-price-split. Every runtime target event is excluded and residual uncertainty is itself leave-one-event-out.",
    uncertainty_report_band: "P10_TO_P90_OF_LEAVE_ONE_EVENT_OUT_RESIDUALS; SAME_UNCERTAINTY_WIDTH_REPORTED_BY_V16",
    elimination_support: "LEAVE_ONE_EVENT_OUT_P10_P90_DISTRIBUTION_OVERLAP_FOR_BOTH_X_CONDITIONAL_AND_SHAPE_MEMBER_FLOORS; NO_POINT_TARGET",
    minimum_support: { value: MIN_CLASS_N, provenance: "existing quote-shape coherence law" },
    event_starting_price_split: eventStartingPriceSplit,
    cells,
    shape_floor_support: shapeFloorSupport,
  };
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.writeFileSync(output, canonical(library));
  process.stdout.write(canonical({ status: "BUILT", output, cells: Object.keys(cells).length, usable_cells: Object.values(cells).filter((cell) => cell.usable).length, rows: rows.length }));
}

if (require.main === module) main();
