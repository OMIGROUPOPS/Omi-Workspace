# PLEX AIM_V2 RULING — operational parameters (relayed 2026-07-06, evening)

**Provenance:** text as relayed by the operator with the execution dispatch, 2026-07-06.
The relay delivered the ruled parameter set below, citing ruling item ⑦ (hierarchical
fallback) inline. If a fuller verbatim Plex body exists beyond this relay, this file
reserves its slot (REANCHOR precedent); the operative constraints are in force as
relayed either way. Everything remains GATED-OFF; nothing arms from this ruling alone.

---

## THE RELAYED TEXT (verbatim, the ruled parameters)

RE-DERIVE the candidate tables as OPERATIONAL under the ruled parameters:
clock = LATCH-CAL canonical, per-event residual gate 25m (fail → no_bell);
prior weight w = 0.25; dip admissibility ITF+CHALL only, survival floor 3¢,
mains dip = NULL; complement fold as per-cell consistency gate (fat-tail
flag); hierarchical fallback ACTIVE per ⑦: cell → (cat,bucket) → cat curve,
parent valid ONLY if honest-era n≥30 at its own tier, ITF/CHALL only above
the survival floor, mains NULL full stop, borrowed_from + inflated resid_sd
on every fallback aim. Trigger accounting = honest-only (blend is estimator
input post-fire, never trigger basis).

RE-VALIDATE on the ledger day, C46 two-lane, all pre-registered metrics
incl. gold-leg production + B3-conversion (now ratified Lane-1 bars).
Expect participation still short at w=0.25 — report it straight, plus the
fallback chain's contribution separately (how many steps served by borrowed
tiers vs true cells vs NULL).

THE RAMP FORECAST, from real ingestion: with night-1's honest sample rate,
per (cat,Tbin) tier — when does each cat curve cross honest n≥30 (dates),
and when does honest-only coverage cross the §3 trigger? The output is a
dated schedule, not a vibe.

Note in the report (no build): the tennis.db live_scores retention gap —
collector overwrites in-play transitions; a retention change would bank
observed true starts from tonight forward. PARKED pending its own dispatch.

---

## Extracted constraints (C45 grep surface)
- **Clock: LATCH-CAL (K=600/M=20,000) is CANONICAL** for the aim tables; per-event
  residual gate |bell − certified latch| ≤ 25m where a latch exists — fail → no_bell.
- **Prior weight w = 0.25** (card-era rows quarter-weighted as ESTIMATOR input);
  **the §3 coverage trigger stays HONEST-ONLY** — the blend never counts toward firing.
- **Dip admissibility: ITF_M/ITF_W/ATP_CHALL/WTA_CHALL only, survival floor 3¢**
  (operationalized: cell dip admissible iff P(dip ≥ 3¢) ≥ 0.50 in-cell); **mains dip =
  NULL full stop, including via fallback.**
- Complement fold = per-cell consistency gate with fat-tail flag (never an n-doubler).
- **Hierarchical fallback ACTIVE (⑦):** cell → (cat,bucket) T-curve → (cat,T) curve;
  a parent tier serves ONLY if its own honest-era n ≥ 30; ITF/CHALL only above the
  survival floor; every fallback-served aim carries `borrowed_from` + inflated
  `resid_sd` (×1.5 tier-2, ×2.0 tier-3 — stated inflation).
- Gold-leg production + B3-conversion are RATIFIED Lane-1 bars alongside the standing
  set (participation holds · joint-gap shrinks · lazy shrinks · ≤97 rate).
- live_scores retention gap: PARKED pending its own dispatch (no build here).
- Implemented by: `analysis/aim_v2_operational.py` → `data/shape_corpus/aim_v2_operational_LATCHCAL.json`,
  re-validation + ramp forecast in `.claude/autopsy_20260706/AIM_V2_OPERATIONAL_REPORT.md`.
