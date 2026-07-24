# Window-1 Start-Truth Recovery Round 2 — freeze declaration

This declaration extends, but does not overwrite, the V3 real-start ledger
frozen at `224417da642a9f378a0d83f76edffe9890cb4a6f`.

## Immutable scope

- D remains the 804 July 12-20 big-4 floor-passing events.
- The 234 V3 exact starts and 31 V3 clean intervals are preserved.
- Round 2 targets only the 539 V3 events that lacked a positive-capable
  boundary.
- Start extraction may read event identity, clocks, status, score/result,
  lifecycle, and source lineage only.
- It may not read policy decisions, placements, fills, prices, deltas,
  candidate results, or success/failure labels.
- Schedule may align identity but may not form a start endpoint.

## New exact-source law

The retained TennisExplorer historical results page is the provider surface
used by `te_live.py` and named `te_honest` in the chronological Living Vault.
A result start clock is accepted at minute precision only when all of these
facts are present:

1. both Kalshi structured-target competitors match the two TennisExplorer
   players by normalized surname and first initial;
2. tournament canonical name and competition class match;
3. the provider page date is within two days of the retained milestone date,
   used for identity alignment only;
4. exactly one provider match ID satisfies that crosswalk;
5. the row has a completed result and a non-null start clock; and
6. the page-declared Berlin/Prague/Vienna timezone is converted with
   `Europe/Berlin`.

A shared city is insufficient when competition class differs. In particular,
WTA-125/ITF Istanbul collisions are rejected.

## Conflict law

Every source is retained. A raw milestone `not_started` receipt with higher
precedence at or after the result clock blocks promotion and leaves the event
`CONTRADICTORY`. Lower-precedence tape or engine live-by observations that
precede an accepted exact provider start remain named conflicts; source
precedence controls, not the value favorable to historical policy results.

## Frozen result

- exact = 687
- clean intervals = 31
- positive-capable = 718
- timing-blocked = 86
- required = 603
- margin = 115
- newly recovered exact = 453
- higher-precedence conflicts blocked = 11
- frozen ledger SHA-256 =
  `9d972c17837d3e36789c10396bd3a7c825c512c2eac3aa2fcbeabf96ed6a23e0`

The gate passes. Historical receipt re-adjudication is permitted solely to
classify the already-published lifecycle against this frozen ledger. The
six-family/24-policy development runner remains frozen and unscored until
independent ledger review. No holdout is open.
