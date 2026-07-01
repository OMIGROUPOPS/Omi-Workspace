# OMQS — DEPLOY-BOX COMPARE: prior (flags ON) vs current (bisect, flags OFF)

**The bisect (commit `2b23b5d`, Jun 30 15:46 ET):** *"restore green-window flags — liquid_repost / grace_kill / sustained_flow OFF; pair_governor stays OFF."* **Exactly 3 flags flipped OFF** — `liquid_repost_at_touch` (armed `e95bfb0`), `match_live_grace_kill` (`36d9344`), `sustained_flow_latch` (`3473a5d`). Behaviorally confirmed: `liquid_repost_at_touch` fired **24× Jun30, 0× Jul1**. Both boxes keep `completion_ceiling` ON and `pair_governor` OFF → the prior/current diff is **cleanly those 3 flags.**

- **PRIOR box** = W6, Jun30 00:56 → 15:46 (14.8 h), flags ON.
- **CURRENT box** = Jun30 15:46 → Jul1 18:40 (26.9 h wall, **~10 h disk-crash outage** → ~17 h active), flags OFF.

## Side-by-side (entry-boxed: each leg attributed to the config live at its first fill/post)
| lens | PRIOR (flags ON) | CURRENT (flags OFF) |
|---|---|---|
| legs touched | **237 (383/day)** | 87 (78/day; ~123/day outage-adj) |
| events | 124 | 48 |
| **fills** | **219 (354/day)** | 49 (44/day; ~69/day outage-adj) |
| pair both / one / missed | **98 / 23 / 3** | 14 / 21 / 13 |
| **completion rate** | **79%** | **29%** |
| one-sided **strand rate** | 19% | 44% |
| combined dist (both-filled) | ≤97: **9** · 98-100: **68** · >100: **21** | ≤97: 0 · 98-100: 12 · >100: 2 |
| entry terciles (fills) | cheap 68 · mid 84 · exp 67 | cheap 17 · mid 13 · exp 17 · flat 2 |
| one-sided class | PULLED 6 · TOO_DEEP 4 · NO_OPP 3 | PULLED 8 · TOO_DEEP 3 · NO_OPP 4 |
| gate footprints | t20m_fallback **119** · itf_vol 20 · maker_only 3 · fat_spread 3 | t20m_fallback 40 · itf_vol 22 · maker_only 1 · fat_spread 1 |
| P&L (log-settled, **UNRELIABLE**) | −$102.72 (n=58 of 222; 164 unlogged) | −$5.45 (n=37 of 83) |
| **P&L authoritative (OMQS_DEPLOY_PNL, Kalshi REST)** | **W6 −$31.4/day** (n=209) | **W7 −$2.5/day** (n=11, too thin) |

## What the bisect actually did — CONFIRMED: liquid_repost drove volume + completions
- **Throughput collapsed ~5-8×:** 354 fills/day → 44 (≈69 outage-adjusted). **The "prior printed more" claim is emphatically confirmed.** `liquid_repost_at_touch` (re-post at the touch to chase a fill) is the obvious volume driver; `grace_kill`/`sustained_flow` hold resting bids longer past the gun → more fills convert. Turning all three off = far fewer fills.
- **Completion collapsed 79% → 29%** (strand rate 19% → 44%). The flags were **completing pairs** — which is exactly the always-lay/keep-laying behavior M-α1 credited (+$26). So the prior box was, operationally, *running the always-lay lever*, and it did stranding far less.

## But it is NOT a P&L regression — both boxes bleed, PRIOR bled MORE
- **Authoritative REST P&L: prior −$31.4/day vs current −$2.5/day** (per `OMQS_DEPLOY_PNL_JUN24-30.md`, which boxes n=836 settled legs by entry-config). *(My log-settled −$102/−$5 is on a 26%/45% subset — the settled-event log gap — so it is unreliable; defer to the REST numbers.)*
- **The extra completions don't earn.** Even PRIOR completed **mostly at par**: only **9 of 98 (9%) cleared ≤97**, 68 at par (98-100), and **21 locked over-100 losses**. Entry terciles were ~31% expensive in *both* boxes — the bisect changed **volume, not entry quality.**
- So the flags bought **8× more par-priced completions + 8× more naked losers feeding the asymmetric exit (FUCKUP-3)** → the prior box lost *more* absolutely. The bisect **reduced activity and thus reduced the absolute bleed.**

## Verdict — is the bisect the regression?
- **Operationally, yes:** a 5-8× throughput and 79%→29% completion regression, driven by the 3 flags (liquid_repost primary).
- **On P&L, no:** neither config earned; prior bled ~13× more per day (−$31 vs −$2.5). The completion the flags buy is par-priced and feeds the losing exit — **more completion ≠ profit.**
- **Therefore: restoring the flags would restore completion AND the bleed.** The bisect is not the profit regression to chase; **the root is the exit geometry / naked-favorite loss (FUCKUP-3), not the flags** — consistent with the `OMQS_DEPLOY_PNL` verdict (green never earned; liquid_repost's W3 was the *best* window; completion_ceiling W6 was the recent bleed). **Before killing gates: killing/restoring gates moves volume, not the sign of P&L.**

Caveats: current box has a ~10 h outage (fills/day understated ~1.6×, shown outage-adjusted); log-settled P&L unreliable (defer to REST); PRIOR window 14.8 h vs CURRENT 26.9 h (per-day normalized). Method: `compare.py`; metrics `compare_metrics.json`.
