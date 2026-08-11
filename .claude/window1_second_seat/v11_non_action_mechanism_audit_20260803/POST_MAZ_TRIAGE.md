# Post-MAZ triage — machine records only [ANALYTICAL_ESTIMATE]

Analysis seat only. Read-only. No reconstructions — ledger terminals, raw prints, raw tapes. Machine artifact:
`…/POST_MAZ_TRIAGE.json`.

## ① Edge-clipped census — the fill print after our edge

Population: every dev-804 and sealed-238 leg terminating `REST_UNFILLED_AT_HARD_PREBELL_EDGE` plus every
one-sided pair's unfilled leg = **568 legs** (dev 466 / sealed 102). Measured: post-edge prints at-or-below the
terminal rest price, from full-life fit-local prints (dev) and the holdout/exam repull (sealed — coverage past
the edge is partial there; sealed counts are lower bounds).

| | value |
|---|--:|
| legs with ≥1 post-edge sub-rest print | **461 / 568 (81.2%)** |
| total lots in those prints | 119,420,995 |
| minutes-past-edge (first qualifying print) | p25 **10.8** · median **18.1** · p75 36.1 · max 2,939.9 |
| by corpus | dev 374 · sealed 87 |

By bell class (with / of):

| bell | share |
|---|--:|
| exact | **113/130 (86.9%)** |
| live_by_only | 241/289 (83.4%) |
| schedule_only | 87/119 (73.1%) |
| clean_interval | 12/16 |
| contradictory | 8/14 |

By category: ATP_CHALL 275/319 · ATP_MAIN 50/65 · WTA_CHALL 76/108 · WTA_MAIN 60/76.

**The asked question — does the class concentrate in schedule_only? NO.** The share is uniform-to-higher in
**exact**-bell events (86.9%) than schedule_only (73.1%). Count observation, flagged without interpretation:
post-edge prints after an *exact* bell are post-bell prices by construction; the schedule_only 87 are the only
subset where an inferred boundary could have clipped genuinely pre-match flow. Counts and distribution only, as
ordered.

## ② Dipless-43 quarantine scope — 43/43 QUARANTINED, and why no per-leg clearance is honest

The independent copied-terminal-snapshot signature tested (terminal identical-book run > 1 h crossing or
postdating the edge) **fires on ZERO of the 43 — including MAZ itself**. It is therefore **not the defect's
fingerprint**, and it cannot clear the other 42. What the 43 share is the thing that matters: **every row was
produced by one reconstruction code path** (`dipless43.py` — same tape loader, same span logic) — the path the
standing forensic convicted on MAZ. Exposure is uniform; per-leg discrimination is not available from machine
records.

**Stamp: 43/43 QUARANTINED** — MAZSPI·MAZ by the standing forensic; the other 42 by shared reconstruction code
path, one line each in the JSON rows. `THE_DIPLESS_43_RAW` (aa1cc301/9ff18c8c) conclusions should be treated as
quarantined pending the forensic's specific mechanism being re-run against the corrected reconstruction.

## ③ Anatomy map S18 — amended and recommitted

S18's defect entry no longer cites FANBIG as a candidate crediting defect. Amended to: *"Defect: none standing —
the FANBIG through-bid item (`653b7f13`) was MOOTED by the post-MAZ forensic (an evidence-join error in the
reconstruction, not a crediting defect); no open S18 defect."* Applied to `THE_ANATOMY_MAP_DIALS.md` and `.json`
in this commit.

## Conservation

① 568 legs = 461 with post-edge sub-rest print + 107 without; bell splits sum 568; category splits sum 568.
② 43 rows, one stamp each (43 QUARANTINED + 0 CLEAN), method note in JSON. ③ one amendment, both files.
Sources: V47 fb74c8b8 + sealed 2bae8931 ledgers, fit-local/holdout/exam prints, fit-local/exam/holdout tapes.
