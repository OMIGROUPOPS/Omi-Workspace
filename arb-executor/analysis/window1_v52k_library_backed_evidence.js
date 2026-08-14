"use strict";

// V52k changes clause 3 only over the frozen V52h behavioral stack.  A
// receipt-local level may be licensed by either the game's post-onset tape or
// the two operator-bound library assets.  Unlike V52i/V52j, library evidence
// may name a level below the shown range.  It never changes onset, read,
// referee, settlement, joint-target, crediting, or scavenger mechanics.

const v52h = require("./window1_v52h_remove_pair_lows_precondition.js");

let validationStore = null;

function configurePalantir(store) {
  if (!store?.boot_assertion?.passed || store.boot_assertion.under_validation_loaded !== 2 || store.boot_assertion.canonical_clean_store_unchanged !== true) throw new Error("V52k under-validation boot assertion failed");
  validationStore = store;
  return v52h.configurePalantir(store);
}
function requiredValidationStore() { if (!validationStore) throw new Error("V52k validation store not configured"); return validationStore; }
function candidateProvenance(id) {
  const asset = requiredValidationStore().loaded[id];
  if (!asset || asset.entry.status !== "UNDER-VALIDATION_V52I") throw new Error(`V52k candidate unavailable ${id}`);
  return {
    asset_id: id,
    status: asset.entry.status,
    validation_continuation: "V52K_LIBRARY_EVIDENCE_AUTHORITY; CANONICAL_ASSET_UNCHANGED",
    source_sha256: asset.sources.length === 1 ? asset.sources[0].sha256 : null,
    source_sha256s: asset.sources.length > 1 ? asset.sources.map((source) => source.sha256) : null,
    source_commit: asset.sources.length === 1 ? asset.sources[0].commit : null,
    role: "LIBRARY_EVIDENCE_INPUT_UNDER_VALIDATION_NEVER_GATE",
  };
}

function normalizedClauses(value = {}) {
  const clauses = v52h.normalizedClauses(value);
  return value.library_backed_level_evidence
    ? { ...clauses, library_backed_level_evidence: true }
    : clauses;
}

function priceRegion(value) {
  return typeof value === "string" && ["le25", "26_50", "51_75", "ge76"].includes(value) ? value : null;
}
function libraryCandidates({ category, priceRegion: region, row }) {
  const store = requiredValidationStore();
  const ask = Number.isInteger(row?.ask) ? row.ask : null;
  const grid = ask === null ? null : store.loaded.G_GRID_LEVEL_DISCOUNT.data?.[category]?.[String(ask)] ?? null;
  const cell = `${category}|${priceRegion(region)}`;
  const greek = store.loaded.G3_DIP_RECOVERY_GRADIENT.data;
  const depth = greek?.depth_cells?.[cell] ?? null;
  const recovery = greek?.recovery_within_60min?.[cell] ?? null;
  return {
    role: "GRID_AND_G3_MAY_LICENSE_BELOW_SHOWN_RANGE_CLAUSE_3_ONLY",
    decision_time_inputs: { category, price_region: priceRegion(region), current_ask_cents: ask },
    G_GRID: Number.isFinite(grid?.edge_p50) ? { discount_cents: grid.edge_p50, cell_ask_cents: ask, raw: grid } : null,
    G3: depth && Number.isFinite(recovery) ? { dip_depth_median_cents: depth.median, dip_depth_p75_cents: depth.p75, recovery_within_60min: recovery, n: depth.n, cell } : null,
    provenance: [candidateProvenance("G_GRID_LEVEL_DISCOUNT"), candidateProvenance("G3_DIP_RECOVERY_GRADIENT")],
  };
}

function continuousConsultation(context) {
  const frozen = v52h.continuousConsultation(context);
  if (!context?.clauses?.library_backed_level_evidence) return frozen;
  const candidates = libraryCandidates(context);
  return {
    ...frozen,
    N4: { ...frozen.N4, library_level_evidence_under_validation: candidates },
    under_validation: { enabled: true, candidate_ids: candidates.provenance.map((row) => row.asset_id), status: "UNDER-VALIDATION_CONTINUED_V52K" },
    priors_gate: false,
  };
}

function roundCent(value) { return Number.isFinite(value) ? Math.round(value) : null; }
function pairCap(inputs) {
  const counterpart = inputs?.siblingCredited === true ? inputs.siblingEntryCents : inputs?.siblingStandingTarget;
  return Number.isInteger(counterpart) ? 99 - counterpart : null;
}
function libraryEvidenceSelection(license, incumbent, inputs = {}) {
  const frozen = v52h.machineReadLevel(license, incumbent);
  const candidates = license?.palantir?.N4?.library_level_evidence_under_validation ?? null;
  const originalBounds = frozen.evidence?.post_onset_observation_bounds ?? null;
  const ask = frozen.evidence?.current_book?.ask;
  const gridDiscount = candidates?.G_GRID?.discount_cents;
  const dipDepth = candidates?.G3?.dip_depth_median_cents;
  const recovery = candidates?.G3?.recovery_within_60min;
  const readExists = license?.read?.passed === true && Number.isFinite(license?.onset?.timestamp_epoch)
    && Number.isFinite(frozen.evidence?.evaluation_timestamp_epoch)
    && Number.isFinite(frozen.evidence?.directional_evidence_timestamp_epoch)
    && frozen.evidence.evaluation_timestamp_epoch >= license.onset.timestamp_epoch
    && frozen.evidence.directional_evidence_timestamp_epoch >= license.onset.timestamp_epoch
    && frozen.evidence.directional_evidence_timestamp_epoch <= frozen.evidence.evaluation_timestamp_epoch
    && typeof frozen.evidence?.evaluation_receipt === "string" && frozen.evidence.evaluation_receipt.length > 0
    && typeof frozen.evidence?.directional_evidence_receipt === "string" && frozen.evidence.directional_evidence_receipt.length > 0;
  const candidateComplete = Number.isInteger(ask) && Number.isFinite(gridDiscount) && Number.isFinite(dipDepth)
    && Number.isFinite(recovery) && recovery >= 0 && recovery <= 1;
  if (!readExists || !candidateComplete) return {
    clause: "CLAUSE_3_LIBRARY_BACKED_LEVEL_EVIDENCE",
    applicable: false,
    frozen_clause_2_read_passed: readExists,
    evidence_authority: frozen.authorized ? "POST_ONSET_TAPE" : "NONE",
    reason: !readExists ? "POST_ONSET_MACHINE_READ_ABSENT_LIBRARY_CANNOT_BYPASS_CLAUSE_2" : "LIBRARY_CELL_INCOMPLETE",
    frozen_machine_read: frozen,
    candidates,
    original_tape_bounds: originalBounds,
    selected_target_cents: frozen.target_cents ?? null,
    target_changed: false,
  };
  const weightedDiscount = roundCent((gridDiscount * recovery) + (dipDepth * (1 - recovery)));
  const libraryFloor = ask - Math.max(1, weightedDiscount);
  const lawfulLibraryFloor = v52h.lawfulCent(libraryFloor) && libraryFloor < ask;
  const belowShownRange = Number.isInteger(originalBounds?.min_cents) && lawfulLibraryFloor && libraryFloor < originalBounds.min_cents;
  const cap = pairCap(inputs);
  const capAccommodates = !Number.isInteger(cap) || libraryFloor <= cap;
  const useLibrary = lawfulLibraryFloor && capAccommodates && (belowShownRange || frozen.authorized !== true);
  return {
    clause: "CLAUSE_3_LIBRARY_BACKED_LEVEL_EVIDENCE",
    applicable: useLibrary,
    frozen_clause_2_read_passed: readExists,
    evidence_authority: useLibrary ? "VALIDATED_LIBRARY" : frozen.authorized ? "POST_ONSET_TAPE" : "NONE",
    reason: useLibrary ? (belowShownRange ? "LIBRARY_LICENSES_LEVEL_BELOW_GAME_SHOWN_RANGE" : "LIBRARY_LICENSES_LEVEL_WHERE_TAPE_AUTHORITY_ABSENT")
      : !lawfulLibraryFloor ? "LIBRARY_LEVEL_NOT_LAWFUL_BELOW_CURRENT_TOUCH"
        : !capAccommodates ? "LIBRARY_FLOOR_INCOMPATIBLE_WITH_CLAUSE_6_PAIR_SUM"
          : "TAPE_AUTHORITY_RETAINED_LIBRARY_NOT_BELOW_SHOWN_RANGE",
    weighting_law: "ROUND(G_GRID_DISCOUNT*G3_RECOVERY + G3_MEDIAN_DIP_DEPTH*(1-G3_RECOVERY))",
    arithmetic: `${gridDiscount}*${recovery}+${dipDepth}*${1 - recovery}=${weightedDiscount};${ask}-${weightedDiscount}=${libraryFloor}`,
    frozen_machine_read: frozen,
    candidates,
    prior_values: {
      G_GRID_discount_cents: gridDiscount,
      G3_dip_depth_median_cents: dipDepth,
      G3_recovery_within_60min: recovery,
      weighted_discount_cents: weightedDiscount,
    },
    prior_provenance: candidates.provenance,
    current_touch_ask_cents: ask,
    original_tape_bounds: originalBounds,
    library_supported_floor_cents: lawfulLibraryFloor ? libraryFloor : null,
    below_shown_range: belowShownRange,
    clause_6_cap_cents: Number.isInteger(cap) ? cap : null,
    selected_target_cents: useLibrary ? libraryFloor : frozen.target_cents ?? null,
    target_changed: useLibrary && libraryFloor !== frozen.target_cents,
    library_floor_is_hard_lower_bound: true,
  };
}

function gateDecision(inputs, incumbent) {
  const clauses = normalizedClauses(inputs.clauses);
  if (!clauses.library_backed_level_evidence) return v52h.gateDecision({ ...inputs, clauses }, incumbent);
  const selection = libraryEvidenceSelection(inputs.birthLicense, incumbent, inputs);
  if (!selection.applicable) {
    const frozen = v52h.gateDecision({ ...inputs, clauses: { ...clauses, library_backed_level_evidence: false } }, incumbent);
    const stamped = { ...selection, final_licensed_target_cents: frozen.target_cents ?? null };
    return {
      ...frozen,
      birth_license: frozen.birth_license ? { ...frozen.birth_license, level: { ...frozen.birth_license.level, library_backed_level_evidence: stamped } } : null,
      library_backed_level_evidence: stamped,
    };
  }
  const target = selection.selected_target_cents;
  const evidence = inputs.birthLicense?.level?.machine_read_evidence ?? {};
  const unionBounds = {
    min_cents: Math.min(target, Number.isInteger(selection.original_tape_bounds?.min_cents) ? selection.original_tape_bounds.min_cents : target),
    max_cents: Math.max(target, Number.isInteger(selection.original_tape_bounds?.max_cents) ? selection.original_tape_bounds.max_cents : target),
  };
  const adjustedLicense = {
    ...inputs.birthLicense,
    level: {
      ...inputs.birthLicense?.level,
      proposed_target_cents: target,
      machine_read_evidence: {
        ...evidence,
        post_onset_observation_bounds: unionBounds,
        tape_only_post_onset_observation_bounds: selection.original_tape_bounds,
        licensing_evidence_bounds_include_validated_library_floor: true,
      },
      library_backed_level_evidence: selection,
    },
  };
  const adjustedIncumbent = {
    ...incumbent,
    target_cents: target,
    reason: "V43_LIBRARY_BACKED_LEVEL_EVIDENCE",
    placement: { ...(incumbent?.placement ?? {}), target_cents: target, authority: "V43_LIBRARY_BACKED_LEVEL_EVIDENCE" },
  };
  const decision = v52h.gateDecision({ ...inputs, clauses: { ...clauses, library_backed_level_evidence: false }, birthLicense: adjustedLicense }, adjustedIncumbent);
  if (v52h.lawfulCent(decision.target_cents) && decision.target_cents < selection.library_supported_floor_cents) throw new Error("V52k licensed below library-supported floor");
  const stamped = { ...selection, final_licensed_target_cents: decision.target_cents ?? null };
  return {
    ...decision,
    birth_license: decision.birth_license ? {
      ...decision.birth_license,
      level: { ...decision.birth_license.level, library_backed_level_evidence: stamped },
    } : null,
    library_backed_level_evidence: stamped,
  };
}

function decideReceipt(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const atomic = v52h.decideReceipt({ ...inputs, clauses: { ...clauses, library_backed_level_evidence: false } });
  return { ...atomic, decision: gateDecision({ ...inputs, clauses }, atomic.decision.unguarded_decision ?? atomic.decision), library_backed_level_evidence_enabled: Boolean(clauses.library_backed_level_evidence) };
}
function decide(inputs) {
  const clauses = normalizedClauses(inputs.clauses);
  const incumbent = v52h.decide({ ...inputs, clauses: { ...clauses, library_backed_level_evidence: false } });
  return gateDecision({ ...inputs, clauses }, incumbent.unguarded_decision ?? incumbent);
}

module.exports = { ...v52h, configurePalantir, requiredValidationStore, candidateProvenance, normalizedClauses, priceRegion, libraryCandidates, continuousConsultation, pairCap, libraryEvidenceSelection, gateDecision, decideReceipt, decide };
