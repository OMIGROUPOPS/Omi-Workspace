# Band Authority Runtime Audit

## Ruling

**The spike map is not the selected live exit surface.** There is currently no
running `live_v4` process. The last executed process, and the presently stopped
installation if booted by the frozen command, resolve
`data/durable/exit_surface_gated_optima/` from the explicit production config.

The apparent spike-map load at `_load_exit_table` is the second argument of
`dict.get`: it is reached only when `exit_table_dir` is absent from the loaded
config. The production config contains that key.

## File:line receipt - last process that actually ran

Immutable source: `fd4abec0f3d464634ee1d61ac02f6c977c41fb3c`.

1. `live_v4.py:305-308` selects `config/deploy_v5_live.json` by default and
   permits an explicit `LIVE_V4_CONFIG` override.
2. `live_v4.py:4704-4737` is `_load_exit_table`.
3. `live_v4.py:4712` contains the spike-map **missing-key fallback**.
4. `deploy_v5_live.json:33` explicitly selects
   `data/durable/exit_surface_gated_optima/`, so the fallback is not selected.
5. `live_v4.py:5046-5059` is `exit_rule_for`, which reads the cached table
   populated by `_load_exit_table`.

The stopped-engine operational receipt bound the exact executed source SHA-256
`834b9e04...f1d54` and config SHA-256 `3d5b07af...bed2a1`. Recomputing the Git
objects at `fd4abec0` reproduces both SHA-256 values exactly. The captured
process command was `python3 -u live_v4.py`; it did not name an alternate
config.

## Read-only VPS census - 2026-08-04 16:21:21 UTC

- Process count: `0`.
- VPS HEAD: `1fafcebc28c30f16bcefad6c41eee076d8e2c016`.
- The stopped VPS has uncommitted changes to `live_v4.py` and
  `deploy_v5_live.json`; this audit did not create or modify them.
- The installed config still selects gated optima at line 33.
- Installed source has `_load_exit_table` at line 5074, the inactive spike
  fallback at line 5082, and `exit_rule_for` at line 5416.
- All four installed gated-optima parquets match the seal byte-for-byte.

Because the engine is stopped, it consumes no surface "today." The last engine
that made exit decisions consumed gated optima. The currently installed files
would also resolve gated optima if booted by the frozen no-override command.

## Conditional spike-map comparison

The requested antecedent is false, so a spike-vs-seal fill reclassification was
not run. Under the proven binding, actual lookup and sealed lookup are the same
lookup; therefore the number of fills whose exit differs from the sealed
surface is identically zero for that binding. This audit does not manufacture a
separate post-June-15 historical fill census after the conditional failed.

## One-line hardening proposal - not applied

```diff
- rel_dir = self.config.get("exit_table_dir", "data/durable/spike_volatility_map/")
+ rel_dir = self.config.get("exit_table_dir", "data/durable/exit_surface_gated_optima/")
```

That line removes the latent superseded fallback without changing the present
configured behavior. It is a proposal only. No live source, config, process,
cron, order, or position was mutated.

The wording "route to the sealed CSVs" needs one correction: the CSVs are the
sealed provenance/build inputs, but this loader consumes parquet columns
`price_low`, `price_high`, and `band_exit_X`. The correct one-line path target
is the sealed **parquet directory**. Loading the CSVs literally requires a
different loader and is not a one-line repair.
