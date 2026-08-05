# Window-1 V31 dip-pressure governor — 2026-08-05

V31 is measured and rejected. V29-R3 remains the operative baseline at JOINT
68. The V31 repair-with-earned-authority scored JOINT 67, so it may not be
promoted despite passing its implementation, conservation, and determinism
tests.

The organ binds the six causal EWMA bands at
`e64b0837e04e3ea7dd58fbbba907816b3fdbdcb2`: cross, lock, bid dominance,
ask dominance, ask staircase, and bid staircase, with a 120-second halflife.
The training target remains the frozen ten-minute deeper-dip target. Thresholds
and pressure-implied drop depths are learned only from chronologically prior
category decisions. The runtime decision contains no elapsed-time trigger and
re-evaluates on causal own-book receipts.

Authority requires at least 20 held-out HIGH calls and an absolute held-out
precision lift of at least five percentage points above the category base
rate. Only WTA_CHALL earned authority: 26 HIGH calls, 23.08% precision versus
16.25% base rate. ATP_CHALL, ATP_MAIN, and WTA_MAIN did not earn authority and
remain byte-identical to R3.

V31 changed 26 of 1,608 streams. Seven demotions found a deeper fill; nineteen
lost the completion because the deeper dip did not return. It gained zero
JOINT pairs and lost one. The full disposition is therefore 7
DEMOTED_THEN_DEEPER_FILL, 19 DEMOTED_THEN_LOST, and 1,582 UNTOUCHED.

ARNROM|ROM at epoch 1783896551 (the named 42-cent case) was LOW pressure.
ATP_CHALL had no earned authority, so the leg was not demoted and remained
credited at 42. This is a named regression result, not a forced fixture.

Two clean builds produced byte-identical payloads with SHA-256
`8a0ef9ab2a3718875a291059343a7ba0e2de2078588438256971869eb7dde55a`.
No holdout, live, runtime network, orders, positions, exits, settlement, DCA,
Window 2, deployment, audited-close policy input, future-floor policy input,
or wall-clock policy input occurred.

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/5db33ffdf26d22b5287825d0648d47205d1b9c13/.claude/window1_live_v4_replay/v31_dip_pressure_governor_20260805/REPORT.md

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/5db33ffdf26d22b5287825d0648d47205d1b9c13/.claude/window1_live_v4_replay/v31_dip_pressure_governor_20260805/VERDICT_RECEIPT.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/5db33ffdf26d22b5287825d0648d47205d1b9c13/.claude/window1_live_v4_replay/v31_dip_pressure_governor_20260805/SCORECARD.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/5db33ffdf26d22b5287825d0648d47205d1b9c13/.claude/window1_live_v4_replay/v31_dip_pressure_governor_20260805/GOVERNOR_AUTHORITY_FIT.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/5db33ffdf26d22b5287825d0648d47205d1b9c13/.claude/window1_live_v4_replay/v31_dip_pressure_governor_20260805/DEMOTE_RISK_RECEIPT.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/5db33ffdf26d22b5287825d0648d47205d1b9c13/.claude/window1_live_v4_replay/v31_dip_pressure_governor_20260805/ARNROM_ROM_REGRESSION_RECEIPT.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/5db33ffdf26d22b5287825d0648d47205d1b9c13/.claude/window1_live_v4_replay/v31_dip_pressure_governor_20260805/DECISION_TRACE_1608.json

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/5db33ffdf26d22b5287825d0648d47205d1b9c13/.claude/window1_live_v4_replay/v31_dip_pressure_governor_20260805/DETERMINISM_RECEIPT.json
