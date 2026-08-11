# Mirror-trust sizing — dev 804, V47 trace

Analysis seat only. Read-only. Sizes **LAW B** (derive the sibling's placement from the right eye's inverse read) before any build. One-eyed = one leg's snapshot read RIGHT vs the frozen QR path while the sibling's read is not its inverse; vindication per the `a20e1a85` method (sibling's bid at the right leg's key moment vs the sibling's subsequent fit-local flow). Machine artifact: `…/MIRROR_TRUST_SIZING_DEV.json` (all rows).

## The class and the vindication

| | value |
|---|--:|
| readable pairs (both reads + both frozen paths) | 604 |
| **one-eyed pairs** | **240** (40%) |
| vindicated / not / n-a | 167 / 68 / 5 |
| **vindication rate** | **71.1%** |

By category: ATP_CHALL 113 · ATP_MAIN 50 · WTA_CHALL 30 · WTA_MAIN 47. The sealed exam's 91% vindication (n=22) softens to **71% on the dev-wide class (n=235 decided)** — still a real signal: when one eye is right and the mirror disagrees, the market sides with the right eye's inverse 2.4× more often than not.

## LAW B counterfactual — the money

| channel | n | cents |
|---|--:|--:|
| new pairs completed (V47 one-sided, right leg credited, cf sibling fill cap-feasible, <100) | 2 | +7 |
| completed pairs improved (deeper cf sibling fill) | 16 | +48 |
| **TOTAL** | — | **+55** |

## The sizing verdict

**LAW B is worth ~55¢ on the dev slate — it does not pay for a build.** The vindication is real (71.1%) but the money doesn't follow, for structural reasons visible in the rows: in most one-eyed games the right eye's inverse predicts **RISING** for the sibling (the right leg read FALLING) — and a RISING sibling is precisely the one whose flow never comes down to a lawful bid, so the cf placement doesn't fill either; when the inverse predicts FALLING, the tracking cf fills near the low but the right leg's own entry is usually too rich for the pair to clear the cap (the CAP_BOUND richness organ again). The mirror's information is real; the maker mechanics can't monetize it. **Sized before build: decline LAW B** — the lever it competes with (first-fill discipline: pay the filled leg's own floor, 31/45 sealed cap-kills self-inflicted) holds the cents this instrument was hoped to find.

## Conservation

604 readable pairs → 240 one-eyed = 167 vindicated + 68 not + 5 n-a. LAW B: 2 new pairs (+7¢) + 16 improved (+48¢) = **+55¢**. Source dev V47 fb74c8b8, frozen paths QR 57daf3c1, prints fit-local; method a20e1a85.