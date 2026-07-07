# VAULT PENDING — C-RETENTION (observed true starts), 2026-07-06

**Prior art (C45):** START_TIME_JOIN.md 2e86cf3 (zero observed starts on disk; the collector
discards in-play transitions — 19,264 rows kept, zero starts) · AIM_V2_OPERATIONAL_REPORT §5
(PARKED pending own dispatch — this is that dispatch) · session-latch partial source (gun
silent 75%, not a substitute) · tennis.db disk-full grave (two crashes, auto_vacuum=NONE) ·
no retention change anywhere in history (grepped).

**The change (d7320817, collector-side only, zero live_v4 changes):** te_live.py banks the
FIRST observed in-play row per match into `observed_starts` (te_match_id PK, set-once
INSERT OR IGNORE, timestamped) alongside the existing overwrite flow. Additive: no existing
statement or consumer read path altered. **Growth bound: ≤ global slate (~600–1,000
matches/day) × ~120 B/row ≈ ≤120 KB/day ≈ ≤44 MB/yr** against the 16.8 GB db; append-only,
no delete churn, so auto_vacuum=NONE posture is unchanged by this table (the db's growth
problem lives elsewhere — book_prices 39.7M rows — unchanged here, named).

**No-trading-delta proof:** live_v4.py's only tennis.db touches are
`_commence_time_from_book_prices` (book_prices), `_kalshi_commence_time`
(kalshi_price_snapshots), `_get_side_fv` (book_prices) — grep-proofed; none reads
live_scores or observed_starts. A new table cannot alter those reads. C46 satisfied as
no-trading-delta.

**Accumulator wiring (same commit):** observed starts preferred as the bell where present
(honest-era rows get MORE honest); LATCH-CAL bar (K=600/M=20,000, the ruled canonical)
for everything unobserved; every new sample carries `bell_src` — the bar150→latchcal
axis change in accumulator samples is tagged and confined to coverage/harness (derivation
re-detects independently).

**VC note:** te_live.py entered version control for the first time with this fix — it had
run uncommitted since April (discipline gap, closed).

**Live verification:** appended below after the first hour of banked starts tonight.
