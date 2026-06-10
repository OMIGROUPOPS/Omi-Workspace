# FLAGSHIP EPOCH — P&L baseline

**Epoch timestamp:** 2026-06-10 12:55:19 PM ET (2026-06-10T16:55:19Z)
**Source of truth:** live Kalshi API pull (read-only), cross-checked against bot state — ZERO discrepancies.

## Code / config provenance

| item | value |
|---|---|
| code commit (HEAD, running process) | `783a80e432ff15454d63408591c3bc3c8f040299` |
| executor | `arb-executor/live_v4.py`, pid fresh-booted 2026-06-10 12:51:53 PM ET |
| config | `config/deploy_v5_live.json` sha256 `03c62c71b9296a52a5bd7c85f34ce6a61d8bd49ac464b9d20d1093c87a9e3b02` |
| `completion_reprice` | ABSENT from config → flag OFF (PART-2 dormant; `completion_cells_loaded` absent from boot log, verified) |
| entry table | `docs/policy/per_regime_offsets_v2.csv` (36 rows, boot-verified) |
| exit tables (RUNNING) | UNCOMMITTED working-tree parquets, mtime 2026-05-27 13:39 — the known 2026-06-01 VC-discipline finding (coarse exit tables outside VC). Running shas: atp_chall `89bae1ff…`, atp_main `a9aee4ec…`, wta_chall `259c573f…`, wta_main `a91e7545…` |

## Account state at epoch (exchange truth)

| number | value |
|---|---|
| **Cash** | **$2,750.1042** |
| **Portfolio value at mark** | **$0.00** (zero open positions) |
| **Total** | **$2,750.1042** |

- **Open positions:** NONE (unsettled-position pull: 0 rows; all-positions pull: 0 nonzero rows).
- **Resting orders (entry bids AND exit sells):** NONE (exchange: 0; bot `state/live_v4_resting.json`: `{}`; boot reconcile: positions 0, resting 0, linked 0, unmanaged 0, orphans 0).
- **Cross-check bot vs exchange:** 0 vs 0 on positions, 0 vs 0 on orders → **zero discrepancies**.

## Pre-epoch line (the old era)

The two legacy positions previously carried open at 5c **do not exist on the exchange at
epoch time** — no open position of any era remains (0 unsettled rows), and no ≤6c buy
appears in the last 100 fills. They settled pre-epoch; their P&L is already realized
into the cash number above. **Pre-epoch carry: $0.00 — nothing to mark, the pre-epoch
line is closed.** Any later forensic attribution of that old-era P&L reports as a
separate pre-epoch line, never blended into post-epoch reads.

Pre-epoch same-day context (for log joins; all BEFORE the epoch cut): VASGUE-VAS round
trip today — buy yes 5 @ 30c (15:09:56Z, maker, fee 0) → sell 5 @ 37c (16:47:50Z, maker,
fee 0), closed flat pre-epoch.

**All P&L from this point measures against this epoch.**

## Addendum — ENOSPC incident immediately post-epoch (numbers unaffected)

At 16:57Z (2 min after the epoch pull) the freshly-restarted process died on
`OSError: [Errno 28] No space left on device` (disk hit 100%; tick-CSV flush failed,
then the logger raised inside ws_reader's handler). Root cause: 20G of
`analysis/premarket_ticks` raw tape CSVs on a 48G disk (steady ~91% floor per the
watchdog comment; today it topped out). Remediation: freed ~750M (journal vacuum +
npm/pip caches), bot relaunched 17:05Z (clean boot, reconcile 0/0/0); >3-day-old
tick/trade CSVs gzipped in place (lossless) in a nice'd background job. The epoch
numbers are unaffected: zero resting orders existed and the bot placed nothing while
down, so no fill or balance change was possible in the 16:55→17:05 gap. Open item for
the operator: tick-tape retention/archive policy (raw CSVs grow unbounded; the durable
parquet tape is built from them).

**Data-gap provenance (sidecar, not executor):** `tennis_odds` odds collection DOWN
**2026-06-05 12:36 PM ET → 2026-06-10 2:26 PM ET** (revived). The collector died Jun 5
(original cause unrecoverable — the old respawn's `tee` truncated its log); the `*/5`
respawn cron was a structural no-op the whole window (pgrep self-match: the cron
shell's own cmdline contains both the pattern and the tmux command text — fixed by
moving respawn into `deploy/respawn_tennis_odds.sh`, cc90c97d). `book_prices` daily
rows collapsed 83–129k/day → <1.1k/day (residual collectors) through the gap. FV/odds
history is unavailable for that window; v4 trading was unaffected (FV routing off).
Same latent respawn defect exists in the betexplorer / kalshi_price cron lines
(processes currently alive) — operator decision pending.
