# Fresh holdout exam adapter: blocked before DEV inertness

Date: 2026-08-06

The frozen policy/build sources are byte-identical to V36 `bfde0d8`, V35
`0799fba`, and R3 `49f6501`. A binding-only adapter nevertheless cannot be
constructed from the supplied sealed inputs.

R3's exact entry point consumes frozen V29-R2 event, leg, trace, disposition,
and arm-receipt outputs. It does not consume raw tape or an external boundary
ledger. Generating those predecessor decisions for the sealed population
would reconstruct policy rather than rebind input.

Separately, all 342 sealed tape files share one BBO/depth schema ending in a
carried `last_trade` field. None contains exchange trade identity, aggressor
side, trade size, or exchange timestamp. The strict seller-aggressor fill law
therefore cannot be evaluated from the sealed tape package.

DEV inertness and Stage 3 were not started. Decision-trace comparisons,
scorecard comparisons, brain invocations, retries, and score rows are zero.
The standing one-run authorization remains unconsumed.

The eight external old-seal rewrites are self-consistent as an obsolete N=0
package and were preserved unstaged. Their output schema and default path
match `build_window1_fresh_holdout_seal_exam.js`; the exact command line of
the exited Node process was not captured. The controlling corrected N=171
declaration, its event list, and the exam list remain byte-identical at
SHA-256 `06ede0264a196bbebc005785c3ffdee5a840afe1a617f86f0354eedf65ac4313`.

Canonical package:
https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/4f4d546421043f187bc73e2d9ad1eca0b9cf7f36/.claude/window1_fresh_holdout_exam_adapter_gate_20260806/REPORT.md
