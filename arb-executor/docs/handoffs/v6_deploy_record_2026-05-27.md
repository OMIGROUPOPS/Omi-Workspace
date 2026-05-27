# v6 exit-table DEPLOYED — record — 2026-05-27

**v6 exit tables are LIVE** (all 4 categories), deployed ~01:18 ET on operator authorization. Supersedes the staged plan in `deployment_swap_2026-05-27.md` (which had used DISABLE→HOLD; corrected to **least-bad R** per operator).

## What was deployed
- **Disabled bands now carry the least-bad R** (the max-EV R even where total $ ≤ 0), encoded as `+Rc` (not HOLD). The bot enters and scalps the small capture, losing less than riding the full drop to settle.
- Corrected 4-cat totals (raw_max, in-sample — directional):

| cat | v6 total | disabled-band $: least-bad vs HOLD | bands |
|---|---|---|---|
| ATP_MAIN | $1,222.90 | −12.50 vs −369.70 (+357.20) | 31 |
| WTA_MAIN | $1,150.80 | −30.20 vs −211.00 (+180.80) | 28 |
| ATP_CHALL | $1,716.80 | −72.40 vs −294.20 (+221.80) | 33 |
| **WTA_CHALL** | **+$57.90** (back positive) | −24.50 vs −154.40 (+129.90) | 7 |

WTA_CHALL went **positive** with least-bad R → all 4 deployed (no pause needed).

## Deploy sequence executed
1. Backed up live tables → `{cat}_adaptive_exit_bands.bak_pre_v6.parquet`.
2. Promoted v6 → live `{cat}_adaptive_exit_bands.parquet` (md5-verified == v6).
3. Graceful restart (`deploy_v5_live.json`, 5ct), new log `live_v4_20260527_011823.log`, PID 3652029.

## Post-deploy verification (all PASS)
- `EXIT_TABLE_LOADED` = **31/28/33/7 bands** (v6; was 55/57/61/55). hold_cells 0/0/5/0.
- 0 tracebacks, mode LIVE, paper_mode absent, WS connected, main loop running, single instance (old PID gone).
- Reconcile preserved the **37 open positions**: adopted existing resting sells; re-posted exits for naked positions at the **new v6 R** (e.g. KASBAN cell 13 @ R46). **0 duplicate resting sells** (no over-exposure), `orphans` cleared 7→0 within ~80s (the 7 were pending entry buy bids, not sells).
- WS: 0 reconnects / 0 errors.

## Rollback (instant)
`cp {cat}_adaptive_exit_bands.bak_pre_v6.parquet {cat}_adaptive_exit_bands.parquet` for each cat, then graceful restart. Backups on the VPS.

## ⚠️ Standing operational item — FD limit resets on restart
`prlimit` (FD soft cap → 262144, the leak mitigation) is **per-process** and was reset to the default 1024 by this restart. I **re-applied it to PID 3652029**. **Every future restart needs prlimit re-applied** until the trade-tape FD leak is fixed in code (or the launch command sets `ulimit -n`). Flag for CC: close `analysis/trades/{ticker}.csv` handles, or add `ulimit -n 262144` to the tmux launch.

## Caveats (carried)
- v6 R from **raw_max** (optimistic) vs the prior deployed **size_qual_max_250** — live capture may underperform the in-sample numbers.
- Per-band R is in-sample (zone-aware on active, least-bad on disabled).

*Deployed live. Backups + rollback ready. Bot on v6 exit tables + per_regime_offsets_v2.csv entry (unchanged). Monitoring re-armed on the new log.*
