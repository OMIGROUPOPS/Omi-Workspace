# EPISODE-REFERENCE AMENDMENT — contemporaneous-BBO defect across the async opportunity census

**Cursor Codex is confirmed exactly. VUKBRO has ONE lawful episode, not eight: the print at 1783979002.68 has contemporaneous bid 42 (d2=−1, lawful); the seven later prints have contemporaneous bid 41 (d2=0, combined delta 0, unlawful). The defect was systemic — every prior episode used a sibling bid read from the thinned/normalized observation stream, which left stale, crossed books standing. Re-sourcing every episode's contemporaneous BBO from the raw guarded-cache snapshots (lawful, non-crossed, latest ≤ episode ts) changes every naked and no-fill aggregate. Corrected, self-consistent (0 mismatches), and published below.**

Date: 2026-07-26 · Branch: `audit/window1-independent` · Additions-only child of `30ca8e85fbfbc0cfa1e30d514c8c1769d006a82c` · Auditor: independent CC session
Scope: episode-level contemporaneous-reference construction across all naked and no-fill episodes. No census implemented; no scoring/tuning/ranking/holdout/live; prior audit files unmodified.

## 1. Episode-level reference law (cited and applied)

- **Strict-ask evidence:** bid and ask taken from the **same** lawful external book snapshot that proves ask < X; X = ask+1; d2 = X − that snapshot's bid; snapshot receipt and timestamp preserved.
- **Print evidence:** X = print price; contemporaneous bid = the **latest lawful non-crossed external BBO snapshot with ts ≤ print ts**, from the **raw guarded-cache snapshots** (not the thinned normalized stream); no later book; no earlier bid reused after a newer lawful BBO exists; ask never used as bid; carried last-trade never used as BBO; no coarse-second merge.
- **Lawful book:** best_bid > 0, best_ask > 0, best_bid < best_ask (crossed/locked/non-positive rejected).
- **Credited-leg reference (d1):** `FROZEN_X_EVIDENCE_LEDGER.book_and_chain_at_first_observation.nonself_best_bid_cents` for the credited (event, leg, price) — authoritative, unchanged from the prior amendment.
- **Qualification (integer cents, fee 0):** d2 = X − contemporaneous_bid; require **d1 + d2 + fee < 0** strictly; boundary positive-provable; episode ts strictly later than the credited first fill and ≤ guarded_cutoff_ts.

## 2. VUKBRO receipt-by-receipt (bound cache `fbacf0ab…16a07`)

Credited first leg **BRO** (PRICE_REACHED, X1=58, ts0=1783949040.451872), sibling **VUK**, d1=0, b2_max=−1 — identical for both candidates. All eight previously-claimed episodes, with contemporaneous BBO from the raw cache:

| # | print ts | X | contemporaneous BBO ts | bid | ask | d2 | d1+d2 | classification |
|--|--|--|--|--|--|--|--|--|
| 1 | 1783979002.679826 | 41 | 1783979002.0 | **42** | 43 | −1 | −1 | **LAWFUL** |
| 2 | 1783982271.157324 | 41 | 1783982271.0 | 41 | 42 | 0 | 0 | UNLAWFUL |
| 3 | 1783982271.157324 | 41 | 1783982271.0 | 41 | 42 | 0 | 0 | UNLAWFUL |
| 4 | 1783982271.157324 | 41 | 1783982271.0 | 41 | 42 | 0 | 0 | UNLAWFUL |
| 5–8 | 1783982633.379576 | 41 | 1783982631.0 | 41 | 42 | 0 | 0 | UNLAWFUL |

**VUKBRO lawful episode count = 1.** Exactly reproduces Codex. The prior `30ca8e85` claim of 8 lawful episodes (all bid=42/d2=−1) is refuted; its bid=42 was a stale, **crossed** book (bid 42 / ask 41 at 1783974571) held over by the thinned normalized stream for thousands of seconds.

## 3. Every naked episode recomputed from frozen raw sources — final counts

| | macro_hold | macro_micro |
|---|--:|--:|
| naked events | 237 | 240 |
| **recovered (lawful later in-window in-budget opportunity)** | **22** | **25** |
| qualifying in-window episodes | **3,229** | **3,278** |
| recurring X-levels (global-first predates first fill; lawful in-window recurrence) | **18** | **25** |
| residual no-lawful-opportunity | **215** | **215** |
| first-recovery evidence split | 16 print / 6 strict-ask | 19 print / 6 strict-ask |

Membership (22/25) is robust: both my raw scanner and the independent validator agree. The scanner's first episode total (3,226/3,275) **undercounted by 3 each** on two events (CERKOL, FRUKRE); the authoritative enumerator + independent third path give **3,229/3,278**, adopted here. Conservation: recovered + residual = 22+215 = 237 and 25+215 = 240 ✓; evidence split sums to recovered (16+6=22, 19+6=25) ✓.

## 4. No-fill counterfactual path census — recomputed contemporaneously (NOT unaffected)

My prior claim that no-fill was unaffected was **wrong**: the old no-fill scan used the same thinned/crossed books. Recomputed with contemporaneous raw BBO on both legs, symmetric print+strict-ask evidence, strict chronological ordering, strict combined negativity, no IC/simultaneous gate:

| | macro_hold | macro_micro |
|---|--:|--:|
| no-fill events | 336 | 340 |
| **either-orientation union** | **65** | **68** |
| both orientations | 52 | 54 |
| exactly one | 13 | 14 |
| neither | 271 | 272 |

(Prior `0abe9a3a` reported 81/84 either — refuted.) These remain **counterfactual**, not realized policy misses.

## 5. Self-consistency gate — PASS

An independent validator recomputed every one of the 47 survivor rows (bid0, d1, b2_max, contemporaneous sibling bid, d2, boundary status, strictly-later, ≤ cutoff, strict combined budget, episode count, earliest episode) from the raw cache via a second implementation path, plus a third-path confirm on VUKBRO and one survivor per candidate. **Row-level mismatches = 0.** Conservation into every published aggregate holds (recovered = survivor rows; episode totals = Σ per-survivor episodes; recovered + residual = total; evidence split = recovered). VUKBRO validates at exactly 1 lawful episode.

## 6. Supersession statement

Superseded by this amendment:
- **`30ca8e85` VUKBRO eight-episode claim** → **1 lawful episode** (`VUKBRO_EPISODE_RECONCILIATION.json`);
- **`30ca8e85` naked aggregates** 46/49 recovered, 4,622/4,948 episodes, 112/119 X-levels → **22/25, 3,229/3,278, 18/25**;
- **`0abe9a3a` no-fill union** 81/84 (and the "no-fill unaffected" statement) → **65/68** (52/54 both, 13/14 one, 271/272 neither);
- residual no-lawful → **215/215**; first-recovery evidence split → **16/6 and 19/6**.

Prior mechanical findings unchanged: sole additions-only lineage of the frozen census, D=804, 24/24 artifact hashes, null metrics/no-scorer, and the structural Item-1/Item-3/Item-4 code findings (global-first-X construction, unbounded exposure class, orientation-rows-not-events). `BOUNDARY_COMPLIANT_EVENT_LEVEL_CENSUS.json` and the `30ca8e85` receipts are **no longer controlling for any naked-recovery or no-fill count**; the `CONTEMPORANEOUS_EPISODE_CENSUS.json` in this amendment is controlling. Prior audit files were not modified.

## Final amended ruling

**BLOCKED — verdict unchanged, magnitude corrected a third time (downward, disclosed).** With contemporaneous BBO bound from the raw guarded cache, **22/237 and 25/240 naked events** still recover a lawful in-window in-budget later opportunity, **18/25 sibling X-levels** were still discarded by the V1 global-first-X rule, and **65/68 no-fill events** had a counterfactual asynchronous pair path — the structural time-axis-censoring defect stands. The magnitude has now been corrected three times (missing right boundary → stale first-leg reference bid → stale/crossed episode-level sibling BBO), each downward and each disclosed; the underlying V1 defect is unchanged. No strategy, score, benchmark, or deployment is validated; the no-fill union is counterfactual.
