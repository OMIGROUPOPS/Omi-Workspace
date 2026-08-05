# Governor-conditional measurement — the buy-moment exam

Analysis seat only. Read-only, causal, no oracle input. Machine artifact:
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/GOVERNOR_BUYMOMENT_EXAM.json`.

**The point:** measure the 12-band governor signal **where a governor deploys** — at
the actual R3 buy/release moments — **not where the signal is loudest** (the
wrong-phase legs, where dip-timing hit AUC 0.78). This is the authority map any future
governor must land inside.

## Population & label

Consult points from R3 (49f6501): **acted-leg fill moments + release evaluations** —
**1,437** deduped (1,147 ACTED_FILL + 290 RELEASE_EVAL); 1,155 receive a walk-forward
held-out score. At each, the full 12-band causal EWMA state (own-leg 6 + sibling-leg 6,
e64b0837 spec). **Label y=1** if a *deeper qualifying entry* — a qualifying ask floor
(dwell/5-lot/spread-lawful) or a true print **strictly below the about-to-pay price** —
occurs *later* on that leg's own tape (i.e., the buy was premature; a governor should
have waited). **Base rate = 0.573** — more than half of buy-moments had a cheaper entry
still to come.

## Authority map — per category, own / sibling / combined (walk-forward held-out)

| category | n | base | own AUC / AP | sib AUC / AP | comb AUC / AP | best set |
|---|--:|--:|---|---|---|---|
| ATP_CHALL | 553 | .512 | **0.572** / .632 | 0.546 / .609 | 0.570 / .618 | own / combined |
| ATP_MAIN | 191 | .681 | 0.535 / .717 | 0.525 / **.738** | 0.522 / .728 | ~chance (high base) |
| WTA_CHALL | 195 | .585 | 0.507 / .637 | **0.610** / **.732** | 0.540 / .663 | **sibling** |
| WTA_MAIN | 216 | .625 | 0.539 / .691 | 0.542 / .685 | **0.559** / **.701** | combined |
| **overall** | 1155 | .573 | 0.558 / .658 | 0.548 / .656 | 0.560 / .654 | — (lift ≈ 1.15) |

**The sober headline: at the deploy points the governor signal is weak** — overall AUC
~0.55–0.57, lift only ~1.15 over the 0.573 base. The 0.78 dip-timing AUC was measured
on the wrong-phase legs *where the signal is loudest*; here, at every actual buy-moment,
it is much thinner. That is the honest number a governor lives on.

**But the map is heterogeneous, and that is its value:**
- **WTA_CHALL → the sibling book is the authority** (sib AUC 0.610, AP 0.732) while
  own is pure chance (0.507). For WTA_CHALL a governor must read the *other* leg.
- **ATP_CHALL → own/combined** (0.572), sibling adds nothing on average.
- **ATP_MAIN → near-chance everywhere** (0.52–0.54) atop a high 0.681 base — a governor
  here barely beats "always wait"; abstain or use a strong prior.
- **WTA_MAIN → combined** (0.559) edges own and sib.

A governor that used one global feature set would be wrong in two of four categories.

## Named row — ARNROM | ROM, 18:49:11 ET, pay 42

| feature set | score | rank (ATP_CHALL) |
|---|--:|---|
| own | 0.575 | 285 / 683 (top 41.7%) |
| **sibling** | **0.739** | **37 / 683 (top 5.4%)** |
| combined | 0.714 | 61 / 683 (top 8.9%) |

At ROM's buy-moment (paying 42), **own bands are blind** — cross 0.0, lock 0.0,
bid_stair 0.0 (only a passive bid-dom 0.72 / ask-stair 0.85). The **sibling ARN's book
is screaming**: cross/lock EWMA **15.74**, ARN's bid crossing the ask (57 ≥ 56) with
best-bid **1,723** lots and bid-depth to **21,335** (corroborating the cited ~9,541
crossed lots). A deeper ROM entry **did** occur later (label 1) — buying at 42 was
premature.

**Own ranks it mid-pack (41.7%) and misses the urgency; the sibling set ranks it top
5.4%; combined top 8.9%.** This is the emblem of "one side's read is both": the leg you
are about to overpay on is silent, and the only warning is on the *other* book. A
governor keyed to own-book alone walks straight into this fill; the sibling channel
flags it decisively.

## Verdict

On average the 12-band governor is weak at its deploy points (AUC ~0.56, lift 1.15) —
no loud, uniform edge. Its real authority is **conditional and sibling-weighted**:
decisive for WTA_CHALL and for the loud-sibling tail (ARNROM|ROM top 5.4% on the
sibling set), near-useless for ATP_MAIN. The map above — not a single global threshold —
is what a governor must be fit inside: read the sibling for WTA_CHALL and whenever the
sibling book crosses, read own for ATP_CHALL, and hold a wait-prior for ATP_MAIN.

## Conservation

1,437 consult points (1,147 acted fills + 290 release evals) = 1,437 scored; 1,155
held-out after walk-forward warm-up. Base rate 0.573. Per-category n: ATP_CHALL 553,
WTA_MAIN 216, WTA_CHALL 195, ATP_MAIN 191.
