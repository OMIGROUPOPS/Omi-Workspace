# OUTCOME PROOF (C46, two-lane) — C-NIGHTLY-ADJUDICATION (live trade identifiers + the conviction replay as a nightly instrument)

**Candidate SHA: `3cd1da38`** (live_v4.py trade-id stamper + 4th boot rebuild; conviction_replay.py --date/--nightly + ADJUDICATION writer; cron /root/adjudication_nightly.sh @ 12:20 AM ET).

## Prior art (C45)
- **MIGRATION DOCTRINE (RULING_PAIR_ECONOMICS)** — the organ: human memory as process → gates and nightly instruments; the nightly footer is the migration meter. No new class (loop infrastructure).
- **C-CONVICTION-REPLAY** — the one-shot this makes permanent: same composer, same 3a gate (runs nightly; a failure writes GATE FAILED and refuses the replay), same grading and footer.
- **The fingerprint pattern (#1 orders → #2 gun → #3 cycles → this, #4 trade ids)** — the sequence is rebuilt at boot from the jsonl, never memory; retroactive-continuity seed: on a day with replay ids but no live stamps, the sequence starts at the day's fill count — exactly how the replay numbered — so live ids CONTINUE the replay's series.
- **C-CYCLE-CAP emitter stamps** — same single-emitter discipline: the id is minted at placement (order_placed buy, new cycle) and inherited by entry/exit/scalp/settled rows.

## LANE 1 — MECHANISM
- **Row-for-row equivalence (Part 3, replay-harness law):** tonight's build re-run on the July 10 recorded slate — **123/123 original rows identical** on (id, ticker, price, grade, posterior); the re-run appends rows 124–125 for the two fills that landed after the 4:30 PM one-shot. The cron and the one-shot are the same instrument.
- **Identifier continuity:** boot loader seeds seq = day's fill count when no jsonl stamps exist (July 10: the replay's numbering base), then live minting continues; ids include the date so the midnight basis reset rolls the sequence naturally.
- **Nightly output:** ADJUDICATION_YYYYMMDD.md + RESULTS json committed beside the ledger; NIGHTLY_PASS gains the MIGRATION METER line; the 3a gate self-checks the composer every night before any grading.

## LANE 2 — SETTLEMENT P&L
$0 claimed. Identifiers and grading; §0A untouched; pair-97 graded as legacy, never an anchor (constraint #11).

## Regression watches
`trade_ids_rebuilt {day, seq, open_ids}` at every boot (the 4th rebuild line) · every fill row carries `trade_id` from tonight · ADJUDICATION_<date>.md lands nightly at 12:20 AM (absence = the cron failed, visible by morning) · gate-3a nightly result inside the file.
