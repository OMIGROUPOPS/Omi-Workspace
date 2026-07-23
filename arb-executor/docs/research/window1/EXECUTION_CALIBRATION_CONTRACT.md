# Window-1 execution-calibration contract

Status: calibration-only gate. It does not authorize candidate scoring,
tuning, ablation, a holdout read, or production mutation.

## Immutable denominator and stop law

`D` is the 804 floor-passing July 12-20 big-4 events and exactly 1,608
required legs. Missing or uncertain evidence censors a source, feature, leg,
or boundary. It never removes an event from `D` and never becomes a simpler
proxy.

The seven-hour `C=4 / X=734` output remains a reproducible narrow-proxy
baseline. Nothing in this gate overwrites or reinterprets that artifact.
July 24-26 remains the registered holdout for that baseline and is not an
input to this gate. A materially corrected instrument receives a new
prospective holdout only after it passes validation.

The calibration run must stop before computing `C`, `PC`, `NC`, `IC`, `X`,
dynamic-floor gap, dip/catch performance, candidate ranks, ablations, or
policy parameters.

## A. Real-start contract

Every event receives one of four precision classes:

1. exact official/milestone bell;
2. causal start interval;
3. causal live-by bound; or
4. schedule-only bound.

The causal source precedence is official/milestone bell,
`market_lifecycle_v2` exchange transition, mapped live-score onset/bound,
defensible tape-regime onset, and schedule as last resort. A schedule-only
row is always censored and can never carry an exact start. A current-state
live-score receipt and a first market trade are not exact starts.

## B. Causal market-data contract

The canonical true-print stream is keyed by exchange `trade_id` and uses the
exchange timestamp, YES price, and positive exchange size. Archived WS trade
messages are reconciled to the cursor-complete public tape at trade identity,
ticker, WS millisecond timestamp precision, price, and size. Reconnect
duplicates are counted once. A zero-size row, book transition, touch, or
trade-through without an identified positive print cannot become a fill.

Top-five pressure is usable only at the timestamped snapshots actually
recorded. Raw WS deltas do not become full depth. A full-depth feature
requires a non-empty ladder snapshot followed by sequence-continuous deltas
inside a recorder-started reconnect epoch. No July 12-20 required ticker
currently satisfies that ancestry contract.

## C. Historical execution contract

The receipt-grain replay and any future candidate scorer share
`window1_execution_kernel.py`. The historical path consumes:

- exact accepted and failed placement rows, including price, quantity and
  timestamps;
- official private fills keyed by fill and order identity;
- preserved cancellation receipts;
- causal nonplacement receipts; and
- the conception/event/leg lineage used by the frozen lifecycle validation.

The pass target is exact and non-negotiable:

- 258 exact-five filled legs;
- 12 other-quantity filled legs;
- 870 exact nonfills;
- 468 legitimately censored legs; and
- zero event/leg, quantity, price, timestamp, duplicate-receipt, zero-size,
  or denominator mismatches.

All relevant dual exact-five events must also reproduce. The replay emits one
public-safe row per required leg plus a mismatch-only ledger. Private order,
fill, trade, client-order, account, and attempt identities remain outside
Git.

## D. Full OS research adapter

`WINDOW1_OS_ADAPTER_CONTRACT.json` is the versioned inventory. Each component
has exactly one status: `available`, `partially_available`, `unavailable`, or
`excluded`, plus exact source receipts, a reason, and a missing-input action.
The adapter must include pair/sibling law, sealed bands, dual divot/catch,
drift, cohorts, orientation, walk/park, riser/deceleration/mirror/seesaw,
dynamic floor and recut cells, ATLAS/reach, causal FV/book voices, BBO/top
five, and own-order fingerprints/contributed volume.

`AIM_V2` is `excluded`. Full WS depth is `unavailable`. Pinnacle is
unavailable unless a causal recorded row is produced. Those states censor
their named features and do not fail the adapter merely because the input
never existed. The adapter fails if a source receipt is missing, a component
is omitted, AIM_V2 is enabled, full depth is overstated, or any missing input
is silently replaced.

## Gate rule

The complete gate passes only when:

- all 804 start-ledger rows satisfy the precision contract;
- WS/public trade identity reconciliation has zero mismatches;
- top-five gaps and full-depth unavailability are explicitly censored;
- the shared execution kernel reproduces all 1,608 frozen leg outcomes with
  zero mismatches; and
- the OS adapter is complete and fail-closed.

Any mismatch yields `GATE FAIL`, and candidate scoring remains forbidden.

## Reproduction

Use a detached research worktree and owner-only evidence paths. First run the
unit/regression tests:

```text
python -m pytest -q \
  arb-executor/tests/test_window1_execution_kernel.py \
  arb-executor/tests/test_window1_execution_calibration.py \
  arb-executor/tests/test_window1_ws_trade_reconcile.py \
  arb-executor/tests/test_window1_fit_benchmark.py \
  arb-executor/tests/test_window1_lifecycle_validator.py
```

Run `window1_ws_trade_reconcile.py` against the immutable raw WS directory,
complete public true-print JSONL and their frozen receipts. Keep its SQLite
work database outside Git. Then run `window1_execution_calibration.py` with
the owner-only placement/fill/lifecycle inputs and the committed public
ledgers. Its output directory may enter Git only after the manifest confirms
that no private paths or identities were emitted.

If the gate passes and the operator separately authorizes scoring, the
smallest next run is one deterministic, predeclared corrected-instrument
replay over all `D=804` development events using the frozen adapter and
kernel versions. It reports `C`, `PC`, `NC`, `IC`, `X`, dynamic-floor gap,
and per-leg dip/catch separately. It performs no tuning, ablation, holdout
read, or denominator change.
