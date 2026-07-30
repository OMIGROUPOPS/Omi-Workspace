# One-authority census — 2026-07-30

Rechecked against exact deployed source commit
`c40a8f9abc3d38792b82be049adefb95c3d64752`.

## Finding

The live code does not implement one pricing authority. It lets many organs
compute a price, passes that price into `place_order`, and only then sometimes
replaces it with a sealed fish. That is a late rewrite, not structural
exclusion.

The previously found `order_id`/`price` versus `oid`/`px` defect is repaired
in this deployed base by the single `_canon_order()` boundary. The repair
holds and fails closed on an unreadable bot-owned price. That fixes order
identity; it does not fix the authority architecture below.

## Authority named by the current dossier

`_price_authority()` has only three answers:

| State at consultation | Named authority |
|---|---|
| pair is `flat_flat`, called band has a sealed row, leg inventory below lot | `SEAL` |
| same, but the leg already holds a lot | `SEAL-HELD` |
| every other state, including any exception while reading sealed state | `LEGACY:path_aim` |

It has no distinct state for completion, pair-governor, DCA, cadence, recovery,
or drain replay, although all of those paths can submit a buy price.

## Every real entry-price writer

| Writer | Price it proposes |
|---|---|
| Initial V4 conception | ATLAS `current_anchor - bottom.depth_p50`; preliminary entry/cohort/staircase prices are calculated first and overwritten |
| Orientation variant | current preliminary target for riser; ATLAS p75 depth for faller |
| Fresh sibling bound | lower of proposed price and `combined_goal - booked_sibling_basis` |
| Sibling lower/re-aim | goal-derived level |
| Missing-sibling repost | aim-table depth and combined-goal level |
| Pair-governor scoot | governor-derived sibling level |
| Completion reprice | `completion_cells` X, current ask, and ATLAS sibling path depth |
| Live completion cross | current ask |
| Completion freshness / revert | recomputed completion target or prior resting price |
| Walk/repost | regime offset, join bid, staircase surface, aim-table reshuffle, cohort re-aim, sanctioned-walk clamps |
| Fallback/cadence/deadline | ask-minus-one, current bid/ask, or cadence target |
| Legacy pending/FV route | legacy cell/FV arithmetic |
| DCA and reconcile-DCA | fill basis minus DCA trigger |
| Drain replay / recovery | persisted historical order price |
| Authority sweep | sealed fish |

Exit sells are outside the entry-price authority law.

## Exact chokepoint failures

1. **Other organs remain fully capable of pricing.** Every writer above computes
   an integer before calling `place_order`.
2. **SEAL overwrites instead of excluding.** `_place_order_unlocked` changes the
   caller's price to the fish when they differ.
3. **The caller is not told.** `place_order` returns `(order_id, response)`, not
   the final authorized price. Several callers then store their original
   proposal in `Position.entry_price`, while the exchange received the fish.
4. **Price-sensitive guards run on the wrong price.** Never-marketable,
   `[5,95)`, pair-seesaw, and other checks run before the sealed rewrite. They
   are not re-run on the fish.
5. **Authority lookup fails open.** `_price_authority()` catches all exceptions
   and returns `LEGACY:path_aim`; the placement wrapper also logs authority
   errors and continues.
6. **The dossier is descriptive, not binding.** It names SEAL while the same
   decision record can still carry an ATLAS aim.
7. **The reconciliation sweep proves the invariant is not structural.** It
   searches for mismatches later, cancels them, and reposts at the fish.

## Required replacement contract

The lawful structure is:

1. Resolve and name the authority before any price calculation.
2. The authority alone returns an `AuthorizedEntryIntent` containing authority,
   fitted-surface identity, exact input key and timestamp, price, and phase.
3. Other organs may return constraints or vetoes, never another price.
4. `place_order` accepts an authorized intent for entry buys, not a bare price.
5. Any missing/invalid authority contract fails closed.
6. All price-sensitive guards evaluate the final authorized price.
7. The final price is returned to and stored by the caller.

This replacement must wait for the lawful aim-surface contract. Until then,
sealed action and DROP enforcement must remain held.
