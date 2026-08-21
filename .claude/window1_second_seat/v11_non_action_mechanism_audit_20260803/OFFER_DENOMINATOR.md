# THE OFFER DENOMINATOR — one honest definition [VERIFICATION SEAT · ANALYTICAL_ESTIMATE]

**License (L18): LAW_INDEX read at `d449889e`; laws consulted: L0 · L6 · L11 · L17 · L20 · L22.**
Job 1 of the reinstated verification seat. Worked rows: `OFFER_DENOMINATOR_EXAM4_WORKED.csv`. Findings
banked same-commit in `FINDINGS_VERIFICATION_SEAT.md` (L20).

## The three circulating definitions

| | definition | basis | 804 count | what it is |
|---|---|---|--:|---|
| **A** | POST_ONSET_OFFER_CENSUS (`22441e05`) | interim-onset offer capture; games the census could BIND | 612 | a *coverage-limited* census: games its capture did not bind are `NOT_BOUND`, not "not offered" |
| **B** | Truth-table offered (`c0056976`, carried @ `96597c98`) | pre-match floors (verified span) summing <100, any margin ≥1¢, UNKNOWN_BELL excluded | **680** | the market fact on the sole window source (L11) |
| **C** | realized completes | whatever the exam credited | varies by grading | a numerator, never a denominator |

**Published denominator — ONE:**
> **completes-as-%-of-offered = (valid-fill completes: both legs credited inside the verified pre-match span, pair under par) ÷ (truth-table OFFERED_UNDER_PAR games, 680-basis, UNKNOWN_BELL excluded from both sides).** Margin ladders (≥10 / ≥5 / ≥3 / thin 1–2¢) are reported *beneath* it, never as the headline. Any-price (B) is the denominator; A is retired as a denominator (its `NOT_BOUND` class makes every ratio on it a coverage artifact).

On the 804: L17's V52l lineage = **311 / 680 = 45.7%** (cents 714 / 3,123 = 22.9%); V52r = 300/680 = 44.1%.

## Exam #4 (V53-04b Stage-1 @ `d449889e`), line by line — why "23 completes vs 4 offered"

Exam #4's F24 scoreboard binds its offer source to **definition A** and its closes to the old
`INDEPENDENT_CLOSE_AUDIT_1608` (`a30f5ccd`), not to the truth table. Three things happen at once:

1. **25 of its 30 games are `NOT_BOUND` in the 612-census** (+1 `FORMATION_ONLY_OFFER`). Only 4 are
   `OFFERED_POST_ONSET` → "4 offered". **20 of the 23 completes sit on NOT_BOUND games** and are invisible to
   the ladder. The "75% of offered" is 3 of 4 bound games.
2. **Under definition B, 28 of the 30 are offered** (TANHAV not-offered; PUTJEA UNKNOWN_BELL).
3. **The 23 completes are old-ruler completes. Re-stamped on the truth table: 15 VALID · 3 POST-BELL
   (KUMTUR both legs, HESKOT|KOT, ASTNOH|NOH) · 4 PRE-FORMATION (MERDRO both legs at 6¢ — the formation-era
   Delta88 prints, combined 12¢; DAHBAE|DAH 6¢; CERTRU|CER; EIGCAR|EIG) · 1 UNKNOWN-SPAN (PUTJEA).**

| honest reading of exam #4 | value |
|---|--:|
| offered (B) | 28 of 30 |
| valid completes | **15** |
| **completes as % of offered** | **15 / 28 = 53.6%** |
| naive "23/30" | 76.7% — not a lawful ratio (old-ruler numerator) |
| receipt's "75% of 4 offered" | a coverage artifact of definition A |

**Embargo stands until this commit lands; after it, any offered-percentage must cite definition B and a
valid-fill numerator.** Findings F-VS-001…006 banked.
