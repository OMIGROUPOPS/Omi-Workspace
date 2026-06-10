# Exclusion Regime v1 — what the scanner deliberately does not trade

One page. Each excluded class: mechanism in code, provenance, ratification state.
Compiled 2026-06-10 ([C-SCAN-READS] R4); line numbers cite live_v4.py @ 783a80e4.

## How exclusion works mechanically
Discovery enumerates ONLY the series in `SERIES_MAP` (live_v4.py:142–152) — the
market pull loops `for series in ALL_SERIES` (live_v4.py:2071,2074). Any series
absent from that dict is never queried, never subscribed, never routed: exclusion
by omission, one site. A second, separate gate filters discovered categories at
placement: `if cat not in self.categories_enabled: continue` (live_v4.py:3391;
config `categories_enabled`, loaded at live_v4.py:981, value in deploy_v5_live.json
= ATP_MAIN / WTA_MAIN / ATP_CHALL / WTA_CHALL).

## 1. ITF (108 listed events on 2026-06-10: KXITFMATCH 53 men's, KXITFWMATCH 55 women's)
- Site: series absent from `SERIES_MAP` (live_v4.py:142–152).
- Provenance: SERIES_MAP inherited verbatim from live_v3.py (first tracked at
  eb99a928, 2026-04-17 — "live_v3 deploy: 10/5ct baby"; may predate in untracked
  form) into live_v4.py at f7ad6061 (2026-05-25, "initial copy from live_v3.py").
  No code comment states a rationale.
- **RATIFICATION: ITF exclusion RATIFIED KEPT by operator 2026-06-10. Rationale:
  volume.** Noted future test: per-series in-match volume profiles vs a tradeable
  threshold (corpus replay) — QUEUED, not scheduled.

## 2. Derivatives — set-winner / exact-score / total-games / game-spread
(2026-06-10 board: KXWTASETWINNER 26, KXATPSETWINNER 24, KXATPEXACTMATCH 12,
KXATPGTOTAL 11, KXATPGSPREAD 11)
- Site: same — series absent from `SERIES_MAP` (live_v4.py:142–152).
- Provenance: same inheritance chain (eb99a928 → f7ad6061). No stated rationale
  in code; the entire edge corpus (atlas, exit surfaces, entry tables) is built on
  match-winner contracts only.
- **Status: PRESENTED FOR OPERATOR RATIFICATION. No recommendation.**

## 3. Futures / outrights / specials
(e.g. tournament winners KXATP/KXWTA, #1-rank KXATP1RANK, KXATPRETIRE,
KXATPRETURN, finals qualifiers)
- Site: same — absent from `SERIES_MAP`.
- Provenance: same inheritance chain. These are not match-shaped (no T-240 window,
  no match start, no pair structure); every layer of the v4 machine assumes a
  paired two-outcome match.
- **Status: PRESENTED FOR OPERATOR RATIFICATION. No recommendation.**

## 4. Grand-slam category gating (the one DISCOVERED-but-gated class)
- `KXATPGRANDSLAM` / `KXWTAGRANDSLAM` ARE in `SERIES_MAP` (live_v4.py:147–148,
  categories ATP_SLAM / WTA_SLAM) — discovered and subscribed — but excluded at
  placement by the `categories_enabled` gate (live_v4.py:3391; config value lacks
  the slam categories). Introduced with the v4 placement loop at 823b9573 /
  cc54eeef (2026-05-25).
- Note: the only KXATP/KXWTAGRANDSLAM events currently listed are season-long
  futures ("Who will win a WTA Grand Slam in 2026?"), not matches; the category
  gate is what keeps the scanner out of them today.
- **Status: PRESENTED FOR OPERATOR RATIFICATION. No recommendation.**
