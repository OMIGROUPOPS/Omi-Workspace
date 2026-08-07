# Sealed-171 exam unblock and consumed one-run failure

The public-print re-pull passed for all 342 legs: 1,062,870 canonical positive-size trades, 1,231 fully terminated pages, and zero failed tickers. The independent nightly-method sample matched 155,463 exchange trades to 155,463 captured prints across 20 events with zero identity, price, size, or taker-side mismatch.

The adapter reproduced both frozen development packages byte-for-byte on all 804 events before the exam: V36 inspected 3,631,920 decisions and V35 inspected 3,610,317 decisions. Strict/census decision traces, full scorecards, and both frontiers matched for both brains. Policy mutations and sealed invocations at that gate were zero.

The authorized sealed process was invoked once. It evaluated all 171 V36 events, then failed before V35 and before any score output while serializing the full V36 decision stream: `RangeError: Invalid string length` at `gzipRows` / `Array.join`. The authorization is consumed. There was no retry, repair, completed scorecard, frontier, regret output, or performance conclusion.

R3 was excluded and not invoked, pursuant to transitive-input blocker `4f4d546421043f187bc73e2d9ad1eca0b9cf7f36`.

The eight externally rewritten files under `.claude/window1_fresh_holdout_seal_20260806/` remain preserved unstaged and unused. Their controlling reconciliation is `.claude/window1_fresh_holdout_exam_adapter_gate_20260806/SEAL_REWRITE_RECONCILIATION.json`: the high-confidence writer is the obsolete seal builder, which rewrote an N=0 package at a common timestamp; exact exited command-line attribution was not recoverable. The corrected 171-event declaration and list remain controlling.

No live engine, account, order, position, or trading surface was accessed. No policy was changed. A new authorization and an independently audited streaming serializer repair are required before any further sealed execution.
