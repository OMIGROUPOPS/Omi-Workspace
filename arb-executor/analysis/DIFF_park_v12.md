# DIFF — park_v12 (lock candidate): veto dropped; FLOOR derived (0.50, not 0.45); Sharpe conjunct REJECTED — it's a confound that ranks lotteries above the engine

Branch: blend/agent-derivation. Builds on v11 (`park_v11_firewall.py`).

## Signed & implemented
- **Reach-region veto DROPPED.** occ·cond is the sole firewall; fire the lowest RESOLVED mode (necessary-gated by EV/paid/supp). Opus's deeper reason adopted: the veto measured the *symptom* (lotteries tend high-X) not the *cause* (lotteries are unresolved); c18 proves symptom/cause come apart (high-X, fully resolved, not a lottery). Favorite-ballast bug (#1) disappears — c84–c92 were only failing the fractional-range veto, never occ·cond (0.88–1.00).
- **Doctrine restated (a):** the cheap engine fires its **lowest resolved edge, which is high precisely because cheap contracts that move at all move far** — c18 firing +53 on 18¢ is ~290% gross capture = the literal "8% capital / 38% profit, deep bounces" mechanism, NOT a small-bank story. Same rule (lowest resolved mode), two shapes (bank for cells with a resolved low mode; reach for cells whose lowest resolved mode just is high).

## Diff 2 — FLOOR is PRINCIPLED and engine-start is ROBUST (not reverse-engineered)
Census of cheapest-firing cent vs FLOOR:

| FLOOR | nfire | cheapest firing | cheap-zone (≤20) firing |
|---|---|---|---|
| 0.40 | 57 | c5 | 5,11,12,14,15,16,18,19,20 |
| **0.45** | 50 | **c11** | 11,12,14,15,16,18,19 |
| **0.50** | 43 | **c11** | 11,14,15,16,18,19 |
| **0.55** | 36 | **c11** | 11,14,15,16,18,19 |

**Engine-start = c11 for EVERY floor in [0.45, 0.55].** It is NOT a knife-edge artifact of choosing 0.45 — it falls out of the entire "more-likely-than-not" region. **Principled line: occ·cond ≥ 0.50** = "a majority of resamples both visit the cluster AND pin its center" = literally more-likely-than-not resolved. The [0.40,0.50] band is dense (14 modes), so 0.45 sits *inside* ambiguity; **0.50 is the defensible cut and lands the same c11.** → Move FLOOR 0.45 → 0.50 (principled, same engine-start, removes the one un-derived knob).

## Diff 1 — the Sharpe conjunct is REJECTED: it does not separate engine from lottery; it ranks the lottery HIGHER

Per-N fired-payoff risk metrics (weighted):

| cell | firedX | occ·cond | EV | disp | **Sharpe** | P(loss) | hit% | class |
|---|---|---|---|---|---|---|---|---|
| 18 | 53 | 0.56 | 5.54 | 33.4 | **0.166** | 0.67 | 33 | engine reach |
| 19 | 52 | 0.58 | 6.11 | 34.0 | 0.180 | 0.65 | 35 | engine reach |
| 21 | 47 | 0.51 | 5.78 | 33.2 | 0.174 | 0.61 | 39 | engine reach |
| 11 | 18 | 0.57 | 3.44 | 14.5 | 0.237 | 0.50 | 50 | engine bank |
| 16 | 11 | 0.79 | 2.85 | 12.4 | 0.230 | 0.30 | 70 | engine bank |
| 84 | 8 | 0.93 | 0.23 | 25.6 | 0.009 | 0.08 | 92 | ballast |
| 92 | 2 | 1.00 | 1.49 | 6.9 | 0.216 | 0.01 | 99 | ballast |
| **5 (forced)** | 40 | 0.28 | 4.54 | 18.4 | **0.247** | 0.79 | 21 | LOTTERY |
| 6 (forced) | 37 | 0.34 | 3.55 | 17.9 | 0.199 | 0.78 | 22 | LOTTERY |
| 7 (forced) | 59 | 0.10 | 5.87 | 26.2 | 0.224 | 0.81 | 20 | LOTTERY |

**The forced c5 +40 lottery has Sharpe 0.247 — HIGHER than c18's 0.166 and higher than every Class-3 engine reach.** A Sharpe floor that admits the engine admits the lotteries; one that excludes the lotteries (>0.25) excludes nearly the whole engine. **Sharpe is the wrong axis** — it rewards the lottery's tight EV concentration (+40/−5 spreads less than c18's +53/−18). It is the X-veto's mistake one level over: a confound, not the cause.

**The cause is occ·cond, and the lotteries are ALREADY dead on it** (c5 +40 = 0.28 < 0.50). The forced-lottery rows are counterfactuals that can never fire. So the firewall does NOT need a Sharpe conjunct — adding one would *break* it (it'd admit the lottery and kill the engine).

## The REAL question Diff 1 surfaces (for Opus — the next argument)
Sharpe is dead, but it revealed that **Class-3 high-reach-only cells (c18/19/21) are the WEAKEST resolved cells**: P(loss) 0.61–0.67, hit 33–39%, Sharpe ~0.17. They pass resolvability honestly but they lose ~2/3 of the time. The doctrine says fire the lowest resolved mode — and these qualify — but are they the engine or its marginal edge?

Note the separating axis is **hit-rate / P(loss)**, NOT Sharpe: lotteries hit 20–22% (P(loss) ~0.8), c18/19/21 hit 33–39% (P(loss) ~0.65), deeper engine c59/66 hit 71–74% (P(loss) ~0.27). But **paid(X)=1−hit^KP and supp already encode hit-rate in the EV/paid/supp gate** — so a low-hit reach is already damped there. The open question: is the existing paid/supp damping sufficient to make c18/19/21 fire only when genuinely worth it, or do we want an explicit hit-rate / max-P(loss) floor as the load-bearing conjunct (NOT Sharpe)? My read: paid/supp already does this and c18/19/21 firing with EV>hold after paid/supp damping IS the honest engine edge — but I flag them as the marginal members, not co-signed.

## Status
- Veto dropped ✅. FLOOR → 0.50 (principled, robust c11 engine-start). Sharpe conjunct REJECTED (confound; would admit lottery, kill engine).
- The honest firewall = occ·cond≥0.50 (epistemic) + EV/paid/supp (tradeability, hit-rate already inside). Lowest resolved mode fires.
- Open for Opus: (1) confirm Sharpe is correctly rejected and we do NOT add a risk-adjusted conjunct; (2) are c18/19/21 (P(loss) 0.65) the engine or its margin — is paid/supp's existing hit-rate damping the right and sufficient gate, or do we want an explicit max-P(loss) floor? NOT locked pending this.
