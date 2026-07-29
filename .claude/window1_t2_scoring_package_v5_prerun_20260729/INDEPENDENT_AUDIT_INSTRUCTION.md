# Independent Window-1 T2 scoring-package V5 audit

Do not authorize or execute V5.

1. Before opening expected V5 summaries, independently inspect the parent V4
   test blob and establish its three real-development `score_t2_event`
   attempts, one completed in-memory event row, zero completed candidates,
   zero persisted result rows, and zero aggregate/frontier/regret output.
2. Freeze that independent receipt, then compare it to
   `V4_CONSTRUCTION_TEST_ACTIVITY_CORRECTION.json`. Any mismatch is BLOCK;
   no post-hoc reconciliation is allowed.
3. Inspect the corrected V4 test source independently. Enumerate every direct
   scorer call. Prove all event, boundary, fill, and reference inputs are
   synthetic and a frozen-development-event-ID guard runs before scorer import.
4. Instrument the corrected V4 and V5 test runs. Require zero development
   scorer attempts, exactly three guarded synthetic scorer calls, 6,432 real
   prepared calls inspected without scoring, and no V5 results directory.
5. Recompute the sole inherited-file old/new blobs and hashes. Prove every V4
   package artifact and runtime source is byte-identical and V5 changes no
   scoring semantic.
6. Recompute all manifests, bundle identity, null scans, authorization/ID
   rejection, complete test collection with zero omissions/deselections, and
   both clean deterministic builds.

A PASS certifies a score-free V5 PRE-RUN only. It is not authorization.
