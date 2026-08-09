# V43 composition recalibration — two dials

Analysis seat only. Read-only. Both dials scored inside the composed machine (V43 `01a58334`, census `639e8b19`). **Bar for any recommendation: true book > 1,748 with the naked book improved toward ≥ 0.** Baseline V43 = 395 completed / 1,910¢ locked / **−162¢ naked** / **1,748¢ true book**. Machine artifact: `…/V43_COMPOSITION_RECALIBRATION.json`.

## Dial A — guard tolerance in composition

| T | completed | locked ¢ | naked ¢ | **true book ¢** | withheld resolved (comp/naked/held) |
|---|--:|--:|--:|--:|---|
| **10** | 395 | 1910 | -162 | **1748** | 0/0/36 |
| **15** | 398 | 1976 | -171 | **1805** | 3/2/31 |
| **20** | 399 | 1983 | -172 | **1811** | 4/4/28 |
| **25** | 404 | 2007 | -181 | **1826** | 9/5/22 |
| **removed** | 415 | 2123 | -192 | **1931** | 23/13/0 |

**Loosening the guard raises the true book monotonically (1,748 → 1,931 removed) but *worsens* the naked book (−162 → −192).** Every pair the loosened guard lets through that then fails to complete becomes a naked loss — the exact exposure the guard existed to prevent. **Dial A alone fails the bar** (naked moves the wrong way). The guard tolerance is the wrong lever for the naked book. **The standalone T=10 calibration (`645e035b`, net +73¢ in isolation) is COMPOSITION_STALE**: with arm+loosen making withheld pairs feasible, the guard is a net drag, not a gain.

## Dial B — dry-sibling withhold (the naked-book fix)

Withhold a leg's fill while its **sibling's flow-so-far has never come within 3¢ of any lawful sibling level** (decision-time only; lifted the instant it does). This targets the **NO_FLOW_NEAR −224¢ tail** directly — don't fill a leg whose sibling can never hedge.

| | value |
|---|--:|
| completed | 395 (unchanged) |
| locked ¢ | 1910 (unchanged) |
| **naked ¢** | **+49** (from −162) |
| **true book ¢** | **1959** |

**Two columns:**

| | ¢ | legs |
|---|--:|--:|
| **naked losses avoided** | +230 | 36 |
| winners forgone | −19 | 7 |
| **net naked improvement** | **+211** | — |

Per category (avoided / forgone ¢): ATP_CHALL 127/0 · ATP_MAIN 51/13 · WTA_CHALL 2/6 · WTA_MAIN 50/0. **Dial B meets the bar cleanly**: true book **1,959** (> 1,748), naked **+49** (≥ 0), completions and locked untouched — it only removes the unhedgeable naked losers.

## A + B — guard removed, replaced by dry-sibling withhold

| completed | locked ¢ | naked ¢ | **true book ¢** |
|--:|--:|--:|--:|
| 415 | 2123 | **+42** | **2165** |

**A+B is the recommendation: true book 2165¢ (> 1,748 ✓), naked +42¢ (≥ 0 ✓)** — both bar criteria met, and the best true book of any configuration. **Remove the deep-gap guard entirely and replace it with the dry-sibling withhold**: removing the guard captures the feasible completions it was blocking (+2,123¢ locked), and the dry-sibling rule fixes the naked book (+42¢) by cutting the NO_FLOW_NEAR losers the guard never addressed. Dial B alone (1,959 / +49) also passes if the guard architecture is retained.

## Named

| game | V43 (T10) | A T25 | A removed | B | A+B |
|---|--:|--:|--:|--:|--:|
| **PUTJEA** | — | — | — | — | — |
| **PENTHA** | — | — | 55 | — | 55 |
| **SHEOLI** | — | — | 92 | — | 92 |
| **SALIBR** | — | — | — | — | — |

- **PUTJEA — the 73 pair is unachievable.** JEA has **no qualifying flow at all** (union reach null); its rest at 64 never fills whether or not the guard withholds — the guard's withhold was **moot**. PUTJEA stays naked (PUT at 9) under every tolerance; **Dial B correctly withholds the naked PUT** (JEA is dry) → the game becomes a costless skip.
- **PENTHA — completes at 55 (locked 45¢) only when the guard is removed.** Both legs were GUARD_WITHHELD; removal fills them → a real completion the T=10 guard was blocking. A+B keeps it.
- **SHEOLI — completes at 92 (locked 8¢) on guard removal** (same GUARD_WITHHELD pattern).
- **SALIBR — stays incomplete under both dials.** IBR is FLOW_ABOVE_REST (rest 1¢ too deep), not a guard or dry-sibling case — neither dial reaches it; it needs a further loosen, not a recalibration.

## Verdict

The guard-tolerance dial cannot satisfy the bar (loosening lifts true book but degrades the naked book; tightening blocks completions). The **dry-sibling withhold is the correct naked-book mechanism** — it converts the −162¢ naked book to positive by cutting exactly the NO_FLOW_NEAR losers. **Ship A+B (guard removed + dry-sibling): true book 2,165¢, naked +42¢** — the only configuration that clears both bars at the frontier.

## Conservation

804 games. Baseline 395/1,910/−162/1,748. Dial A: T10 1,748 · T15 1,805 · T20 1,811 · T25 1,826 · removed 1,931 (naked degrades −162→−192). Dial B 395/1,910/**+49**/**1,959** (avoided +230/36 legs, forgone −19/7). A+B **415/2,123/+42/2,165**. Source V43 01a58334, census 639e8b19, certified closes 57daf3c1; T10 calibration 645e035b = COMPOSITION_STALE.