# THE PAIR-POSITION / FLOOR-TIMING CENSUS — WHEN by ROLE, dev-804 [ANALYTICAL_ESTIMATE]

Analysis seat only. Read-only. **Role tables are UNVALIDATED-CANDIDATE** (journey-derived, prior-not-gate;
no decision-input claims). No mechanism proposals. Full rows: `PAIR_POSITION_FLOOR_TIMING_CENSUS.csv`
(1,602 legs) + `.json`.

**Pins.** Journeys and pair families: `ec88f8e3` `MACRO_JOURNEY_TABLE.json` — the pair-class rule
re-implemented here **reproduces its published split exactly (MIRRORED 547 / FLAT_BOTH 196 /
OPPOSED_UNBALANCED 37 / DECOUPLED_SAME_DIRECTION 21)**. Machine actuals: dev-804 @ `4716657a`
(`MARKET_EVENT_LEDGER_804` fills/credits, `POST_ONSET_OFFER_CAPTURE_LEDGER_804` canonical onsets,
`FIRST_POST_LEDGER` 1,173 first posts with read-at-post). Tape: `fit-local/prints.jsonl`. Floor = the leg's
cheapest post-onset in-window true print; floor position = (first floor print − onset) / (w1_right − onset).

## ① The standing families, roles tagged [CANDIDATE]

547 MIRRORED pairs → 1,094 role legs (net > 0 → **CLIMBER**, net < 0 → **FALLER**); 1,059 role legs carry a
measurable floor (35 lack post-onset prints or onset). Mirrored exemplars (largest amplitude):
**26JUL20GALARN (±59¢)** · 26JUL12PRIBAL (±49.5¢) · 26JUL12MORNEP (±49.5¢).

## ② WHEN the floor comes, by role — measured, not assumed

Floor position as fraction of the post-onset span (0 = onset, 1 = bell edge):

| cell | CLIMBER n · p25 / med / p75 | FALLER n · p25 / med / p75 |
|---|---|---|
| **ALL** | **532 · 0.07 / 0.30 / 0.69** | **527 · 0.27 / 0.65 / 0.93** |
| ATP_CHALL \| 26_50 | 188 · 0.13 / 0.43 / 0.77 | 195 · 0.33 / 0.74 / 0.95 |
| ATP_MAIN \| 26_50 | 124 · 0.05 / 0.20 / 0.56 | 124 · 0.21 / 0.58 / 0.93 |
| WTA_MAIN \| 51_75 | 111 · 0.04 / 0.18 / 0.56 | 113 · 0.24 / 0.59 / 0.86 |
| WTA_CHALL \| 26_50 | 66 · 0.09 / 0.34 / 0.66 | 62 · 0.34 / 0.69 / 0.92 |
| ATP_CHALL \| 51_75 | 18 · 0.05 / 0.25 / 0.65 | 10 · 0.22 / 0.52 / 0.61 |

**The expected result holds, measured: the climber's floor comes early (median 0.30 of the span) and the
faller's late (median 0.65), in every cell with n ≥ 10.** (The one inversion is WTA_CHALL|51_75 at n=6/7 —
too thin to read.) **The exceptions are counted and large: 193/532 climbers (36%) floor in the LATE half,
and 208/527 fallers (39%) floor in the EARLY half** — the pattern is a real median separation, not a law.
Exception exemplars: climbers flooring at the very edge — KHOZHA|KHO, CASGHI|GHI, IMATRA|IMA (pos 1.00);
fallers flooring at onset — MARSKA|SKA, OLIZIE|ZIE (pos 0.00), SINMAT|SIN (0.001).

## ③ The machine against the clock — both errors, in cents and minutes

**Bought-a-faller-early (the GUEGOM error): 186 credited faller legs filled before their floor print** —
leg-grain depth **1,741¢** (median 4¢, p75 10¢; median 180 minutes before the floor came). By category:
ATP_MAIN 63 · ATP_CHALL 60 · WTA_MAIN 52 · WTA_CHALL 11. Exemplars: **26JUL12KULZAA|ZAA (65¢ deep, 9.7 h
early)** · 26JUL20GALARN|GAL (59¢, 1.5 h) · 26JUL12HECISO|HEC (58¢, 38 min) — GUEGOM|GUE itself is #4
(57¢, 54 min).

**Missed-a-climber-by-waiting (the inverse error): of 492 measurable mirrored pairs, waiting until the
faller's floor moment would have cost > 0¢ on the climber in 257 (52%)** — total **2,523¢** (median 4¢, p75
8¢; median floor-to-floor gap 5.4 h), plus **27 climbers with no print at all after the faller's floor**
(unbuyable by then, cost unmeasurable, counted not priced). Exemplars: 26JUL12BROGIU|BRO (83¢ climb-away) ·
26JUL12MICKUL|MIC (81¢) · 26JUL12KULZAA|KUL (78¢). **Stated plainly: at leg grain the inverse error is
bigger than the GUEGOM error (2,523¢ > 1,741¢), and half of patience's wins are the other half's losses —
neither "buy early" nor "wait for the faller" dominates at census grain.** (The big-cents tops of both
tables are the violent-collapse games of `3f4b0046` — the two errors are the two sides of the same
collapses.)

## ④ Readability at the posting moment — did we understand the position before posting?

At each leg's actual first-post receipt, the machine's own read (RISING/FALLING, from
`FIRST_POST_LEDGER.license.read.state`) vs the leg's eventual journey role:

- **Leg grain: 532/838 = 63.5%** of mirrored-leg first posts carried a read matching the eventual role.
- **Pair grain (both legs posted, 405 mirrored pairs): both reads matched roles in 210/405 = 51.9%.**
  Read-pair shapes at post: coherent mirror (one RISING one FALLING) 312 (77%) — of which the orientation
  was RIGHT 210 and fully INVERTED **102 (25% of pairs: read the climber as the faller and vice versa)**;
  FALLING+FALLING 66; RISING+RISING 27. Inverted exemplars: **26JUL20GALARN (±59¢: read FALLING on the
  climber ARN, RISING on the collapsing faller GAL)** · 26JUL12GURDAL (±49¢) · 26JUL12ARIZHA (±49¢).
- **By time-into-window (quarters):** Q1 65% · Q2 71% · **Q3 61% · Q4 59%** — role-readability does NOT
  improve with a fuller window; late posts read the roles *worse* (reads weight the recent tape; the
  journey's role is an open→edge fact). Stated as measured, no mechanism offered.
- By cell (n ≥ 20): WTA_MAIN|51_75 70% · WTA_CHALL|26_50 67% · ATP_MAIN|26_50 62% · ATP_CHALL|26_50 61% ·
  ATP_CHALL|51_75 52%.

Grain caveat, stated: each leg's read is taken at its own posting receipt (the sibling's read at that exact
receipt is not exported in the dev-804 first-post ledger); the pair judgment joins the two legs' own-post
moments.

## Conservation

1,602 journey legs → 801 pairs classed (547+196+37+21 exact vs `ec88f8e3`); 1,094 mirrored role legs, 1,059
with floors (35 named-absent in the CSV); machine: 1,173 first posts, 838 on mirrored role legs, 405
mirrored pairs with both legs posted (210+195); faller-early 186 rows and climber-wait 257+27 rows
enumerated in the JSON; the ② table's cells sum to their categories. Role tables CANDIDATE; no re-scoring;
no mechanism proposals — the operator rules the consequence. ANALYTICAL_ESTIMATE.
