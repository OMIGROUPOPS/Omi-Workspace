# ATP_MAIN paired-N — settlement-aware per-game EV — 2026-05-27

Read-only, local. 1,907 paired ATP_MAIN events. Mean combined-anchor (both-YES cost) = **101.6c** (>100 → ride-to-settle bleeds the vig). Per-game EV (operator spec, refs A40/B23/E32), per match with real anchors:

```
EV = P(both fire)·(R_f+R_d) + P(only fav)·(R_f − dog_anchor)
   + P(only dog)·(R_d − fav_anchor + 99) + P(neither)·(100 − combined_anchor)
fee = 7·P·(1−P) cents per leg per fill (entry always; exit when that leg fires)
```
Sweep R_f,R_d ∈ [1,55]; maximize per-game EV; DISABLE pair if max EV < 0.

## ⚠️ The result contradicts the "settlement bleeds" premise — here's why
- **Optimized per-game EV: $5,340 @10ct vs v6 $2,323 (2.3×). DISABLE pairs: 0 (none).**
- **But the optimizer picks DEEP R_fav (mean R_f ≈ 32) and both-fire rate ≈ 0%.** It is NOT finding a reliable double-cash; it's doing the opposite.
- **Why:** the spec's `only-dog → R_d − fav_anchor + 99` term means a **favorite that rides to settlement WINS (settles 99)**. For a 63c favorite that's **+36c** — hugely positive. So the EV-maximizing move is to set R_fav deep enough that the favorite *never exits and rides to its settlement win*. The strategy degenerates toward "hold the favorite to settle, scalp the dog."
- **The vig bleed (−1.6c) only applies to the `neither` case (both legs ride).** The `only-dog` case is a favorite-settlement *profit*, not a bleed — because the model assumes the favorite always wins at 99. So "settlement is not a safety net" holds only when *both* ride; a lone favorite riding to settle is modeled as the best outcome.

## ⚠️ This rests on an optimistic assumption — flag before acting
- **`fav rides → 99` assumes the favorite always wins.** Real ATP_MAIN favorite win rates are ~82–90% (per the cap audit), not 100%. A win-rate-weighted settle (`fav_settle = 100·P(fav win)`, e.g. ~85c) would cut the riding-favorite EV sharply and could flip several pairs negative — the current **0 DISABLE** is a consequence of the optimistic 99.
- **Deep R picks on small pairings (N=15–111) are in-sample overfit** (same caveat as the prior paired runs); the deep R_dog/R_fav values won't generalize.
- **Recommendation:** before using these R, re-run with a win-rate-weighted settlement value (I can do this), which is the honest version of "settlement is not a safety net." As specified, the formula rewards riding the favorite, which is a directional favorite bet, not the paired-exit design.

## Per band-pair (settlement-aware EV, @10ct per-game in cents)

| fav band | dog band | N | comb | v6 (R_f,R_d) | v6 EV | opt (R_f,R_d) | opt EV | both-fire | action |
|---|---|---|---|---|---|---|---|---|---|
| 62-64 | 38-40 | 111 | 101.8 | (8,1) | 3.9 | (38,1) | 31.1 | 0% | active |
| 86-89 | 10-16 | 89 | 101.2 | (11,6) | 9.9 | (14,51) | 11.1 | 0% | active |
| 59-61 | 41-42 | 83 | 101.5 | (24,26) | 27.7 | (41,31) | 41.5 | 0% | active |
| 67-68 | 33-35 | 75 | 101.7 | (2,24) | 4.8 | (33,41) | 37.9 | 0% | active |
| 77-79 | 23-25 | 72 | 101.9 | (14,22) | 14.2 | (23,39) | 22.5 | 0% | active |
| 72-74 | 26-28 | 66 | 100.9 | (3,3) | -1.0 | (28,41) | 30.3 | 0% | active |
| 69-71 | 31-32 | 64 | 101.6 | (17,12) | 16.2 | (31,14) | 28.2 | 0% | active |
| 55-56 | 45-46 | 63 | 101.3 | (33,39) | 37.9 | (45,48) | 46.5 | 0% | active |
| 80-82 | 20-22 | 63 | 101.5 | (1,52) | 4.1 | (20,53) | 23.5 | 0% | active |
| 72-74 | 29-30 | 62 | 102.2 | (3,26) | -1.2 | (28,31) | 24.8 | 0% | active |
| 52-54 | 49-51 | 61 | 102.4 | (11,3) | 12.2 | (48,47) | 56.8 | 0% | active |
| 83-85 | 17-19 | 61 | 101.5 | (15,54) | 18.3 | (17,55) | 19.6 | 0% | active |
| 65-66 | 36-37 | 59 | 101.9 | (33,3) | 30.7 | (35,39) | 40.8 | 0% | active |
| 90-94 | 5-9 | 54 | 100.8 | (2,63) | 11.1 | (9,55) | 15.0 | 0% | active |
| 90-94 | 10-16 | 53 | 101.9 | (2,6) | 2.5 | (10,18) | 10.8 | 0% | active |
| 52-54 | 47-48 | 47 | 100.9 | (11,11) | 13.7 | (48,11) | 45.5 | 0% | active |
| 57-58 | 43-44 | 47 | 101.3 | (18,3) | 20.3 | (43,55) | 51.3 | 0% | active |
| 75-76 | 26-28 | 45 | 102.0 | (8,3) | 5.9 | (25,55) | 27.1 | 0% | active |
| 57-58 | 45-46 | 43 | 102.6 | (18,39) | 30.5 | (43,48) | 51.6 | 0% | active |
| 59-61 | 43-44 | 39 | 102.8 | (24,3) | 18.1 | (41,1) | 34.4 | 0% | active |
| 59-61 | 38-40 | 38 | 100.1 | (24,1) | 21.9 | (41,8) | 36.6 | 0% | active |
| 55-56 | 47-48 | 34 | 102.7 | (33,11) | 23.8 | (45,1) | 38.0 | 0% | active |
| 62-64 | 36-37 | 33 | 100.4 | (8,3) | 7.2 | (37,3) | 33.4 | 0% | active |
| 65-66 | 33-35 | 30 | 100.5 | (33,24) | 23.6 | (35,1) | 29.5 | 0% | active |
| 69-71 | 33-35 | 30 | 103.2 | (17,24) | 15.4 | (31,24) | 28.6 | 0% | active |
| 75-76 | 23-25 | 30 | 100.3 | (8,22) | 6.8 | (25,16) | 26.1 | 0% | active |
| 83-85 | 10-16 | 30 | 99.7 | (15,6) | 14.7 | (17,12) | 16.6 | 0% | active |
| 69-71 | 29-30 | 27 | 100.0 | (17,26) | 25.3 | (31,41) | 37.5 | 0% | active |
| 65-66 | 38-40 | 26 | 103.6 | (33,1) | 26.1 | (35,19) | 29.1 | 0% | active |
| 80-82 | 17-19 | 26 | 99.8 | (1,54) | 19.0 | (20,55) | 36.1 | 0% | active |
| 77-79 | 20-22 | 24 | 99.8 | (14,52) | 17.5 | (23,47) | 28.2 | 0% | active |
| 62-64 | 41-42 | 22 | 103.8 | (8,26) | 12.3 | (38,55) | 49.0 | 0% | active |
| 49-51 | 49-51 | 19 | 100.8 | (3,3) | -3.7 | (50,48) | 46.8 | 0% | active |
| 77-79 | 26-28 | 19 | 103.6 | (14,3) | 12.2 | (23,55) | 31.5 | 0% | active |
| 67-68 | 36-37 | 15 | 103.5 | (2,3) | 0.8 | (33,44) | 50.7 | 0% | active |

*Read-only, local, in-sample. EV per operator spec (fav-wins-99 settle); the optimistic-settle + overfit caveats above are material. v6 deployed, no change.*