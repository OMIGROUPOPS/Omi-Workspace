# live_v4 missing-exit-cell fail-loud PRE-RUN

The engine remains parked. This package changes only the missing-cell branch of
`LiveV3.exit_rule_for`: exact table hits remain unchanged; a missing cell emits
`CRITICAL_exit_cell_missing`, deterministically borrows the nearest same-category
cell, emits `exit_cell_nearest_borrowed`, and raises when no same-category
surface exists. The old silent `(15, "exit")` return is absent.

No deployment, restart, cron restoration, live access, order action, position
action, configuration change, or exit action occurred. Python runtime execution
was unavailable on this workstation; the executable Python test is committed
for audit, while the source-invariant Node test passed locally.
