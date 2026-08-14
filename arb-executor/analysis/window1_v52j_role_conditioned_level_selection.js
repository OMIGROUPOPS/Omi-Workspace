"use strict";

// V52j changes clause 3/N4 level selection only over the frozen V52h stack.
// V52i's symmetric depth refinement is deliberately not inherited.  The
// existing pair reads assign a receipt-local role: FALLING may consult the two
// under-validation depth priors, while RISING/SETTLED/insufficient retain the
// frozen evidence-backed level.  Priors never create, withdraw, or gate live
// authority.

const v52h = require("./window1_v52h_remove_pair_lows_precondition.js");

let validationStore = null;

function configurePalantir(store) {
  if (!store?.boot_assertion?.passed || store.boot_assertion.under_validation_loaded !== 2 || store.boot_assertion.canonical_clean_store_unchanged !== true) throw new Error("V52j under-validation boot assertion failed");
  validationStore = store;
  return v52h.configurePalantir(store);
}
function requiredValidationStore() { if (!validationStore) throw new Error("V52j validation store not configured"); return validationStore; }
function candidateProvenance(id) {
  const asset = requiredValidationStore().loaded[id];
  if (!asset || asset.entry.status !== "UNDER-VALIDATION_V52I") throw new Error(`V52j continuing candidate unavailable ${id}`);
  return {
    asset_id: id,
    status: asset.entry.status,
    validation_continuation: "V52J_ROLE_CONDITIONED_USE; CANONICAL_ASSET_UNCHANGED",
    source_sha256: asset.sources.length === 1 ? asset.sources[0].sha256 : null,
    source_sha256s: asset.sources.length > 1 ? asset.sources.map((source) => source.sha256) : null,
    source_commit: asset.sources.length === 1 ? asset.sources[0].commit : null,
    role: "RECORDED_PRIOR_INPUT_UNDER_VALIDATION_NEVER_GATE",
  };
}

function normalizedClauses(value = {}) {
  const clauses = v52h.normalizedClauses(value);
  return value.role_conditioned_level_selection
    ? { ...clauses, role_conditioned_level_selection: true }
    : clauses;
}

function priceRegion(value) {
  return typeof value === "string" && ["le25", "26_50", "51_75", "ge76"].includes(value) ? value : null;
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
    role: "FALLER_ONLY_DEPTH_PRIORS_BESIDE_LIVE_EVIDENCE_NEVER_GATE",
    decision_time_inputs: { category, price_region: priceRegion(region), current_ask_cents: ask },
    G_GRID: Number.isFinite(grid?.edge_p50) ? { discount_cents: grid.edge_p50, cell_ask_cents: ask, raw: grid } : null,
    G3: depth && Number.isFinite(recovery) ? { dip_depth_median_cents: depth.median, dip_depth_p75_cents: depth.p75, recovery_within_60min: recovery, n: depth.n, cell: key } : null,
    provenance: [candidateProvenance("G_GRID_LEVEL_DISCOUNT"), candidateProvenance("G3_DIP_RECOVERY_GRADIENT")],
  };
}

function normalizeRole(read) {
  if (read === "FALLING" || read === "RISING") return read;
  if (read === "SETTLED") return "SETTLED";
  return "INSUFFICIENT";
}
function pairRoleCoherence(ownRole, siblingRole) {
  if (ownRole === "INSUFFICIENT" || siblingRole === "INSUFFICIENT") return "INSUFFICIENT_PAIR_READ";
  if ((ownRole === "FALLING" && siblingRole === "RISING") || (ownRole === "RISING" && siblingRole === "FALLING")) return "INVERSE_COHERENT";
  if (ownRole === siblingRole && (ownRole === "FALLING" || ownRole === "RISING")) return "SAME_DIRECTION_DISAGREEMENT";
  return "SETTLED_OR_MIXED";
}
function pairRoleAssignment(license) {
  const ownRole = normalizeRole(license?.read?.state);
  const siblingRead = license?.palantir?.N4?.pair_role_inputs?.sibling_read ?? null;
  const siblingRole = normalizeRole(siblingRead?.state);
  return {
    clause: "CLAUSE_3_N4_ROLE_CONDITIONED_LEVEL_SELECTION",
    own_role: ownRole,
    sibling_role: siblingRole,
    pair_read_coherence: pairRoleCoherence(ownRole, siblingRole),
    own_read_evidence: {
      state: license?.read?.state ?? null,
      receipt: license?.read?.receipt ?? null,
      quote_path_state: license?.read?.quote_path_state ?? null,
      pressure_state: license?.read?.pressure_state ?? null,
      directional_evidence_receipt: license?.level?.machine_read_evidence?.directional_evidence_receipt ?? null,
      directional_evidence_kind: license?.level?.machine_read_evidence?.directional_evidence_kind ?? null,
    },
    sibling_read_evidence: siblingRead,
    licensing_coherence: license?.coherence ?? null,
    re_evaluated_at_every_read: true,
  };
}

function continuousConsultation(context) {
  const frozen = v52h.continuousConsultation(context);
  if (!context?.clauses?.role_conditioned_level_selection) return frozen;
  const candidates = depthCandidates(context);
  return {
    ...frozen,
    N4: {
      ...frozen.N4,
      depth_candidates_under_validation: candidates,
      pair_role_inputs: {
        own_read: { state: context.combinedState ?? null, quote_path_state: context.quoteState ?? null, pressure_state: context.pressureState ?? null, receipt: context.row?.receipt ?? null },
        sibling_read: context.siblingReadEvidence ?? { state: context.siblingState ?? null, receipt: null },
      },
    },
    under_validation: { enabled: true, candidate_ids: candidates.provenance.map((row) => row.asset_id), status: "UNDER-VALIDATION_CONTINUED_V52J" },
    priors_gate: false,
  };
}

function roundCent(value) { return Number.isFinite(value) ? Math.round(value) : null; }
function roleConditionedSelection(license, incumbent) {
  const frozen = v52h.machineReadLevel(license, incumbent);
  const role = pairRoleAssignment(license);
  const candidates = license?.palantir?.N4?.depth_candidates_under_validation ?? null;
  const bounds = frozen.evidence?.post_onset_observation_bounds;
  const ask = frozen.evidence?.current_book?.ask;
  const gridDiscount = candidates?.G_GRID?.discount_cents;
  const dipDepth = candidates?.G3?.dip_depth_median_cents;
  const recovery = candidates?.G3?.recovery_within_60min;
  const hasDepthAuthority = frozen.authorized === true && v52h.lawfulCent(frozen.target_cents)
    && Number.isInteger(ask) && Number.isFinite(gridDiscount) && Number.isFinite(dipDepth)
    && Number.isFinite(recovery) && recovery >= 0 && recovery <= 1
    && Number.isInteger(bounds?.min_cents) && Number.isInteger(bounds?.max_cents);
  if (role.own_role !== "FALLING") return {
    clause: "CLAUSE_3_N4_ROLE_CONDITIONED_LEVEL_SELECTION",
    applicable: false,
    reason: role.own_role === "RISING" ? "RISING_USES_OWN_NEAR_SUPPORT_FROZEN_EVIDENCE_BACKED_LEVEL" : "SETTLED_OR_INSUFFICIENT_USES_FROZEN_EVIDENCE_BACKED_LEVEL",
    role_assignment: role,
    live_authority_retained: true,
    priors_gate: false,
    frozen_machine_read: frozen,
    candidates,
    selected_target_cents: frozen.target_cents ?? null,
    target_changed: false,
  };
  if (!hasDepthAuthority) return {
    clause: "CLAUSE_3_N4_ROLE_CONDITIONED_LEVEL_SELECTION",
    applicable: false,
    reason: frozen.authorized !== true ? "FALLING_LIVE_MACHINE_READ_AUTHORITY_ABSENT_PRIORS_SILENT" : "FALLING_DEPTH_PRIOR_CELL_OR_LIVE_BOUND_ABSENT",
    role_assignment: role,
    live_authority_retained: true,
    priors_gate: false,
    frozen_machine_read: frozen,
    candidates,
    selected_target_cents: frozen.target_cents ?? null,
    target_changed: false,
  };
  const weightedDiscount = roundCent((gridDiscount * recovery) + (dipDepth * (1 - recovery)));
  const priorCandidate = ask - Math.max(1, weightedDiscount);
  const liveBoundedCandidate = Math.max(bounds.min_cents, Math.min(bounds.max_cents, priorCandidate));
  const selected = Math.min(frozen.target_cents, liveBoundedCandidate);
  return {
    clause: "CLAUSE_3_N4_ROLE_CONDITIONED_LEVEL_SELECTION",
    applicable: true,
    reason: selected < frozen.target_cents ? "FALLING_DEPTH_PRIORS_LOWER_FROZEN_LIVE_AUTHORIZED_TARGET" : "FALLING_FROZEN_TARGET_ALREADY_AT_OR_BELOW_DEPTH_REFERENCE",
    role_assignment: role,
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
  if (!clauses.role_conditioned_level_selection) return v52h.gateDecision({ ...inputs, clauses }, incumbent);
  const selection = roleConditionedSelection(inputs.birthLicense, incumbent);
  const adjustedLicense = selection.applicable ? {
    ...inputs.birthLicense,
    level: { ...inputs.birthLicense.level, proposed_target_cents: selection.selected_target_cents, role_conditioned_level_selection: selection },
  } : {
    ...inputs.birthLicense,
    level: { ...inputs.birthLicense?.level, role_conditioned_level_selection: selection },
  };
  const adjustedIncumbent = selection.applicable ? {
    ...incumbent,
    target_cents: selection.selected_target_cents,
    placement: incumbent?.placement ? { ...incumbent.placement, target_cents: selection.selected_target_cents } : incumbent?.placement,
  } : incumbent;
  const decision = v52h.gateDecision({ ...inputs, clauses: { ...clauses, role_conditioned_level_selection: false }, birthLicense: adjustedLicense }, adjustedIncumbent);
  const licensedSelection = { ...selection, final_licensed_target_cents: decision.target_cents ?? null };
  return {
    ...decision,
    birth_license: decision.birth_license ? { ...decision.birth_license, level: { ...decision.birth_license.level, role_conditioned_level_selection: licensedSelection } } : null,
    role_conditioned_level_selection: licensedSelection,
  };
}

function decideReceipt(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const atomic = v52h.decideReceipt({ ...inputs, clauses: { ...clauses, role_conditioned_level_selection: false } });
  return { ...atomic, decision: gateDecision({ ...inputs, clauses }, atomic.decision.unguarded_decision ?? atomic.decision), role_conditioned_level_selection_enabled: Boolean(clauses.role_conditioned_level_selection) };
}
function decide(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const incumbent = v52h.decide({ ...inputs, clauses: { ...clauses, role_conditioned_level_selection: false } });
  return gateDecision({ ...inputs, clauses }, incumbent.unguarded_decision ?? incumbent);
}

module.exports = { ...v52h, configurePalantir, requiredValidationStore, candidateProvenance, normalizedClauses, depthCandidates, normalizeRole, pairRoleCoherence, pairRoleAssignment, continuousConsultation, roleConditionedSelection, gateDecision, decideReceipt, decide };
