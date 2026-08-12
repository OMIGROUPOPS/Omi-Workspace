# The decision audit — judgment, not cents [ANALYTICAL_ESTIMATE]

Analysis seat only. Read-only. V49b dev-804 staged ledger (operator-cited `47b51fd2`), per game per leg.
Verdicts against **forward truth only** (the `12d67c8a` method: realized mid path +30/60/90 min from the
decision moment, dev tapes, majority direction, ±2¢ band; a directional read is WRONG only when the market
moved *opposite* — stasis never convicts). Whole-window ex-post labels not used (that ruler is convicted,
doctrine 2). Machine artifact with all 1,608 leg rows: `DECISION_AUDIT.json`.

**Coverage gap, reported not reconstructed:** the staged V49b carries no ACTION_TRACE, so walk-level
(per-reprice) grading is unavailable from machine records. Graded moments: join arm, the governing read at
stand, first withhold, terminal restraint.

## Deliverable 1 — the state × verdict matrix (legs)

| state | RIGHT_READ_RIGHT_PLAY | RIGHT_READ_WRONG_PLAY | WRONG_READ | CORRECT_RESTRAINT | STARVED | Σ |
|---|--:|--:|--:|--:|--:|--:|
| COMPLETE (393 g) | 625 | 0 | 161 | 0 | 0 | 786 |
| PARTIAL (357 g) | 282 | 284 | 148 | 0 | 0 | 714 |
| NEITHER (54 g) | 0 | 78 | 26 | 0 | 4 | 108 |
| **total** | **907** | **362** | **335** | **0** | **4** | **1,608** |

Three reads:

- **The OS's judgment is mostly sound: 56.4% of legs are right-read-right-play and only 20.8% are wrong
  reads.** But 161 of the 786 completed legs (20.5%) are **lucky fills** — credited while the read was
  forward-wrong.
- **CORRECT_RESTRAINT is empty — structurally.** V49b stood on 1,603 of 1,608 legs. This OS does not restrain;
  it stands everywhere and lets the window arbitrate. There is no restraint to grade (and none to inflate).
- The 362 right-read-wrong-play legs are the judgment-side view of the par sheet's placement bill: the read
  was right and the level/timing still failed.

**Moment grades:** join arms — 1,315/1,589 (82.8%) not contradicted by forward truth. **Withholds — 420/676
moments (62.1%) directly preceded downward flow**: the deep-gap guard's withholds sat in front of oncoming
flow more often than not. The S12 guard grades far worse at the moment level than its cents footprint
(59¢ at par) suggests, because elsewhere the rest usually re-stood in time.

**The partial split (all 357, one-eyed test extended):**

| bucket | games |
|---|--:|
| intentional-and-right (unfilled leg = correct restraint) | 0 |
| **half-right-never-arbitrated** (reads inverse, held both) | **118** |
| plain misread (unfilled leg forward-wrong, non-inverse) | 49 |
| execution-shortfall (unfilled read RIGHT, non-inverse — level/timing only) | 190 |

The fourth bucket is reported, not forced, into the ordered three: it is the largest — **53% of partials are
not judgment failures at all**; the unfilled leg read the market correctly and simply never filled. Of the 118
one-eyed games, vindication by each read's own forward truth: **BOTH 86** · NEITHER 19 · UNFILLED-only 8 ·
FILLED-only 5. BOTH dominating is the mirror doing what mirrors do — the sibling tapes moved oppositely, both
opposed reads were locally right, and the OS held two correct, unarbitrated reads to the bell (the §-open
arbitration slot, S3's unconsumed `disagreement` flag, measured again from the judgment side).

## Deliverable 2 — the discriminator pass (game-level; RIGHT = no wrong-read leg)

804 games adjudicate **RIGHT 530 / WRONG 274 (65.9%)**. RIGHT-share per bin, separation = max−min over bins
with n≥25 (splits only, no models):

| rank | feature | separation | the split |
|---|---|--:|---|
| 1 | **category** | **0.163** | WTA_MAIN .737 · ATP_MAIN .728 ≫ ATP_CHALL .631 · **WTA_CHALL .574** |
| 2 | **volume shape** | **0.127** | 1k–10k lots .688 > 10k+ .648 ≫ **100–999 lots .561** |
| 3 | **price cell** | **0.122** | le25+le25 .750 > 26_50+51_75 .660 > **ge75+le25 .628** |
| 4 | mirror coherence | 0.083 | coherent_inverse .684 > incoherent_same .663 > mixed_settled .601 |
| 5 | late-volume share | 0.047 | (flat) |
| 6 | spread regime | 0.023 | (flat — spread does not separate) |

Where this OS works: **main-tour games with moderate liquidity and balanced-to-cheap price cells.** Where it
doesn't: **WTA challengers, thin tapes (sub-1k lots), and the lopsided ge75+le25 cell.** Spread regime —
the obvious suspect — separates nothing (0.023).

## Tautology check (doctrine 2)

CORRECT_RESTRAINT would trivially inflate via (a) judging restraint by absence-of-fill (ex-post — the
convicted ruler), (b) counting stasis as earned restraint, or (c) crediting restraint on legs the market never
offered. Guards applied: any never-stood leg with an in-window trade at-or-below its would-be rest is forced
to WRONG_READ, never restraint; restraint would have been stratified earned-moved-away vs vacuous-stasis. The
structural fact moots the risk here: **V49b stands on 1,603/1,608 legs — the class is empty because the OS has
no restraint behavior, not because the classifier cleared it.**

## Conservation

1,608 legs = 907+362+335+0+4; states 786+714+108; partial split 0+118+49+190 = 357; vindication 86+19+8+5 =
118; discriminator bins each sum 804. Forward truth from dev tapes (1,608/1,608 loaded), prints fit-local
(1,592 legs with in-window trades). ANALYTICAL_ESTIMATE.
