# Dual-rest realization + collision census

Analysis seat only. Read-only. Two standing riser bids, **T5-armed**, causal fills (`cca7c6c1`). **Order A** = persistence-only join (P2). **Order B** = bid−1 tracker, held **≥1¢ above A** (`B = max(bid−1, A+1)`). **First-fill-wins**: the entry is whichever level flow reaches first; the sibling is treated as cancelled. Fallers fixed. Beside the **632 / 5,217¢** collectable bar and P1 (410/3,442) / P2 (480/3,493). Machine artifact: `…/DUAL_REST_REALIZATION.json`.

## Realized capture

| order | completable | under-par | locked ¢ | ≤93/≤95/≤97/<100 | riser forfeits |
|---|--:|--:|--:|---|--:|
| **Order A (join, =P2)** | 521 | **480** | **3493** | 83/120/206/480 | 117 |
| **Order B (bid−1 ≥A+1)** | 604 | **447** | **3443** | 83/121/211/447 | 32 |
| **DUAL first-fill-wins** | 604 | **454** | **3471** | 83/122/214/454 | 32 |

*(bar 632 / 5,217¢; P1 bid−1 410 / 3,442¢; P2 join 480 / 3,493¢.)*

## The dual is dominated by the shallow tracker

**Overlap census:** both **292** · only-B **85** · **only-A 0** · neither 32. **only-A = 0**: the join never fills a leg the tracker doesn't also fill — B sits 1¢ above A and shallower, so any flow deep enough to hit A passed through B first. With first-fill-wins, **B always wins the race**, so the DUAL takes B's shallow price and the join's depth is forfeited.

Result: DUAL **cuts forfeits 117→32** (B catches the 85 legs the join never arms) but **locks less than the pure join** (3471¢ vs 3493¢) — it trades depth for completion and lands at 67% of the bar. Running a tracker beside the join **front-runs** it; there is no synergy, only a race the shallow order wins.

## Per category — DUAL under-par (locked ¢)

| category | under-par | locked ¢ |
|---|--:|--:|
| ATP_CHALL | 210 | 1180 |
| ATP_MAIN | 90 | 564 |
| WTA_CHALL | 73 | 1269 |
| WTA_MAIN | 81 | 458 |

## Collision census — double-fill exposure at cancel latency

Of the **292 both-legs**, flow reaches the second (sibling) level within Δ of the first fill — a double-fill if the cancel round-trip exceeds Δ:

| cancel latency Δ | legs double-fill | worst-case extra-lot ¢ |
|---|--:|--:|
| ≤ 1s | **39** | 1810 |
| ≤ 5s | **39** | 1810 |
| ≤ 30s | **45** | 2066 |

At a realistic **1–5 s** cancel latency, **39 of 292 both-legs (13%) double-fill**, worst-case extra-lot exposure **1810¢ ($18.10)** — an unwanted second long lot at the sibling level. By 30 s it is 45 legs / 2066¢. Per category (≤5 s): ATP_CHALL 15 · ATP_MAIN 9 · WTA_CHALL 6 · WTA_MAIN 9.

## Named

| leg | anytime | A join (ts) | B bid−1 (ts) | dual entry | overlap | gap s | 2-lot avg |
|---|--:|--:|--:|--:|---|--:|--:|
| **NIK** | 18 | 29 | 30 | 30 | both | 62 | 29.5 |
| **COP** | 47 | 64 | 65 | 64 | both | 0 | 64.5 |
| **VRB** | 68 | None | 68 | 68 | only_B | None | None |
| **ARN** | 50 | None | 56 | 56 | only_B | None | None |
| **WES** | 60 | None | None | None | neither | None | None |

- **COP — gap 0, guaranteed double-fill.** A (64) and B (65) fill at the *same instant* → colliding at any latency; 2-lot avg 64.5. The deep transient 47 is still unrealized (no rest occupied it).
- **NIK — the ≥1¢-above-A rule costs the deep catch.** A joins at 29, forcing B ≥ 30, so B fills at **30** (dual entry) — where free bid−1 alone reached **19** (prior task). The join (29) fills 62 s later: both, but no collision ≤30 s. The dual is *worse* for NIK than a lone tracker.
- **VRB (68) / ARN (56) — only-B.** The join never arms; the dual is just the tracker's solo fill. ARN's 50 remains unrealized by any order.
- **WES — neither.** No persistent level, no tracker catch; realized zero.

## Verdict

Two rests do **not** beat one join on locked value: first-fill-wins hands the entry to the shallow tracker, which front-runs the join (only-A = 0). The dual buys completion (forfeits 117→32) at the cost of depth (locks 22¢ less than the pure join) and imports a 13% double-fill tail. The 5,217¢ collectable bar stays ~1,750¢ out of reach — the single-rest realization ceiling is not broken by a second order, only reshaped.

## Conservation

409 riser legs, 637 games; fallers fixed. Bar 632/5,217¢; P1 410/3,442; P2 480/3,493. A 480/3493 · B 447/3443 · DUAL 454/3471 (forfeits 32). Overlap both 292 / only-B 85 / only-A 0 / neither 32. Collisions ≤1s/5s/30s = 39/39/45 legs (1810/1810/2066¢). Machinery cca7c6c1, sealed union 57daf3c1, divot census d1ac9497.