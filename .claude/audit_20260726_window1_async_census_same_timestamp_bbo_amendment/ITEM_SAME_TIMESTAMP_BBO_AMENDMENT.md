# SAME-TIMESTAMP BBO AMENDMENT — three-receipt episode-total correction to b8840a01

**Cursor Codex is confirmed exactly, again. The three disputed episodes — CERKOL `06a93c92…`, CERKOL `8f0d3c80…`, FRUKRE `3e4c49d6…` — are all UNLAWFUL (X=17, d1=0, contemporaneous bid=17, d2=0, combined delta 0). Counting them requires reusing an older same-second bid=18 row after 22 (CERKOL) / 17 (FRUKRE) newer lawful rows exist — forbidden. Episode totals are superseded: 3,229 → 3,226 (macro-hold) and 3,278 → 3,275 (macro-micro). Every event-level finding survives unchanged. The recurring-X-level figure 18/25 is additionally found NON-REPRODUCIBLE from b8840a01's artifacts and is superseded by a receipt-backed recomputation: 27/34.**

Date: 2026-07-26 · Branch: `audit/window1-independent` · Additions-only sole child of `b8840a01471eeb30a0f66e786c19ef0378c7dd83` · Auditor: independent CC session
Scope: exactly the three disputed receipts, the episode totals they inflate, and the required recurring-X recheck. No census implemented; no scoring/tuning/ranking/holdout/live; prior audit files unmodified; frozen implementation under audit unchanged at `9220eba26b00a5b94e86d9c644adef16382942a0`.

## 1. The three receipts, row by row (raw guarded-cache-v3, preserved ordinals)

All three prints have X=17 on the sibling leg with d1=0, so lawfulness requires d2 < 0, i.e. contemporaneous bid ≥ 18.

| receipt | event / leg | print ts | latest lawful preserved row ≤ print ts | bid/ask | d2 | d1+d2 |
|--|--|--|--|--|--|--|
| `06a93c92-0d52-4040-1ed2-6882d5490b0a` | CERKOL / KOL | 1784015992.802679 | ordinal 218181 @ 1784015992.0 | **17**/18 | 0 | **0 — UNLAWFUL** |
| `8f0d3c80-128b-4359-4f43-1d9e5a6b57d1` | CERKOL / KOL | 1784016002.654942 | ordinal 218181 @ 1784015992.0 | **17**/18 | 0 | **0 — UNLAWFUL** |
| `3e4c49d6-a936-45a0-6577-5f2fdefe62b9` | FRUKRE / FRU | 1784613175.116969 | ordinal 58380 @ 1784613175.0 | **17**/18 | 0 | **0 — UNLAWFUL** |

The only way to obtain d2=−1 is the **older favorable row at the same whole-second timestamp**: CERKOL ordinal 218159 @ 1784015992.0 (bid 18/ask 19) with **22 newer lawful rows** standing between it and the print; FRUKRE ordinal 58363 @ 1784613175.0 (bid 18/ask 19) with **17 newer lawful rows** standing. Reusing an earlier bid after a newer lawful BBO exists is forbidden by b8840a01's own §1 law. At CERKOL the rows immediately at/after the print are locked 17/17 (unlawful) — but the latest *lawful* row is already bid=17, so no lawfulness detour reaches 18. Full row receipts: `DISPUTED_THREE_EPISODE_RECEIPT.json`.

## 2. Superseded episode totals

| | macro_hold | macro_micro |
|---|--:|--:|
| b8840a01 published (authoritative enumerator) | 3,229 | 3,278 |
| **amended (lawful, receipt-backed)** | **3,226** | **3,275** |
| delta | −3 (CERKOL −2, FRUKRE −1) | −3 (CERKOL −2, FRUKRE −1) |

## 3. Why b8840a01's validation failed (required explanation)

b8840a01 ran two paths and compared them — then **selected the wrong one**. Its raw scanner produced the lawful counts (CERKOL 10, FRUKRE 4; totals 3,226/3,275; these are the very `episodes` fields still present in its own `CONTEMPORANEOUS_EPISODE_CENSUS.json`). Its "authoritative enumerator" broke same-timestamp ties to an earlier preserved ordinal, resurrecting the stale bid=18 rows at the same whole second, and produced CERKOL 12, FRUKRE 5 (totals 3,229/3,278). Facing the 3-episode divergence, the amendment declared the scanner an "undercount" and adopted the enumerator — inverting the correct resolution. The "independent third path" that reported "matched" confirmed only VUKBRO and DODDEL, neither of which is a divergent event, so the disagreement was never adjudicated at the receipt level. The defect class is the same one the VUKBRO amendment was written to kill (stale favorable reference bids), now at same-second granularity: **among equal-timestamp preserved rows, only the last preserved ordinal is the market's standing book.**

## 4. Independent reproduction (this amendment)

A fresh enumerator built only from the raw guarded-cache-v3 files and b8840a01's §1 law reproduces **all 47 survivor rows exactly at the scanner values** (47/47; including all six strict-ask-evidence events), reproduces every `earliest_*` first-recovery tuple (0 mismatches), finds the three disputed receipts in **zero** qualifying sets, and confirms VUKBRO at exactly 1 lawful episode. A second, independent selection path (bisect + reverse lawful scan) re-verified the BBO row choice of **all 6,501 qualifying episodes: 0 selection mismatches, 0 older/favorable selections remaining**. Conservation holds throughout (totals = Σ rows; recovered = survivor rows; recovered + residual = total; evidence split = recovered). Receipts: `CONTEMPORANEOUS_BBO_SELECTION_CENSUS.json`, `INDEPENDENT_RAW_ROW_VALIDATION_RECEIPT.json`.

## 5. Event-level findings — preserved (verified, not assumed)

Recovered naked **22/237 and 25/240** (CERKOL keeps 10 lawful episodes, FRUKRE 4 — membership unaffected); residual **215/215**; first-recovery split **16 print + 6 strict-ask / 19 print + 6 strict-ask** (both disputed events' earliest recoveries predate the disputed prints by hours); no-fill union **65/336 and 68/340** (52/54 both, 13/14 one, 271/272 neither) — carried forward unchanged because the three receipts belong to naked events and touch no no-fill event; **VUKBRO = 1 lawful episode**.

## 6. Recurring-X recheck (required) — 18/25 superseded by 27/34

X=17 was never a lawful recurring X-level: the lawful X sets are CERKOL {19, 21, 22} and FRUKRE {21, 24}, and the frozen ledger has **no observation at all** for X=17 on either event (`first_observation_timestamp = null`). Removing the three episodes therefore removes no lawful X-level. However, the recheck exposed that b8840a01's published 18/25 is **not reproducible from its artifacts**: it published no per-X detail, and no natural rule reaches it (all-evidence 27/34; print-evidence-only 21/28; earliest-recovery-X-only 15/17). The receipt-backed recomputation under the stated definition — distinct (event, X) sibling levels with ≥1 lawful in-window in-budget episode whose ledger `first_observation_timestamp` is ≤ the credited first-fill ts (hence rejected by V1's global-first rule) — gives **27 (macro-hold) / 34 (macro-micro)**, enumerated per (event, X) with ledger timestamps in the census artifact. A further **16/16** lawful-recurrence X-levels have **no ledger observation whatsoever** (invisible to V1 entirely — a strictly stronger form of the Item-1 defect), published separately and not blended into the 27/34.

## 7. Supersession statement

Superseded by this amendment:
- **b8840a01 episode totals 3,229/3,278 → 3,226/3,275** (`CONTEMPORANEOUS_BBO_SELECTION_CENSUS.json` controlling);
- **b8840a01 §3 sentence** "the scanner's first episode total (3,226/3,275) undercounted by 3 each … the authoritative enumerator + independent third path give 3,229/3,278, adopted here" → **refuted**: the scanner was lawful; the enumerator overcounted via forbidden older same-second bid rows;
- **b8840a01 recurring X-levels 18/25 → 27/34** (non-reproducible figure replaced by receipt-backed per-(event,X) enumeration; the 16/16 no-ledger-observation X-levels are published alongside as a separate class).

Preserved and still controlling: recovered naked 22/25, residual 215/215, first-recovery splits 16/6 and 19/6, no-fill union 65/68 (52/54, 13/14, 271/272), VUKBRO = 1, D=804, the additions-only lineage findings, and the structural Item-1/Item-3/Item-4 defects. Prior audit files were not modified.

## Final amended ruling

**BLOCKED — verdict unchanged, magnitude corrected a fourth time (downward, disclosed).** With same-timestamp ties lawfully resolved to the last preserved ordinal, **22/237 and 25/240 naked events** still recover a lawful in-window in-budget later opportunity across **3,226/3,275 episodes**, **27/34 sibling X-levels** (plus 16/16 ledger-invisible ones) were still discarded or unseen by the V1 global-first construction, and the no-fill counterfactual union stands at **65/68**. The four corrections (right boundary → first-leg reference bid → episode-level sibling BBO → same-timestamp ordinal selection) each shrank the magnitude and each was disclosed; the underlying V1 structural defect is untouched by all four. No strategy, score, benchmark, or deployment is validated; the no-fill union remains counterfactual.
