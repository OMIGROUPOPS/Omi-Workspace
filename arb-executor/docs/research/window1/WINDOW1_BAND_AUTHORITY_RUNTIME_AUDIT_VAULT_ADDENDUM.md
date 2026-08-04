# Vault Addendum - Band Authority Runtime Audit

Date: 2026-08-04

The potential spike-map runtime defect is **not active**. The last executed
`live_v4` process used source blob `f1857199` and config blob `d36e9e76`; the
config's line 33 selects the sealed gated-optima runtime parquets. The
spike-map string inside `_load_exit_table` is only the missing-key fallback.
`exit_rule_for` consumes the table already loaded from the selected directory.

The engine remains stopped. A read-only VPS census found zero `live_v4`
processes. It also found pre-existing uncommitted source/config changes on the
stopped VPS; the config still selects gated optima, and all four sealed runtime
parquets match their frozen hashes.

No conditional spike-map fill reclassification was performed because the
runtime did not select spike-map. Actual-versus-sealed difference is zero under
the proven binding because they are the same table.

The latent fallback should still be hardened, after operator approval, by
changing the default directory on one line from `spike_volatility_map/` to
`exit_surface_gated_optima/`. That proposal was not applied. The loader reads
sealed parquets; the provenance CSVs cannot be substituted literally without a
schema/loader change.
