# The post-onset offer census — the bell's denominator [ANALYTICAL_ESTIMATE]

Analysis seat only. Read-only. All 804 dev games. Per leg: the **post-onset floor** = cheapest contract sold
at-or-after the leg's onset, onset by the **current interim method reproduced faithfully** from
`window1_v52_stability_onset.js` @ `98d07986` (60 s grid; candidate A = spread AND cross-leg mid-sum both
settle, ts = max of the two splits; candidate B = trailing-hour cadence rises; **selected = earliest valid**;
binding CODEX-INTERIM — the §8 PRIMED standard supersedes the binding, and both candidates are reported where
they differ). Old offer basis = PAR_SHEET @ `b7f12d6f` (711/93). Per-game rows and both-candidate floors:
`POST_ONSET_OFFER_CENSUS.json`.

## The three counts (+ two named gaps)

| class | games |
|---|--:|
| **OFFERED_POST_ONSET** (post-onset pair floor < 100) | **612** |
| **FORMATION_ONLY_OFFER** (the old 711-basis offer existed; post-onset sum ≥ 100 or a leg never sold post-onset) | **72** |
| NOT_OFFERED_POST_ONSET | 82 |
| NO_ONSET (≥1 leg never fired either candidate — 47 legs; named gap, not folded) | 36 |
| NO_TAPE (named gap) | 2 |
| **Σ** | **804** |

**The denominator every bell verdict is judged against: 612.** Against the old scoreboard: 711 offered →
**612 survive the onset cut; 72 of the old offers (10.1%) were formation mirages** — the discount existed
only in the chaos the gate now refuses to trade; 27 more old-offers sit inside the NO_ONSET/NO_TAPE gaps.

## Margin distribution of the offered 612 — thin offers are real, and named

p25 **2¢** · median **3¢** · p75 **7¢**.

| margin under 100 | games |
|---|--:|
| ≥ 3¢ | **384** |
| ≥ 5¢ | **236** |
| ≥ 10¢ | **90** |
| 1–2¢ (thin — real, named) | 228 |

## Category splits (offered / of)

| category | OFFERED_POST_ONSET | FORMATION_ONLY | NOT_OFFERED | NO_ONSET | share offered |
|---|--:|--:|--:|--:|--:|
| ATP_MAIN | 133/147 | 6 | 4 | 3 | **90%** |
| WTA_MAIN | 134/152 | 9 | 6 | 3 | **88%** |
| ATP_CHALL | 263/369 | 40 | 45 | 20 | 71% |
| WTA_CHALL | 82/136 | 17 | 27 | 10 | **60%** |

The mains keep their offers after waking; the challengers shed them — the same gradient as the zone table
(`35ac1f5b`) and the read-starvation mechanism (`2af60dfc`): thin tapes both blind the read *and* carry
formation-heavy offers.

## The A/B sensitivity — what the PRIMED ruling moves here

Where both candidates fire on both legs and disagree, **111 games flip offered-status between candidate A
and candidate B onsets.** The interim earliest-valid binding is load-bearing at the denominator level; under
the PRIMED standard those 111 (plus the 36 NO_ONSET) reclassify via traces, not a line.

## Conservation

804 = 612 + 72 + 82 + 36 + 2; margins n = 612; category cells sum to their classes; 47 no-onset legs named;
old basis 711 + 93 = 804 (side-by-side, not force-reconciled — the classes partition differently by
construction). Sources: fit-local tapes (804-game minute-grid pass) + prints (frozen spans), onset math
faithful to `98d07986` via prefix-sum SSE (identical arithmetic). ANALYTICAL_ESTIMATE.
