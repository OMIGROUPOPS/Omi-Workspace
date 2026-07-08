# POST-FILL MOVE QUOTE — divot vs reprice, per fill (2026-07-08 preflight-adjacent; read-only, freeze intact)

**Cohort:** honest-era W1-filled legs from the evening ledger (n=276 with tape) + tonight's 12 by name. Tick tape (top-of-book), post-fill windows. **Classifier (operator's distinction):** DIVOT = bid dips below fill but best ask holds within 2¢ of pre-fill AND bid recovers ≥ fill within 30 min (flow event; book snapped back). REPRICE = best ask follows down ≥3¢ AND mid stays below fill at +30 min (the leg's value moved through us). NO_UNDERCUT = bid never drops below fill in +60m. AMBIG = mixed signature (named honestly; the classifier is strict — 40-45% land here). Producer `/root/post_fill_move.py`, raw `/root/post_fill_move.json`.

## 1 · TIME TO UNDERCUT

The undercut, when it comes, comes **immediately: median 0.1–0.3 min in ITF/CHALL** (mains 4.5–5.9, tiny n). We are filled at the local top of the move almost by construction — the fill IS the flow event's leading edge. Depth curves per leg in the raw json; tonight's named table below carries the 5/15/30/60 marks.

## 2 · THE SPLIT (era, per cat)

| cat | n | DIVOT | REPRICE | NO_UNDERCUT | AMBIG | undercut med (min) |
|---|---|---|---|---|---|---|
| ITF_M | 90 | 13 | 24 | 13 | 40 | 0.2 |
| ITF_W | 74 | 8 | **31** | 7 | 28 | 0.1 |
| ATP_CHALL | 76 | 10 | **27** | 8 | 31 | 0.2 |
| WTA_CHALL | 24 | 1 | 3 | 8 | 12 | 0.3 |
| ATP_MAIN | 6 | 2 | 0 | 0 | 4 | 4.5 |
| WTA_MAIN | 6 | 1 | 0 | 0 | 5 | 5.9 |

**Tonight's 12 by name:** REPRICE — NAKSHI-NAK (40, undercut +25.8m), OKIMAT-OKI (53, +43m), YAMNAK-YAM (90, instant), CHOCAO-CAO (49, instant), WEISUN-WEI (79, instant, −13¢ at +60m), TUPPAN-PAN (14, instant, −11¢ held). DIVOT — GURKAL-KAL (65, 1¢ dip, snapped), WEISUN-SUN (18, 1¢ dip, snapped). NO_UNDERCUT — LOMTOM-TOM (62), NASLEE-LEE (25). AMBIG — NAKSHI-SHI (57), BORZEN-ZEN (42). *(Overnight caveat: several matches now in-play; "band touched" below uses all prints post-fill.)*

## 3 · W1 CONSEQUENCE PER CLASS — the wound's cost, stated

| cat | band touched \| DIVOT | \| REPRICE | \| NO_UNDERCUT |
|---|---|---|---|
| ITF_M | **9/13 (69%)** | **6/24 (25%)** | 3/13 (23%) |
| ITF_W | 4/8 (50%) | 11/31 (35%) | **6/7 (86%)** |
| ATP_CHALL | 3/8 (38%) | **5/27 (19%)** | 1/8 (13%) |

- **REPRICE → band-unreachable ~65–81%** (ITF_M 75%, ATP_CHALL 81% never touch): the no-bueno class quantified — when the ask follows the bid down, the exit band mostly never prints again pregame. Tonight: 5 of 6 reprice legs untouched.
- **DIVOT confirms the gold pattern**: band touched at 2–3× the reprice rate (ITF_M 69% vs 25%); tonight WEISUN-SUN dipped 1¢, snapped back, and CASHED at 23 within the hour.
- ITF_W's quiet anomaly: **NO_UNDERCUT legs touch their band 86%** — the strongest class of all is the fill that never gets undercut; strength at the fill is band predictive.

## 4 · THE ROLL-UP LINE (the aim build inherits this)

Of decisively-classified fills (DIVOT+REPRICE+NO_UNDERCUT): **divot share = ITF_M 26% / ITF_W 17% / ATP_CHALL 22%; reprice share = ITF_M 48% / ITF_W 67% / ATP_CHALL 60%.**

**Our fills are predominantly standing in front of reprices, not catching divots — in ITF_W two-thirds of decisive fills are the market moving through us.** The dip quantile must target the DIVOT class (flow events with intact asks), and the classifier gives the aim build its selector shape: an aim that fills while the ask holds is buying flow; an aim that fills as the ask follows is fading real information. Where a cat's fills skew REPRICE (ITF_W, ATP_CHALL), deepening the dip alone buys MORE reprices cheaper — the conditioning variable (ask-hold / sibling-tape state, per §3 seesaw: the sibling's print IS the leg's move) matters more than the depth. Feeds AIM_V2's dip-admissibility conditioning at the arm request; the joint-shadow's ex-self fields already log the chain state every decision.

*(AMBIG 40-45% stated: strict thresholds; the class is refinable with the same tape when the aim build wants it. Mains n≤6 — no read.)*
