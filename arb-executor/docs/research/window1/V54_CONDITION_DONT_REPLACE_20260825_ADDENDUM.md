# V54 — condition, don't replace; conviction is the deliverable

License: L18 dispatch; `LAW_INDEX.md` read at `ad7138bd` with SHA-256 prefix `41784e6a`; CC authority `F-VS-219..222` at `ad7138bd`; conditioning `F-VS-066`; pair coherence `F-VS-053`; Definition Lock; rest-priced fill law; welds; conviction-before-the-floor.

Scope: CRIJEA smoke plus GIUBAR, URSPAL, LAJSVA, and DANPRA only. No 804, sealed, live, or deployment path ran.

Verdict: `SELF_STOP_BED_AND_UNGUARDED_ORDER_LINEAGE_UNTOUCHED`. The decisive package is `.claude/window1_live_v4_replay/v54_condition_dont_replace_20260825`.

- GIUBAR: incomplete; BAR ends resting at 27¢ and GIU at 64¢. The named fatal receipt lawfully conditions the 64¢ prior to 66¢, and both 27¢/66¢ floor rests appear in the decision stream, but the tape does not credit the pair while they stand.
- URSPAL: completes at PAL 40¢ + URS 58¢ = 98¢, Δ2. The explicit continuous estimate 57.526¢ rounds in the operator-named direction to 58¢; required 39+57 parity is not reproduced.
- LAJSVA: partial; LAJ fills 54¢ and SVA rests 41¢. SVA re-prices 37→41 on the deriving 41¢ print receipt with zero scheduler latency, but crediting occurs before that print is observed, and no later lawful print credits the rest.
- DANPRA: incomplete; DAN ends resting 56¢ and PRA has no standing rest. The over-par lawful-incomplete proof is not reproduced.

Executable repairs:

- True conditioning executes on 1,438 authority rows with zero receipt violations. Every current-game channel is graded and receipt-pinned; traded evidence is strongest; book evidence is informative but cannot author alone; the replacement operator is absent.
- At GIUBAR receipt `2898debe-683f-4cd1-7a5e-572e1b7ac028`, the complete prior distribution—including the 66¢ JUSHEI vote—survives. Traded 69¢, bid 68¢, and spread-clearing 70¢ update it to a 65.719¢ posterior and a directed 66¢ level.
- All 52 derived-and-postable target changes act on the same receipt with zero scheduler latency violations.
- Sixteen post-credit leg reads remain live, feed the sibling and overturn tests, and never emit a second order for the credited leg.
- All 1,438 fractional estimates carry an explicit integer direction; URS's named 57.5-class row becomes 58¢.
- Two complete executions per game are byte-identical.

Independent gate failure:

- One emitted LAJ order at 59¢ against ask 60¢ is lawful by value but lacks the production `TARGET_CENTS_LT_LIVE_ASK_CENTS` predicate receipt. The uncovered path is retained as `POST_ONLY_GUARD_DID_NOT_COVER_EMITTED_ORDER`; it was not repaired after observing the bed.

Ledger: this build adds builder findings `BC-042..045`. No builder-owned `F-VS` identifier was created.

Case study: `.claude/window1_live_v4_replay/lajsva_case_study_v28_condition_dont_replace_20260825`.
