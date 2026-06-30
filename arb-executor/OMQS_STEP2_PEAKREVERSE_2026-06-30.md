# OMQS STEP 2 — PEAK-THEN-REVERSE DISCRIMINATOR SWEEP (Jun 24–29 held-out)

Source: Kalshi /markets/trades tick-tape, 605 settled filled legs Jun 24–29 (the held-out validation window, today excluded). Each rule fires dynamically on the in-match (post-gun) path; flattens at the trigger level; NET$ = saves(losers cut early) − forfeits(winners/recoverers killed). Same two gates as the monotonic validation. MEASUREMENT ONLY.

Context: the monotonic cut (Step 1, shipped `b1aaef9`) covers the 35% monotonic-faller slice; this sweep targets the **ERHROD-class peak-then-reverse — 95 legs / −$648/wk (65% of the loss)** that the monotonic filter never fires on.

---

## Sweep results — NET$ (Jun 24–29 held-out)

**Rule 1 — Trailing-stop-from-peak** (cut when current < running_max − X):
| X¢ | TOTAL NET | fires | days +ve |
|---:|---:|---:|---:|
| 5 | +$440.0 | 559 | 4/6 |
| 8 | +$406.6 | 533 | 4/6 |
| 10 | +$353.0 | 516 | 4/6 |
| 12 | +$330.0 | 502 | 4/6 |
| 15 | +$356.1 | 477 | 4/6 |

**Rule 2 — Reversal-magnitude** (cut when leg gives back X% of peak−fill; fires only on legs that peaked above fill):
| X% | TOTAL NET | fires | days +ve |
|---:|---:|---:|---:|
| 50% | +$463.2 | 482 | 4/6 |
| 67% | +$369.7 | 466 | 4/6 |
| 75% | +$322.8 | 464 | 4/6 |
| 100% | +$180.4 | 449 | 4/6 |

**Rule 3 — Post-peak-monotonic-down** (peak must exceed fill+1; cut Y below the running peak):
| Y¢ | TOTAL NET | fires | days +ve |
|---:|---:|---:|---:|
| **5** | **+$590.7** | 492 | 4/6 |
| 8 | +$543.3 | 468 | 4/6 |
| 10 | +$490.2 | 453 | 4/6 |

Per-day (best of each rule): every rule is **strongly +ve on the bleed/high-volume days** (Jun24 +$200–294, Jun26 +$90–115, Jun29 +$150–173) and **slightly −ve on the two quiet green days** (Jun27 −$4 to −$21, Jun28 −$0.1 to −$12.5).

---

## Gate evaluation

**Gate (a) — total NET positive AND positive every day: PARTIAL.**
- Total NET: **massively positive** for all three rules (+$180 to +$591), dwarfing the monotonic cut's +$205.
- Positive every day: **FAILS** — Jun 27 and Jun 28 (the quiet green days, few losers, mostly winners) are negative for **every** parameter of every rule, because the discriminators cut wobbly **winners** (forfeiting band) when there are few ERHROD losers to save. No parameter recovers those two days.

**Gate (b) — parameter robustness: PASSES.** All three rules decay smoothly with the parameter (no cliff): trail +440→+356 over X=5–15; revmag +463→+180 over 50→100%; ppmono +591→+490 over Y=5–10. Operating points sit on a plateau, not a knife-edge.

---

## Verdict — ERHROD is ADDRESSABLE, but the naive discriminators over-cut on green days

The peak-then-reverse class is **NOT structurally hopeless** (unlike a net-negative result): all three discriminators are dominantly +EV (best = post-peak-monotonic-down Y=5, +$590.7/wk) and robust. **But none clears the STRICT "positive every day" gate** — they forfeit $4–21 on the 2 quiet green days by cutting wobbly winners.

Caveat — **high fire rate**: the best operating points fire on 75–81% of legs (ppmono Y=5 = 492/605). That is essentially "trailing-stop everything that pulls back from its peak" — a large behavior change whose net is positive only because the ERHROD saves dominate the many small band-gains it forfeits. A higher parameter (lower fire rate) trades net for fewer cuts.

**Next step (not a build yet):** a discriminator that recovers the green days — candidates: (i) gate the cut by day-type/volume (only fire when in-match flow is heavy), (ii) require a larger reversal (deeper give-back) so wobbly winners survive, (iii) combine with the monotonic cut and only apply peak-reverse above a peak-gain threshold. The ERHROD −$648/wk is reachable; the operating point needs one more refinement pass before it clears the every-day gate.
