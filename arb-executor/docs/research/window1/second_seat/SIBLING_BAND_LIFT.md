# Sibling-band lift — V31.1 feature spec

Analysis seat only. Read-only, causal, no oracle input. Machine artifact:
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/SIBLING_BAND_LIFT.json`.

Re-run of Path-Alpha Part 2 (dip-timing, spec at e64b0837) with the feature set
**doubled**: the armed leg's six causal EWMA bands **plus the sibling leg's six**
(read causally at the same timestamp), walk-forward-by-date logistic. Same 218
wrong-phase legs (R3 49f6501), same 10-min divot horizon, 68,001 samples.

## Result — sibling bands add held-out lift

| feature set | held-out divot AUC |
|---|---|
| own-leg 6 bands (baseline) | 0.777 |
| **own + sibling 12 bands** | **0.794** |
| **Δ** | **+0.016** |

Median lead 2070 s (vs 2221 s baseline) — essentially unchanged (~35 min), still far
above the 4.0 s bar.

### Per category

| category | own-6 | own+sibling-12 | Δ |
|---|---|---|---|
| WTA_CHALL | 0.691 | 0.720 | **+0.029** |
| ATP_CHALL | 0.759 | 0.785 | **+0.026** |
| ATP_MAIN | 0.635 | 0.652 | **+0.017** |
| WTA_MAIN | 0.702 | 0.627 | **−0.075** |

## Reading

**The sibling's book carries information about the armed leg's deeper dip** — for three
of four categories, adding the sibling's six bands lifts held-out AUC (+0.017 to
+0.029). That is the machine form of "one side's read is both": in a two-player market
the winner-side demand pressure that precedes the loser-side knock-down is visible on
*either* book, and reading both beats reading one. **This is V31.1's feature spec** for
the dip trigger: own-6 ∪ sibling-6.

**With one gate.** WTA_MAIN *degrades* (−0.075) when the sibling bands are added — the
thinner WTA_MAIN books make the extra six features overfit rather than inform. So the
V31.1 spec is **category-gated**: own+sibling for ATP_CHALL / ATP_MAIN / WTA_CHALL;
own-only for WTA_MAIN. A single global model that forces sibling features everywhere
would give back most of the ATP/WTA_CHALL gain on WTA_MAIN.

**Scope.** This lift is on the *dip-timing* AUC (when the knock-down lands), the part
that already passed the Jul-6 bar — not on the role call, which remains the coin-flip+
bottleneck from Path-Alpha Part 1. Sibling bands sharpen the trigger; they do not by
themselves solve role separation at the lockable moment. V31.1 = category-gated
own∪sibling dip trigger; the role-call frontier (V31 sequential reader) is still open.
