# Window-1 official-start recovery

This ledger was extracted without reading policy decisions, placements,
fills, or candidate outcomes.  Schedule is retained only as a last-resort
bound and never proves a positive Window-1 fill.

## Start gate — FAIL

- exact starts = 234
- clean causal intervals = 31
- live-by-only = 450
- contradictory = 26
- schedule-only = 63
- unresolved = 0
- positive-Window-1-provable population = 265
- timing-blocked population = 539
- required = 603
- missing from gate = 338

Historical public-provider rows carrying an in-play or ended status now use
their provider `start_utc` as the historical match-start fact.  The deployed
six-hour freshness corridor is not applied to historical reconstruction.
Live-by observations and scheduled times remain one-sided bounds.

The gate can pass only with 338 additional
event-resolved exact starts or noncontradictory causal intervals.  The
currently blocked population is 450 live-by-only,
26 contradictory, 63
schedule-only, and 0 unresolved events.
