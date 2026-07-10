# OUTCOME PROOF (C46, two-lane) — C-DRAIN-REPLAY (restart-amnesia #6: the drain itself; the PAPJER-PAP class)

**Candidate SHA: `SHA_DR`** (live_v4.py drain manifest + `_drain_replay` at boot and at halt-clear; monitor `drain_replay_violations` + LIVE_STATUS zero-tolerance section).

## Prior art (C45)
- **THE INCIDENT (this dispatch)** — order `45f12259` (PAP 53¢×5, placed 11:00:49 pm under two operator rulings): drain-cancelled 11:14:54 pm (`order_cancelled, label: shutdown_cancel`), never re-placed, nothing noticed. The deploy's own close-out had verified the bid its restart then destroyed — the verification was incomplete. The monitor said zero violations — a second defect.
- **The restart-amnesia family (#1–#5)** — orders → gun state → cycle history → unlock volume → tape memory. #6 is the drain itself: state the bot DELIBERATELY destroys at shutdown must be replayed or its loss named.
- **`_shutdown_drain` (#0-infra)** — cancel-only by design ("writes no in-place state") — kept; the manifest write is additive, before any cancel.
- **C47 conception halt + tonight's TUPMAK halt (11:33–11:43 pm)** — the halt-clear retry hook exists because tonight's halt would have eaten a boot-time replay (refusal `conception_halt` stays in the manifest and retries at `conception_halt_cleared`).
- **The chokepoint (place_order)** — the replay runs THROUGH it: every guard (halt, band, horizon, gun, cycle-cap, in-flight lock, buy-position guard) re-evaluates; refusals carry the chokepoint's own named `_error`.

## LANE 1 — MECHANISM (the PAP restore is the manual execution of exactly what the code now automates)
The restore, 11:48:43 pm ET, each gate's verdict as the dispatch ordered:
- anchor: last print 708s old → ADMIT (fresh; the 7,200s allowance not even needed)
- book/cell: 53 bid / 55 ask, cell zone intact
- combined-goal: 97 − JER@44 = bound 53 → joined the bid AT 53 (never-marketable ok)
- dedup/position: 0 resting, 0 position → ADMIT
- **PLACED: buy 5 shares @53¢, order `91c5024d`, resting (HTTP 201)** — pair whole (53+44=97=goal) 3h11m before the 3:00 am start.
The code path automates this: manifest written pre-cancel → boot replay through place_order → outcomes exhaustive (replaced / refused-NAMED / already_covered / stale-discard-LOUD / halt-retry). The monitor section turns any silent residue into a rendered VIOLATION within 10 min of boot.
Account (Part 2, cited): post-boot fresh evaluation re-placed JER (11:15:54) and PAWHRU (11:15:59) because their events came up for fresh placement on the new boot's cycle; PAP got no v4_place, no skip, no line at all — the router's fresh-place path never returned to it (its event already had one resting leg from 11:15:54 onward), and no machinery owned the drained order. That orphaned-by-design gap is what the manifest closes; the deep router why (one-leg-resting pair state suppressing the sibling's fresh place) is BOARDED with the cancel-race defect rather than patched blind at midnight.

## LANE 2 — SETTLEMENT P&L
$0 claimed. The restore re-establishes a ruling-mandated posture; its P&L grades in the early-unlock/tape-basis cohorts like any entry.

## Regression watches
`drain_replay` outcome lines at EVERY deploy (n must equal the drain's cancel count) · monitor DRAIN-REPLAY section stays 0 violations · `drain_manifest_error` / `drain_replay_error` absent · `drain_replay_stale_discard` only after crashes >2h.
