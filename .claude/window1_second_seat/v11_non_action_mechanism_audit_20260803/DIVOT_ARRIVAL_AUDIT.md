# Divot arrival audit — did the divots come, and what refused them

Analysis seat only. Read-only. Every **riser-side unfilled leg** in the sealed 82 (`b26cf548`, read RISING) and the dev one-eyed 240 (`e177c2fb`, frozen CLIMBING): the leg's full BBO ask series scanned for **dip-and-resume divots after the rest lawfully stood** (`d1ac9497` method: an ask run lower than both neighbors), refusal graded on the **deepest post-stand trough T** vs the rest R and the pair cap. Sealed tapes from the exam's private capture (AUG series) + the holdout-exam tapes (JUL series). Machine artifact: `…/DIVOT_ARRIVAL_AUDIT.json`.

## The refusal census

| refusal class | sealed (12) | ¢ | dev (62) | ¢ |
|---|--:|--:|--:|--:|
| **NO_DIVOT_CAME** | 10 | 0 | 41 | 0 |
| CAP_BOUND | 1 | 0 | 17 | 0 |
| TROUGH_ABOVE_REST | 1 | 1 | 2 | 3 |
| EXPECTED_FILL_ANOMALY (quote-trough ≤ rest, trades-as-truth uncredited) | 0 | 0 | 2 | 6 |
| **total** | **12** | | **62** | |

## The verdict — absence, not refusal

**The divots mostly never came.** 51 of 74 riser-side unfilled legs (**69%**) saw **zero** post-stand dip-and-resume on their ask — the VRB recurring-divot shape is the exception on losing risers, not the rule. Where a divot DID arrive (23 legs), the **pair cap refused 18 of them** (sealed 1 + dev 17: the trough undercut the natural rest but sat above the 99−sibling-entry cap) — and the cents at stake are **~0**: even filled at the trough, sibling-entry + trough lands over par. TROUGH_ABOVE_REST is a 3-leg tail (+4¢); the 2 EXPECTED_FILL_ANOMALY legs are ask-troughs at/below the rest that trades-as-truth lawfully didn't credit (no trade printed there).

## The V50 preview

Of the 18 CAP_BOUND refusals, **8 dev + 1 sealed = 9 troughs fit under the cap IF the sibling fill had paid its own floor** — the first-fill-discipline lever again admits half the refused divots mechanically. But the census prices them at ~0¢ (over-par pairs): **V50's divot-side payoff is admission, not cents** — the money case for first-fill discipline rests on the sealed 31/45 richness-kills, not on divot recovery.

## Named exemplars per class

- **26JUL27MONMAZ·MON** (sealed, CAP_BOUND): trough 82¢ vs rest 80/cap 80, 1 divots, value 0¢
- **26JUL28POLDAL·DAL** (sealed, TROUGH_ABOVE_REST): trough 61¢ vs rest 60/cap 61, 5 divots, value 1¢
- **26JUL13BOUZHA·ZHA** (dev, TROUGH_ABOVE_REST): trough 74¢ vs rest 73/cap 75, 109 divots, value 2¢
- **26JUL15VILMAR·VIL** (dev, TROUGH_ABOVE_REST): trough 51¢ vs rest 50/cap None, 2 divots, value 1¢
- **26JUL13WINKIR·KIR** (dev, CAP_BOUND): trough 29¢ vs rest 27/cap 27, 25 divots, value 0¢
- **26JUL15LAJKRU·LAJ** (dev, CAP_BOUND): trough 69¢ vs rest 67/cap 67, 3 divots, value 0¢
- **26JUL19VUKGEA·GEA** (dev, EXPECTED_FILL_ANOMALY): trough 64¢ vs rest 64/cap None, 59 divots, value 5¢
- **26JUL13TIMANN·TIM** (dev, EXPECTED_FILL_ANOMALY): trough 41¢ vs rest 41/cap 41, 4 divots, value 1¢

## Conservation

Sealed 12 legs classified 12; dev 62 classified 62 — each exactly once. Divot method d1ac9497 (dip-and-resume ask runs), post-lawful-stand (join/first-action). Sealed tapes: exam private capture + holdout-exam-20260807; dev: fit-local. Sources b26cf548, e177c2fb, 2bae8931, fb74c8b8.