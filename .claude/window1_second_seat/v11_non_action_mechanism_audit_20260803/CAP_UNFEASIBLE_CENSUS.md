# CAP_UNFEASIBLE census — the 134 legs, and the guard

Analysis seat only. Read-only. The **134** naked legs tagged CAP_UNFEASIBLE_AT_ARM in the V41 full-book P&L (`a30f5ccd`): a leg filled and armed a pair cap (99 − its entry) that the sibling could never rest under. For each, the book state of **both** expressions at the fill instant. Machine artifact: `…/CAP_UNFEASIBLE_CENSUS.json`.

## The infeasibility gap — sibling contemporaneous ask − its cap

| stat | ¢ |
|---|--:|
| n | 134 |
| min / p25 / median / p75 / max | -3 / 1 / 1 / 2 / 61 |
| mean | 2.6 |

**Most infeasibility is marginal** — median gap **1¢**, p75 2¢ — but a **heavy tail to 61¢** carries the damage (the sibling trades a rich, wide book the cap never approaches).

## Time structure — was the cap ever feasible?

| structure | legs |
|---|--:|
| **INFEASIBLE_FROM_PLACEMENT** | **132** |
| feasible at placement, broken by drift | 2 |

**132 of 134 were infeasible the moment the rest stood** — the sibling was already priced out at placement. This is **structural, not drift**: the maker filled one side of a pair whose two asks already summed well over 100, leaving a naked directional long with no hedge ever available.

## Per category

| category | legs | gap median ¢ | infeasible-from-placement | naked P&L ¢ |
|---|--:|--:|--:|--:|
| ATP_CHALL | 53 | 1 | 51 | -28 |
| ATP_MAIN | 32 | 1 | 32 | -138 |
| WTA_CHALL | 7 | 1 | 7 | +6 |
| WTA_MAIN | 42 | 1 | 42 | -95 |

ATP_MAIN (−138¢ on 32 legs) and WTA_MAIN (−95¢ on 42) carry the loss; the filled side is a favorite bought rich whose dog sibling never cheapens to the cap.

## The guard question — two columns, always

Guard: **place a rest at level L only if 99 − L ≥ sibling's contemporaneous ask − T** (evaluated at the cap-setting fill). Benefit = the 134 infeasible-cap naked legs withheld (loss avoided). Cost = completed pairs whose first fill the same rule blocks (the sibling's ask was momentarily above the cap before it dropped to fill) **plus** winning naked legs withheld.

| T (¢) | withheld of 134 | loss avoided ¢ | completed pairs forfeited (¢) | winning naked forfeited (¢) | **net ¢** |
|---|--:|--:|--:|--:|--:|
| 0 | 116 | +232 | 162 (−365) | 96 (−248) | **-381** |
| 2 | 20 | +121 | 16 (−85) | 7 (−59) | **-23** |
| 3 | 11 | +106 | 10 (−68) | 4 (−56) | **-18** |
| 5 | 5 | +87 | 7 (−62) | 2 (−53) | **-28** |
| 10 | 3 | +79 | 2 (−4) | 1 (−2) | **+73** |

**Only a loose guard pays.** At **T=10¢** the rule withholds the **3 catastrophic deep-gap legs** (loss avoided +79¢ — ROCBUE −57, KREZHE −22, plus the unpriced PUTJEA) for a collateral cost of just **−6¢** (2 completed pairs, 1 winning naked) → **net +73¢**. Every tighter tolerance **loses money**: at T=0 the guard forfeits **162 completed pairs (−365¢) and 96 winning naked (−248¢)** to avoid −232¢ — because most completed pairs' first fills momentarily show the sibling ask above the cap before it drops. The median gap is 1¢; guarding it nukes the book. The guard is worth building **only at the deep tail** (T≈10), where infeasibility is genuine and permanent.

## Named

| game · filled | entry | sibling | cap | sibling ask (bid, spread) | reach | **gap** | time | naked P&L |
|---|--:|---|--:|--:|--:|--:|---|--:|
| PUTJEA · JEA | 64 | PUT | 35 | 75 (21, 54) | None | **40** | infeasible from placement | — |
| ROCBUE · ROC | 73 | BUE | 26 | 78 (8, 70) | 82 | **52** | infeasible from placement | -57 |
| KREZHE · KRE | 74 | ZHE | 25 | 86 (8, 78) | 48 | **61** | infeasible from placement | -22 |
| BORDIM · DIM | 47 | BOR | 52 | 53 (50, 3) | 64 | **1** | infeasible from placement | -13 |

- **PUTJEA · JEA** (entry 64) — PUT trades **75** (bid 21, spread 54), cap 35 → gap **40**, infeasible from placement (ask 93 at rest). The naked JEA long is unmarked (no certified close). The CAP_UNFEASIBLE archetype: a rich wide dog the cap never touches.
- **ROCBUE · ROC** — the worst loser (**−57¢**): bought the favorite at **73**, BUE (dog) at ask 78 / spread 70, cap 26, gap **52**. ROC collapsed to a certified close of 16. Never hedgeable (73 + 78 = 151).
- **KREZHE · KRE** (−22) gap **61** and **BORDIM · DIM** (−13) gap **1** — DIM is the marginal case (sibling BOR ask 53 just over cap 52); its small −13 is exactly the kind of leg a tight guard would wrongly chase.

## Conservation

134 CAP_UNFEASIBLE legs. Gap median 1¢ / max 61¢ / mean 2.6¢. Time structure 132 infeasible-from-placement / 2 drift. Per-category naked P&L ATP_CHALL −28 / ATP_MAIN −138 / WTA_CHALL +6 / WTA_MAIN −95. Guard net by T: T0 -381 · T2 -23 · T3 -18 · T5 -28 · T10 +73. Source V41 MARKET a30f5ccd, certified closes 57daf3c1, sibling books from fit-local tapes.