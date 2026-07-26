# Window-1 Range-Attack scoring package V2 PRE-RUN

This additions-only package corrects the four findings at
`3811a772aea381767a763af90320a1af91475816` without changing candidates, strategy, fill law,
metric law, D=804, or the passed strict-ask instrument.

## Frozen corrections

- Exact integer validation rejects truncation of quantity and cent prices.
- Runtime consumes 991 unique guarded fills: 501 macro-hold and 490
  macro-micro; 965 are print-backed and 26 strict-ask-backed.
- The three duplicate keys are resolved only by frozen policy interval and
  evidence identity during package construction. Runtime cannot read policy
  streams or raw interval receipts.
- The frozen source reproduces 272 latest-timestamp multi-receipt ties (one
  more same-price tie than the audit headline); 208 share one price and retain
  all supporting receipts. The 64 differing-price ties are unavailable because
  no authoritative exchange sequence survives normalization.
- Future audit authorization supplies the audit commit separately; the report
  at that exact commit binds package commit, execution ID, bundle, and command
  template without impossible self-reference.
- Committed text identities use canonical LF bytes, so LF and CRLF checkouts
  produce the same package.

All C/PC/S/IC and performance values remain null. No development scorer,
benchmark, holdout, live, or production surface was invoked.
