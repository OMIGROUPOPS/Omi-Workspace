# Sealed-exam streaming serializer repair audit

The prior exam at `a746d17582284736f9b3a9e6c8db2bf61e9204e1` failed after all 171 V36 policy evaluations because `gzipRows` attempted to join the entire full decision trace into one JavaScript string.

The repair is serialization-only. `FULL_DECISION_TRACE.jsonl.gz` now uses an async JSONL row generator piped through deterministic gzip to a file stream, matching the established V32/V35/V36 builder pattern. The same immutable decision array is streamed twice and the two gzip files must match by SHA-256 and byte size. V36 and V35 builder and policy files were not modified.

The focused synthetic audit streamed 1,025 one-megabyte rows: 1,074,817,990 uncompressed bytes. Streaming decompression reproduced every byte, the compressed artifact was 1,069,588 bytes, and peak RSS delta was 109,858,816 bytes.

The strengthened DEV-804 audit passed for both brains. V36 matched its frozen compact traces, scorecard, frontiers, and all 3,631,920 ordered full-trace rows (8,636,386,885 JSONL bytes; SHA-256 `353a9d2a074ac0040ed3c69bf87be41c4cbbc0c8b2355b6d2041d897f87815b5`). V35 matched the same surfaces and all 3,610,317 rows (6,706,475,775 bytes; SHA-256 `8badd4e9cc8e0d5370623de836e3143b469ba086a963be234fdf82f8b27dc5b4`).

The first DEV audit process completed both replays but hit an external 1,800-second watchdog before its combined receipt; it wrote no PASS receipt and never invoked the sealed exam. The identical audit then passed under a longer watchdog. This was pre-exam audit work and did not consume the fresh authorization.

Policy SHA-256 remains `5db3922d5749e11548bca0c301abec19da5e2dfb993ffc17a44ec90989e34f73` for V36 and `14d237ccfcda4c716a43c6c455ad0f4a8c8994835f770bd3ff18ce4d7d79a54f` for V35.

The first newly authorized exam attempt then reached all 171 V36 policy evaluations but exhausted Node's 4 GiB heap before any score row or result artifact was written. Its only output was the 688-byte start receipt, preserved by SHA-256 `c51ea3f1512701aafcf33e2a3a56dcb6741f702074170c81cdbc40deb8298c8b`. This is the authorization's explicitly retryable mechanical-failure class.

The follow-up repair removed every remaining `gzipRows/Array.join` JSONL path and processes one brain through replay, streaming serialization, two-build comparison, and release before loading the next. The >1 GiB focused test again passed, this time with 110,624,768 bytes of peak RSS delta. A fresh post-change DEV-804 audit again proved both complete decision streams, scorecards, and frontiers byte-identical. No policy byte changed and no exam score row exists before the permitted re-attempt.
