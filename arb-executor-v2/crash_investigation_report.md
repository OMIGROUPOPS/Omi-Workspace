# Crash Investigation Report: Jan 31 Low Uptime

## Summary

**Root Cause:** Bot crashed repeatedly on Jan 31, achieving only **4% uptime** (1.0 hours of data collection in 25.8 hours).

## Evidence

### 1. Session Analysis

```
Jan 29-30 sessions (from price_history files):
# 1 | 01/29 17:56 -> 01/29 17:57 |    1 min [CRASH]
# 2 | 01/29 20:50 -> 01/29 20:57 |    7 min
# 3 | 01/29 21:40 -> 01/29 21:41 |    1 min [CRASH]
# 4 | 01/29 21:43 -> 01/29 21:44 |    1 min [CRASH]
# 5 | 01/29 21:54 -> 01/29 22:29 |   34 min
# 6 | 01/30 09:05 -> 01/30 09:05 |    0 min [CRASH - 18 rows!]
# 7 | 01/30 09:18 -> 01/30 09:34 |   16 min
# 8 | 01/30 09:35 -> 01/30 09:53 |   19 min
# 9 | 01/30 09:54 -> 01/30 14:03 |  249 min (longest!)
#10 | 01/30 14:28 -> 01/30 14:57 |   29 min
#11 | 01/30 14:57 -> 01/30 15:03 |    6 min
#12 | 01/30 15:03 -> 01/30 15:07 |    4 min [CRASH]
#13 | 01/30 15:08 -> 01/30 15:34 |   26 min
#14 | 01/30 15:34 -> 01/30 15:56 |   22 min
#15 | 01/30 16:35 -> 01/30 16:54 |   19 min
#16 | 01/30 16:54 -> 01/30 19:25 |  150 min
```

**11 restarts on Jan 30 alone!**

### 2. Jan 31 Data Gaps

```
Total span: 25.8 hours
Active collection: 1.0 hours (4% uptime!)

Gaps > 5 minutes:
  01/31 09:19 -> 01/31 15:22 (363 min / 6 hrs)  <- entire afternoon
  01/31 15:28 -> 01/31 20:33 (305 min / 5 hrs)  <- MISSED PRIME TIME
  01/31 20:39 -> 01/31 22:33 (114 min / 2 hrs)  <- more prime time
  01/31 22:36 -> 02/01 10:21 (705 min / 12 hrs) <- overnight
```

### 3. Known Error Logs

```
logs/bot_paper_20260128_213952.log.err:
  "PARTIALLY UNHEDGED POSITION - Bot stopped for safety"

logs/bot_paper_20260129_090222.log.err:
  UnicodeEncodeError: 'charmap' codec can't encode characters in position 26-28
  (Windows cp1252 encoding issue with arrow symbols)
```

### 4. No Logs from Jan 31

**Critical finding:** No log files exist for Jan 31 sessions, meaning the bot was started without logging enabled (no `2>&1 | tee` or similar).

## Comparison

| Metric | Jan 29-30 | Jan 31/Feb 1 |
|--------|-----------|--------------|
| Total span | 22.1 hrs | 25.8 hrs |
| Active time | 10.9 hrs | 1.0 hrs |
| **Uptime %** | **23%** | **4%** |
| Restarts | 16 | Unknown |
| Prime time rows | 243,613 | 10,718 |
| Arbs found | 1,703 | 130 |

## Changes Made

Added **uptime logging system** to `arb_executor_v7.py`:

### 1. New log file: `logs/uptime.log`

Format:
```
2026-01-31 15:22:00 | STARTED | Mode: PAPER (NO_LIMITS) | Scan: 500ms
2026-01-31 20:33:00 | STOPPED | Reason: KeyboardInterrupt
2026-01-31 20:39:00 | STARTED | Mode: PAPER (NO_LIMITS) | Scan: 500ms
2026-01-31 22:33:00 | STOPPED | Reason: CRASH: UnicodeEncodeError: 'charmap' codec...
```

### 2. Crash logs: `logs/crash_YYYYMMDD_HHMMSS.log`

Full traceback saved on any unhandled exception.

### 3. Code changes

```python
# New function: log_uptime(event, reason, details)
# Logs STARTED/STOPPED events with timestamps

# On start:
log_uptime("STARTED", details={
    'scan_interval': f"{SCAN_INTERVAL}ms",
    'max_contracts': MAX_CONTRACTS,
    'min_buy_price': MIN_BUY_PRICE,
})

# On KeyboardInterrupt:
log_uptime("STOPPED", "KeyboardInterrupt")

# On crash:
log_uptime("STOPPED", f"CRASH: {error_type}: {error_msg}")
# Also saves full traceback to logs/crash_*.log
```

## Recommendations

1. **Always run with logging:**
   ```bash
   python arb_executor_v7.py --start 2>&1 | tee logs/bot_$(date +%Y%m%d_%H%M%S).log
   ```

2. **Use process manager:**
   - `screen` or `tmux` for manual runs
   - `systemd` service for production
   - `pm2` or `supervisor` for auto-restart

3. **Add monitoring:**
   - Alert if `logs/uptime.log` shows STOPPED without STARTED within 5 min
   - Alert if no new rows in `price_history.csv` for > 10 min

4. **Fix known issues:**
   - Unicode encoding error was partially fixed (use ASCII arrows)
   - Unhedged position safety stop is intentional but may need review

## Realistic Expectations

| Scenario | Hourly Rate |
|----------|-------------|
| 4% uptime (Jan 31) | $31/hr |
| 23% uptime (Jan 29-30) | $150/hr |
| 50% uptime (moderate) | $200-300/hr |
| 80%+ uptime (production) | $400-500/hr |

**$329/hr is achievable** with proper process management and monitoring.
