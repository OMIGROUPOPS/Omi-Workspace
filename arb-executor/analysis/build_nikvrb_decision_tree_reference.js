#!/usr/bin/env node
"use strict";

// Deterministic NIK-VRB two-leg decision-tree reference. Reads frozen replay
// evidence only; never imports/executes live_v4 and never runs a population
// replay or scorer.

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const repo = path.resolve(process.argv[2] || ".");
const checkOnly = process.argv.includes("--check");
const outDir = path.join(
  repo,
  ".claude/window1_live_v4_replay/nikvrb_decision_tree_20260731"
);
const reportPath = path.join(
  repo,
  "arb-executor/docs/research/window1/NIKVRB_DECISION_TREE_REFERENCE.md"
);

const INPUTS = {
  clock: [
    ".claude/window1_live_v4_replay/nikvrb_coupling_20260730/NIKVRB_DUAL_BOOK_CLOCK.csv",
    "9ec9ef0fab27cd750a7d3fba1407bc6c6a8955104071f27b67dac6bd7f8965e5",
  ],
  quote_series: [
    ".claude/window1_live_v4_replay/nikvrb_coupling_20260730/NIKVRB_DUAL_QUOTE_SERIES.csv",
    "14df33928268d3bb043e7d067f8742c30a9b08bd0e190e2698e252001754ff9b",
  ],
  clock_summary: [
    ".claude/window1_live_v4_replay/nikvrb_coupling_20260730/NIKVRB_DUAL_BOOK_CLOCK_SUMMARY.json",
    "0416f9028d6bcc0b0a9943816fa38cabbacb3d65a249ce3f650b8c131db66b71",
  ],
  ask68_visits: [
    ".claude/window1_live_v4_replay/nikvrb_decision_autopsy_20260731/NIKVRB_VRB_ASK68_VISITS.csv",
    "383089cc2bf24f060e21de92fb53656341d38a956d49e946434fc6186129f9c1",
  ],
  nondecision: [
    ".claude/window1_live_v4_replay/nikvrb_decision_autopsy_20260731/NIKVRB_NON_DECISION_LEDGER.csv",
    "cf2b8407ddf4eb257cb0cc00a34681f2638da03db1770c7532c568cd799297f1",
  ],
  silence: [
    ".claude/window1_live_v4_replay/nikvrb_decision_autopsy_20260731/NIKVRB_SILENCE_CENSUS.json",
    "e8f3ad33d924309a247d5b7afd2f4c0709509854686f0bb56f8fb7269d75446d",
  ],
  trace: [
    ".claude/window1_live_v4_replay/one_game_nikvrb_20260730/NIKVRB_DECISION_TRACE.json",
    "cf3ecdafc43ff0305ae95addd5a98fc1d53695dbbeae6c7080ad79de0fae1b42",
  ],
  autopsy: [
    "arb-executor/docs/research/window1/NIKVRB_DECISION_AUTOPSY.md",
    "ffb29bc9e4585276cf3b72a9e790ead2fe53ebba8fb9f533ea48d40563a2a9f3",
  ],
  live_v4: [
    "arb-executor/live_v4.py",
    "f6fb1d20f3943f7bac26d94ccf1e9d98a5f22762cd3357394adfc8a3b108d760",
  ],
  config: [
    "arb-executor/config/deploy_v5_live.json",
    "46607d2404d6794c30c6c61fd52d08c9e787a613a1984d8c21204457d5d2472f",
  ],
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

function csvEscape(value) {
  const text = value === null || value === undefined ? "" : String(value);
  return /[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

function csvText(columns, rows) {
  return `${[
    columns.join(","),
    ...rows.map((row) => columns.map((column) => csvEscape(row[column])).join(",")),
  ].join("\n")}\n`;
}

function ts(value) {
  return Date.parse(value) / 1000;
}

function tminus(min) {
  const sign = min >= 0 ? "T-" : "T+";
  return `${sign}${Math.abs(min).toFixed(3)}`;
}

const sourceBytes = {};
const sourceRows = [];
for (const [id, [relative, expected]] of Object.entries(INPUTS)) {
  const bytes = fs.readFileSync(path.join(repo, relative));
  const actual = sha256(bytes);
  if (actual !== expected) throw new Error(`${id} source mismatch ${actual} != ${expected}`);
  sourceBytes[id] = bytes;
  sourceRows.push({ id, path: relative, bytes: bytes.length, sha256: actual });
}

const clock = parseCsv(sourceBytes.clock.toString("utf8"));
const visits = parseCsv(sourceBytes.ask68_visits.toString("utf8"));
const nondecisions = parseCsv(sourceBytes.nondecision.toString("utf8"));
const trace = JSON.parse(sourceBytes.trace.toString("utf8"));
const clockSummary = JSON.parse(sourceBytes.clock_summary.toString("utf8"));
const silence = JSON.parse(sourceBytes.silence.toString("utf8"));
const config = JSON.parse(sourceBytes.config.toString("utf8"));

if (clock.length !== 13123 || nondecisions.length !== 6408 || visits.length !== 9) {
  throw new Error(`population mismatch clock=${clock.length} decisions=${nondecisions.length} visits=${visits.length}`);
}
if (config.orientation_live !== false || config.interim_entry_aim_mode !== "ATLAS") {
  throw new Error("deployed orientation/aim binding changed");
}
if (config.combined_goal !== 97 || config.staircase_hold_trail_burst !== 5) {
  throw new Error("deployed budget/hold binding changed");
}

const SCHEDULED = ts("2026-07-19T12:30:00-04:00");
const BELL = ts("2026-07-19T12:35:00-04:00");
function clocks(epoch) {
  return {
    tminus_scheduled: tminus((SCHEDULED - epoch) / 60),
    tminus_bell: tminus((BELL - epoch) / 60),
  };
}

const preliminaryTargets = {
  "2026-07-19T06:28:05-04:00|NIK": 29,
  "2026-07-19T07:07:33-04:00|NIK": 26,
  "2026-07-19T07:13:58-04:00|VRB": 69,
  "2026-07-19T07:15:43-04:00|VRB": 67,
  "2026-07-19T07:51:21-04:00|NIK": 24,
};

const consultations = trace.consultations.map((call, index) => {
  const key = `${call.time_et}|${call.leg}`;
  const riser = call.orientation.riser === call.leg;
  const p75 = call.atlas.depth_p25_p50_p75[2];
  const orientationTarget = riser
    ? preliminaryTargets[key]
    : Math.max(1, call.anchor.price - p75);
  return {
    sequence: index + 1,
    time_et: call.time_et,
    ...clocks(ts(call.time_et)),
    leg: call.leg,
    call_class: index === 0 || index === 2
      ? "DISCOVERY_REALIZED"
      : "REALIZED_AFTER_MARKETABLE_STALE_GATE",
    inputs: {
      book: call.book,
      anchor: call.anchor,
      joint_orientation: call.orientation,
      flow: call.flow,
    },
    ordered_organs: [
      { organ: "fresh_print_anchor", returned: `${call.anchor.source}:${call.anchor.price}`, opens: "native cell, regime, and preliminary role" },
      { organ: "orientation_prior", returned: `${call.orientation.riser}_RISER conviction=${call.orientation.conviction}`, opens: riser ? "riser_near_now" : "faller_deep_cast" },
      { organ: "cohort/preliminary", returned: `target=${preliminaryTargets[key]}`, opens: "preliminary target only" },
      { organ: "selector/contention", returned: `${call.contention.verdict}:${call.contention.best_pct}%`, opens: call.contention.verdict === "DROP" ? "veto only if contention_drop_enforced" : "path continues" },
      { organ: "pair_verdict", returned: `${call.pair.verdict}:${call.pair.combined_at_path}`, opens: "composition label; synthetic sibling only" },
      { organ: "initial_entry_aim", returned: `ATLAS:${call.atlas.aim}`, opens: "actual price assignment" },
      { organ: "orientation_live_branch", returned: config.orientation_live ? `ACTIVE:${orientationTarget}` : `SKIPPED:${orientationTarget}`, opens: config.orientation_live ? "role-conditioned aim" : "nothing" },
      { organ: "final_assignment", returned: String(call.actual_order_cents), opens: "resting entry interval" },
    ],
    preliminary_target_cents: preliminaryTargets[key],
    actual_ATLAS_target_cents: call.actual_order_cents,
    orientation_consumed_target_cents: orientationTarget,
    join_target_cents: call.book.bid,
    signer: call.actual_signer || call.named_authority,
    overwritten: riser
      ? `riser-near-now ${preliminaryTargets[key]} overwritten by ATLAS ${call.actual_order_cents}`
      : `faller branch available at ${orientationTarget}; ATLAS signed ${call.actual_order_cents}`,
  };
});

const decisionLedger = [];
for (const call of consultations) {
  decisionLedger.push({
    timestamp_et: call.time_et,
    epoch: ts(call.time_et),
    tminus_scheduled: call.tminus_scheduled,
    tminus_bell: call.tminus_bell,
    leg: call.leg,
    call_class: call.call_class,
    fired: "PRICED_CONSULTATION",
    door_opened: call.inputs.joint_orientation.riser === call.leg ? "RISER_NEAR_NOW_PRELIMINARY" : "FALLER_CAST_PRELIMINARY",
    signed_decision: `PLACE_${call.actual_ATLAS_target_cents}`,
    signer_or_return: "ATLAS_P50",
    reachable_after: "entry placement and resting manager",
    unreachable_after: "orientation-conditioned final aim; alternative fitted tiers; unenforced contention veto",
    code_path: "live_v4.py:4739-5009;2960-3055;5057-5080;12029-12164",
  });
}

for (const row of nondecisions) {
  decisionLedger.push({
    timestamp_et: row.timestamp_et,
    epoch: ts(row.timestamp_et),
    tminus_scheduled: row.tminus_scheduled,
    tminus_bell: row.tminus_actual_bell,
    leg: row.leg,
    call_class: row.leg === "VRB" ? "REALIZED_AFTER_RESTING_GATE" : "REALIZED_AFTER_FILL_GATE",
    fired: row.router_return,
    door_opened: row.leg === "VRB" ? "RESTING_MANAGER" : "ACTIVE_POSITION_CONTINUE",
    signed_decision: row.signed_non_decision,
    signer_or_return: row.signed_non_decision,
    reachable_after: row.leg === "VRB" ? "next BBO callback; existing FIFO order" : "exit management only",
    unreachable_after: row.overwritten_or_unreached,
    code_path: row.code_path,
  });
}

const transitionRows = [
  ["2026-07-19T06:28:57-04:00", "NIK", "ASYNC_STATE_REALIZATION", "BAND_B4_FLAT", "band became readable after first NIK placement", "live_v4 band cascade"],
  ["2026-07-19T07:14:42-04:00", "VRB", "ASYNC_STATE_REALIZATION", "BAND_B4_FLAT", "band became readable after first VRB placement", "live_v4 band cascade"],
  ["2026-07-19T10:39:57.500480-04:00", "NIK", "FILL_TRANSITION", "FILL_24_PHASE_ACTIVE", "entry manager becomes unreachable", "live_v4.py:9777-9787"],
  ["2026-07-19T10:40:14-04:00", "VRB", "POST_FIRST_FILL_REALIZATION", "REPRICE_65_TO_73", "combined headroom readable; opportunity already gone", "live_v4.py:7290-7293;13501-13600"],
  ["2026-07-19T11:09:33-04:00", "VRB", "ASYNC_STATE_REALIZATION", "BAND_B2_FALLER", "late band change; early 70 divot no longer reachable", "live_v4 band cascade"],
  ["2026-07-19T12:30:12-04:00", "PAIR", "GUN_TRANSITION", "PRICE_DIVERGENCE_GUN", "fresh entry paths freeze", "live_v4 gun state"],
  ["2026-07-19T12:30:33-04:00", "VRB", "POLICY_TERMINATION", "CANCEL_REMAINING_ENTRY", "no further Window-1 entry exposure", "live_v4 match-live cancellation"],
];
for (const [time, leg, callClass, decision, effect, code] of transitionRows) {
  const c = clocks(ts(time));
  decisionLedger.push({
    timestamp_et: time,
    epoch: ts(time),
    tminus_scheduled: c.tminus_scheduled,
    tminus_bell: c.tminus_bell,
    leg,
    call_class: callClass,
    fired: decision,
    door_opened: decision,
    signed_decision: decision,
    signer_or_return: decision,
    reachable_after: effect,
    unreachable_after: "see effect",
    code_path: code,
  });
}
decisionLedger.sort((a, b) => a.epoch - b.epoch || a.leg.localeCompare(b.leg));

const latestClockAt = (epoch) => {
  let chosen = null;
  for (const row of clock) {
    if (ts(row.timestamp_et) > epoch) break;
    chosen = row;
  }
  return chosen;
};

const visitBranches = visits.map((visit) => {
  const joint = latestClockAt(ts(visit.valid_from_et));
  const number = Number(visit.visit);
  return {
    visit: number,
    interval_et: `${visit.valid_from_et}..${visit.valid_to_et}`,
    tminus_scheduled: visit.tminus_scheduled_at_start,
    tminus_bell: visit.tminus_bell_at_start,
    joint_book: {
      NIK: { bid: Number(joint.NIK_bid), ask: Number(joint.NIK_ask), last: Number(joint.NIK_last) },
      VRB: { bid: Number(visit.quote_state_bid), ask: Number(visit.quote_state_ask), last: Number(joint.VRB_last) },
      bid_total: Number(joint.NIK_bid) + Number(visit.quote_state_bid),
      ask_total: Number(joint.NIK_ask) + Number(visit.quote_state_ask),
    },
    actual: number === 1 ? "NO_VRB_ORDER" : number === 2 ? "CANCEL_67_THEN_PLACE_65" : "REST_65__QUIET_STAIRCASE_HOLD",
    orientation_riser_strict_ask_credit_first: number === 1
      ? "NO_VRB_ORDER_YET"
      : number === 2
        ? "CREDIT_FILL_AT_ORIGINAL_69"
        : "ALREADY_FILLED_AT_69__NO_RESTING_ENTRY",
    orientation_riser_cancel_first: number === 1
      ? "NO_VRB_ORDER_YET"
      : number === 2
        ? "CANCEL_69_THEN_RECONCEIVE_67"
        : "REST_67__NOT_68_OR_69",
    release_staircase_only: number <= 2
      ? "UNCHANGED_EARLIER_PATH"
      : "MAKER_CEILING_67; DOWNSTREAM_EVIDENCE_HOLD_CAN_STILL_KEEP_65",
  };
});

const firstVrb = consultations.find((r) => r.time_et === "2026-07-19T07:13:58-04:00");
if (!firstVrb || firstVrb.preliminary_target_cents !== 69 || firstVrb.actual_ATLAS_target_cents !== 67) {
  throw new Error("decisive VRB junction mismatch");
}
if (visitBranches[2].actual !== "REST_65__QUIET_STAIRCASE_HOLD") {
  throw new Error("visit branch mismatch");
}

const counterfactual = {
  schema_version: "NIKVRB_COUNTERFACTUAL_BRANCHES_V1",
  event: trace.event,
  scope: "one-game decision-tree validation; not an 804-event candidate or score",
  call_coverage: {
    raw_market_clock_rows: clock.length,
    exact_priced_consultations: consultations.length,
    exact_repeated_nondecision_rows: nondecisions.length,
    exact_transition_rows_added: transitionRows.length,
    exact_decision_ledger_rows: decisionLedger.length,
    aggregate_only_skip_no_trade_observations: {
      VRB: 349,
      NIK: 4,
      reason: "The committed trace preserves state transition counts but the referenced full per-call trace is absent; timestamps are not fabricated.",
    },
  },
  consultations,
  branches: [
    {
      branch: "ACTUAL",
      changed_door: null,
      path: "orientation opens VRB-riser preliminary 69 -> ATLAS overwrites 67 -> marketable-stale cancel -> ATLAS 65 -> staircase quiet holds",
      VRB_exposure_before_return_to_68: 65,
      result: "miss early divot; post-fill reaim 73 arrives 206.3 minutes after low",
    },
    {
      branch: "CONSUME_ORIENTATION_RISER_AT_FIRST_VRB_CALL",
      changed_door: "live_v4.py:12095-12110; retain target_bid=69 at 07:13:58 instead of ATLAS=67",
      path: "VRB riser -> near-now 69 -> rest 84 seconds before ask returns to 68",
      VRB_exposure_before_return_to_68: 69,
      result_under_strict_ask_credit_first: "fill once at original X=69 on visit 2; visits 3/4/9 have no resting entry because leg is filled",
      result_under_current_cancel_first_ordering: "cancel 69 as marketable-stale and reconceive 67; visits 3/4/9 rest 67",
      ruling: "This is the single structural divergence, but fill-before-cancel ordering is a separate required invariant.",
    },
    {
      branch: "JOIN_AUTHORITY_NUMERIC_CONTROL",
      changed_door: "initial_entry_aim JOIN returns contemporaneous best bid",
      path: "07:13:58 book 69/70 -> target 69",
      frozen_result: "NIKVRB completes PC in the existing 10-second JOIN replay at NIK=24, VRB=69",
      structural_status: "numeric corroboration only; JOIN does not explain why the riser should receive the price",
    },
    {
      branch: "RELEASE_STAIRCASE_ONLY",
      changed_door: "do not early-return at quiet staircase hold",
      path: "visits 3/4/9 book is 67/68; maker-safe maximum is 67",
      result: "cannot put a bid at 68 or 69 and may still be held at 65 by downstream no-evidence logic",
    },
    {
      branch: "ENFORCE_CONTENTION_DROP",
      changed_door: "contention_drop_enforced=true",
      path: "VRB selector says DROP at both priced calls",
      result: "no VRB entry; strictly worse on this specimen",
    },
    {
      branch: "WAIT_FOR_BAND",
      changed_door: "require band before placement",
      path: "VRB B4/flat becomes readable at 07:14:42, 44 seconds after the first priced call",
      result: "opens too late to create the 07:13:58 order; flat does not uniquely select 69",
    },
  ],
  ask_68_visit_branches: visitBranches,
  single_junction: {
    time_et: "2026-07-19T07:13:58-04:00",
    tminus_scheduled: "T-316.033",
    tminus_bell: "T-321.033",
    actual: "orientation prior opens riser-near-now 69, then ATLAS p50 overwrites it with 67",
    should: "consume the already-open riser branch and rest at 69",
    code: "live_v4.py:4863-5009 -> 12072-12110 -> 12163",
    causal_gap_seconds_before_ask_68_visit_2: 84,
  },
};

const jointTree = {
  schema_version: "NIKVRB_JOINT_DECISION_TREE_V1",
  event: trace.event,
  settlement_inverse_constraint_cents: 100,
  entry_pair_budget_cents: 97,
  decisive_snapshot: {
    timestamp_et: clockSummary.focus_vrb_70.timestamp_et,
    tminus_scheduled: clockSummary.focus_vrb_70.tminus_scheduled,
    tminus_bell: clockSummary.focus_vrb_70.tminus_actual_bell,
    NIK: { bid: 28, ask: 29, last: 32, resting_order: 26, inferred_role: "FALLER" },
    VRB: { bid: 69, ask: 70, last: 70, resting_order_actual_after_call: 67, role: "RISER" },
    totals: { bid: 97, ask: 99, last: 102, proposed_resting_pair_orientation_path: 95 },
    collapsed_options: {
      VRB: "riser near-now: 69",
      NIK: "faller cast already resting: 26",
      combined: "69+26=95 <= 97",
    },
  },
  sibling_read_map: [
    { path: "orientation_prior", reads_actual_sibling: true, use: "names VRB riser/NIK faller", consumed_by_final_signer: false },
    { path: "pair_verdict", reads_actual_sibling: false, use: "fabricates 100-current complement", consumed_by_final_signer: false },
    { path: "pair_seesaw_state", reads_actual_sibling: true, use: "refusal ceiling only", consumed_by_final_signer: "constraint only" },
    { path: "initial_entry_aim", reads_actual_sibling: false, use: "symmetric per-leg ATLAS p50", consumed_by_final_signer: true },
    { path: "post_fill_arrival", reads_actual_sibling: true, use: "headroom after NIK fill", consumed_by_final_signer: "too late; lower-only helper returns" },
  ],
  conditional_semantics: [
    {
      upstream_door: "VRB_RISER",
      later_input: "B4_FLAT at 07:14:42",
      path_conditioned_meaning: "A shallow flat/pulse state after a riser call is compatible with retouch/recurrence; it does not reset the leg to a symmetric deep target.",
      executable_mapping_in_frozen_code: false,
    },
    {
      upstream_door: "NIK_FALLER",
      later_input: "declining print/BBO path",
      path_conditioned_meaning: "The same downward tick supports a patient faller cast; after the exact-five fill it is diagnostic only.",
      executable_mapping_in_frozen_code: "initial cast exists; post-fill entry mapping correctly absent",
    },
    {
      upstream_door: "VRB_RISER",
      later_input: "quiet flow with ask retouches",
      path_conditioned_meaning: "Quiet print cadence does not prove absence of a quote pulse; the nine ask-68 states remain causal market evidence.",
      executable_mapping_in_frozen_code: false,
    },
  ],
  temporal_path: [
    { time: "06:28:05", tminus_scheduled: "T-361.917", tminus_bell: "T-366.917", event: "NIK discovery", availability: "orientation already says VRB riser; NIK is faller" },
    { time: "07:13:56.179481", tminus_scheduled: "T-316.064", tminus_bell: "T-321.064", event: "VRB true print 70", availability: "actual joint books 97 bid / 99 ask / 102 last" },
    { time: "07:13:58", tminus_scheduled: "T-316.033", tminus_bell: "T-321.033", event: "decisive aim call", availability: "69 path exists now; band not yet available" },
    { time: "07:14:42", tminus_scheduled: "T-315.300", tminus_bell: "T-320.300", event: "VRB B4 flat realized", availability: "downstream only; cannot retroactively open 07:13:58" },
    { time: "07:15:22", tminus_scheduled: "T-314.633", tminus_bell: "T-319.633", event: "ask returns 68", availability: "69 exposure would be certain under strict-ask law" },
    { time: "07:21:12..07:39:00", tminus_scheduled: "T-308.800..T-291.000", tminus_bell: "T-313.800..T-296.000", event: "visits 3-9", availability: "too late for 68/69 maker placement; ceiling 67" },
    { time: "10:39:57.500480", tminus_scheduled: "T-110.042", tminus_bell: "T-115.042", event: "NIK fills 24", availability: "post-fill pair headroom opens after VRB pulse era" },
    { time: "10:40:14", tminus_scheduled: "T-109.767", tminus_bell: "T-114.767", event: "VRB 65->73", availability: "lawful but 206.3 minutes after VRB low; later minimum 74" },
    { time: "11:09:09..11:38:49", tminus_scheduled: "T-80.838..T-51.172", tminus_bell: "T-85.838..T-56.172", event: "NIK slides 23->19->18", availability: "NIK already exact-five active; no entry path exists" },
  ],
  conclusion: "The legs are one asynchronous inverse tree. At the decisive snapshot, orientation and actual books collapse VRB to near-now 69 and NIK to the existing faller cast 26. The OS reads this shape, then discards it before price assignment.",
};

const ledgerColumns = [
  "timestamp_et", "epoch", "tminus_scheduled", "tminus_bell", "leg",
  "call_class", "fired", "door_opened", "signed_decision",
  "signer_or_return", "reachable_after", "unreachable_after", "code_path",
];
const ledgerText = csvText(ledgerColumns, decisionLedger);

const report = `# NIKVRB two-leg decision-tree reference

This document sits beside \`NIKVRB_DECISION_AUTOPSY.md\`. The autopsy says what each organ returned. This reference says what the return meant **inside the path that made it reachable**.

It is a one-game structural validation only. It does not modify \`live_v4.py\`, execute a replay, score the 804, or grant any organ global authority.

## Answer first: the single divergence

At **07:13:58 ET (T-316.033 scheduled / T-321.033 bell)**, the joint orientation prior had already classified VRB as the riser with conviction 1.0. Inside \`_v4_entry_anchor\`, that door made VRB's role-specific preliminary target the live bid, **69**. NIK's faller order was already resting at 26, so the joint proposed basis was 95, inside the 97 pair budget.

The tree then left that branch. \`_initial_entry_aim\` recomputed VRB independently as \`70 - ATLAS p50 3 = 67\`. Because \`orientation_live=false\`, lines 12095-12110 did not restore 69. Line 12163 assigned 67.

**The divergence is: orientation opened the correct riser branch, but the final aim layer did not consume the branch.**

Changing that one decision node at this call rests 69 for 84 seconds before the ask returns to 68. Under strict-ask-credit-before-cancel law, it fills once at the original 69 on visit 2. If cancellation is allowed to run first, it cancels and reconceives 67. That execution ordering is a separate invariant; the trace does not conceal it.

## The tree the OS walked

\`\`\`mermaid
flowchart TD
  A["Fresh VRB print 70; book 69/70"] --> B["Orientation: VRB riser, NIK faller"]
  B --> C["Preliminary riser target: 69"]
  C --> D["Selector: DROP, but veto disabled"]
  D --> E["Pair verdict: COMPOSED using synthetic sibling 30"]
  E --> F["ATLAS p50 overwrites 69 with 67"]
  F --> G["orientation_live false: role branch skipped"]
  G --> H["Place 67"]
  H --> I["Ask 68: cancel marketable-stale"]
  I --> J["Re-conceive through same tree; 67 becomes 65"]
  J --> K["6 cadence returns + 868 quiet staircase returns"]
  K --> L["NIK fills 24 at T-110"]
  L --> M["Arrival helper sees 65 already under cap and returns"]
  M --> N["Regular manager raises VRB to 73, 206.3m after low"]
\`\`\`

The five priced calls and all 6,408 receipt-resolvable repeated returns are in \`NIKVRB_PATH_DECISION_LEDGER.csv\`. Calls are labeled \`DISCOVERY_REALIZED\`, \`REALIZED_AFTER_MARKETABLE_STALE_GATE\`, \`REALIZED_AFTER_RESTING_GATE\`, or \`REALIZED_AFTER_FILL_GATE\`; later organs are not misreported as discovery facts.

The committed trace also reports 349 VRB and four NIK \`skip_no_trade\` observations. Their state transitions and counts survive, but the referenced full per-call trace is absent. They remain an aggregate evidence boundary and are not assigned fabricated timestamps. The 13,123-row market clock is complete market chronology; it is not falsely relabeled as 13,123 OS calls.

## What each later organ meant after the door

| Door already taken | Later return | Meaning in that branch | What became unreachable |
|---|---|---|---|
| Fresh-print anchor | native cell/page | A priced consultation may exist | No-fresh-trade skip path |
| Orientation says VRB riser | preliminary 69 | near-now riser catch while NIK casts | symmetric depth should be contextual, not a role reset |
| Selector returns DROP | -6.5% | a veto only if enforcement is enabled | Nothing; enforcement was false |
| Pair returns COMPOSED | 93 | synthetic-complement composition label | Actual NIK 28/29 state remains unread by this organ |
| ATLAS p50 | 67 | independent depth target | The already-open 69 branch is overwritten |
| \`orientation_live=false\` | skip | ATLAS remains signer | role-conditioned 69 cannot return |
| VRB entry_resting | cadence/staircase return | preserve 65 FIFO | best-bid mismatch, recurrence, window truth, cohort, repost |
| NIK phase active | manager guard false | exact-five leg is done | every fourth-move/re-buy path, correctly |
| NIK first fill | pair headroom 73 | sibling price becomes lawful | early VRB pulse is already historical |

Band and tick semantics are branch-conditioned. VRB's B4/flat state arrived at 07:14:42, after the riser door and first order. Inside a VRB-riser branch, “flat” is compatible with a shallow retouch; it does not logically reset the leg to symmetric deep-cast posture. Conversely, a downward tick in NIK's faller branch supports patience until fill, but becomes entry-ineligible afterward. These interpretations are structural diagnostics: the frozen code does not contain a source-proven composed band/flow action mapping, so this reference does not invent one.

## Counterfactual junctions

| Changed door | Path opened | Position before the 68 pulse | Result on this specimen |
|---|---|---:|---|
| Consume orientation-riser at 07:13:58 | role target 69 | 69 | Strict ask 68 credits 69 on visit 2; cancel-first ordering falls back to 67. |
| Use JOIN as numeric control | contemporaneous bid 69 | 69 | Frozen JOIN replay completes NIKVRB at NIK 24 / VRB 69; this corroborates price, not structure. |
| Release staircase only | later resting manager | at most 67 | Too late: visits 3/4/9 are already 67/68, so maker-safe ceiling is 67. |
| Enforce contention DROP | refusal | none | Worse: no VRB exposure. |
| Wait for band B4 | band-aware path after 07:14:42 | not present at 07:13:58 | Too late and flat does not uniquely select 69. |

### Visits 3, 4, and 9

| Visit | Clock at start | Actual | Orientation branch with strict-ask credit | Orientation branch with cancel-first ordering |
|---:|---|---|---|---|
${[3, 4, 9].map((n) => {
  const v = visitBranches[n - 1];
  return `| ${n} | ${v.tminus_scheduled} / ${v.tminus_bell} | ${v.actual} | ${v.orientation_riser_strict_ask_credit_first} | ${v.orientation_riser_cancel_first} |`;
}).join("\n")}

There is no honest late single-door change that rests 68 or 69 during these visits: ask is already 68, so a maker buy cannot exceed 67. The useful door is earlier.

## The tree it should have walked

\`\`\`mermaid
flowchart TD
  A["Both books causal: NIK 28/29, VRB 69/70"] --> B["Orientation: VRB riser; NIK faller"]
  B --> C["Collapse roles: VRB near-now; NIK cast"]
  C --> D["NIK existing order 26 + VRB bid 69 = 95"]
  D --> E["95 <= pair budget 97"]
  E --> F["Rest VRB 69 at 07:13:58"]
  F --> G["Later ask 68 is strict-ask evidence"]
  G --> H["Credit original 69 before maker-safety action"]
  H --> I["Keep NIK exact-five path independent and asynchronous"]
\`\`\`

This is not “orientation wins a vote.” It is: orientation selects a branch; within the riser branch, near-now has a different meaning than it has for the faller. The sibling state constrains the price simultaneously but the legs may fill hours apart.

## Joint tree: where sibling state is and is not read

At the decisive VRB print, the actual joint state was:

| | NIK | VRB | Total |
|---|---:|---:|---:|
| Bid | 28 | 69 | 97 |
| Ask | 29 | 70 | 99 |
| Last | 32 | 70 | 102 |
| Proposed role-path order | 26 | 69 | 95 |

The inverse constraint collapses the roles: VRB-riser near now and NIK-faller cast. \`_orientation_prior\` reads both bids and sees this. \`_pair_verdict\` does not: it substitutes \`100-current\`. \`_pair_seesaw_state\` reads the sibling only as a refusal ceiling. \`_initial_entry_aim\`, which signs, returns to a one-leg ATLAS number.

Thus sibling state becomes readable before pricing, is partially read, and is then discarded at the signing junction. It becomes authoritative only after NIK fills, when it is 206.3 minutes too late for VRB's low.

## Time is the branch-availability axis

| Time | Scheduled / bell | Door availability |
|---|---|---|
| 06:28:05 | T-361.917 / T-366.917 | NIK discovery; orientation already identifies VRB riser/NIK faller. |
| 07:13:56.179481 | T-316.064 / T-321.064 | VRB print 70; actual joint state becomes causal. |
| 07:13:58 | T-316.033 / T-321.033 | The 69 riser path exists. This is the decisive junction. |
| 07:14:42 | T-315.300 / T-320.300 | VRB B4/flat appears only after first placement. |
| 07:15:22 | T-314.633 / T-319.633 | Ask 68 returns; a 69 order has evidence now. |
| 07:21-07:39 | T-308.8..T-291 / T-313.8..T-296 | Visits 3-9; late maker ceiling is only 67. |
| 10:39:57.500480 | T-110.042 / T-115.042 | NIK fills 24; post-fill sibling door opens. |
| 10:40:14 | T-109.767 / T-114.767 | VRB raises to 73 after its pulse window; minimum afterward is 74. |
| 11:09-11:38 | T-80.8..T-51.2 / T-85.8..T-56.2 | NIK slides to 18, but its exact-five entry branch is already closed. |

VRB's actionable pulse path exists before T-120. NIK's material slide is after it. A pair organ invoked only after the first fill cannot recover the early branch; in this event, “late” means “nonexistent.”

## Validation ruling before 804

NIKVRB validates the **structure**:

1. a joint orientation call can open role-specific child paths;
2. the actual signer can overwrite that path and erase its meaning;
3. the sibling is observable early enough to enforce the 97 budget;
4. a later resting-manager change cannot recreate the early 69 door;
5. strict ask credit must precede maker-safety cancellation for the original exposure;
6. NIK's post-fill decline must remain outside entry authority.

It does **not** validate a global flag or an 804-event strategy. Enabling \`orientation_live\` globally also deepens faller calls (for example NIK's p75 path), so that complete branch must be replayed causally before population use. No 804 run is performed here.

## Reproduction and containment

- Build: \`node arb-executor/analysis/build_nikvrb_decision_tree_reference.js .\`
- Verify: \`node arb-executor/analysis/build_nikvrb_decision_tree_reference.js . --check\`
- Focused test: \`node arb-executor/tests/test_nikvrb_decision_tree_reference.js\`

All inputs are hash-bound in \`SOURCE_HASH_MANIFEST.json\`. No scorer, live engine, holdout, network, order, position, exit, settlement, DCA, or Window-2 surface is accessed.
`;

const sourceManifest = canonical({
  schema_version: "NIKVRB_DECISION_TREE_SOURCE_MANIFEST_V1",
  git_parent: "b9577450ff412f37f80b612b9e6ba1d096eef975",
  sources: sourceRows,
  invariants: {
    live_v4_executed: false,
    scorer_invoked: false,
    population_replay_invoked: false,
    holdout_accessed: false,
    live_or_network_accessed: false,
    live_v4_modified: false,
  },
});

const files = {
  "NIKVRB_PATH_DECISION_LEDGER.csv": ledgerText,
  "NIKVRB_COUNTERFACTUAL_BRANCHES.json": canonical(counterfactual),
  "NIKVRB_JOINT_TREE.json": canonical(jointTree),
  "SOURCE_HASH_MANIFEST.json": sourceManifest,
};
const artifacts = Object.entries(files).map(([name, text]) => ({
  path: `.claude/window1_live_v4_replay/nikvrb_decision_tree_20260731/${name}`,
  bytes: Buffer.byteLength(text),
  sha256: sha256(Buffer.from(text)),
}));
artifacts.push({
  path: "arb-executor/docs/research/window1/NIKVRB_DECISION_TREE_REFERENCE.md",
  bytes: Buffer.byteLength(report),
  sha256: sha256(Buffer.from(report)),
});
const determinism = canonical({
  schema_version: "NIKVRB_DECISION_TREE_DETERMINISM_V1",
  build_command: "node arb-executor/analysis/build_nikvrb_decision_tree_reference.js .",
  check_command: "node arb-executor/analysis/build_nikvrb_decision_tree_reference.js . --check",
  encoding: "UTF-8 LF; canonical JSON and CSV",
  decision_rows: decisionLedger.length,
  artifacts,
  result: "BYTE_IDENTICAL_WHEN_CHECK_COMMAND_PASSES",
});
files["DETERMINISTIC_REGENERATION_RECEIPT.json"] = determinism;
files["ARTIFACT_HASH_MANIFEST.json"] = canonical({
  schema_version: "NIKVRB_DECISION_TREE_ARTIFACT_MANIFEST_V1",
  artifacts: [
    ...artifacts,
    {
      path: ".claude/window1_live_v4_replay/nikvrb_decision_tree_20260731/DETERMINISTIC_REGENERATION_RECEIPT.json",
      bytes: Buffer.byteLength(determinism),
      sha256: sha256(Buffer.from(determinism)),
    },
  ],
});

function compareOrWrite(filePath, text) {
  if (checkOnly) {
    if (!fs.existsSync(filePath)) throw new Error(`missing ${filePath}`);
    if (!fs.readFileSync(filePath).equals(Buffer.from(text))) {
      throw new Error(`non-deterministic artifact ${filePath}`);
    }
  } else {
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    fs.writeFileSync(filePath, text, "utf8");
  }
}

for (const [name, text] of Object.entries(files)) compareOrWrite(path.join(outDir, name), text);
compareOrWrite(reportPath, report);

process.stdout.write(canonical({
  status: checkOnly ? "CHECK_PASS" : "BUILD_PASS",
  event: trace.event,
  raw_clock_rows: clock.length,
  decision_rows: decisionLedger.length,
  repeated_nondecisions: nondecisions.length,
  ask_68_visits: visits.length,
  decisive_junction: counterfactual.single_junction,
  population_scored: false,
}));
