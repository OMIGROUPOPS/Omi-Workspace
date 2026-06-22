# Crawford / Rodionov premarket+corridor tick read (Jun 22 2026 ET)

Event KXATPMATCH-26JUN22CRAROD. Legs: **Jurij Rodionov** (favorite, our staircase deep-cast),
**Oliver Crawford** (underdog, engagement->fallback). Boundaries ET: window-1 open 06:30 | corridor
open (scheduled) 10:30 | real start 11:16:15. Tables in this dir; normalization yes->buy/no->sell.

- **Closest our-bid vs last-traded (Rodionov, pre-real-start):** gap **1c** at 10:21:41.47 (our bid 67c, last-traded 68c). Our bid never sat at or above a traded print before the gun.
- **Deepest taker-NO SELL level on Rodionov (window-1+corridor):** 67c @ 10:08:25, cumulative sell size at/below that level = **1** contract(s).
- **Dips with real sell size within 1-2c of our walk-at-that-minute (Rodionov):** 9 trade(s). 68c x16 @ 10:06:40 (our bid 66c); 68c x84 @ 10:06:40 (our bid 66c); 68c x1 @ 10:06:43 (our bid 66c); 68c x10 @ 10:06:43 (our bid 66c)
- **Min pair-basis achievable by crossing Rodionov (lift ask) + Crawford@31:** 99c at 10:10:00 ET. basis<100 buckets: **30** of 573.
- **Crawford fill:** @31c at 11:14:18 ET (corridor, pre-real-start); exit resting sell @38c (band 7).

Tables: band (per-tick book+last-traded+our bid), fillability (per leg/price: sell-vol<=level,
buy-vol>=level, our bid when it traded, would_maker_fill), crosstrace (30s pair-basis if crossing).
No conclusions beyond the tables.
