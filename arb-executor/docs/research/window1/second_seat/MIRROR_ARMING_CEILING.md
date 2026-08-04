# Mirror-arming ceiling — model-free, V28 population

Analysis seat only. Descriptive. Read-only. **No access to Codex's V29 work.**
Population drawn from V28's trace (commit 3339f30); the arming test is computed
independently from each leg's own raw tape and my own audited closes (commit
50ce0f49). Per-leg rows in `MIRROR_ARMING_CEILING.csv`; grids in
`MIRROR_ARMING_CEILING_SUMMARY.json`.

## Test

For each leg, after its **sibling's credited fill timestamp**, did a lawful entry
exist on this leg's own tape — a qualifying ask (≥10s dwell, ≥5-lot, residency-
maker) at a price **≤ both** `99 − sibling_fill` (the pair-completion cap, so the
combined stays under 100) **and** `own_audited_close − 1` (strictly below its own
landing)? CONVERTIBLE cites the first qualifying moment + price; NOT_CONVERTIBLE
cites which bound blocked it (**CAP_UNREACHABLE** = the `99 − sibling_fill` cap
binds; **PRICE_NEVER_PRINTED** = no below-close-1 qualifying ask after the fill).

## Populations & conservation

- **Class (a) — carried pairs:** the 148 completed pairs that cashed under par but
  **not** as clean joint captures (`PAIR_COMPLETED_UNDER_PAR_BUT_NOT_BOTH_LEGS_STRICTLY_BELOW_AUDITED_CLOSE`),
  both legs credited → **296 legs**. (This is the mirror-arming-improvable read of
  the operator's ~144 strict-carried set.)
- **Class (b) — completion-mirror FN legs:** the **237** uncredited legs whose
  sibling was credited and whose later qualifying floor was strictly below own
  close (V28's COMPLETION false-negative class).

**533 legs = 296 (a) + 237 (b), each in exactly one row** (disjoint: carried pairs
are both-credited; FN legs are uncredited).

## Class (b) — the FN class collapses under the completion cap

| verdict | legs | share |
|---|---:|---:|
| CONVERTIBLE | **29** | 12% |
| NOT_CONVERTIBLE | 208 | 88% |
| — CAP_UNREACHABLE (`99 − sibling_fill` binds) | **201** | 85% |
| — PRICE_NEVER_PRINTED | 7 | 3% |

**This is the load-bearing finding.** Codex flagged 237 legs as false-negatives
because a below-close price printed after the sibling filled. But once the
**pair-completion cap** is applied — the mirror must be buyable at `≤ 99 −
sibling_fill` to keep the combined under 100 — **only 29 survive.** On **201 of 237
(85%) the cap is unreachable: the sibling already filled too high, so no below-close
entry on the mirror's tape could complete the pair under par.** The mirror-arming
ceiling for the FN class is **29, not 237** — the FN count overstates the
convertible opportunity by ~8×.

## Class (a) — carried pairs could often have been cheaper

| verdict | legs | share |
|---|---:|---:|
| CONVERTIBLE | **119** | 40% |
| NOT_CONVERTIBLE | 177 | 60% |
| — PRICE_NEVER_PRINTED | 117 | 40% |
| — CAP_UNREACHABLE | 60 | 20% |

40% of carried-pair legs had a below-close, under-cap entry available after the
sibling filled — the pair completed, but a cleaner (both-below-close) capture was
on the tape. Here the binding NOT_CONVERTIBLE reason flips: PRICE_NEVER_PRINTED
(117) dominates over CAP_UNREACHABLE (60), because carried pairs completed at lower
combined prices (the cap is looser), so the failure is the price simply not
returning below the close.

## Release timing — how fast V29's descent trigger must be

Minutes from the sibling's credited fill to the first qualifying arming moment,
among convertibles:

| class | median | ≤5 min | ≤15 min | ≤60 min | >60 min |
|---|---:|---:|---:|---:|---:|
| (b) FN mirror | **0.9 min** | **21 / 29** | 22 | 22 | 7 |
| (a) carried | 102.8 min | 29 / 119 | 39 | 53 | 66 |

**The FN convertibles release almost immediately — median 0.9 minutes, 21 of 29
within five minutes of the sibling fill.** A descent trigger that arms the mirror
must fire within a ~1-5 minute window of the sibling's fill to catch them; a slow
trigger misses the entire FN-convertible set. The carried-pair convertibles release
far more slowly (median 1.7 h), so those are a patience play, not a speed play.

## Per category × region (CONVERTIBLE / total)

Class (b) FN mirror:

| cat | le25 | 26_50 | 51_75 | ge76 |
|---|---|---|---|---|
| ATP_CHALL | 2/15 | 12/57 | 2/42 | 0/10 |
| ATP_MAIN | 1/9 | 3/20 | 0/9 | 0/0 |
| WTA_MAIN | 2/10 | 2/11 | 0/10 | 0/9 |
| WTA_CHALL | 1/3 | 3/10 | 1/14 | 0/8 |

Class (a) carried (full grid in the JSON): the convertibles concentrate in the
mid regions (26_50, 51_75) across all categories, mirroring where the pair cap has
room.

## Reading

The mirror-arming ceiling is small and cap-limited. For the FN class the honest
convertible count is **29** — the pair-completion cap, set by how high the sibling
already filled, forbids the other 201 regardless of what printed below the close.
Where conversion is possible it is available within minutes, so the mechanism V29
needs is a **fast** descent trigger on the sibling's fill, not a wide net. For the
carried pairs, 40% had a cleaner capture on the tape but on a slow clock — a
separate, patience-shaped opportunity. Model-free throughout; every arming moment
is a real qualifying tape row after the sibling's fill.

## Artifacts

`MIRROR_ARMING_CEILING.csv` (per leg: class, sibling fill, own close, both caps,
target, verdict, reason, first qualifying moment + price, release minutes) and
`MIRROR_ARMING_CEILING_SUMMARY.json`.
