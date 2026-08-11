# The dipless 43 — raw-tape verification, no episode machinery

Analysis seat only. Read-only. The 43 no-dip riser legs (`9ee14bf5`) re-derived with the same detector, then audited at **full tape resolution**: every BBO ask change, every trade print (fit-local + holdout + exam repull), prints below the displayed ask, and the honest floor vs our rest. Machine artifact: `…/THE_DIPLESS_43_RAW.json` (per-leg rows: ask changes, distinct levels, min ask, time within 1/2/3¢ of the low, print counts/lows, below-ask counts).

## The verdict census

| verdict | legs |
|---|--:|
| **GENUINELY_STATIC** (ask never moved below its start; nothing traded under it) | **17** |
| **TRADED_THROUGH** (prints below the displayed ask) | **14** |
| **NO_POSTSTAND_RECORD** (the rest stood at/after the tape's end — vacuously 'dipless') | **12** |
| MICRO_TOUCHED | 0 |

## The episode ruler — stamped PARTIAL_UNDERCOUNT, but the collectability verdict holds

Of the **31 legs with a post-stand record**, **14 (45%) TRADED_THROUGH** — prints landed below the displayed ask, invisible to any ask-episode detector. The ruler under-counts *touches*. **But it does not under-count collectability**: of the 14 traded-through legs, **only 1 had its honest floor at-or-below our rest** — the through-prints landed **1-7¢ above the rest** (BEN +2, BRA +4, PAR +5, ROD +2, SCH +1, DAL +2, ECH +3, ZHU +7…). Deep flow through the book, never deep enough to touch us. The 17 GENUINELY_STATIC legs are absolute: **0 ask changes, 1 distinct level** the entire post-stand span.

## The stand-too-late 12 — a new honest class

**12 legs have no post-stand tape at all** (26JUL12CHAJON, 26JUL13BOUGAN, 26JUL14SQUKUM, 26JUL16BICCAS, 26JUL17DRAGEA, 26JUL20JOHAGU, 26JUL12ALTGAS, 26JUL12DROBLO, 26JUL13RINAST, 26JUL13RISPOH, 26JUL14CARVON, 26JUL20TOTRUG) — the join armed at or after the record's end, so their 'dipless' verdict was vacuous. These belong to the L4/arming organ, not the dip-supply story: nothing could ever have filled them because the rest never stood inside the record.

## The dip-supply split, re-cut on raw touches

| class | legs |
|---|--:|
| genuinely static (no touch, no through-trade) | 17 |
| traded-through above the rest (uncatchable by ≤rest law) | 13 |
| traded-through at/below rest (the one real miss) | 1 |
| stand-too-late (no post-stand record) | 12 |

**The 9ee14bf5 conclusion survives raw verification**: the unfilled risers' problem is absence — of dips, of sub-rest flow, or of a standing rest at all. Exactly **one** leg in the 43 had raw flow reach our rest. The episode ruler is stamped PARTIAL_UNDERCOUNT for touches, HOLDS for collectability.

## Conservation

43 re-derived = 17 static + 14 traded-through + 12 no-post-stand-record (verdicts sum 43). Prints from fit-local + holdout-exam + exam repull (43/43 covered). Sources 9ee14bf5, f40ac8ea, tapes fit-local + exam private + holdout-exam.