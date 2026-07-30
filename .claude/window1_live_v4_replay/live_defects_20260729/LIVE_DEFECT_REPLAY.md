# live_v4 four-defect replay — five fixed games

Fill model: resting order, price touches, it fills in full. No depth proof and
no five-contract gate.

The same five exact-start games and the same tape were used for every row. The
fill-poll class was reproduced by making the single-order status response stale
after a real paper fill while leaving account fill receipts and positions
current.

## Result

| Profile | Pair completions | Legs filled | External cancel rows | Defect signals | Worst fill-to-booking lag |
|---|---:|---:|---:|---:|---:|
| Four-defect control | 0/5 | 3/10 | 82 | 11 | 40.6s |
| Clock contract only | 0/5 | 3/10 | 82 | 11 | 40.6s |
| Field contract only | 0/5 | 1/10 | 92 | 16 | 40.6s |
| Contention DROP only | 0/5 | 1/10 | 18 | 7 | 6.5s |
| Fill receipt poll only | 0/5 | 3/10 | 31 | 5 | 4.0s |
| All four fixed | 0/5 | 1/10 | 19 | 0 | 2.5s |

“Defect signals” counts authority-foreign, authority-mismatch, unbooked-fill,
and naked-leg rows. `paper_order_cancelled` is the paper adapter’s duplicate
observation of the same cancellation and is not counted as another external
cancel in this table.

## What each repair did

### 1. Clock mismatch

The builder stores `bottom.t_med_min` and `path` slices in minutes relative to
the per-leg volume-derived `-0k` onset. The live dossier subtracted that value
from `tts_min`, which is T-minus scheduled start, and selected a path slice
with the same mismatched coordinate.

The repair refuses those legacy fields by default. It will read only an
explicit `tminus_actual_bell_med_min` / `path_tminus_actual_bell` contract.
Until a schedule-to-bell translation is available, it reports
`REFUSED_AXIS_MISMATCH`.

Measured effect: zero trace-level order effect, zero completion effect. These
consumers were shadow/dossier telemetry, not the placement timer. The old
readout was false, but it did not time every historical order.

### 2. Field contract

`reconcile()` emits normalized order rows as `order_id` and `price`. The
authority sweep now reads those exact fields. The explicit false replay branch
reads the historical `oid` / `px` names only to reproduce the defect.

Measured effect: the repair produced 14 mismatch detections and 7 sealed
re-anchors. It reduced filled legs from 3 to 1 and raised external cancel rows
from 82 to 92. The identity repair is correct; the sealed depth surface it
activates is not yet outcome-safe.

### 3. Contention DROP

The selector returns `DROP` when its fitted contention yield is below the
threshold. The deployed config had `selector_drop_enforce`, but that key
controls the separate pair-seesaw law. The placement gate reads
`contention_drop_enforced`; because that key was absent it defaulted false,
fell through to `_pa9`, and posted the order.

The branch gives the placement veto its own explicit enabled key.

Measured effect: filled legs fell from 3 to 1, completions stayed 0, and
external cancels fell from 82 to 18 because most entries were never posted.
This removes churn by refusing activity; it did not recover outcomes.

### 4. Fill-poll miss

`check_fills()` used one sequential `GET /portfolio/orders/{id}` per active
order. A stale/starved order response could miss a fill until the 60-second
position reconciliation saw exchange quantity ahead of engine quantity.

The repair makes one paginated `GET /portfolio/fills` receipt pass before the
legacy per-order loop, filters strictly to currently tracked entry order IDs,
and books those fills through the existing `_book_v4_entry_fill()` method.
The old per-order poll remains as fallback.

Measured effect: identical 3/10 leg fills and 0/5 completions, but the worst
booking delay fell from 40.6 seconds to 4.0 seconds. Unbooked-fill and
naked-leg signals fell from 3 each to zero. This is a safety fix, not an alpha
change.

## Deploy order

1. **Fill receipt poll first.** It preserves outcomes and removes the naked,
   unbooked interval.
2. **Clock-contract refusal second.** It removes a false telemetry
   interpretation and has no decision effect until a valid bell surface and
   bridge exist.
3. **Keep the canonical field repair, but do not let sealed re-anchor govern
   money before the depth refit is selected.** The contract is correct; its
   currently selected prices lost two of three filled legs in this sample.
4. **Contention DROP last, after the timing/depth surface is replaced.** The
   gate works, but the old fitted verdict mostly suppresses orders and does not
   improve completions.

Do not deploy this branch wholesale merely because all four switches exist in
the replay. The immediate safe set is fill receipt polling plus clock-axis
refusal. Field-driven sealed action and contention veto require the refitted
table/bridge decision.
