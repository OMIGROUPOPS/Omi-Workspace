# Window-1 ground-truth grading-only binding

Date: 2026-08-14

`W1_GROUND_TRUTH_TABLE` at
`c0056976c446afcb4d9603796a2e06c068ee94d6` is the sole authority for
floors, fill validity, offer denominators, and deltas. Its frozen SHA-256 is
`f7bc71d8e615859db272d841e125bc4836a685d82bb2d6769762c9bc19e56729`.
Twenty `UNKNOWN_BELL` games remain a named, non-gradeable class.

This binding is grading-only. V52h's historical replay windows and decision
stream are not rebound. The 30-game proof re-emits all 712,896 frozen receipt
rows by immutable Git-object reference with zero receipt-key, policy-field, or
decision-stream differences. Its grading denominator is 29 plus one
`UNKNOWN_BELL` event. The resulting four-state observation is 13
`COMPLETE_AT_DELTA`, 11 `PARTIAL_FOR_REASON`, five `NEITHER_FOR_REASON`, and
one `UNKNOWN_BELL`.

Two clean grading builds are byte-identical. No policy replay was invoked by
the adapter. No sealed, holdout, live, network-runtime, order, position, exit,
settlement, deployment, or DCA access occurred.

The prior mixed-window proof is blocked diagnostic evidence only. It showed
that rebinding the right edge before replay changes the current noncausal
stability onset. It is not a successful grading artifact and is not committed
as Part A.
