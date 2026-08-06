# Deep-pair hygiene census — is the deep bar skill or schedule contamination?

Analysis seat only. Read-only. Deep pair = strict completed with combined ≤95.
V34-W1 `e56d79a2`, V35 `0799fba`, V36 (state-directional). Machine artifact:
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/DEEP_PAIR_HYGIENE_CENSUS.json`.

## The census — per model

| model | deep ≤95 | exact | live_by | schedule | other | w/ terminal-collapse | **exact + clean** |
|---|--:|--:|--:|--:|--:|--:|--:|
| **V34-W1** | **34** | 9 | 14 | 11 | — | 6 | **9** |
| **V35** | 25 | 5 | 12 | 6 | 2 | 0 | **5** |
| **V36** | 20 | 7 | 6 | 6 | 1 | 0 | **7** |

- **(a) bell_confidence** — only **9 of V34's 34** deep pairs sit on an **exact** bell;
  25 (73%) rest on **estimated** right edges (14 live_by, 11 schedule_only). The window
  boundary those 25 are graded against is a guess.
- **(b) terminal collapse** — **6 of V34's 34** have a leg whose fill (≤9¢) sits inside a
  monotone seller-dump run of ≥3 descending prints spanning ≥10¢ into single digits: a
  **settlement-collapse catch**, not a pre-bell arbitrage. All 6 are in the *non-exact*
  bell games. The cheap leg's fill sits a median **149 min** from the (estimated) right
  edge — deep into the tail.
- **(c) re-grade on exact-bell alone** — the deep bar collapses to **9 (V34) / 5 (V35) /
  7 (V36)**, and every exact-bell deep pair is *also* collapse-clean (exact+clean = exact).

## Verdict — the deep bar is mostly schedule-window contamination

**The 34 is not robust Window-1 skill.** Strip the games whose bell is estimated and the
games that merely caught a settlement collapse, and **only 9 survive** — a **73%
haircut**. V35's 25 → 5 and V36's 20 → 7 tell the same story: the deep tail is
disproportionately schedule-only / live-by games where the "combined ≤95" is a product
of an uncertain right edge letting a late collapse print through, not a lawful pre-bell
fill. The honest deep bar, uncontaminated, is **single digits per model (9 / 5 / 7)** —
and on that clean bar V34 (9) ≥ V36 (7) ≥ V35 (5), the reverse of the raw-count ranking.

## Risen-top takes — the GANJAN-JAN class (V35, all strict completions)

Across all 264 V35 strict completions, **85 credited TAKES fired ≥5¢ above the leg's own
print-backed floor** — the machine bought a top after the evidence floor re-formed
*upward*, when a much cheaper print-backed floor already existed.

| metric | value |
|---|--:|
| risen-top takes | **85** |
| combined-price damage — median | **13¢** |
| p90 | ~50¢ |
| max | **85¢** (JACDA·JAC: took 93, floor 8) |
| **total combined damage** | **1,808¢** |

GANJAN·JAN is the archetype and present in the set (took **79** with a print-backed floor
of **1** → **+78¢**). Others: PALCOL·PAL 74/floor 1 (+73), HERALM·ALM 71/7 (+64),
BUEMAR·BUE 59/1 (+58). **1,808¢ of combined-price damage** is the cost of the take path
buying risen tops instead of resting for the floor — the same failure that vaporized
V34's deep pairs (part-1 autopsy: 18 take-fired-shallower legs), quantified across the
whole book.

## Conservation

V34 deep 34 = 9 exact + 14 live_by + 11 schedule; 6 terminal-collapse (all non-exact);
exact+clean 9. V35 deep 25 = 5+12+6+2; exact+clean 5. V36 deep 20 = 7+6+6+1; exact+clean
7. Risen-top takes 85 of 528 V35 credited legs; damage sum 1,808¢, median 13¢, max 85¢.
