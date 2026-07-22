# Window-1 definition and freeze protocol

Status: **selection protocol frozen before candidate scoring; empirical Window-1 selection is blocked because the VPS validation gate fails.** The complete July 12–20 public event universe is ledgered, but causal book, print, and order-receipt gaps prohibit candidate scoring. No candidate is called the frozen Window-1 until validation passes and the development-only fit command writes `window1_freeze.json`.

Research base: `193e90da406214d2e5d9b2c7b5f752ddda046895`, the fetched `origin/blend/kalshi-occ-fallback` tip used to create `codex/window1-definition` on 2026-07-21.

## Scope and objective

This is entry research only. Window 2, exits, settlement, and realized exit P&L are not inputs, features, labels, or conclusions. DCA is not a candidate and is out of scope.

The primary operating target is both conditions together:

- `C / D >= 0.75`, where `D` is every floor-passing big-4 game and `C` is a game whose two required five-contract legs complete inside the selected Window 1.
- combined entry cost is below par: the two required-leg VWAPs sum to less than 100 cents.

The benchmark always prints raw `D`, `C`, and `S` before percentages. `S` is the number of completed games with combined entry cost below 100. It reports `C/D`, `S/C`, and `S/D`; missing, unknown, thin, corrupt, and error games remain in `D`.

The historical yardsticks are kept separate:

1. `combined entry cost = leg A fill VWAP + leg B fill VWAP`.
2. `combined-vs-par delta = combined entry cost - 100`. Negative means under par. The Vault legacy tier at combined cost at or below 97 is reported separately, not substituted for the strict under-100 target.
3. `individual leg reference delta = leg fill VWAP - frozen W1-close reference for that leg`.
4. `pair reference delta = the sum of the two individual leg reference deltas`.

The Vault defines distortion or discount as combined cost against par. The chronological Loop-5 record defines its per-leg delta as fill minus W1 close and pair delta as the sum of those per-leg values. Neither is realized exit P&L.

## Immutable floor law

The source universe is every exchange-catalog big-4 match event dated 2026-07-12 through 2026-07-20 inclusive:

- ATP main
- WTA main
- ATP challenger
- WTA challenger

Every such game passes by default. The only allowed pre-simulation exclusion is an independently receipted cancellation or void that occurred before the candidate Window-1 left edge. Unknown class, missing band, missing leg map, thin tape, missing file, source gap, corrupt interval, and simulator error are named outcomes and remain in the denominator.

Each ledger row carries event id, category, date, two leg tickers where known, required lot, floor decision, floor reason, evidence receipt, period, and data state. The ledger is sorted, written once, hashed, and rechecked before fit and holdout.

## Clock and boundary candidates

The simulated clock uses only schedule knowledge available at the simulated timestamp. A later corrected schedule may not leak backward.

Left-edge candidates, evaluated on fit only, are relative to the contemporaneous authoritative scheduled-start snapshot:

- T minus 8 hours
- T minus 6 hours
- T minus 4 hours
- T minus 2 hours

The right edge is the independently verified actual start when the actual-start receipt becomes available. Accepted actual-start authorities are Sportradar milestone, an official start feed, or exchange status. Exchange timestamps control ordering.

When actual start is not observed, the row is explicitly schedule-only and the fit-only corridor candidates are scheduled time plus 15, 30, 45, or 60 minutes. A schedule-only row can never end at scheduled time and can never be labeled an observed right edge.

Boundary sensitivity must publish all 16 left-edge and corridor combinations on the fit denominator. The selected boundary is the deterministic fit winner under this order:

1. maximize `C/D`;
2. then maximize `S/D`;
3. then minimize mean combined-vs-par delta;
4. then deterministic candidate id.

No boundary result is published because the VPS validation run returned 3,683 mismatches. The gate was run; it did not pass.

## Entry-policy candidates

All candidates use five contracts per required leg and the same event ledger, clocks, data filters, and queue model.

The fit menu is fixed before scoring:

- discovery-time park of both legs at the causal touch;
- original walk law: rest both legs, re-aim only on causal book or verified-print evidence, and never churn on an unobserved timer;
- existing backwalk or divot placement at its own lawful depth;
- depth-aware placement using the full ladder and queue bounds;
- per-category and pre-established January shape-cell placement;
- simultaneous posting versus declared first-leg and second-leg sequencing;
- after the first leg fills, a declared second-leg re-aim bounded by combined entry cost, with the first fill known at that timestamp;
- queue- and verified-volume-aware parking.

No candidate may use a later close, settlement, exit, holdout outcome, or Window-2 state to choose an entry. No candidate may silently refuse a floor-passing game; an unplaced leg is a non-completion.

## Causal feature stack

Macrostructure features are category, favorite or underdog role, contemporaneous schedule source and confidence, the pre-established January-present shape prior, time to scheduled start, causal phase, and cross-game or class liquidity visible at that timestamp.

Microstructure features are full bid and ask ladders, depth by level, bid-versus-ask imbalance, ask-ceiling pressure, bid support, spread and spread change, bounded queue position, attributable own posted volume, verified-print direction, size and tempo, replenishment, cancellation and absorption bounds, movement below top five, movement around the resting order, and first-leg fill state while managing the sibling.

The Pridankina/Udvarty-style extreme ask-over-bid ladder is a required fit sanity class. It is measured across the corpus at the causal timestamp and ablated; a single screenshot cannot create a rule.

Feature ablations remove one family at a time. Major features are also tested independently where sample support permits. Each result prints the change in raw `D`, `C`, `S`, combined-vs-par delta, individual leg reference deltas, games per day, and cents by class.

## Fill and non-fill law

A Window-1 completion requires official exchange fill receipts for the full five-contract lot on both legs before the selected right edge. For hypothetical replay, the order must have a causal placement receipt, full-ladder queue state, and only receipt-deduplicated true prints with independently verified size.

Missing or zero print size contributes zero. Synthetic transition rows contribute zero. Local receipt time is metadata. Tape, WebSocket, and transition duplicates share one exchange receipt identity and are counted once.

Queue cancellation ownership is bounded. A simulated fill is exact only if even the pessimistic queue bound completes. A simulated non-fill is exact only if even the optimistic queue bound does not complete. The interval between those bounds is `queue_unknown`, never a fill.

`premarket_ticks` is top-five only. `depth_recorder` is snapshot, top-20, and change-deduplicated. Neither can prove full queue position. `ws_depth` may support the queue only within a full, readable, uncorrupted sequence epoch with no reconnect gap. Own resting volume is attributable only through exact engine order and client-order fingerprints.

## Validation and freeze sequence

The gate compares every official entry order on every floor-passing operational event, including orders that never filled. It requires exact agreement on event, ticker, leg, order identity, posted price, quantity, exchange clock, fill or non-fill, first-fill time, completion time, and combined entry cost. Passing means 100 percent agreement and at least one compared order; there is no 90-percent or aggregate-pair substitute.

The amended chronological split was declared before any candidate scoring:

- development/backwalk history: 2026-07-12 through 2026-07-20 inclusive;
- forward holdout: the first three complete UTC dates strictly after the UTC date containing the eventual fit freeze.

July 18–20 is inspected history and is not untouched. Boundary selection, policy tuning, and ablation may use the full development period only. The fit command freezes the development-ledger subset hash, selected boundary and policy id, metric constants, fit-input hash, freeze timestamp, and the three forward dates. The freeze receipt and those dates must be committed before the holdout ledger is built or any holdout evidence is opened.

The forward sample is never extended after viewing. If its `D` is too small for a stable claim, the report says so. The holdout runner accepts only the frozen candidate and a declaration tied to the committed freeze receipt, rejects a changed development subset, rejects unregistered holdout dates, and refuses a second result.

Current development-ledger state: **immutable, 804/804 floor-passing big-4 events, SHA-256 `28348235eef26c10475e016614e999d83304ce01a587f890cd9f739c41269999`**. Current freeze state: **not empirically frozen**. Current validation state: **failed after event-level comparison**. Therefore strategy `C` and `S`, delta distributions, the 75-percent target, and an empirical ceiling are not adjudicated.
