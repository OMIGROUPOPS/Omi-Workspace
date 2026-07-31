#!/usr/bin/env node
"use strict";

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");
const { runColdReplay } = require("./nikvrb_sibling_shape_cold_replay.js");

const repo = path.resolve(process.argv[2] || ".");
const checkOnly = process.argv.includes("--check");
const outDir = path.join(repo, ".claude/window1_live_v4_replay/nikvrb_sibling_shape_tune_20260731");
const reportPath = path.join(repo, "arb-executor/docs/research/window1/NIKVRB_SIBLING_SHAPE_REPLAY.md");

const INPUTS = {
  clock: [
    ".claude/window1_live_v4_replay/nikvrb_coupling_20260730/NIKVRB_DUAL_BOOK_CLOCK.csv",
    "9ec9ef0fab27cd750a7d3fba1407bc6c6a8955104071f27b67dac6bd7f8965e5",
  ],
  trace: [
    ".claude/window1_live_v4_replay/one_game_nikvrb_20260730/NIKVRB_DECISION_TRACE.json",
    "cf3ecdafc43ff0305ae95addd5a98fc1d53695dbbeae6c7080ad79de0fae1b42",
  ],
  ask68: [
    ".claude/window1_live_v4_replay/nikvrb_decision_autopsy_20260731/NIKVRB_VRB_ASK68_VISITS.csv",
    "383089cc2bf24f060e21de92fb53656341d38a956d49e946434fc6186129f9c1",
  ],
  prior_tree: [
    ".claude/window1_live_v4_replay/nikvrb_decision_tree_20260731/NIKVRB_COUNTERFACTUAL_BRANCHES.json",
    "939064abd665a37644644300ecc622a10384cf4ffcc5f41d0e21d45659137962",
  ],
  live_v4: [
    "arb-executor/live_v4.py",
    "f6fb1d20f3943f7bac26d94ccf1e9d98a5f22762cd3357394adfc8a3b108d760",
  ],
  deploy_config: [
    "arb-executor/config/deploy_v5_live.json",
    "46607d2404d6794c30c6c61fd52d08c9e787a613a1984d8c21204457d5d2472f",
  ],
  time_axis: [
    "arb-executor/analysis/aim_time_axis.py",
    "5cab94e67060cc1bda186fb5ca2fbcde1ab02ce64fd1762209983b02514221ca",
  ],
};

function sha256(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
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
  return rows.filter((r) => r.length === headers.length)
    .map((r) => Object.fromEntries(headers.map((h, i) => [h, r[i]])));
}

function gzipJsonlBase64(rows) {
  const text = `${rows.map((row) => JSON.stringify(row)).join("\n")}\n`;
  return `${zlib.gzipSync(Buffer.from(text), { level: 9, mtime: 0 }).toString("base64")}\n`;
}

function cleanText(value) {
  return String(value === null || value === undefined ? "" : value).replace(/\|/g, "\\|").replace(/\n/g, " ");
}

function intOrNull(value) {
  if (value === "" || value === null || value === undefined) return null;
  const n = Number(value);
  return Number.isInteger(n) ? n : null;
}

function epoch(value) {
  const milliseconds = Date.parse(value);
  if (!Number.isFinite(milliseconds)) throw new Error(`invalid timestamp ${value}`);
  return milliseconds / 1000;
}

function buildQuoteTransitions(rows, leg) {
  const transitions = [];
  let prior = { bid: null, ask: null };
  let priorKey = "__UNSEEN__";
  let verifiedLast = null;
  for (const row of rows) {
    if (row.event_kind === `PRINT_${leg}` && row[`${leg}_print_trade_id`]) {
      verifiedLast = {
        receipt: row[`${leg}_print_trade_id`],
        timestamp_et: row.timestamp_et,
        price: intOrNull(row[`${leg}_print_price`]),
        size: Number(row[`${leg}_print_size`]),
      };
    }
    const bid = intOrNull(row[`${leg}_bid`]);
    const ask = intOrNull(row[`${leg}_ask`]);
    const key = `${bid}|${ask}`;
    if (key === priorKey) continue;
    const changedSides = [];
    if (bid !== prior.bid) changedSides.push("bid");
    if (ask !== prior.ask) changedSides.push("ask");
    const transition = {
      sequence: Number(row.sequence),
      timestamp_et: row.timestamp_et,
      epoch: epoch(row.timestamp_et),
      tminus_scheduled: row.tminus_scheduled,
      tminus_bell: row.tminus_actual_bell,
      trigger: row.event_kind,
      bid,
      ask,
      raw_normalized_last: intOrNull(row[`${leg}_last`]),
      latest_verified_print_at_transition: verifiedLast ? { ...verifiedLast } : null,
      changed_sides: changedSides,
      next_transition_epoch: null,
      duration_to_next_transition_seconds: null,
    };
    if (transitions.length) {
      const previous = transitions[transitions.length - 1];
      previous.next_transition_epoch = transition.epoch;
      previous.duration_to_next_transition_seconds = Number((transition.epoch - previous.epoch).toFixed(6));
    }
    transitions.push(transition);
    prior = { bid, ask };
    priorKey = key;
  }
  return transitions;
}

function quoteLeadIn(transitions, decision, count) {
  const decisionEpoch = epoch(decision.timestamp_et);
  return transitions
    .filter((row) => row.sequence >= 2 && row.sequence <= decision.sequence)
    .slice(-count)
    .map((row) => ({
      sequence: row.sequence,
      timestamp_et: row.timestamp_et,
      tminus_scheduled: row.tminus_scheduled,
      tminus_bell: row.tminus_bell,
      bid: row.bid,
      ask: row.ask,
      raw_normalized_last: row.raw_normalized_last,
      latest_verified_print_at_transition: row.latest_verified_print_at_transition,
      changed_sides: row.changed_sides,
      seconds_held_before_next_change_or_decision: Number((Math.max(
        0,
        Math.min(row.next_transition_epoch === null ? decisionEpoch : row.next_transition_epoch, decisionEpoch) - row.epoch
      )).toFixed(6)),
    }));
}

function recentPrints(rows, leg, decision, count = 5) {
  return rows
    .filter((row) => Number(row.sequence) <= decision.sequence
      && row.event_kind === `PRINT_${leg}`
      && row[`${leg}_print_trade_id`])
    .slice(-count)
    .map((row) => ({
      sequence: Number(row.sequence),
      timestamp_et: row.timestamp_et,
      tminus_scheduled: row.tminus_scheduled,
      tminus_bell: row.tminus_actual_bell,
      price: intOrNull(row[`${leg}_print_price`]),
      size: Number(row[`${leg}_print_size`]),
      receipt: row[`${leg}_print_trade_id`],
    }));
}

function pulseRecurrenceBreakdown(rows, leg, throughSequence) {
  const state = {
    bid: { prior: null, down: false, trough: null, recurrences: 0 },
    ask: { prior: null, down: false, trough: null, recurrences: 0 },
  };
  for (const row of rows) {
    if (Number(row.sequence) > throughSequence) break;
    for (const side of ["bid", "ask"]) {
      const value = intOrNull(row[`${leg}_${side}`]);
      if (!Number.isInteger(value)) continue;
      const s = state[side];
      if (Number.isInteger(s.prior) && value < s.prior) {
        s.down = true;
        s.trough = value;
      } else if (s.down && value > s.trough) {
        s.recurrences += 1;
        s.down = false;
        s.trough = null;
      } else if (s.down && value < s.trough) s.trough = value;
      s.prior = value;
    }
  }
  return {
    bid_recurrences: state.bid.recurrences,
    ask_recurrences: state.ask.recurrences,
    total: state.bid.recurrences + state.ask.recurrences,
    definition: "each bid or ask fall below its immediately prior value arms a local trough; the next value above that trough completes one recurrence",
  };
}

function quoteRows(rows) {
  return rows.map((row) => {
    const verified = row.latest_verified_print_at_decision || row.latest_verified_print_at_transition;
    return `| ${row.tminus_scheduled} / ${row.tminus_bell} | ${row.bid ?? "—"}/${row.ask ?? "—"} | ${row.changed_sides.join("+") || "none"} | ${row.seconds_held_before_next_change_or_decision}s | ${row.raw_normalized_last ?? "—"} | ${verified ? `${verified.price} @ ${verified.timestamp_et.slice(11, 19)}` : "none"} |`;
  }).join("\n");
}

const sourceBytes = {};
const sourceManifest = [];
for (const [id, [relative, expected]] of Object.entries(INPUTS)) {
  const bytes = fs.readFileSync(path.join(repo, relative));
  const actual = sha256(bytes);
  if (actual !== expected) throw new Error(`${id} source mismatch ${actual} != ${expected}`);
  sourceBytes[id] = bytes;
  sourceManifest.push({ id, path: relative, bytes: bytes.length, sha256: actual });
}

const rawClock = parseCsv(sourceBytes.clock.toString("utf8"));
const trace = JSON.parse(sourceBytes.trace.toString("utf8"));
const visits = parseCsv(sourceBytes.ask68.toString("utf8"));
if (rawClock.length !== 13123 || visits.length !== 9 || trace.consultations.length !== 5) {
  throw new Error(`frozen input mismatch rows=${rawClock.length} visits=${visits.length} calls=${trace.consultations.length}`);
}

const current = runColdReplay({ rawRows: rawClock, trace, scenario: "current" });
const tuned = runColdReplay({ rawRows: rawClock, trace, scenario: "tuned" });

const expected = {
  vrb_fill_price: 69,
  vrb_fill_et: "2026-07-19T07:15:22.000000-04:00",
  patience_arm_et: "2026-07-19T10:30:39.000000-04:00",
  patience_arm_bid: 24,
  faller_release_et: "2026-07-19T10:40:57.000000-04:00",
  faller_target: 19,
  nik_fill_et: "2026-07-19T11:09:20.922837-04:00",
  nik_fill_price: 19,
};

const tunedPlace = tuned.material_decisions.find((row) => row.action === "PLACE_NIK_19");
if (!tuned.fills.VRB || tuned.fills.VRB.price !== expected.vrb_fill_price
    || tuned.fills.VRB.evidence_et !== expected.vrb_fill_et
    || !tuned.patience || tuned.patience.armed_et !== expected.patience_arm_et
    || tuned.patience.arm_bid !== expected.patience_arm_bid
    || !tunedPlace || tunedPlace.timestamp_et !== expected.faller_release_et
    || !tuned.fills.NIK || tuned.fills.NIK.price !== expected.nik_fill_price
    || tuned.fills.NIK.evidence_et !== expected.nik_fill_et) {
  throw new Error(`cold replay acceptance mismatch ${JSON.stringify({ fills: tuned.fills, patience: tuned.patience, tunedPlace })}`);
}
if (!current.fills.NIK || current.fills.NIK.price !== 21
    || !current.fills.VRB || current.fills.VRB.price !== 69) {
  throw new Error("current orientation branch no longer reproduces NIK21/VRB69");
}

const closes = { NIK: 19, VRB: 83 };
const fillableLows = { NIK: 18, VRB: 70 };
const tunedOutcome = {
  pair_complete: Boolean(tuned.fills.NIK && tuned.fills.VRB),
  pair_cost_cents: tuned.fills.NIK.price + tuned.fills.VRB.price,
  individual_delta_to_close_cents: {
    NIK: tuned.fills.NIK.price - closes.NIK,
    VRB: tuned.fills.VRB.price - closes.VRB,
  },
  combined_delta_to_close_cents:
    tuned.fills.NIK.price - closes.NIK + tuned.fills.VRB.price - closes.VRB,
  gap_to_own_fillable_low_cents: {
    NIK: tuned.fills.NIK.price - fillableLows.NIK,
    VRB: tuned.fills.VRB.price - fillableLows.VRB,
  },
  grading_note: "both legs are independently within one cent of their own frozen fillable low; no aggregate leg offsets the other",
};

const eventKindCounts = {};
for (const row of rawClock) eventKindCounts[row.event_kind] = (eventKindCounts[row.event_kind] || 0) + 1;
const marketReceiptCount = Object.entries(eventKindCounts)
  .filter(([kind]) => kind.startsWith("BBO_") || kind.startsWith("PRINT_"))
  .reduce((sum, [, count]) => sum + count, 0);
const noDecisionCounts = {};
for (const row of tuned.decision_ledger.filter((row) => !row.material)) {
  noDecisionCounts[row.action] = (noDecisionCounts[row.action] || 0) + 1;
}

const firstAsk18 = rawClock.find((row) => Number(row.NIK_ask) === 18);
const firstPrint18 = rawClock.find((row) => row.event_kind === "PRINT_NIK" && Number(row.NIK_print_price) === 18);
const nondecisionSummary = {
  raw_clock_rows: rawClock.length,
  lawful_market_receipts_reconsidered: marketReceiptCount,
  material_decisions: tuned.material_decisions.length,
  repeated_nondecision_counts: noDecisionCounts,
  lock_points: {
    before_first_true_print: "discovery gate: no price authority",
    while_resting: "hold unless a named consultation, fill receipt, T2 sibling-shape resolution, or full-cell release fires",
    patience: "no NIK order until its live bid is one full five-cent cell below the T2 arm bid and VRB remains above its fill",
    after_leg_fill: "that leg's entry route is locked; books and tape remain readable",
    after_pair_fill: "all Window-1 entry routes are locked",
  },
  first_NIK_ask_18: firstAsk18 ? {
    timestamp_et: firstAsk18.timestamp_et,
    tminus_scheduled: firstAsk18.tminus_scheduled,
    tminus_bell: firstAsk18.tminus_actual_bell,
    tuned_state: "PAIR_ENTRY_COMPLETE; NIK already filled 19 on independent print evidence",
  } : null,
  first_NIK_print_18: firstPrint18 ? {
    timestamp_et: firstPrint18.timestamp_et,
    tminus_scheduled: firstPrint18.tminus_scheduled,
    tminus_bell: firstPrint18.tminus_actual_bell,
    tuned_state: "PAIR_ENTRY_COMPLETE; no re-buy",
  } : null,
};

const clockBySequence = new Map(rawClock.map((row) => [Number(row.sequence), row]));
const visualOrder = (order) => {
  const start = clockBySequence.get(order.action_sequence);
  const end = clockBySequence.get(order.end_sequence);
  return {
    leg: order.leg,
    price: order.price,
    quantity: order.quantity,
    start_sequence: order.action_sequence,
    start_et: order.action_et,
    start_tminus_scheduled: start.tminus_scheduled,
    start_tminus_bell: start.tminus_actual_bell,
    end_sequence: order.end_sequence,
    end_et: order.end_et,
    end_tminus_scheduled: end.tminus_scheduled,
    end_tminus_bell: end.tminus_actual_bell,
    end_reason: order.end_reason,
    authority: order.authority,
  };
};
const visualAcceptance = {
  schema_version: "NIKVRB_VISUAL_ACCEPTANCE_V1",
  clock_source: INPUTS.clock[0],
  clock_sha256: INPUTS.clock[1],
  current_orientation_branch: {
    orders: current.order_intervals.map(visualOrder),
    fills: current.fills,
  },
  corrected_sibling_shape_branch: {
    orders: tuned.order_intervals.map(visualOrder),
    fills: tuned.fills,
  },
  acceptance_marks: {
    VRB: "both branches rest 69 before strict ask 68 credits 69",
    NIK_current: "21 remains resting until the later public print 19 credits 21",
    NIK_corrected: "21 cancels at T-119.350 scheduled; 19 rests from T-109.050 until public print 19 credits 19 at T-80.651",
    later_ask_18: "arrives at T-57.483 scheduled after pair-entry lock; no re-buy",
  },
};

const visitDecisions = visits.map((visit) => ({
  visit: Number(visit.visit),
  time_et: visit.valid_from_et,
  tminus_scheduled: visit.tminus_scheduled_at_start,
  tminus_bell: visit.tminus_bell_at_start,
  book: `${visit.quote_state_bid}/${visit.quote_state_ask}`,
  current: visit.decision,
  tuned: Number(visit.visit) === 1
    ? "NO_ORDER_YET__VRB_DISCOVERY_NOT_COMPLETE"
    : Number(visit.visit) === 2
      ? "STRICT_ASK_68_CREDITS_RESTING_69_BEFORE_REPRICE"
      : "VRB_ALREADY_FILLED_69__ENTRY_PHASE_LOCKED",
  english: Number(visit.visit) === 1
    ? "The ask reached 68 before VRB had a verified discovery call, so the OS had no lawful order to hold or move."
    : Number(visit.visit) === 2
      ? "The 69 riser bid was already resting. Ask 68 was strictly through it, so fill accounting signed 69 before the resting manager could cancel."
      : "VRB was already filled at 69. The repeated ask-68 pulse updated shape memory but could not trigger another entry.",
}));

const material = tuned.material_decisions.map((row, i) => ({
  decision_number: i + 1,
  timestamp_et: row.timestamp_et,
  tminus_scheduled: row.tminus_scheduled,
  tminus_bell: row.tminus_bell,
  joint_observation: row.joint_observation,
  shapes: row.shapes,
  organ: row.organ,
  organ_returns: row.organ_returns || null,
  door_opened: row.door_opened,
  signer: row.signer,
  action: row.action,
  declined: row.declined,
  code_path: row.code_path,
  english: row.english,
}));

const decision = (action) => {
  const row = tuned.decision_ledger.find((candidate) => candidate.action === action);
  if (!row) throw new Error(`missing decision ${action}`);
  return row;
};
const clockDecision = (row) => ({
  sequence: Number(row.sequence),
  timestamp_et: row.timestamp_et,
  tminus_scheduled: row.tminus_scheduled,
  tminus_bell: row.tminus_actual_bell,
});
const firstBothBooks = tuned.decision_ledger.find((row) => row.action === "NO_ORDER__NO_VERIFIED_LAST_TRADE");
const placeNIK26 = decision("PLACE_NIK_26");
const placeNIK23 = decision("REPRICE_NIK_23");
const placeVRB69 = decision("PLACE_VRB_69");
const fillVRB69 = decision("CREDIT_VRB_FILL_69");
const placeNIK21 = decision("REPRICE_NIK_21");
const cancelNIK21 = decision("CANCEL_NIK_21__WAIT");
const placeNIK19 = decision("PLACE_NIK_19");
const fillNIK19 = decision("CREDIT_NIK_FILL_19");
const ask18Ledger = tuned.decision_ledger.find((row) => row.sequence === Number(firstAsk18.sequence));
const bellLedger = tuned.decision_ledger.find((row) => row.trigger === "ACTUAL_BELL");
if (!firstBothBooks || !ask18Ledger || !bellLedger) throw new Error("missing per-leg trace boundary point");

const quoteTransitions = {
  NIK: buildQuoteTransitions(rawClock, "NIK"),
  VRB: buildQuoteTransitions(rawClock, "VRB"),
};
const withEvidence = (leg, point, leadCount = 8) => {
  const sibling = leg === "NIK" ? "VRB" : "NIK";
  const ownLead = quoteLeadIn(quoteTransitions[leg], point, leadCount);
  const siblingLead = quoteLeadIn(quoteTransitions[sibling], point, Math.min(leadCount, 6));
  const ownPrints = recentPrints(rawClock, leg, point);
  const siblingPrints = recentPrints(rawClock, sibling, point);
  if (ownLead.length) ownLead[ownLead.length - 1].latest_verified_print_at_decision = ownPrints.length ? ownPrints[ownPrints.length - 1] : null;
  if (siblingLead.length) siblingLead[siblingLead.length - 1].latest_verified_print_at_decision = siblingPrints.length ? siblingPrints[siblingPrints.length - 1] : null;
  return {
    sequence: point.sequence,
    timestamp_et: point.timestamp_et,
    tminus_scheduled: point.tminus_scheduled,
    tminus_bell: point.tminus_bell,
    own_quote_lead_in: ownLead,
    sibling_quote_lead_in: siblingLead,
    own_recent_true_prints: ownPrints,
    sibling_recent_true_prints: siblingPrints,
  };
};
const atlasFaller = trace.consultations.filter((call) => call.leg === "NIK")
  .map((call) => ({
    time_et: call.time_et,
    page: call.atlas.page,
    population: call.atlas.n,
    depth_p25_p50_p75: call.atlas.depth_p25_p50_p75,
    anchor_source: call.anchor.source,
    anchor_price: call.anchor.price,
    atlas_p50_aim: call.atlas.aim,
    replay_faller_p75_target: call.anchor.price - call.atlas.depth_p25_p50_p75[2],
  }));
const recurrenceAtArm = pulseRecurrenceBreakdown(rawClock, "VRB", cancelNIK21.sequence);
if (recurrenceAtArm.total !== cancelNIK21.organ_returns.sibling_completed_quote_recurrences) {
  throw new Error(`recurrence decomposition mismatch ${JSON.stringify(recurrenceAtArm)}`);
}

const perLegTrace = {
  schema_version: "NIKVRB_PER_LEG_CAUSAL_TRACE_V1",
  event: trace.event,
  clock_scope: {
    first_market_sequence: 2,
    first_both_books_sequence: firstBothBooks.sequence,
    bell_sequence: bellLedger.sequence,
    market_receipts: marketReceiptCount,
    complete_receipt_ledger: ".claude/window1_live_v4_replay/nikvrb_sibling_shape_tune_20260731/NIKVRB_T375_TO_BELL_DECISION_TRACE.jsonl.gz.b64",
  },
  honesty_fences: {
    atlas_depth: "historical ATLAS price-dip quantile; not displayed queue depth or top-five depth",
    faller_p75: "the one-game replay candidate selects ATLAS p75 after orientation calls the leg a faller; this is candidate code, not the production ATLAS p50 signer",
    recurrence_threshold: "the arm rule requires total recurrences > 0; 97 is the observed accumulated count, not a calibrated threshold",
    five_cent_cell: "CELL_WIDTH_CENTS=5 is transplanted from live_v4 V4_REPRICE_MOVE_CENTS, a resting-repost deadband; it is not a learned faller cell lattice",
    cancel_choice: "the arm transition closes the NIK order before evaluating HOLD or improvement; cancel/wait is imposed by this replay branch and is not proven as the unique OS consequence of the recurrence evidence",
    ask18_choice: "after pair completion the entry gate computes no alternative price; pair basis 69+18=87 is hindsight only",
    normalized_last: "the clock's normalized last column can lag the latest receipt-identified print; both values are retained and only the receipt-backed value is described as verified",
  },
  atlas_faller_calls: atlasFaller,
  recurrence_at_patience_arm: recurrenceAtArm,
  VRB: [
    {
      id: "VRB_DISCOVERY_WAIT",
      ...withEvidence("VRB", firstBothBooks, 4),
      organ: "DISCOVERY_GATE",
      return: "NO_CALL: no receipt-identified VRB true print",
      prediction: "none; the riser/faller path is not yet price-authoritative for VRB",
      action: "no VRB order",
      declined: "BBO-only price conception",
      code_path: "ColdReplay.process:firstDualBook",
    },
    {
      id: "VRB_ROLE_BECOMES_VISIBLE_FROM_NIK_DISCOVERY",
      ...withEvidence("VRB", placeNIK26, 4),
      organ: "orientation inside INITIAL_ENTRY_TREE",
      return: "VRB riser, conviction 1.0, voices cohort + anchor_role",
      prediction: "VRB is the near-now climbing leg; pulses are expected before T2 while NIK is the inverse faller",
      action: "role opened, but no VRB target because VRB still lacks its own true-print anchor",
      declined: "no cross-leg substitution for a missing VRB anchor",
      code_path: "buildConsultations -> ColdReplay.process:consultation",
    },
    {
      id: "VRB_PLACE_69",
      ...withEvidence("VRB", placeVRB69, 16),
      organ: "ORIENTATION_RISER_NEAR_NOW",
      return: "current external bid 69",
      prediction: "the fresh 70 print and 69/70 book make the shallow riser retouch executable now, before T2",
      price_math: "riser branch target = current bid = 69; ATLAS p50 alternative = 70 - 3 = 67",
      action: "place five at 69",
      declined: "ATLAS 67",
      code_path: "buildConsultations:146-148 -> ColdReplay._place",
    },
    {
      id: "VRB_FILL_69",
      ...withEvidence("VRB", fillVRB69, 16),
      organ: "FILL_ACCOUNTING",
      return: "STRICT_ASK_CERTAIN_FILL because external ask 68 < exposed 69",
      prediction: "none; this is execution evidence, not a shape forecast",
      price_math: "credit original exposed X=69; do not move it to the new 67 bid",
      action: "credit five at 69",
      declined: "maker-safety cancel/reprice before fill credit",
      code_path: "ColdReplay._fillEvidence:252-261 -> ColdReplay._fill",
    },
    {
      id: "VRB_POST_FILL_LOCK_THROUGH_BELL",
      ...withEvidence("VRB", bellLedger, 6),
      organ: "FILLED_PHASE_GATE / PAIR_ENTRY_COMPLETE after NIK fill",
      return: "entry ineligible on every later receipt",
      prediction: "market state remains readable; no second VRB entry is permitted",
      action: "no re-buy through observed bell",
      declined: "all later VRB consultations and quote-pulse entries",
      code_path: "ColdReplay.process:legFilledLock -> ColdReplay.process:pairCompleteLock",
    },
  ],
  NIK: [
    {
      id: "NIK_DISCOVERY_WAIT",
      ...withEvidence("NIK", firstBothBooks, 4),
      organ: "DISCOVERY_GATE",
      return: "NO_CALL: no receipt-identified true print",
      prediction: "none",
      action: "no NIK order",
      declined: "BBO-only conception",
      code_path: "ColdReplay.process:firstDualBook",
    },
    {
      id: "NIK_PLACE_26",
      ...withEvidence("NIK", placeNIK26, 6),
      organ: "ORIENTATION_FALLER_DEEP",
      return: "VRB riser/NIK faller; ATLAS page ATP_CHALL|underdog|26_50 p75 depth 7",
      prediction: "NIK is the inverse faller; deeper reach is expected later than VRB's riser entry",
      price_math: "verified print anchor 33 - historical p75 dip 7 = 26; p50 alternative 33 - 4 = 29",
      action: "place five at 26",
      declined: "ATLAS p50 29",
      code_path: "buildConsultations:146-148 -> ColdReplay._place",
    },
    {
      id: "NIK_REPRICE_23",
      ...withEvidence("NIK", placeNIK23, 8),
      organ: "ORIENTATION_FALLER_DEEP",
      return: "same ATLAS page and same p75 depth 7; anchor changed",
      prediction: "faller remains a deeper-cast leg",
      price_math: "verified last 32 is above ask 30, so tight-mid anchor 30 - 7 = 23; the three-cent target move is entirely anchor 33 -> 30",
      action: "replace 26 with 23",
      declined: "ATLAS p50 26; later same-timestamp bid 23 was not used because it occurs after the decision row",
      code_path: "buildConsultations:146-148 -> ColdReplay._place",
    },
    {
      id: "NIK_REPRICE_21",
      ...withEvidence("NIK", placeNIK21, 12),
      organ: "ORIENTATION_FALLER_DEEP",
      return: "same ATLAS page p75 depth 7 with new verified print anchor 28",
      prediction: "inverse slide still has room; early table depth is not yet terminal",
      price_math: "verified print anchor 28 - p75 dip 7 = 21; 22 and 20 are not outputs of this frozen quantile row; p50 alternative is 24",
      action: "replace 23 with 21",
      declined: "ATLAS p50 24",
      code_path: "buildConsultations:146-148 -> ColdReplay._place",
    },
    {
      id: "NIK_CANCEL_21_AT_T2",
      ...withEvidence("NIK", cancelNIK21, 12),
      organ: "SIBLING_REALIZED_SHAPE",
      return: `first T2 receipt; VRB 73/74, four cents above fill; ${recurrenceAtArm.bid_recurrences} bid plus ${recurrenceAtArm.ask_recurrences} ask recurrences`,
      prediction: "VRB's riser path is treated as realized, so inverse NIK is expected to slide later inside T2",
      price_math: "none; 97 > 0 satisfies a boolean evidence-presence gate but does not calculate a price",
      action: "cancel 21 and wait without an order",
      declined: "holding 21; improving it; computing an alternative target",
      code_path: "ColdReplay.process:siblingShapePatienceArm:397-435",
    },
    {
      id: "NIK_PLACE_19",
      ...withEvidence("NIK", placeNIK19, 14),
      organ: "FALLER_PATIENCE_RELEASE",
      return: "arm bid 24 - current bid 19 = five-cent mechanical threshold; VRB bid 73 remains above fill 69",
      prediction: "the first full mechanical move ends patience; the current bid may receive a later retouch",
      price_math: "target = current NIK bid 19; 20 was only four below the arm bid and 18 was not yet observed",
      action: "place five at 19",
      declined: "ATLAS 21 and every unseen lower price",
      code_path: "ColdReplay.process:fallerPatienceRelease:437-466 -> ColdReplay._place",
    },
    {
      id: "NIK_FILL_19",
      ...withEvidence("NIK", fillNIK19, 10),
      organ: "FILL_ACCOUNTING",
      return: "PRICE_REACHED on strictly later positive-size public print 19",
      prediction: "none; execution fact closes the pair-entry path",
      price_math: "credit original exposed X=19",
      action: "credit five at 19",
      declined: "cancel/reprice before fill credit",
      code_path: "ColdReplay._fillEvidence:252-261 -> ColdReplay._fill",
    },
    {
      id: "NIK_ASK_18_DECLINED",
      ...withEvidence("NIK", ask18Ledger, 10),
      organ: "FILLED_PHASE_GATE",
      return: "PAIR_ENTRY_COMPLETE",
      prediction: "none; entry pricing is unreachable after both exact-five fills",
      price_math: "no alternative was calculated; 69+18=87 versus achieved 88 is an ex-post counterfactual only",
      action: "record 17/18 book and do not re-buy",
      declined: "all further Window-1 entry actions",
      code_path: "ColdReplay.process:pairCompleteLock:474-481",
    },
    {
      id: "NIK_LOCK_THROUGH_BELL",
      ...withEvidence("NIK", bellLedger, 6),
      organ: "FILLED_PHASE_GATE",
      return: "PAIR_ENTRY_COMPLETE",
      prediction: "none",
      action: "no re-buy through observed bell",
      declined: "all entry pricing",
      code_path: "ColdReplay.process:pairCompleteLock",
    },
  ],
};

const summary = {
  schema_version: "NIKVRB_SIBLING_SHAPE_COLD_REPLAY_V1",
  event: trace.event,
  scope: "one-event cold replay; score-free; no population inference; live_v4 unchanged",
  candidate: {
    name: "orientation_riser_plus_sibling_shape_faller_patience",
    orientation_riser: "existing orientation-conditioned live-bid branch",
    faller_patience_arm: "first lawful receipt inside existing T2 bucket when sibling riser remains above fill after at least one raw quote recurrence",
    faller_release: "current faller bid moves one existing five-cent price cell below its arm bid while sibling support remains intact",
    faller_price_authority: "current lawful non-crossed external best bid; no table and no future low",
  },
  current_outcome: {
    fills: current.fills,
    pair_complete: true,
    pair_cost_cents: current.fills.NIK.price + current.fills.VRB.price,
    individual_delta_to_close_cents: {
      NIK: current.fills.NIK.price - closes.NIK,
      VRB: current.fills.VRB.price - closes.VRB,
    },
    combined_delta_to_close_cents:
      current.fills.NIK.price - closes.NIK + current.fills.VRB.price - closes.VRB,
    gap_to_own_fillable_low_cents: {
      NIK: current.fills.NIK.price - fillableLows.NIK,
      VRB: current.fills.VRB.price - fillableLows.VRB,
    },
  },
  tuned_outcome: tunedOutcome,
  exact_acceptance: expected,
  fluidity: nondecisionSummary,
  vrb_ask_68_visits: visitDecisions,
  live_v4_modified: false,
  population_run: false,
};

function bookText(book) {
  return `${book.bid ?? "—"}/${book.ask ?? "—"}/${book.last ?? "—"}; spread ${book.spread ?? "—"}; dwell ${book.dwell_seconds ?? "—"}s; last ${book.last_trade_provenance.state}`;
}

function returnsText(row) {
  if (!row.organ_returns) return "none";
  return Object.entries(row.organ_returns)
    .map(([key, value]) => `${key}=${typeof value === "object" ? JSON.stringify(value) : value}`)
    .join("; ");
}

const materialRows = material.map((row) => `| ${row.decision_number} | ${cleanText(row.tminus_scheduled)} / ${cleanText(row.tminus_bell)} | NIK ${cleanText(bookText(row.joint_observation.NIK))}; VRB ${cleanText(bookText(row.joint_observation.VRB))} | ${cleanText(row.shapes.VRB)} / ${cleanText(row.shapes.NIK)} | ${cleanText(row.organ)} → ${cleanText(row.door_opened)} | ${cleanText(returnsText(row))} | ${cleanText(row.signer)} | ${cleanText(row.action)}; overwritten/declined ${cleanText(row.declined)} |`).join("\n");

const visitRows = visitDecisions.map((row) => `| ${row.visit} | ${row.tminus_scheduled} / ${row.tminus_bell} | ${row.book} | ${cleanText(row.english)} |`).join("\n");
const noDecisionRows = Object.entries(noDecisionCounts)
  .sort((a, b) => b[1] - a[1])
  .map(([action, count]) => `| ${action} | ${count.toLocaleString("en-US")} | ${action.includes("PATIENCE") ? "Sibling shape had armed patience; the local one-cell release had not fired." : action.includes("COMPLETE") ? "The credited fill locked entry while books and tape remained readable." : action.startsWith("HOLD_") ? "The existing resting order remained lawful and no named transition fired." : "No causal entry door was open."} |`)
  .join("\n");

const tracePoint = (leg, id) => {
  const point = perLegTrace[leg].find((candidate) => candidate.id === id);
  if (!point) throw new Error(`missing trace point ${leg}/${id}`);
  return point;
};
const vrbPlaceQuoteRows = quoteRows(tracePoint("VRB", "VRB_PLACE_69").own_quote_lead_in);
const vrbFillQuoteRows = quoteRows(tracePoint("VRB", "VRB_FILL_69").own_quote_lead_in);
const nik26QuoteRows = quoteRows(tracePoint("NIK", "NIK_PLACE_26").own_quote_lead_in);
const nik23QuoteRows = quoteRows(tracePoint("NIK", "NIK_REPRICE_23").own_quote_lead_in);
const nik21QuoteRows = quoteRows(tracePoint("NIK", "NIK_REPRICE_21").own_quote_lead_in);
const nikCancelQuoteRows = quoteRows(tracePoint("NIK", "NIK_CANCEL_21_AT_T2").own_quote_lead_in);
const nik19QuoteRows = quoteRows(tracePoint("NIK", "NIK_PLACE_19").own_quote_lead_in);
const nikFillQuoteRows = quoteRows(tracePoint("NIK", "NIK_FILL_19").own_quote_lead_in);
const nikAsk18QuoteRows = quoteRows(tracePoint("NIK", "NIK_ASK_18_DECLINED").own_quote_lead_in);
const consultation = (leg, time) => {
  const call = trace.consultations.find((candidate) => candidate.leg === leg && candidate.time_et === time);
  if (!call) throw new Error(`missing consultation ${leg}/${time}`);
  return call;
};
const organPanel = (call) => [
  `anchor ${call.anchor.source}=${call.anchor.price}`,
  `orientation ${call.orientation.riser} riser, conviction ${call.orientation.conviction}, voices ${(call.orientation.voices || []).join("+") || "none"}`,
  `cohort ${call.cohort.cell}, n=${call.cohort.n}, dip-p50=${call.cohort.dip_p50}, reach-3c=${call.cohort.reach_3c}, rose=${call.cohort.rose_pct}%`,
  `ATLAS ${call.atlas.page}, n=${call.atlas.n}, depth=${call.atlas.depth_p25_p50_p75.join("/")}, p50 aim=${call.atlas.aim}`,
  `contention ${call.contention.verdict} ${call.contention.best_pct}%`,
  `pair ${call.pair.verdict}, composed=${call.pair.combined_at_path}, synthetic sibling=${call.pair.sibling_estimate}`,
  `flow ${call.flow.bucket}, prints30m=${call.flow.prints_30m}, p-fill-1h=${call.flow.p_fill_1h}`,
  `FV ${call.external_fv.status}/${call.external_fv.reason}; Polymarket ${call.polymarket}; library ${call.library.verdict}`,
].join("; ");
const vrb69Panel = organPanel(consultation("VRB", "2026-07-19T07:13:58-04:00"));
const nik26Panel = organPanel(consultation("NIK", "2026-07-19T06:28:05-04:00"));
const nik23Panel = organPanel(consultation("NIK", "2026-07-19T07:07:33-04:00"));
const nik21Panel = organPanel(consultation("NIK", "2026-07-19T07:51:21-04:00"));

const report = `# NIK–VRB sibling-shape cold replay

## Result

The tune changes the faller at the joint-tree level, not by choosing a deeper table row. The current orientation-conditioned branch buys VRB at **69** and NIK at **21**: NIK is two cents above its own 19 close and three cents above its own 18 fillable low, so the pair's combined success depends on VRB carrying it. In the corrected branch VRB still rests **69** at T−316.033 scheduled / T−321.033 bell and is credited by strict ask 68 at T−314.633 / T−319.633. NIK rests 21 early, but at the first lawful receipt inside the existing T2 timing bucket the realized VRB pulse path cancels that exposure. NIK then waits unexposed until its own live bid falls one complete existing five-cent cell, from 24 to 19. The current bid signs 19 at T−109.050 / T−114.050; a strictly later public print at 19 credits it at T−80.651 / T−85.651.

The frozen close references are VRB 83 and NIK 19. Individual deltas are **−14** and **0**; combined delta is **−14**. Against each leg's own frozen fillable low, VRB 69 is one cent better than the print floor via strict ask and NIK 19 is one cent above its 18 low. The result no longer depends on one leg paying for a bad sibling entry. Any letter grade still depends on the separately declared N-cent tolerance; this replay does not invent it.

## The tune

1. Orientation still opens VRB's riser-near-now door and NIK's faller door.
2. At the first receipt inside the already-existing T2 bucket (60–120 minutes before schedule), the joint reader asks whether the riser is still above its fill and has completed a causal raw-quote recurrence. If yes, the riser shape is *realized*, and the inverse faller order is cancelled into patience.
3. Patience releases only when the faller's own live bid has moved one existing five-cent price cell below the arm bid while the sibling remains above its fill. The current external bid signs the price. No ATLAS depth and no future low participates.
4. The release receipt cannot fill its new order. Only a strictly later print or strict ask can credit it.

Implementation path: buildConsultations → ColdReplay.process:siblingShapePatienceArm → ColdReplay.process:fallerPatienceRelease → ColdReplay._fillEvidence → ColdReplay._fill in arb-executor/analysis/nikvrb_sibling_shape_cold_replay.js. Production live_v4.py is byte-identical to the parent and is not armed by this one-event tune.

## Read this before the trace

Three labels in the first report were too compressed:

- **ATLAS depth is not live book depth.** It is a historical price-dip distribution attached to page \`ATP_CHALL|underdog|26_50\`. On all three NIK calls the frozen row is \`[p25=2, p50=4, p75=7]\`, population 1,470. The replay's faller branch chooses p75 and computes \`anchor - 7\`. No displayed size or queue field produces 26, 23, or 21.
- **The 97 recurrences are observations, not a threshold.** They decompose into **${recurrenceAtArm.bid_recurrences} bid recurrences + ${recurrenceAtArm.ask_recurrences} ask recurrences** under the replay's local-trough counter. The code gate is merely \`recurrences > 0\`. The first receipt inside T2, not the 97th recurrence, fires the branch.
- **The five-cent cell is mechanical.** It is copied from production \`V4_REPRICE_MOVE_CENTS=5\`, where it is a resting-repost deadband. The tune repurposes that number as a faller-patience release. It is not a learned NIK cell lattice and it does not prove that five cents is economically optimal.

There is also a source distinction the compact table hid. The clock has a normalized \`last\` column and separately preserved true-print receipts. At T−119 the normalized NIK last says 28 while the newest proven print is 27; at T−109 it still says 28 while the newest proven print is 24. The tuned release does not use last trade, so the target is unaffected, but the trace reports the receipt-backed print as the authoritative last-trade fact and keeps the lagging normalized field visible.

## VRB alone, from appearance to bell

### T−375.450 / T−380.450: visible, but not priceable

Both books first coexist at 5/92. Neither leg has a receipt-identified print. \`DISCOVERY_GATE\` returns \`NO_ORDER__NO_VERIFIED_LAST_TRADE\`; BBO-only conception is unreachable. At NIK's first lawful consultation (T−361.917), orientation already names VRB the riser with conviction 1.0, but VRB still lacks its own anchor, so that call opens a *role* and not a VRB order.

### T−316.033 / T−321.033: VRB 69

Leading quote states (raw normalized last and the newest proven print are deliberately separate):

| Scheduled / bell | VRB bid/ask | Side changed | Held until next change or call | Raw last | Newest proven print |
|---|---:|---|---:|---:|---|
${vrbPlaceQuoteRows}

The useful local sequence is: 67/75; ask compresses 74, 76, 75, 73, 72, 71, 70, 69, then 68 while bid stays 67; ask snaps back to 75; later bid lifts 67→69 while ask compresses 73→72→71→70. That 69/70 state holds 21 seconds before the consultation. A true print at 70 arrives 1.821 seconds before the call.

**Every organ at the call:** ${vrb69Panel}.

The OS reads **VRB riser / climb with pulses expected before T2**. In this branch, the fresh 70 print plus the 69/70 book means the shallow retouch is actionable now. \`ORIENTATION_RISER_NEAR_NOW\` signs the live bid: \`X=69\`. ATLAS separately says \`70 - p50(3) = 67\`; the branch declines 67. Nothing in this call predicts an unseen future low.

### T−314.633 / T−319.633: ask 68 credits the resting 69

| Scheduled / bell | VRB bid/ask | Side changed | Held until next change or call | Raw last | Newest proven print |
|---|---:|---|---:|---:|---|
${vrbFillQuoteRows}

The immediate pre-fill book is 69/70. It has held **105 seconds from first appearance and 84 seconds since our order**. At 07:15:22 both sides step down together to 67/68: ask falls from 70 to 68 and bid falls from 69 to 67. Because 68 is strictly below the already exposed 69, \`_fillEvidence\` returns \`STRICT_ASK_CERTAIN_FILL\` and credits five at the original 69 before any maker-safety action can lower or cancel it.

After that, VRB's entry path is locked. The later frozen 07:15:43 consultation would have proposed current-bid 67 in this orientation branch (and ATLAS 65), but that exact consultation timestamp is absent from the 13,123-row dual clock, so the cold replay does not invent a row for it. Every receipt that is present takes \`legFilledLock\`, and after NIK fills it takes \`pairCompleteLock\`. Visits 3–9 to ask 68 therefore update pulse memory but cannot create a second VRB entry.

## NIK alone, from appearance to bell

### T−361.917 / T−366.917: NIK 26

| Scheduled / bell | NIK bid/ask | Side changed | Held until next change or call | Raw last | Newest proven print |
|---|---:|---|---:|---:|---|
${nik26QuoteRows}

The book jumps from 5/92 to 23/33 after 13 minutes 28 seconds. A one-contract true print at 33 follows 0.766 seconds later; the consultation is 3.234 seconds after that print. Orientation calls VRB the riser, making NIK the faller. The replay's faller child does not use displayed depth: it selects the ATLAS historical p75 dip of seven cents. Exact arithmetic is \`33 - 7 = 26\`. ATLAS p50 would be 29 and is explicitly declined. Thus 26 is a candidate-imposed p75 output, not a number inferred from the 23/33 queue.

**Every organ at the call:** ${nik26Panel}. Orientation opens the faller child; the replay p75 child signs. Cohort, contention, pair, flow, FV, Polymarket and library remain context and do not overwrite 26.

### T−322.450 / T−327.450: NIK 23

| Scheduled / bell | NIK bid/ask | Side changed | Held until next change or call | Raw last | Newest proven print |
|---|---:|---|---:|---:|---|
${nik23QuoteRows}

From the first call, bid rises 23→29 and ask falls 33→32. The 29/32 book then persists for roughly 36 minutes 37 seconds. At T−322.733 ask falls to 31 and holds 17 seconds; at the call it falls again to 30 while bid remains 29. The newest true print is 32, now outside the 29/30 book, so the anchor gate replaces the print with tight-mid 30. The ATLAS row does not change: p75 remains seven. Exact arithmetic is \`30 - 7 = 23\`. That is the whole three-cent order move: anchor 33→30, fixed depth seven. A later same-timestamp row shows bid 23, but its preserved sequence is after the decision and did not sign the target.

**Every organ at the call:** ${nik23Panel}. The only controlling numeric change is the anchor. Orientation keeps the same child open; the same p75 child overwrites 26 with 23. The p50 result 26 and all contextual voices are declined.

### T−278.650 / T−283.650: NIK 21

| Scheduled / bell | NIK bid/ask | Side changed | Held until next change or call | Raw last | Newest proven print |
|---|---:|---|---:|---:|---|
${nik21QuoteRows}

The book spends most of the next 43 minutes near 28/29. At T−278.667 it breaks rapidly through 24/29, 24/28, 23/28, 23/27 and 24/27 while a true print establishes 28. At the next preserved call the causal book is 24/27 and the verified anchor is 28. The same historical p75 seven signs \`28 - 7 = 21\`. It is 21 rather than 22 or 20 because the row exposes 2/4/7, and this branch chooses exactly the third number. P50 would sign 24. “Depth call” means this macro dip lookup; it does not mean the 24/27 book displayed seven contracts.

**Every organ at the call:** ${nik21Panel}. The branch again gives the p75 child the pen. ATLAS p50 says 24; contention says trade-at-path; the pair organ says composed 93 using a synthetic sibling 72; none of those numbers displaces 21 in this replay.

### T−119.350 / T−124.350: cancel 21

| Scheduled / bell | NIK bid/ask | Side changed | Held until next change or call | Raw last | Newest proven print |
|---|---:|---|---:|---:|---|
${nikCancelQuoteRows}

NIK 21 has rested for 9,558 seconds. The first receipt inside the existing T2 bucket sees NIK 24/29 and VRB 73/74. VRB's bid is four cents above its 69 fill. The raw quote tracker has completed ${recurrenceAtArm.total} local-trough recoveries since observation began (${recurrenceAtArm.bid_recurrences} bid, ${recurrenceAtArm.ask_recurrences} ask).

What *resolved* is the replay state flag, not a calibrated recurrence score: \`T2_OPEN && VRB_bid>69 && recurrence_count>0 && valid_NIK_book\`. The threshold is one recurrence; 97 is merely the accumulated value by the first T2 receipt. \`siblingShapePatienceArm\` then calls \`_closeOrder("NIK")\` unconditionally. It does **not** score continued support for 21, compare HOLD with WALK, or compute an improved target. That is why it cancels rather than holds or improves: this one-game tune made cancel/wait the only reachable child. The evidence supports “reconsider NIK”; it does not independently prove that cancellation is the uniquely correct response.

### T−109.050 / T−114.050: NIK 19

| Scheduled / bell | NIK bid/ask | Side changed | Held until next change or call | Raw last | Newest proven print |
|---|---:|---|---:|---:|---|
${nik19QuoteRows}

After cancellation, 40 receipts repeat \`HOLD_NO_ORDER__WAIT_FOR_FULL_CELL\`. NIK is 24/28 at T−117.133 (zero-cent bid drop), then 23/27 at T−109.800 (one cent). A burst of receipt-identified prints at 24 arrives around T−110. The newest proven last at release is 24 even though the normalized clock column still carries 28.

At the first 19/27 BBO, the release calculation is \`arm_bid 24 - live_bid 19 = 5\`, while VRB remains 73/77 above its fill. The price is 19 because the current bid signs after the first full mechanical threshold crossing. A bid of 20 would be only four cents down; 18 had not been observed. Later preserved rows in the same second bounce 19→20→19, then 21/20/21 and 22/23. They are strictly later than the action and do not rewrite it.

This “cell” does not have a multi-cell market taxonomy behind it. The code imports production's five-cent reprice deadband and treats one such move as release authority. That is the exact rule; it is also the unproven economic assumption in this tune.

### T−80.651 / T−85.651: print 19 fills NIK

| Scheduled / bell | NIK bid/ask | Side changed | Held until next change or call | Raw last | Newest proven print |
|---|---:|---|---:|---:|---|
${nikFillQuoteRows}

The 19 order rests 1,703.923 seconds. The book compresses from 25/29 through 23/24, 22/24, 20/24, 19/24 and 19/23. A strictly later positive-size public print at 19 then returns \`PRICE_REACHED\`; fill accounting credits the exposed 19. The trigger that created the order never fills it.

### T−57.483 / T−62.483: ask 18 is observed and declined

| Scheduled / bell | NIK bid/ask | Side changed | Held until next change or call | Raw last | Newest proven print |
|---|---:|---|---:|---:|---|
${nikAsk18QuoteRows}

The book has already shown 18/19 shortly after the fill; the first ask 18 arrives later when 17/19 becomes 17/18. The deciding rule is \`ColdReplay.process:pairCompleteLock\`: both exact-five entry fills exist, so every later Window-1 entry organ is unreachable. The OS does **not** believe that 18 is too expensive and does **not** compare it with 19. It calculates no alternative cost at all. Ex post, 69+18 would be 87 instead of the achieved 88, but that counterfactual was not decision-time evidence. From the 19 fill through the observed bell, 9,762 receipts repeat the same pair-complete refusal.

## Both legs on the same clock

## Every material decision, in order

The complete receipt-by-receipt English ledger is frozen as NIKVRB_DECISION_PROCESS_ENGLISH.jsonl.gz.b64. The exact requested T−375-through-bell slice is NIKVRB_T375_TO_BELL_DECISION_TRACE.jsonl.gz.b64: **13,122 rows, sequences 2–13,123**, including the two same-time appearance rows and the bell. Both are base64-wrapped deterministic gzip so repository LF normalization cannot corrupt them. Every row contains both books, spread, dwell, last-trade provenance, both shape calls, the organ, opened door, signer, action, declined action, and code path. The prose below summarizes state changes; the ledger is the exhaustive event-by-event record.

| # | Scheduled / bell | Joint observation (bid/ask/last) | Shape call: VRB / NIK | Organ and door | Organ returns | Price signer | Action and overwritten/declined action |
|---:|---|---|---|---|---|---|---|
${materialRows}

## What the shapes mean

- **VRB riser, climbing with pulses:** expect the useful VRB entry early, before T2. A divot is a recurrence opportunity, not evidence that the path has reversed.
- **NIK inverse faller:** while VRB keeps resolving upward, NIK's early depth is not terminal. The useful NIK move is expected after the T2 door opens, so an early table-generated bid loses authority when the sibling shape becomes realized.
- **Late faller impulse:** one full live price-cell move on NIK, with VRB still above its fill, changes “wait” into “rest at the current bid.” It predicts a retouch/print at the new live level; it does not predict an unseen 18.

## VRB's nine ask-68 visits

| Visit | Scheduled / bell | VRB book | Tuned decision in English |
|---:|---|---|---|
${visitRows}

The pre-orientation OS cancelled 67 on visit 2, reconceived 65, then repeated quiet-staircase HOLD. Both the current orientation branch and this tuned branch instead let fill accounting consume ask 68 against the already-resting 69 before the resting manager runs. Visits 3–9 are therefore shape observations, not entry decisions.

## NIK's late slide and the non-decisions

At T−119.350 / T−124.350, the joint-shape organ cancels 21 and deliberately has no NIK order. From there, every receipt asks the same causal question: has NIK's **live bid** moved a full five-cent cell from 24 while VRB remains above 69? Until the answer is yes, the result is a named patience HOLD with no order.

At T−109.050 / T−114.050, NIK's bid first reaches 19 while the ask is 27 and VRB is 73/77. The full cell has arrived. The live bid signs 19. The order rests for 1,703.923 seconds. At T−80.651 / T−85.651, a positive-size public print at 19 fills it. When ask later reaches 18 at ${nondecisionSummary.first_NIK_ask_18.tminus_scheduled} / ${nondecisionSummary.first_NIK_ask_18.tminus_bell}, the OS sees both entries as complete; it records the lower book but declines a fourth entry or re-buy without calculating an alternative entry cost.

| Repeated decision | Receipts | English reason |
|---|---:|---|
${noDecisionRows}

## How fluid the process is

The cold clock contains **${rawClock.length.toLocaleString("en-US")}** ordered rows, of which **${marketReceiptCount.toLocaleString("en-US")}** are BBO or true-print receipts. Each receipt refreshes the joint observation and reaches a named gate, but only **${tuned.material_decisions.length}** state-changing decisions occur. Reconsideration is therefore frequent; authority changes are sparse.

The chain unlocks only on: a lawful discovery consultation, strict fill evidence, entry into the existing T2 timing bucket with a resolved sibling shape, a full live price-cell move on the faller, or the Window-1 boundary. It locks at three places: missing discovery evidence, a resting-order HOLD without a named trigger, and the filled-phase gate. The important repair is that the T2 sibling-shape transition now sits *before* the filled-phase lock on NIK; 21 is cancelled while entry is still reachable.

## Scope fence

This is a cold, one-event, score-free replay against frozen July 19 chronology. It reads no future row at a decision, runs no 804-event population, changes no production candidate, and does not modify or execute live_v4.py. The full ledger makes the silences explicit rather than treating absence of an action as absence of a decision.
`;

const outputMap = new Map();
function addOutput(relative, bytes) {
  outputMap.set(relative, Buffer.isBuffer(bytes) ? bytes : Buffer.from(bytes));
}

addOutput("NIKVRB_REPLAY_SUMMARY.json", canonical(summary));
addOutput("NIKVRB_MATERIAL_DECISIONS.json", canonical(material));
addOutput("NIKVRB_PER_LEG_CAUSAL_TRACE.json", canonical(perLegTrace));
addOutput("NIKVRB_NONDECISION_CENSUS.json", canonical(nondecisionSummary));
addOutput("NIKVRB_VRB_ASK68_TUNED_DECISIONS.json", canonical(visitDecisions));
addOutput("NIKVRB_CURRENT_ORDER_INTERVALS.json", canonical(current.order_intervals));
addOutput("NIKVRB_TUNED_ORDER_INTERVALS.json", canonical(tuned.order_intervals));
addOutput("NIKVRB_VISUAL_ACCEPTANCE.json", canonical(visualAcceptance));
addOutput("NIKVRB_DECISION_PROCESS_ENGLISH.jsonl.gz.b64", gzipJsonlBase64(tuned.decision_ledger));
addOutput("NIKVRB_T375_TO_BELL_DECISION_TRACE.jsonl.gz.b64", gzipJsonlBase64(
  tuned.decision_ledger.filter((row) => row.sequence >= 2)
));
addOutput("SOURCE_HASH_MANIFEST.json", canonical({ schema_version: "NIKVRB_SIBLING_SHAPE_SOURCE_MANIFEST_V1", sources: sourceManifest }));
addOutput("FORBIDDEN_ACCESS_RECEIPT.json", canonical({
  schema_version: "NIKVRB_SIBLING_SHAPE_FORBIDDEN_ACCESS_V1",
  population_run: false,
  scorer_imported_or_invoked: false,
  live_v4_imported_or_invoked: false,
  live_network_order_position_exit_settlement_access: false,
  holdout_access: false,
  production_file_modified: false,
}));
addOutput("../../../arb-executor/docs/research/window1/NIKVRB_SIBLING_SHAPE_REPLAY.md", report);

const artifactRows = [...outputMap.entries()].map(([relative, bytes]) => ({
  path: relative.startsWith("../") ? "arb-executor/docs/research/window1/NIKVRB_SIBLING_SHAPE_REPLAY.md" : `.claude/window1_live_v4_replay/nikvrb_sibling_shape_tune_20260731/${relative}`,
  bytes: bytes.length,
  sha256: sha256(bytes),
})).sort((a, b) => a.path.localeCompare(b.path));
addOutput("ARTIFACT_HASH_MANIFEST.json", canonical({ schema_version: "NIKVRB_SIBLING_SHAPE_ARTIFACT_MANIFEST_V1", artifacts: artifactRows }));
addOutput("DETERMINISTIC_REGENERATION_RECEIPT.json", canonical({
  schema_version: "NIKVRB_SIBLING_SHAPE_DETERMINISM_V1",
  command: "node arb-executor/analysis/build_nikvrb_sibling_shape_reference.js . --check",
  canonical_json: "JSON.stringify(value, null, 2) plus LF",
  gzip: "level=9, mtime=0; base64 text wrapper protects compressed bytes from repository LF normalization",
  source_rows: rawClock.length,
  ledger_rows: tuned.decision_ledger.length,
  t375_to_bell_ledger_rows: tuned.decision_ledger.filter((row) => row.sequence >= 2).length,
  output_hashes: artifactRows,
}));

for (const [relative, bytes] of outputMap.entries()) {
  const target = relative.startsWith("../") ? path.join(outDir, relative) : path.join(outDir, relative);
  if (checkOnly) {
    const existing = fs.readFileSync(target);
    if (!existing.equals(bytes)) throw new Error(`determinism mismatch ${target}`);
  } else {
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, bytes);
  }
}

const result = {
  status: checkOnly ? "CHECK_PASS" : "BUILT",
  event: trace.event,
  source_rows: rawClock.length,
  ledger_rows: tuned.decision_ledger.length,
  material_decisions: tuned.material_decisions.length,
  current: { NIK: current.fills.NIK && current.fills.NIK.price, VRB: current.fills.VRB && current.fills.VRB.price },
  tuned: { NIK: tuned.fills.NIK.price, VRB: tuned.fills.VRB.price, combined_delta: tunedOutcome.combined_delta_to_close_cents },
  patience: tuned.patience,
  population_run: false,
  live_v4_modified: false,
};
process.stdout.write(canonical(result));
