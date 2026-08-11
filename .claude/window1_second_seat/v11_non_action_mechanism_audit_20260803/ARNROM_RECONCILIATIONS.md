# Two reconciliations — arnrom_marks_v47 @ 528d75e4 [ANALYTICAL_ESTIMATE]

Analysis seat only. Read-only. Measurement only — no re-scoring, no repair proposals.

## ① Duplication — verified; mechanism = (b), at source

Fable's parse verifies exactly: **470 ARNROM action rows = 235 unique (receipt, kind, leg, ts) keys × exactly
2** — multiplicity distribution {2: 235}, per kind PLACE 64→32 · REPRICE 214→107 · WITHHOLD_START 62→31 ·
LIFT 62→31 · CANCEL 60→30 · FILL 4→2 · PAIR_ARM 4→2. Within every pair the rows differ in **exactly one
field: `mode`** — one row `MARKET_UNION_REACH`, one row `STRICT_PRINT_CROSS` (FILL rows additionally differ in
`fill_class`). The extraction did **not** join ACTION_TRACE with the ledger (it read the trace alone);
**the ACTION_TRACE itself double-writes at source** — every decision is emitted once per scoring lane. Whole
trace: **1,220,114 rows = 590,455 keys × 2 + 39,204 keys × 1** (the singles are lane-specific rows, dominantly
fills crediting in one lane only).

Prior artifacts whose counts consumed raw ACTION_TRACE tallies, inflation bounded:

- **`12d67c8a` read-organ forward-truth** — consumed the dev V47 trace raw: the "1,208,014 candidate receipts /
  ~1.06 M scored" counts are **≈2× inflated** (≈604 k unique decisions). Both lanes carry identical
  (ts, state), so **every rate, accuracy, and confusion share is invariant**; only the ns halve.
- **`b26cf548` sealed top-3 packs** — RECEIPT_TIMELINE_V1 row counts (BARLEC 97 / ISOMUK 100 / PETMCD 164)
  are **≈2× inflated** (sealed trace dual-writes identically); timeline content/order unaffected.
- **`a20e1a85` top-10 tail monotone check** — consumed sealed-trace target *sequences*; duplicates are adjacent
  identical targets, so the monotone (≥) verdicts and all stamps are **invariant**.
- **`528d75e4` arnrom_marks_v47 itself** — the artifact under audit: 470 → 235 unique decisions.

No other committed artifact consumed raw trace tallies (all others read event/regret ledgers).

## ② Floor contradiction — the table row is wrong-high; anchor mismatch named

**d3db740f's floor definition as implemented** (`causal_reach.py`/`causal_reach2.py`): per-leg trigger by
family — *tracking* = first two-sided book; *persistent_join* = an **analytic reconstruction** from the
fit-local tape: within a contiguous `bid == reach-level` run of ≥300 s containing a seller-hit, trigger =
`max(run_start + 300 s, first seller-hit ts)`; *pulse* = second ask-divot visit. Window = the fit-local QR
span. Channels = `min(deepest post-trigger true trade, deepest post-trigger ≥10 s-dwelled ask)`, with
**strict `ts > trigger`**.

**Why ARN returned 56 against a lawful 50 fill**: ARN's analytic join trigger resolved to **1783875407 — the
timestamp of the completing 50¢ print itself** (the seller-hit that anchors the analytic trigger *is* the fill
print). Strict-after then excluded that very print, leaving 56 as the post-trigger minimum. The executable's
join stood **earlier** (its own receipts show the rest standing before 16:56:47), so V47 lawfully credits the
50. Two anchor mismatches, named: **(i)** the analytic trigger is event-anchored to the reach/seller-hit
moment rather than the executable's actual stand time; **(ii)** the strict-after inequality excludes the
anchoring print. The table row is **wrong-high** for any leg whose analytic trigger coincides with (or
postdates) its completing print.

**The census — the impossible set (entry < causal_floor), all credited dev legs:**

| | value |
|---|--:|
| V47 dev credited legs | **1,138** |
| with a causal_floor in the d3db740f table | 867 |
| **impossible set: entry < causal_floor** | **213** (24.6% of the 867) |

Per category (impossible / with-floor): ATP_CHALL 77/378 · ATP_MAIN 57/198 · WTA_CHALL 21/115 · WTA_MAIN 58/176.

Gap (causal_floor − entry) distribution over the 213: **p25 1¢ · median 2¢ · p75 5¢ · max 70¢**.

## Conservation

① 470 rows = 235 × 2 (dist {2:235}); whole trace 1,220,114 = 590,455×2 + 39,204×1; 4 consuming artifacts
listed with bounds, all rates invariant. ② 1,138 credited = 867 with-floor + 271 without; impossible set 213,
per-category splits sum 213; gap dist over exactly the 213. Sources: V47 fb74c8b8 ACTION_TRACE +
MARKET_EVENT_LEDGER, CAUSAL_LEG_TABLE d3db740f. ANALYTICAL_ESTIMATE throughout; measurement only.
