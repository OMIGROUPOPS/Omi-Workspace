"use strict";

// V52e wires N9 as a continuously consulted prior overlay over frozen V52d.
// Priors can add information or rescue an N4 abstention beside live evidence;
// they can never withdraw an authority V52d already earned.

const v52d = require("./window1_v52d_disagreement_referee.js");

let cleanStore = null;

function configurePalantir(store) {
  if (!store?.boot_assertion?.passed || store.boot_assertion.unvalidated_loaded || store.boot_assertion.quarantined_loaded || store.boot_assertion.superseded_loaded) throw new Error("N9 CLEAN-store boot assertion failed");
  cleanStore = store;
  return store.boot_assertion;
}

function requiredStore() { if (!cleanStore) throw new Error("N9 CLEAN store not configured"); return cleanStore; }
function provenance(id) {
  const asset = requiredStore().loaded[id];
  if (!asset) throw new Error(`N9 asset not loaded ${id}`);
  const status = asset.entry.status.startsWith("VALID-NARROW") ? "VALID-NARROW" : "VALIDATED";
  return { asset_id: id, status, source_sha256: asset.sources.length === 1 ? asset.sources[0].sha256 : null, source_sha256s: asset.sources.length > 1 ? asset.sources.map((source) => source.sha256) : null };
}
function inverseRelation(own, sibling) {
  if (own === "SETTLED" || sibling === "SETTLED") return "mixed_settled";
  if ((own === "RISING" && sibling === "FALLING") || (own === "FALLING" && sibling === "RISING")) return "coherent_inverse";
  return "incoherent_same";
}
function gridCell(category, cents) {
  const row = requiredStore().loaded.P1.data?.[category]?.[String(cents)] ?? null;
  return row && Number.isFinite(row.edge_p50) ? { cell_cents: cents, ...row } : null;
}

function consultN2({ category, startingPriceSplit, combinedState, row }) {
  const store = requiredStore();
  const p2 = store.loaded.P2.data.discriminators?.tables ?? {};
  const p4 = store.loaded.P4.data;
  const p11 = store.loaded.P11.data.DEV;
  const p14 = store.loaded.P14.data;
  const state = p4.accuracy_per_state?.["60m"]?.[combinedState] ?? null;
  const categoryRate = p4.accuracy_per_category?.["60m"]?.[category] ?? null;
  const signalRank = p14.per_category?.[category] ?? null;
  const hiddenCounts = p11.by_category?.[category] ?? null;
  const hiddenTotal = hiddenCounts ? Object.values(hiddenCounts).reduce((a, b) => a + b, 0) : 0;
  return {
    node: "N2",
    consulted_at_receipt: row.receipt,
    consulted_at_timestamp_epoch: row.ts,
    decision_time_inputs: { category, starting_price_split: startingPriceSplit, state: combinedState },
    category_base_rate_60m: categoryRate,
    state_base_rate_60m: state,
    cell_base_rate: p2.cell?.[startingPriceSplit] ?? null,
    hidden_book_signal_prior: hiddenCounts ? { counts: hiddenCounts, total: hiddenTotal } : null,
    validated_signal_priors: signalRank ? { n_spike: signalRank.n_spike, rank: signalRank.rank.slice(0, 3).map(({ signal, auc_oriented, lift }) => ({ signal, auc_oriented, lift })) } : null,
    role: "RECORDED_PRIOR_INPUT_TO_LIVE_TAPE_ELIMINATION_NEVER_A_GATE",
    provenance: [provenance("P2"), provenance("P4"), provenance("P11"), provenance("P14")],
  };
}

function consultN4({ category, startingPriceSplit, row }) {
  const store = requiredStore();
  const p2 = store.loaded.P2.data.discriminators?.tables ?? {};
  const decisionCell = Number.isInteger(row.ask) ? row.ask : null;
  return {
    node: "N4",
    consulted_at_receipt: row.receipt,
    consulted_at_timestamp_epoch: row.ts,
    decision_time_cell_source: "CURRENT_QUALIFYING_BOOK_ASK_NOT_EX_POST_CLOSE",
    grid: Number.isInteger(decisionCell) ? gridCell(category, decisionCell) : null,
    zone: { category: p2.cat?.[category] ?? null, starting_price_split: p2.cell?.[startingPriceSplit] ?? null },
    leak_ordering: store.loaded.P6.data.mechanism_classes ?? null,
    role: "REFERENCE_BOUND_BESIDE_LIVE_EVIDENCE_NEVER_SOLE_AUTHORITY",
    provenance: [provenance("P1"), provenance("P2"), provenance("P6")],
  };
}

function consultN5({ category, quoteState, pressureState, siblingState, row }) {
  const store = requiredStore();
  const mirror = store.loaded.P2.data.discriminators?.tables?.mirror ?? {};
  const p12 = store.loaded.P12.data;
  const sealed = store.loaded.P13.data.sealed;
  const cap = store.loaded.P13.data.cap;
  const quoteRelation = inverseRelation(quoteState, siblingState);
  const pressureRelation = inverseRelation(pressureState, siblingState);
  return {
    node: "N5",
    consulted_at_receipt: row.receipt,
    consulted_at_timestamp_epoch: row.ts,
    category,
    sibling_state: siblingState,
    quote_candidate: { state: quoteState, mirror_relation: quoteRelation, validated_right_share: mirror[quoteRelation]?.share ?? null },
    pressure_candidate: { state: pressureState, mirror_relation: pressureRelation, validated_right_share: mirror[pressureRelation]?.share ?? null },
    mirror_coherence_base_rate: sealed.MIRROR_COHERENCE ?? null,
    one_eyed_vindication_base_rate: cap.THE_22 ? { n: cap.THE_22.n, vindicated: cap.THE_22.vindicated, rate: cap.THE_22.n ? cap.THE_22.vindicated / cap.THE_22.n : null } : null,
    divot_arrival_base: p12.DEV ? { total: p12.DEV.total, class_counts: Object.fromEntries(Object.entries(p12.DEV.classes || {}).map(([key, value]) => [key, Number.isFinite(value) ? value : value?.n ?? null])) } : null,
    role: "TIE_AND_MARGIN_INFORMANT_NEVER_A_GATE",
    provenance: [provenance("P2"), provenance("P12"), provenance("P13")],
  };
}

function continuousConsultation(context) {
  return {
    manifest: { commit: requiredStore().manifest_commit, sha256: requiredStore().manifest_sha256, status: "CLEAN_STORE_ONLY" },
    N2: consultN2(context),
    N4: consultN4(context),
    N5: consultN5(context),
    continuous_at_decision_time: true,
    priors_gate: false,
  };
}

function normalizedClauses(value = {}) {
  const clauses = v52d.normalizedClauses(value);
  return value.palantir_priors ? { ...clauses, palantir_priors: true } : clauses;
}

function machineReadLevel(license, incumbent) {
  const frozen = v52d.machineReadLevel(license, incumbent);
  const prior = license?.palantir?.N4 ?? null;
  if (!prior || frozen.authorized) return { ...frozen, palantir: prior, palantir_rescue: false, frozen_authority_preserved: frozen.authorized };
  const bounds = frozen.evidence?.post_onset_observation_bounds;
  const grid = prior.grid;
  const ask = frozen.evidence?.current_book?.ask;
  const liveBounded = Number.isInteger(bounds?.min_cents) && Number.isInteger(bounds?.max_cents) && Number.isInteger(frozen.proposed_target_cents)
    ? Math.max(bounds.min_cents, Math.min(bounds.max_cents, frozen.proposed_target_cents)) : null;
  const gridReference = Number.isInteger(ask) && Number.isFinite(grid?.edge_p50) ? ask - grid.edge_p50 : null;
  const target = v52d.lawfulCent(liveBounded) && Number.isInteger(gridReference)
    ? Math.max(bounds.min_cents, Math.min(liveBounded, gridReference)) : null;
  const authorized = frozen.supported_authority && frozen.evidence_is_post_onset && frozen.receipt_bound && v52d.lawfulCent(target);
  return {
    ...frozen,
    authorized,
    target_cents: authorized ? target : null,
    palantir: prior,
    palantir_rescue: authorized,
    frozen_authority_preserved: false,
    live_evidence_bounded_target_cents: liveBounded,
    grid_reference_target_cents: gridReference,
    authority: authorized ? "V52E_N4_LIVE_EVIDENCE_BOUND_WITH_CLEAN_GRID_REFERENCE" : null,
  };
}

const firstFailure = v52d.firstFailure;

function gateDecision(inputs, incumbent) {
  const clauses = normalizedClauses(inputs.clauses);
  if (!clauses.palantir_priors) return v52d.gateDecision({ ...inputs, clauses }, incumbent);
  const original = inputs.birthLicense;
  const readLevel = machineReadLevel(original, incumbent);
  const license = {
    ...original,
    onset: original?.onset ? { ...original.onset, binding_status: "CODEX-INTERIM", binding_changed_by_V52e: false } : null,
    diary: original?.diary ? { ...original.diary, role: "RECORDED_REFERENCE_INPUT_NOT_SOLE_LEVEL_AUTHORITY" } : null,
    palantir: original?.palantir ?? null,
    level: {
      ...original?.level,
      target_cents: readLevel.target_cents,
      authority: readLevel.authorized ? (readLevel.palantir_rescue ? "V52E_N4_PRIOR_INFORMED_LIVE_BOUND_LEVEL" : "V52B_EVIDENCE_BACKED_MACHINE_READ_LEVEL") : "V52B_MACHINE_READ_LEVEL_ABSTAIN",
      machine_read: readLevel,
      palantir_prior_informed: Boolean(readLevel.palantir_rescue),
    },
  };
  const active = v52d.lawfulCent(inputs.activeTarget) ? inputs.activeTarget : null;
  if (active !== null && incumbent?.action === "CANCEL_REST") return { ...incumbent, birth_license: license, judgment_gate: { enabled: true, verdict: "INCUMBENT_LICENSED_REST_GUARD", failure: null, clause_N9: "PRIORS_INFORM_NEVER_GATE" } };
  const failure = firstFailure(license, readLevel);
  if (failure) return { action: "HOLD_REST", target_cents: active, reason: `V52E_BIRTH_BLOCKED_${failure}`, placement: incumbent?.placement ?? null, guard: active === null ? null : incumbent?.guard ?? null, unguarded_decision: incumbent, birth_license: license, judgment_gate: { enabled: true, verdict: "BLOCKED", failure, clause_N9: "PRIORS_INFORM_NEVER_GATE" } };
  const target = readLevel.target_cents;
  const action = active === null ? "PLACE_REST" : active === target ? "HOLD_REST" : "REPRICE_REST";
  return { action, target_cents: target, ...(action === "REPRICE_REST" ? { direction: target > active ? "UP" : "DOWN" } : {}), reason: action === "HOLD_REST" ? "V52E_LICENSED_LEVEL_ALREADY_STANDING" : "V52E_LICENSED_PRIOR_INFORMED_LEVEL_POST", placement: { target_cents: target, unbounded_target_cents: readLevel.proposed_target_cents, authority: license.level.authority, incumbent_authority: readLevel.incumbent_authority, displayed_bid_consumed_as_unlicensed_anchor: false, evidence: readLevel.evidence, palantir: license.palantir?.N4 ?? null }, guard: active === null ? null : incumbent?.guard ?? null, unguarded_decision: incumbent, birth_license: license, judgment_gate: { enabled: true, verdict: action === "HOLD_REST" ? "LICENSED_HOLD" : "POST", failure: null, clause_N9: "PRIORS_INFORM_NEVER_GATE" } };
}

function decideReceipt(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const atomic = v52d.decideReceipt({ ...inputs, clauses: { ...clauses, palantir_priors: false } });
  return { ...atomic, decision: gateDecision({ ...inputs, clauses }, atomic.decision.unguarded_decision ?? atomic.decision), palantir_priors_enabled: Boolean(clauses.palantir_priors) };
}
function decide(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const incumbent = v52d.decide({ ...inputs, clauses: { ...clauses, palantir_priors: false } });
  return gateDecision({ ...inputs, clauses }, incumbent.unguarded_decision ?? incumbent);
}

function adjudicateDisagreement(args) {
  const frozen = v52d.adjudicateDisagreement(args);
  const prior = args.palantir?.N5 ?? null;
  if (!prior) return frozen;
  const result = { ...frozen, palantir_priors_consumed: true, historical_inputs_consumed: true, palantir: prior, prior_role: "INFORMANT_NEVER_GATE" };
  if (!frozen.firing || frozen.resolved) return result;
  const q = prior.quote_candidate?.validated_right_share;
  const p = prior.pressure_candidate?.validated_right_share;
  if (!Number.isFinite(q) || !Number.isFinite(p) || q === p) return { ...result, status: "HONEST_TIE_FREEZE_STANDS_AFTER_N5_PRIOR" };
  const winnerReading = q > p ? args.quote.state : args.pressure;
  const loserReading = q > p ? args.pressure : args.quote.state;
  return { ...result, status: "ADJUDICATED_N5_STRICTLY_STRONGER_VALIDATED_BASE_RATE", resolved: true, winner: { reading: winnerReading, evidence_class: "VALIDATED_N5_PRIOR", validated_right_share: Math.max(q, p) }, loser: { reading: loserReading, evidence_class: "VALIDATED_N5_PRIOR", validated_right_share: Math.min(q, p) }, comparison: { ordering: ["FROZEN_V52D_IN_GAME_BACKING_FIRST", "N5_VALIDATED_MIRROR_BASE_RATE_ONLY_ON_FROZEN_TIE"], decisive_field: "validated_right_share", result: q > p ? 1 : -1, strict: true } };
}

module.exports = { ...v52d, configurePalantir, requiredStore, provenance, inverseRelation, consultN2, consultN4, consultN5, continuousConsultation, normalizedClauses, machineReadLevel, firstFailure, gateDecision, decideReceipt, decide, adjudicateDisagreement };
