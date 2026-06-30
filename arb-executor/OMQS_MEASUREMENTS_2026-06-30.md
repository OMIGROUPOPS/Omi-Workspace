# OMQS MEASUREMENTS — 2026-06-30 (M1 distortion gate, M2 gun-cancel overlay)

Source: authoritative Kalshi REST (settlements/fills) + fv_burst_anchor from the order-event logs (live_v3_2026062[4-9].jsonl, 20260630.jsonl) + Kalshi /markets/trades tick-tape. All $ in dollars, prices in cents (yes terms), 5-lot sizing. Read-only measurements — NOT builds. The flag-bisect (restart 15:46:04 ET) runs untouched.

---

## M1 — DISTORTION GATE CALIBRATION

Candidate gate: **do not fill if `entry_price > fv_mid + X`** (fv_mid at fill). Net = losses_blocked − wins_blocked, where losses_blocked = summed loss of gated legs that settled negative (avoided), wins_blocked = summed profit of gated legs that settled positive (forfeited). Uses realized per-leg settlement P&L.

### Full-week X-sweep — 756 settled fv_burst legs, Jun 24–30

| X | gated | losses_blocked | wins_blocked | NET |
|---:|---:|---:|---:|---:|
| 0 | 326 | +$216.22 | +$121.22 | +$95.01 |
| **2** | **231** | **+$182.20** | **+$84.05** | **+$98.15  ← best** |
| 3 | 194 | +$161.91 | +$64.10 | +$97.81 |
| 5 | 146 | +$119.89 | +$47.17 | +$72.72 |
| 8 | 112 | +$97.19 | +$35.09 | +$62.10 |
| 10 | 90 | +$87.72 | +$26.10 | +$61.63 |

**Best X = 2** (NET +$98.15/week), on a flat X=2–3 plateau (~+$98). At X=2: gates **231 of 326 distortion legs (71%)**; distortion (entry > fv_mid) = **43% of all fills**, so X=2 blocks ~31% of all fills.
(Today-only optimum was X=0 at +$27.22; X=0 over-gates the green days, so the week favors X=2.)

### Per-day robustness — NET$ by X

| date | n | X0 | X2 | X3 | X5 | X8 | X10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-06-24 | 181 | +46.2 | +41.9 | +38.4 | +30.9 | +27.2 | +24.7 |
| 2026-06-26 | 39 | -3.0 | -2.5 | -2.0 | -1.1 | -1.1 | -0.7 |
| 2026-06-27 | 54 | -1.6 | -1.0 | -2.4 | -1.5 | -0.3 | -0.3 |
| 2026-06-28 | 118 | +4.2 | +7.8 | +7.0 | +6.0 | +3.2 | +3.6 |
| 2026-06-29 | 248 | +38.3 | +39.6 | +44.4 | +39.2 | +33.9 | +34.1 |
| 2026-06-30 | 113 | +10.9 | +12.4 | +12.3 | -0.7 | -0.7 | +0.2 |

(Jun 25 omitted: n≈3 settled legs, net $0.) Gate is strongly +EV on the bleed/high-volume days (Jun 24 +$42, Jun 29 +$40, Jun 30 +$12) and only marginally −EV on the quiet green days (Jun 26 −$2.5, Jun 27 −$1.0). X=2–3 is robust; X=0 too aggressive on green days; X≥5 leaves money on the table.

### BUILD CAVEAT (verbatim — must verify before shipping)

M1 used `fv_mid` as stamped at the volume-burst **ONSET (the gun)**, which occurs **hours after** a premarket fill. The live gate needs fair value computable at **FILL-CONFIRM time (premarket)**. Whether a usable premarket fv exists at the fill instant is **UNCONFIRMED** — `fv_mid`-at-burst is hindsight. The gate's real-time input (e.g. the A43 fv-predictor, AUC 0.73) must be available at the fill instant, not just at burst. Confirm this before building the gate.

---

## M2 — GUN-CANCEL NET-DOLLAR OVERLAY

81 flow-through cancels (Track 2a: v4_t20m_fallback entry-bid cancels where the tape later traded at/through our bid). 69 had a settled outcome: **43 would-win, 26 would-lose.** Sibling-filled subset: n=64.

### Two models, side by side

| model | sum positive | sum negative | NET | sibling-filled subset |
|---|---:|---:|---:|---:|
| ride-to-settle (BOUND, illusion) | +$85.40 | −$49.95 | **+$35.45** | +$39.90 |
| **band-capped (REALISTIC policy)** | **+$25.32** | **−$49.95** | **−$24.62** | **−$20.18** |

### Methodology correction

Under the **actual fill+band exit policy**: a winner exits at **+band (≈$0.35–0.95/leg, capped)**, a loser **rides to −bid (full)**. The ride-to-settle model (+$35) credits winners the full +(100−P) ride — an illusion the policy never realizes. Band-capping the wins flips the net:

- **NET = −$24.62** (sibling-filled subset −$20.18).
- I.e. **had we filled those 81 bids, we would have LOST ~$25** under the current exit.
- **The stale-buffer gun-cancel is currently PROTECTIVE, not costly.** It inadvertently dodges fills that feed the asymmetric exit.

This **contradicts the prior +$20–40 prediction**: the sibling-filled "missed completions" are net **−$20**, not positive, because they feed the same asymmetric exit.

---

## REORDERING THIS FORCES

- **Distortion gate (M1) = the real +EV lever: +$98/week at X=2.** Works by pre-emptively blocking the legs destined to ride to 0. Rank 1 confirmed.
- **Gun-detection (M2) is below Rank 2 — currently protective.** Fixing it (filling more) is ~−$25/day while the exit stays asymmetric. Do NOT build the gun-fix until the exit is fixed.
- Both trace to the same asymmetric exit; the gate captures the benefit on the entry side without touching the exit. Build target: distortion gate at X=2, pending the fill-confirm fv-availability check.
