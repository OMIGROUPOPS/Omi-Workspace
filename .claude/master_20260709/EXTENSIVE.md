# THE EXTENSIVE — P&L attribution · ITF tradability · favorite timing (cut 2026-07-09 12:37 pm ET; mold FENCED per leg, gross+clean side by side; raw in extensive.json)

## PART 1 — P&L TIMELINE ATTRIBUTION (exchange settlements, respawn Jul-8 3:30 pm → cut)
**The finding IS the empty table: total realized settlements across the whole recovery window = +$3.87, in three rows** (ITF_W clean +2.50 at the 8-am hour, ITF adopted-class +1.37 at 5 am; every other cat × era × bot/manual row rounds to $0.00 — full hourly grid in the json).
- **The climb was NOT settlement-driven — by anyone.** Not bot mains (settled $0.00; the bot's mains book was ~2 legs as stated), **not the MANUAL book either (manual rows $0.00 in-window — the manual tickers barely settled at all)**. Balance moved $754.57 → $766.46 (noon → 12:37 pm) on **open-mark recovery and inventory cycling** — the morning finding (cash→inventory conversion, realized-positive) now confirmed against exchange settlement truth over the full respawn window. Nobody "paid us back"; the book marked back.
- Mold fencing: blackout-mold settlements in-window netted $0.00 (their damage realized BEFORE the respawn window — already attributed in the 07-08 dossier's −$167 mechanical class; not re-counted here).

## PART 2 — ITF TRADABILITY FILTER (corpus n=1,600 ITF pairs by W1-volume quartile)

| quartile (W1 contracts) | ITF_M: woke (≥V2 ever) / any dip-fill event | ITF_W: same |
|---|---|---|
| q1 < 2,500 | **63.0% / 63.9%** | **63.5% / 63.5%** |
| q2 2.5–6k | 83.8% / 86.2% | 79.7% / 83.0% |
| q3 6–12.5k | 93.9% / 94.8% | 91.5% / 92.5% |
| q4 > 12.5k | 91.6% / 95.0% | 94.4% / 96.9% |

- **The floor exists and it is the bottom quartile: below ~2,500 W1 contracts, one ITF match in three NEVER wakes** (never reaches 6 prints/30m) **and never produces a single dip-fill event** — those books are the structural-untradeable class (fills only via anti-selection on a lattice that never converges; the FILL_REDO V0 row is their whole life). Above ~6k, wake rates are 92–97% — volume is indeed the best bet.
- **Filter proposal (findings only): qualify ITF conceptions at a per-cell volume gate — running-volume projection ≥ q2 (~2.5k) as the hard floor, with the gauge's OPEN state as the micro-confirm** (macro qualifies the match, tape times the entry — granularity law). recut_cells_volume already carries per-cell vol medians for the refit.
- **What it saves vs forfeits — stated honestly as PENDING:** the era join (our fills × match volume) returned empty — the volume ledger's bell universe predates yesterday evening's matches; the would-have P&L of the excluded population computes at tonight's ledger refresh and lands as this entry's amendment. Corpus-side, the excluded third of q1 produces no dip-fill events at all — there is structurally nothing to forfeit there.

## PART 3 — FAVORITE TIMING DOCTRINE (heavy cells 75–94; n=222 ITF_M / 204 ITF_W / 109 ATP_CHALL legs)

| metric | ITF_M | ITF_W | ATP_CHALL |
|---|---|---|---|
| dip dwell (min at low+2) p25/**p50**/p75/p90 | 0/**3**/28/176 | 0/**3**/36/217 | 3/**160**/377/446 |
| climb start (last low-touch, rel bell) p25/**p50**/p90 | −70/**−42**/−2 | −81/**−50**/−9 | −52/**−27**/−1 |
| dip start rel VOLUME ONSET p25/**p50**/p75 | −42/**−11**/−1 | −91/**−15**/0 | (in json) |
| climb size (close − low) p25/**p50**/p75/p90 | 7/**17**/32/43 | 7/**21**/33/46 | (smaller) |

**The climb anatomy, plainly:**
1. **The heavy leg's bottom is a ~3-MINUTE event at median** (ITF) — wide only in the p75+ tail. The capture window is razor-thin: this is why reprice beats divot 2:1 in our fills — the divot barely exists as a resting target unless the bid is ALREADY THERE.
2. **The dip and the volume onset are the same event** (dip starts med 11–15 min BEFORE onset, p75 at onset) — the wake IS the dip; by the time the gauge confirms OPEN, the bottom is printing or gone.
3. **The ascent owns the final ~45 minutes** (last low-touch med T−42/−50), and **missing it costs a median 17–21¢** (p75 32–33) — the whole cell-edge plus the climb. The dual outcome priced: a dip fill carries that climb as W2-swing cushion AND (Part A chain) +6–9 points of band-reach; a post-climb fill has neither.

**THE FAV-ENTRY TIMING SPEC (for the consumption layer, findings only):**
- **MACRO (arms):** heavy-cell (75–94) legs on volume-qualified matches (Part 2 floor) get their aim RESTING at edge_p50-below-close from **T−90** (before the p25 climb start) — the bid must pre-exist the 3-minute window; placing on the signal is already late.
- **MICRO (confirms):** volume-onset approach (V1→V2 transition) = the dip is imminent-or-live; the aim HOLDS through onset ±15 min. **No fill by onset+15 → the climb owns the tape: stand down to join-at-close posture or skip — never chase the ascent** (the reprice class, named and priced above).
- ATP_CHALL differs per the category law: dwell p50 160 min (a long soggy bottom, not a snap) — the CHALL fav can be worked patiently; the ITF fav cannot.
