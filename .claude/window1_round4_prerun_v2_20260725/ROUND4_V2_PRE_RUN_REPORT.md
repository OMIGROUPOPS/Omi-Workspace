# Window-1 Round-4 PRE-RUN V2

This additions-only V2 supersedes `4f65344672430adc51fe0a5a7e8c9279b2b354ed` for future execution binding and
implements only Item 5 amendment `abe543e33bf40cf6cca14e046c40904d2de5e878` plus the original audit's stale
100-field removal.

- D=804 and actionable=804 for both unchanged candidate IDs.
- 1,598 candidate-event streams are byte-identical to V1.
- Exactly ten streams change: five named events times two candidates.
- Every changed stream has two causal-role NO_CALLs, two market-evidence
  NO_CALLs, zero placements, a non-censored event terminal, and continued D
  membership.
- No price is fabricated and no executed print substitutes for BBO authority.
- Candidate order-distinctness remains 707 real events.
- Both inert 100-cent fields are absent; S and IC remain diagnostics only.
- Primary cumulative print-volume fills and strict `b1+b2+fee<0` headroom are
  unchanged; the receipt scan has zero arithmetic violations.
- All C/PC/S/IC fields remain null. No scorer, benchmark, tuning, ranking,
  holdout, live, or production action occurred.

The V2 execution inventory contains no execution ID or command and authorizes
no benchmark.
