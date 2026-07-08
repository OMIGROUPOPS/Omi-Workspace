# EARLY-CANVAS STUDY — CONCEPTION-HORIZON Part 2 (T-8h → T-24h), landed 3:55 pm ET 2026-07-08

**Findings only. The T-8h bound moves on operator ruling, never on this doc by itself.**

## Prior art (C45)
- **PROOF_CONCEPTION_HORIZON.md (07-08)** — the bound this study exists to test; "what the bound forfeits, stated honestly" is exactly the question answered below. Delta: this doc replaces "unstudied territory" with measurements.
- **HOURLY_APPENDIX 07-07 (FLOOR-BY-HOUR)** — T-8h→bell verdicts (ITF prints/min 0.00 until T-3h; mains par-locked every bin). Delta: window extended to T-24h, same universe/conventions; adds drift information content, anti-selection on early prints, and per-game flow-state transitions.
- **PAIR-STORY 07-07** — "early posting buys POSITION, not early fills." Delta: quantifies what that position would have been worth beyond T-8h (≈ nothing, see §3).
- **LIVING_VAULT FOUNDATIONS §5 (07-08, operator)** — early quiet is volume-conditional, not time-conditional; distributions over medians. This study is that doctrine's first fitted test.

## Method
`analysis/early_canvas_20260708.py` on the VPS (read-only corpus; detached + watcher, 0 restarts). Universe = 2,460 detected-bell pairs (pair_story conventions: LATCH-CAL corpus bells, observed_starts preferred on suffix+day match; prints convention fillable(t) = min print in trailing 15 min; quote-touch = ask+ask cross). 2,444 OK / 16 thin-ticks skips. Hour bins T-24→T-1. Flow-state per game: onset = first minute with prints in ≥5 of trailing 15; floor97/floorS = first minute joint prints-fillable ≤97 / ≤ cat S-line. Raw: `results.jsonl` (7.4MB, VPS `/root/early_canvas_20260708/`); `aggregate.json` + `meta.json` committed here.

## §1 COVERAGE FIRST — how much tape exists out there
Coverage (pct of pairs with any tick in bin): **beyond T-16h the non-mains tape is essentially unobserved** — ITF_M 0.2–13%, ITF_W 1–10%, CHALL 0–17% (T-24→T-16). Coverage arrives at T-12 (88–96% all non-mains cats) — collectors pick games up ~half a day out. Mains are watched all day (67–94% from T-24). **Every "beyond T-16h" claim below rests on thin tape and is labeled as such; the T-12→T-8 zone is well-covered and the verdicts there are real.**

## §2 THE LATTICE BEYOND T-8h (per cat, prints + quotes)

| cat | bin | prints/min p50/p90 | zero-print bins % | joint-fillable any % | jf ≤97 % | joint-ask p10/p50 |
|---|---|---|---|---|---|---|
| ITF_M | T-12 | 0.00 / 0.02 | 88 | 3.0 | 1.1 | 103/123 |
| ITF_M | T-9 | 0.00 / 0.03 | 81 | 3.7 | 0.2 | 101/105 |
| ITF_W | T-12 | 0.00 / 0.00 | 91 | 2.5 | 1.2 | 102/136 |
| ITF_W | T-9 | 0.00 / 0.02 | 84 | 4.3 | 1.4 | 101/105 |
| ATP_CHALL | T-12 | 0.00 / 0.07 | 61 | 11.4 | 1.5 | 100/102 |
| ATP_CHALL | T-9 | 0.00 / 0.10 | 55 | 14.4 | 1.3 | 100/101 |
| WTA_CHALL | T-12→T-9 | 0.00 / 0.05 | 61–65 | 2–4 | 0–2.1 | 100/102 |
| ATP_MAIN | T-24→T-9 | 0.00–0.12 / 0.08–0.42 | 14–54 | 18–66 | **0.0–0.6** | 100/101 |
| WTA_MAIN | T-24→T-9 | 0.00–0.08 / 0.07–0.42 | 14–63 | 14–58 | **0.0–1.2** | 100/101 |

Reference (inside the horizon): jf ≤97 stays ≤4.1% through T-4 in every cat, wakes at T-2 (ITF 27–30%, CHALL 2–12%), and the real floor is T-1 (ITF 84–86%, CHALL 62–65%, mains 11–23%). **The ≤97 canvas does not exist before T-2h anywhere, in either convention** — beyond T-8h the ITF joint-ask p50 is 104–186 (T-16's 186 = the book is often not even two-sided; the lattice out there isn't par, it's absent).

## §3 WHAT THE BOUND FORFEITS — measured ≈ NOTHING
- **jf ≤97 in every T-24→T-9 bin, every cat: 0.0–2.2%** — and those slivers are sparse-print artifacts (ITF T-12 has 2.5–3.0% joint measurability at all).
- **Anti-selection on early sell-flow prints** (the our-resting-bid-fill proxy, outcome = bell mid − print): underwater-at-bell 28–69% across the covered T-12→T-8 zone (small-n bins hit 100%) — an early fill is a coin flip against the bell, **before** fees and before the game.
- **Drift variance:** median |mid move to bell| from T-12: ITF 14–17¢, CHALL 4–6¢, mains 1.5–2¢. Early ITF entry = 14¢ of unmodeled drift; drift_corr(mid@bin, mid@bell) rises monotonically toward the bell (ITF 0.50→0.80, CHALL 0.77→0.85) — early prices are strictly less informative, never more.

## §4 FLOW-STATE — the operator's §5 doctrine, fitted
- **The floor arrives WITH the flow, not with the clock: onset→floor97 lag p50 = 0–1 min** (ITF_M 0, ITF_W 0, ATP_CHALL +1, WTA_CHALL 0; p25 ≈ −4, p75 ≈ +8..14). The fillability event IS the flow transition.
- **The "early-floor" population (floor97 before T-2h: ITF 11.6–12.4%, CHALL 6–10%, mains 3–5.5%) is flow-early, not clock-early** — even those pairs open at their own onset (EARLY-pop lag p50 −10..0 min). No population anywhere opens quiet.
- Flow onset time-to-bell: ITF p50 −54 min (p10 −166..−208), CHALL −50/−19, mains −486..−596 (mains "onset" is meaningless — liquid all day; the gauge should not run mains).
- **Fitted provisional thresholds for the live-monitor gauge (ITF/CHALL only):** WAKING ≥ ~0.2 prints/min (trailing-30m; onset-pop p10–p25), OPEN ≥ ~0.4–0.6 with spread ≤4¢ (floor97-pop p50; LATE-pop spread p50 1–4¢). Early-floor pops carry WIDER spreads (ITF p50 6–7¢, p75 24–28¢) — a fast tape with a wide spread is the early-floor signature, not a contradiction.
- floorS (≤ cat S-line) exists on 51% of ITF pairs (ttb p50 −35 min), 51%/44% CHALL (−31/−22), 10–20% mains (−11/−19): the S canvas is a last-hour object everywhere.

## §5 VERDICTS (per cat: does anything before T-8h ever justify a resting bid?)
- **ITF_M / ITF_W — NO.** Zero-print 80–91%, jf ≤97 ≤1.4%, ask-lattice 104+ (often one-sided), 11–17¢ drift variance, ~coin-flip anti-selection.
- **ATP_CHALL / WTA_CHALL — NO.** Denser quotes than ITF but the same absence: jf ≤97 ≤1.5%, ask p50 101–102; the CHALL floor is T-1/T-2 and flow-gated.
- **ATP_MAIN / WTA_MAIN — NO (re-confirmed to T-24h).** Watched all day, par-locked all day: jf ≤97 ≤1.2% in every bin T-24→T-4. The 07-07 refutation extends to the full day.
- **The T-8h bound forfeits nothing measurable.** Evidence is compatible with keeping T-8h as-is or tightening; nothing supports loosening. The eventual replacement is conception keyed on observed flow-state (§4 thresholds) — clock distance was always the proxy, and the lag-0 onset→floor result says the gauge can carry the load once thresholds are ratified.

**Caveats:** beyond T-16h non-mains claims ride ≤17% coverage (§1 honesty); anti-selection n is small in single early bins (aggregate across T-12→T-8 before reading); rate30/spread thresholds are fitted on the same corpus they'd police — ratify on forward tape (the gauge's flow_state jsonl is already accumulating).
