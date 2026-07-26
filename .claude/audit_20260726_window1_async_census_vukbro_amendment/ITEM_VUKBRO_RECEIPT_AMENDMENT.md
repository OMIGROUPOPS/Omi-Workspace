# VUKBRO RECEIPT AMENDMENT — reconciling the contradictory VUKBRO descriptions in the boundary amendment

**The three committed VUKBRO descriptions are reconciled. Controlling truth: d1 = 0, b2_max = −1, earliest lawful recovery = a print of X=41 against sibling bid 42 (d2 = −1) at 1783979002.68, 8 qualifying episodes — identical for both candidates. The `BOUNDARY_COMPLIANT_EVENT_LEVEL_CENSUS.json` VUKBRO row (d1=−1/b2_max=0/first_recovery 1783971964.6/52 episodes) is REFUTED. The root cause is a first-leg reference-bid derivation error that also shifts the amendment's naked aggregates; corrected authoritative counts are published here.**

Date: 2026-07-26 · Branch: `audit/window1-independent` · Additions-only child of `0abe9a3a48ebe12bcc965174b63fd2d4d5e4ea00` · Auditor: independent CC session
Scope: VUKBRO contradiction and the naked-recovery aggregates it exposed. No census implemented; no scoring/tuning/ranking/holdout/live; settled structural items untouched.

## 1. VUKBRO reconstructed per candidate from frozen sources

The frozen result ledger is unambiguous and identical for both candidates: **credited first leg BRO** (`fillable`, `PRICE_REACHED`, X1=58, qty=5, ts0=1783949040.451872); **VUK** the uncredited sibling. The authoritative contemporaneous reference bid is the frozen census's own `FROZEN_X_EVIDENCE_LEDGER.book_and_chain_at_first_observation` for BRO@58 = **bid 58 / ask 59**. Therefore, per candidate (macro_hold and macro_micro — bitwise identical):

- credited first-leg = BRO; sibling = VUK
- credited first-fill receipt `174ece05-…`, ts0 = 1783949040.451872, X1 = **58**
- latest lawful prior/contemporaneous bid (x-evidence) = **58**; fee = **0**; **d1 = 0**; **b2_max = floor(−0−1) = −1**
- guarded cutoff = 1783992600.0, positive-provable = **true**
- **8 qualifying sibling episodes**, all print-type, all X=41 vs contemporaneous bid 42 → d2 = −1, strict budget d1+d2 = −1 < 0, all strictly after ts0 and ≤ cutoff
- **earliest** = print X=41, bid 42, d2=−1, receipt `e7faf7a4-…`, ts **1783979002.679826** (≤ cutoff)
- five-contract capacity at the earliest episode: executed volume at/below X = 4,378.7 (reported separately from price reach; reach does not require it)
- no earlier qualifying episode exists under the correct b2_max=−1

## 2. Resolution of the three competing descriptions

- `BOUNDARY_COMPLIANT_EVENT_LEVEL_CENSUS.json`: d1=−1, b2_max=0, first recovery 1783971964.6, 52 episodes — **REFUTED**. Its permissive b2_max=0 came from a reference bid of 59; the authoritative x-evidence bid is 58. The 1783971964.6 point only qualified under the erroneous b2_max=0.
- `MANUAL_VERIFICATION_RECEIPT.json`: d1=0, b2_max=−1, `inwin_qualifying_first=null` — **d1/b2_max CORRECT; the null was wrong**, an artifact of a helper that inspected only strict-ask books (VUK's recovery is print-based).
- `ITEM_BOUNDARY_AMENDMENT.md` prose: print 41 / bid 42 / ts 1783979002.68 / d1=0 / b2_max=−1 — **CORRECT and affirmed**.

**Controlling truth = the narrative print description, for both candidates.** VUKBRO remains a lawful survivor; the corrected first recovery is later (elapsed ≈ 8.3 h, not 6.4 h) and the episode count is 8, not 52.

## 3. Direct raw recompute — invariants verified

Strictly later than the first fill ✓ (all 8 > 1783949040.45); ≤ guarded_cutoff_ts ✓ (all ≤ 1783992600.0); print and strict-ask provenance separate ✓ (all 8 are prints; VUK has no qualifying strict-ask at b2_max=−1); contemporaneous lawful positive-size BBO ✓ (bid 42/ask present per book); exact combined-headroom arithmetic ✓ (d1+d2 = 0+(−1) = −1 < 0); five-contract capacity reported separately from price reach ✓ (4,378.7 executed vol at/below X, not used to gate reach).

## 4. Aggregate consequence — the fix is systemic; aggregates change

The reference-bid error was not VUKBRO-specific: the amendment scan derived each credited leg's bid0 from the merged books+prints stream, which at coarse 1-second timestamps can select a same-second value off by one. Re-deriving **every naked event's** bid0 from the authoritative x-evidence contemporaneous book corrects d1/b2_max across the affected events. Corrected vs superseded (macro_hold / macro_micro):

| aggregate | superseded (`0abe9a3a`) | corrected authoritative |
|---|--:|--:|
| recovered naked events | 49 / 52 | **46 / 49** |
| qualifying in-window episodes | 5,603 / 5,929 | **4,622 / 4,948** |
| recurring X-levels (global-first predates first fill, lawful recurrence before right) | 117 / 124 | **112 / 119** |
| residual naked with no lawful later opportunity | 188 / 188 | **191 / 191** |
| first-recovery evidence split (macro_hold) | 42 strict-ask / 59 print | **21 strict-ask / 25 print** |
| **no-fill either-orientation union** | 81 / 84 | **81 / 84 (unchanged)** |

The no-fill union is unaffected: it uses an order-independent minimum d1 over each leg's own observations, with no credited-leg bid0 dependency.

## 5. Supersession statement

This amendment explicitly supersedes:
- the **VUKBRO row in `MANUAL_VERIFICATION_RECEIPT.json`** (the `inwin_qualifying_first=null` is wrong; d1=0/b2_max=−1 affirmed);
- the **VUKBRO prose/example in `ITEM_BOUNDARY_AMENDMENT.md`** (affirmed as correct, but restated here as controlling, with the elapsed time corrected to ≈8.3 h);
- the **VUKBRO row in `BOUNDARY_COMPLIANT_EVENT_LEVEL_CENSUS.json`** (d1=−1/b2_max=0/1783971964.6/52 — refuted);
- and, per Item 4, the **naked-recovery aggregates** of `0abe9a3a` (49/52, 5,603/5,929, 117/124) — **corrected to 46/49, 4,622/4,948, 112/119**.

`BOUNDARY_COMPLIANT_EVENT_LEVEL_CENSUS.json` is therefore **no longer controlling for the naked-recovery fields**; its no-fill union fields (81/84, 52/54 both, 29/30 one, 255/256 neither) remain valid. The original amendment files are left unmodified as required.

## 6. Final amended ruling

**BLOCKED — unchanged verdict, twice-corrected magnitude.** After binding the reference bid authoritatively from the frozen x-evidence book, **46/237 and 49/240 naked events** still recover a lawful in-window in-budget later opportunity, and **112/119 sibling X-levels** still had a lawful in-window recurrence the V1 global-first-X construction discarded — the structural time-axis-censoring defect stands. The magnitude has now been corrected twice (first for the missing right boundary in `0abe9a3a`, now for the reference-bid derivation), each time downward and each time disclosed. No strategy, score, benchmark, or deployment is validated; the no-fill union remains counterfactual.

Residual disclosure: sibling-episode bids are read from each observation's own chain state, so individual episode *counts* retain marginal coarse-second sensitivity; membership (≥1 qualifying episode) and earliest-recovery identification are robust where d2 margins are non-zero.
