# Absorption audit and frozen residual test

Scope: bench only. No engine, conduct, face, library-span, or finalist-replay change.
Do not commit source rows, local training rows, models, or remote audit intervals.

## Completed run

The audit completed at nice 10 on droplet A (former PID 2842252). Its directory is
`/mnt/omi-trading-data-nyc3/library/absorption_audit_20260913/production`.
`RUN.exit` recorded code 0. All 6,482 parts were hash-verified. MAIN had 449 and
CHALL 763 independent games with measured refill; unexplained failures: zero.
The full remote receipt hash is recorded in AUDIT_RECEIPT.json.

No population fit is permitted until the entire audit completes, every part
hash verifies, no unexplained usable-interval reconciliation failure remains,
and both tours have at least 100 independent games with measured refill.
Accounting identities verify the arithmetic, not gross maker orders: this is
net displayed replenishment, with offsetting adds/cancels unidentifiable.

Only aggregate audit coverage, reason counts, rules, and hashes may be returned.
No new audit interval, source print, private example, or per-leg dataset leaves
the droplet. Local modeling uses the already-present gate proofs and witnesses.
The API label remains authoritative; arithmetic aggressor estimates never fill
missing flow. Unknown boundary ordering, off-screen consumed levels, and missing
labels are unobserved, not measured zero. Zero execution denominator is separate.

## Frozen inputs and contract

- `CONTRACT.json`: pre-fit method and promotion bars; do not overwrite.
- `RESERVATION.json`: 140 MAIN / 344 CHALL games, selected using formation
  metadata. Label: **historically inspected — not fresh**.
- `INPUTS.json`: pre-fit source and unchanged-engine pins.
- Fresh confirmation is deferred to LIVE_PAPER after DESK activation.
- Development skips reserved JSON payloads before decoding. Confirmation models,
  scales, choices, and the FIRST member universe are frozen before opening the
  reserved slice. Both tours finish development before the confirmation phase.

## Code and results

- `absorption_audit.py`: all consumed levels, including the prior best quote.
- `absorption_residual_data.py`: selected-source adapter, exact cached FIRST
  atlas projection, strict-later positive-size targets, causal book features.
- `absorption_residual_model.py`: equal-game ridge residual model, translated
  FIRST distribution, hierarchical date/game uncertainty and promotion bar.
- `absorption_residual_run.py`: separate development/confirmation phases.
- `absorption_residual_pipeline.py`: audit verification and conditional launch;
  no scheduler or automatic commit/push.
- `resume_absorption_confirmation.py`: execution-only recovery from an empty
  atlas game. Verifies that the runner differs only by an empty-input guard;
  reuses the frozen models and completed checkpoints without reopening their
  source outcomes. No fitting or model selection.
- `publish_absorption_residual.py`: verifies completion and emits aggregates,
  never training rows, model pickles, or per-receipt scores.

The historical confirmation phase finished all 140 MAIN and 344 CHALL games;
two CHALL games had no atlas receipts and remain in the eligible denominator.
The initial attempt completed MAIN and 109 CHALL games before an empty NumPy
mask stopped it. The continuation scored only the remaining 235 CHALL games.
EXECUTION_RESUME.json preserves both code bindings and model hashes. This was
one interrupted final phase, not a second confirmation experiment.

Neither primary correction passed. Earlier-only validation selected zero for
both BASE and BOOK in every outer/confirmation fit. The one nonzero single-block
diagnostic (CHALL favourite refill) did not pass either phase. See REPORT.md,
PRIMARY_SUMMARY.json, and the full 36 contrasts per phase in the result JSONs.

Important: full-span measured coverage is not measured coverage at the model's
gates. Only 57 MAIN / 43 CHALL development games, and 29 MAIN / 32 CHALL historical
confirmation games, had measured refill at a gate. This is not a powered rejection
of absorption itself. Fresh confirmation remains deferred to LIVE_PAPER.

The primary comparison is FIRST, baseline-only correction, and baseline plus all
book blocks. Six single-block additions are diagnostics with the same simultaneous
multiple-comparison adjustment, not a post-confirmation selection procedure.

No inner validation means zero correction, explicitly reported. No available
book readings means BASE fallback, explicitly counted. Gate coverage is reported
separately from all-interval audit coverage; the latter cannot be claimed as
feature availability at every gate. Native prior snapshots at a gate's own second
are unavailable until that second completes. An unavailable gate proof is not
replaced by an invented or future interval.

## Execution

From the worktree's `arb-executor/analysis`, using the bundled Python runtime:

```powershell
python -B -m unittest test_absorption_audit test_absorption_residual_model test_absorption_residual_data test_absorption_residual_run
python -B absorption_residual_pipeline.py --root C:\Users\omigr\omi-w1-face --out C:\tmp\absorption_residual_20260913 --host root@104.131.191.95
```

The pipeline may wait for the existing remote audit. It does not relaunch or alter
that audit. If the audit bar fails it stops without fitting. It writes only private
local outputs until review. Final result files must be reviewed before copying
aggregate reports into this directory and committing the ordered deliverable.

No quiet completion automation has been created for this order without approval.
