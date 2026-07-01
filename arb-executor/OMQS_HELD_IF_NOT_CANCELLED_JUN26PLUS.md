# OMQS — the 89% trade-through subset: WIN/LOSS if we'd HELD (Jun 26–30 settled)

Scope: the 1,373 entry bids cancelled BEFORE the real start where a trade later printed at/through the bid (the 89% subset from OMQS_CANCEL_TIMING). Counterfactual: had we HELD and filled at our resting bid, outcome under the CURRENT fill+band exit (winner exits at +band, capped; loser rides to −bid). Settled Jun 26+ only. Kalshi REST + tick-tape. Read-only.

## Three numbers

**(1) n filled-if-held:** 1,216 (of the 1,373 subset; 157 dropped — no settled leg result / unresolved).

**(2) win/loss:** **527 / 689 = 43% win.**

**(3) net P&L (fill+band, band-capped wins / −bid losses):** **−$653.47** (per-bet −53.7¢).
- Reference (ride-to-settle upper bound, if winners rode to full 100−P instead of the +band cap): +$17.38.

## Read
Had we held these bids instead of cancelling them, we would have **LOST ~$653** under the current exit — only 43% won, and the asymmetric fill+band exit caps the 527 winners at a small +band while the 689 losers ride to −bid in full. **The pre-start cancel is protective, not costly, as long as the exit stays band-asymmetric** (the ride-to-settle bound of +$17 shows the loss is entirely the exit geometry, not the fills). Do not "fix" the premature cancel to capture these fills until the exit asymmetry is fixed.
