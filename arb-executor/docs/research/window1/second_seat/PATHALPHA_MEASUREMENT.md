# Path-Alpha full measurement — learned role rule, dip timing, combined ceiling

Analysis seat only. Read-only, no oracle input to the signals. Machine artifact:
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/PATHALPHA_MEASUREMENT.json`.

**Signals** — the six bands (`cross`, `lock`, `bid_dom`, `ask_dom`, `ask_stair`,
`bid_stair`) computed **causally** as EWMA rolling state (halflife 120 s) from each
leg's own WS-delta tape — no fixed snapshot window, no oracle input.

**Conservation** — 772 role-resolved events (oracle at 4aee323f); 619 receive a
held-out role prediction (the rest fall in the walk-forward warm-up before min-train
40); 218 wrong-phase legs for the dip test.

## 1. Role rule, learned lawfully (walk-forward by date)

Logistic on the leg-differential band-state at `call_moment`, expanding-window,
trained only on earlier dates. **Held-out role accuracy = 347/619 = 56.1%** — versus
the 54.3% tie-neutral coin-flip and the oracle Tier-A 179.

| category | held-out role accuracy |
|---|---|
| WTA_CHALL | 71/114 = 62.3% |
| ATP_CHALL | 160/281 = 56.9% |
| WTA_MAIN | 65/123 = 52.8% |
| ATP_MAIN | 51/101 = **50.5%** (chance) |

**A lawfully-learned rule barely clears the coin flip (+1.8 pp).** Roles are *not*
reliably separable at `call_moment` — the earliest lockable instant. This is the
sober counter to the six-band autopsy: the separating signatures the autopsy saw form
*later* (leads of 88–1332 min before the patient floor, i.e., well after the call), so
at the moment you must commit to arm, the book has not yet declared the role.

## 2. Dip timing — the bands as leading indicators (R3 wrong-phase legs, 49f6501)

Population: 218 wrong-phase legs (`V28_CARRIED_POSITIVE_LEG` ∪ `INCUMBENT_FIRST`,
deduped). Target = a qualifying ask new-low ≤ `aim_cents` (the deeper dip) within
10 min. 68,001 causal decision samples.

- **Combined walk-forward AUC = 0.777** (learned signs). Per band: **lock 0.822,
  cross 0.816, ask_stair 0.795, bid_dom 0.72, bid_stair 0.695, ask_dom 0.665** — every
  band clears 0.65 on its own.
- **Median lead = 2221 s (37 min)**, n=810 divots.
- **THE BAR (ruled Jul 6): AUC > 0.65 AND median lead > 4.0 s fill latency → PASS.**

The deeper dip is *preceded by demand pressure*: crossing, locking, bid-depth
dominance and an ask staircase build ~37 min before the knock-down. (My first pass
hand-weighted these with the signs inverted, yielding a spurious 0.29/FAIL; the
learned model recovers the true 0.777 — receipt in the artifact's `part2` note.)

## 3. The combined ceiling

Events where the **held-out learned role call is right AND the race is won AND both
floors exist (Tier A)** = **78** (ATP_CHALL 49, ATP_MAIN 13, WTA_MAIN 9, WTA_CHALL 7).

| ceiling | n |
|---|---:|
| read-moment (Tier B1) | 24 |
| formed-call tie-neutral (Tier B2) | 20 |
| **Path-Alpha combined (nominal)** | **78** |
| oracle Tier A (roles known) | 179 |

**Read this honestly:** the 78 rests on a role call that is only 56.1% reliable, so
roughly half of it is chance — it is **role-reliability-limited, not a robust 78**. The
gap to the oracle 179 is almost entirely the role call, not the dip or the race.

## Verdict — the harmonized architecture

The six-band autopsy was **half right**. The bands carry real, lawfully-learnable
structure — Part 2 proves it: **0.777 AUC, PASS**, they tell you *when* the deeper dip
lands, 37 min early. But that structure predicts **dip timing, not role**, at the
lockable moment. The role-separating signal exists yet forms too late to be called at
`call_moment`, so the learned role rule stays at coin-flip+1.8 and caps the honest
combined ceiling near its role reliability.

**Actionable split:** dip-timing is bankable now (arm the standing floor, let the AUC
0.78 / 37-min-lead signal fire the release). Role-calling at the lockable moment is
*not* solved and is the true bottleneck. The open frontier (call it V31) is a
**sequential reader** that spends race slack — the won-slack median was hours — to
accumulate role signal past `call_moment` until confidence clears a learned bar, then
arms. Parts 1–2 bound both sides of that trade: 56% at the earliest call, a role
signature that matures over the following 1–20+ hours, and a dip trigger that leads by
37 min. That is where the ceiling above 78 lives, and it is measurable next.
