# April wrong-time entries v1 — re-derivation ([C-T51-COHORTS], 2026-06-10)

Definition: April BUY order (Kalshi orders history, status=executed, placement
created_time) placed AFTER the match's true start; true start = tape volume onset
(T51-style 10-prints/60s latch) from the historical_pull API tape (complete record),
live tape fallback. Artifact: `april_wrongtime_v1.parquet` (all 1,671 orders, per-row
verdict + T51 catch + miss reason).

## CHECKSUM: NOT re-found — both numbers reported, definition gap stated
- Historical figure: **272**.
- Re-derivation: **943** wrong-time (all buys) / **532** (first-buy-per-ticker only,
  the DCA/re-entry-excluded proxy). Coverage: 1,664/1,671 orders truth-resolved.
- Definition gap: the April-era strategy entered in-play BY DESIGN (Channel-2 era,
  DCA + re-entries), so tape-truth lateness sweeps in deliberate in-play buys; the
  historical 272 almost certainly counted entries that were wrongly timed relative
  to the bot's SCHEDULE BELIEF (placed as if pre-match), a belief not preserved in
  any surviving April state. Not forced.

## T51 replay against the re-derived cohort (the honest catch rate)
Caught = the bot's OWN live trade tape (what its T51 would have seen) latched at or
before the entry placement. Verdicts over the 943 / (532 first-buy):

| outcome | all buys | first-buy only |
|---|---|---|
| **caught** | 146 (15.5%) | 104 (19.5%) |
| MISS: subscription gap (no live tape existed at the bot) | 787 (83.5%) | 419 (78.8%) |
| MISS: live tape latched only after the entry | 10 | 9 |

The dominant miss is STRUCTURAL: for 83% of wrong-time entries no live print record
exists at the bot (not subscribed / recording absent in the April build) — T51 was
blind there, and what it would have seen is unknowable from surviving data. The
Plex >=95% bar therefore CANNOT be certified against April; the modern-data answer
is the bucket-A table (36/41 FULL + 5/41 PARTIAL hypothetical-window protection).
