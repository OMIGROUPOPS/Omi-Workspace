# OMQS MEASUREMENTS — Task A (premarket-FV feasibility) + Task B (§4 selective cut), 2026-06-30

Source: Kalshi REST (settlements/fills) + /markets/trades tick-tape (299,725 trades, 195 settled filled legs today) + live_v4.py code-check. Read-only. Bisect (restart 15:46:04 ET) untouched.

---

## TASK A — PREMARKET FV FEASIBILITY → gate is UNBUILDABLE on existing FV

**Code-check — premarket FV constructs EXIST:**
- `_running_mid` (live_v4.py:1757) — 30-min trailing traded-mid, BBO-mid fallback (`V4_RUNNING_MID_WINDOW_SEC=1800`, `MIN_TRADES=1`).
- `_fv_anchor_price` (1773) — freshest in-window tape print.
- `best_bid_at_post`/`best_ask_at_post` logged at order_placed (BBO at bid post).
- The A43 drift-predictor is **offline/observe-only** (fv_burst is observe-only by design); NOT wired at fill.

**But they do NOT carry the distortion signal.** Reconstructed each construct at fill time from the tape (192 legs with fv_burst + tape):

| construct | median(entry − construct) | X-sweep NET (X=0/2/3/5/8/10) |
|---|---|---|
| burst-fv_mid (M1 baseline, retrospective) | 0.0 | +27.1 / +22.7 / +23.5 / +9.4 / +12.0 / +9.9 |
| **running-mid (premarket, fill-time)** | **−1.0** | **−3.3 / −0.5 / 0 / 0 / 0 / 0** |
| **last-traded (premarket, fill-time)** | **−1.0** | **−1.0 / +1.6 / +2.0 / −0.8 / −0.8 / 0** |

At fill, **entry sits ~1¢ BELOW the premarket constructs** (we fill on dips, by construction), so `entry > premarket_FV + X` fires on almost nothing and nets ≈$0. **The X=2 +$98/week does NOT hold on any premarket construct — it collapses.** The distortion (entry above *eventual* fair) is a **forward** property, visible only at the burst (after the price collapses), not at the fill instant.

**Verdict: M1's distortion gate is RETROSPECTIVE-ONLY / unbuildable with existing FV.** The only entry-side path is *building* the A43 drift-predictor as a live fill-time fair value (a model build, not a config gate) — and A43 itself found it could not lift ROI through the asymmetric exit offline. Plex's retraction is confirmed by data.

---

## TASK B — §4 SELECTIVE DOWNSIDE-CUT → a POSITIVE rule exists (framing-dependent)

Corpus: 195 settled filled legs today (42 losers −$95.84, 152 winners). Each leg's full in-match tape pulled. Cut = flatten at `fill−X` if the leg falls there without first reaching `fill+band`.

**CRITICAL framing correction:** timing the cut from the **fill** is wrong — fills are ~T-200min (deep premarket), where price just noises around fill; the collapse happens **in-match at the gun**, hours later. A fill-relative cut either kills recoverers (looser, −$45) or never fires (monotonic, premarket noise → 0). **Timed from the gun (tape onset), the result flips.**

**Gun-relative cut sweep (NET$, today):**

| rule | X | N | fires | saves | forfeits | NET |
|---|---:|---:|---:|---:|---:|---:|
| looser (any dip) | 10 | 15 | 97 | +69.1 | −71.7 | −2.6 |
| looser | 10 | 30 | 74 | +65.5 | −49.3 | +16.2 |
| looser | 15 | 30 | 67 | +58.1 | −52.4 | +5.6 |
| **monotonic (no up-wobble above fill post-gun)** | **10** | **30** | **42** | **+45.6** | **−19.5** | **+26.0 ← best** |
| monotonic | 10 | 15 | 48 | +45.6 | −25.9 | +19.7 |
| monotonic | 15 | 30 | 40 | +39.8 | −22.9 | +16.9 |
| monotonic | 20 | 30 | 35 | +33.6 | −24.8 | +8.8 |

**Best rule: monotonic, X=10¢, N=30min from the gun → NET +$26.0/day (today).** Cut at fill−10 IF, in the first 30 min after the gun, the leg falls to fill−10 **without ever printing above fill**. Decidable at gun+30 with past-only data (no look-ahead).

**Why monotonic works and looser doesn't — separability:** of legs that dipped ≥10¢ below fill in-match, **36 were losers / 110 recovered-or-won (75% recovered)**. A naive dip-cut kills 75% recoverers (→ ≈$0). The **monotonic filter** (price went straight down from the gun, never bouncing above fill) selects the true fallers — fired set is loser-enriched (+$45.6 saved vs −$19.5 forfeited).

**PREREQUISITE — re-elevates gun-detection:** this cut needs the **gun** (tape-onset) to time the in-match window. Gun-detection (`match_live_detected`) currently fires **once/day** (dead). So the §4 cut's +$26 is *gated on fixing gun-detection*. Note this is the EXIT-cut use of the gun — distinct from M2's entry-cancel use (where the stale-buffer cancel is protective). **Gun-detection is the enabler of the §4 cut, not the entry-cancel.**

**CAVEATS:** (1) today only, n=1 day — the +$26 needs prior-week validation (the rule could be day-specific; E32/Jun-2 $6.15 warns blanket-flatten forfeits bounces — the monotonic filter is what avoids that, but only today is measured). (2) Requires the gun-detection fix first. (3) Band per loser estimated from the per-entry-price exit-band map.

---

## NET REORDERING

- **Task A (premarket gate): DEAD** on existing FV. Only a built forward predictor could carry it.
- **Task B (§4 cut): a POSITIVE rule exists** — gun-relative monotonic cut, +$26/day today — **but gated on gun-detection**, and needs week-validation.
- This **re-connects gun-detection**: not worth fixing for entry-cancel (M2: protective), but it is the **prerequisite for the §4 downside-cut** (Task B). Sequence: fix gun-detection → build the monotonic in-match cut → validate on the week.
