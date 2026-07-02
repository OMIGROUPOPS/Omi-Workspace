# OMQS P6 — CAPPED-WALK REPLAY + CEILING SWEEP (read-only) — 2026-07-02

**Question.** Take the bot's *actual* logged bid-walk (`v4_place.target_bid` + every `v4_move_repost.new_target`) and impose a **combined cap by construction** — the leader (higher) leg's walk is clamped so `leaderTgt(t) ≤ CAP − followerTgt(t)` at all times; the follower (cheaper) leg is unclamped. Replay fills against the L1 tape (maker bid fills when a trade prints ≤ target OR the ask descends ≤ target), hold-to-settle window (no t20m/match-live cancel — the walk-hold thesis). Sweep `CAP ∈ {95,96,97,98,99,uncapped}`. Judge **at cap-97** on three pre-committed axes. Box = Jun30 15:46 → now; **111 paired events, tape span 1.95 d.** Method: `p6.py` → `p6_frontier.json`.

## Validation gate — PASS (walk model is calibrated)
> Uncapped combined **min 80 / med 99 / max 106**, **70% (61/87) in the 98–100 band**, **44.6 completions/day**. Median in 98–100, clustered high → **reproduces the live box** (known behavior: combined 98–100, completion regime by flag era). **The walk model is not miscalibrated; the axes may be judged.**

## The frontier
| CAP | comp | /day | strand | combined (min/med/p75/max) | **E1 hold-$** | E2 band-$ | E3 asym-$ | ≤97 | 96-97 pile |
|--:|--:|--:|--:|--|--:|--:|--:|--:|--:|
| **95** | 58 | **29.8** | 42 | 80 / **95** / 95 / 98 | **+15.35** | −6.10 | +6.30 | 57 | 1 |
| 96 | 59 | 30.3 | 42 | 80 / 96 / 96 / 99 | +12.75 | −6.15 | +6.15 | 57 | 50 |
| **97** | 61 | **31.3** | 40 | 80 / **97** / 97 / 100 | +10.25 | −6.25 | +6.05 | 58 | **54** |
| 98 | 71 | 36.4 | 31 | 80 / 98 / 98 / 100 | +8.75 | −8.60 | +8.10 | 15 | 12 |
| 99 | 81 | 41.6 | 21 | 80 / 99 / 99 / 101 | +6.60 | −11.70 | +11.05 | 12 | 9 |
| uncap | 87 | 44.6 | 15 | 80 / 99 / 100 / 106 | +4.20 | −17.75 | +16.40 | 11 | 8 |

- **E1 = hold-to-settle**, analytic on the mirror pair (`$ = Σ (100−combined)/100 × 5 shares`) — robust, covers **all** completions.
- **E2 = live band-sell (+8)**, **E3 = winner-ride/loser-stop(12)** — need the settled outcome, so **coverage is only n=4→12 settled pairs** (most of the box is unsettled). **Treat E2/E3 as directional, not powered.**

## PASS / FAIL @ cap-97 (pre-committed) — **FAIL → closure fires**
| axis | result | verdict |
|---|---|---|
| ① ≥25 completions/day-equiv | **31.3/day** | PASS |
| ② median combined ≤95, no 96-97 pile | **median 97**, cluster **54/61 in 96-97** | **FAIL** (the exact pre-committed failure mode) |
| ③ reproducible signature | deterministic; per-cat {ATP_CHALL 16, ITF_M 15, ITF_W 13, WTA_MAIN 10, ATP_MAIN 7}; n=61, 58 ≤97 | reported |

**VERDICT @ cap-97: FAIL. Per the pre-commit, the static combined-cap-at-97 walk branch CLOSES.**

## Why it fails — the mechanism (the two invariants)
**INV-1 — the cap is a clamp, not a price-improver.** Fills pile at `cap−0/−1`: cap-97 → **54/61 land at 96-97, median = 97**; cap-95 → median = 95; cap-99 → median = 99. The median combined **equals the cap** because clamping the leader makes it fill at the clamp, not deeper. So axis-② "median ≤95" is a **restatement of "set the cap ≤95,"** not a discovery of edge — and it costs completions monotonically (**44.6 → 29.8/day as cap tightens 99→95**). The one genuinely deep double-fill (combined **80**) appears at every cap — it is cheap on the tape regardless, not a product of the cap.

**INV-2 — the locked edge is exit-policy-gated.** E1 (hold) locked-edge rises monotonically as the cap tightens (**+$4.20 uncap → +$15.35 at cap-95**), and stays ≥25/day throughout. **But under the live band-sell exit (E2) the *entire* frontier is P&L-negative** (−$6 to −$18) — the FUCKUP-3 defect (band caps the rising winner, holds the falling loser to zero). The cap's edge is realized **only** under hold-to-settle (E1) or asymmetric winner-ride/loser-stop (E3, positive everywhere). **Capping without changing the exit converts a positive locked edge into a loss.** (E2/E3 underpowered — n=4-12 — but the sign is consistent with the live grade card's −$55 realized and the FUCKUP-3 ledger.)

## Contingent closure (pre-committed language)
The static **combined-cap-at-97 walk is REFUTED** on its own pre-committed signature axis (median 97 ≠ ≤95; 96-97 pile 54/61). **Closure fires; the capped-walk-at-97 branch is closed.** The frontier documents one orthogonal exception — **cap-95 clears axis-② (median 95) at 29.8/day with E1 +$15.35** — but per INV-1 that is a tautology of the cap level, and per INV-2 its realization **requires abandoning the live band-sell exit** for hold-to-settle / asymmetric. That is an **exit-policy** result, **not** a vindication of the cap, and pursuing it is the **operator's call, not a silent continuation** (Plex's rule). **The next lever is the exit policy, not the entry cap.**

Artifacts: `p6.py`, `p6f_output.txt`, `p6_frontier.json` (`/root/shadow_p4/` on the VPS + repo). Read-only throughout; no live changes; bot untouched (PID 501822).
