"use strict";

// Stateful structural port of the survivor_shapes organ at 189eaa20.
// The fitted V13/V18/V19 libraries are consumed from their pinned Git objects.
// Unlike the retired replay, this port never uses a right-edge progress bin.
// F-VS-139/143 rebind the runtime criterion to the objective axis: the causal
// traded-low path and each fitted shape's member-backed traded-low depth bins.
// Ask reachability remains executable-book evidence; it cannot define a floor.

const SOURCE_COMMIT = "189eaa20";
const MODULES = Object.freeze({
  single: "window1_interim_elimination_v13",
  pair: "window1_pair_interim_elimination_v18",
  couple: "window1_pair_couple_elimination_v19",
});
const TRADED_LOW_AXIS = "POST_FORMATION_TRUE_TRADE_LOW_CENTS";
let libraries = null;

function configureSurvivorShapeLibraries(binding) {
  if (!binding || binding.source_commit !== SOURCE_COMMIT) throw new Error("SURVIVOR_SHAPE_SOURCE_COMMIT_MISMATCH");
  if (!binding.pair?.groups || !binding.pair?.pair_hypothesis_groups || !binding.couple?.pair_couple_groups) throw new Error("SURVIVOR_SHAPE_LIBRARY_INCOMPLETE");
  if (!binding.sha256?.pair || !binding.sha256?.couple || !binding.sha256?.traded_low_support) throw new Error("SURVIVOR_SHAPE_LIBRARY_HASH_MISSING");
  const shapes = Object.values(binding.pair.groups).flatMap((group) => group.shapes ?? []);
  if (shapes.some((shape) => !shape.traded_low_support || !Array.isArray(shape.traded_low_support.depth_bins_cents))) {
    throw new Error("SURVIVOR_SHAPE_TRADED_LOW_SUPPORT_MISSING");
  }
  libraries = binding;
}

function cent(value) { return Number.isInteger(value) && value >= 1 && value <= 99 ? value : null; }
function finite(value) { return Number.isFinite(value) ? value : null; }
function region(price) { return price <= 25 ? "le25" : price <= 50 ? "26_50" : price <= 75 ? "51_75" : "ge76"; }
function macroState(prefix) {
  if (!prefix) return "UNAVAILABLE";
  if (prefix.trade_net === 0 && prefix.trade_drawdown_from_peak === 0) return "ANCHOR_OR_UNMOVED";
  if (prefix.trade_net > 0 && prefix.trade_drawdown_from_peak === 0) return "AT_RISING_PEAK";
  if (prefix.trade_net > 0) return "PULLBACK_ABOVE_ANCHOR";
  if (prefix.trade_net === 0) return "RETURNED_TO_ANCHOR_FROM_PEAK";
  if (prefix.trade_net === prefix.trade_dip) return "AT_DESCENDING_LOW";
  return "REBOUND_BELOW_ANCHOR";
}

function matchingSingleBins(shape, row) {
  if (!Number.isInteger(row?.observed_traded_low_depth_cents)) return [...(shape.traded_low_support?.depth_bins_cents ?? [])];
  // A final traded low cannot be shallower than a low already printed. Exact
  // member-backed depth bins at or beyond the observed depth remain possible.
  return (shape.traded_low_support?.depth_bins_cents ?? []).filter((depth) => depth >= row.observed_traded_low_depth_cents);
}

function causalTradePrefix(leg) {
  const anchor = cent(leg.anchor_cents);
  const rows = leg.prints.filter((row) => cent(row.price_cents) && (!Number.isFinite(leg.formation_end_epoch) || row.timestamp_epoch >= leg.formation_end_epoch));
  if (!anchor || !rows.length) return { rows: rows.length, anchor_cents: anchor, current: rows.at(-1) ?? null, prefix: null };
  const current = rows.at(-1);
  const low = Math.min(...rows.map((row) => row.price_cents));
  const high = Math.max(...rows.map((row) => row.price_cents));
  return {
    rows: rows.length,
    anchor_cents: anchor,
    current,
    prefix: {
      trade_net: current.price_cents - anchor,
      trade_dip: low - anchor,
      trade_peak: high - anchor,
      trade_drawdown_from_peak: high - current.price_cents,
      observed_traded_low_cents: low,
      observed_traded_low_depth_cents: anchor - low,
    },
  };
}

function rowForLeg(state, reads, legId) {
  const leg = state.legs[legId];
  const tradePath = causalTradePrefix(leg);
  const book = reads.books.value[legId];
  const anchor = cent(leg.anchor_cents);
  return {
    leg_id: legId,
    price_region: anchor ? region(anchor) : null,
    anchor_cents: anchor,
    observed_traded_low_cents: tradePath.prefix?.observed_traded_low_cents ?? null,
    observed_traded_low_depth_cents: tradePath.prefix?.observed_traded_low_depth_cents ?? null,
    latest_trade_cents: cent(tradePath.current?.price_cents),
    latest_trade_receipt: tradePath.current?.receipt ?? null,
    ask: cent(book?.ask_cents),
    bid: cent(book?.bid_cents),
    spread: cent(book?.ask_cents) && cent(book?.bid_cents) ? book.ask_cents - book.bid_cents : null,
    top_ask_size: finite(book?.ask_1_sz),
    top5_ask_depth: finite(book?.ask_depth_5),
    receipt: book?.receipt ?? state.receipt,
    prefix: tradePath.prefix,
    prefix_provenance: {
      structural_source: `${SOURCE_COMMIT}:V13/V18/V19 member identities and ordinal families`,
      runtime_axis: TRADED_LOW_AXIS,
      target_axis: TRADED_LOW_AXIS,
      ask_reachability_role: "EXECUTABLE_BOOK_INFORMATION_ONLY_NEVER_FLOOR_DEFINITION",
      formation_rule: "POST_CAUSAL_FORMATION_TRUE_PRINTS_ONLY",
    },
  };
}

function signablePairTuples(hypotheses, highShapes, lowShapes) {
  const high = new Set(highShapes), low = new Set(lowShapes), tuples = new Map();
  for (const hypothesis of hypotheses) for (const pair of hypothesis.member_single_shape_pairs ?? []) {
    if (!high.has(pair.high_shape_id) || !low.has(pair.low_shape_id)) continue;
    const key = `${pair.high_shape_id}|${pair.low_shape_id}`;
    const prior = tuples.get(key) ?? { high_shape_id: pair.high_shape_id, low_shape_id: pair.low_shape_id, n: 0, pair_hypothesis_ids: [] };
    prior.n += pair.n;
    if (!prior.pair_hypothesis_ids.includes(hypothesis.pair_hypothesis_id)) prior.pair_hypothesis_ids.push(hypothesis.pair_hypothesis_id);
    tuples.set(key, prior);
  }
  return [...tuples.values()];
}

function applyPairInterim(group, highShapes, lowShapes, highRow, lowRow) {
  if (!group) return { status: "PAIR_SOURCE_UNAVAILABLE_ABSTAIN", high_shapes: highShapes, low_shapes: lowShapes, hypotheses: [], tuples: [] };
  // The retired synchronized envelopes were fitted on ask paths. They are not
  // lawful runtime evidence after the traded-low-axis ruling. Pair hypotheses
  // may still narrow by their fitted component-shape tuples once each component
  // survived its own traded-low support test; the ask bins are not consulted.
  const hypotheses = group.hypotheses.filter((hypothesis) => hypothesis.usable_for_signing);
  const tuples = signablePairTuples(hypotheses, highShapes, lowShapes);
  if (!tuples.length) return { status: "PAIR_INTERIM_ABSTAINS_NO_SIGNABLE_CURRENT_SUPPORT", high_shapes: highShapes, low_shapes: lowShapes, hypotheses: [], tuples: [] };
  const allowedHigh = new Set(tuples.map((row) => row.high_shape_id));
  const allowedLow = new Set(tuples.map((row) => row.low_shape_id));
  const narrowedHigh = highShapes.filter((id) => allowedHigh.has(id));
  const narrowedLow = lowShapes.filter((id) => allowedLow.has(id));
  if (!narrowedHigh.length || !narrowedLow.length) return { status: "PAIR_INTERIM_CONTRADICTION_ABSTAINS", high_shapes: highShapes, low_shapes: lowShapes, hypotheses: [], tuples: [] };
  return { status: "PAIR_COMPONENT_TRADED_LOW_SUPPORT_MUTUALLY_NARROWED", high_shapes: narrowedHigh, low_shapes: narrowedLow, hypotheses, tuples };
}

function applyPairCouples(group, highShapes, lowShapes) {
  if (!group) return { status: "PAIR_COUPLE_SOURCE_UNAVAILABLE_ABSTAIN", high_shapes: highShapes, low_shapes: lowShapes, couples: [] };
  const high = new Set(highShapes), low = new Set(lowShapes);
  const couples = group.couples.filter((row) => row.usable_for_signing && high.has(row.high_shape_id) && low.has(row.low_shape_id));
  if (!couples.length) return { status: "NO_SIGNABLE_PAIR_COUPLE_ABSTAIN", high_shapes: highShapes, low_shapes: lowShapes, couples: [] };
  const allowedHigh = new Set(couples.map((row) => row.high_shape_id));
  const allowedLow = new Set(couples.map((row) => row.low_shape_id));
  return {
    status: "SIGNABLE_PAIR_COUPLES_NARROWED_BOTH_LEG_SETS",
    high_shapes: highShapes.filter((id) => allowedHigh.has(id)),
    low_shapes: lowShapes.filter((id) => allowedLow.has(id)),
    couples,
  };
}

function eliminationRecord(shapeId, module, receipt, evidence, matchedBins = []) {
  const overturn = module === MODULES.single
    ? "REINSTATE_ONLY_IF_THE_TRUE_TRADE_LEDGER_OR_MEMBER_DEPTH_BINDING_IS_CORRECTED_SO_THIS_SHAPE_HAS_A_REMAINING_EXACT_TRADED_LOW_DEPTH_BIN"
    : module === MODULES.pair
      ? "REINSTATE_WHEN_A_SIGNABLE_SYNCHRONIZED_PAIR_HYPOTHESIS_SUPPORTS_THIS_SHAPE_ON_A_LATER_RECEIPT"
      : "REINSTATE_WHEN_A_SIGNABLE_HIERARCHICAL_PAIR_COUPLE_SUPPORTS_THIS_SHAPE_ON_A_LATER_RECEIPT";
  return { shape_id: shapeId, eliminated_by: module, eliminated_at_receipt: receipt, evidence, matched_bins: matchedBins, overturn_test: overturn, last_rechecked_receipt: receipt };
}

function targetCriterion(group, shapeIds, row) {
  const shapeById = new Map((group?.shapes ?? []).map((shape) => [shape.shape_id, shape]));
  const counts = new Map();
  const shapeSupports = [];
  for (const shapeId of shapeIds) {
    const support = shapeById.get(shapeId)?.traded_low_support;
    if (!support) continue;
    const remaining = (support.depth_bins_cents ?? []).filter((depth) => !Number.isInteger(row.observed_traded_low_depth_cents) || depth >= row.observed_traded_low_depth_cents);
    shapeSupports.push({ shape_id: shapeId, support_n: support.support_n, depth_bins_cents: support.depth_bins_cents, remaining_depth_bins_cents: remaining, min_depth_cents: support.min_depth_cents, max_depth_cents: support.max_depth_cents });
    for (const depth of remaining) counts.set(depth, (counts.get(depth) ?? 0) + (support.depth_counts?.[String(depth)] ?? 0));
  }
  const depths = [...counts.keys()].sort((a, b) => a - b);
  const levels = depths.map((depth) => row.anchor_cents - depth).filter(cent).sort((a, b) => a - b);
  return {
    axis: TRADED_LOW_AXIS,
    anchor_cents: row.anchor_cents,
    observed_traded_low_cents: row.observed_traded_low_cents,
    observed_traded_low_depth_cents: row.observed_traded_low_depth_cents,
    candidate_final_depth_bins_cents: depths,
    candidate_final_floor_levels_cents: [...new Set(levels)],
    candidate_depth_counts: Object.fromEntries([...counts.entries()].map(([depth, n]) => [String(depth), n])),
    deepest_supported_floor_cents: levels.length ? Math.min(...levels) : null,
    shallowest_supported_floor_cents: levels.length ? Math.max(...levels) : null,
    signable: levels.length > 0,
    shape_supports: shapeSupports,
    ask_reachability_defines_target: false,
  };
}

function initialise(state, rows) {
  const legs = {};
  for (const [legId, row] of Object.entries(rows)) {
    const group = libraries.pair.groups[`${state.category}|${row.price_region}`];
    const all = group?.shapes?.map((shape) => shape.shape_id) ?? [];
    legs[legId] = { price_region: row.price_region, all_shape_ids: all, survivor_shapes: [...all], eliminated: {}, trajectory: [], prior_current_cents: null };
  }
  return { source_commit: SOURCE_COMMIT, modules: MODULES, legs, transitions: 0 };
}

function advanceSurvivorShapes({ state, reads }) {
  if (!libraries) throw new Error("SURVIVOR_SHAPE_LIBRARIES_NOT_CONFIGURED");
  const rows = Object.fromEntries(state.leg_ids.map((id) => [id, rowForLeg(state, reads, id)]));
  if (!state.dual_belief.survivor_shape_state) state.dual_belief.survivor_shape_state = initialise(state, rows);
  const shapeState = state.dual_belief.survivor_shape_state;
  const stages = {};
  for (const legId of state.leg_ids) {
    const legState = shapeState.legs[legId], row = rows[legId];
    if (!legState.all_shape_ids.length && row.price_region) {
      legState.price_region = row.price_region;
      const seedGroup = libraries.pair.groups[`${state.category}|${row.price_region}`];
      legState.all_shape_ids = seedGroup?.shapes?.map((shape) => shape.shape_id) ?? [];
      legState.survivor_shapes = [...legState.all_shape_ids];
    }
    const group = libraries.pair.groups[`${state.category}|${legState.price_region}`];
    const matches = new Map((group?.shapes ?? []).map((shape) => [shape.shape_id, matchingSingleBins(shape, row)]));
    const hasTradeEvidence = Number.isInteger(row.observed_traded_low_depth_cents);
    const compatible = legState.all_shape_ids.filter((id) => (matches.get(id) ?? []).length);
    const singleSurvivors = !hasTradeEvidence
      ? [...legState.survivor_shapes]
      : compatible.length
        ? compatible
        : [...legState.all_shape_ids];
    const singleStatus = !hasTradeEvidence
      ? "INSUFFICIENT_EVIDENCE_NO_POST_FORMATION_TRUE_TRADE_LOW"
      : compatible.length
        ? "EXACT_MEMBER_TRADED_LOW_DEPTH_BINS_NARROWED"
        : "INSUFFICIENT_EVIDENCE_OBSERVED_TRADED_LOW_OUTSIDE_LIBRARY_SUPPORT_REOPEN_FULL_SET";
    stages[legId] = { row, group, matches, before: [...legState.survivor_shapes], single: singleSurvivors, single_status: singleStatus };
  }
  const ordered = [...state.leg_ids].sort((a, b) => (state.legs[b].books[0]?.bid_cents ?? 0) - (state.legs[a].books[0]?.bid_cents ?? 0) || a.localeCompare(b));
  const [highId, lowId] = ordered;
  const pair = applyPairInterim(libraries.pair.pair_hypothesis_groups[state.category], stages[highId].single, stages[lowId].single, rows[highId], rows[lowId]);
  const couple = applyPairCouples(libraries.couple.pair_couple_groups[state.category], pair.high_shapes, pair.low_shapes);
  const finalByLeg = { [highId]: couple.high_shapes, [lowId]: couple.low_shapes };
  const updates = {};
  for (const legId of state.leg_ids) {
    const legState = shapeState.legs[legId], stage = stages[legId], after = finalByLeg[legId].length ? finalByLeg[legId] : stage.single;
    const beforeSet = new Set(stage.before), afterSet = new Set(after);
    const eliminatedNow = stage.before.filter((id) => !afterSet.has(id));
    const reinstatedNow = after.filter((id) => !beforeSet.has(id));
    for (const shapeId of legState.all_shape_ids) {
      if (afterSet.has(shapeId)) {
        if (legState.eliminated[shapeId]) legState.eliminated[shapeId].overturned_at_receipt = state.receipt;
        delete legState.eliminated[shapeId];
        continue;
      }
      const module = !stage.single.includes(shapeId) ? MODULES.single : !(legId === highId ? pair.high_shapes : pair.low_shapes).includes(shapeId) ? MODULES.pair : MODULES.couple;
      const evidence = {
        current_receipt: state.receipt,
        axis: TRADED_LOW_AXIS,
        current_reference_cents: stage.row.observed_traded_low_cents,
        macro_state: macroState(stage.row.prefix),
        prefix: stage.row.prefix,
        pair_status: pair.status,
        couple_status: couple.status,
      };
      const priorRecord = legState.eliminated[shapeId];
      legState.eliminated[shapeId] = priorRecord
        ? { ...priorRecord, latest_evidence: evidence, matched_bins: stage.matches.get(shapeId) ?? [], last_rechecked_receipt: state.receipt }
        : eliminationRecord(shapeId, module, state.receipt, evidence, stage.matches.get(shapeId) ?? []);
    }
    const current = stage.row.observed_traded_low_cents, prior = legState.prior_current_cents;
    const move = Number.isInteger(current) && Number.isInteger(prior) ? current - prior : null;
    const movement = {
      prior_cents: prior,
      current_cents: current,
      move_cents: move,
      material_two_cent_move: Number.isInteger(move) && Math.abs(move) >= 2,
      axis: TRADED_LOW_AXIS,
      effect: reinstatedNow.length ? "OVERTURNED_PRIOR_ELIMINATIONS_AND_REINSTATED_SHAPES" : eliminatedNow.length ? "ELIMINATED_SHAPES_WITH_NO_REMAINING_MEMBER_TRADED_LOW_DEPTH_BIN" : Number.isInteger(move) && Math.abs(move) >= 2 ? "CONFIRMED_OR_SHIFTED_ON_TRADED_LOW_AXIS_WITHOUT_SURVIVOR_CHANGE" : "TIGHTENED_OR_HELD_ON_TRADED_LOW_AXIS",
      eliminated_shape_ids: eliminatedNow,
      reinstated_shape_ids: reinstatedNow,
    };
    const signature = after.join("|");
    const priorSignature = legState.survivor_shapes.join("|");
    if (signature !== priorSignature || movement.material_two_cent_move) {
      legState.trajectory.push({ timestamp_epoch: state.current_epoch, receipt: state.receipt, before: stage.before, after, movement, modules: { single: stage.single_status, pair: pair.status, couple: couple.status }, overturn_tests_rechecked: Object.values(legState.eliminated).map((row) => ({ shape_id: row.shape_id, overturn_test: row.overturn_test, last_rechecked_receipt: state.receipt })) });
      shapeState.transitions += 1;
    }
    legState.survivor_shapes = [...after];
    legState.prior_current_cents = current;
    const criterion = targetCriterion(stage.group, after, stage.row);
    updates[legId] = {
      all_shape_ids: [...legState.all_shape_ids],
      survivor_shapes: [...after],
      eliminated_shape_ids: Object.keys(legState.eliminated).sort(),
      eliminations: Object.values(legState.eliminated).map((record) => ({ ...record, last_rechecked_receipt: state.receipt })),
      eliminated_now: eliminatedNow,
      reinstated_now: reinstatedNow,
      movement,
      trajectory_count: legState.trajectory.length,
      price_region: legState.price_region,
      modules: { single: stage.single_status, pair: pair.status, couple: couple.status },
      target_criterion: criterion,
      target_axis: TRADED_LOW_AXIS,
    };
  }
  return { source_commit: SOURCE_COMMIT, source_sha256: libraries.sha256, high_leg_id: highId, low_leg_id: lowId, pair_status: pair.status, couple_status: couple.status, legs: updates };
}

module.exports = { SOURCE_COMMIT, MODULES, TRADED_LOW_AXIS, configureSurvivorShapeLibraries, advanceSurvivorShapes, macroState, causalTradePrefix };
