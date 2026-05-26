# live_v4.py entry-path audit (PID 3191329, deploy_v5_live.json) — 2026-05-27

Read-only inspection of the running build. No code changes.

## How the bot decides WHEN to enter
- Entry is driven by **`routing_tick`** (re-evaluates each event every tick) + **`on_bbo_update`** (manages the resting bid). For each leg it looks up the **anchor regime** of the current price and reads `(placement_minute, bid_offset_cents)` from the entry table.
- **Placement gate:** it does nothing until `time_to_start <= placement_minute*60` — i.e. it posts at **T-placement_minute** for that leg's regime (earliest T-240m; table values 60/90/120/180/240m). Before T-4h it doesn't even evaluate (`V4_MAX_PLACEMENT_SEC`).
- So: **premarket maker bid at a per-regime scheduled minute, with a T-20m taker fallback.** Both mechanisms, in sequence.

## Does it post maker bids in [T-4h, T-20m]? At what price?
- **Yes.** At its regime's `placement_minute`, it computes `target_bid = current_price − bid_offset_cents` and:
  - if `time_to_start <= T-20m` → **miss_fallback** (taker at ask),
  - elif `target_bid >= ask` (or round5 force) → **marketable_taker** (lift ask, 1c fee),
  - else → **resting_maker** limit buy at `target_bid`, managed to T-20m.
- The discount = **`bid_offset_cents`** (1–7c in the v2 table), **per (category, anchor_regime)**.

## Per-band entry discount + posting bucket (B1–B4)?
- **Discount: per-REGIME only** — `bid_offset_cents` keyed on the 9 coarse regimes (r05_14 … r85_94 = 10c bands), **not** the fine cell-bands from the new analysis, and **not** stored in the exit parquet.
- **Posting time: a single `placement_minute` per regime** (continuous minutes-before-start), **not** a B1–B4 bucket. There is no bucket concept in the code.
- ⇒ **No support for per-band discount or B1–B4 post_start.**

## Per-band tail policy (skip vs taker fallback)?
- **No.** The T-20m fallback is **hard-coded for every unfilled resting bid** (`_v4_manage_resting_inner`, STEP 6, `V4_T20M_SEC`): if still unfilled at T-20m it **always crosses as a taker at the ask** ("the atlas baseline entry"). There is **no skip option** and **no per-band policy field** anywhere.

## What it reads from `{cat}_adaptive_exit_bands.parquet` vs config json vs entry CSV
- **Exit parquet** (`_load_exit_table`): reads **only `price_low`, `price_high`, `band_exit_X`**. Expands each band to its 1c cells → `{cell_id → (band_x|None, "exit"|"hold")}`. `band_exit_X == "HOLD"` → hold-to-settle; else exit at `fill_price + band_x`. **No entry fields are read from this parquet.**
- **config json** (`deploy_v5_live.json`): `sizing` (5ct), `categories_enabled`, `entry_table_path`, `exit_table_dir`, `min_depth_for_exit_realization`, feature flags. No per-band entry params.
- **entry CSV** (`per_regime_offsets_v2.csv`): `(placement_minute, bid_offset_cents, expected_fill_rate, expected_net_roi_pct)` per (category, regime). 36 rows = 4 cat × 9 regime.

## How it handles "no fill by T-20m"
- **Always taker fallback:** at T-20m it cancels the resting bid and crosses at the current ask (`entry_mode = miss_fallback`, `paid_taker_fee = True`, fires once). This is the atlas-baseline entry. **Skip is not implemented.**

## Bottom line
The bot supports **per-band exit_R** (swappable via the exit parquet) but **NOT** per-band `discount`, per-band `post_start` (B1–B4), or per-band `tail_policy` (skip vs fallback). Entry discount/timing are per-**regime** (9 bands) in a separate CSV; the tail is hard-coded taker fallback. ⇒ Part 2 takes the **gaps path** (see `live_v4_gaps_2026-05-27.md`).

*Read-only. No code changes, no config swap, no restart.*
