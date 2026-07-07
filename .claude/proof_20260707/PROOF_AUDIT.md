# OUTCOME PROOF (C46, two-lane) — C47-ENFORCE post-boot book audit

**Candidate SHA: `1c04f1d1`** (v1.1: conception_on_owned requires a resting buy; supersedes `e156a071`) (post-boot book audit, assert-and-halt: gate-banked snapshot diff, five per-leg assertions, conception halt, jsonl-verified).
Replay: deterministic, against the prior slate's banked exchange snapshots (the 09:38 ET pre-containment book — the exact book every overnight boot woke into — and the bleed-attribution fills tape). Producer: `arb-executor/analysis/forensic_20260707/proof_audit_replay.py` (committed at the candidate SHA).

## Verdict

- **LANE 1 (mechanism, luck-free, deterministic): the audit CONVICTS the overnight book and would have halted the storm at 01:12 ET.** Replaying the audit's exact assertions on the 09:38 snapshot: **FAIL with 48 failures** (10 buy-stacks, 12 exit-qty mismatches, 12 no-exit legs, 14 conception-on-owned under the v1.1 bq>0 refinement). Every overnight boot (01:07/02:07/02:34) woke into this book — the first boot's audit fails within 5 min, conceptions halt, and the layering stops at layer one. Construction impact: **upper-estimate 92 tickers / 509.7 surplus shares / $229.35 committed** during the 02:34-boot window alone could not have been conceived under an armed halt (VANBOO's `159fb665`, placed 02:34:19, is the named exhibit). Exits keep working throughout — the halt is one-sided by design; no legitimate first-lot conception is blocked when the book is clean (audit passes → no behavior change; the current post-containment book is the PASS case the deploy verifies live).
- **LANE 2 (settlement P&L, secondary): flagged LUCK-POLLUTED.** The prevented conceptions overlap the 07-07 class-(a) realized −$37.76; no settlement claim is the verdict — Lane 1's deterministic FAIL is.

## Replay table (assertions on the 09:38 pre-containment book)

| assertion | failures | exhibits |
|---|---|---|
| buy_stack | 10 | HOLSCH-SCH, ILARYB-ILA, JUNMOR-MOR, BOUMOC-MOC, CIASNI-SNI, OGUJAS-OGU |
| exit_qty_mismatch | 12 | BARZIN-BAR, GLIYUN-GLI, GLIYUN-YUN, MARBER-MAR, MARCRE-CRE, ECHADD-ADD |
| no_exit (hold-rule not distinguishable in the banked snapshot — stated; live audit exempts strategy=="hold" and flags exit_unpostable_itm) | 12 | BARSIM-BAR, BASGAU-GAU, PLAMAR-MAR, LORZAR-LOR, URSPOU-POU, GUESAN-SAN |
| conception_on_owned (bq>0, v1.1) | 14 | HOLSCH-SCH, ILARYB-ILA, JUNMOR-MOR, BASGAU-GAU, MARCRE-CRE, PLAMAR-MAR |

**VERDICT: FAIL (48) → conceptions halt, alert artifact committed+pushed, halt clears only on a passing re-audit.**
