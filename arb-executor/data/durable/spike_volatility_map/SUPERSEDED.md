# SUPERSEDED — do not deploy from this directory

This spike-map adaptive exit surface was **superseded 2026-06-01** (config
flip `1775b453`) by the validated gated-optima surface at
`data/durable/exit_surface_gated_optima/` — see `LOCKED_DOWN.md` there for
identity, provenance, validation, and the change protocol.

Why: this surface **fails the smoothness gate** (2026-06-12 run of
`analysis/exit_surface_smoothness.py`): adjacent-cell band jumps up to 57c,
dozens of unnamed >5c jumps per category, HOLD cells present. It is retained
solely as a named rollback artifact; the repo and deployed copies of this
directory have also drifted apart historically, so any rollback must re-pull
from repo blobs and re-clear the smoothness gate first.
