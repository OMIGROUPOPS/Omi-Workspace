# THE WEEK'S STANDING ORDER (2026-07-05 → 2026-07-12) — operator verbatim

> CC — THE WEEK'S STANDING ORDER (config holds, analysis attacks):
> CONFIG: holds one week. The riser revision accumulates fv_observe evidence (target ~100+
> FV-graded riser legs, then the Plex bounce at full n). No tuning changes. Defects are
> exempt from the hold — any zero-tolerance violation or new class patches same-day through
> the gate, as established.
> ANALYSIS: full offense, nightly. Every night, pushed to git:
> 1. The ledger + causal chains + EARNED/GIFT stamps + exchange-truth P&L (the standing
>    pass, as built).
> 2. THE LEAK DECOMPOSITION — the week's central question: why aren't more pairs completing
>    at ≤97 when the faller mechanism demonstrably manufactures discounts? For every pair
>    that completed >97 (and every half-pair whose bound couldn't be met): decompose the
>    excess-over-97 into its components — riser concession (the leg-1 fill vs what a deeper
>    riser post would have paid, per the depth replay's retention data) / faller depth
>    shortfall (our faller level vs the dip the tape actually delivered) / completion timing
>    (did the bound arrive after the fader's dip had passed) — per category, cents
>    attributed per component. Cumulative across the week: the ranked table of where the
>    combined leaks, with dollar weights.
> 3. The repriceable counter + fv_observe accumulation status (the two evidence streams
>    building toward their gates).
> END OF WEEK deliverables: (a) the leak decomposition across the full sample — the
> evidenced answer to "what stands between us and ≤97 completions at volume"; (b) the riser
> Plex bounce at full n; (c) the pre-T-4h exploitation spec — the ITF early-window finding
> (≤97 achievable 90-96% pre-T-4h, JOINT peak 80% at T-4h→T-2h) turned into a concrete
> posting-window proposal, since the confirmed thesis has never been exploited.
> Vault: this standing order verbatim, so every session this week opens knowing the box
> holds still precisely SO the analysis can aim.

## Operational state at issue (2026-07-05 ~00:30 ET)

- **Held config** = build `aba83af` (PID at deploy 3039371), flags: per_cat_depth,
  leg2_reshuffle(97), premarket_walk_cap, match_live_grace_kill, latch_tape_override,
  reaim_on_sibling_arrival, repost_sibling_on_boot, repost_hold_same_price,
  marketable_stale_pin_exempt. riser_post UNCHANGED (the revision waits for its gate).
- Monitor: tmux `live_monitor`, 10-min cycles, LIVE_STATUS + jsonl pushed on change.
- Nightly pass: see NIGHTLY_PASS.md. Leak decomposer: `audit/leak_decomposition.py`,
  cumulative `week_leak.jsonl` (rides the monitor's auto-commit).
- fv_observe riser accumulation at issue: **18 / ~100 target**.
- Night-1 leak headline (21 events): **half_timing dominates — 8 events, ~131¢: the
  fader's dip to ≤bound passed BEFORE leg-1 filled (the bound didn't exist yet).**
  Sequential completion structurally forfeits the early fader divot — the direct bridge
  to deliverable (c), the pre-T-4h posting-window spec.
