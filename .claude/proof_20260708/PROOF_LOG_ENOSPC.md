# PROOF — C-LOG-ENOSPC (candidate `9a74b061`): the logger must drop the line, never the bot

**This document is the OUTCOME_PROOF for code candidate `9a74b061`** (C-LOG-ENOSPC: `_log` / `_log_tick` / `_log_trade` write+flush wrapped `try/except OSError`, dropped-line counter `_log_write_errors`). Zero config delta; band levels, aims, walk caps, gates untouched.

## Prior art (gate — C45)
- Greps: `ENOSPC|No space left|disk_full|log_file.flush|OSError` over LESSONS.md, LIVING_VAULT.md, JUNE_VAULT APPENDIX, `.claude/rulings/`, BOARD.md.
- Established: **disk-full incident 06-25 + 07-01 recurrence** (archive prune 2ec6b3d; tennis.db/historical_pull cache — *operational* remediation only, the crash class in code was never named); **C-ERROR-TRIPWIRE** (live_v4.py:1856 — rate-watches crash-class *events*, but sat downstream of the very flush that died: the tripwire itself was killed by the defect it watches); **C47-CONTINUOUS** (07-07: 15-min steady_cadence audit — an in-process auditor, same blast radius as the process); the disk-gated respawn cron (`<90%` guard — correct gate, no remediation arm). **DELTA: first time the crash class itself (unprotected logger I/O in the trading loop) is named and closed in code.**
- This is a DEFECT fix under the week standing order (config HOLDS; defects exempt via gate).

## What happened (the conviction, exchange truth + jsonl)
- **02:52:04–02:52:22 ET 07-08**: disk hit 100% (16G tennis.db + 11G durable + 9.0G uncompressed tick CSVs + 243MB console log). WS handlers logged `WS_ERROR {"[Errno 28] No space left on device"}` and *survived* (reconnect loop swallows). Then `routing_tick → _route_event → _log("skipped") → self.log_file.flush()` raised `OSError: [Errno 28]` **uncaught** → `run()`'s catch-all called `self._log("error", ...)` which **raised again from the same flush** → process exit. Console traceback preserved: `logs/live_v4_crash_20260708.log.gz` (tail).
- The respawn cron (`*/2`, gated `disk<90%`) correctly refused to boot onto a full disk — and nothing frees disk or escalates, so DOWN was an absorbing state: **02:52→15:30 ET, 12.6h**.
- The last audit of any kind: `POST_BOOT_AUDIT steady_cadence PASS 02:50:37` (55 positions, 316 resting orders). **After 02:52 there were zero audits** — the 15-min auditor lives inside the process (C47-CONTINUOUS blast-radius note), the external `position_audit.py` cron has *never* run (dash `.` PATH-only sourcing: `. .env` → `.: .env: not found`, rc=2 since the line was written; fixed to `. ./.env` this pass), and nightwatch/watchdog scream BOT_DOWN only into local files (~758 minutely alerts, no channel out).
- The dead bot's **316 resting orders kept filling**: 8 legs filled naked 04:37–11:18 ET (all fills post-crash; every pre-crash fill had its exit resting — the 07-07 sweep-era machinery held).

## Two-lane statement (C46)
- **LANE 1 — MECHANISM: unchanged by construction on every decision path.** The guard binds only when a log write raises `OSError` — a state in which the prior code **terminated the process**. No aim, band, walk, completion, or booking computation reads the logger's success. Trade construction on any tape where writes succeed is byte-identical; lint + smoke replay (gate [1/3],[2/3]) prove parse+run identity on the recorded slate.
- **LANE 2 — SETTLEMENT P&L: n=0 settlements attributable to the change** (LUCK-N/A) — the fix creates no trades; it removes a process-death. Secondary lane reported as the counterfactual below.

## Per-leg outcome replay — last night's slate WITH the fix (conservative: fills unchanged; only exit-posting resumes)
Replay convention: with `9a74b061`, the 02:52 flush error increments a counter and the loop continues (run():9690 sleeps 5s and resumes — the exact path proven by today's live boot posting all 8 exits in 36s). Each naked fill would have been booked at fill time (check_fills was alive) and its band exit posted within the same tick — the identical prices the real reconcile posted at 11:30, just 2.0–6.9h earlier. No credit claimed for better exits; the delta is exposure-hours, plus the two ITM legs realize the SAME taker prints they realized today.

| leg | filled (ET) | naked hours (actual) | exit posted (actual 11:30/adopted) | with fix | outcome delta claimed |
|---|---|---|---|---|---|
| MILMIS-MIS | 04:37:45 | 6.9 | 98¢ resting (basis 92) | same, at fill | 0.0¢ (exposure only) |
| VANSEL-VAN | 04:44:01 | 6.8 | 45¢ resting (basis 38) | same, at fill | 0.0¢ (exposure only) |
| MILMIS-MIL | 05:32:27 | 6.0 | 9¢ → crossed, taker-sold 5 @ 13¢ (basis 6) | same sell hours earlier | ≥0 (same print claimed) |
| JONJEA-JON | 06:16:06 | 5.2 | 61¢ resting (basis 50) | same, at fill | 0.0¢ |
| LUENAT-LUE | 06:45–06:51 | 4.7 | 65¢ → crossed, taker-sold 5 @ 85¢ (basis 53) | same sell hours earlier | ≥0 (same print claimed) |
| LUENAT-NAT | 06:59:47 | 4.5 | 49¢ resting (basis 41) | same, at fill | 0.0¢ |
| JONJEA-JEA | 09:30:40 | 2.0 | 56¢ resting (basis 47) | same, at fill | 0.0¢ |
| TOMSHI-TOM | 11:18:57 | 0.2 | 82¢ resting (basis 63) | same, at fill | 0.0¢ |

Second wave (fills 15:27–15:44 UTC while containment ran, live bot adopted ≤8 min): DAMARN-ARN/DAM, PDARIB-RIB, MAXABA-MAX, ISHCRO-CRO — all covered by steady-state reconcile; with the fix these never orphan at all (check_fills books them at fill).

**BOTTOM LINE:** Lane 1 unchanged by construction; Lane 2 claims $0.00 (conservative — no print is claimed that the tape didn't produce). What the fix buys is the removal of a proven absorbing-death: 12.6h × 316 unattended resting orders → 0. Sweep verification after containment: **32/32 positions covered, 0 naked (15:44:59 UTC)**.

## Companion operational closures (same pass, not code)
1. Disk freed 100% → 82% (2,205 idle tick CSVs gzipped in place — lossless, readers handle .csv.gz; crashed console log archived to `logs/live_v4_crash_20260708.log.gz`).
2. `position_audit` cron line `. .env` → `. ./.env` (dash `.` does not search CWD) — the 30-min *external* naked-leg audit runs for the first time since Feb.
3. Daily disk hygiene cron: gzip idle tick CSVs (>4h old) + truncate `/tmp/live_v4.log` at 500MB (the jsonl in `logs/` is the durable record) + gzip jsonls older than 2 days.
