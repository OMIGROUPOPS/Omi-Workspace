# THE ORACLE DIVERGENCE MAP — sample-of-30 [ANALYTICAL_ESTIMATE]

Analysis seat only. Read-only. Per game: the **winning line** (per leg, the post-onset floor print(s) and the
minimal standing plan that captures both legs at floor under kiss=credit), then the machine's actual V52h
trace walked against it, the **first divergence** marked at one of the eight decision nodes (wake / read /
diary / level / pair-coherence / license / action / credit-at-tape), and stamped **KNOWABLE_DEFECT** vs
**FORESIGHT_REQUIRED**. Full rows: `ORACLE_DIVERGENCE_MAP_30.csv` + `.json`.

**Pins.** V52h machine born @ `b43d7cde` (market-proof precondition removed). The sample-of-30 walked here is
the outcome table's cohort @ `576c705f` (`PER_GAME_OUTCOME_TABLE.json`), whose **V52h traces are the
`V52H_BASELINE_FULL_DECISION_TRACE_30_GAMES` chunks frozen in the same package** (395,073 receipts,
manifest-exact), with onsets from its `STABILITY_ONSET_LEDGER`. (`b43d7cde`'s own package traces a different
30-game cohort; the four-state on this cohort — 18 complete / 10 partial / 2 neither — is identical for V52h
and V52i, and the outcome table matches it.) Tape: `OMI-Window1-private/fit-local/prints.jsonl`, the
hash-bound replay source (4,836,462 true prints; 164,495 on these 60 legs). Validation: reconstructing every
credit by walking standing rests against the tape reproduces the outcome table's credited legs and entry
prices **30/30 exactly**.

## Method

**Winning line.** Per leg: post-onset floor = the minimum true-print price in [canonical onset, pre-match
boundary] reachable after the first post-onset decision receipt; the winning pair takes each leg's floor
(cheapest reachable pair when several floor-print levels exist), lawful only if the pair sums ≤99. The
minimal standing plan under kiss=credit: a rest at exactly the floor price, standing from any receipt before
a floor print into that print (any of the leg's floor prints will do — a leg credited at its floor via a
later floor print conforms). **Divergence.** Walked at receipt grain: the first receipt from which the
machine's standing answer, held through the binding moment (the floor print, or the kiss that consumed the
rest), differed from the winning line's required answer. **Stamp.** KNOWABLE_DEFECT if the winning answer
was supportable from tape evidence in hand before the last moment the machine could still have re-answered —
a post-onset true print at/below the floor, or a displayed ask at/below the floor, cited per game;
FORESIGHT_REQUIRED if no such evidence existed yet (what was missing is stated). Method boundary: palantir /
G-grid priors were **not** credited as support — no receipt names the floor level as a prior — so a
FORESIGHT stamp means *no tape evidence*; the operator may re-adjudicate those cells against the prior
store.

## The aggregate — divergence node × knowability × cents

Cents law: shallow wins carry the banked-vs-offer gap (offer margin − locked delta); misses carry the full
offer margin. Every first divergence in the sample lands at the **level** node — wake, read, diary,
pair-coherence, license, and action never diverged first on these 30 games (post-V52h the machine wakes,
reads, and licenses in time everywhere here; what it gets wrong is **where it stands**).

| first-divergence cell | games | ¢ | exemplars |
|---|--:|--:|---|
| **level(stood-above-floor) × FORESIGHT_REQUIRED** | **18** | **173** | GUEGOM 57¢ · BALHUA 32¢ · MORNEP 26¢ |
| level(stood-below-floor) × KNOWABLE_DEFECT | 4 | 38 | KUMTUR 24¢ · CASGEA 6¢ · ARSMAR 6¢ |
| level(authority-not-earned) × KNOWABLE_DEFECT | 1 | 2 | ARSRIC 2¢ |
| NO_WINNING_LINE (no post-onset pair ≤99 on the tape) | 5 | 0 | JONSPI (sum 101) · VANLEE/SALIBR/WESCOP (sum 100) · PUTJEA (tape silent) |
| CONFORMED (both legs captured at floor) | 2 | 0 | HOLBOU 1¢ margin banked whole · WOLVAN 1¢ |

Conservation: 30 = 18+4+1+5+2 games; 213¢ = 134¢ inside wins + 79¢ in misses. Leg grain (60): 28
stood-above-floor · 11 stood-below-floor · 3 authority-not-earned · 16 conformed · 2 no-post-onset-prints.
Credited legs above their own post-onset floor: 30, depth 201¢ — the package's `ENTRY_LATER_FLOOR` receipt
records 30/202¢ (1¢ convention difference on one leg; ROMGAL's census offer margin 5¢ vs print-grain 4¢ is
the same edge, cents here use the frozen census where it exists).

## All 30 games — margin, banked, divergence, entries vs floors

| game | state | offer | banked | ¢ | first divergence | knowability | leg | entries vs floors |
|---|---|--:|--:|--:|---|---|---|---|
| 26JUL12GUEGOM | PARTIAL | 57 | - | 57 | level(stood-above-floor) | FORESIGHT_REQUIRED | GUE | x/62 vs GOM@42/GUE@1 |
| 26JUL12BALHUA | COMPLETE | 33 | 1 | 32 | level(stood-above-floor) | FORESIGHT_REQUIRED | HUA | 17/82 vs BAL@1/HUA@66 |
| 26JUL12MORNEP | COMPLETE | 29 | 3 | 26 | level(stood-above-floor) | FORESIGHT_REQUIRED | NEP | 71/26 vs MOR@70/NEP@1 |
| 26JUL12KUMTUR | COMPLETE | 30 | 6 | 24 | level(stood-below-floor) | KNOWABLE_DEFECT | KUM | 72/22 vs KUM@69/TUR@1 |
| 26JUL12PANYOR | COMPLETE | 19 | 1 | 18 | level(stood-above-floor) | FORESIGHT_REQUIRED | YOR | 86/13 vs PAN@80/YOR@1 |
| 26JUL16MERDRO | COMPLETE | 13 | 3 | 10 | level(stood-above-floor) | FORESIGHT_REQUIRED | DRO | 49/48 vs DRO@39/MER@48 |
| 26JUL17BURMER | COMPLETE | 8 | 2 | 6 | level(stood-above-floor) | FORESIGHT_REQUIRED | BUR | 41/57 vs BUR@37/MER@55 |
| 26JUL18CASGEA | PARTIAL | 6 | - | 6 | level(stood-below-floor) | KNOWABLE_DEFECT | CAS | x/65 vs CAS@29/GEA@65 |
| 26JUL19ARSMAR | PARTIAL | 6 | - | 6 | level(stood-below-floor) | KNOWABLE_DEFECT | ARS | x/60 vs ARS@35/MAR@59 |
| 26JUL15ROMGAL | PARTIAL | 5 | - | 5 | level(stood-above-floor) | FORESIGHT_REQUIRED | GAL | 67/x vs GAL@66/ROM@30 |
| 26JUL12POLKUH | COMPLETE | 5 | 1 | 4 | level(stood-above-floor) | FORESIGHT_REQUIRED | POL | 18/81 vs KUH@15/POL@80 |
| 26JUL12DAHBAE | COMPLETE | 4 | 1 | 3 | level(stood-above-floor) | FORESIGHT_REQUIRED | BAE | 94/5 vs BAE@92/DAH@4 |
| 26JUL13SANDAN | COMPLETE | 3 | 1 | 2 | level(stood-above-floor) | FORESIGHT_REQUIRED | SAN | 75/24 vs DAN@75/SAN@22 |
| 26JUL15PRIMOL | COMPLETE | 4 | 2 | 2 | level(stood-above-floor) | FORESIGHT_REQUIRED | PRI | 29/69 vs MOL@28/PRI@68 |
| 26JUL18BADZID | COMPLETE | 3 | 1 | 2 | level(stood-above-floor) | FORESIGHT_REQUIRED | ZID | 74/25 vs BAD@74/ZID@23 |
| 26JUL20ARSRIC | PARTIAL | 2 | - | 2 | level(authority-not-earned) | KNOWABLE_DEFECT | ARS | x/62 vs ARS@36/RIC@62 |
| 26JUL20QUEKAL | PARTIAL | 2 | - | 2 | level(stood-below-floor) | KNOWABLE_DEFECT | KAL | x/31 vs KAL@68/QUE@30 |
| 26JUL12PRIBAL | PARTIAL | 1 | - | 1 | level(stood-above-floor) | FORESIGHT_REQUIRED | BAL | 3/x vs BAL@1/PRI@98 |
| 26JUL13BLISAS | COMPLETE | 3 | 2 | 1 | level(stood-above-floor) | FORESIGHT_REQUIRED | BLI | 43/55 vs BLI@42/SAS@55 |
| 26JUL14DELXIL | COMPLETE | 2 | 1 | 1 | level(stood-above-floor) | FORESIGHT_REQUIRED | XIL | 83/16 vs DEL@83/XIL@15 |
| 26JUL15TABMID | COMPLETE | 3 | 2 | 1 | level(stood-above-floor) | FORESIGHT_REQUIRED | MID | 24/74 vs MID@23/TAB@74 |
| 26JUL20KYMCLA | COMPLETE | 2 | 1 | 1 | level(stood-above-floor) | FORESIGHT_REQUIRED | CLA | 24/75 vs CLA@23/KYM@75 |
| 26JUL20TROISO | COMPLETE | 2 | 1 | 1 | level(stood-above-floor) | FORESIGHT_REQUIRED | ISO | 22/77 vs ISO@21/TRO@77 |
| 26JUL13JONSPI | NEITHER | none | - | 0 | NO_WINNING_LINE | - | - | x/x vs JON@89/SPI@12 |
| 26JUL13VANLEE | PARTIAL | none | - | 0 | NO_WINNING_LINE | - | - | x/55 vs LEE@45/VAN@55 |
| 26JUL14PUTJEA | NEITHER | none | - | 0 | NO_WINNING_LINE | - | - | x/x vs no post-onset prints |
| 26JUL14SALIBR | PARTIAL | none | - | 0 | NO_WINNING_LINE | - | - | x/56 vs IBR@44/SAL@56 |
| 26JUL14WOLVAN | COMPLETE | 1 | 1 | 0 | CONFORMED | - | - | 79/20 vs VAN@79/WOL@20 |
| 26JUL15WESCOP | PARTIAL | none | - | 0 | NO_WINNING_LINE | - | - | x/18 vs COP@83/WES@17 |
| 26JUL17HOLBOU | COMPLETE | 1 | 1 | 0 | CONFORMED | - | - | 33/66 vs BOU@33/HOL@66 |

## The exemplar walks

### level(stood-above-floor) × FORESIGHT_REQUIRED — 18 games / 173¢

**26JUL12GUEGOM (57¢, PARTIAL).** Winning line: GUE rest@1¢ (45 floor prints from onset+67.5 min, first
size 195) + GOM rest@42¢ (2 floor prints, first at onset+10 s, size 63) = 43, margin 57. Machine: GUE — wake
✓ read ✓ (2,356 comparable book transitions) level ✗: posted 62¢ at onset+3.8 min
(`GUE.csv.gz#row-46316`, reason `V52E_LICENSED_PRIOR_INFORMED_LEVEL_POST`, book 63×62), kissed 15 s later;
the 1¢ tape (the runner's collapse) began 63 min after the rest was consumed — no print or ask at/below 1¢
existed before the kiss: **FORESIGHT_REQUIRED** (the winning answer needed the collapse itself). GOM — the
42¢ floor printed 10 s after GOM's onset; machine stood 37¢ (settlement-bound target, `#row-64999`) with the
ask displayed at 41¢ — knowable at leg grain, but the game's first divergence is GUE's, 9.2 min earlier.
The pair died on the bought side's early kiss.

**26JUL12BALHUA (32¢, COMPLETE banked 1).** Winning line: BAL@1¢ (19 floor prints from onset+92 min) +
HUA@66¢ (3 floor prints from onset+23.7 min) = 67, margin 33. Machine: HUA posted 82¢ at onset+4.4 min
(`HUA.csv.gz#row-1452`, ask 93/bid 82), kissed 28 s later — 18.8 min before the 66¢ evidence existed:
FORESIGHT. BAL posted 17¢ at onset+8.4 min (ask 21), kissed 6 s later; the 1¢ floor came 84 min after. Both
legs' kisses consumed the rests before either floor level had ever traded or been offered. Banked 1¢ of a
33¢ offer.

**26JUL12MORNEP (26¢, COMPLETE banked 3).** Winning line: MOR@70¢ + NEP@1¢ = 71, margin 29. NEP posted 26¢
at onset+2.1 h (ask 27), kissed instantly; its 1¢ floor (45 prints) arrived 16.4 h later. MOR posted 71¢ at
onset+11.3 h, kissed in 1 s; the 70¢ floor printed 6.8 h after that. FORESIGHT both legs — deepest
time-gaps in the sample between kiss and first floor evidence.

### level(stood-below-floor) × KNOWABLE_DEFECT — 4 games / 38¢

**26JUL12KUMTUR (24¢, COMPLETE banked 6).** Winning line: KUM@69¢ (one floor print, onset+7.9 min, bid-side,
size 45) + TUR@1¢ = 70, margin 30. Machine: KUM stood 60¢ from its onset receipt (`KUM.csv.gz#row-19909`)
through the 69¢ floor print — then repriced **up** and was credited at 72¢ three minutes after refusing 69:
the walk's cleanest buy-through-the-refused-floor. Evidence in hand: the ask was displayed at 60¢ (crossed
book, bid shown 75) at the divergence receipt — sellers at/below the floor level were in evidence:
**KNOWABLE_DEFECT**. TUR posted 22¢, kissed at onset+3.4 min, 1¢ tape 70 min later (FORESIGHT, second leg).
First divergence is KUM's.

**26JUL18CASGEA (6¢, PARTIAL).** GEA conformed — credited at its 65¢ floor 6.7 min after onset. CAS: floor
29¢ (onset+28.1 min); machine stood **28¢** — one cent under the kiss — with the ask displayed at 29¢
sixteen seconds before the print (`CAS.csv.gz#row-28592`): KNOWABLE_DEFECT. One cent of standing distance
cost the whole 6¢ pair.

**26JUL19ARSMAR (6¢, PARTIAL).** ARS: floor 35¢ (onset+44 min, 2 prints); machine posted 29¢ at onset+31 s
and never moved; the ask touched 35¢ 3.4 min before the floor print (`ARS.csv.gz#row-138`):
KNOWABLE_DEFECT. MAR was credited 60¢ vs floor 59¢ (foresight at leg grain, 1¢). The knowable six cents
died on ARS's static stand.

### level(authority-not-earned) × KNOWABLE_DEFECT — 1 game / 2¢

**26JUL20ARSRIC (2¢, PARTIAL).** RIC conformed at its 62¢ floor. ARS: read passed with **3,550 comparable
book transitions consulted**, yet `MACHINE_READ_LEVEL_AUTHORITY_NOT_EARNED` held from onset+18 s
(`ARS.csv.gz#row-1651`) through **31 floor prints at 36¢** (first at onset+2.1 h), the ask sitting at
exactly 36¢ from onset+89 min (`#row-4457`). The clause-③ authority threshold, not evidence scarcity,
refused a floor the book displayed for hours: KNOWABLE_DEFECT.

### The five fat-offer/thin-bank games — divergences inside wins, named explicitly

BALHUA 32¢ and MORNEP 26¢ walked above; KUMTUR 24¢ above (the one knowable fat game). **26JUL12PANYOR
(18¢, banked 1).** Winning: PAN@80 + YOR@1 = 81, margin 19. YOR posted 13¢ (ask 15), kissed at onset+8.8
min; 1¢ floor 47 min later. PAN was credited at 86¢ **eleven milliseconds before** the 80¢ floor print
(credit 1783858255.908, floor .919) — the same market pulse that proved 80 executed the 86 rest first:
FORESIGHT by 11 ms, the sample's sharpest statement of kiss-precedes-evidence. **26JUL16MERDRO (10¢, banked
3).** MER conformed at its 48¢ floor (onset+8.2 min). DRO posted 49¢ at onset+22.8 min (ask 53), kissed 8
min later; the 39¢ tape (16 floor prints) began 4.5 h after the kiss: FORESIGHT. Fat five total: 110¢ of
the 134¢ forgone inside wins.

### NO_WINNING_LINE — 5 games / 0¢

**26JUL13JONSPI**: floors 89+12 = 101 — no pair ≤99 ever printed post-onset; leg-grain divergences exist
(JON's 89¢ floor printed 1 s after onset under authority-not-earned; SPI stood 10¢ vs floor 12¢ with the
ask at 12¢) but no lawful line to charge them against. **26JUL13VANLEE** (VAN conformed at 55; LEE's 45¢
floor under authority-not-earned with ask displayed at 45 — but 45+55 = 100, one cent past lawful) —
likewise **26JUL14SALIBR** and **26JUL15WESCOP** (both sum 100). **26JUL14PUTJEA**: zero post-onset prints
on either leg — nothing to kiss; the tape itself was silent. These five carry the outcome table's null offer
margins; charged 0¢.

### CONFORMED — 2 games

**26JUL17HOLBOU**: BOU credited at its 33¢ floor (a later floor print; the first passed while the rest
stood elsewhere — the plan needs only one), HOL at its 66¢ floor; 99 joint, the whole 1¢ margin banked.
**26JUL14WOLVAN**: VAN at 79¢ floor (later floor print), WOL at 20¢ floor; 1¢ margin banked whole. The
machine's only two oracle-conformed games are the two thinnest margins in the sample.

## Conservation

30 games = 18 + 4 + 1 + 5 + 2; 213¢ = 173 + 38 + 2 + 0 + 0 = 134¢ (banked-vs-offer gaps, 16 divergent
completes) + 79¢ (full margins, 7 divergent misses); 60 legs = 28 + 11 + 3 + 16 + 2. Credit reconstruction
against the tape matches the frozen outcome table 30/30 (entries and credited-leg sets exact). Winning-line
margins equal the frozen census offer margins on all 24 games where the census has a number (ROMGAL 4¢
print-grain vs 5¢ census noted; census used). No score, policy, or Codex artifact touched.
ANALYTICAL_ESTIMATE.
