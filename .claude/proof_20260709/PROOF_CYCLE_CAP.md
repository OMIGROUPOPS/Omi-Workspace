# OUTCOME PROOF (C46, two-lane) — C-CYCLE-CAP (the operator's re-entry ruling: ALLOWED, capped at 2)

**Candidate SHA: `bbd8cada`**.

## Prior art (C45)
- **DAALU_REENTRY.md (07-09)** — the evidence package this ruling was made on: 23 legs / 46 cycles / +$15.84 / 22 of 23 net positive; both mechanisms named (router never wired to the cash guard; in-memory set wiped at restarts). This build is its §3 ALLOWED-path fix shape, verbatim.
- **C-ORPHAN-FINGERPRINT + C-GUN-PERSIST** — the pattern's first two applications; this is the third (cashed history), rebuilt at the SAME boot slot.
- **C-NO-REBUY-AFTER-CASH (07-07)** — the guard this AMENDS: its blanket session-set becomes a count gate (cycle-2 legal, cap binds); its audit assertion `post_exit_rebuy` becomes `cycle_cap_breach`.
- **C-BAND-CLAMP / make-it-stick lesson** — the chokepoint half exists because sweep-level gates get re-derived around.
- **SETTLEMENT VOCABULARY + grading laws** — the cycle-stamp on every fill/exit/scalp row exists so ledger grades never blend cycles.

## LANE 1 — MECHANISM (replayed against the forensic's own exhibits)
- **DAALUX under this build:** cycle-1 runs unchanged (count 0 → both gates open). At cycle-1 cash, count=1. The 2:54 pm restart REBUILDS count=1 from the jsonl lineage → **cycle-2 conceives LEGALLY (the ruling)** and its rows stamp `cycle: 2`. At cycle-2 cash, count=2 → **any cycle-3 attempt dies at the repost sweep (`cycle_cap_reached`) AND the chokepoint (`cycle_cap_refused`), and a resting buy beyond cap FAILS the audit (`cycle_cap_breach`) — across restarts.**
- **The LIXSUN class (same-session router re-conception):** the chokepoint gate now covers the router path the old guard never touched — cycle-2 passes, cycle-3 refuses.
- **Counting is completed-cash-only** (partials never increment — the TAN-shape partial class is exempt by construction); adopted-class fills are excluded from the lineage rebuild (A54 basis, fill-time unreliable).
- **Byte-identity notes:** legs with 0 completed cycles see no behavior change anywhere; the ONLY loosening vs the old guard is deliberate (cycle-2 now legal — the ruling itself); the only tightening is the cap surviving restarts and covering the router.

## LANE 2 — SETTLEMENT P&L
$0 claimed. The class measured +$15.84/week gross (fee-blind convention, flagged in the reconciliation); the ruling banks it as sanctioned behavior with a bound — no claim, the nightly ledger now cycle-stamps and reads it honestly.

## Regression watches
`cycle_history_rebuilt{n_legs,n_at_cap}` at every boot (the third rebuild line) · `cycle_cap_refused` / `cycle_cap_reached` skips · `cycle_cap_breach` audit failures (must stay 0) · `cycle` stamp present on every fill/exit/scalp row from this boot · monitor `open_cycle2` (standing).
