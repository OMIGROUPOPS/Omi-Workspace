# OMQS — CANCEL-TIMING vs REAL START, settled events Jun 26–30 (post both P0 order-path fixes)

Scope: 385 settled events Jun 26+ (settled_time ≥ Jun 26 ET), 748 legs. Authoritative: Kalshi REST (settlements/fills) + /markets/trades tick-tape. Real start = tape-onset (first 60s window with ≥5 trades followed by another ≥5, across the event's legs). Entry-bid cancels = order_cancelled joined by order_id to an order_placed with action=buy. "At/through the bid" = a trade printed at yes_price ≤ the cancelled bid. Read-only; bisect bot untouched.

## The four numbers

**(1) Entry-bid cancels — before vs after the real start:** of 1,443 entry cancels (with a detectable onset), **1,373 = 95% were cancelled BEFORE the real match start; 70 = 5% after.**

**(2) Pre-start cancels that flow then hit:** of the 1,373 cancelled-before-start bids, **1,223 = 89% had a trade print AT or THROUGH that bid's price AFTER we cancelled it** (i.e. the market came to our killed bid — it would have filled; upper bound, ignores queue position).

**(3) Scheduled start vs actual tape-onset:** **median gap = +40 min** (real start lands ~40 min after the scheduled time). **151 of 371 events = 41% started 1 hour or more late.**

**(4) match_live_detected firing:** fired on **59 of 385 settled events**; **never fired on 322 of 381 events that had a real start = 85% never.**

## One-line read
Entry cancels are keyed on the stale scheduled clock (median 40 min early, 41% of events 1h+ late), so 95% fire before the real start and 89% of those kill a bid the market then trades into — while the real-start detector (`match_live_detected`) is silent on 85% of events. The cancel timing runs blind to the actual match start.
