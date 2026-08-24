"use strict";

// Stateful structural port of the survivor_shapes organ at 189eaa20.
// The fitted V13/V18/V19 libraries are consumed from their pinned Git objects.
// Unlike the retired replay, this port never uses a right-edge progress bin:
// a hypothesis survives when any of its fitted interim envelopes is compatible
// with the causal prefix visible at this receipt.

const SOURCE_COMMIT = "189eaa20";
const MODULES = Object.freeze({
  single: "window1_interim_elimination_v13",
  pair: "window1_pair_interim_elimination_v18",
  couple: "window1_pair_couple_elimination_v19",
});
const MACRO_KEYS = ["ask_net", "ask_dip", "ask_peak", "ask_drawdown_from_peak"];
const PAIR_MACRO_KEYS = [
  "high_ask_net", "high_ask_dip", "high_ask_peak", "high_ask_drawdown_from_peak",
  "low_ask_net", "low_ask_dip", "low_ask_peak", "low_ask_drawdown_from_peak",
  "ask_sum", "ask_net_sum",
];
const QUALIFIED_DWELL_SECONDS = 10;
const QUALIFIED_CAPACITY_CONTRACTS = 5;
let libraries = null;

function configureSurvivorShapeLibraries(binding) {
  if (!binding || binding.source_commit !== SOURCE_COMMIT) throw new Error("SURVIVOR_SHAPE_SOURCE_COMMIT_MISMATCH");
  if (!binding.pair?.groups || !binding.pair?.pair_hypothesis_groups || !binding.couple?.pair_couple_groups) throw new Error("SURVIVOR_SHAPE_LIBRARY_INCOMPLETE");
  if (!binding.sha256?.pair || !binding.sha256?.couple) throw new Error("SURVIVOR_SHAPE_LIBRARY_HASH_MISSING");
  libraries = binding;
}

function cent(value) { return Number.isInteger(value) && value >= 1 && value <= 99 ? value : null; }
function finite(value) { return Number.isFinite(value) ? value : null; }
function region(price) { return price <= 25 ? "le25" : price <= 50 ? "26_50" : price <= 75 ? "51_75" : "ge76"; }
function macroState(prefix) {
  if (!prefix) return "UNAVAILABLE";
  if (prefix.ask_net === 0 && prefix.ask_drawdown_from_peak === 0) return "ANCHOR_OR_UNMOVED";
  if (prefix.ask_net > 0 && prefix.ask_drawdown_from_peak === 0) return "AT_RISING_PEAK";
  if (prefix.ask_net > 0) return "PULLBACK_ABOVE_ANCHOR";
  if (prefix.ask_net === 0) return "RETURNED_TO_ANCHOR_FROM_PEAK";
  if (prefix.ask_net === prefix.ask_dip) return "AT_DESCENDING_LOW";
  return "REBOUND_BELOW_ANCHOR";
}

function matchesRange(value, range) {
  return Array.isArray(range) && Number.isFinite(value) && value >= range[0] && value <= range[1];
}

function matchingSingleBins(shape, row) {
  if (!row?.prefix) return [];
  return Object.entries(shape.interim_envelopes ?? {}).flatMap(([bin, envelope]) => {
    const stateMatches = (envelope.macro_states ?? []).includes(macroState(row.prefix));
    const rangesMatch = MACRO_KEYS.every((key) => matchesRange(row.prefix[key], envelope[key]));
    return stateMatches && rangesMatch ? [Number(bin)] : [];
  });
}

function causalAskPrefix(leg) {
  const books = leg.books.filter((row) => cent(row.bid_cents) && cent(row.ask_cents) && row.bid_cents <= row.ask_cents);
  const formedIndex = Number.isFinite(leg.formation_end_epoch)
    ? books.findIndex((row) => row.timestamp_epoch >= leg.formation_end_epoch)
    : books.findIndex((row) => row.ask_cents - row.bid_cents === 1);
  if (formedIndex < 0) return null;
  const rows = books.slice(formedIndex);
  const first = rows[0], current = rows.at(-1);
  let low = first.ask_cents, high = first.ask_cents, lastAsk = first.ask_cents, lastAskChange = first.timestamp_epoch;
  let episodeAsk = null, episodeStart = null, episodeRecorded = false, priorQualifiedAsk = null, qualifiedDescents = 0, qualifiedRises = 0;
  for (const row of rows) {
    if (episodeAsk === null || row.ask_cents !== episodeAsk) {
      episodeAsk = row.ask_cents;
      episodeStart = row.timestamp_epoch;
      episodeRecorded = false;
    }
    if (!episodeRecorded && row.timestamp_epoch - episodeStart >= QUALIFIED_DWELL_SECONDS && finite(row.ask_1_sz) >= QUALIFIED_CAPACITY_CONTRACTS) {
      if (priorQualifiedAsk !== null) {
        if (row.ask_cents < priorQualifiedAsk) qualifiedDescents += 1;
        else if (row.ask_cents > priorQualifiedAsk) qualifiedRises += 1;
      }
      priorQualifiedAsk = row.ask_cents;
      episodeRecorded = true;
    }
    if (row.ask_cents !== lastAsk) {
      lastAsk = row.ask_cents;
      lastAskChange = row.timestamp_epoch;
    }
    low = Math.min(low, row.ask_cents);
    high = Math.max(high, row.ask_cents);
  }
  return {
    rows: rows.length,
    first,
    current,
    ask_dwell_seconds: Math.max(0, current.timestamp_epoch - lastAskChange),
    prefix: {
      ask_net: current.ask_cents - first.ask_cents,
      ask_dip: low - first.ask_cents,
      ask_peak: high - first.ask_cents,
      ask_drawdown_from_peak: high - current.ask_cents,
      qualified_ask_descent_count: qualifiedDescents,
      qualified_ask_rise_count: qualifiedRises,
    },
  };
}

function rowForLeg(state, reads, legId) {
  const leg = state.legs[legId];
  const askPath = causalAskPrefix(leg);
  const book = askPath?.current ?? reads.books.value[legId];
  const current = cent(book?.ask_cents);
  const firstBid = cent(askPath?.first?.bid_cents) ?? cent(leg.anchor_cents);
  return {
    leg_id: legId,
    price_region: firstBid ? region(firstBid) : null,
    ask: current,
    spread: cent(book?.ask_cents) && cent(book?.bid_cents) ? book.ask_cents - book.bid_cents : null,
    top_ask_size: finite(book?.ask_1_sz),
    top5_ask_depth: finite(book?.ask_depth_5),
    ask_dwell_seconds: finite(askPath?.ask_dwell_seconds),
    receipt: book?.receipt ?? state.receipt,
    prefix: askPath?.prefix ?? null,
    prefix_provenance: {
      source: `${SOURCE_COMMIT}:build_window1_quote_shape_elimination_replay_v1.js::prefixRows`,
      first_book_rule: Number.isFinite(leg.formation_end_epoch) ? "FIRST_TWO_SIDED_BOOK_AT_OR_AFTER_CAUSAL_FORMATION_END" : "LEGACY_FIRST_SPREAD_EQUALS_ONE_FALLBACK",
      dwell_seconds: QUALIFIED_DWELL_SECONDS,
      capacity_contracts: QUALIFIED_CAPACITY_CONTRACTS,
      reference_series: "BEST_ASK_ONLY",
    },
  };
}

function pairFeatures(highRow, lowRow) {
  if (!highRow?.prefix || !lowRow?.prefix) return null;
  return {
    high_ask_net: highRow.prefix.ask_net,
    high_ask_dip: highRow.prefix.ask_dip,
    high_ask_peak: highRow.prefix.ask_peak,
    high_ask_drawdown_from_peak: highRow.prefix.ask_drawdown_from_peak,
    low_ask_net: lowRow.prefix.ask_net,
    low_ask_dip: lowRow.prefix.ask_dip,
    low_ask_peak: lowRow.prefix.ask_peak,
    low_ask_drawdown_from_peak: lowRow.prefix.ask_drawdown_from_peak,
    ask_sum: Number.isInteger(highRow.ask) && Number.isInteger(lowRow.ask) ? highRow.ask + lowRow.ask : null,
    ask_net_sum: Number.isFinite(highRow.prefix.ask_net) && Number.isFinite(lowRow.prefix.ask_net) ? highRow.prefix.ask_net + lowRow.prefix.ask_net : null,
  };
}

function matchingPairBins(hypothesis, highRow, lowRow) {
  const features = pairFeatures(highRow, lowRow);
  if (!features) return [];
  return (hypothesis.joint_interim_envelopes ?? []).flatMap((envelope, bin) => {
    const matches = PAIR_MACRO_KEYS.every((key) => matchesRange(features[key], envelope[key]));
    return matches ? [bin] : [];
  });
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
  const hypotheses = group.hypotheses.filter((hypothesis) => hypothesis.usable_for_signing && matchingPairBins(hypothesis, highRow, lowRow).length);
  const tuples = signablePairTuples(hypotheses, highShapes, lowShapes);
  if (!tuples.length) return { status: "PAIR_INTERIM_ABSTAINS_NO_SIGNABLE_CURRENT_SUPPORT", high_shapes: highShapes, low_shapes: lowShapes, hypotheses: [], tuples: [] };
  const allowedHigh = new Set(tuples.map((row) => row.high_shape_id));
  const allowedLow = new Set(tuples.map((row) => row.low_shape_id));
  const narrowedHigh = highShapes.filter((id) => allowedHigh.has(id));
  const narrowedLow = lowShapes.filter((id) => allowedLow.has(id));
  if (!narrowedHigh.length || !narrowedLow.length) return { status: "PAIR_INTERIM_CONTRADICTION_ABSTAINS", high_shapes: highShapes, low_shapes: lowShapes, hypotheses: [], tuples: [] };
  return { status: "PAIR_AND_SINGLE_LIBRARIES_MUTUALLY_NARROWED", high_shapes: narrowedHigh, low_shapes: narrowedLow, hypotheses, tuples };
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
    ? "REINSTATE_WHEN_THIS_SHAPE_MATCHES_ANY_FITTED_CAUSAL_INTERIM_ENVELOPE_ON_A_LATER_RECEIPT"
    : module === MODULES.pair
      ? "REINSTATE_WHEN_A_SIGNABLE_SYNCHRONIZED_PAIR_HYPOTHESIS_SUPPORTS_THIS_SHAPE_ON_A_LATER_RECEIPT"
      : "REINSTATE_WHEN_A_SIGNABLE_HIERARCHICAL_PAIR_COUPLE_SUPPORTS_THIS_SHAPE_ON_A_LATER_RECEIPT";
  return { shape_id: shapeId, eliminated_by: module, eliminated_at_receipt: receipt, evidence, matched_bins: matchedBins, overturn_test: overturn, last_rechecked_receipt: receipt };
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
    const compatible = legState.all_shape_ids.filter((id) => (matches.get(id) ?? []).length);
    const singleSurvivors = compatible.length ? compatible : [...legState.survivor_shapes];
    stages[legId] = { row, group, matches, before: [...legState.survivor_shapes], single: singleSurvivors, single_status: compatible.length ? "CAUSAL_INTERIM_ENVELOPES_NARROWED" : "INSUFFICIENT_EVIDENCE_SINGLE_MODULE_ABSTAINS" };
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
        current_reference_cents: stage.row.ask,
        macro_state: macroState(stage.row.prefix),
        prefix: stage.row.prefix,
        pair_status: pair.status,
        couple_status: couple.status,
      };
      legState.eliminated[shapeId] = eliminationRecord(shapeId, module, state.receipt, evidence, stage.matches.get(shapeId) ?? []);
    }
    const current = stage.row.ask, prior = legState.prior_current_cents;
    const move = Number.isInteger(current) && Number.isInteger(prior) ? current - prior : null;
    const movement = {
      prior_cents: prior,
      current_cents: current,
      move_cents: move,
      material_two_cent_move: Number.isInteger(move) && Math.abs(move) >= 2,
      effect: reinstatedNow.length ? "OVERTURNED_PRIOR_ELIMINATIONS_AND_REINSTATED_SHAPES" : eliminatedNow.length ? "ELIMINATED_SHAPES_INCONSISTENT_WITH_NEW_MOVEMENT" : Number.isInteger(move) && Math.abs(move) >= 2 ? "CONFIRMED_OR_SHIFTED_WITHOUT_SURVIVOR_CHANGE" : "TIGHTENED_OR_HELD_SUB_TWO_CENT_MOVE",
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
    };
  }
  return { source_commit: SOURCE_COMMIT, source_sha256: libraries.sha256, high_leg_id: highId, low_leg_id: lowId, pair_status: pair.status, couple_status: couple.status, legs: updates };
}

module.exports = { SOURCE_COMMIT, MODULES, configureSurvivorShapeLibraries, advanceSurvivorShapes, macroState, causalAskPrefix };
