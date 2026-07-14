# FORENSIC — handler_error — LIVE DEFECT (>=2 in 60min)  <!-- 1784042469 -->
written 2026-07-14 12:37:05 PM ET by live_validation_loop (read-only). Patch conversation starts NOW.

## Events (2 total this session)
- 11:21:01  — [Errno 28] No space left on device
- 11:21:09  — [Errno 28] No space left on device

## Timeline (raw log lines for the burst pair)

## Code path
traceback embedded in the event details. run() catch ~8345 (skips the rest of the loop turn incl. last_routing_sweep update), on_bbo_update catch ~6221 (skips _v4_manage_resting). Tripwire: [C-ERROR-TRIPWIRE] in _log.
