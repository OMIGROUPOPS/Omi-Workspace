"use strict";

// One adapter for the existing C-ONE-TRUTH / frozen-Git consultation path.
// It never discovers files and never falls back.  The builder supplies bytes
// read through its existing gitShow loader; this module validates that every
// consumed asset came from MACHINE_PALANTIR.store_CLEAN and has an allowed
// status before exposing the compact N2/N4/N5 consultation surfaces.

const REQUIRED = Object.freeze(["P1", "P2", "P4", "P6", "P11", "P12", "P13", "P14"]);
const FORBIDDEN_INVENTORIES = Object.freeze(["inventory_UNVALIDATED", "inventory_QUARANTINED", "inventory_SUPERSEDED"]);

function assert(condition, message) { if (!condition) throw new Error(message); }
function validatedStatus(status) { return typeof status === "string" && (status.startsWith("VALIDATED") || status.startsWith("VALID-NARROW")); }

function makeCleanStore(manifest, assets) {
  assert(manifest?.LABEL === "MACHINE_PALANTIR", "wrong palantir manifest");
  assert(Array.isArray(manifest.store_CLEAN), "palantir CLEAN store absent");
  const clean = new Map(manifest.store_CLEAN.map((entry) => [entry.id, entry]));
  const loaded = {};
  for (const id of REQUIRED) {
    const entry = clean.get(id);
    assert(entry, `required CLEAN asset absent ${id}`);
    assert(validatedStatus(entry.status), `non-validated CLEAN status refused ${id}: ${entry.status}`);
    const asset = assets[id];
    assert(asset && asset.data && Array.isArray(asset.sources) && asset.sources.length > 0, `asset bytes absent ${id}`);
    assert(asset.sources.every((source) => source.inventory === "store_CLEAN" && /^[0-9a-f]{40}$/.test(source.commit) && /^[0-9a-f]{64}$/.test(source.sha256)), `asset provenance invalid ${id}`);
    loaded[id] = Object.freeze({ entry: Object.freeze({ ...entry }), data: Object.freeze(asset.data), sources: Object.freeze(asset.sources.map((source) => Object.freeze({ ...source }))) });
  }
  for (const inventory of FORBIDDEN_INVENTORIES) {
    const forbiddenIds = new Set((manifest[inventory] || []).map((entry) => entry.id));
    assert(!Object.keys(loaded).some((id) => forbiddenIds.has(id)), `${inventory} asset loaded`);
  }
  return Object.freeze({
    label: manifest.LABEL,
    manifest_commit: assets.__manifest.commit,
    manifest_sha256: assets.__manifest.sha256,
    loaded: Object.freeze(loaded),
    boot_assertion: Object.freeze({
      passed: true,
      required_ids: REQUIRED,
      loaded_ids: Object.keys(loaded).sort(),
      source_inventory: "store_CLEAN",
      unvalidated_loaded: 0,
      quarantined_loaded: 0,
      superseded_loaded: 0,
      fallback_loads: 0,
    }),
  });
}

module.exports = { REQUIRED, FORBIDDEN_INVENTORIES, validatedStatus, makeCleanStore };
