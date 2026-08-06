# Boot gate — Stage A read-only audit

Status: **STAGE_A_COMPLETE_AWAITING_EXPLICIT_STAGE_B_WORD**. Stage B and Stage C were not authorized or started.

- VPS HEAD: `7036ace045c6ee0e45b9c4bdc956c54906d21afa`; branch: `blend/kalshi-occ-fallback`; Git drift rows: 12431.
- Drift split: 13 modified, 12418 untracked, 0 deleted.
- live_v4 processes: 0; recorder-like processes: 1.
- Resting exchange orders: 0; exit sells: 0 / 0 contracts; entry buys: 0 / 0 contracts.
- Unsettled positions: 0; exit coverage exact/under/over: 0/0/0.
- Installed crontab SHA-256: `a0476a5698250e5c00cb8d5b5eadcf8fbb927c518ce44d1002b14e7ae184deeb`; active live_v4 launch lines: 0.
- live_v4 HEAD blob / working blob / SHA-256 / bytes: `f1857199164664037fef41b024e60f27fa373548` / `c25cd3129248710a665d77eb815a9df6a93c9009` / `25698d80642524c70f39d850ef0a7041edda6df9c4d2dbac0c666d58aab56a63` / 1025887.
- Active configuration SHA-256: `46607d2404d6794c30c6c61fd52d08c9e787a613a1984d8c21204457d5d2472f`.
- Controlling stop receipt: 12 exits / 50 contracts, not the prompt's 17. Current lookup: 5 executed; 7 not returned by the historical order lookup.
- Balance: $398.2753; portfolio value: $0; root free bytes: 20072894464.
- Restart readiness: NOT_READY. Blockers: dirty VPS tree; working live_v4 bytes differ from the HEAD/preimage; crontab differs from the controlled-stop hash; 17-exit premise conflicts with the controlling 12-exit receipt.
- Audit mutations: 0 across filesystem, Git, cron, processes, orders, positions, balance, and services.

The complete drift list, processes, disk/inode state, paginated orders, paginated positions, balance response, and per-ticker exit reconciliation are frozen in `VPS_AND_EXCHANGE_READONLY_SNAPSHOT.json`.
