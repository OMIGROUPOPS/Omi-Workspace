# WALK/REPOST INTERACTION MODEL — the last AIM_V2 arm bar (2026-07-07 late; findings only)

**Data:** tonight's joint-shadow decisions (every placement/repost since the fields went live ~19:39 ET): **62 legs / 157 decisions** — one partial evening; the model REFITS nightly as the shadow accumulates (this is the arm-request's seed, not its full n). Producer `.claude/sweep_20260707/walk_repost_model.py` (committed alongside).

## P(walked | …)

| slice | P(walked) |
|---|---|
| **first posture = below_chain** | **85.7%** |
| **first posture = join** | **43.8%** |
| bucket 0 / 1 / 2 / 3 | 64.7 / 58.8 / 44.4 / 38.5% |
| Tbin >4h / 2-4h | 53.8 / 50.0% |

**The interaction statement:** resting BELOW the chain begets walking — a leg that opens below the non-self chain walks at 2× the rate of a join-posture leg. The expression invariant (join/improve-1) is therefore a walk-suppressor before the cap ever binds: it removes the below-chain posture that generates most walks. Cap = journey bound on what remains.

## Walk distance, cadence, EROSION (fitted-aim discount NET of walk drift; bar <25%)

| cat | legs | P(walked) | drift med/p75 (¢) | cadence med (min) | erosion med / p75 | **% walked legs >25% bar** | % over the RULED cap | % joint-would-bind |
|---|---|---|---|---|---|---|---|---|
| ITF_M | 21 | 66.7% | 2 / 3 | 25.2 | **0.17** / 0.40 | **30.8%** | 0.0% | 14.3% |
| ITF_W | 40 | 47.5% | 1 / **7** | **2.5** | **0.17** / **2.33** | **42.1%** | **15.8%** | 21.1% |
| ATP_CHALL | 1 | — | — | — | — | — | — | (n=1, no read) |

## The read (feeds the arm request post-checkpoint)

- **The MEDIAN passes the bar; the TAIL fails it hard.** Median erosion 17% in both ITF cats (under the 25% standing bar) — but 31-42% of walked legs individually exceed the bar, and ITF_W's p75 erosion is **233%**: walks that consume the fitted dip discount twice over. The mean story is fine; the damage is a fat tail of chase-walks (the ALCCLA/TANKAW class, now measured against the fitted aims).
- **The ruled caps target exactly that tail:** 15.8% of tonight's ITF_W walks exceeded even the generous 20¢ ruled cap; every one of those is a >100%-erosion walk by construction. The joint counterfactual would have bound 14-21% of walked legs — consistent with the evening rollup's caps-bite signal.
- **Cadence differs by cat:** ITF_W reposts every ~2.5 min (churny — the same-price FIFO hold is doing work here), ITF_M every ~25 min. The cap's value concentrates where cadence is fast.
- **Interaction with caps+expression, stated:** expression (join posture) halves walk INCIDENCE; the cap bounds walk MAGNITUDE on the residual; together they attack incidence×magnitude = the erosion tail, which is the only part of the distribution failing the bar. Neither alone covers both factors — the ruling's joint-arm framing is what the data shape wants.
- **Bar verdict tonight: median-PASS / tail-FAIL** → the arm case rests on the shadow nights showing the joint counterfactual converts the tail's erosion into either held discounts (starvation acceptable) or earlier fills — the conversion/starvation delta the nightly rollup measures. Not armable on one evening; the checkpoint gets the refit.
