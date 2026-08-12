# MERDRO close-out — denomination · stability onset · queue-vs-print [ANALYTICAL_ESTIMATE]

Analysis seat only. Read-only. Machine records only. Machine artifact: `MERDRO_CLOSEOUT.json`; trajectory
CSVs: `game_tape_packs/26JUL16MERDRO/MER_stability_trajectory.csv` · `DRO_stability_trajectory.csv`.

## PART A — YES/NO price-field audit → **DENOMINATION CLEAN**

The two floor trades, Kalshi's official record exactly as served, beside our tape:

| trade_id | leg | Kalshi `yes_price_dollars` | Kalshi `no_price_dollars` | our `price_cents` |
|---|---|--:|--:|--:|
| c6b0dd11-f7a3-5aad-4d5f-4aab58733c31 | MER | **0.0600** | 0.9400 | **6** |
| 9ce4c803-dcc7-45e4-8a5b-36ec014a7f5a | DRO | **0.0600** | 0.9400 | **6** |

By code line: the @ `db470ec8` diff compared **`yes_price_dollars`** (`tape_diff.py`:
`p=int(round(float(x["yes_price_dollars"])*100))`); the recorder writes **the YES price** into `price_cents`
([window1_public_tape_export.py:100-102](../../arb-executor/analysis/window1_public_tape_export.py) —
`price = dollars_to_cents(row.get("yes_price_dollars"), "yes_price_dollars")`, fallback integer `yes_price`
at lines 104–105, hard `ExportError` if no YES price; written at line 118). Ours = yes_price in both places.
**Stamp: DENOMINATION CLEAN — continuing.**

## PART B — stability onset, MERDRO (trajectories; no thresholds, no verdicts)

Method: per-minute grid over the W1 span (window `[1784150048, 1784221200−edge]`, scheduled bell
`1784221200` derived from machine t_minus fields). Shift point per candidate = the neutral two-segment
least-squares split (argmin SSE) of that series — arithmetic, not a chosen threshold; the operator rules
which candidate qualifies. Full series in the trajectory CSVs (spread · bid/ask dwell · book-change cadence
30-min · trade cadence + median size 60-min · |mid-sum − 100|).

**The side-by-side shift table** (T-minus = minutes before scheduled bell; before/after = segment means):

| leg | candidate | shift T−min | before | after | post-onset traded floor |
|---|---|--:|--:|--:|--:|
| DRO | spread | 1,124 | 70.2 | 1.1 | 39 |
| DRO | quote cadence | 1,131 | 858.5/30min | 105.1 | 39 |
| DRO | mid-sum dev | 1,074 | 1.72 | 0.48 | 39 |
| DRO | ask dwell | 704 | 1,135 s | 6,859 s | 39 |
| DRO | bid dwell | 691 | 1,089 s | 6,542 s | 39 |
| DRO | trade cadence | 223 | 10.5/hr | 81.2/hr | 40 |
| MER | spread | 1,124 | 68.8 | 0.8 | 48 |
| MER | mid-sum dev | 1,074 | 1.72 | 0.48 | 48 |
| MER | trade cadence | 676 | 51.1/hr | 22.1/hr | 60 |
| MER | quote cadence | 607 | 85.7/30min | 33.5 | 60 |
| MER | bid dwell | 412 | 2,201 s | 16,500 s | 60 |
| MER | ask dwell | 322 | 1,745 s | 10,643 s | 60 |

Beside the **formation floor of 6¢**: the 6¢ prints landed at T−1,183 (MER) and T−1,172 (DRO) — **before
every candidate's onset on both legs.** Post-onset traded floors run **39–40 (DRO)** and **48–60 (MER)**
under every candidate. Reported as trajectories and floors only; no verdict drawn.

## PART C — queue-vs-print, both formation fills (arithmetic only)

| leg | trade | print size | displayed bid size at 6¢ (book row at/just before print) | stamp |
|---|---|--:|--:|---|
| MER | c6b0dd11… @ T−1,183 | 26.56 | **217.0** (row ts 1784150210, book 6/94) | **QUEUE_IMPROBABLE** — 26.56 < 217; a late joiner watches it absorbed ahead |
| DRO | 9ce4c803… @ T−1,172 | 57.21 | **218.0** (row ts 1784150832, book 6/93) | **QUEUE_IMPROBABLE** — 57.21 < 218 |

Both formation fills printed into a displayed queue ~4–8× their size. The replay credits are lawful under
trades-as-truth, but a rest that *joined* the 6-bid (rather than opened it) would in expectation have watched
both prints absorbed in front of it. Stated with the numbers; no re-scoring performed.

## Conservation

Part A: 2 trades × both Kalshi price fields, 2/2 ours=yes. Part B: 12 shift rows = 2 legs × 6 candidate
series (dwell contributes bid+ask); every row carries before/after and a post-onset floor; grid gaps inherit
the pack's flagged recorder gaps (quiet-or-outage undistinguishable, not smoothed). Part C: 2 stamps, both
QUEUE_IMPROBABLE. Sources: Kalshi public API (2026-08-12 pull), game_tape_packs @ `c09bde99`, recorder source
`window1_public_tape_export.py`, V49b staged ledger anchors. ANALYTICAL_ESTIMATE.
