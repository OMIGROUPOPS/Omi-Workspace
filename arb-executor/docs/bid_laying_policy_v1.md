# Bid-Laying Policy v1 — Deployable Strategy Specification

**Date:** 2026-05-23
**Status:** Canonical. This is the deployable bid-placement specification for the bot.
**Synthesis of:** T42 spike-volatility atlas (locked) + Path B v1/v2/v3 arc (T43/T44/T45) + Plex Premarket Execution Rounds 5/6 + operator policy thesis (SIMONS_MODE).
**Source lookup table:** `docs/policy/per_regime_offsets_v1.csv` (36 entries, git-tracked).

---

## Section 1 — Scope and authority

This document defines the bot's bid placement behavior for **atlas-qualifying paired tennis events**.

- The atlas (T42, locked at commit `d99c6e9`) is the **strategy floor**: T-20m taker entry + per-cell exit rule, **+8.70% blended ROI measured** across the corpus.
- This spec **ADDS** entry-side maker placement on top of the locked atlas. It is **strictly dominant by construction**: every placement either improves on the T-20m taker entry (fills earlier/cheaper) or, on a miss, falls back to the exact atlas baseline entry. The strategy therefore can never underperform the +8.70% floor.
- The atlas owns the exit side and the realized-PnL measurement. This spec owns **entry-side fill mechanics only**. Nothing here re-opens the exit rule or the cell model.

---

## Section 2 — Strategy summary

For every atlas-qualifying paired event, at **T-4h** (or as soon as the market opens premarket, whichever is later), post maker bids on **BOTH legs simultaneously**. Per leg: `bid_price = T-20m_anchor_estimate − offset`, where `offset` is determined by the leg's anchor regime (in cents) per the per-regime table in Section 3. If the target bid is at or above the current ask at posting, execute as a **MARKETABLE TAKER** (lift the ask, pay the current ask). Otherwise post as a **RESTING MAKER** limit buy and let premarket drift work. If the bid is still unfilled at **T-20m**, fall back to a **taker** at the current ask — this is the atlas baseline entry. Apply the locked atlas per-cell exit rule from the actual entry point forward through settlement.

---

## Section 3 — Per-regime offset table (deployable)

> **SUPERSEDED by v2 (2026-05-23, Path B v4 / ROADMAP T47).** The deployable table is now
> `docs/policy/per_regime_offsets_v2.csv` — offsets re-optimized on net realized PnL rather than
> v1's entry-capture objective, lifting blended net ROI from 10.70% to 11.73% (+1.024pp). See
> Section 12. The v1 offsets below are retained for provenance.

The full 36-entry table (4 categories × 9 anchor regimes) is read at bot startup from
`docs/policy/per_regime_offsets_v1.csv` (v1; see Section 12 for the v2 successor). Schema:

```
category, anchor_regime, anchor_low_cents, anchor_high_cents,
placement_minute, bid_offset_cents, expected_fill_rate, expected_improvement_cents
```

Each row is the `(placement_minute, bid_offset_cents)` pair that maximized
`expected_improvement_cents` at v1 hindsight for that `(category, anchor_regime)` stratum.

The per-regime structure, stated in prose so this spec is self-contained:

- **Deep underdogs (r05_14):** 2–3¢ offset, posted at T-240 (WTA_CHALL at T-180). Underdog books drift *down toward* the anchor, so only a small offset at high fill captures edge; large offsets barely fill. Expected improvement ~1.0–1.2¢.
- **Mild underdogs (r15_24):** 5¢ offset at T-240 (WTA_CHALL at T-180). Expected improvement ~1.2–1.7¢.
- **Mid-low bands (r25_44):** mixed by category — 2–15¢ offsets at T-120/T-180/T-240. ATP tends to small offsets at high fill (3–8¢); WTA_CHALL favors 10¢ at T-120. Expected improvement ~1.2–2.3¢.
- **Coin flip (r45_54):** 15¢ offset at T-90/T-180 (WTA_CHALL 10¢ at T-120). The drift gradient turns from down-toward to up-away here. Expected improvement ~1.8–3.3¢.
- **Mild favorites (r55_64):** 3–15¢ offsets at T-90/T-180/T-240 (ATP_CHALL 3¢ at high fill; others 15¢). Expected improvement ~1.7–2.3¢.
- **Strong favorites (r65_74):** 15¢ offset at T-120/T-180/T-240. Expected improvement ~2.1–3.3¢.
- **Heavy favorites (r75_94):** 15¢ offset at T-90/T-180/T-240. Favorite books drift *up*, so a 15¢-below bid sits above the early mid and gets swept as the market climbs — this band captures the corpus's largest entry edge, ~4.4–7.0¢.

The dominant pattern is a clean **favorite/underdog asymmetry driven by the Scope A T4 drift gradient**: expected improvement rises monotonically with anchor regime, and the optimal offset rises with it (2–3¢ for deep underdogs → 15¢ for heavy favorites). Placement timing is a weak second-order lever — earlier placement (T-4h/T-2h) weakly dominates, and almost every regime's optimum sits at T-240 or T-180.

---

## Section 4 — Execution branch at posting

For each leg, at its `placement_minute`:

1. Compute `target_bid = anchor_estimate − regime_offset`.
2. Clamp `target_bid` to **≥ 1¢**.
3. Read `current yes_ask_close`.
4. If `target_bid ≥ yes_ask_close`: **MARKETABLE TAKER** — submit a taker buy at the current ask. Pay the taker fee. Done.
5. Else: post as a **RESTING MAKER LIMIT BUY** at `target_bid`.

---

## Section 5 — Resting maker bid management (T-4h → T-20m)

While a bid is resting:

- Monitor **Round 4's two-of-four composite detector** (volume burst + bilateral taker flow + BBO velocity + distortion spike).
- If the detector fires **AND** own bid is unfilled **AND** `current_ask ≤ target_bid + 5¢`: **CROSS IMMEDIATELY** (Round 6 Stage 3 velocity override). Lock the entry before the burst completes.
- If the detector fires **AND** `current_ask > target_bid + 5¢`: the spread is pathological — **do NOT cross**. Let the bid sit and accept miss risk.
- If the bid fills naturally at any minute: done. Hold for atlas exit-rule application.

---

## Section 6 — Taker fallback at T-20m

If the resting bid is still unfilled at T-20m:

- Cross as a **taker** at the current ask.
- This **IS** the atlas baseline entry — the entry on which the +8.70% blended ROI was measured.
- By construction, the strategy never underperforms the baseline floor.

---

## Section 7 — Atlas exit-rule application

From the **actual entry point** forward (whether marketable taker, resting fill, or T-20m fallback taker):

- Look up N's cell rule from `data/durable/spike_volatility_map/{category}_descriptive_1c.parquet`, with `cell_id = round(anchor_price × 100)`.
- If the rule is **"exit at +X cents"**: monitor the post-entry trajectory for `entry_price + X` with ≥250ct depth. If reached, exit there.
- If the rule is **"hold to settlement"**: hold to settlement; realize `+(99 − entry)` on a winner or `−(entry − 1)` on a loser.

---

## Section 8 — Expected economics (with realism caveats)

- **Atlas baseline floor** (T-20m taker only): **$6,158 on $70,813 capital = 8.70% blended ROI** (measured).
- **Per-regime maker placement** (this spec, pre-realism): **$8,098 on $66,902 capital = 12.11% blended ROI** (T45).
- **Post-realism deployable estimate:** apply a 0.5–0.7× B25 discount on the lift → **blended ROI ~10–11%** (range $7,100–$7,500 PnL on the corpus at 10ct sizing).
- **Capital deployed per trade:** `anchor_price × 10ct` (10ct sizing convention from T42).
- **Per-execution-mode ROI:** marketable_taker **27.8%**, maker_resting **20.1%**, miss_fallback **9.2%** — the 9.2% IS the atlas baseline floor, so the worst execution mode is still the floor.

---

## Section 9 — Deployment philosophy (cross-ref SIMONS_MODE)

- **Trade ALL 90 cells per category.** Volume is the constraint, not selectivity. (LESSONS E32 + SIMONS_MODE Section 1.)
- **Both legs of every paired event** get this treatment (LESSONS B23).
- The capital constraint is **depth** (LESSONS F33), not bankroll (operator-stated).
- The bot is **mechanical**: it posts per the table, branches at posting, and holds to the atlas exit. No active intervention, no per-trade judgment calls.

---

## Section 10 — What this spec does NOT cover

- **Strategy bands not in the atlas** — out of scope; the atlas is the strategy.
- **Singleton-leg events** (~17% of corpus) — this spec handles paired events; singletons get the atlas baseline only.
- **WTA Challenger FV gap** — unresolved, downstream T-item.
- **Bug 4 settlement-mechanics** — separate execution-lock item.

---

## Section 11 — Open downstream work

- **Path C: drift predictor analysis** — could conditionally adjust the offset by per-event observable features, possibly lifting the fill rate from 28.4% blended toward 40%+. Plex Round 7 framing in flight; App task drafts after.
- **Layer B v2 producer** — tick-level fill-realism replacement for the minute-cadence simulator (T36, not yet built).
- **Bug 4 implementation** — settlement-state mechanics correction.
- **Paper-mode integration test suite.**

## Section 12 — v4 update: net-PnL-optimized per-cell offsets (2026-05-23, ROADMAP T47)

**This section supersedes the Section 3 / v1 offset table.** Path B v4 re-swept the
(placement_minute × bid_offset) grid per (category × anchor_regime) cell, optimizing **net realized
PnL through the full strategy** (entry capture + atlas X exit + miss-fallback − 1¢ taker fee) rather
than v1's entry-side `fill_rate × offset`. The deployable table is now
**`docs/policy/per_regime_offsets_v2.csv`** (same schema, with `expected_net_roi_pct`).

**Result:** blended **net ROI 11.73% vs v3's 10.70% (+1.024pp; +1.22pp vs canonical v3), on lower
capital** — pre-realism (apply the B25 0.5–0.7× discount for deploy-time expectations). Analytical
commit `c90985b`; finding doc `docs/analysis/premarket_dynamics_v1/path_b_v4_findings.md`; per-cell
detail `path_b_v4_cell_optimum.csv`.

**The load-bearing change — offsets are now SHALLOW.** v4's net-PnL-optimal offsets are 1–3¢ on
27 of 36 cells (vs v1's deep 15¢ on favorites). Mechanism: the atlas exit realizes a fixed +X above
entry regardless of how deep the entry, so a deeper offset adds **no exit upside** — it only raises
the miss rate (→ fallback to the T-20m anchor, zero improvement). A shallow bid fills reliably,
captures a small consistent entry discount, and deploys less capital. v1's "ask for a big discount on
favorites" was optimizing the wrong objective once the fixed-profit exit caps the payoff. (This is
also why the Path C drift-predictor refinements — Phase 1–3, held unpromoted — could not beat v3: the
exit cap binds against feature-conditional *entry* tweaks; the productive lever was simply re-setting
the static offset on the correct objective.)

**Deployment notes / open design choices:**
- v2 offsets maximize net **dollars** per cell (atlas doctrine: throughput is the constraint, not
  capital). 3 deep-underdog cells (ATP_MAIN r05_14, WTA_CHALL r05_14/r15_24) thereby trade a little
  ROI for more total $; switch those to a net-ROI argmax if capital becomes the binding constraint.
- The v4 measurement used a ±5min ask fallback at the placement minute (lifts the v3-repro baseline
  ~1.7% vs the canonical exact-ask v3; the +1.024pp improvement is apples-to-apples within v4).
- Execution branch (Section 4), resting-bid management (Section 5), T-20m taker fallback (Section 6),
  and atlas exit application (Section 7) are unchanged — only the per-cell offset/placement table is
  re-optimized.
