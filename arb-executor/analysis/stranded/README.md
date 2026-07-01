# Stranded-single analysis substrate (preserved from VPS `/tmp`, 2026-07-01)

**Why this exists:** the completion-cancer diagnosis (§4E of the June Vault, n=93 stranded singles) was built through a chain of ephemeral `/tmp` scripts on the VPS over Jun 26 – Jul 1. The summarizing artifact `OMQS_ADVERSE_SELECTION_STRANDED.md` was **never persisted**, and the whole substrate sat in `/tmp` on a box that hit 100% disk. This directory locks the substrate into git so one reboot can't erase it. Preserved verbatim (byte-for-byte from `/tmp`, bundle md5 `b60f27135a591c3f50166bd638f20d80`).

**Status:** this is the raw/partial substrate, NOT the clean labeled input. The authoritative 93-event kept/missed/winner list is being rebuilt from the Jun24-30 order-event logs + Kalshi REST fills/settlements, gated on reproducing the funnel's 93 events + −$50.65 baseline (see the sibling `OMQS_ADVERSE_SELECTION_STRANDED.md` + `stranded_93.json` once the gate passes).

## Data files
- `stranded_ext.json` — list of 186 `{tk, ft}` (ticker, fill_ts unix) = 93 pairs × 2 legs. Producer not captured in `/tmp`; schema ambiguous (both legs carry an `ft`), so NOT trusted as-is for kept/missed labeling.
- `stranded_ticks.json` — dict keyed per-leg: `{cov, bid, ask, mid, delta}`. Book snapshot + tick-recorder coverage flag per leg.
- `stranded_rolldowns.json` — 19 rolled-down stranded legs with `rolldowns` + `cancel_ts`. **Narrow scope:** built by `rolldown_scope.py` from `logs/live_v3_20260627.jsonl` (Jun-27 ONLY) and CHALL/ITF cats only — this is NOT the Jun24-30 3-cat 93-set.
- `need_files.txt` / `need_tickers.txt` — `prep_files.py` output: ws-depth hour-files + tickers to pull for the rolldown legs.
- `settled.json` — Kalshi settlement snapshot (Jun 28) used for winner-labeling.
- `ttrades.jsonl` — extracted WS trade events (Jun 29) for the rolldown legs (input to `dip2.py`).

## Producer / analysis scripts
- `rolldown_scope.py` — origin: classifies rolled-down legs as stranded (self not filled, sibling filled) from the order-event log. Defines the "stranded" predicate.
- `prep_files.py` — from `stranded_rolldowns.json`, enumerates the ws_depth hour-files + tickers needed.
- `dip2.py` — reads `ttrades.jsonl`, analyzes dips on stranded legs.
- `dipthrough.py` — reads `data/durable/ws_depth_recorder` (L2 depth), builds per-leg windows around rolldowns → dip-through detection.
- `distort3.py` — **α-adjacent**: re-frames one-leg-only as recoverable (a resting at-touch maker on the missed leg would have filled) vs genuinely-unfillable, from `analysis/premarket_ticks` (L1) + `analysis/trades`.
- `xts.py`, `halfB.py`, `twojobs.py`, `trace_fix1.py` — supporting scratch from the same arc.

## Tapes referenced (live on the VPS, not copied here)
- L1 enriched: `analysis/premarket_ticks/*.csv` (bid_1/ask_1/last_trade/mid per tick, ET)
- L2 depth: `data/durable/ws_depth_recorder/ws_YYYYMMDD_HH.jsonl.gz`
- trades: `analysis/trades/`
