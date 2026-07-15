# WINDOW-BOUNDARY CONSUMER CENSUS (C-WINDOW-LAW v1 Part 2 — every clock consumer in live_v4, its boundary, its lawfulness per §5)

§5 law: **W1 = fill→scheduled · CORRIDOR = scheduled→gun · W2 = gun→settle. The corridor opens at schedule, closes at gun, never at a burst.**

| # | consumer (code site) | boundary consulted | lawful per §5? |
|---|---|---|---|
| 1 | v4 placement window (`V4_MAX_PLACEMENT_SEC`, `time_to_start` at v4_place) | scheduled | **LAWFUL** — W1 opener |
| 2 | early_unlock (ITF T−8h on realized volume ≥2,500) | scheduled + realized volume | **LAWFUL** — W1 opener variant (operator ruling 07-09) |
| 3 | conception horizon / `conception_beyond_horizon` | scheduled | **LAWFUL** — W1 bound |
| 4 | T−15 `match_start_buffer` entry cancel | scheduled | **LAWFUL** — W1 closer at the scheduled boundary (conservative by design) |
| 5 | completion buffer exemption (rides to T−0) | scheduled | **LAWFUL** — corridor-open consumer (completion bids may stand into the corridor) |
| 6 | `schedule_corrected` window deferral (start pushed → cancel early bids) | scheduled (future-only corrections, C-SCHEDULE-TRUST) | **LAWFUL** |
| 7 | `schedule_abandon_deferred` (tape_not_live) | scheduled + tape silence | **LAWFUL WITH CAVEAT** — uses the market clock but defers on dead tape; corridor-aware in effect |
| 8 | **`match_live_cancel` latch (volume burst)** | **BURST** | **CORRIDOR-BLIND — THE CONVICTION** (06-19 forensic: median +22 min premature; tonight: latches at 1:17–2:47 PM, hours before starts, evacuated 8 fitted aims). Closes the corridor at a burst, which §5 forbids. |
| 9 | **`match_live_grace_kill`** (grace then cancel) | **BURST** (inherits the latch) | **CORRIDOR-BLIND** — same class, sibling #1 |
| 10 | **post-latch entry freeze via `_gun_state` when source = `tape_latch`** | **BURST-sourced gun** | **CORRIDOR-BLIND, sibling #2** — the freeze itself is lawful (W2 opener) but INHERITS burst blindness when the gun's source is a bare latch; tonight's BROBOB/NEFTHO placements were blocked by latch-sourced state |
| 11 | fused gun freeze, evidence-grade sources (te_scoreboard / schedule_live / fallback bell / percat / self_fill) | gun | **LAWFUL** — W2 opener; the corridor closes here |
| 12 | self_fill bell (own-tape rise, 3-condition scope) | own fills/placements (evidence) | **LAWFUL** gun source |
| 13 | fallback bell source 5 (prints/min + honest-start clock) | honest clock + tape | **LAWFUL** gun source (fired LAJSVA +12.3 min on a 4-print tape) |
| 14 | percat fitted source 7 (prints30 ≥ threshold) | fitted flow | **LAWFUL** gun source |
| 15 | chase pursuit arming (first fill / first bell) | fill / gun | **LAWFUL** — W2-edge lock |
| 16 | pair-law seesaw (live sibling book vs page quantiles) | book state (clock-free) | **LAWFUL** — not a clock consumer |
| 17 | exit posting / band logic | fill-time anchors | **LAWFUL** — §0A fitted anchors, clock-free |
| 18 | nightly grading (`bells` = gun_fired as W1 end) | gun | **LAWFUL** — grades on our clock |
| 19 | dossier `honest_clock` surface | scheduled + anchor age | **LAWFUL** — reporting |

**The corridor-blind class: rows 8–10 — one family.** The latch conflates "volume arrived" with "the match started," and §5 says only the gun closes the corridor. The path thesis makes this expensive by construction: the fitted dips arrive WITH flow, and rows 8–10 evacuate the book exactly then (tonight: 9 touches, 0 bids present). **The remedy is the separately-gated presence build (re-place-on-unlatch + status-gated cancels) awaiting the operator's explicit word — NOT shipped here.**
