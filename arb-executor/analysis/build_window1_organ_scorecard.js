#!/usr/bin/env node
"use strict";

// Deterministic, score-free synthesis of the frozen Window-1 organ scorecard
// and defect ledger. This program reads committed replay evidence only. It
// never imports or executes live_v4, never invokes a scorer, and never writes
// outside the versioned report/package paths below.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const repo = path.resolve(process.argv[2] || ".");
const checkOnly = process.argv.includes("--check");
const outDir = path.join(repo, ".claude/window1_organ_scorecard_20260731");
const reportPath = path.join(
  repo,
  "arb-executor/docs/research/window1/WINDOW1_ORGAN_SCORECARD_AND_DEFECT_LEDGER.md"
);

const INPUTS = {
  quote_legs: {
    path: ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_REACHABILITY_LEGS.csv",
    sha256: "453fdafbe955c5a4eed8357e77a2abcaa35bd1e84d783b19400aebaf3e2d17ba",
  },
  divot_episodes: {
    path: ".claude/window1_live_v4_replay/quote_reachability_20260730/WINDOW1_QUOTE_DIVOT_EPISODES.csv",
    sha256: "973e4c3edf985cca55001407f06540415e53eb6b6c2babdc099193b082df65ef",
  },
  os_rescore: {
    path: ".claude/window1_live_v4_replay/quote_touch_os_rescore_rebalanced_20260731/WINDOW1_QUOTE_TOUCH_OS_RESCORE.json",
    sha256: "3fd04e63033b7e9898511c651581e4c2f1660fc386c08d4fcd55db09f5e04fb4",
  },
  recognition: {
    path: ".claude/window1_t2_iteration_history/WINDOW1_T2_RECOGNITION_LAPS.json",
    sha256: "37bf1691218a55975da19ff06e2bfeb11c412166fc0928da45b30653bcd6a30c",
  },
  atlas_key_study: {
    path: ".claude/window1_live_v4_replay/atlas_interim_20260730_consult_v2/ATLAS_KEY_AND_INTERIM_STUDY.json",
    sha256: "fdb9357314dd8d9511af88f0f85ec1f9c101a76412bb2265c7cf851310e4988f",
  },
  orientation: {
    path: ".claude/window1_live_v4_replay/orientation_initial_20260730/ORIENTATION_INITIAL_REPLAY.json",
    sha256: "d6d761962afdab4030efc47d456e453c87bca8d9d5f67067200b5b7648509d56",
  },
  nikvrb_nondecision: {
    path: ".claude/window1_live_v4_replay/nikvrb_decision_autopsy_20260731/NIKVRB_NON_DECISION_LEDGER.csv",
    sha256: "cf2b8407ddf4eb257cb0cc00a34681f2638da03db1770c7532c568cd799297f1",
  },
  nikvrb_trace: {
    path: ".claude/window1_live_v4_replay/one_game_nikvrb_20260730/NIKVRB_DECISION_TRACE.json",
    sha256: "cf3ecdafc43ff0305ae95addd5a98fc1d53695dbbeae6c7080ad79de0fae1b42",
  },
  band_map: {
    path: "arb-executor/state/band_map_v1.json",
    sha256: "caf255a283bbb32f1d9bd2edd5f4d898d5f50fc8e67d5f9a076579b695a9e68c",
  },
  atlas: {
    path: ".claude/trendpath/ATLAS_V1.json",
    sha256: "efdfc2b414a752db560b7e494642632a0530c68f54b6d4e8f86d303887b5100c",
  },
  live_v4: {
    path: "arb-executor/live_v4.py",
    sha256: "f6fb1d20f3943f7bac26d94ccf1e9d98a5f22762cd3357394adfc8a3b108d760",
  },
  live_config: {
    path: "arb-executor/config/deploy_v5_live.json",
    sha256: "46607d2404d6794c30c6c61fd52d08c9e787a613a1984d8c21204457d5d2472f",
  },
  nikvrb_autopsy: {
    path: "arb-executor/docs/research/window1/NIKVRB_DECISION_AUTOPSY.md",
    sha256: "ffb29bc9e4585276cf3b72a9e790ead2fe53ebba8fb9f533ea48d40563a2a9f3",
  },
};

function sha256(bytes) {
  return crypto.createHash("sha256").update(bytes).digest("hex");
}

function canonical(value) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') {
        field += '"';
        i += 1;
      } else if (ch === '"') quoted = false;
      else field += ch;
    } else if (ch === '"') quoted = true;
    else if (ch === ",") {
      row.push(field);
      field = "";
    } else if (ch === "\n") {
      row.push(field.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      field = "";
    } else field += ch;
  }
  if (field || row.length) {
    row.push(field.replace(/\r$/, ""));
    rows.push(row);
  }
  const headers = rows.shift();
  return rows
    .filter((r) => r.length === headers.length)
    .map((r) => Object.fromEntries(headers.map((h, i) => [h, r[i]])));
}

function median(values) {
  if (!values.length) return null;
  const a = [...values].sort((x, y) => x - y);
  const m = Math.floor(a.length / 2);
  return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
}

function pct(n, d) {
  return d ? Number(((100 * n) / d).toFixed(1)) : null;
}

const sourceManifest = [];
const sourceBytes = {};
for (const [id, item] of Object.entries(INPUTS)) {
  const absolute = path.join(repo, item.path);
  const bytes = fs.readFileSync(absolute);
  const actual = sha256(bytes);
  if (actual !== item.sha256) {
    throw new Error(`source binding mismatch ${id}: ${actual} != ${item.sha256}`);
  }
  sourceBytes[id] = bytes;
  sourceManifest.push({ id, path: item.path, bytes: bytes.length, sha256: actual });
}

const quoteLegs = parseCsv(sourceBytes.quote_legs.toString("utf8"));
const legMap = new Map(quoteLegs.map((r) => [`${r.event_id}|${r.leg}`, r]));
const os = JSON.parse(sourceBytes.os_rescore.toString("utf8"));
const recognition = JSON.parse(sourceBytes.recognition.toString("utf8"));
const atlasStudy = JSON.parse(sourceBytes.atlas_key_study.toString("utf8"));
const orientation = JSON.parse(sourceBytes.orientation.toString("utf8"));
const nondecision = parseCsv(sourceBytes.nikvrb_nondecision.toString("utf8"));

if (quoteLegs.length !== 1608 || os.population !== 804) {
  throw new Error(`population mismatch legs=${quoteLegs.length} D=${os.population}`);
}
if (os.events.length !== 20100) throw new Error(`OS matrix rows ${os.events.length} != 20100`);

const recognitionRows = [];
function priceRegion(price) {
  if (price <= 25) return "le25";
  if (price <= 50) return "26_50";
  if (price <= 75) return "51_75";
  return "ge75";
}
for (const event of recognition.recognition.events) {
  for (const leg of event.legs || []) {
    const q = legMap.get(`${event.event_id}|${leg.leg_id}`);
    if (!q || q.quote_10s_floor_limit_cents === "") continue;
    for (const signal of leg.signals || []) {
      if (signal.instrument === "reach_law") continue;
      const depth = Number(signal.depth_cents);
      const target = Number(leg.current_bid_cents) - depth;
      const floor = Number(q.quote_10s_floor_limit_cents);
      recognitionRows.push({
        event_id: event.event_id,
        category: event.category,
        price_region: priceRegion(Number(leg.current_bid_cents)),
        leg_id: leg.leg_id,
        instrument: signal.instrument,
        band: signal.band || null,
        flow_state: leg.flow_state,
        net_cents: leg.net_cents,
        target_cents: target,
        floor_cents: floor,
        signed_error_cents: target - floor,
        reached: target >= floor,
      });
    }
  }
}

function recognitionBreakdown(id) {
  const rows = recognitionRows.filter((r) => r.instrument === id);
  const result = {};
  for (const row of rows) {
    if (!result[row.category]) result[row.category] = {};
    if (!result[row.category][row.price_region]) result[row.category][row.price_region] = [];
    result[row.category][row.price_region].push(row);
  }
  return Object.fromEntries(Object.entries(result).sort().map(([category, regions]) => [
    category,
    Object.fromEntries(Object.entries(regions).sort().map(([region, values]) => [region, {
      rows: values.length,
      median_signed_depth_error_cents: median(values.map((r) => r.signed_error_cents)),
      reached: values.filter((r) => r.reached).length,
      reached_rate_pct: pct(values.filter((r) => r.reached).length, values.length),
    }])),
  ]));
}

function organRecognition(id) {
  const rows = recognitionRows.filter((r) => r.instrument === id);
  return {
    rows: rows.length,
    median_signed_depth_error_cents: median(rows.map((r) => r.signed_error_cents)),
    reached: rows.filter((r) => r.reached).length,
    reached_rate_pct: pct(rows.filter((r) => r.reached).length, rows.length),
  };
}

const expectedRecognition = {
  w1_drift_atlas: { rows: 1000, median: -4, reached: 57 },
  band_taxonomy: { rows: 913, median: -3, reached: 96 },
  cohort_library: { rows: 953, median: -8, reached: 11 },
  aim_v2: { rows: 547, median: -5, reached: 12 },
};
for (const [id, expected] of Object.entries(expectedRecognition)) {
  const actual = organRecognition(id);
  if (
    actual.rows !== expected.rows ||
    actual.median_signed_depth_error_cents !== expected.median ||
    actual.reached !== expected.reached
  ) throw new Error(`recognition conservation failed for ${id}: ${JSON.stringify(actual)}`);
}

const fillLabel = "QUOTE_OR_PRINT_DWELL_10";
const modes = ["ATLAS", "ORIENTATION", "JOIN", "TOUCH_MINUS_1", "ONE_SPREAD_BELOW_MID"];
const modeNames = {
  ATLAS: "ATLAS",
  ORIENTATION: "ORIENTATION",
  JOIN: "JOIN",
  TOUCH_MINUS_1: "TOUCH_MINUS_1",
  ONE_SPREAD_BELOW_MID: "ONE_SPREAD_BELOW_MID",
};
const frozenOutcomes = modes.map((mode) => {
  const m = os.matrix[fillLabel][mode];
  return {
    mode: modeNames[mode],
    D: m.events,
    filled_legs: m.legs_filled,
    completed_pairs: m.pairs_completed,
    PC: m.negative_combined_delta,
    IC: m.both_legs_under_own_close,
  };
});
const joinOutcome = frozenOutcomes.find((r) => r.mode === "JOIN");
if (joinOutcome.PC !== 23 || joinOutcome.D !== 804) throw new Error("frozen 23/804 JOIN mismatch");

const joinRows = os.events.filter((e) => e.fill_model_label === fillLabel && e.mode === "JOIN");
if (joinRows.length !== 804) throw new Error(`JOIN event rows ${joinRows.length} != 804`);
const joinFilledLegs = [];
let joinNoFill = 0;
let joinNaked = 0;
for (const event of joinRows) {
  const legs = Object.entries(event.legs);
  const fills = legs.filter(([, leg]) => leg.filled);
  if (!fills.length) joinNoFill += 1;
  else if (fills.length === 1) joinNaked += 1;
  for (const [legId, leg] of fills) {
    joinFilledLegs.push({ event_id: event.event_id, leg_id: legId, ...leg });
  }
}
const laterLower = joinFilledLegs.filter(
  (r) => Number.isFinite(r.fill_minus_own_fillable_low_cents) && r.fill_minus_own_fillable_low_cents > 0
);
const laterLowerEvents = new Set(laterLower.map((r) => r.event_id));
const centsAboveFloor = laterLower.reduce((n, r) => n + r.fill_minus_own_fillable_low_cents, 0);
if (
  joinFilledLegs.length !== 601 || joinNaked !== 429 || joinNoFill !== 289 ||
  laterLower.length !== 245 || laterLowerEvents.size !== 240 || centsAboveFloor !== 565
) throw new Error("JOIN fill/later-floor conservation failed");

const pcIds = {};
for (const mode of modes) {
  pcIds[mode] = new Set(
    os.events
      .filter((e) => e.fill_model_label === fillLabel && e.mode === mode && e.negative_combined_delta)
      .map((e) => e.event_id)
  );
}
function comparison(mode) {
  const other = pcIds[mode];
  const join = pcIds.JOIN;
  return {
    against: mode,
    join_PC: join.size,
    other_PC: other.size,
    overlap: [...join].filter((id) => other.has(id)).length,
    join_only: [...join].filter((id) => !other.has(id)).length,
    other_only: [...other].filter((id) => !join.has(id)).length,
  };
}

const exactStartIds = ["HURBIG", "NIKVRB", "LAJVAN", "BRAVED", "KORJIM"];
const exactStart = [];
for (const shortId of exactStartIds) {
  const rows = joinRows.filter((e) => e.event_id.includes(shortId));
  if (rows.length !== 1) throw new Error(`exact-start identity ${shortId} count ${rows.length}`);
  const eventId = rows[0].event_id;
  const perMode = modes.map((mode) => {
    const event = os.events.find(
      (e) => e.event_id === eventId && e.fill_model_label === fillLabel && e.mode === mode
    );
    return {
      mode,
      completed: event.pair_completed,
      PC: event.negative_combined_delta,
      legs: Object.fromEntries(
        Object.entries(event.legs).map(([leg, x]) => [leg, {
          filled: x.filled,
          fill_price_cents: x.fill_price_cents,
          reachable_floor_cents: x.own_fillable_low_cents,
          fill_minus_floor_cents: x.fill_minus_own_fillable_low_cents,
        }])
      ),
    };
  });
  exactStart.push({ event_id: eventId, modes: perMode });
}
const exactPcs = exactStart.flatMap((e) => e.modes.filter((m) => m.PC).map((m) => `${e.event_id}|${m.mode}`));
if (exactPcs.length !== 1 || !exactPcs[0].includes("NIKVRB|JOIN")) {
  throw new Error(`exact-start PC conservation failed: ${exactPcs.join(",")}`);
}

const vrbCallbacks = nondecision.filter((r) => r.leg === "VRB");
const nikCallbacks = nondecision.filter((r) => r.leg === "NIK");
const vrbCadence = vrbCallbacks.filter((r) => r.signed_non_decision === "HOLD_CADENCE").length;
const vrbQuiet = vrbCallbacks.filter((r) => r.signed_non_decision === "HOLD_STAIRCASE_QUIET_FIFO").length;
const nikAskAtOrBelow24 = nikCallbacks.filter((r) => Number(r.ask) <= 24).length;
if (
  vrbCallbacks.length !== 874 || vrbCadence !== 6 || vrbQuiet !== 868 ||
  nikCallbacks.length !== 5534 || nikAskAtOrBelow24 !== 5387
) throw new Error("NIKVRB callback conservation failed");

if (atlasStudy.price_key_displacement_rows.length !== 1408 || atlasStudy.key_mismatch_rows.length !== 891) {
  throw new Error("ATLAS key-study population mismatch");
}
const displacementPageChanges = atlasStudy.price_key_displacement_rows.filter((r) => r.page_changed).length;
const strictPageChanges = atlasStudy.key_mismatch_rows.filter((r) => r.page_changed).length;
const strictRoleChanges = atlasStudy.key_mismatch_rows.filter((r) => r.role_changed).length;
if (displacementPageChanges !== 31 || strictPageChanges !== 14 || strictRoleChanges !== 8) {
  throw new Error("ATLAS key mismatch conservation failed");
}

const organScorecard = {
  schema_version: "WINDOW1_ORGAN_SCORECARD_V1",
  law: {
    scope: "Window 1 entry only",
    D: 804,
    opportunity_denominator: 598,
    frozen_best_PC: 23,
    fill_law: "positive true print at/through X or lawful opposite quote at/through X sustained 10 seconds",
    pair_law: "asynchronous combined-negative relative to each leg's frozen Window-1 close; IC never gates",
    signer_rule: "no organ receives execution authority from this scorecard",
  },
  headline: {
    maker_opportunity_PC: 598,
    frozen_JOIN_PC: 23,
    missed_PC_opportunities: 575,
    conclusion: "placement, not opportunity scarcity",
  },
  frozen_action_outcomes: frozenOutcomes,
  organ_rows: [
    {
      organ: "ATLAS",
      verdict: "ACTIVELY_WRONG",
      recognition: organRecognition("w1_drift_atlas"),
      recognition_category_price_region: recognitionBreakdown("w1_drift_atlas"),
      signed_live_aim_census: { rows: 1331, median_signed_depth_error_cents: -3, too_deep: 1205, reached: 126, reached_rate_pct: 9.5 },
      category_price_region: {
        ATP_CHALL: { le25: [-2, 12.0], "26_50": [-3, 8.7], "51_75": [-2, 13.2], ge75: [-5, 5.9] },
        ATP_MAIN: { le25: [-2, 24.0], "26_50": [-3, 14.6], "51_75": [-4, 9.4], ge75: [-11, 6.9] },
        WTA_CHALL: { le25: [-2.5, 0.0], "26_50": [-3, 6.0], "51_75": [-3, 4.5], ge75: [-3, 0.0] },
        WTA_MAIN: { le25: [-3, 10.0], "26_50": [-3, 13.7], "51_75": [-5, 5.4], ge75: [-9, 3.6] },
      },
      reason: "Targets are systematically below the 10-second reachable floor; JOIN gains 22 PC over ATLAS with no lost PC.",
      pre_entry_cell: false,
      signing_authority: false,
    },
    {
      organ: "BAND_B1_B8",
      verdict: "ACTIVELY_WRONG_EXCEPT_LOCAL_WTA_CHALL_B3",
      recognition: organRecognition("band_taxonomy"),
      recognition_category_price_region: recognitionBreakdown("band_taxonomy"),
      direction_test: { calls: 913, native_direction: "FLAT_FOR_ALL_CALLS", actual_flat: 257, actual_flat_rate_pct: 28.1, non_flat: 656, recurrent_pulses_ge_3c: 238 },
      by_category_band: {
        ATP_CHALL: { B1: [90, 16.7, 35], B4: [358, 27.1, 83], B6: [61, 31.1, 16] },
        ATP_MAIN: { B1: [21, 19.0, 11], B3: [51, 13.7, 23], B5: [50, 18.0, 23], B8: [12, 41.7, 3] },
        WTA_CHALL: { B3: [59, 57.6, 5], B6: [63, 34.9, 6], B8: [18, 27.8, 1] },
        WTA_MAIN: { B1: [44, 34.1, 7], B3: [52, 23.1, 21], B6: [34, 38.2, 4] },
      },
      tuple_meaning: "[calls, flat-direction hit %, recurrent >=3c pulses]",
      reason: "A print-keyed band map calls every measured leg flat in a quote-driven recurrence market.",
      pre_entry_cell: false,
      signing_authority: false,
    },
    {
      organ: "COHORT_LIBRARY",
      verdict: "ACTIVELY_WRONG",
      recognition: organRecognition("cohort_library"),
      recognition_category_price_region: recognitionBreakdown("cohort_library"),
      reason: "Median target is eight cents below the reachable floor and only 1.2% reach.",
      pre_entry_cell: false,
      signing_authority: false,
    },
    {
      organ: "AIM_V2",
      verdict: "ACTIVELY_WRONG",
      recognition: organRecognition("aim_v2"),
      recognition_category_price_region: recognitionBreakdown("aim_v2"),
      reason: "Median target is five cents below the reachable floor and only 2.2% reach.",
      pre_entry_cell: false,
      signing_authority: false,
    },
    {
      organ: "REACH_LAW",
      verdict: "ACTIVELY_OVERCONFIDENT",
      census: { rows: 2019, mean_predicted_reach_pct: 28.57, actual_reach_pct: 3.2, brier: 0.1824 },
      category_source_examples: {
        ATP_CHALL: { atlas: [32.02, 4.1], band: [37.11, 6.1], cohort: [16.97, 1.3] },
        WTA_CHALL: { atlas: [36.64, 1.8], band: [34.36, 2.1], cohort: [15.85, 0.0] },
      },
      tuple_meaning: "[predicted reach %, observed reach %]",
      category_price_region_status: "Source/category summaries exist, but the frozen scorecard does not reconstruct a missing per-row reach payload beyond the cited recognition rows.",
      pre_entry_cell: false,
      signing_authority: false,
    },
    {
      organ: "SELECTOR_CONTENTION",
      verdict: "ACTIVELY_INVERTED",
      census: { measurable: 1244, TRADE: 511, TRADE_good: 8, TRADE_good_pct: 1.6, DROP: 733, DROP_good: 21, DROP_good_pct: 2.9, selected_good: 29, any_fitted_tier_good: 199, missed_available_good_tier: 170 },
      reason: "TRADE underperforms DROP and selected tier misses 170 legs with a better fitted tier; enforcement remains off.",
      category_price_region_status: "The comparable selector census is preserved in aggregate; a complete 804-event tier-opinion payload was not retained, so missing cells are not fabricated.",
      pre_entry_cell: false,
      signing_authority: false,
    },
    {
      organ: "PAIR_VERDICT",
      verdict: "NOISE",
      census: { measurable: 582, verdict_COMPOSED: 582, actual_pair_negative: 450, false_positive: 132, base_rate_pct: 77.3 },
      reason: "Constant verdict has no discrimination and constructs sibling as 100-current instead of reading sibling evidence.",
      category_price_region_status: "Pair verdict is pair-grain, not a lawful per-leg price-region surface; splitting its synthetic sibling would compound the defect.",
      pre_entry_cell: "synthetic rather than observed",
      signing_authority: false,
    },
    {
      organ: "FLOW",
      verdict: "NOISE_OR_INVERTED",
      census: {
        quiet: { n: 657, fall: 191, unknown: 41, climb: 240, flat: 185, pulse_pct: 30.9 },
        warm: { n: 352, fall: 115, climb: 145, flat: 92, pulse_pct: 21.0 },
        open: { n: 11, fall: 2, climb: 3, flat: 6, pulse_pct: 9.1 },
      },
      reason: "Quiet has more large pulses than warm/open and does not identify direction.",
      category_price_region_status: "Flow is reported by causal state; the retained summary does not carry a complete category+region joint cube.",
      pre_entry_cell: true,
      signing_authority: false,
    },
    {
      organ: "ORIENTATION",
      verdict: "PROVISIONALLY_PREDICTIVE_BUT_UNDERINSTRUMENTED",
      census: { preserved_action_payloads: 5, pair_direction_correct: 4, completion_change: 0, mean_gap_before: 5.5, mean_gap_after: 5.75 },
      correct: ["HURBIG", "NIKVRB", "LAJVAN", "KORJIM"],
      reversed: ["BRAVED"],
      reason: "Four of five exact-start pairs have correct shape, but the 804-event opinion/confidence payload was not preserved and the frozen replay changes no completion.",
      category_price_region_status: "Only five exact-start action payloads survive; an 804-event category+region cube is unavailable.",
      pre_entry_cell: "available only for five retained actions",
      signing_authority: false,
    },
    {
      organ: "CONVICTION",
      verdict: "UNSCORABLE_INSTRUMENTATION_DEFECT",
      census: { preserved_rows: 123, date_scope: "2026-07-10 only", same_804_population: false },
      reason: "Not a comparable opinion surface for the frozen population.",
      category_price_region_status: "Unavailable: the only retained artifact is a 123-row July-10 population.",
      pre_entry_cell: false,
      signing_authority: false,
    },
    {
      organ: "LAST_TRADE_RELATIVE_TO_SPREAD",
      verdict: "SPARSE_WEAK_SIGNAL_NOT_AUTHORITY",
      census: {
        rows: 1409,
        above_ask: { n: 73, climb: 27, fall: 24, flat: 10, unknown: 12, stated_fall_hit_pct: 32.9 },
        at_ask: { n: 1131, climb: 368, fall: 300, flat: 280, unknown: 183, stated_fall_hit_pct: 26.5 },
        inside: { n: 42, call: "NO_CALL" },
        at_bid: { n: 147, climb: 61, fall: 38, flat: 28, unknown: 20, stated_climb_hit_pct: 41.5 },
        below_bid: { n: 16, climb: 5, fall: 0, flat: 6, unknown: 5, stated_climb_hit_pct_all_pct: 31.3, directional_hit: "5/5" },
        strict_joint_games: 3,
        strict_joint_both_correct: 1,
      },
      reason: "Below-bid direction is promising but only five directional rows; joint evidence exists for three games.",
      category_price_region_status: "The retained spread-position census is not a complete category+region cube; absence remains named.",
      pre_entry_cell: true,
      signing_authority: false,
    },
    {
      organ: "PAIR_SHAPE",
      verdict: "PROVISIONALLY_PREDICTIVE",
      census: { events: 804, largest_shape: "CLIMB+FALL", largest_shape_n: 296, flat_flat: 81, climb_flat: 112, strict_distinct_first_10s_floor: 597, first_CLIMB_sibling_FALL: 280, first_CLIMB_total: 382, rate_pct: 73.3 },
      reason: "Pair topology is materially stronger than scalar depth voices, but no full pre-entry signed action payload exists.",
      category_price_region_status: "Pair shape is event-grain; the category+region leg cube was not retained as a signed pre-entry opinion surface.",
      pre_entry_cell: "partial",
      signing_authority: false,
    },
  ],
  atlas_native_anchor_mismatch: {
    fitted_anchor: "first-hour discovery median",
    live_consult_anchor: "current last trade or tight mid",
    comparable_rows: atlasStudy.price_key_displacement_rows.length,
    page_changes: displacementPageChanges,
    signed_order_rows: atlasStudy.key_mismatch_rows.length,
    signed_page_changes: strictPageChanges,
    signed_role_changes: strictRoleChanges,
  },
  authority_ruling: {
    pen_awarded_to: null,
    retained_control: "JOIN lawful non-self book placement",
    rationale: "JOIN is the best frozen causal action at 23 PC, but a control is not evidence that a new organ deserves authority.",
    one_authority_chokepoint_armed: false,
  },
};

const defects = [
  {
    rank: 1,
    defect: "placement_gap_umbrella",
    measured_cost: { maker_opportunities: 598, frozen_JOIN_PC: 23, missed: 575 },
    cause_status: "CONSERVATION_ENVELOPE_NOT_A_SINGLE_CAUSE",
    proposed_fix: "Use the following causal layers; do not claim one organ explains all 575.",
    replay_gate: "Any fix must exceed 23/598 on the same 10-second law and preserve all exact-start controls.",
    retained: false,
  },
  {
    rank: 2,
    defect: "organ_disagreement_without_reliable_arbiter",
    measured_cost: { disagreeing_legs: 1013, disagreeing_events: 509, events_examined: 510, median_target_span_cents: 4, p90_target_span_cents: 21, negative_opportunity_events: 425, disagreement_and_missed_opportunity_events: 412 },
    proposed_fix: "Preserve JOIN until a pair-shape/recurrence candidate wins a full causal replay; record all voices without granting a pen.",
    exact_start_effect: "NIKVRB proves ATLAS can overwrite the correct pair shape; BRAVED proves orientation can also reverse it.",
    retained: false,
  },
  {
    rank: 3,
    defect: "ATLAS_deep_target_and_native_anchor_mismatch",
    measured_cost: { versus_JOIN_PC_lost: 22, versus_JOIN_completed_pairs_lost: 37, versus_JOIN_filled_legs_lost: 384, JOIN_PC_lost_to_ATLAS: 0, page_changes: 31, strict_page_changes: 14, strict_role_changes: 8 },
    proposed_fix: "Demote ATLAS to context and restore its native discovery anchor before any future retest.",
    exact_start_effect: "JOIN preserves NIKVRB PC; ATLAS produces no exact-start PC.",
    retained: "JOIN_BASELINE_ONLY",
  },
  {
    rank: 4,
    defect: "filled_leg_disables_entry_review",
    measured_cost: { filled_legs_with_later_lower_floor: 245, events: 240, cents_above_later_floor: 565, median_cents: 2, max_cents: 25, NIK_post_fill_callbacks: 5534, NIK_ask_at_or_below_fill: 5387 },
    proposed_fix: "Continue diagnostic price review after fill, but never re-buy: exact-five means the later lower price is opportunity evidence, not entry authority.",
    exact_start_effect: "NIK filled exactly five at 24; the later 18 cannot be lawfully recaptured without DCA/re-buy.",
    retained: false,
  },
  {
    rank: 5,
    defect: "staircase_quiet_hold_masks_recurrence",
    measured_cost: { NIKVRB_VRB_callbacks: 874, cadence_holds: 6, quiet_FIFO_holds: 868, ask_68_quote_state_visits: 9, residence_seconds: 641 },
    proposed_fix: "Test an episode-keyed recurrence response: recognition receipt cannot fill its action; only strictly later recurrence may credit.",
    exact_start_effect: "NIKVRB JOIN is already PC, so this specimen alone cannot move 23; full 804 replay is mandatory.",
    retained: false,
  },
  {
    rank: 6,
    defect: "band_print_cell_applied_to_quote_recurrence",
    measured_cost: { calls: 913, actual_non_flat: 656, recurrent_ge_3c_pulses: 238, flat_hit_pct: 28.1 },
    proposed_fix: "Remove band signing authority; preserve B1-B8 only as descriptive print-conditioned context until quote-native validation exists.",
    retained: false,
  },
  {
    rank: 7,
    defect: "selector_contention_inversion",
    measured_cost: { selected_good: 29, available_good: 199, missed_available_good: 170, TRADE_good_pct: 1.6, DROP_good_pct: 2.9 },
    proposed_fix: "Do not enable contention enforcement; retest only after native anchors and a causal target outcome are bound.",
    retained: false,
  },
  {
    rank: 8,
    defect: "reach_probability_overconfidence",
    measured_cost: { rows: 2019, predicted_pct: 28.57, observed_pct: 3.2, brier: 0.1824 },
    proposed_fix: "Prevent reach probability from signing price until recalibrated on the quote-or-print law.",
    retained: false,
  },
  {
    rank: 9,
    defect: "cohort_and_AIM_V2_too_deep",
    measured_cost: { cohort_rows: 953, cohort_reach_pct: 1.2, AIM_V2_rows: 547, AIM_V2_reach_pct: 2.2 },
    proposed_fix: "Demote both to context; do not average them into a scalar target.",
    retained: false,
  },
  {
    rank: 10,
    defect: "pair_verdict_fabricates_sibling",
    measured_cost: { rows: 582, constant_COMPOSED: 582, false_positive: 132 },
    proposed_fix: "Require actual causal sibling book/print state and retain UNKNOWN when absent.",
    retained: false,
  },
  {
    rank: 11,
    defect: "window_truth_and_arrival_use_different_reaim_paths",
    measured_cost: { NIKVRB_first_sibling_reaim: "65->73", move_reposts: 9, window_truth_reaims: 5 },
    proposed_fix: "Unify receipt-keyed arrival/reaim reason accounting, then replay; do not infer an 804-event cost from one specimen.",
    retained: false,
  },
  {
    rank: 12,
    defect: "missing_pre_entry_opinion_payloads",
    measured_cost: { orientation_actions: 5, conviction_rows: 123, conviction_date: "2026-07-10", required_events: 804 },
    proposed_fix: "Instrument opinions before action without changing actions; score only once the full population exists.",
    retained: false,
  },
];

const defectLedger = {
  schema_version: "WINDOW1_DEFECT_LEDGER_V1",
  population: { D: 804, frozen_score: "23/598", opportunity_gap: 575 },
  keep_rule: "A proposed execution change is retained only after a same-law full replay exceeds 23 PC without violating exact-five, asynchronous pair, or exact-start controls.",
  defects,
  retained_changes: [],
  retained_control_facts: ["JOIN remains the frozen comparator at 23 PC"],
  forbidden_interpretations: [
    "post-fill lower prices authorize a re-buy",
    "five-share scarcity is the primary price-reach law",
    "individual-negative is a PC gate",
    "a constant COMPOSED verdict proves pair information",
    "a NIKVRB-only improvement moves the 23/598 aggregate",
  ],
};

const exactStartReceipt = {
  schema_version: "WINDOW1_EXACT_START_VALIDATION_V1",
  event_count: exactStart.length,
  events: exactStart,
  negative_pair_completions: exactPcs,
  ruling: "NIKVRB JOIN is the only exact-start PC under the frozen 10-second law; all future fixes must preserve it and may not use the post-fill NIK 18-cent tape as a second entry.",
};

const sourceReceipt = {
  schema_version: "WINDOW1_ORGAN_SCORECARD_SOURCE_MANIFEST_V1",
  git_parent: "2140f5231da50f24483468bafee0c512368dd3d7",
  sources: sourceManifest,
  access: { scorer_invoked: false, live_v4_executed: false, network_accessed: false, holdout_accessed: false, files_mutated_before_part1_report: false },
};

const report = `# Window-1 organ scorecard and defect ledger

## Ruling

The frozen scoreboard remains **23 PC from 598 maker-reachable negative-pair opportunities** under the 10-second true-print-or-opposite-quote law. The 575-event gap is a placement gap, not evidence scarcity.

No organ gets the pen. The only retained fact is the unchanged JOIN control: it produces 23 PC, versus 1 for ATLAS/orientation and 3 for touch-minus-one/one-spread. This document changes no strategy or live code.

## Organ scorecard

| Organ | Comparable evidence | Verdict | Why it cannot sign |
|---|---:|---|---|
| ATLAS | 1,000 recognition rows; median error -4c; 5.7% reach | Actively wrong | Systematically too deep; JOIN gains 22 PC with no ATLAS-only PC. |
| Band B1-B8 | 913 calls; 28.1% actual flat; 238 pulses | Actively wrong except local WTA_CHALL B3 | Every native call is FLAT in a quote-recurrence market. |
| Cohort | 953; median -8c; 1.2% reach | Actively wrong | Deepest systematic miss. |
| AIM_V2 | 547; median -5c; 2.2% reach | Actively wrong | Sparse cells do not recover the floor. |
| Reach | 2,019; 28.57% predicted vs 3.2% actual | Actively overconfident | It magnifies the wrong depth voices. |
| Selector/contention | 1,244; TRADE 1.6% vs DROP 2.9% good | Actively inverted | Selected 29 good targets while 199 fitted tiers contained one. |
| Pair verdict | 582; 582 COMPOSED; 132 false positives | Noise | It synthesizes sibling as 100-current and never discriminates. |
| Flow | 1,020 recognition states | Noise/inverted | Quiet contains more large pulses than warm/open. |
| Orientation | 4/5 pair shapes correct; zero completion change | Provisionally predictive | Only five action payloads survive; mean gap worsens 5.5c to 5.75c. |
| Conviction | 123 rows from July 10 | Unscorable | Not the 804-event population. |
| Last trade / spread | 1,409; below-bid 5/5 directional but n=5 | Sparse weak signal | Only three games have strict joint two-leg evidence. |
| Pair shape | 597 strict two-leg floors; climb sibling falls 73.3% | Provisionally predictive | Strongest shape evidence, but no full pre-entry signed action surface. |

Signed error is target minus the reachable 10-second floor: negative means the order was too deep. \`ORGAN_SCORECARD.json\` freezes a category+price-region cube for every recognition instrument with a comparable row payload, plus the B1-B8 table. For reach, selector, pair verdict, flow, orientation, conviction, last-trade position, and pair shape, the file explicitly names why a complete comparable category+region cube is unavailable rather than manufacturing one.

## Frozen action comparison

| Action | Filled legs | Completed | PC | IC |
|---|---:|---:|---:|---:|
${frozenOutcomes.map((r) => `| ${r.mode} | ${r.filled_legs} | ${r.completed_pairs} | ${r.PC} | ${r.IC} |`).join("\n")}

ATLAS and orientation are outcome-identical. JOIN versus ATLAS has 22 JOIN-only PC, one shared PC, and zero ATLAS-only PC. Touch-minus-one and one-spread each have two PC that JOIN misses, but each loses 22 JOIN PC; they are not replacements.

## Shape, not scalar depth

The pair surface is not two independent depth numbers. The largest joint shape is climb+fall (296 games); among 382 games whose first revealed leg climbs, the sibling falls in 280 (73.3%). The combined-negative pair law and the 100-sum topology must remain explicit. No scalar organ may be applied before a lawful pre-entry cell exists.

Last-trade position relative to the spread is retained as a joint contextual predictor, not authority. Below-bid last trade points climb in all five directional rows, but the full bucket has only 16 observations and only three games have strict joint two-leg evidence.

## Defect ledger, ordered by measured cost

| Rank | Defect | Measured cost | Fix / disposition |
|---:|---|---|---|
${defects.map((d) => `| ${d.rank} | ${d.defect} | ${Object.entries(d.measured_cost).map(([k, v]) => `${k}=${v}`).join("; ")} | ${d.proposed_fix} **Retained: ${String(d.retained)}.** |`).join("\n")}

## NIKVRB control

VRB made 874 pre-fill decisions while resting at 65: six cadence holds and 868 quiet-staircase FIFO holds. Its ask occupied 68 in nine quote states for 641 seconds. Those are affirmative non-decisions.

NIK is different. After the five-lot filled at 24, 5,534 BBO callbacks occurred, 5,387 with ask at or below 24. None entered the entry manager because the leg was active. The later 18-cent tape is diagnostic opportunity; exact-five forbids a fourth move or re-buy.

Under the frozen 10-second matrix, JOIN already makes NIKVRB a PC pair (NIK 24, VRB 69, combined delta -9). Therefore a NIKVRB-only recurrence repair cannot claim movement above 23. It must be tested across all 804 games.

## Five exact-start controls

Only NIKVRB under JOIN is PC. HURBIG, LAJVAN, BRAVED, and KORJIM remain incomplete across the five frozen actions. \`EXACT_START_VALIDATION.json\` preserves every leg result and reachable-floor gap.

## Keep / discard gate

No proposed mechanism is retained. JOIN remains the comparator, not a new strategy. A future recurrence-aware pair-first candidate must:

1. use causal BBO/print receipts and strictly later fill evidence;
2. preserve exact-five and never reinterpret post-fill review as re-buy/DCA;
3. preserve the NIKVRB JOIN PC and all five exact-start memberships;
4. exceed 23 PC on the same 598-opportunity, 804-event, 10-second law;
5. identify a complete pre-entry cell before an organ may sign.

Until then, no one-authority chokepoint is armed.

## Containment

This build reads committed development artifacts only. It does not execute \`live_v4.py\`, invoke a scorer, access holdout/live/network data, or modify any order, position, exit, settlement, or Window-2 state.
`;

const files = {
  "ORGAN_SCORECARD.json": canonical(organScorecard),
  "DEFECT_LEDGER.json": canonical(defectLedger),
  "EXACT_START_VALIDATION.json": canonical(exactStartReceipt),
  "SOURCE_HASH_MANIFEST.json": canonical(sourceReceipt),
};
const artifactRows = Object.entries(files).map(([name, text]) => ({
  path: `.claude/window1_organ_scorecard_20260731/${name}`,
  bytes: Buffer.byteLength(text),
  sha256: sha256(Buffer.from(text)),
}));
artifactRows.push({
  path: "arb-executor/docs/research/window1/WINDOW1_ORGAN_SCORECARD_AND_DEFECT_LEDGER.md",
  bytes: Buffer.byteLength(report),
  sha256: sha256(Buffer.from(report)),
});
const determinism = canonical({
  schema_version: "WINDOW1_ORGAN_SCORECARD_DETERMINISM_V1",
  command: "node arb-executor/analysis/build_window1_organ_scorecard.js .",
  check_command: "node arb-executor/analysis/build_window1_organ_scorecard.js . --check",
  canonical_encoding: "UTF-8 LF; JSON two-space indentation and terminal LF",
  artifacts: artifactRows,
  result: "BYTE_IDENTICAL_WHEN_CHECK_COMMAND_PASSES",
});
files["DETERMINISTIC_REGENERATION_RECEIPT.json"] = determinism;
const artifactManifest = canonical({
  schema_version: "WINDOW1_ORGAN_SCORECARD_ARTIFACT_MANIFEST_V1",
  artifacts: [
    ...artifactRows,
    {
      path: ".claude/window1_organ_scorecard_20260731/DETERMINISTIC_REGENERATION_RECEIPT.json",
      bytes: Buffer.byteLength(determinism),
      sha256: sha256(Buffer.from(determinism)),
    },
  ],
});
files["ARTIFACT_HASH_MANIFEST.json"] = artifactManifest;

function compareOrWrite(filePath, text) {
  if (checkOnly) {
    if (!fs.existsSync(filePath)) throw new Error(`missing generated artifact ${filePath}`);
    const actual = fs.readFileSync(filePath);
    if (!actual.equals(Buffer.from(text))) throw new Error(`non-deterministic artifact ${filePath}`);
  } else {
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    fs.writeFileSync(filePath, text, "utf8");
  }
}

for (const [name, text] of Object.entries(files)) compareOrWrite(path.join(outDir, name), text);
compareOrWrite(reportPath, report);

process.stdout.write(canonical({
  status: checkOnly ? "CHECK_PASS" : "BUILD_PASS",
  D: 804,
  opportunity: 598,
  frozen_PC: 23,
  organ_pen: null,
  retained_execution_changes: 0,
  artifacts: Object.keys(files).length + 1,
}));
