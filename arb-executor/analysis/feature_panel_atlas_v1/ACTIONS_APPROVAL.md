# Protected Actions proof — prepared, NOT enabled

The draft is outside `.github/workflows`. No workflow, secret, environment,
Spaces release, runner or upload has been created. It fails closed even if copied
into the active workflow directory before approval is finished.

## Required approval

- Approve exact input release hashes and the Spaces prefix. Earlier source
  extraction approval does not authorize uploading private inputs elsewhere.
- Configure `feature-panel-approved` with required reviewers, prevent self
  approval, and restrict deployments to the approved branch/commit. Use only a
  read-only release-prefix-scoped Spaces credential; no fork or PR trigger.
- Pin checkout action SHA, Python, NumPy and numerical environment. Run a
  Windows/Linux byte-parity smoke test, not a substitute for full determinism.
- Review the proof execution/reducer adapter before removing the hard stop.
  This draft prepares the matrix/security contract, not an enabled execution
  path. Frozen fitted models must retain identical earlier-only cohorts.
- Check actual concurrency, artifact quota and Spaces egress. Free standard
  runner minutes do not authorize billable storage or egress.

## Input allowlist

`feature_panel_actions_plan.INPUT_NAMES` is exhaustive. Every entry requires
exact bytes/SHA256 in a release manifest: tick library/receipt, print-count
sidecar/receipt, derived feature extract and positive-print witnesses,
supplemental availability and their receipts, and the odds archive *receipt*.

Private positive-print witnesses stay private. No SQLite/parquet store, raw
Spaces objects, named-check tapes, tune sample or 804 data is allowed. Every
input row must belong to the pinned library; event-name dates July 11–21 and
TUNE_SAMPLE-tagged rows fail closed. Credentials never enter a repository,
artifact, log, cache or command-line argument. No wildcard artifact upload.
The release directory must contain exactly the allowlisted files. Sparse
checkout excludes named-check face/tape directories; the final execution code
manifest also needs review before enabling the draft.

## Sharding and proof

Category × two passes × five query shards is at most 20 jobs. Categories without
advancing variants produce no jobs. Every shard gets the complete member
library. Schedule by recorded receipt cost, ties by canonical identity; never
split a query. Reduce in original month/stream/query/receipt order, not by
summing floating-point shard aggregates.

June cannot select variants; its models/scales/member library remain frozen.
FIRST and finalists receive full-universe/full-receipt proof. Both complete
outputs must match. Report stalled/missing fits; never invent coefficients.

## Artifact policy

Only names in `PUBLIC_ARTIFACTS` may be public: reviewed aggregate summaries,
optimizer outcomes, receipts, determinism and shard counts. Private journals,
checkpoints, per-receipt diagnostics, feature arrays, fitted-sample caches, raw
witnesses and source objects must never enter public artifacts or Actions
caches. Reduction transfers require separately approved encrypted storage and
hashes. Keep public artifacts within the verified account quota and use short
retention. The draft deliberately performs no upload.
