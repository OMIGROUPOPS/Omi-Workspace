# SEQUENTIAL FLOOR — the achievable entry edge, measured the doctrine's way (2026-07-08, SEND-ORDER #2)

**Read-only corpus study. ENTRY ONLY — no settlement columns anywhere.** 2,448 detected-bell pairs (LATCH-CAL corpus bells + observed_starts upgrade), 2,435 measured / 13 no-W1-fillable skips. W1 = T-8h→bell per match; prints-only fillable convention unchanged (min print in trailing 15 min). Fav = higher W1-closing leg. Raw: `aggregate.json`, `seqfloor_20260708.py` (results.jsonl on the VPS, `/root/seqfloor_20260708/`).

## Prior art (C45)
- **PAIR_STORY 07-07** — the simultaneous joint floor (min over co-fillable minutes of fav+dog): the lens this supersedes. Its S-lines (ITF 84/84, CHALL 93/90, mains 93) were set on that lens.
- **LIVING_VAULT front page** — each leg at ITS OWN divot; seesaw; divots 45–65 min apart; drift = the entry edge. This study is that doctrine turned into the measurement.
- **Fused-gun / LATCH-CAL bells** — same bell axis; **EKSLUX caveat carries: bells are tape-derived except 2 certified rows.**
- **B3 half_timing (07-05/06)** — the fader's dip passes before leg-1 fills; the time-shape section below is that finding's population-level confirmation.

## THE MEASURE
Per leg: **edge = W1-closing fillable − deepest fillable in W1** (its own time). Sequential pair edge = fav edge + dog edge. Implied entry combined = deepest_fav + deepest_dog. Doctrine premium = simultaneous joint floor − implied combined.

## §1 Per-cat table (p10/p25/**p50**/p75, ¢)

| cat | n | fav edge | dog edge | **pair edge** | **implied combined** | closing combined | simultaneous (old lens) | doctrine premium | ≥3/5/8/12¢ % | gap min p50 | fav-first % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ITF_M | 827 | 0/0/**6**/19 | 0/0/**0**/3 | 0/3/**9**/23 | 52/63/**79**/90 | 77/85/**92**/97 | 66/74/**84**/94 | 0/0/**4**/10 | 77/68/57/43 | 41 | 69.0 |
| ITF_W | 763 | 0/0/**4**/19 | 0/0/**0**/3 | 0/2/**8**/21 | 53/65/**79**/92 | 77/85/**92**/97 | 68/75/**85**/94 | 0/0/**4**/10 | 73/64/52/43 | 44 | 65.5 |
| ATP_CHALL | 470 | 0/0/**2**/7 | 0/0/**0**/2 | 0/1/**3**/10 | 62/76/**92**/97 | 79/88/**96**/100 | 71/80/**93**/99 | 0/0/**2**/4 | 57/39/29/23 | 62 | 66.2 |
| WTA_CHALL | 49 | 0/0/**0**/3 | 0/0/**0**/1 | 0/0/**1**/5 | 68/81/**95**/97 | 80/87/**95**/99 | 77/82/**92**/99 | 0/0/**1**/3 | 37/29/16/12 | 33 | 57.1 |
| ATP_MAIN | 166 | 0/1/**1**/2 | 0/0/**1**/1 | 1/1/**2**/4 | 92/97/**98**/99 | 95/100/**101**/102 | 94/98/**99**/100 | 0/0/**1**/2 | 40/13/3/2 | 137 | 54.2 |
| WTA_MAIN | 160 | 0/0/**1**/2 | 0/0/**1**/1 | 0/1/**3**/4 | 82/95/**98**/99 | 90/99/**101**/101 | 83/98/**99**/100 | 0/0/**1**/2 | 51/21/9/7 | 145 | 58.1 |

**The doctrine's number: ITF's sequentially-achievable combined is median 79 (p25 63–65) — 5–6¢ below the simultaneous floor the S-lines were set on, and the premium is 10¢+ on a quarter of ITF pairs.** Sequential-only pairs (joint lens undefined, no co-fillable minute): 2–5 per cat — negligible; the premium, not existence, is the story.

## §2 The edge is FAV-SIDE — the dog has no depth, only timing
Dog edge is median **0** in every cat (p75 ≤3¢): **the dog's cheapest W1 moment is (nearly) its closing price** — it drifts down INTO the bell. The favorite carries essentially the whole sequential edge (med 4–6¢ ITF, p75 19), dipping mid-window and recovering. Per fav-bucket (n≥15):

| cat\|bucket | n | fav edge p25/50/75 | pair edge p50 | implied p50 | ≥5¢ % | fav-first % | tFavDeep | tDogDeep |
|---|---|---|---|---|---|---|---|---|
| ITF_W\|80-90 | 145 | 2/**15**/27 | **16** | 77 | **75.9** | 75.2 | −61m | −11m |
| ITF_M\|80-90 | 128 | 1/**9**/22 | 12 | 83 | 69.5 | 75.0 | −56m | −14m |
| ITF_M\|90+ | 127 | 3/**9**/23 | 10 | 87 | 74.8 | **81.9** | −51m | −15m |
| ITF_W\|90+ | 92 | 3/**8**/20 | 9 | 89 | 69.6 | **85.9** | −70m | −12m |
| ITF_M\|70-80 | 161 | 0/**9**/22 | 11 | 78 | 67.7 | 68.9 | −42m | −14m |
| ITF_W\|70-80 | 153 | 0/**8**/24 | 11 | 78 | 66.7 | 71.9 | −45m | −13m |
| ITF_M\|<60 | 247 | 0/**3**/11 | 8 | 72 | 64.8 | 58.7 | −31m | −17m |
| ATP_CHALL\|80-90 | 66 | 0/**3**/24 | 5 | 89 | 50.0 | 81.8 | −66m | −9m |
| ATP_CHALL\|90+ | 64 | 1/**4**/15 | 5 | 95 | 50.0 | 76.6 | −151m | −19m |
| ATP_MAIN (all buckets) | 166 | ~1/**1**/2 | 2 | 98–99 | 4–17 | ~46–63 | −135..−424m | −70..−286m |

**The heavier the favorite, the harder and earlier it dips and the more reliably it dips FIRST** (fav-first 82–86% in the 90+ buckets vs ~54–59% in balanced pairs). The richest cell on the whole canvas is **ITF_W fav-80-90: median 15¢ fav dip, median implied combined 77, three-quarters of pairs ≥5¢.**

## §3 TIME SHAPE — the sequencing recipe, signed
- **Fav divot: mid-window** — med T−31..−70 min by ITF bucket (deeper buckets dip earlier).
- **Dog divot: the last ~15 minutes** — med T−9..−17 min across every ITF/CHALL bucket.
- Gap between the two deepest moments: med 41–62 min ITF/CHALL (the 45–65 min doctrine number, reproduced and now SIGNED: **fav first, 2:1**).
- This is B3's half_timing at population scale, inverted into a recipe: **work the fav's dip mid-window; the dog's floor arrives near the bell — completion timing, not completion depth.** (The gun's job: the dog's floor lives exactly where the latch was blind; the fused gun + flow gauge are what make the late window workable.)

## §4 Mains/CHALL re-verdict under the sequential lens
- **Mains: still par-locked.** Sequential opens ~1¢ at median (implied 98 vs simultaneous 99); the liquid extended clock does NOT hide a floor — it never leaves par. A tail exists (WTA_MAIN ≥5¢: 21% of pairs, p10 implied 82) but the median story is unchanged: NO-GO for depth; mains remain a timing/join canvas at best.
- **ATP_CHALL: materially softened.** Med pair edge 3¢ but the fav-heavy buckets (80-90/90+) run 50% ≥5¢ with fav dips of 3-4¢ med / 15-24¢ p75 — the simultaneous 93 hid a bucket-conditional edge. WTA_CHALL n=49: no read beyond "small" (holds provisional).

## §5 Proposed S-line refits (findings only — operator ratifies)

| cat | current S-line (simultaneous lens) | sequential med implied | **proposed** |
|---|---|---|---|
| ITF_M | 84 | 79 | **79** |
| ITF_W | 84 | 79 | **79** |
| ATP_CHALL | 93 | 92 | **92** |
| WTA_CHALL | 90 (n=29 prov.) | 95 (n=49) | **hold 90** — both samples too small to move a line |
| ATP_MAIN | 93 | 98 | **93 is fiction on any lens** — either restate 97 (p25) or keep 93 as an explicit practically-empty filter; operator's call |
| WTA_MAIN | 93 | 98 | same as ATP_MAIN |

## §6 AIM_V2 target re-anchor note
1. **The aim surface is SIDE-CONDITIONAL, not symmetric.** Current AIM_V2 aims dips on both legs (ITF/CHALL, ≥3¢ floor). The data: the fav leg carries the depth (bucket-conditioned, med 3–15¢, p75 ~20+); **the dog leg's dip depth is ~0 — a dog-side depth aim is aiming at nothing.** Dog-side policy should be join-at-close-level, timed to the late window (flow-state gated), not deepened.
2. **Bucket conditioning beats cat conditioning:** within ITF the fav-80-90 bucket offers ~3× the median dip of the <60 bucket. The (cat, fav-bucket, side) cell is the natural aim key.
3. **Timing prior for free:** fav aims should expect their fill window med T−30..−70; dog completions med T−9..−17 — the aim table can carry these as placement/patience priors. All of this feeds the ramp's honest-n accumulation; nothing arms on this study alone (C46 Lane-1 bars unchanged).

**Caveats:** tape-derived bells (2 certified); prints-only convention is conservative (understates fillability where the book quotes but never prints); entry-only by construction — nothing here says these entries CASH (that's the W1→W1 multiplication mandate's other factor); ITF p75 fav edges (19–27¢) partly ride the knife-contaminated wide-spread class (pair_story's standing caveat).
