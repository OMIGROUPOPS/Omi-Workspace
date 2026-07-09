# DAALU RE-ENTRY FORENSIC — the premarket re-conception class (2026-07-09 ~3:30 pm ET; read-only; the re-entry ruling is the operator's open decision)

## 1 — THE TRACE (KXITFWMATCH-26JUL09DAALUX, both legs; all stamps anchored-clock W1, no gun fired — `gun_thin_shadow` only, genuinely premarket throughout)

| time | event |
|---|---|
| 8:01 am | LUX conception REFUSED at the horizon (working as designed) |
| 11:18 am | DAA bid placed @30 (in-window conception) |
| 1:31:55 pm | **CYCLE-1 DAA fills @31** → exit posted @37 |
| 1:35:26 pm | **CYCLE-1 LUX fills @66** (sibling completion) → exit posted @83 |
| 1:35:33 / 1:49:51 pm | **both legs CASH** (+$0.30 / +$0.85) — `_session_exited` stamped on both |
| **2:54:41 pm** | **the OS-build deploy restarts the bot** → `window_open_set` re-fires for BOTH legs |
| **2:54:52–2:55 pm** | **CYCLE-2 conceived fresh: DAA @63, LUX @34→35 — ELEVEN SECONDS after boot** |
| later | cycle-2 cashes too (DAA 63→78 +$0.75, LUX 34→41 +$0.35) |

**Was no_rebuy_after_cash consulted? NO — and it couldn't have been.** Its actual scope, precisely (code cites):
- `_session_exited` gates **ONLY the sibling-repost sweep** (live_v4.py:4321) and the **audit assertion** (:9427). **The ROUTER's fresh-conception path never consults it** — a cashed leg's deleted position reads as fresh canvas.
- The set is **IN-MEMORY** (:6538, stamped at exit booking) — **a restart wipes it**. Cycle-2 was conceived by the boot router 11 seconds into the new process, which had no memory the pair ever existed. The fingerprint lesson's THIRD instance (orders → gun state → cashed history).
- The audit's `post_exit_rebuy` check inherits both gaps: it fired zero times on any of this week's 23 multi-cycle legs.

## 2 — THE WEEK SWEEP (every leg with >1 completed buy→cash cycle; premarket = cycle-2 entry before any gun fire)

**23 legs · 46 completed cycles · 22/23 with premarket cycle-2 · TOTAL +$15.84 (jsonl convention, fee-blind flagged per the reconciliation) · 22/23 legs NET POSITIVE** (sole loser HERAMB −$0.15). Full roster in the session sweep; exhibits:

| leg | cycles (entry→cash, pnl) | mechanism |
|---|---|---|
| DAALUX-LUX | 66→83 +0.85 · 34→41 +0.35 | restart-wipe (2:54 pm boot) |
| DAALUX-DAA | 31→37 +0.30 · 63→78 +0.75 | restart-wipe |
| LIXSUN-LIX | 34→41 +0.35 · 58→71 +0.65 (4h apart) | **router re-conception, same session — no restart needed** |
| MATKOM-KOM | 7→11 +0.20 · 7→11 +0.20 (7h apart) | router re-conception |
| DAMARN-DAM | 37→45 +0.40 · 35→43 +0.40 | router re-conception (the BOUHAR day's engine, twice) |
| CHOYAM-YAM | 67→84 +0.85 ×2 | the one non-premarket cycle-2 |

**Reported honestly, as ordered: this defect class is PROFITABLE — ~$16/week gross across 46 cycles at a 96% leg win rate.** Doctrine violation ≠ loss: the class is literally the exit engine running the same swing twice. Both mechanisms produce it: (a) restart-wipe of the in-memory guard, (b) the guard's design scope never covered the router at all — multi-hour same-session re-conceptions (LIXSUN/MATKOM/DAMARN) are the ROUTER working as built.

## 3 — THE GUARD'S SCOPE GAP + FIX SHAPE (nothing ships; the ruling is the operator's)
- **Gap, named:** C-NO-REBUY-AFTER-CASH = repost-sweep-only + session-memory-only. Two open doors: the router conception gate (never wired) and restart amnesia (never persisted).
- **Fix shape IF re-entry is ruled forbidden:** per-leg cash-cycle history persisted per premarket — rebuilt at boot from the jsonl `exit_filled`/`scalp_filled` lineage (the fingerprint pattern applied to cashed history), consulted at BOTH the repost sweep and the router conception gate, with the audit assertion inheriting the persistent set.
- **Fix shape IF re-entry is ruled allowed:** the same persistence, consumed as a CYCLE COUNTER (cap per leg per premarket, cycle-stamped in the ledger so grades never blend cycles) — the class trades on, bounded and visible.
- **The evidence package's own read (data, not a ruling): the class earns, the mechanism is unintentional, and the honest framing is that the bot discovered premarket re-scalping by accident.** The operator rules on whether accident becomes doctrine.
