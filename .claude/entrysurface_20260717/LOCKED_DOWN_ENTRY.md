# LOCKED_DOWN — THE ENTRY SURFACE SEAL (Stage 5, 2026-07-18)

The June ceremony, entry-side. Every input hash, every solve stage, the
drill campaign cited. The sealed object consults ONLY its survivors;
FAILED-HOLDOUT and THIN rows are present and silent; the violent-faller
REFUSE is law.

## The sealed object
- `state/entry_tables_sealed_v1.json`
  sha256 `3e01b92eadb03a87b001f1f7b096961aab0c47fbacfb39a7cdf633998bade56f`
- **SEALED 4 · REFUSE 5 · FAILED-HOLDOUT/THIN 27** (of 36 bands)
- Survivors + receipts:
  - WTA_CHALL-B3 flat, depth 11¢ — replay-frame holdout 7/36 fills CI-pass, ROC +0.019
  - ATP_MAIN-B2 faller, depth 25¢ — reach-frame holdout realized 0.30 vs pred 0.24, ROC 0.218
  - WTA_CHALL-B1 dog-flat/faller, depth 12¢ — reach-frame holdout 0.18 vs 0.16, ROC 0.252
  - ATP_MAIN-B8 riser park, depth 1¢ — holdout 4/6 fills, ROC +0.042 (park-class, n thin, labeled)

## Input lineage (hashes at seal)
- band_map_v1.json        `caf255a283bbb32f1d9bd2edd5f4d898d5f50fc8e67d5f9a076579b695a9e68c` (Stage 1, C50 d3ca814f)
- drift_surfaces_v1.json  `aeac847d26c1421c21be67d19ce4992a69f90840ae20443d4a8aaa31da8201a6` (Stage 2 P1)
- divot_tables_v1.json    `89c514ec35673de8f552b2b66b9ceafb8181b9c8f6c00b1679899a3a2a82ac06` (P3, C50 59dc1eea)
- entry_tables_v1.json    `ad1642be8c0f461e199a78af74455c53c802454eac2a1fee4715674b36da26b9` (Stage 3, C50 9cdc621d)
- entry_tables_v2.json    `bd6bc5fb80da73ef0a6df499e1d0fe0f1b5617ef62997247f144b964d2803fe5` (Stage 4 drill output)
- Drill campaign: 10 iterations, CONVERGED at train/holdout gap +0.0194 —
  memorization CAUGHT by the meter; 10 CI-failures named; the campaign is
  the reason 27 bands are silent. `.claude/entrysurface_20260717/LOOP_CAMPAIGN.md`
- Spectrum lineage: range_spectrum_v1.jsonl (12,170 legs, honest clocks,
  Phase A corrected table) — upstream C50s on the ledger.

## The wire (WHEN-FLAT)
- `entry_table_prior_enabled: true` (config); consult site =
  `_cohort_read` fallback — fires ONLY where live cohort n < 30 and no
  labeled borrow exists; returns `{"table": true, ...}` — TABLE-LABELED,
  never silent; `cohort_aim`/dossier logs carry `SEALED-TABLE:<band>` or
  `REFUSE:<band>` as the cell name.
- Live-outranks-table law: rich cohort cells short-circuit before the
  table is ever read (order of returns in `_cohort_read`).

## Countersign
- Seat: CC (Fable 5), Stage 5 C50.
- The operator's read of this document IS the countersign line; objections
  reopen the seal at Stage 6's checkpoint, nothing re-fits silently.


## AMENDMENT — 4b RE-FRAME AND RE-DRILL (2026-07-18, same ceremony, new hash)

The re-framed drill (each strategy in its OWN frame: all-window divots,
conception casts, touch parks; LOOP2_CAMPAIGN.md) returned the harsher
truth: **all ten 4a failures are REAL** (every one still fails own-frame)
and **both replay-frame survivors DEMOTE** — ATP_MAIN-B8 (park fills 9/10,
ROC −0.025: fills into losers on the close mark) and WTA_CHALL-B3
(drill-drifted to 1¢, 34/45 fills, ROC −0.049). The seal SHRINKS:

- `state/entry_tables_sealed_v1.json` (amended)
  sha256 `c0c29e54792e2f49cad6e96297367b4ada80051cde464a8f3dddb748ae1ce8e7`
- **SEALED 2** (ATP_MAIN-B2 cast 25¢ · WTA_CHALL-B1 cast 12¢ — reach-frame
  receipts; own-frame holdout THIN for both, both receipts shown) ·
  REFUSE 5 · silent 29.
- New lineage: entry_tables_v3.json (4b drill output)
  sha256 recorded at the amendment commit; LOOP2_CAMPAIGN.md +
  REPLAY2_DAY.md cited.
- Named caveat on the flats' CI test: the catch tables predict a divot
  RATE per window; a single resting bid fills once — the CI compares a
  rate to a proportion (units-harsh). The verdict does NOT rest on it:
  the flats' own-frame holdout ROC ≈ 0 or negative is the decider.
- The subtractive direction is noted: this amendment only SILENCES rows
  (fewer table consults live); no code changed; the wire's law
  (live-outranks-table, labeled, refuse-holds) is untouched.
