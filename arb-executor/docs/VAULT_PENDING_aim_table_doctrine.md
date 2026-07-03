# VAULT PENDING — AIM-TABLE doctrine (merge into canonical §4 on `blend/agent-derivation`)

> Staged on the deploy branch `blend/kalshi-occ-fallback` (code lives here). The canonical Vault
> forbids re-growing this branch's stub, so this entry is staged for the next agent-derivation
> merge. Source: 2026-07-03 entry-side patch dispatch (`.claude/aim_dispatch_20260703/`).

## §4x — AIM-TABLE doctrine (placement aims at the dip; FV is the yardstick, not the target)

**Doctrine line:** *Placement aims at the DIP below FV — the discount the market pays a correctly-placed
resting bid to the gun. Realized FV is the YARDSTICK we grade by, never the TARGET we post at. Spread
bounds fillability. All per-category. (Entry grades are hypotheses; settled results are the test.)*

1. **The aim is the dip, not FV (A49 generalized).** 97% of tickers dip below their anchor before the gun;
   a resting bid posted at the dip is *paid a discount* to the gun price. Posting at FV forfeits that
   discount and instant-fills at the going rate (the zero-discount fill). The deployable per-cat dip
   (`docs/policy/aim_table.json`, derived from the 9.3M-row PMU + raw ITF trades): MAIN ~2¢, CHALL ~3¢,
   ITF ~4¢ (capped — see §3). The old flat 3¢ was already close for tour; the lever is per-category, not
   a bigger constant.

2. **FV is the yardstick, not the target (proven 2026-07-03).** Grade-vs-result on the settled slate:
   pairs that were NOT both-legs-FV-positive settled *better* than both-FV-positive (net +$5.95 vs +$3.35,
   win 0.73 vs 0.55). Requiring both-legs-FV>0 as an A-gate would **discard winners**. The A-shape is
   `combined ≤ 97 + clean-green exit`, full stop. FV-capture measures whether we bought under the gun; it
   does not predict the settle. Report FV alongside the grade; never gate on it.

3. **Spread bounds fillability.** How deep a resting bid still gets *paid* is set by the spread structure,
   not by desire. Tour books are tight (1–2¢) → deep bids don't fill → shallow aim (2–3¢). ITF/CHALL
   books are wide → deep bids *can* fill (97–99% dip-through) → but the wide-spread dip magnitude is
   **contaminated by directional collapse** (the falling-knife: a "20¢ dip" is often the losing side
   collapsing, not a discount on a stable leg). Deepening ITF beyond a conservative cap needs a
   spread-clean, collapse-separated derivation. Wide spread = *permission* to rest deep, not a *mandate*.

4. **The cap lineage (banned → leaking → superseded).** `paired_cap` was **banned** (blunt veto, starved
   participation). `completion_combined_ceiling` **leaks**: its scope is completion-reprice only, so two
   independent rich *entry* fills (CASOSO 17+95=112) sail past an armed ceiling. The successor is
   **`leg2_reshuffle` — a sequenced RE-AIM, not a cap**: leg-1 (riser) posts at bid and is *never vetoed*
   for projected combined; leg-2 (faller) re-aims to `min(dip, goal − leg1_basis)` on leg-1 fill and is
   re-derived on *every* leg-2 walk (closing the ceiling's checks-once hole). It only lowers/holds the
   resting bid, never pulls it. Bound, not veto: the pair converges to ≤ goal by *moving the aim*, not by
   refusing the leg. Completion+ceiling remains COMPLEMENTARY (it pays a starved favorite UP to fill;
   reshuffle only lowers) — keep both; they cover disjoint directions. Residual: simultaneous independent
   entry fills at rich prices are a race neither fully closes.

5. **Chasing is a premarket disease, not a gun disease.** STATIC bids capture +1.89¢ FV; CHASED (walked-up)
   bids capture −1.22¢ — a ~3¢ fill penalty. But post-gun chasing is already ~null (the walk's `if _live:
   return`); the damage is *premarket* walk-up (ALCCLA +26¢, 3.7h pre-gun, no volume-burst gun ever fired).
   `freeze_at_gun` (hold-static-through-the-gun) is correct but near-inert keyed to the burst latch. The
   real lever is a **premarket walk-cap** (bound the walk-up distance) — it needs no gun signal at all.
