# Authority map — artifact defect fix + error-bar hardening

Analysis seat only. Descriptive. Read-only. Fixes a machine-map defect in
`ASYMMETRIC_SPREAD_SUMMARY.json` (e3833e63) and hardens the BID authority map with
error bars. Same population, same isolation. Machine output in
`ASYMMETRIC_AUTHORITY_HARDENED.json`; the old summary is stamped `SUPERSEDED_BY`,
not deleted. Conservation unchanged: **1,512 covered + 96 uncovered = 1,608.**

## 1. The defect

`authority_map_bid.authorized` in the prior summary held **13 cells / 152 legs** —
including the **8 wide-book (>3c) rows** the report's prose excluded as spread
artifacts. The exclusion lived only in the narrative; the machine map Codex
reconciles against still carried the artifacts, so it could inherit them.

**Fix: the regime exclusion is now encoded in the rule.** Authority is grantable
**only in the ≤1c and 2-3c regimes**; every >3c row carries
`SPREAD_ARTIFACT_EXCLUDED` and can never be granted (its BID P=1.0 is the spread,
not skill). Corrected machine map:

- **authorized: 5 cells / 105 legs** (matches expected) — all 2-3c:
  ATP_CHALL le25, ATP_MAIN 51_75, WTA_MAIN le25, WTA_MAIN 51_75, WTA_MAIN ge76.
- **SPREAD_ARTIFACT_EXCLUDED: 8 cells / 47 legs** (>3c) — ATP_CHALL 51_75/ge76,
  ATP_MAIN le25, WTA_MAIN 51_75/ge76/26_50, WTA_CHALL 51_75/ge76.

## 2. Hardening — Wilson lower ≥ 0.70 AND p90 shortfall ≤ 4c

The 5 corrected candidates, BID-anchored, with a Wilson-95 lower bound on P, a
2,000-sample bootstrap CI on mean shortfall, and the p90 / max of the per-leg loss:

| cell | regime | n | P | **Wilson lo** | mean sf | sf CI95 | **p90** | max | verdict |
|---|---|---:|---:|---:|---:|---|---:|---:|---|
| ATP_CHALL le25 | 2-3c | 36 | .889 | **.747** | 2 | [1.0, 4.0] | 0.5 | 4 | **SURVIVES** |
| ATP_MAIN 51_75 | 2-3c | 24 | .917 | **.742** | 2 | [0.0, 2.0] | 0.0 | 2 | **SURVIVES** |
| WTA_MAIN ge76 | 2-3c | 11 | 1.000 | **.741** | 0 | [0.0, 0.0] | 0.0 | 0 | **SURVIVES** |
| WTA_MAIN 51_75 | 2-3c | 20 | .900 | .699 | 1 | [0.0, 1.0] | 0.1 | 1 | FAIL — Wilson .699 < .70 |
| WTA_MAIN le25 | 2-3c | 14 | .857 | .601 | 2 | [0.0, 3.0] | 0.7 | 3 | FAIL — Wilson .601 < .70 (thin) |

**Hardened authority = 3 cells / 71 legs: ATP_CHALL le25, ATP_MAIN 51_75,
WTA_MAIN ge76 (all 2-3c).**

The two cells you put on trial split on their point estimate, not their n:
**WTA_MAIN ge76 (n=11) survives** because a perfect 11/11 pushes the Wilson lower
to .741; **WTA_MAIN le25 (n=14) fails** because 12/14 (P .857) only reaches .601.
And **WTA_MAIN 51_75 fails by 0.001** — its point P=.900 looked safe but the
20-leg interval crosses .70 (.699); with error bars it is a coin-flip, not
authority. No survivor's p90 shortfall exceeds 0.5c; ATP_CHALL le25 carries the
only non-trivial tail (max 4c on one leg, p90 0.5).

## The map Codex reconciles against

The independent BID authority map V26's fitted authority must land inside is now
the **3 hardened survivors (71 legs)**, machine-encoded with regime gating so no
>3c artifact can re-enter:

| cell | regime | P (Wilson lo) | p90 / max shortfall |
|---|---|---|---|
| ATP_CHALL le25 | 2-3c | .889 (.747) | 0.5 / 4 |
| ATP_MAIN 51_75 | 2-3c | .917 (.742) | 0.0 / 2 |
| WTA_MAIN ge76 | 2-3c | 1.000 (.741) | 0.0 / 0 |

Any cell × regime V26 authorizes outside these three — any ≤1c bid-anchored grant
(the fall-tail still forbids it), any >3c grant (`SPREAD_ARTIFACT_EXCLUDED`), or
either of the two error-bar failures (WTA_MAIN 51_75, WTA_MAIN le25) — is a
cross-seat finding to reconcile.

## Reading

The corrected map removes the artifact inheritance at the machine level (13 → 5),
and the error bars remove two more on thin-sample uncertainty (5 → 3). What
survives is small and specific: BID-anchored authority is defensible in exactly
three 2-3c cells / 71 legs, each with a Wilson-lower ≥ .74 and a bounded p90 loss.
Everything the point estimates suggested but the intervals cannot support is now
labelled, not granted.

## Artifacts

`ASYMMETRIC_AUTHORITY_HARDENED.json` (corrected map with `SPREAD_ARTIFACT_EXCLUDED`
flags, hardened map with Wilson/bootstrap/p90 per cell, and BID stats for every
populated cell × regime). Old `ASYMMETRIC_SPREAD_SUMMARY.json` carries the
`SUPERSEDED_BY` stamp.
