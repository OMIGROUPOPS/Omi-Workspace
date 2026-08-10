# Standability v2 — the placement-window law

Analysis seat only. Read-only. v1 (`3dd57fba`) tested the ask **at the print instant** and called 46 PRINT_ABOVE legs ONLY_BY_PREDICTION. But the lawful test is a **window**: standable if best_ask > P at **any** moment before the completing print — a post-only bid at P placeable then, and once standing the later ask-descent to P **fills it by mechanics**. The *choice* of P is graded separately: **lawful-evidence** (a prior trade ≤ P, or the bid reached P) vs **bare prediction**. Machine artifact: `…/STANDABILITY_V2_PLACEMENT_WINDOW.json`.

## The 46 re-cut

| verdict | legs |
|---|--:|
| **WINDOW_LAWFUL_EVIDENCE** (window existed + evidence for P) | **20** |
| WINDOW_BARE_PREDICTION (placeable, but no evidence for choosing P) | 6 |
| NO_WINDOW (ask never > P before the print — a buyer-lift at the ask) | 20 |
| **total** | **46** |

**v1 was too strict.** 20 of the 46 'predictions' had a **real placement window** with evidence for the level — the ask sat above P for a long stretch, so a lawful bid at P could have stood and been filled by the eventual descent. Only **20 are truly unplaceable** (the print was a buyer-lift at the ask, no prior window); **6** are placeable but bidding at P would have been a guess.

## The window was long where it existed

For the 26 legs with a window, its duration: min 0h01m · p25 1h07m · **median 3h22m** · p75 4h46m · max 33h43m. **The ask sat above P for a median of ~3 hours** — placement was never the constraint; the instant-check simply looked at the wrong moment.

## Per category (the 46)

| category | LAWFUL_EVIDENCE | BARE_PREDICTION | NO_WINDOW |
|---|--:|--:|--:|
| ATP_CHALL | 10 | 4 | 12 |
| ATP_MAIN | 0 | 0 | 1 |
| WTA_CHALL | 8 | 2 | 3 |
| WTA_MAIN | 2 | 0 | 4 |

## Recoverable under window-law — the 458 ceiling restated

Adding the WINDOW_LAWFUL_EVIDENCE legs (whose games now have all missing legs lawfully standable):

| | games | locked ¢ |
|---|--:|--:|
| v1 recoverable (ask > P at print) | 62 | 1,064 |
| **v2 recoverable (window-law)** | **81** | **1162** |

| category | recoverable games | locked ¢ |
|---|--:|--:|
| ATP_CHALL | 34 | 324 |
| ATP_MAIN | 10 | 210 |
| WTA_CHALL | 30 | 465 |
| WTA_MAIN | 7 | 163 |

**The ceiling restated: 396 captured + 81 lawfully-recoverable = 477 toward 700** — up from 458 (the window-law adds 19 games the instant-check wrongly wrote off). Still **223 short of 700.** The residual is the 20 NO_WINDOW buyer-lifts + the PRINT_BEFORE/ONLY_BY_PREDICTION remainder — unreachable by any lawful resting bid, recoverable only by foreknowledge or fee-negative taking. **The honest lawful ceiling on this tape is ~477, not 700.**

## Conservation

46 PRINT_ABOVE ONLY_BY_PREDICTION legs re-cut, each one verdict: WINDOW_LAWFUL_EVIDENCE 20 + WINDOW_BARE_PREDICTION 6 + NO_WINDOW 20 = 46. Recoverable under window-law 81 games / 1162¢ → ceiling 396+81=477 (short 223). Window median 3h22m. Ruler: CANON traded-at-level + trades-as-truth, placement-window. Refines 3dd57fba. Source V48 e073c606, tapes/prints fit-local.