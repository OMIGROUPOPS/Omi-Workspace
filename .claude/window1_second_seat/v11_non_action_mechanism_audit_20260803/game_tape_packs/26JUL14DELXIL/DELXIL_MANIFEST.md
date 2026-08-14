# DELXIL tape pack - raw series only (no analysis)

Exact GUEGOM format (@ c09bde99 pack format, @ 03e38798 GUEGOM variant): `tminus_bell_s` on every
book and trade row is T-minus to the LIVE-BY BELL EDGE - the actual bell was never observed
(t_minus_actual_bell null on all 3,232 V52H trace rows @ 576c705f; no observed_starts.db row for
this game). The scheduled bell (1784039400) is 2.8 h EARLIER than the live-by edge (1784049342.9):
a delayed start; the edge governs. Ticker `KXATPCHALLENGERMATCH-26JUL14DELXIL` per the dev-804
ledger @ 4716657a - the KXATPMATCH prefix in the request corrected to KXATPCHALLENGERMATCH.

| leg | book rows (chg) | trades | true | W1 close (last true trade) | last mid | gaps>600s |
|---|--:|--:|--:|---|---|--:|
| DEL | 1323 | 32 | 32 | 84¢ @ tminus 445s | 83.5¢ | 16 |
| XIL | 2356 | 29 | 29 | 17¢ @ tminus 48s | 15.5¢ | 17 |

Edges: w1_left 1783986059 · w1_right 1784049342.914 · live-by bell edge 1784049342.9 (= pre_match_boundary; scheduled 1784039400, actual bell unobserved).
Heartbeat caveat as @ c09bde99: gaps flagged, not smoothed. No analysis, no annotations.
