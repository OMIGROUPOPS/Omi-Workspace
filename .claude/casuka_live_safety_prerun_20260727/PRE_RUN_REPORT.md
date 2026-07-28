# CASUKA Live-Safety Repair PRE-RUN

Status: **FROZEN FOR INDEPENDENT AUDIT — NOT DEPLOYED**

## Lineage

- Branch: `codex/casuka-live-safety-repair`
- Exact parent: `a4996dd00e82ed3534f97a09251697f1d82dbbab`
- Parent remote lineage: `origin/p0/real-start-entry-guard`
- Controlling independent reproduction: `b442908f3b253d1e13d5b2a5e93c3dbf0491320d`
- Audit report blob: `c31f208ef86f4831352f6dffe0cc958459d82fc3`
- Frozen repair packet blob: `cd41db2eaf0c37a2ac532682ecaade08c33649f7`
- Parent and audit `arb-executor/live_v4.py` blob: `949f6995352b7be6f73be8e44af01a70a758c63e`

The identical parent/audit engine blob proves this repair starts from the
engine implementation independently reproduced in the CASUKA audit.

## Diff containment

Product code changes are limited to `arb-executor/live_v4.py`. One focused
test module and this sanitized PRE-RUN receipt directory are additions. No
configuration, deployment, state, order, position, strategy, research, or T2
file changed.

## Frozen repairs

### D1 — reconcile-cycle exit-intent serialization

Each reconcile pass now owns one per-ticker exit-intent ledger. Successful
exit resets and sell posts update it. `RECONCILE_EXIT_TOPUP` discards the
cycle's original `pos_map`/`ord_map` quantity calculation and re-reads the
authoritative position and all paginated resting sells before calculating a
top-up. The shared sell chokepoint re-reads again immediately before POST.

Both organ orderings converge:

- heal then top-up: heal replaces 2 with 5; top-up records a named zero/no-op;
- top-up then heal: interim 3 is cancelled with the old 2; heal leaves one
  5-contract exit.

### D2 — sell-side exchange-truth clamp

The single order-submission chokepoint performs the last operation before
every sell POST:

`available = max(0, exchange_position_qty - effective_resting_sell_qty)`

The exchange position and complete paginated resting-sell census are
authoritative. The reconcile-cycle floor covers just-acknowledged intent not
yet visible in a later GET. Missing/malformed truth and repeated cursors fail
closed. A nonpositive or excessive proposal is refused in full, receipted as
`sell_exchange_truth_refused`, and sent to the existing best-effort operator
notification path. Buy-side, retry, post-only, exit, and quarantine laws are
unchanged.

### D3 — pair-classifier truth

Pair state is `filled` only when the in-memory position has strictly positive
booked `entry_qty` **and** the audit's authoritative unsettled-position map
has strictly positive quantity. Settled state is named `settled`. A stale
dictionary member, an `entry_resting` zero-booked leg, or a stale active leg
with no unsettled holding cannot manufacture `filled` or `pair_incomplete`.

## CASUKA causal replay

The focused in-memory exchange replay preserves the reproduced sequence:

1. partial held quantity 2 receives one 2-contract exit;
2. authoritative held quantity advances to 5;
3. the heal cancels the 2-contract exit and posts one 5-contract exit;
4. same-cycle top-up re-reads held 5/resting 5 and posts zero;
5. final resting sell quantity is exactly 5 and never exceeds held quantity.

No audit incident order or live account state was queried or mutated.

## Validation

- Focused CASUKA fixtures: 12/12 pass.
- Relevant inherited suites: 7/7 pass:
  `test_lane_a_live_safety`, `test_lane_a_review_fixes`, `test_order_v2`,
  `test_bbo_settlement_gate`, `test_shutdown`, `test_monotonic_cut`,
  `test_fv_quote`.
- Deployment AST lint: PASS.
- Complete inherited script census at parent: 46/84 pass, 38 historical
  failures.
- Complete script census after repair: 47/85 pass, 38 failures.
- The 38 inherited failure names are byte-for-byte identical before/after;
  the only net test change is the new passing CASUKA suite.
- Python compile and `git diff --check`: PASS.
- Offline smoke replay: not run because this clean worktree contains no
  recorded `premarket_ticks`; the smoke gate itself refuses an empty corpus.

The acceptance replay uses in-memory API doubles only. It creates no network
client and performs no live read or write.

## Before/after invariants

| Invariant | Before | After |
|---|---|---|
| Heal 2→5 then same-cycle top-up | stale top-up could post 3 | top-up re-reads and posts 0 |
| New sell vs held/resting truth | no shared sell clamp | every sell fails closed at chokepoint |
| Final CAS resting sells | 8 against held 5 | exactly one 5-lot against held 5 |
| Filled classifier | `ticker in self.positions` | booked qty >0 and unsettled held qty >0 |
| Buy/retry/quarantine protections | existing | unchanged |

## Non-action proof

There was no deployment, process restart, exchange query, network order call,
order cancellation, order placement, position mutation, configuration change,
or T2 research-worktree modification. See `FORBIDDEN_ACCESS_RECEIPT.json`.
