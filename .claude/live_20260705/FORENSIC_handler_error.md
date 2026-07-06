# FORENSIC — handler_error — LIVE DEFECT (>=2 in 60min)  <!-- 1783355181 -->
written 2026-07-06 12:29:35 PM ET by live_validation_loop (read-only). Patch conversation starts NOW.

## Events (2 total this session)
- 12:26:21  — [Errno 28] No space left on device
- 12:26:21  — [Errno 28] No space left on device

## Timeline (raw log lines for the burst pair)

## Code path
traceback embedded in the event details. run() catch ~8345 (skips the rest of the loop turn incl. last_routing_sweep update), on_bbo_update catch ~6221 (skips _v4_manage_resting). Tripwire: [C-ERROR-TRIPWIRE] in _log.
