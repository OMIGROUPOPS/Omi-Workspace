# OWN-GAME AUTHOR COUNTER-GRADE — @ec23ad2e

License: LAW_INDEX read @ec23ad2e, sha256 41784e6a… (verified this seat).
Build: `v54: condition author on own game and bank bed stop`.
Package: `stage1_store/v54_author_reads_own_game_20260825/`.
Method: four independent lanes, each recomputing from the custodied trace (810 DECISION_STAGE +
6,635 REARM_ATTEMPT + 5 FILL_EVENT; 1,276 derivations), prints.jsonl, raw tick tapes, and
`git show ec23ad2e:` code. Filed: F-VS-219 … F-VS-222.

Ledger compliance first: FINDINGS_V53.md carries **zero** F-VS rows — all re-designated
BC-001..BC-041; my ledger untouched. The F-VS-215 ruling was honored. Filings resume at 219.

---

## 1 — Verification: the claims hold; the serialization is honest (F-VS-219)

- **Sentence == derivation == recomputation, 1,276/1,276.** Every row carries
  `AUTHOR_CHAIN=PRIOR_x_TO_CONDITIONED_y_TO_LEVEL_z`; the parsed triple matches the structured
  chain on all 1,276; the panel prior reproduces as the weighted q50 of the serialized votes on
  1,276/1,276; the conditioned level reproduces as the own-evidence median on all 1,114
  conditioned rows; on all 73 priced orders, action == sentence == authority (0 substitutions).
- **214 suppressed panel moves — exact** (recounted; all HOLD-only; all 59 REPRICEs + 14 PLACEs
  carry `conditioning_changed: true`). Label caveat: all 214 sit on the conditioned path, where
  the prior has no arithmetic influence anyway (§2).
- **BAR's 25→27 self-correction — real, and the build's one clean win of the class.**
  ln41 REPRICE 26 (bid 26) · ln42 REPRICE 25 (bid 25) — bid-following down — then
  **ln43 REPRICE 25→27 at ts 1783841801.304, on the first 27 print's own receipt (2898debe…),
  with the bid still 25**: an own-evidence correction, 0.113 s before the fill print (4fa381b8).
  Entry == rest == 27, the exact floor.
- **Fills: five, all resolve by trade id, entry == rest** (BAR 27 · GIU 69 · URS 58 on the 57
  floor print · PAL 40 · LAJ 54 — the d837b992 set minus SVA). FILL_HANDOFF lists exactly these.
- **Determinism X2 byte-identical** on all four games; stage/rearm/fill counts reconcile exactly.
- **Cancels/rearms reconcile:** 4 crossed rests cancelled by the new continuous post-only
  (receipt-for-receipt vs CONTINUOUS_POST_ONLY_RECEIPT), 6 rearm restores pair 1:1 with cancels;
  GIU's one unresolved rearm was DISAGREES-blocked 8,169 s and re-entered by a fresh authority
  placement (the 69). Zero crossed rests held; zero post-span DANPRA rows (last ts == span_end
  1784372160 exactly).

---

## 2 — The mechanism: "conditioning" is replacement, and the book-follower returns a fourth time — with honest paperwork (F-VS-220)

`dual_belief_os.js` @ec23ad2e: the conditioned level is
`ownEvidenceCentral ?? engineTarget` (:314-318) over evidence rows
{OBSERVED_TRUE_TRADE_LOW, **CAUSAL_LIVE_BOOK_BID**, SPREAD_EYE_CLEARING} (:306-313).
The `??` deletes the panel prior the moment any evidence row exists — and the live bid exists
whenever a book does. Measured: of 32 orders priced at the bid, **30 had the bid as the ONLY
evidence row** (the "conditioned" level IS the bid verbatim); 66 of 73 priced orders were
licensed by nothing but a book change; two-row medians are `Math.round(mean)`, half-up. The
suppression guard cannot restrain it: bid ticks are conditioning changes (:340-354).

This is the F-VS-147/202/211 book-follower class, **fourth appearance**, now living inside the
"one author" itself — with one real difference: the serialization is honest. The chain openly
prints prior→bid→bid; nothing is misstamped. The panel survives only while there is no book;
own-tape evidence enters only as a backward running min, which is ≥ the eventual floor at every
pre-floor moment. What the order asked — "where own-tape conditioning should outrank the panel
and doesn't" — inverts: own-game conditioning ALWAYS outranks the panel; the defect is that
two of its three channels are touch measures.

---

## 3 — The residuals, rows, street per cent (F-VS-221)

**(a) LAJ 54 vs 51 — 3¢ DATA-GAP; the latency question answers to zero.**
Every consumption of arrived evidence was instant: the 62 print consumed at its own receipt
(0.000 s); the 54-cluster @1784036624.370 consumed by rearm attempt #1592 ON the print receipt
(0.000 s); the PLACE 54 came 17.630 s later at ln4171 — the entire latency is the exchange's own
book re-quote (ask 54→55 only at 1784036642; a 54 rest was unpostable before it). The fill @54
came 14,331 s later; the first sub-54 evidence (53 print) arrived **+1,857.294 s after the fill**,
the 51 floor print **+9,150.157 s after** — consumption latency for the 51: infinite, because the
harness drops credited legs (zero LAJ rows post-fill). Street: 0¢ MISREAD, 0¢ UNCONSUMED,
**3¢ DATA-GAP**. Bonus fact: the crossed-rest cancel at ln4165 SAVED 7¢ — a standing 61 would
have filled at 61 on the .370 cluster; the 19,283 s no-rest gap cost 0¢ (exactly 9 prints passed,
all in that cluster).

**(b) SVA — floor-exact 41 rest, NOT filled: the whole leg lost by one receipt.**
The 41 level was derived from the FIRST 41 print @1784020201.830 with 0.000 s consumption —
blocked then only by postability (41 == ask 41). At the int-1784020209 book receipt the tape
already showed bid 41 / ask 42 — postability present and demonstrably consumed
(`belief_receipt row-355`) — and the author held 40. The move came at **1784020209.484, on the
last 41 print's own receipt**: under the fill law (prints tested against the rest standing before
same-instant evaluation) the fill-eligible window on 41 closed at the exact receipt where it
opened. Zero ≤41 prints in the remaining 58,190.516 s; the rest stood floor-exact and dead.
d837b992 acted on the int-209 receipt and was filled at 41 by the .484 prints. Street:
**DATA-UNCONSUMED** — the fatal margin was strictly less than 0.484 s of receipt ordering.

**(c) GIU 69 vs 66 — the conditioning consumed the touch and annihilated its own downside math.**
ln45 PLACE 69 (bid 69; own-tape 69 prints licensed the level; spread-eye clearing 70 the third
row). On the same row: panel prior 64, JUSHEI's licensed floor **66** (w 0.755), modal depth
histogram floor **67** (mass 48), remaining-dip q25 = 2 (69−2 = 67) — all consumed into
`engineTarget` and deleted by the `??`. Street: 69→68 **WRONG DATA CONSUMED** (bid + clearing
inside the evidence median); 68→67 **RIGHT DATA UNCONSUMED** (dip q25, modal floor 67 on the
row); 67→66 **RIGHT DATA UNCONSUMED** (weak — 66 existed as vote + histogram mass inside a median
outputting 64); the exact identity "66" is future-print data. Post-fill, GIU derivations are
EMPTY (ln72–208): the machine stops reading its own game once credited — the 67/66 prints were
never read at all.

**(d) URS 1¢ + PAL 1¢ (Δ2 vs required Δ4).**
URS: placed AT 57 at span start (a bid echo, not floor knowledge), bid-chased to 63, and in the
endgame **provably re-derived and held 57** with the 58-print evidence in hand (ln909–947,
1784028664–1784030288). It left 57 at **ln958 @1784031271 on a 1¢ bid uptick**: two-row median
(57, 58) = round(57.5) = 58 by half-up rounding — 1,426.6 s before the floor print filled it at
58. Tenure can't hold the 57: the exact-floor tenure protects only `active == tape-min` (58) —
anchored to a level class that is ≥ floor by construction. Street: **WRONG DATA CONSUMED** (the
bid row inside the median, plus the rounding). PAL: lifted 35→40 at ln551 with **bid 37** — the
opening-burst print 40 and clearing 41 outvoted the bid in the median (chain 38→40→40); filled
40, 68.61 s before the only receipt ever naming 39. Street: **WRONG DATA CONSUMED** for the
stand; the exact "39" was DATA THAT NEVER EXISTED at any decision time.

---

## 4 — DANPRA: the inversion, and a law-level contradiction (F-VS-222)

The own-game conditioning finally derived **both** true floors at their floor prints:
DAN chain 53→59→59 first at ln7430 ts 1784339306.774 (the floor print's own receipt);
PRA chain 40→41→41 at ln7433 (own low 41 from the floor print @1784342553.971). Then:

- **DAN proven.** The pair allocator rejected {59,43}/{59,42}/{59,41} (excess 3/2/1) fail-loud;
  at ln7434 ts 1784347275 it allocated DAN alone (ONE_OPEN_SIDE_OR_LIVE_TOUCH), PLACE 59 — 7,968 s
  after the floor moment and 5,008 s after the last ≤59 print, so the rest can never fill, which
  is the point — and DAN held 59 through span end exactly (17 conduct rows now in the receipt).
- **PRA lost — by law, not by failure.** On every row ln7435–7450:
  `rejected_candidate_targets {DAN:59, PRA:41}, excess_cents 1, reason
  PAIR_CONSERVATION_VETO_AUTHORITY_LEVELS_NOT_REWRITTEN`; divergence stamped honestly
  (authority 41, final null). With DAN resting 59, PRA's only floor-lawful rest (41) is exactly
  what the par veto must reject, and everything the par veto would accept (≤40) is floor-unlawful.
- **The contradiction, named (ZERO CONTRADICTIONS item):** whenever a pair's floors sum over par,
  the F-VS-121 proof-by-conduct standard (rests AT floors on BOTH legs) is **arithmetically
  unsatisfiable** while par conservation is senior. The build stamps DANPRA LAWFUL_INCOMPLETE on
  17 DAN-only conduct rows + the zero-headroom arithmetic ("59+41=100; offer 0"). That is a
  **redefinition of the standard** — one-leg conduct + arithmetic, not both-legs conduct — and it
  is the defensible reading, but it needs operator ratification, not silent adoption. The gate's
  DANPRA tripwire row now PASSES; the tripwire still fails the run on GIUBAR Δ4<7, URSPAL Δ2<4,
  and LAJSVA (unstamped-incomplete with the SVA leg lost per §3b).

---

## Scoreboard

@ec23ad2e vs the two parents: BAR 27 recovered (own-evidence self-correction — the build's model
row) · GIU 69 again (touch consumed as evidence) · URS 58 again (rounding + bid row took back the
57 it held) · PAL 40 (gave back 34d43755's exact-floor 39) · LAJ 54 (gave back 52) · SVA lost
entirely by <0.484 s of receipt ordering (was floor-exact 41 fill at d837b992) · DANPRA best state
yet (DAN proven, stamp banked) with a law contradiction underneath it. Street totals over the
9¢ of measurable gap (GIU 3, URS 1, PAL 1, LAJ 3, +SVA leg): WRONG-DATA-CONSUMED 3¢ ·
RIGHT-DATA-UNCONSUMED 2¢ + the SVA leg · DATA-GAP/never-existed 4¢.
