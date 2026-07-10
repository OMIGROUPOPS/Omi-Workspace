# RULING — EARLY UNLOCK (operator, 2026-07-09 late night; the realized volume floor unlocks the full 8-hour placement window)

## The operator's words, verbatim

> "with this particular game, it clearly crosses the volume floor we had set no? therefore, its tradeable. we are taking advantage of the full 8 hour window to scheduled start if the volume meets standards."

(Spoken on Papoe–Jeran, M15 Bucharest QF — realized lifetime volume ≈2,866 shares against the staged 2,500 floor, sitting untradeable in the silent T−8h→T−4h corridor.)

## Operationalization (C-EARLY-UNLOCK, this deploy)

1. **The unlock:** at the v4 placement gate, when an event's **realized lifetime contract volume ≥ the staged floor (2,500)**, the T−240 min placement cap lifts to the full conception horizon (T−8h, honest-anchored). The corridor between T−8h and T−4h stops being unconditionally silent — volume buys entry into it.
2. **Realized only, never projected** — STEP1 §P1b stands (early volume is uninformative as a *predictor*; this ruling keys on volume that already happened, which is not a projection).
3. **ITF categories only** (ITF_M, ITF_W) — the floor is an ITF ruling; mains/CHALL gates untouched.
4. **Volume basis is LIFETIME, named per line:** primary = Kalshi REST `volume_fp` summed across the event's legs at every discovery cycle (`kalshi_rest_lifetime`); fallback = `ws_contracts_since_boot` (named as such — undercounts across restarts, never silently substituted).
5. **Everything downstream unchanged:** FV, cells, plays, sizing, horizon chokepoint, gun refusals, cycle cap, in-flight lock, all existing protections. The unlock moves ONE number: the event-level placement window edge.
6. **Self-measuring:** every buy placed under the unlock is stamped `early_unlock: true` + realized-volume-at-placement + basis; fills inherit the stamp; the nightly ledger renders the early-unlock cohort separately so the entry-table refit grades early entries against the standard-window cohort honestly. Watches: early_unlock entries/night, fill rate and Δaim vs the standard cohort.
