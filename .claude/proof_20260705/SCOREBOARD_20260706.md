# SCOREBOARD — 2026-07-06 slate, C-RISER-REVISION live test (pre-registered 2026-07-05, BEFORE the data)

**Deployed:** `9925dd6` (armed state `bde7c958`, code `4d7b065c`), PID 3766708, boot 22:46 ET Jul 5.
Flag `riser_post_revision` ON: riser legs post riser_post below best bid (CHALL 3¢ / ITF_M 3¢ / ITF_W 2¢ /
mains hold 0) at the leg2_reshuffle conception site. Walks/reposts untouched — erosion is bar (e).

## Prior art (gate — C45)
Bars derive from: PROOF_PASS.md two-lane replay (89/107 retained, +2–3¢ Δaim), RISER_REVISION_PROPOSAL.md
retention curves (N=69), C44 amendment (riser adverse selection: mean +1.6¢ token discount baseline,
8/11 fills above burst-FV), FULL_TAPE_REGRADE baseline (81%→79% pairs ≤97; 41→63 pinned at 97).
DELTA: tomorrow's numbers against these pre-registered bars.

## LANE 1 — MECHANISM (primary; the fix lives or dies here)
| bar | pre-registered pass condition | baseline (07-05 box) |
|---|---|---|
| (a) riser Δaim shift | riser-leg fill discount vs best-bid-at-post: median ≥ +2¢ on CHALL/ITF risers (distribution shifts NEGATIVE by ≈ the depth) | mean +1.6¢ "token" (C44); riser_post=0 |
| (b) riser fill retention | riser legs still fill: retention ≥ 60% of the category's paired-eligibility baseline (curves say 62–90%; replay said 83%) | 91% at depth 0 |
| (c) ≤97 completion rate | holds or improves vs baseline | 79–81% of pairs ≤97 |
| (d) grade construction | naked-single count and A–F mix hold or improve | 37 naked / F24 D14 A38 C52 B16 (147 box) |
| (e) erosion detector | share of riser fills that walked back UP to the touch before filling < 25% — else the walk/repost paths are eating the revision and the CONCEPTION-only scope was insufficient | n/a (new) |

**Decision rule (pre-registered): if (a) does not move — median shift < 1¢ on CHALL/ITF riser fills — the fix
MISSED and comes out (disarm `riser_post_revision`, one config flip through the gate). If (a) moves but (b)
collapses below 50%, same exit. Bars (c)/(d) protect against structural regression; (e) triggers the walk-cap
follow-up build, not a disarm, if (a) still passes.**

## LANE 2 — SETTLEMENT P&L (secondary, sanity)
Reported with its n. **Flag LUCK-POLLUTED below n≈30 settlements — never the sole verdict.** A Lane-1 win
with a Lane-2 loss at small n = "insufficient settlements," not guilty.

## How to grade (tomorrow's pass)
Re-run `full_tape_regrade.py` (fresh box) + `proof_pass.py` conventions; riser legs identified per-leg
(side=="riser"); Δaim vs best-bid-at-post from the log's order_placed/v4_place records; the erosion bar from
repost chains. Same push: scoreboard graded → verdict row appended here → Vault deploy-ledger update.
