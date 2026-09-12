# FACE v3 amendment — Astra mockup review

2026-09-12. Supersedes the earlier proposed TUNE/LIVE palette and tab names. The old Day Sheet is concept prior art, not a visual template. Source hashes are in MOCKUP_RECEIPT.json; mockup HTML/PNG files are static, not an application or live data.

| Tab | Initial review | Final build ruling |
|---|---|---|
| LAB | AMEND: reduce decimal noise, retain exact raw values/source on hover; real axes, signed gap strip and oracle are mandatory in implementation, not decorative chart space. Use fixed receipt panel, not a modal. | SIGN: shared background, two text greys, amber only for our bids/fills, red only faults/PAPER. Source/receipt/OS binding on numeric panels. Preserve all existing trace/grade/renewal functionality; missing detail/depth stays explicit. |
| DESK | AMEND: historical examples must never be labelled today's positions. Mockup explicitly says historical example; actual disconnected DESK must show no invented live games, balance, heartbeat or freshness. | SIGN for gated UI and ledger contract. The operator has approved the prospective LIVE_PAPER cohort rule. Activation still requires verified read-only ingress and an enforced disjoint cohort at runtime. No live feed opened or key used by this design work. |
| SCOREBOARD | AMEND: include actual cohort counts and grade revision rows, not placeholder promises. Latest-per-game totals and all-run history have separate denominators. | SIGN: regenerated mockup includes counts/sums and stored history. Current rubric/letters unchanged; no grading code/OS edit. |

Build order: LAB, then gated DESK, then SCOREBOARD. Commit each part separately; capture actual application screens after build. One background; no per-side colors, green/red washes, badge outlines or decorative icons. Numeric display rounding is presentation only, with exact values retained on hover.

LAB execution boundary: the hosted static client must not contain engine code or credentials. It reads prepared, hash-bound runs; arbitrary tape execution requires a local OS adapter. The old rerun_game fallback temporarily edits a builder and is not authorized by this face-only order. Do not wire that fallback to a button or claim selecting a stored trace reruns the OS. Missing local runner is explicitly reported, not silently substituted. Library/tune imports must carry source class and pinned OS/trace provenance, and reject sealed/LIVE_PAPER research inputs.

Inspection boundary: the hosted deployment excludes ~2.37 GB of raw stages/accountability. A fixed inspector may show compact stored receipt data and local full-source details, but cannot invent omitted pool member rows or renewals. Preserve local full-detail access and disclose hosted omissions.

Acceptance: five grades and source hashes unchanged; three tabs/deep links and keyboard controls work; no overlay inspector; no hidden loss of oracle/grade/history; unavailable depth and DESK activation honest; no engine or source data edits; public build contains no engine, secrets, raw tape or per-tick renewal files. Auto-deploy needs the actual Git connection/stable alias verified, not an assumption that the old immutable preview URL changes.
