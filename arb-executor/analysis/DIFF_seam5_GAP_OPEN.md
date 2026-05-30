# SEAM 5 (GAP splitter) — OPEN. v14 does NOT lock as-is. Opus called it; my "GAP is safe" prediction was falsified.

## What Opus predicted and the test that confirmed it
Census-stability across GAP∈[4,8] is necessary-not-sufficient (compensating reclassification + boundary blindness — the engine-start check all over again). The principled probe: (a) inter-mode-gap **histogram** — is the cutoff in a valley or a populated region? (b) per-cell fired-mode **set-identity** diff (not cardinality).

**Result — GAP=6 is NOT in a valley:**
- 33 cells have inter-mode gap in [4,8] (densest part of the distribution, not empty space).
- 18 cells flip their fired mode across GAP∈[4,8].

My structural story ("cheap = bank-vs-reach ~33 apart; mid-book unimodal ~0; nothing at 4–8") was **half-wrong**: cheap cells do split wide, but the mid-book (c43–c84) is riddled with two modes 4–8 cents apart. The tape has cells torn between e.g. a +12 and a +17 exit. GAP=6 sits on top of them.

## Filtering to what moves money
18 fired-mode flips → **8 economic-state flips** → **3 EXIT↔non-EXIT flips** (c13, c37, c42) → **1 materially solid case: c13.**
- **c13**: EXIT X=13 at **+2.95 SE** under GAP=5 → **PARK-noise** at GAP=6. A bankable exit destroyed by the threshold.
- c37 (+0.89 SE), c42 (+0.69 SE): sub-1-SE, within-noise either way — the gate is already ambivalent; conservative park is fine.
- The other 10 flippers only nudge their fired center ±1–2 cents while staying in the same economic state — harmless.

## c13 is the textbook artifact (the smoking gun)
Draws: lower cluster X 6–27 (n=234) with sharp spikes at X=10 (68), X=13 (35), X=24 (60); reach tail X 32–59 (n=66). Largest internal gap = **5** (just under GAP=6). So GAP=6 **refuses to split**, merges everything 6–27 with the 32–59 reach into one blob:
- MERGED center X=15, merged cond **0.19** (false smear → PARK-noise).
- SPLIT lower cluster own-center X=13, cond **0.60** (trustworthy → EXIT +2.95 SE).

Exactly Opus's predicted failure: two near-adjacent sharp modes merged into a fake smear that parks real money.

## Every candidate fix tested is WORSE than the disease (all falsified)
| splitter | stable on own knob? | collateral |
|---|---|---|
| **GAP=6 fixed** | no (18 flips across [4,8]) | parks c13 (+2.95 SE) |
| **Dip test** (gap > pctile of null gaps) | YES (0 flips across pctile[80,95]) | **DESTROYS c5, c6** (over-splits cheap bimodal engine; global cond 0.04/0.21 → noise) + kills c12, c36 |
| **Spread** (gap > Z·within-MAD) | no (16 flips across Z[1.5,3]) | moves the arbitrary cutoff from cents to MAD-space |
| **Split-helps-resolvability** (split iff lowest cluster's own cond > merged cond) | no (13 flips across improve-margin) | saves c13 but **kills c12, c36** (v14 recoveries) |

**The dip test is the trap:** stable on its own knob (Opus's necessary condition) but catastrophically wrong against validated ground truth (c5/c6 → noise). Stability is necessary, not sufficient — Opus's own lesson, turned back on the candidate.

## The real diagnosis (deeper than "pick a better GAP")
c13's lower cluster is **itself internally multi-modal** (modes ~10, ~13, ~24). The whole **≤2-mode assumption** is the limitation — the cell wants the *lowest sharp sub-mode*, and no single global split point can find it because the cell is multi-modal, not bimodal. This is the tri-modal case sitting **upstream of every gate we hardened** (null, band, centroid, firewall). The fired-object principle that closed seams 1–4 says: judge the lowest mode on its own — but the *splitter that defines "the lowest mode"* is itself the last unhardened object.

## The fork (method-authority call for Opus)
The fix is a **threshold-free, mode-count-free readout**: "what is the cheapest exit X the bootstrap reliably pins (local cond ≥ FLOOR with non-trivial occ)?" — scan candidate centers from cheapest up, fire the lowest whose local window pins ≥FLOOR. This drops GAP and the ≤2-mode assumption entirely and makes the readout assumption-matched to multi-modal cells. (Partial test started; needs stability sweep on its own occ_min/window params + the c44-must-stay-noise + c5/c6-must-survive + ballast-preserved checks before it can be trusted. NOT yet validated — three candidates already died at this exact step.)

## Status
- **v14 kernel is NOT locked.** c13 is a real defect; the splitter must change.
- GAP=6 → replace with a lowest-sharp-submode readout (candidate), pending Opus method sign-off + full validation.
- Recovered seams 1–4 (X-veto, Sharpe, occ·cond product, per-mode cond) all still stand — this is upstream of them, not a regression of them.
