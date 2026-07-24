# AIM_V2 contamination receipt for the corrected Window-1 replay

Verdict: the pinned shape prior is excluded.

The prior named by the narrow candidate specification is
`arb-executor/data/shape_corpus/aim_v2_operational_LATCHCAL.json`, SHA-256
`6183ddec56eaab2ad48432aa7c802ea6265e608fa26cdd960aa1dde866824356`.
It first entered Git history in commit
`c8c91b3386d1ab36543f73317326d4a76bfe86db` on 2026-07-06. That commit
added the table together with `AIM_V2_OPERATIONAL_REPORT.md`, and its subject
identifies the table as “AIM_V2 OPERATIONAL … LATCHCAL.” `git log --follow`
finds no earlier version or independent authorization for these bytes.

The later candidate declaration's `shape_prior_authority_commit` points to
that same AIM_V2 commit. It therefore proves AIM_V2 lineage, not independent
lineage. The corrected replay does not consume the table, its SHA, or the
derived `shape_aim50_cents`, `shape_dip50_cents`, or shape-offset decision
fields.

The resulting named feature gap is the cell-conditioned resting aim and
shape-cell placement offset. The separately ratified
`.claude/seqfloor_20260708/recut_cells.json` remains eligible only for the
post-fill dynamic-floor and dip/catch reporting measures. It is not used to
create, alter, or relabel an entry policy.
