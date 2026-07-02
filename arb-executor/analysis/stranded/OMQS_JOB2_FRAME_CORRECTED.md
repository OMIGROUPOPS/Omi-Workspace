# OMQS — CORRECTED JOB-2 MEASUREMENT FRAME (2026-07-01, supersedes pair-completion-NET)

**This supersedes the earlier pair-completion-NET scoring** used in `OMQS_MALPHA1_PAIRECON.md` (M-α1). That frame scored "complete the pair, hold both to settlement, NET vs baseline" — which is **wrong per the operator's doctrine** (§0A of the Vault):
- It scored **NET-to-settlement**, mixing the exit into an entry measurement. **Distortion (combined ≤97) is the entry scoreboard**, full stop — "if the combined is anything over 100¢ it's a total failure regardless of fills." Entry success is measured by the combined, not by a hold-to-settle P&L.
- It assumed **simultaneous both-leg fills at static cell targets**. The doctrine is **sequential, inverse-aware**: fill the two legs at DIFFERENT times, each at its OWN divot in Window 1 (the legs seesaw; the weak moment for one is the strong moment for the other). "Always-lay-both" = always be WORKING both legs (each hunting its own divot), NOT posting both simultaneously.

## The corrected frame — score current cells AND proposed tape-derived targets by:

**(i) Combined ≤97 achievement rate under SEQUENTIAL fills.**
Each leg is evaluated against **its own tape window and its own divot timing** (use the `dip_timing` surfaces), not a shared instant. For each pair: could leg A fill at its Window-1 divot AND leg B fill at its (different-time) Window-1 divot such that **combined ≤97**? Report the ≤97 rate (and the ≤100 / >100 tail). This is the entry scoreboard — the three observable prices only (best bid / best ask / last traded), never a constructed mid.

**(ii) Window-reachability of each fill's tailored exit band.**
For each simulated fill, does its tailored exit band get **touched** in Window 1 / the corridor / Window 2 (the window-map methodology already built — `OMQS_WINDOW_MAP_JUN26PLUS`)? A discounted entry has three shots at its exit, two before the game can hurt it; a late/expensive entry is W2-only (the knife). Report band-reach rate by window.

**(iii) Throughput floor — unchanged: ≥ 25 fills/day.**
A target set that scores well on (i)+(ii) but drops below 25 fills/day fails the floor. (Context: the bisect dropped current throughput to ~44-69 fills/day; the prior flags-ON box ran ~354/day — see `OMQS_DEPLOYBOX_COMPARE.md`.)

## NOT scored
- **NOT** pair-hold-to-settlement NET (the M-α1 metric). Settlement P&L is an exit/outcome measure and is downstream of the window-blind exit debt (§0A); it does not measure entry success.
- **NOT** simultaneous-fill combined at static cell targets (wrong timing model).

## Inputs / status
- **Inputs:** `dip_timing` surfaces (per-leg divot timing), the window-map methodology (`OMQS_WINDOW_MAP_JUN26PLUS`), the enriched L1 tape (`analysis/premarket_ticks`, bid/ask/last per tick). Re-anchor all timing on **true tape onset**, not scheduled start (§0A: tts@fill is stale-clock-contaminated everywhere).
- **Status:** the FRAME is landed here; the RUN (scoring current cells + proposed targets on i/ii/iii) is the next job, and it requires the dip_timing + window-map surfaces wired to the sequential-fill simulator.
- Relates: Vault §0A (doctrine), §4E/§4F/§4G, `OMQS_MALPHA1_PAIRECON.md` (superseded metric), `OMQS_DEPLOYBOX_COMPARE.md` (throughput context).
