# P0 REAL-START v4 PRE-RUN

Status: **PASS — frozen for independent audit; not deployed**

## Bound lineage

- Parent / P0 v1-v3 base: `a4996dd00e82ed3534f97a09251697f1d82dbbab`
- Base live_v4.py: `949f6995352b7be6f73be8e44af01a70a758c63e` / `cb9e6cc3810d156da3e52df69b8058f25ec1d05aa6a1430aeccf4d869b31aca8` / `1008748` bytes
- P0 v1-v4 candidate: `363e1c8a11525915dc053175283a6c81b72e8b0d` / `07b6511d9d8b81f9bd563764d0a72a729426f34244ad8a4c1eff96db4b403e4e` / `1032682` bytes
- P0 v4 patch: `9702c11215ee3f12dd0c96dea2d2d35b52ca705272e9cc1c85285bd497ce438a` / `30291` bytes

The reverse patch check reproduces the exact v1-v3 base. The source patch
changes only boot hydration and entry-authority ordering. It changes no
strong-live threshold, schedule rule, cadence rule, print predicate, exit,
settlement, DCA, CASUKA, keepalive, deployment, or Window-1/T2 mechanism.

## Result

Every discovered entry-eligible event starts fail-closed. A bounded,
receipt-identified historical public-trade scan runs before entry authority.
`PENDING`, `EVALUATING`, and `NO_CALL` refuse buys; complete insufficient tape
defers to the unchanged v1-v3 gate; `REAL_START` is monotonic and sweeps entry
buys. The sole exchange POST chokepoint revalidates immediately before POST.
Exit sells and reconciliation do not wait on hydration.

The SHICHA fresh-boot fixture passes: 651 lawful historical prints fire the
unchanged predicate despite future schedule/occurrence and absent scoreboard
join; SHI 5@79 is never posted, a resting entry is swept, exits remain lawful,
and the historical grade remains W2.

## Validation

- Focused v4 tests: 23/23
- Inherited P0 v1-v3 assertions: 56/56
- Negative/adversarial fixtures: 16/16
- Compile and AST call-site lint: PASS
- Two clean deterministic regenerations: byte-identical
- Synthetic bounded performance: 804 events / 6,432 rows in
  1012.562 ms median total; worst observed event
  12.336 ms; peak traced memory
  3529118 bytes

## Containment

The engine remained stopped, keepalive cron remained disabled, and the
original crontab backup remained immutable under the controlling receipt
`fd623dd042da2f1dfb9479c8a759c8c610672215`. Construction used read-only containment verification.
No deployment, restart, cron restoration, order/position/configuration
mutation, CASUKA integration, or T2 work occurred.
