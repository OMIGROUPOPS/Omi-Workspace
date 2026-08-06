# V34 dual-side residency machine - canonical trading-phase scoring

V34's state machine is unchanged. Scoring is clipped per leg from the earlier of first two-sided book or first true exchange print through the hash-bound trading-phase boundary implied by that leg's THE_603_MAP true_close. Every non-null close is validated against the ordered exchange prints; null closes remain unavailable and use the sibling's game boundary only to clip their streams. Terminal settlement-collapse prints are excluded from decisions, fills, floors, close grades, frontier, and regret. The 234-event exact-bell subset remains timing metadata only.

- Canonical T1-joint comparison universe: 750.
- STRICT-LAW JOINT: 63; delta vs R3 68: -5; gap to named 603: 540; gap to T1 750: 687.
- CENSUS-PRICED JOINT: 89; delta vs R3 68: 21; gap to named 603: 514; gap to T1 750: 661.
- STRICT completed / under par / both-below / carried: 441 / 441 / 63 / 371.
- CENSUS completed / under par / both-below / carried: 481 / 481 / 89 / 386.
- ARNROM STRICT: 97; CENSUS: 97.
- Canonical close availability: 1606/1608; map mismatches: 0.

The prior settlement-basis V34 package is preserved as a stamped negative control and is not consumed by this score.
