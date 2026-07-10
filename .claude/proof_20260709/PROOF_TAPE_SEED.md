# OUTCOME PROOF (C46, two-lane) — C-TAPE-SEED (boot-seed last-trade memory from REST; restart-amnesia class, FIFTH instance)

**Candidate SHA: `2f26cc00`** (live_v4.py `_seed_tape_memory` + apply_trade basis flip + cohort stamps, daily_ledger tape-basis section).

## Prior art (C45)
- **The restart-amnesia family** — C-ORPHAN-FINGERPRINT (orders) → C-GUN-PERSIST (gun state) → C-CYCLE-CAP (cash cycles) → C-EARLY-UNLOCK's named ws-since-boot undercount (volume) → this: the TAPE memory. Every instance is the same lesson: state the exchange already knows must not die with the process.
- **C-EARLY-UNLOCK close-out (tonight)** — the exhibit: PAPJER unlocked at 2,895 realized shares but both legs skipped `skip_no_trade, last_trade_age_sec: -1.0` — the book HAD prints (PAP 55¢ at 10:04:18 PM ET, REST-verified); only the bot's since-boot memory was empty.
- **The last-trade discipline (§ three observable prices; anchor resolver docstring)** — UNCHANGED: no BBO-mid fallback introduced; `V4_LAST_TRADE_MAX_AGE_SEC = 1800` gates exactly as before, now against HONEST age. A print older than 30 min still skips — that is then an operator threshold ruling, not a code fix.
- **apply_trade cents/dollars heuristic** — the seed parser reuses it verbatim (consistency; REST field shape verified live: `yes_price_dollars` string, `created_time` ISO-Z, `taker_side`).

## LANE 1 — MECHANISM
- **Seed:** at every discovery pass, tickers with NO last-trade memory fetch their most recent REST trade (`/markets/trades?limit=1`) and seed `book.last_trade_price/ts` with the print's ACTUAL timestamp — `last_trade_age_sec` reads honest age (a 2,400s print reads 2,400s, never −1.0). No-trade tickers (JER class) seed nothing and retry at most half-hourly — they keep skipping honestly.
- **Precedence:** a live ws print overwrites its seed immediately (`rest_seeded` → `ws_live`); the seed never wins a race (guarded both sides). One-time `tape_seed_live_confirm` line grades seed-vs-first-live-print agreement (the watch).
- **Scope:** anchor resolution only — the seed writes the same two Book fields apply_trade writes; `_trade_times`/volume-accel/gun detectors are NOT fed (a seeded old print is not a live print).
- **Cohorts:** buys stamp `tape_basis` (rest_seeded vs ws_live) at the single _log emitter, fills inherit; daily_ledger renders the split so seeded-anchor entries are graded separately before anyone trusts them.
- **Live verification (in the close-out):** PAPJER/BAYERE/PAWHRU legs post-deploy — seeded age, whether the 1800s threshold admits the anchor, and the placement line where it fires.

## LANE 2 — SETTLEMENT P&L
$0 claimed. The seed changes when an anchor becomes available, never its price discipline; the cohort stamp exists so any effect is measured before it is claimed.

## Regression watches
`tape_seeded {checked, seeded, no_trades}` per discovery pass · `tape_seed_live_confirm` delta distribution (seed-vs-live price agreement) · tape-basis cohort fill rates (daily_ledger) · skip_no_trade lines now carry honest ages (never −1.0 for a ticker that has ever printed) · `conception_beyond_horizon` stays 0.
