# v6 exit-table deployment swap plan (zone-aware R) — 2026-05-27

**Status: STAGED, NOT DEPLOYED. Bot untouched. Awaiting operator approval.**

v6 exit parquets built from the **zone-aware** R selection (`{cat}_cell_bands_zone_aware_2026-05-27.md`), in the deployed schema (`price_low, price_high, band_exit_X`), **DISABLE→HOLD** encoded (loader-safe — every `band_exit_X` is `HOLD` or an int; verified, so `_load_exit_table` cannot crash).

Staged on the VPS as **`{cat}_adaptive_exit_bands_v6.parquet`** (distinct `_v6` name — the live `{cat}_adaptive_exit_bands.parquet` the bot reads is **untouched**).

## ⚠️ Decision point before deploy — DISABLE→HOLD is not a true disable
The exit parquet governs the **exit side only**. Entry is still driven by `per_regime_offsets_v2.csv` (unchanged). So a band encoded `HOLD` because it was DISABLE does **not** stop the bot from *entering* that cell — it makes the bot **enter then ride to settle** (no exit). For genuinely negative cells that is a loss:

| cat | v6 total (zone R on active + ride-to-settle on disabled) | zone-aware active-only $ | cost of DISABLE→HOLD |
|---|---|---|---|
| ATP_MAIN | 865.7 | 1235.4 | ≈ −370 |
| WTA_MAIN | 970.0 | 1227.4 | ≈ −257 |
| ATP_CHALL | 1495.0 | 1805.5 | ≈ −311 |
| **WTA_CHALL** | **−72.0** | 93.5 | ≈ −165 (**v6 goes net-negative**) |

(raw_max, in-sample — directional, not a live forecast.)

**⇒ Deploying v6 exit-only as-is would ride disabled-cell losers to settlement.** WTA_CHALL becomes net-negative. Three ways to handle the disabled bands (operator picks):
- **(A) Entry-path skip (correct fix):** implement the per-band entry skip from `live_v4_gaps_2026-05-27.md` so the bot doesn't enter disabled cells at all. Code change (CC).
- **(B) Protective exit on disabled bands:** instead of HOLD, keep disabled bands at a shallow protective R (e.g., their max-EV R or the old deployed R) so losers are exited, not ridden. Parquet-only; I can rebuild.
- **(C) Accept ride-to-settle** on disabled cells (NOT recommended, esp. WTA_CHALL).

Until this is decided, **do not deploy WTA_CHALL v6**; ATP_* / WTA_MAIN are positive but still carry the disabled-cell drag.

## Swap mechanics (from `exit_swap_diff_2026-05-27.md` Part C)
- `_load_exit_table` is **init-only** → a file swap has no effect until restart.
- Open positions **keep their entry-time R** (reconcile adopts existing resting sells); v6 affects **new entries only**.
- DISABLE→HOLD encoding avoids the loader `ValueError` crash a literal `"DISABLE"` would cause.

## Safe deploy sequence (when approved)
1. Pick disabled-band handling (A/B/C above); if (B), I rebuild the v6 parquets accordingly.
2. On the VPS, in a **no-placement window** (no event within its `placement_minute`):
   - Back up live: `cp {cat}_adaptive_exit_bands.parquet {cat}_adaptive_exit_bands.bak_pre_v6.parquet`
   - Promote: `cp {cat}_adaptive_exit_bands_v6.parquet {cat}_adaptive_exit_bands.parquet`
   - Graceful restart live_v4 (C-c, wait, restart on `deploy_v5_live.json`).
3. Verify: `EXIT_TABLE_LOADED` band counts match v6 (31/28/33/7), 0 tracebacks, reconcile 0 orphans, existing resting sells preserved.
4. **Instant rollback:** `cp …bak_pre_v6.parquet …adaptive_exit_bands.parquet` + restart.

## Caveats (carried)
- v6 R from **raw_max** (optimistic) vs deployed **size_qual_max_250** — exit-only swap may over-assume capture realizability at depth.
- Per-band R is **in-sample** best/zone-aware — overfit risk.

*Staged, uncommitted parquets. No swap, no restart, bot untouched. Operator decides disabled-band handling + swap timing.*
