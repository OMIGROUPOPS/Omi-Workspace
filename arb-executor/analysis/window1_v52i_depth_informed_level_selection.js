"use strict";

// V52i changes clause 3/N4 level selection only.  The frozen V52h decision
// stack remains authoritative; depth priors may lower a target only after the
// incumbent live read earned authority.  They never create authority or gate.

const v52h = require("./window1_v52h_remove_pair_lows_precondition.js");

let validationStore = null;

function configurePalantir(store) {
  if (!store?.boot_assertion?.passed || store.boot_assertion.under_validation_loaded !== 2 || store.boot_assertion.canonical_clean_store_unchanged !== true) throw new Error("V52i under-validation boot assertion failed");
  validationStore = store;
  return v52h.configurePalantir(store);
}
function requiredValidationStore() { if (!validationStore) throw new Error("V52i validation store not configured"); return validationStore; }
function candidateProvenance(id) {
  const asset = requiredValidationStore().loaded[id];
  if (!asset || asset.entry.status !== "UNDER-VALIDATION_V52I") throw new Error(`V52i candidate unavailable ${id}`);
  return {
    asset_id: id,
    status: asset.entry.status,
    source_sha256: asset.sources.length === 1 ? asset.sources[0].sha256 : null,
    source_sha256s: asset.sources.length > 1 ? asset.sources.map((source) => source.sha256) : null,
    source_commit: asset.sources.length === 1 ? asset.sources[0].commit : null,
    role: "RECORDED_PRIOR_INPUT_UNDER_VALIDATION_NEVER_GATE",
  };
}

function normalizedClauses(value = {}) {
  const clauses = v52h.normalizedClauses(value);
  return value.depth_informed_level_selection
    ? { ...clauses, depth_informed_level_selection: true }
    : clauses;
}

function priceRegion(value) {
  if (typeof value === "string" && ["le25", "26_50", "51_75", "ge76"].includes(value)) return value;
  return null;
}
function depthCandidates({ category, priceRegion: region, row }) {
  const store = requiredValidationStore();
  const ask = Number.isInteger(row?.ask) ? row.ask : null;
  const grid = ask === null ? null : store.loaded.G_GRID_LEVEL_DISCOUNT.data?.[category]?.[String(ask)] ?? null;
  const key = `${category}|${priceRegion(region)}`;
  const greek = store.loaded.G3_DIP_RECOVERY_GRADIENT.data;
  const depth = greek?.depth_cells?.[key] ?? null;
  const recovery = greek?.recovery_within_60min?.[key] ?? null;
  return {
    role: "TWO_DEPTH_PRIORS_WEIGHT_LEVEL_BESIDE_LIVE_EVIDENCE_NEVER_GATE",
    decision_time_inputs: { category, price_region: priceRegion(region), current_ask_cents: ask },
    G_GRID: Number.isFinite(grid?.edge_p50) ? { discount_cents: grid.edge_p50, cell_ask_cents: ask, raw: grid } : null,
    G3: depth && Number.isFinite(recovery) ? { dip_depth_median_cents: depth.median, dip_depth_p75_cents: depth.p75, recovery_within_60min: recovery, n: depth.n, cell: key } : null,
    provenance: [candidateProvenance("G_GRID_LEVEL_DISCOUNT"), candidateProvenance("G3_DIP_RECOVERY_GRADIENT")],
  };
}

function continuousConsultation(context) {
  const frozen = v52h.continuousConsultation(context);
  if (!context?.clauses?.depth_informed_level_selection) return frozen;
  const candidates = depthCandidates(context);
  return {
    ...frozen,
    N4: { ...frozen.N4, depth_candidates_under_validation: candidates },
    under_validation: { enabled: true, candidate_ids: candidates.provenance.map((row) => row.asset_id), status: "UNDER-VALIDATION_V52I" },
    priors_gate: false,
  };
}

function roundCent(value) { return Number.isFinite(value) ? Math.round(value) : null; }
function depthSelection(license, incumbent) {
  const frozen = v52h.machineReadLevel(license, incumbent);
  const candidates = license?.palantir?.N4?.depth_candidates_under_validation ?? null;
  const bounds = frozen.evidence?.post_onset_observation_bounds;
  const ask = frozen.evidence?.current_book?.ask;
  const gridDiscount = candidates?.G_GRID?.discount_cents;
  const dipDepth = candidates?.G3?.dip_depth_median_cents;
  const recovery = candidates?.G3?.recovery_within_60min;
  const applicable = frozen.authorized === true && v52h.lawfulCent(frozen.target_cents)
    && Number.isInteger(ask) && Number.isFinite(gridDiscount) && Number.isFinite(dipDepth)
    && Number.isFinite(recovery) && recovery >= 0 && recovery <= 1
    && Number.isInteger(bounds?.min_cents) && Number.isInteger(bounds?.max_cents);
  if (!applicable) return {
    clause: "CLAUSE_3_DEPTH_INFORMED_LEVEL_SELECTION",
    applicable: false,
    reason: frozen.authorized !== true ? "LIVE_MACHINE_READ_AUTHORITY_ABSENT_PRIORS_SILENT" : "DEPTH_PRIOR_CELL_OR_LIVE_BOUND_ABSENT",
    live_authority_retained: true,
    priors_gate: false,
    frozen_machine_read: frozen,
    candidates,
    selected_target_cents: frozen.target_cents ?? null,
  };
  const weightedDiscount = roundCent((gridDiscount * recovery) + (dipDepth * (1 - recovery)));
  const priorCandidate = ask - Math.max(1, weightedDiscount);
  const liveBoundedCandidate = Math.max(bounds.min_cents, Math.min(bounds.max_cents, priorCandidate));
  const selected = Math.min(frozen.target_cents, liveBoundedCandidate);
  return {
    clause: "CLAUSE_3_DEPTH_INFORMED_LEVEL_SELECTION",
    applicable: true,
    reason: selected < frozen.target_cents ? "DEPTH_PRIORS_LOWER_FROZEN_LIVE_AUTHORIZED_TARGET" : "FROZEN_LIVE_AUTHORIZED_TARGET_ALREADY_AT_OR_BELOW_DEPTH_REFERENCE",
    live_authority_retained: true,
    priors_gate: false,
    weighting_law: "ROUND(G_GRID_DISCOUNT*G3_RECOVERY + G3_MEDIAN_DIP_DEPTH*(1-G3_RECOVERY))",
    arithmetic: `${gridDiscount}*${recovery}+${dipDepth}*${1 - recovery}=${weightedDiscount}`,
    frozen_machine_read: frozen,
    candidates,
    weighted_discount_cents: weightedDiscount,
    prior_candidate_target_cents: priorCandidate,
    live_bounded_candidate_target_cents: liveBoundedCandidate,
    selected_target_cents: selected,
    target_changed: selected !== frozen.target_cents,
  };
}

function gateDecision(inputs, incumbent) {
  const clauses = normalizedClauses(inputs.clauses);
  if (!clauses.depth_informed_level_selection) return v52h.gateDecision({ ...inputs, clauses }, incumbent);
  const selection = depthSelection(inputs.birthLicense, incumbent);
  const adjustedLicense = selection.applicable ? {
    ...inputs.birthLicense,
    level: { ...inputs.birthLicense.level, proposed_target_cents: selection.selected_target_cents, depth_informed_level_selection: selection },
  } : {
    ...inputs.birthLicense,
    level: { ...inputs.birthLicense?.level, depth_informed_level_selection: selection },
  };
  const decision = v52h.gateDecision({ ...inputs, clauses: { ...clauses, depth_informed_level_selection: false }, birthLicense: adjustedLicense }, incumbent);
  const licensedSelection = { ...selection, final_licensed_target_cents: decision.target_cents ?? null };
  return {
    ...decision,
    birth_license: decision.birth_license ? {
      ...decision.birth_license,
      level: { ...decision.birth_license.level, depth_informed_level_selection: licensedSelection },
    } : null,
    depth_informed_level_selection: licensedSelection,
  };
}

function decideReceipt(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const atomic = v52h.decideReceipt({ ...inputs, clauses: { ...clauses, depth_informed_level_selection: false } });
  return { ...atomic, decision: gateDecision({ ...inputs, clauses }, atomic.decision.unguarded_decision ?? atomic.decision), depth_informed_level_selection_enabled: Boolean(clauses.depth_informed_level_selection) };
}
function decide(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const incumbent = v52h.decide({ ...inputs, clauses: { ...clauses, depth_informed_level_selection: false } });
  return gateDecision({ ...inputs, clauses }, incumbent.unguarded_decision ?? incumbent);
}

module.exports = { ...v52h, configurePalantir, requiredValidationStore, candidateProvenance, normalizedClauses, depthCandidates, continuousConsultation, depthSelection, gateDecision, decideReceipt, decide };
