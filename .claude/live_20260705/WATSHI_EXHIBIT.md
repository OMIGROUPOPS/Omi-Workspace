# WATSHI — the live exhibit (resting-bid tape grading, 2026-07-04 ~20:13 ET)

**Setup:** WAT filled 65c at 19:09:14 ET (5 sh, maker). Sibling SHI bid rested at **35c**
(posted 18:27:58, drain-cancelled 19:57:52 during the gated deploy, **not re-placed since**).

**SHI tape since WAT's fill: 204 trades / 25,100 shares.** The fillable-zone ladder:
36c×848 · 37c×2,124 · 38c×5,963 · 39c×5,279 · 40c×3,885 · 41c×349 (the 58c+ prints are the
other side of the book's action, not our zone). First print 19:09:27 — **13 seconds after
WAT filled** — last 19:26:42.

**Class: FLOW_ABOVE, GAP +1c.** Lowest print 36c vs our 35c bid. Twenty-five thousand
shares traded a single cent above a bid that sat there for 90 minutes. This is the
near-miss class in its purest form — NOT starvation (25k shares is not a dead tape), and
not a queue problem (nothing printed at/below 35).

**The exact reprice that would have filled: 36c** (848 shares printed there; joining it
during the 19:09–19:26 flow fills). **Combined it makes: 65 + 36 = 101 — BREAKS the 97
doctrine (+4 over goal).** And the honest kicker: the doctrine bound is
min(aim 33, goal−basis 32) = **32c** — our original 35c bid was itself already 3c ABOVE
the bound the moment WAT filled at 65 (a fill at 35 = combined 100). The correct action at
19:09:14 was never a reprice UP toward the flow; it was the re-aim DOWN to 32 that
C-REAIM-ON-ARRIVAL (3691ff5, deployed 19:58) now performs on every sibling basis arrival.

**Achievable-combined-RIGHT-NOW: 65 + ask 36 = 101 (+4 vs goal).** This pair cannot be
completed inside doctrine at current prices; the WAT leg rides its 84c exit. Board note:
no SHI bid rests at all post-restart — the pair has no passive completion path until the
bot re-engages the leg.

**Verdict the monitor now renders automatically:** FLOW_ABOVE / gap +1c / repriceable=false
(bound 32 < flow 36) / doctrine_note "flow above but bound 32c < flow — chasing breaks goal."
The class that LOOKS like money left on the table decomposes, under the goal bound, into:
the mistake was the 35c bid still standing after the 65c basis arrived — not the absence
of a chase.
