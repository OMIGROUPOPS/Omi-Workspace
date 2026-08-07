# Stage C — V36 cutover preparation (build, do not switch)

Status: **PREPARED_SOURCE_ONLY_ENGINE_PARKED / LIVE-CAPITAL NO-GO**.

The stopped VPS now has committed Stage-C source at `896de4108a855abb75fd6bc31330445579f2f2fb`. `live_v4.py` is blob `b1ca505c659e8ef92024b124b6caf96c612a1e3b`, SHA-256 `9818ab042854c881a3ae53f5f1f437845d2d11a01102b00df76e4a5d8b8d238a`, 1,001,368 bytes. The engine was never started or restarted, and the inhibited crontab was not changed.

## Drift disposition

The complete `+692/-39`, 31-hunk patch was verified at SHA-256 `6a53d968...` before mutation. Every hunk is enumerated in `DRIFT_DISPOSITION.json`: `KEEP=0`, `RETIRE=31`, unexplained `0`. The working file was restored to exact `f1857199` and the prepared commit then applied. The old patch remains immutable evidence at:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/7fb4c9aecbee7d05fbb24d28f933e17044b8b40d/.claude/boot_gate_stage_b_recorder_seal_20260806/LIVE_V4_UNCOMMITTED_DIFF.patch

No uncommitted entry organ survived. The new diff from `f1857199` contains only the authorized V36 shadow wiring and the independently controlled exit fallback behavior.

## V36 shadow

The five policy/dependency files are byte-identical to the frozen V36 package. The authoritative V36 file is:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/bfde0d8d1135f5c5f48a5f3d619ab30050efab83/arb-executor/analysis/window1_v36_state_directional_rest_mature_floor.js

V36's later operative re-adjudication is controlling; the contaminated deep-frontier rejection is not:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/a76377d7e9e9085c14b3b396a008fddddbb6e627/arb-executor/docs/research/window1/WINDOW1_V36_READJUDICATION_V37_ADDENDUM.md

`v36_shadow_brain.py` receives causal book/trade receipts and emits `v36_shadow_decision` / `v36_shadow_fill`. It has no API, session, place, cancel, or position authority. Incumbent live decisions remain untouched during shadow. Cutover still requires the operator's explicit later word, at which point the migration doctrine requires deletion—not disabling—of the displaced incumbent organ.

## Exit fallback hardening

The silent `(15, "exit")` default is absent. A missing cell emits `CRITICAL_exit_cell_missing`, borrows the deterministic nearest same-category cell with a receipt, and raises if no same-category surface exists. This is the exact behavior controlled by:

https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/07541b48b246155294939ac28808b70655b25b69/arb-executor/live_v4.py

Six focused tests pass. R3 is available and reports `PASS (18 assertions)`.

## Recorder and sealed stream

The authoritative recorder PID `3459414` is supervised by the every-minute guard and is writing the current stream. The nightly N=20 reconciliation is green: `1,779` exchange prints equal `1,779` recorder prints, zero mismatches. The forward registry contains `77` capture-only events, registry SHA-256 `9f5dfb2a...`, with zero decision-relevant consumption.

## Readiness ruling

The Stage-C runtime paths are committed and clean, the engine remains stopped, V36 is shadow-only, exit hardening is present, R3 passes, reconciliation is green, and sealed tagging is intact.

Repository-wide launch readiness is nevertheless **NO-GO**: twelve unrelated tracked modifications predating Stage C remain on the VPS, including four source/config/deploy files. Stage C had no authority to erase or adopt them. The live-capital switch is also independently unauthorized. The containment marker continues to mean that the only live_v4 keepalive line is commented; a future ceremony must boot once with cron still inhibited and may restore the exact original crontab only after every post-boot invariant passes.

## Conservation

- Engine starts/restarts: `0 / 0`
- Cron edits/restorations: `0 / 0`
- Order reads/mutations: `0 / 0`
- Position reads/mutations: `0 / 0`
- Configuration mutations: `0`
- Live-capital switches: `0`
- Recorder/sealed-stream mutations: `0 / 0`

This receipt authorizes nothing beyond independent review.
