# GUEGOM tape pack - raw series only (no analysis)

Format @ c09bde99 plus `tminus_bell_s` on every book and trade row - T-minus to the LIVE-BY BELL
EDGE (actual bell never observed: t_minus_actual_bell null on all V52H trace rows @ 576c705f,
no observed_starts.db row; edge = scheduled = pre_match_boundary = w1_right) - and
per-leg W1 closes. Ticker `KXATPMATCH-26JUL12GUEGOM` per the dev-804 ledger @ 4716657a
(GUEGOM is not in the b43d7cde cohort receipt - different cohort; stated, not silently patched).

| leg | book rows (chg) | trades | true | W1 close (last true trade) | last mid | gaps>600s |
|---|--:|--:|--:|---|---|--:|
| GUE | 17209 | 2140 | 2140 | 1¢ @ tminus 4027s | 1.0¢ | 30 |
| GOM | 12756 | 2389 | 2389 | 99¢ @ tminus 3533s | 98.5¢ | 19 |

Edges: w1_left 1783800341 · w1_right 1783879200 · actual_bell 1783879200 · scheduled 1783879200 · pre_match_boundary 1783879200.
Heartbeat caveat as @ c09bde99: gaps flagged, not smoothed. No analysis, no annotations.
