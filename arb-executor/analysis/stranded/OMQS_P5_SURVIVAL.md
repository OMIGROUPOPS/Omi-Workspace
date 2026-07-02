# OMQS — P5: BOUHAR-CLASS SURVIVAL STUDY (core; spec-gap flagged) 2026-07-02

**Population = walked completions <100** (BOUHAR-class) across PRIOR box (Jun30 00:56-15:46, flags ON) + CURRENT box (Jun30 15:46→now) + today. Read-only. `p5.py` → `/root/shadow_p4/p5_population.json`.

## ⚠ Spec gap — three P5 deliverables need the dispatched spec
The P5 spec was not in CC's context. **Defined + delivered:** population, sizing, exit-reach, net P&L (fresh settlements). **NOT defined (need the dispatch):** **"ribbon arithmetic"** (interpreted below as sum-of-locked-edge — confirm), **"reproducibility signature"**, **"pre-committed close-triggers"** (need the exact threshold values). The survival result below clearly fails any reasonable survival bar, but the *pre-committed* trigger values are Plex's to state.

## Sizing
- **25 pairs** (PRIOR 15, CURRENT 10). Cats: ITF_W 6 · ITF_M 6 · ATP_CHALL 6 · WTA_MAIN 4 · ATP_MAIN 3.
- Combined dist: min 80 · **med 99** · max 99. **Only 5/25 ≤97.** The class is overwhelmingly **par-adjacent (98-99).**
- **Locked edge (100−combined): median 1¢**; **sum = 61¢ = $0.61** total theoretical lock across all 25 pairs (my read of "ribbon arithmetic" — the aggregate edge ribbon).

## Net P&L (fresh settlements) — the class does NOT survive
- **Realized so far: −$17.00** on 7/50 legs settled — **negative despite every pair completing <100.**
- **Mechanism:** **24/25 pairs exited early** (not held to lock). The window-blind band-exit (§0A debt) **sells the winner leg at +band (caps the gain) and rides the loser leg to 0** — FUCKUP-3. So a <100 completion that *should* lock 100−combined instead realizes a loss. Every settled leg in the population is a loser-leg settling negative (−0.75 to −3.70).
- Even the **best case (hold-to-settle) is ~$0.61 gross** across 25 pairs — below fees. The class is economically marginal even before the exit destroys it.

## Exit-reach
- **24/25 (96%) reached an early exit** (`exit_filled`) — the band is reachable, but reaching it is the *problem*: the tailored +band exit on the winner caps the pair's locked edge and leaves the loser naked. Held-to-settle would lock 100−combined; the policy does not hold.

## Verdict
**The BOUHAR-class does not survive.** Walked completions <100 are par-adjacent (98-99, ~1¢ edge, $0.61 aggregate) and the window-blind band-exit converts the paper-lock into a realized loss (−$17 and counting). **This closes "complete more pairs" as a build target** — the walk produces completions (STEP-1 grade) but the completions are worth ~nothing at 98-99 and the exit loses on them. **The lever is the EXIT (make it window-aware / hold <100 completions to lock) and the ENTRY PRICE (get combined ≤97), not completion volume.**

Ties the arc together: ITF paper-opportunity (P4/P4b) + par-bound combined (P3b, ≤97 rare) + window-blind exit (§0A) + FUCKUP-3 → **completing pairs at 98-99 and band-exiting them loses money.**

Method: `p5.py`. Pre-committed close-triggers + reproducibility-signature pending the P5 dispatch spec.
