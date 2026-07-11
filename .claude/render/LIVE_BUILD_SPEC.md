# LIVE_BUILD_SPEC — the binding document for C-LIVE-VIEWER v1 (Plex's spec; where the dispatch and this spec disagree, THE SPEC WINS)

> ⚠ **VERBATIM BODY PENDING — the paste channel dropped Plex's spec text** (checked: not in the dispatch body, not in git, `.claude/render/` did not exist). Per the standing discipline (PLEX_T3_T4 precedent): this slot is reserved for the word-for-word spec; the relay owes it. **v1 was built from the dispatch's own binding scope below; when the verbatim lands, any disagreement is reconciled IN THE SPEC'S FAVOR and the delta is named in the vault.**

## The binding scope as relayed (dispatch C-LIVE-VIEWER v1, 07-10)
- **Section 0 (truth rule):** the API tails the exact files the monitor and adjudication already write — no new source of truth, no duplicate state, no write path anywhere. If an API number disagrees with the nightly ledger's own footer, **the API is the bug, by definition**.
- **/command** (ships first): migration bars · ranked fix queue · no-fill taxonomy · class-ledger badges · exchange-truth verdicts at honest nightly cadence.
- **/trade/:id**: Exhibit-1 triptych parameterized by pair identifier + the L1–L9 step strip pulled live from the slate review per trade — **the L7 chip from row data, never hardcoded** (the spec's explicit warning).
- **Shared color key: verbatim from the spec** — PENDING; v1 ships a PROVISIONAL key (below) to be replaced verbatim on landing.
- **Staleness strip: non-negotiable in v1** — every panel stamped from source-file modification time; STALE badge past 90 minutes.
- **Open trades:** if the live log writes tape and decisions incrementally → 5-second poll; else static in v1 + the intraday grader demoted to its own QUEUE build.
- **Serving:** localhost on the VPS, read-only, loopback only; SSH tunnel for the operator; no public exposure, no credentials, nothing on the order path.

## PROVISIONAL color key (replaced verbatim when the spec lands)
AGREE `#10b981` · WOULD-REFUSE `#ef4444` · NO-OPINION `#71717a` · FITTED `#10b981` · DECREED `#f59e0b` · NAKED `#ef4444` · STALE badge `#9ca3af` on dark · panel bg `#111318` · text `#e5e7eb`.

## Part-3 gap, resolved honestly (not promised around)
**Verified: YES — the live log writes incrementally during the day** (`live_v3_<date>.jsonl` is append-per-event via `_log`; `analysis/premarket_ticks/*.csv` append per book tick via `_log_tick`; trades CSVs append per print). Therefore open trades poll at 5 seconds per the spec (page auto-refresh + `/api/trade/:id` re-reads the tails); composer grades compute on request per page load. The continuous intraday grader (composer running as a daemon) remains a separate QUEUE build only if the spec's verbatim demands more than on-request grading.
