# STRICT_ASK_CREDIT footprint — the rule's damage, and the fix priced

Analysis seat only. Read-only. V45 (`3bda0a54`). The reprice-down is gated by the **V36 FALLING NO_CHASE / STRICT_ASK_CREDIT_BEFORE_REPRICE** rule: the tracking rest walks down only to a **strict-ask-credited** low, so when flow gaps below without a dwelled/credited ask, the rest is frozen above it. Machine artifact: `…/STRICT_ASK_CREDIT_FOOTPRINT.json`.

## (1) The footprint — the rule's true class is 50, not 4

Every uncredited leg where **causal flow passed BELOW the held rest (Cz < R)** and no credit subsequently fired — the reprice-down was suppressed and the flow was lost. **50 legs.** The corrected autopsy called only **4** of them CHAIN_L5_STALE_REPRICE; the other **46** are misattributed:

| current chain-link | footprint legs |
|---|--:|
| L6 PRESENT BUT NO COUNTERPARTY | 42 |
| L5 STALE REPRICE | 4 |
| L2 MISREAD | 4 |
| **total** | **50** |

**42 sit in L6_NO_COUNTERPARTY** — they *look* like a market-no (rest present, seller 'didn't come'), but the flow **did** come, 1-2¢ below the frozen rest, and the rule held the rest up. The L5 threshold (> 3¢ divergence) sees only the 4 deep cases; the rule's real reach is the **50-leg** band. Law-vs-rest **divergence integral = 105¢**; causal flow passed the suppressed zone on **50/50** (the PANFAL signature, by construction). By category: ATP_CHALL 28 · ATP_MAIN 8 · WTA_CHALL 6 · WTA_MAIN 8.

## (2) The fix — gap-credit clause (ANALYTICAL_ESTIMATE)

**Treat a single-tick ask gap ≥ 3¢ as its own credit event**, so the rest may walk down through a gap to the causal level and fill there. Two columns:

| | value |
|---|--:|
| **GAINED — legs unfrozen** | 50 |
| **GAINED — pairs completed** | **39** |
| **GAINED — locked ¢** | **+121** |
| ADVERSE — naked unfrozen legs (into the falling tail) | 11 |

Locked by category: ATP_CHALL 63 · ATP_MAIN 20 · WTA_CHALL 16 · WTA_MAIN 22.

**The falling-tail check** — unfrozen fill (Cz) minus the leg's eventual low; positive = the book kept crashing *below* the fill (a caught knife):

| set | n | median ¢ | p75 | max |
|---|--:|--:|--:|--:|
| all unfrozen | 50 | +28 | +40 | +71 |
| **naked only** | 11 | **+44** | +50 | +71 |

**The gain is hedged, the risk is not.** 39 of 50 unfrozen legs land in **completed pairs (+121¢ locked)** — for those the falling tail is irrelevant (the pair is locked regardless of the crash). The **11 that stay naked** carry it hard: median **+44¢ above the eventual low** — the rest walked down into a book that kept falling ~half the market. **Recommendation: gate the gap-credit on pair completion** — take the unfreeze only when it completes a hedged pair, banking the +121¢ and refusing the 11 naked knives.

## Named — PANFAL·PAN catches the 45–46 flow

PAN: held rest **54¢**, but the causal flow reached **45¢** (qualified-ask low 45¢) — a **9¢ divergence**, the deepest of the footprint (a genuine CHAIN_L5_STALE_REPRICE). The gap-credit clause walks PAN down to **45¢**; with FAL at its causal 47¢ the pair completes at **92¢ (locked 8¢)**. PAN's eventual low was 1¢, so naked it would be a catastrophic knife — but **paired with FAL it is locked**, the clean case for the pair-gated fix.

## Conservation

Footprint 50 uncredited legs (Cz < R), sum-by-link 50; vs 4 genuine L5. Divergence integral 105¢. Fix: 50 unfrozen → 39 pairs / +121¢ locked; 11 naked with falling-tail median +44¢. ANALYTICAL_ESTIMATE. Source V45 3bda0a54, causal reach d3db740f, prints fit-local, closes 57daf3c1.