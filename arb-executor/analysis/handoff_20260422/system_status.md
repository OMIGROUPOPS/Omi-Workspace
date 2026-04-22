# System Status — 2026-04-22 02:04:31 PM ET

## Sidecars

| Sidecar | PID | Heartbeat Age | Status | Extra |
|---|---|---|---|---|
| tennis_odds | 1480785 | 94s (02:02:57 PM ET) | OK | {'events_polled': 206} |
| betexplorer | 1480844 | 625s (01:54:06 PM ET) | OK | {'matches_scraped': 92, 'matched_to_kalshi': 1265} |
| fv_monitor | 1495746 | 59s (02:03:32 PM ET) | OK | {'rows_written': 96, 'events': 56} |
| live_v3 | 1622360 | 17s (02:04:14 PM ET) | OK | {'positions': 65, 'resting_orders': 0, 'ws_connected': True, 'bbo_age_sec': -12} |
| kalshi_price | 1587860 | 211s (02:01:00 PM ET) | OK | {'rows_written': 130, 'tickers': 130} |

## Last 10 Log Events

```
2026-04-22 02:04:10 PM [skipped]  {"reason": "no_valid_sides", "event": "KXATPCHALLENGERMATCH-26APR22KUKRIE"}
2026-04-22 02:04:10 PM [skipped]  {"reason": "no_valid_sides", "event": "KXWTAMATCH-26APR23BOUKAL"}
2026-04-22 02:04:12 PM [ws_error]  {"error": "no close frame received or sent"}
2026-04-22 02:04:12 PM [ws_reconnecting]  {"attempt": 1, "delay_sec": 5}
2026-04-22 02:04:17 PM [price_signal] KXATPMATCH-26APR22BONDRO-BON {"source": "last_traded", "price": 65, "mid": 60.0, "last_traded_age_sec": 5, "divergence_cents": 5.
2026-04-22 02:04:19 PM [skipped]  {"reason": "schedule_gap", "event": "KXATPCHALLENGERMATCH-26APR20CHAHUR", "unmatched_cycles": 4, "op
2026-04-22 02:04:25 PM [ws_connected]  {}
2026-04-22 02:04:25 PM [ws_subscribed]  {"new": 240, "total": 240}
2026-04-22 02:04:25 PM [ws_reconnected]  {"attempt": 1}
2026-04-22 02:04:26 PM [reconcile]  {"positions": 9, "resting_orders": 11, "linked": 9, "reconcile_exits_posted": 0, "unmanaged": 0, "or
```

## Config (deploy_v4.json)

- Active cells: 34
- Disabled cells: 4
- Total referenced: 38
- Entry contracts: 10
- DCA contracts: 5

## Errors/Warnings (last 2h)

```
2026-04-22 01:42:53 PM [ws_error] {"error": "no close frame received or sent"}
2026-04-22 01:44:48 PM [ws_error] {"error": "no close frame received or sent"}
2026-04-22 01:47:34 PM [ws_error] {"error": "no close frame received or sent"}
2026-04-22 01:49:51 PM [ws_error] {"error": "no close frame received or sent"}
2026-04-22 01:52:16 PM [ws_error] {"error": "no close frame received or sent"}
2026-04-22 01:54:37 PM [ws_error] {"error": "no close frame received or sent"}
2026-04-22 01:56:57 PM [ws_error] {"error": "no close frame received or sent"}
2026-04-22 01:59:29 PM [ws_error] {"error": "no close frame received or sent"}
2026-04-22 02:01:56 PM [ws_error] {"error": "no close frame received or sent"}
2026-04-22 02:04:12 PM [ws_error] {"error": "no close frame received or sent"}
```

## Watchdog

- 2026-04-22T13:50:01.623965-04:00 ubuntu-s-1vcpu-2gb-nyc3-01 CRON[1731966]: (root) CMD (/root/Omi-Workspace/arb-executor/
- 2026-04-22T13:55:01.219596-04:00 ubuntu-s-1vcpu-2gb-nyc3-01 CRON[1732561]: (root) CMD (/root/Omi-Workspace/arb-executor/
- 2026-04-22T14:00:01.537306-04:00 ubuntu-s-1vcpu-2gb-nyc3-01 CRON[1733160]: (root) CMD (/root/Omi-Workspace/arb-executor/
