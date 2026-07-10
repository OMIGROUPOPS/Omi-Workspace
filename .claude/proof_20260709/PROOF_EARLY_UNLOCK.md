# OUTCOME PROOF (C46, two-lane) — C-EARLY-UNLOCK (operator ruling: realized volume floor unlocks the full 8h window, ITF only)

**Candidate SHA: `SHA_EU`** (live_v4.py gate branch + lifetime-volume accumulator + cohort stamp, config keys `early_unlock_enabled`/`early_unlock_floor`, daily_ledger cohort section, RULING_EARLY_UNLOCK.md).

## Prior art (C45)
- **RULING_EARLY_UNLOCK.md (this push)** — the operator's verbatim ruling, recorded first (RULING_BOT_ONLY_BASIS precedent).
- **STEP1 §P1b** — projection from early volume BANNED (bal-acc 0.56–0.65); this unlock keys on REALIZED volume only — volume that already happened is not a projection. The P1b finding and this ruling are compatible by construction.
- **Volume ledger 07-09** — fill probability scales with volume bands; a dead book never pays. The unlock is that finding's entry-side expression: a book that already proved life buys the wider window.
- **The PAPJER read query (tonight)** — the exhibit: 2,866 realized shares sitting untradeable in the silent T−8h→T−4h corridor (live_v4.py:7259 gate, silent return).
- **C-CONCEPTION-HORIZON** — the T−8h outer bound is UNCHANGED; the unlock extends the placement edge exactly to it, never past it (the chokepoint's horizon refusal still owns beyond-8h).
- **holdgate.py floor_qual / C-T4-DUAL-FLAG** — same staged 2,500 floor, same realized-contracts discipline, basis named per line.

## LANE 1 — MECHANISM
- **Gate:** ITF_M/ITF_W only; `early_unlock_enabled` config-explicit; volume basis = Kalshi REST `volume_fp` summed per event at every discovery cycle (`kalshi_rest_lifetime`, exchange truth, lifetime), fallback `ws_contracts_since_boot` NAMED (undercounts across restarts, never silent). Below floor or outside ITF → byte-identical to the old gate (`_eu_cap` stays T−240). Mains/CHALL take the identical old path.
- **Downstream unchanged:** the unlock moves ONE comparison bound. FV, cells, plays, sizing, never-marketable, band clamp, horizon chokepoint, gun refusal, cycle cap, in-flight lock, buy-position guard — all evaluated exactly as before on every placement.
- **Self-measuring:** `early_unlock_open` logged once per event per boot (vol + basis + floor + tts); every buy placed while the unlock is open stamps `early_unlock: true` + `unlock_vol` + `unlock_basis` at the single _log emitter; fills inherit; the standard-window cohort is never stamped (the mark clears at T−240). daily_ledger renders the cohort separately. Named limitation: the fill-stamp memory is in-session — a fill after a restart of an early-placed bid loses the stamp on the fill line (the placement line keeps it; offline joins recover the cohort exactly).
- **Live verification (the dispatch's own case):** post-deploy, PAPJER (realized ≈2,866 ≥ 2,500, honest tts ~4–5h) must log `early_unlock_open` and enter side evaluation on boot — reported in the close-out with its placement lines.

## LANE 2 — SETTLEMENT P&L
$0 claimed. The cohort stamp exists precisely so the early entries' P&L is graded honestly against the standard cohort before any claim is made.

## Regression watches
`early_unlock_open` per night (ITF only — any mains/CHALL occurrence = defect) · early_unlock entries/night + fill rate + Δaim vs standard cohort (nightly ledger section) · `unlock_basis` distribution (ws fallback should be rare) · conception_beyond_horizon stays 0 (the unlock must never place past T−8h).
