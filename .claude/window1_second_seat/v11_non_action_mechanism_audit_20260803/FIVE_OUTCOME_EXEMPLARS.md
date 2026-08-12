# The five-outcome exemplar set — named checks for the referee build [ANALYTICAL_ESTIMATE]

Analysis seat only. Read-only. Brain: **V49b staged ledger** (operator-cited `47b51fd2`; carries the
393-ledger caveat per the synthesis fold `d6399035`). Pool: PAR_SHEET @ `b7f12d6f` states/deltas ×
DECISION_AUDIT @ `35ac1f5b` verdicts. Forward truth = the `12d67c8a` method (+30/60/90-min mid path, ±2¢,
majority). **Read provenance, doctrine-1 labeled:** the staged ledger stores classifier COUNTS only, so reads
at join/fill/terminal are machine anchors; every other read (and every sibling read at a shared receipt) is a
**tape-derived trailing-300s proxy — a reconstruction.** Vocabulary per order: "case" = outcome type; "cell"
appears only as an entry price. Machine artifact with full moment grids: `FIVE_OUTCOME_EXEMPLARS.json`.

**Fill-class fingerprint (doctrine 4):** all six credited legs across the five games carry
`MARKET_TRADE_TRUTH_AT_OR_BELOW_STANDING_REST` — the sole class in V49b's allowed set. Check TRUE.

**Selection criteria, stated:** machine records only; exact bell preferred (4 of 5 are exact); prints present
both legs; then the case-defining extremum — largest complete delta (1), thinnest positive delta with a
decomposable per-leg gap (2), fill within 1¢ of own low + sibling WRONG_READ, largest par delta (3), largest
paid-up on a forward-wrong filled read (4), largest offered-NEITHER menu (5). CASE 5's only real menu
(27¢) is schedule_only-belled — caveat named below; the exact-bell alternatives offer ≤2¢ menus.

Moment-row format throughout: **moment @ min-into-window · own read (source) · sibling read (proxy) + sibling
machine anchor · action · book (bid,ask) · next print · forward · verdict.**

---

## CASE 1 — deepest discount: `26JUL16MERDRO` (ATP_MAIN, exact). Pair 6+6=12¢, Δ88. **Beats incumbent ARNROM (Δ6) — replaced.**

| leg | moment | @min | own read | sib read/anchor | action | book | next print | fwd | verdict |
|---|---|--:|---|---|---|---|---|---|---|
| MER | join_arm | 20.9 | RISING (machine) | SETTLED / pre-arm | arm join | (6,93) | 163s→93×8.9 | up | **EARNED** |
| MER | fill | 24.5 | FALLING (machine) | SETTLED / pre-arm | CREDITED @6 | (6,94) | 383s→93×14 | up | lucky |
| DRO | join_arm | 30.9 | RISING (machine) | SETTLED / MER credited | arm join | (6,94) | 183s→93×1 | down | lucky |
| DRO | fill | 35.6 | FALLING (machine) | RISING / MER credited | CREDITED @6 | (6,92) | 801s→60×4.9 | down | **EARNED** |

Both legs: entry 6 = own low 6, **gap 0 — filled at the floor, both sides.** How intentional: **half-earned,
half-ambient.** Two of the four gradeable machine moments match forward truth (MER's arm, DRO's fill); the
other two are credited-on-a-contrary-read. The deeper truth is in the books: both sides opened ~(6,94) — the
12¢ pair was **on the menu from the open** (menu moment 30.9 min, mid-sums pinned at 99–101 throughout). The
OS's contribution was standing at the bid-join on both sides of an ambient gift and staying in the book until
the crossing sweeps came. Intentionality: presence, not prediction.

## CASE 2 — thin complete: `26JUL12POLKUH` (ATP_CHALL, exact). Pair 18+81=99, Δ1; lows 15+80 → 4¢ left.

| leg | moment | @min | own read | sib read/anchor | action | book | next print | fwd | verdict |
|---|---|--:|---|---|---|---|---|---|---|
| POL | first_withhold | 7.3 | RISING (proxy) | FALLING / pre-arm | WITHHOLD (S12) | (74,84) | 236s→83×1 | flat | earned |
| POL | join_arm | 694.1 | RISING (machine) | SETTLED / pre-arm | arm join | (81,82) | 598s→80×18.7 | flat | earned |
| POL | fill | 704.0 | RISING (machine) | SETTLED / pre-arm | CREDITED @81 | (81,82) | 1584s→82×3 | flat | **EARNED** |
| KUH | join_arm | 793.2 | RISING (machine) | SETTLED / POL credited | arm join | (18,20) | **819s→15×72** | up | **EARNED** |
| KUH | fill | 806.9 | RISING (machine) | SETTLED / POL credited | CREDITED @18 | (18,20) | **5s→16×75** | up | **EARNED** |

Where was the better price left — the decomposition the case asked for: **neither "arrived late," "stood
elsewhere," nor "never approached." Both legs were front-of-sweep fills.** KUH filled at 18 and the *same
sweep* printed 16×75 five seconds later, then 15×72 within 14 minutes; POL filled at 81 and 80×18.7 printed
inside 10 minutes. The 4¢ sat 5–800 seconds *behind* our fills, inside the flow that consumed us. Every read
is EARNED — this is the one loss channel no read or level fixes at replay grain: position within the sweep
(the §6 presence-premium bin, measured here at 4¢ on a 99¢ pair).

## CASE 3 — one cheap fill, one miss: `26JUL19ARSMAR` (ATP_CHALL, exact). MAR credited 60 (low 59, gap 1); ARS unfilled, rest 39 vs low 35 @275 min.

| leg | moment | @min | own read | sib read/anchor | action | book | next print | fwd | verdict |
|---|---|--:|---|---|---|---|---|---|---|
| ARS | first_withhold | 230.5 | FALLING (proxy) | RISING / pre-arm | **WITHHOLD (S12)** | **(29,39)** | 8s→39×1 | flat | earned |
| ARS | *(own low 35 prints @275.2 — no rest standing; guard span covers it)* | | | | | | | | |
| ARS | join_arm | 700.1 | RISING (machine) | SETTLED / MAR credited | arm join | (38,40) | 754s→41×10.4 | up | earned |
| ARS | terminal_edge | 709.4 | FALLING (machine) | SETTLED / MAR credited | REST_AT_EDGE @39 | (38,41) | 194s→41 | up | **WRONG** |
| MAR | join_arm | 667.9 | RISING (machine) | SETTLED / pre-arm | arm join | (60,61) | 471s→60×23 | down | lucky |
| MAR | fill | 675.7 | FALLING (machine) | SETTLED / pre-arm | CREDITED @60 | (60,61) | 1094s→59×1 | down | **EARNED** |

Same game, same process — why did A read right and B read wrong: **the reads never actually diverged.** At the
shared withhold receipt (230.5 min) the pair read coherent-inverse (ARS FALLING / MAR RISING) — correct on
both tapes. The fork is a **permission**, not a read: ARS's 10¢-wide book had S12 withholding from 230.5 min,
and ARS's own low (35) printed at 275.2 min into that withhold span with **no rest standing**. By the time the
join armed (700 min) the price had risen to 38–40 and the leg died at the edge holding a stale FALLING read —
the WRONG_READ grade lands on the *terminal* anchor, but the mechanism was S12 sitting on the leg during its
only dip. The two books first stopped summing to ~100 at **54.5 min** (mid-sum 105, sustained) — the pair
constraint had already flagged this game as mutually-overpriced hours before the fork; nothing consumed it.

## CASE 4 — premium fill on a wrong read: `26JUL13SANDAN` (ATP_MAIN, exact). SAN credited 31 vs low 22 (paid up 9); DAN unfilled, rest 68 vs low 69.

| leg | moment | @min | own read | sib read/anchor | action | book | next print | fwd | verdict |
|---|---|--:|---|---|---|---|---|---|---|
| SAN | first_withhold | 157.6 | **FALLING (proxy)** | **RISING / pre-arm** | WITHHOLD (S12) | (32,42) | 2198s→31×12 | down | earned |
| SAN | join_arm | 188.2 | **RISING (machine)** | RISING (proxy) / pre-arm | arm join | (31,33) | 365s→31×12 | **down** | **WRONG** |
| SAN | fill | 194.2 | RISING (machine) | SETTLED / pre-arm | CREDITED @31 | (30,32) | 3754s→31×10 | flat | earned |
| DAN | first_withhold | 157.6 | RISING (proxy) | FALLING / pre-arm | WITHHOLD (S12) | (58,68) | 2720s→70×1.4 | up | earned |
| DAN | join_arm | 1082.2 | RISING (machine) | SETTLED / SAN credited | arm join | (75,76) | 1077s→76×1.3 | flat | earned |
| DAN | terminal_edge | 1198.5 | RISING (machine) | SETTLED / SAN credited | **REST_AT_EDGE @68 = pair cap** | (75,76) | 8s→76×18 | up | earned |

The dual misread, and what in hand contradicted it: thirty minutes **before** SAN's arm, the machine's own
tape read SAN FALLING (157.6 min proxy) and the **sibling read RISING at the same receipt** — under the pair
constraint a rising DAN *implies* a falling SAN. Two independent in-hand signals said "don't arm SAN rising";
S3 consumed neither (the unconsumed `disagreement` flag, again). It armed RISING at 188.2 into a falling
market, was credited at 31 six minutes later, and SAN traded down to 22 by 820 min. **The 9¢ premium then
killed the other leg arithmetically: cap = 99−31 = 68, and DAN's market never traded below 69.** Filled at
SAN's evidence floor (~22–24), the cap would have sat ≥75 and DAN's 69-flow completes the pair. The a20e1a85
sealed richness mechanism, caught live in dev, 1¢ short.

## CASE 5 — offered game, nothing filled: `26JUL14PUTJEA` (WTA_MAIN, **schedule_only — bell caveat: window edges inferred; the menu prints at 89/320 min are deep inside the span, so the finding does not hinge on the boundary**). Par 9+64=73 — a 27¢ win on the tape; we placed and finished with nothing.

| leg | moment | @min | own read | sib read/anchor | action | book | next print | fwd | verdict |
|---|---|--:|---|---|---|---|---|---|---|
| PUT | *(own low 9×1 prints @89.1 — join not yet armed; no rest at level)* | | | | | | | | |
| PUT | first_withhold | 115.1 | RISING (proxy) | SETTLED / pre-arm | WITHHOLD (S12) | (28,80) | 1861s→80×1.3 | flat | earned |
| PUT | join_arm | 442.4 | RISING (machine) | SETTLED / pre-arm | arm join | **(46,82), mid-sum 113** | none | **down** | **WRONG** |
| PUT | terminal_edge | 1504.1 | SETTLED (machine) | SETTLED / JEA armed | REST_AT_EDGE @22 | (46,53) | none | flat | earned |
| JEA | first_withhold | 272.0 | RISING (proxy) | SETTLED / pre-arm | WITHHOLD (S12) | (64,80), **mid-sum 123** | 2891s→64×1 | down | **WRONG** |
| JEA | *(own low 64 prints @320.2 — rest anchored ~18–22, 46¢ below)* | | | | | | | | |
| JEA | join_arm | 445.2 | RISING (machine) | FALLING / PUT armed | arm join | (21,77) | none | flat | earned |
| JEA | terminal_edge | 1504.1 | FALLING (machine) | SETTLED / PUT armed | REST_AT_EDGE @18 | (19,80) | none | flat | earned |

What the machine saw, decided, and stood at: two grotesquely wide books (spreads 16–52¢; mid-sums 101→123 —
mutually overpriced asks all day), guard withholds on both legs early, joins armed at 442/445 min on RISING
reads. What it never consulted: **its own trade tape.** PUT printed **9** at 89 min (before PUT's arm — the
S17-class arrive-after-the-low, mid-window); JEA printed **64** at 320 min while JEA's bid-anchored rest sat
at ~18–22 — **46¢ below the only floor JEA's flow ever offered**. The menu (9+64=73) was fully printed by
320 min; the machine's ledger even *recorded* it (`prior_true_trade_low_cents` is a machine field) and no
organ reads it. Clueless is precise: it watched bids, and this game's truth lived only in trades.

---

## THE CROSS TABLE — five games at their divergence moments

Divergence moment = first receipt where the two legs' **running true-trade lows sum < 100** (the menu
opening), machine-computable at every receipt from fields the ledger already carries.

| | menu @min | consumed | ignored | outcome |
|---|--:|---|---|---|
| C1 MERDRO | 30.9 | bid-join levels (both) | forward reads (contrary at 2 of 4 moments — didn't matter) | Δ88 — stood at both floors when the sweeps came |
| C2 POLKUH | 788.7 | join levels, S12 once (harmless) | nothing material | Δ1+4¢ behind the sweep — queue position, replay-invisible |
| C3 ARSMAR | 537.7 | MAR's join; S12 on ARS | ARS's own 35-low printed inside the withhold span; mid-sum 105 decoupling @54.5 | pair lost 6¢ to a permission sitting on the dip |
| C4 SANDAN | 318.0 | SAN's RISING arm | own 30-min-prior FALLING proxy; sibling's simultaneous RISING (pair-implied SAN falling); cap arithmetic 99−31=68 < 69 | 9¢ premium + pair killed by 1¢ |
| C5 PUTJEA | 320.2 | bids (anchored 18–22 vs 64-flow), RISING arms into down/flat | **`prior_true_trade_low_cents` on both legs** — the 9 and the 64 were recorded and unread; mid-sum 123 | 27¢ menu, nothing filled |

## THE SINGLE RULE — one question, one answer

**What separates the five: whether a lawful rest was standing at the leg's own running true-trade floor at
the receipts where the pair's running lows summed under 100.** Cases 1 and 2 pass — rests stood at the
trade-defined floor when the menu was open (case 2's residue is queue position, outside replay). Case 3 fails
it by permission (S12 held the rest off during the only dip), case 4 by arithmetic (a wrong-read premium set
the cap 1¢ under the sibling's floor), case 5 by anchor (rests keyed to bids 13–46¢ away from where trades
actually printed, arms landing after the lows).

**What already-in-hand information it consults — nothing new:** `prior_true_trade_low_cents` (own and
sibling — both are existing ledger fields recorded at every receipt), the pair-sum of those two lows, and the
cap arithmetic. The rule, stated generally: *while running-low(A) + running-low(B) < 100, each leg's rest
stands at-or-above its own running low, and no permission or cap organ may hold it out of the book at those
receipts.* This is the referee's check, and it is the presence-continuity organ (synthesis §7) stated as a
per-receipt invariant.

**Referee build bindings (named checks, never tuning targets):** `26JUL19ARSMAR`, `26JUL13SANDAN`,
`26JUL14PUTJEA` must improve; `26JUL16MERDRO`, `26JUL12POLKUH` must not degrade.

## Conservation

5 games / 10 legs / 6 credited (fingerprint TRUE, one class); every moment row carries source (machine vs
tape_proxy_300s reconstruction); menu + decoupling moments per game in the JSON. Sources: V49b staged ledger,
dev tapes (10/10 loaded), fit-local prints. ANALYTICAL_ESTIMATE.
