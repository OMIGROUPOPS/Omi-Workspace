# EXIT_PRICE_CAP audit — is the 98c cap costing money? — 2026-05-27

Read-only. Verdict: **the cap is leaving ~1c on the table whenever it binds — and it's an uncalibrated legacy value. Recommend raising 98 → 99.**

## 1. The cap in code
- `EXIT_PRICE_CAP = 98   # never post exit above 98c` (live_v4.py:81). Applied at every exit post: `min(fill+R, EXIT_PRICE_CAP)` — `_v4_apply_exit` (2070), reconcile naked re-post (3462), legacy paths (2204/2229/3629).
- **git blame: `f7ad606` "live_v4.py: initial copy from live_v3.py (no logic changes)" (Druid Osullivan, 2026-05-25 02:02).** Only 2 commits ever touched the symbol (the copy, and the atlas-exit application). **⇒ the value 98 was inherited wholesale from live_v3 and never deliberately calibrated for v4.** The only rationale in code is the bare comment "never post exit above 98c" — no 98-vs-99 reasoning.

## 2. 98 vs 99 touch — cells 85–94c (1,042 tickers, all categories, from the g9-derived tape `raw_max` + depth-qualified `size_qual_max_250`)

| cell | N | raw reach 98 | raw reach 99 | sizequal reach 98 | sizequal reach 99 | P(99 \| 98, raw) |
|---|---|---|---|---|---|---|
| 85 | 147 | 90% | 88% | 89% | 87% | 98% |
| 86 | 111 | 86% | 85% | 86% | 85% | 99% |
| 87 | 116 | 87% | 85% | 85% | 85% | 98% |
| 88 | 114 | 86% | 85% | 86% | 85% | 99% |
| 89 | 105 | 85% | 84% | 84% | 84% | 99% |
| 90 | 95 | 91% | 89% | 89% | 89% | 99% |
| 91 | 99 | 94% | 93% | 94% | 93% | 99% |
| 92 | 75 | 92% | 91% | 91% | 89% | 99% |
| 93 | 91 | 90% | 89% | 90% | 88% | 99% |
| 94 | 89 | 94% | 93% | 94% | 92% | 99% |
| **AGG 85–94** | **1042** | **89.2%** | **88.0%** | **88.6%** | **87.5%** | **98.7%** |

**The decisive number: when price touches 98, it touches 99 ~98.7% of the time** (raw) — and **99 is realizable at ≥250 depth 98.8% of the time it touches 98** (`P(99|98, sizequal)`). The reach-98 vs reach-99 gap is only **~1.2 pp**. There is **no liquidity justification** for stopping at 98 — 99 is reachable *and* depth-fillable almost exactly as often.

## 3. Live v6 session (since restart) — sells at the cap
- Resting sells posted **at 98 (cap): 1** (still resting). **Below 98: 36** (20 exit-filled, 6 settled, rest resting).
- The cap **binds rarely in live** because most v6 R targets land below 98; it only bites the highest cells where `entry + R ≥ 99` (e.g. cell 94 + R5 = 99 → capped to 98; the Andreeva leg is the one currently at 98).

## 4. Recommendation — raise EXIT_PRICE_CAP 98 → 99
- **The cap costs ~1c every time it binds**, on ~88% of high-cell exits (the fraction that reach 99). Since 99 is reached AND depth-realizable 98.7–98.8% of the time that 98 is, capping at 98 forfeits a near-certain cent.
- **99, not 100, is the right ceiling** (100 = settlement; the bot must not post an exit at settlement). 99 captures the full pre-settlement value.
- **Risk of raising to 99 is negligible:** 99's reach rate (88.0%) trails 98's (89.2%) by ~1.2pp, so fills are nearly as frequent; the rare case (reaches 98, stalls before 99, then reverses) is ~1.2% — and even then the position rides to settlement (100 win / 0 loss) as it would today.
- **Magnitude:** binds only where `entry+R ≥ 99` (top cells). Across the 85–94 corpus, ~88% reach 99 → raising the cap captures +1c on essentially every winning high-cell exit that currently caps at 98. At live 5ct that's +$0.05 per such exit; small per-trade but free and strictly positive, concentrated in the highest-volume favorite cells.
- **This is a one-line change** (`EXIT_PRICE_CAP = 99`) — but it's a code change (not a parquet swap) and would only affect *new* exit posts after a restart (existing resting sells at 98 stay until refilled/reposted). Operator/CC decision; no change made here.

*Read-only audit. No code or config changed. raw_max/size_qual from the canonical tape; live counts from the v6 session log.*
