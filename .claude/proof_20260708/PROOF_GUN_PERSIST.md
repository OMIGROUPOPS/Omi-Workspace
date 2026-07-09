# OUTCOME PROOF (C46, two-lane) — C-GUN-PERSIST (board #20, tonight's only PARTIAL)

**Candidate SHA: `1a8a266e`** (boot rebuild of `_gun_state` from the jsonl gun_fired lineage + C47 `buy_placed_post_fire` assertion).

## Prior art (C45)
- **FIX_SCORECARD_20260708 #9 (the finding this closes):** the 7:55 pm boot minted **7 post-fire buy placements on 3 LIVE events (ISOIMA×2, YAMSHI×3, MILMIS×2)** — gun amnesia until the poll re-fired; grace self-healed ≤ minutes. Real but bounded exposure at EVERY restart.
- **C-ORPHAN-FINGERPRINT (`6d84f27e`):** the pattern — rebuild state from the jsonl at boot, never from memory. This build is that pattern applied to the gun; it even reuses the fingerprint timestamps for the audit assertion.
- **Fused-gun deploy `6d84f27e`:** `_gun_state`/`_gun_stamp`/`gun_buy_refused` — the machinery being made restart-durable.

## LANE 1 — MECHANISM (deterministic, vs today's own tape)
- **The 7:55 pm boot, replayed under this build:** the lineage scan finds all 17 same-day fires (≤12h) in the two most-recent jsonl files → ISOIMA/YAMSHI/MILMIS boot as FIRED with `_events_live` set → the sibling-repost pass that placed the 7 post-fire buys hits `gun_buy_refused` at the chokepoint instead; the graced-cancel posture is in force from second zero. The 7:55 pm class is dead by construction.
- **Ordering:** the rebuild runs immediately after the fingerprint load, BEFORE the boot reconcile and the first conception/repost pass — the same slot that made the orphan fix airtight.
- **Audit teeth:** `buy_placed_post_fire` FAILS the boot audit if any resting buy's fingerprint placement-ts postdates its event's fire (+5s slack) — evasion of both the chokepoint and the rebuild is now a halt, not a silent leak. Pre-fire bids surviving grace are explicitly grace's domain (no false positives on the graced-pending class).
- **Bounds:** ≤12h fire recency (older matches are settled; unbounded carryover would only block buys on dead markets but stays clean); fail-soft (no lineage → empty state → poll re-fires exactly as today).
- **Byte-identity:** no config flag needed — the rebuild only ADDS entries to `_gun_state`/`_events_live` that the poll would re-derive minutes later; every consumer treats them identically. In-window behavior of unfired matches untouched.

## LANE 2 — SETTLEMENT P&L
$0 claimed. Refusal/state-rebuild only.

## Regression watches
`gun_state_rebuilt{n}` at every boot vs the day's fire log · `buy_placed_post_fire` (must stay 0) · post-fire placements in any boot minute (the scorecard's #9 check, re-run nightly).
