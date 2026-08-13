"use strict";

// V52i keeps the canonical N9 CLEAN store byte-for-byte and appends exactly
// two iteration-local assets under validation.  This adapter cannot discover
// files or promote any other UNVALIDATED/QUARANTINED/SUPERSEDED entry.

const CANDIDATE_IDS = Object.freeze(["G_GRID_LEVEL_DISCOUNT", "G3_DIP_RECOVERY_GRADIENT"]);

function assert(condition, message) { if (!condition) throw new Error(message); }

function makeUnderValidationStore(cleanStore, candidates) {
  assert(cleanStore?.boot_assertion?.passed, "V52i canonical CLEAN store absent");
  assert(cleanStore.boot_assertion.unvalidated_loaded === 0, "V52i canonical CLEAN store already contains unvalidated assets");
  assert(Object.keys(candidates ?? {}).sort().join("|") === [...CANDIDATE_IDS].sort().join("|"), "V52i candidate identity mismatch");
  const loaded = { ...cleanStore.loaded };
  for (const id of CANDIDATE_IDS) {
    const asset = candidates[id];
    assert(asset?.entry?.id === id && asset.entry.status === "UNDER-VALIDATION_V52I", `V52i candidate status invalid ${id}`);
    assert(asset.data && Array.isArray(asset.sources) && asset.sources.length > 0, `V52i candidate bytes absent ${id}`);
    assert(asset.sources.every((source) => source.inventory === "inventory_UNDER_VALIDATION_V52I" && /^[0-9a-f]{40}$/.test(source.commit) && /^[0-9a-f]{64}$/.test(source.sha256)), `V52i candidate provenance invalid ${id}`);
    loaded[id] = Object.freeze({ entry: Object.freeze({ ...asset.entry }), data: Object.freeze(asset.data), sources: Object.freeze(asset.sources.map((source) => Object.freeze({ ...source }))) });
  }
  return Object.freeze({
    ...cleanStore,
    loaded: Object.freeze(loaded),
    boot_assertion: Object.freeze({
      ...cleanStore.boot_assertion,
      passed: true,
      canonical_clean_store_unchanged: true,
      source_inventory: "store_CLEAN_PLUS_EXACT_V52I_UNDER_VALIDATION_ALIASES",
      under_validation_loaded: CANDIDATE_IDS.length,
      under_validation_loaded_ids: CANDIDATE_IDS,
      unvalidated_loaded: 0,
      candidate_fallback_loads: 0,
      rejected_inventory_classes: ["inventory_UNVALIDATED_EXCEPT_EXACT_OPERATOR_BOUND_ALIASES", "inventory_QUARANTINED", "inventory_SUPERSEDED"],
    }),
  });
}

module.exports = { CANDIDATE_IDS, makeUnderValidationStore };
