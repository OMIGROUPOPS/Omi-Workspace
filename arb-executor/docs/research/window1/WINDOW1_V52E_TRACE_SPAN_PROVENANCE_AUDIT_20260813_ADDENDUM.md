# V52e trace-span provenance audit

Date: 2026-08-13

Controlling V52e: `b09aa22b301205d5d44d683497cf3edc5b177cf8`

Cited SHEVAN closeout: `d9d9a4e3c2615e76276761d7bed8ae92928091f4`

## Ruling

The V52e runner and its materialized input are full-span for all 60 legs in
the frozen 30-game cohort. The apparent trace truncation is export-only. The
file named `V52E_FULL_DECISION_TRACE_30_GAMES` is a stream of entry decision
evaluations, not a stream of every input receipt consumed by the runner.

The replay loop iterates every bounded BOOK and PRINT receipt. A credited leg
continues after the receipt has been consumed without emitting another entry
decision, and PRINT receipts update evidence or credit the order before the
book-decision export site. Therefore a decision trace may end long before the
edge without either the runner or the input ending there.

## Census

- Games: 30.
- Legs: 60.
- Runner FULL_SPAN: 60.
- Runner TRUNCATED: 0.
- Decision exports with an apparent positive gap: 44.
- Credited legs: 41.
- Median apparent export gap: 4,497 seconds.
- P75 / P90 / maximum: 17,754 / 34,458.836 / 73,936.677 seconds.
- Materialization shorter than a usable raw full-depth source: 0. The raw WS
  coverage ledger marks zero of these 60 legs as having a sequence-valid full
  ladder; it is context, not a substitute materialization.

The corrected receipt-span export records, per leg, the final decision
receipt, terminal credit, final materialized BOOK/PRINT receipt consumed, and
the frozen window edge. The original decision trace remains untouched.

## SHEVAN correction

SHEVAN was not holding two unresolved entry rests after the apparent trace
end. Frozen V52e outcomes and private print receipts establish:

- VAN credited its 58-cent rest at T+45,540.556 seconds (T+759.009 minutes).
- SHE credited its 34-cent rest at T+45,677.582 seconds (T+761.293 minutes).

Consequently neither rest was standing at the later T+772-minute VAN
49-cent cluster or the T+792-minute SHE collapse. Those are post-entry market
events. Part B of the cited closeout treated cessation of entry-decision
exports as cessation of runner input consumption; this audit supersedes that
conditional-standing interpretation.

## Integrity and scope

All five V52/V52b/V52c/V52d/V52e policy files are byte-identical to the
controlling V52e commit. No policy was invoked, no replay was rerun, and no
score artifact changed. The observation remains 17 completed pairs out of 30.
Two clean receipt builds are byte-identical. The inherited V52e suites and the
new provenance suite pass 108 assertions with zero omissions or deselections.

No full-804 exam, deployment, live access, holdout access, network operation,
order action, position action, or private-input write occurred. The full-804
exam remains held pending operator review.

Canonical package:
`.claude/window1_live_v4_replay/v52e_trace_span_provenance_audit_20260813/`.
