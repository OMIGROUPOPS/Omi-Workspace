# Riser trigger frontier — the causal reach as a function of trigger law

Analysis seat only. Read-only. Same 3-channel causal machinery (`d3db740f`): a level counts only on post-trigger CANON evidence (any-trade + seller-print + ask-dwell ≥10 s). **Only the riser trigger varies**; faller legs keep their fixed tracking causal floor, so pairs stay scorable. Beside the any-time ceiling **637 / 5,253¢** (telemetry). Machine artifact: `…/RISER_TRIGGER_FRONTIER.json`.

## The five trigger laws

- **T1 pulse 2nd-visit** — the incumbent: arm at the second ask-divot visit.
- **T2 first divot + resume** — arm the first time a trough is seen and price leaves it (both observable).
- **T3 first seller-hit** — arm on the first seller-aggressed print at any level (no persistence wait).
- **T4 persistence ≥300 s only** — arm as soon as any bid level has rested 300 s (no seller-hit required).
- **T5 first two-sided book** — earliest possible; the tracking-class trigger applied to risers.

## The frontier

| trigger | completable | under-par | locked ¢ | ≤93/≤95/≤97/<100 | risers empty | false arms | false-arm ¢ |
|---|--:|--:|--:|---|--:|--:|--:|
| **T1 pulse 2nd-visit [incumbent]** | 469 | **449** | **3054** | 78/124/235/449 | 186 | 75 | 182 (+4 hard) |
| **T2 first divot+resume** | 514 | **482** | **3167** | 80/130/250/482 | 135 | 91 | 181 (+6 hard) |
| **T3 first seller-hit** | 581 | **554** | **4918** | 112/167/296/554 | 56 | 89 | 191 (+6 hard) |
| **T4 persistence≥300s only** | 636 | **631** | **5211** | 119/180/337/631 | 0 | 7 | 10 (+0 hard) |
| **T5 first two-sided book** | 636 | **632** | **5217** | 120/180/338/632 | 0 | 4 | 4 (+0 hard) |

*Any-time ceiling 637 / 5,253¢ (telemetry).* The reach is **monotone in trigger earliness**: the incumbent T1 collects the least (449 / 3054¢) and strands **186 risers with no arm at all**; T4/T5 recover almost the entire ceiling.

## What the frontier says

- **The incumbent 2nd-visit gate is the costliest.** T1 leaves 3054¢ — 2199¢ below the ceiling — because 186 risers never get a second ask-divot visit, so the rest never arms.
- **The seller-hit requirement, not persistence, is what discards flow.** Dropping it (T4, persistence-only) jumps to **631 / 5211¢ — 99% of the ceiling** — with only 7 false arms (10¢). Requiring a hit first (T3) both arms later and costs more false arms (89 / 191¢).
- **Early ≠ reckless when the level is stable.** T4/T5 arm early yet have the *fewest* false arms (7, 4): a persistent/opening level recurs. The *reactive* triggers (T2 first-resume, T3 first-hit) fire on a deep momentary event and over-commit — 91 / 89 false arms — arming at depths the flow never returns to.
- **Reframing the 37% "evaporation."** It was an artifact of the incumbent's late/gated trigger, not the flow: under a persistence-only trigger nearly all of the any-time reach is genuinely collectable.

## Per category — under-par (locked ¢), incumbent T1 vs persistence-only T4

| category | T1 under-par | T1 ¢ | T4 under-par | T4 ¢ |
|---|--:|--:|--:|--:|
| ATP_CHALL | 200 | 1015 | 291 | 1729 |
| ATP_MAIN | 106 | 586 | 128 | 917 |
| WTA_CHALL | 66 | 1011 | 97 | 1987 |
| WTA_MAIN | 77 | 442 | 115 | 578 |

## Named

| leg | anytime | T1 | T2 | T3 | T4 | T5 |
|---|--:|--:|--:|--:|--:|--:|
| **ARN** | 50 | 56 | 50 | 56 | 50 | 50 |
| **WES** | 60 | None | 60 | None | 60 | 60 |
| **COP** | 47 | 47 | 47 | 47 | 47 | 47 |
| **VRB** | 68 | 68 | 68 | 81 | 68 | 68 |

- **ARN — does any lawful trigger reach 50? YES.** T2 (first-resume), T4 (persistence), T5 (two-sided) all reach **50**; only the incumbent T1 and the hit-gated T3 stop at 56. The deep-50 flow *is* collectable — the incumbent trigger was the specific reason it looked lost. (T1/T3 carry a 6¢ false arm here.)
- **WES — does any trigger arm at all? YES, three do.** T2/T4/T5 arm and collect **60**; T1 (no 2nd visit) and T3 (no seller-hit) never arm (null). WES was not structurally hopeless — it was starved by the incumbent gate.
- **COP — 47 under every trigger** (robust; the lone post-arm trade at 47 lands after all five triggers).
- **VRB — 68 under every trigger except T3** (first-hit over-reaches to 81, a 13¢ false arm). Persistence and resume triggers hold it at the true 68.

## Conservation

409 riser legs, 637 games; faller floors fixed. Any-time ceiling 637/5,253¢ (telemetry). Per trigger under-par/locked: T1 449/3054 · T2 482/3167 · T3 554/4918 · T4 631/5211 · T5 632/5217. Machinery d3db740f, sealed union 57daf3c1, divot census d1ac9497. False-arm ¢ = Σ(post-trigger floor − deepest level seen by arm), the depth an early arm saw but the flow never returned to; 'hard' = armed but zero post-trigger flow.