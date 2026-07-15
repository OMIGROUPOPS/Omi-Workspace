# OUTCOME PROOF — C-FLOW-REST-SEED v1 (operator R1 GO word, 2026-07-15)

**Deploy candidate SHA: `f861d24e`** (code `926b4bf4` + honesty fixes `dd42194e`/`25e4d831`/`f861d24e`; branch `blend/kalshi-occ-fallback`).

## PRIOR ART (C45)

- **C-KOAY-EXHIBIT v1** (`.claude/reachrecal_20260715/KOAY_EXHIBIT.md`, same night) — the founding case and the R1 remedy pricing this build ships.
- **C-TAPE-SEED 07-10** (`2f26cc00`+`e7b4e8f0`) — the proven pattern: REST-seed a WS-starved memory; this build applies it to the flow gauge, consultation-local.
- **−0k survivor class 07-11** — live n_eff undercount (WS-seen vs full tape); this build closes it at the dossier consultation site ONLY.
- **C-VAULT-WIRED-ENTRY 07-14** — the dossier law this gauge feeds.
- **Delta:** the consultation gauge gains an exchange-truth input with full provenance stamps; the gun's WS-seen counter (fitted, `percat_fitted` thresholds) is UNTOUCHED — a gun-input change is its own word.

## WHAT SHIPS

1. `_flow_rest_refresh(tk)` (async): REST `/markets/trades?limit=100` → consultation-local cache `self._rest_flow` (30-min trades). Cooldown 45s on `tried`; data freshness on `ts` (a failed fetch never re-stamps stale trades as fresh); fail-soft (WS gauge stands). **Never writes `_trade_times`/`_trade_prices`.**
2. `_route_event` warm hook: fire-and-forget `ensure_future` for in-window events (start unknown or <10h out) — **never blocks the decision slice**.
3. `_entry_dossier` gauge merge: `p30 = max(ws, rest)` (REST can only ADD true prints); trailing median from the richer tape; stamps `gauge_src` / `prints_30m_ws` / `prints_30m_rest` / `flow_bucket_ws` on the reach_law + flow_state surfaces; `flow_rest_seed` event on bucket flips (deduped 300s).
4. Config `flow_gauge_rest_seed: true` (DECREED — operator R1 GO word 07-15; cited in `knob_citations.json`).

## THE PER-GAME OUTCOME REPLAY (vs the prior slate — tonight's jsonl, every dossier consultation recomputed on the exchange REST tape at its own instant)

Replay instrument: `.claude/reachrecal_20260715/replay_flow_seed.py` (run at `926b4bf4`; first run's silent 20-page truncation counted the densest tape as zero — fixed with named truncation/window warnings + 429 backoff before the certified run; the instrument obeys no-silent-caps).

### Founding case (KOAYAZ)

- YAZ consulted 12:25:44 AM: live p30=1/quiet/p_fill 0.000 → REST p30=3 → **warm / 0.010**. (The exhibit's first "open/0.449" draft was WRONG and is amended: the 30-minute bucket lags a 26-second-old burst even on an honest input — named as a second limitation, reach-law-refit territory, NOT cured by this build.)
- KOA consulted 12:26:36 AM: live p30=1/quiet/p_fill 0.000 → REST p30≈15 (exhibit tape read; the replay's certified-run KOA row inherits a REST-history depth warning where the in-play tape outran the page budget — the named-warning lane, never a silent zero) → **open / 0.346** at the gun-bound residency.

### The slate (certified run, numbers below)

**19,141 consultations / 228 tickers replayed.** Per-cat bucket transitions (live-consulted → replayed-honest):

| cat | unchanged | quiet→warm | quiet→open | warm→open | flips |
|---|---|---|---|---|---|
| ITF_M | 1,372 | 17 | 7 | 5 | **29** |
| ITF_W | 17,589 | 61 | 26 | 54 | **141** |
| WTA_CHALL | 5 | 1 | 0 | 0 | 1 |
| ATP_CHALL | 4 | 0 | 0 | 0 | 0 |

**171 flipped consultations of 19,141 (~0.9%)** — the stale-input error is rare and concentrates EXACTLY at onsets (the quiet→open class is the KOA shape: e.g. FOMCHA ws=0/rest=179 → p_fill 0.0→1.0; SUSMAT ws=0/rest=12 → 0.007→1.0; POZMIL's below-floor refusals consulted quiet against a 13-14-print tape for six straight minutes). Certified founding rows: **KOA ws=1/rest=20 → quiet→open, p_fill 0.000→1.0**; YAZ ws=1/rest=3 → quiet→warm, 0.000→0.010 (the amendment's number).

**Named instrument limits (no silent caps):** 15 tickers carry "tape does not reach the window" warnings — most are tickers whose first trade EVER postdates the early consult windows (benign: no trades existed); the deep in-play tapes (KOA, FOMCHA-CHA) may UNDERCOUNT rest prints at their earliest consults (KOA's rest=20 is independently complete: its first print ever was 12:25:22, verified by full pagination in the exhibit read). Undercounts bias the replay AGAINST the seed — the flip counts are floors.

### Behavior isolation (the no-decision-change lane)

- Aims are atlas-page-priced UPSTREAM of the gauge; the gauge feeds the dossier record only. Per-line replay check: **every `placed:path_aim` dossier's aim equals the page's `path_aim` — 199/199, 0 mismatches** (bucket-independent by construction).
- Consumers of `self._rest_flow` in the tree: `_flow_rest_refresh` (writer), `_route_event` warm hook (cooldown read), `_entry_dossier` (gauge merge). No placement, cancel, exit, completion, or gun path reads it.
- The gun's counter (line ~6482 `vol_prints_30m` and the percat threshold path) reads `_trade_times` — untouched by this build; `grep -n "_rest_flow" live_v4.py` shows the three sites above only.

## WATCHES (nightly, from tonight)

- `flow_rest_seed` events/night with bucket_ws→bucket_used transitions (the honest-input meter).
- `gauge_src` split on reach_law consultations (rest_seeded share should dominate in-window; ws_only spikes = the warm hook starving).
- REST call volume via rate-limiter pressure (cooldown 45s bounds it; a 429 storm = named defect).
- The onset-lag limitation accrues evidence for the reach-law refit (YAZ-type: honest-bucket-warm fills within seconds of consult).
