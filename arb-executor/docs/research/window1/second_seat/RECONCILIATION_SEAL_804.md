# Full reconciliation seal — all 804 events

Analysis seat only. Read-only. Unauthenticated public `/markets/trades`. Machine
artifact:
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/RECONCILIATION_SEAL_804.json`.

## What was done

The 21-game trades re-pull diff, extended to the **entire corpus**: public
`/markets/trades` re-pulled today for **all 804 events (1,608 legs)**, window-filtered
to each ticker's guarded `[left, right]`, and diffed by `trade_id` against our
`prints.jsonl`. Same method as the spot check — per-game verdict PRINTS_FAITHFUL /
DEFECT / UNPULLABLE.

## Result — the seal holds

| verdict | events |
|---|---:|
| **PRINTS_FAITHFUL** | **804** |
| DEFECT | 0 |
| UNPULLABLE | 0 |
| **total** | **804** |

**Exchange trades 373,203 = our prints 373,203, exact.** Zero exchange trades we lack,
zero we hold that the exchange lacks, zero price/size/side mismatches, zero unpullable
tickers. The lossless-by-design architecture (WS-delta book + `trade_id`-keyed REST
trades) is now confirmed empirically over the **whole** population, not a 21-game
sample. Every ceiling artifact in this namespace rests on a fully-reconciled tape.

## Standing-audit proposal — nightly spot-check

To keep the seal live against silent recorder drift or exchange-side restatement
(recorded in the artifact as `nightly_spotcheck_spec`):

- **Cadence:** nightly 02:00 ET.
- **Method:** draw N=20 random Window-1 events (seeded by date), re-pull public
  `/markets/trades` for both legs over the guarded window, diff by `trade_id` vs
  `prints.jsonl`.
- **Alarm** on any of: `ex_not_ours > 0`, `ours_not_ex > 0`, price/size/side mismatch
  `> 0`, or an UNPULLABLE on a previously-pullable ticker. Page on the first non-zero.
- **Escalation:** on alarm, widen to the full 804 reconciliation and freeze downstream
  ceiling artifacts until the diff is explained.
- **Rationale:** cheap standing guard; the 21-of-21 and this full-804 seal are the
  baseline it defends. A green nightly diff is the daily proof the denominator under
  every V-series ceiling is still exactly the exchange's own record.

## Conservation

804 events = 804 PRINTS_FAITHFUL + 0 DEFECT + 0 UNPULLABLE. 1,608 legs pulled, 0
unpullable. 373,203 exchange trades reconciled 1:1 against 373,203 stored prints.
