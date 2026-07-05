# PROOF PASS — 2026-07-05 full slate: what happened, the guilty line, the replay under each fix

## TWO-LANE RE-STAMP (C46 as amended 2026-07-05) — and the deploy this doc gates
**This document is the OUTCOME_PROOF for deploy candidate `42a54e04` (C-RISER-REVISION, flag `riser_post_revision`).**
Outcome is judged in TWO LANES (LANE 1 MECHANISM — primary, luck-free, every game counts: the construction of
trades replayed deterministically against the tape — grade distribution, ≤97 rate, Δaim per leg, pair
completion, FV-capture. LANE 2 SETTLEMENT P&L — secondary sanity check, flagged LUCK-POLLUTED below n≈30
settlements, never the sole verdict at small n):

| fix | LANE 1 — MECHANISM (primary) | LANE 2 — P&L (secondary) | verdict |
|---|---|---|---|
| **riser_post revision** | **WIN** — 89/107 riser fills retained (83%) at 2–3¢ better Δaim across the FULL slate, matching the pre-registered N=69 curves; pair-completion structure held (18 lost fills flagged per-row) | **+$6.50** (n=107 legs) | **WINS BOTH → DEPLOYS (`42a54e04`)** |
| **per_match_clock** (staged ce38ca8c) | Correct construction where it binds (1/14 half_timing candidates recovered; 10 refuted by tape = the ITF-no-premarket fact, itself the fix's own evidence base) | +$1.00 (n=1 — LUCK-POLLUTED, secondary) | Arms on CORRECTNESS when its Plex ruling lands; shadow-first |
| **scale-gun _MAIN** (staged shadow) | Mechanically CORRECT — it preserved a fillable bid that the premature latch killed | −$1.90 (**n=1 settlement — LUCK-POLLUTED**; one lost match is noise) | **SHADOW-INSUFFICIENT-N** (revised from "negative/guilty" — insufficient settlements, not guilt) |

**Riser prior-art note (C45, verified — no grave):** greps `riser_post|riser.post|riser depth` over LESSONS.md,
JUNE_VAULT.md(+APPENDIX), ROADMAP.md, .claude/rulings/ and the gated-flag inventory return only THIS week's
lineage (C44 amendment → RISER_REVISION_PROPOSAL.md → PLEX_RISER_BOUNCE_PACKAGE.md → this deploy). No prior
incarnation, no half-fix ancestor; the table's `riser_post` field existed data-only and is wired for the
first time by `42a54e04`.

**Population:** the full current box — every position, all sessions since the aba83af boot (Jul 4 21:32 ET)
through tonight: **147 games / 251+ filled legs, actual net $-3.92** (exchange-truth graded, refreshed
full_tape_regrade.py run tonight). Line numbers reference the RUNNING deploy source (21eaad4).

## Prior art (gate — C45)
- Greps: `regrade|causal|retention|half_timing|riser_post|guilty` over LESSONS.md, JUNE_VAULT.md(+APPENDIX), .claude/rulings/, .claude/nightly_20260705/.
- Established: **C44** (the causal-audit method — code chain + EARNED/GIFT is the "guilty code" discipline this pass extends); **F39** (exchange truth only); FULL_TAPE_REGRADE.md + ftr_dump.json (tonight's actual column IS that machinery re-run); riser_depth_replay.py N=69 retention curves (Fix-C methodology precedent — tonight's per-game retention 89/107 = 83% independently matches its 62-90%); audit/leak_decomposition.py half_timing channel (Fix-A's target); CLOCK_AUDIT.md + PART1_SPEC.md (Fix-A design basis); C40 (lint+smoke law this pass extends with outcome proof).
- Staged-but-never-armed builds replayed here: **C-PM-CLOCK `per_match_clock`** (ce38ca8c), **C-SCALE-GUN `scale_gun_shadow`** (ce38ca8c); proposed: **riser_post revision** (PLEX_RISER_BOUNCE_PACKAGE.md, not relayed).
- DELTA: per-game, per-fix OUTCOME replay against today's actual tape (grades/dollars, not mechanisms) + THE OUTCOME-PROOF LAW into the deploy gate.

## Replay conventions (conservative; no credit the tape doesn't support)
- **FIX A — per_match_clock (Part 1, staged):** completion-recovery channel only. A naked single where the fader's dip≤bound passed BEFORE the bound existed is replayed on the honest TE/ESPN clock: claim ONLY if leg1 shows a catchable dip inside the honest window and BEFORE the fader divot, and the resulting pair ≤100c. No honest join / tape refutes → NO CLAIM (the row says so).
- **FIX B — scale-aware gun (Part 3, proposed for _MAIN):** posted-never-filled mains bids cancelled on the premature latch survive to the honest-start proxy; fill only against real prints ≤ posted after the actual cancel; settle outcome counted BOTH directions (losses negative).
- **FIX C — riser_post revision (proposed; CHALL 3¢/ITF_M 3¢/ITF_W 2¢, mains hold):** every riser fill re-posted depth lower; RETAINED iff the real tape prints ≤ revised while the bid rests (post→latch) → +depth×qty; LOST → −(that leg's actual pnl), pair-break flagged. Retention tonight 89/107 (83%), consistent with the N=69 curves.
- Directional-hold losses are charged to the exit design (OUT OF SCOPE per Vault 0A ⛔) — no fix here claims them.

## BOTTOM LINE — each fix earns or fails on its own number (today's tape, 147 games)
| fix | status | games changed | **net delta $** | reading |
|---|---|---|---|---|
| FIX A per_match_clock | STAGED ce38ca8c | 1 of 14 half_timing candidates | **+1.00** | The clock fix is real but today's tape rarely offered leg1 a pre-divot dip (10/14 refuted by tape, 3 no join). It earns arming as SHADOW on correctness, not on today's dollars. |
| FIX B scale-gun _MAIN | STAGED (shadow) | 1 | **-1.90** | The one surviving mains fill LOSES tonight. Data says: collect shadow agreement first, do NOT arm a consumer on this sample. |
| FIX C riser_post revision | PROPOSED (Plex) | 107 riser legs (89 retained / 18 lost) | **+6.50** | Depth buys cents at 83% retention — consistent with the pre-registered curves; the 18 lost fills' pnl nets against it. Positive on today's tape. |

Actual slate net: **$-3.92**. No fix is credited beyond what today's prints support; rows below say "—" where a fix changes nothing.

## THE TABLE — game | actual | guilty line | replay per fix
Legend: guilty-line refs = running source 21eaad4 (kprim=:3339 kalshi_schedule_primary block, maxlead=:134 V4_MAX_PLACEMENT_SEC, ctarget=:3977 _completion_target, anchor=:2194 _v4_entry_anchor, riser=:1579 riser_post aim, mlive=:4247 _is_match_live).

| game | act | $ | guilty | FIX A | FIX B | FIX C |
|---|---|---|---|---|---|---|
| ATPCH-04LEGWIN | D | +0.90 | placeholder clock window (kalshi_schedule_primary) (:3339) + T-4h lead on that clock (:134) | **+1.00** pair completes 62c (leg1@46 pre-divot + fader@16) -> A/B | — | — |
| ATPCH-05ALBZOR | B | +0.55 | none charged (grade B) | — | — | **+0.15** ALB retained @88 (+3c) |
| ATPCH-05BASRIB | C | +1.30 | riser adverse selection (C44: fills when the leg fades in) (:1579) | — | — | **+0.15** RIB retained @58 (+3c) |
| ATPCH-05BERBOC | C | -0.15 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) / hold-to-settle on the losing leg (exit design; OUT OF | — | — | **-0.95** BOC LOST (floor 75 / t) -> -leg pnl 0.95 [pair breaks -> naked risk] |
| ATPCH-05BINPOL | C | +1.25 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** BIN retained @56 (+3c) |
| ATPCH-05BLIPET | F | -0.30 | partner never reached: _v4_entry_anchor level vs tape / queue (:2194) | — | — | — |
| ATPCH-05CAMBID | A | +1.05 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** CAM retained @79 (+3c) |
| ATPCH-05CARCER | A | +0.45 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** CER retained @90 (+3c) |
| ATPCH-05CHESPE | F | -1.95 | partner never reached: _v4_entry_anchor level vs tape / queue (:2194) | — | — | — |
| ATPCH-05CIZCAZ | C | +1.25 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** CAZ retained @66 (+3c) |
| ATPCH-05COVDEL | C | +1.35 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** DEL retained @65 (+3c) |
| ATPCH-05CRIRUB | C | -3.25 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) / hold-to-settle on the losing leg (exit design; OUT OF | — | — | **+0.15** RUB retained @69 (+3c) |
| ATPCH-05DALARI | C | -0.10 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **-0.20** DAL LOST (floor None / t) -> -leg pnl 0.20 [pair breaks -> naked risk] |
| ATPCH-05DESYEV | C | +3.55 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** YEV retained @65 (+3c) |
| ATPCH-05DIACEC | A | +1.30 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** DIA retained @62 (+3c) |
| ATPCH-05DONGRE | F | -0.95 | placeholder clock window (kalshi_schedule_primary) (:3339) + T-4h lead on that clock (:134) | 0.00 tape: leg1 catchable dip not before fader divot in honest window -> NO CLAIM | — | — |
| ATPCH-05ELLJOH | C | -2.80 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** ELL retained @61 (+3c) |
| ATPCH-05FARMAT | B | +1.20 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** MAT retained @54 (+3c) |
| ATPCH-05FELMOE | C | -3.50 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) / hold-to-settle on the losing leg (exit design; OUT OF | — | — | **+0.15** FEL retained @73 (+3c) |
| ATPCH-05FRUSIN | F | -0.25 | partner never reached: _v4_entry_anchor level vs tape / queue (:2194) | — | — | — |
| ATPCH-05GANZIN | C | -0.45 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** ZIN retained @65 (+3c) |
| ATPCH-05GOIAND | F | -1.55 | partner never reached: _v4_entry_anchor level vs tape / queue (:2194) | — | — | — |
| ATPCH-05GOMMAJ | A | +1.15 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** GOM retained @77 (+3c) |
| ATPCH-05HIGZHU | C | +1.20 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** ZHU retained @55 (+3c) |
| ATPCH-05HUANOC | C | -3.10 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** NOC retained @66 (+3c) |
| ATPCH-05HUEMAR | D | +0.07 | partner never reached: _v4_entry_anchor level vs tape / queue (:2194) | — | — | — |
| ATPCH-05HUEZEB | C | +1.10 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.09** HUE retained @53 (+3c) |
| ATPCH-05IEMBER | C | +0.05 | pre-ruling bound hole (FIXED live 21eaad4 C-BOUND-RULING) (:3977) | — | — | **-0.25** BER LOST (floor None / t) -> -leg pnl 0.25 [pair breaks -> naked risk] |
| ATPCH-05ILAPLU | C | -0.52 | pre-ruling bound hole (FIXED live 21eaad4 C-BOUND-RULING) (:3977) / riser_post=0 aim (aim_table.json): bid at the going  | — | — | **+0.09** ILA retained @92 (+3c) |
| ATPCH-05IMAMIL | C | +1.20 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** MIL retained @55 (+3c) |
| ATPCH-05INGFEL | C | -0.30 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** FEL retained @69 (+3c) |
| ATPCH-05IVAGAN | A | +1.25 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** IVA retained @72 (+3c) |
| ATPCH-05JANRYA | B | +0.40 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** JAN retained @91 (+3c) |
| ATPCH-05KAMVAN | B | +0.64 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.03** VAN retained @84 (+3c) |
| ATPCH-05KOZMAY | A | +1.10 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** MAY retained @48 (+3c) |
| ATPCH-05KUZMAT | A | +0.60 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** KUZ retained @87 (+3c) |
| ATPCH-05LEGSHI | A | +0.55 | none charged (grade A) | — | — | — |
| ATPCH-05LUZSAN | C | -3.60 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** SAN retained @75 (+3c) |
| ATPCH-05MACBRA | A | +0.05 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **-0.20** BRA LOST (floor None / t) -> -leg pnl 0.20 [pair breaks -> naked risk] |
| ATPCH-05MARDUR | C | -2.75 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) / hold-to-settle on the losing leg (exit design; OUT OF | — | — | **+0.15** DUR retained @60 (+3c) |
| ATPCH-05MARHAI | A | +0.30 | none charged (grade A) | — | — | **+0.15** HAI retained @93 (+3c) |
| ATPCH-05MARJUN | B | +1.20 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.12** MAR retained @55 (+3c) |
| ATPCH-05MARNVS | F | -0.25 | partner never reached: _v4_entry_anchor level vs tape / queue (:2194) | — | — | — |
| ATPCH-05MARZAN | D | +0.20 | partner never reached: _v4_entry_anchor level vs tape / queue (:2194) | — | — | — |
| ATPCH-05MELWAL | C | -0.75 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **-0.95** WAL LOST (floor 63 / t) -> -leg pnl 0.95 [pair breaks -> naked risk] |
| ATPCH-05MONHUR | F | -0.20 | partner never reached: _v4_entry_anchor level vs tape / queue (:2194) | — | — | — |
| ATPCH-05MORMAR | B | +1.25 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** MOR retained @56 (+3c) |
| ATPCH-05NIJBER | C | +1.25 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** NIJ retained @71 (+3c) |
| ATPCH-05NUNCLA | A | +1.20 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** CLA retained @54 (+3c) |
| ATPCH-05PAPMBI | C | -2.80 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) / hold-to-settle on the losing leg (exit design; OUT OF | — | — | **+0.15** MBI retained @61 (+3c) |
| ATPCH-05PAPPAR | A | +1.05 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** PAP retained @79 (+3c) |
| ATPCH-05PARHAM | A | +0.05 | none charged (grade A) | — | — | **+0.15** HAM retained @87 (+3c) |
| ATPCH-05PDACAS | B | +1.20 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** PDA retained @55 (+3c) |
| ATPCH-05PEROPI | C | -3.30 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) / hold-to-settle on the losing leg (exit design; OUT OF | — | — | **+0.15** PER retained @70 (+3c) |
| ATPCH-05PIELAR | A | +0.55 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.06** PIE retained @88 (+3c) |
| ATPCH-05POPCAS | B | +0.05 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** POP retained @90 (+3c) |
| ATPCH-05POTANG | B | +1.15 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** POT retained @47 (+3c) |
| ATPCH-05PRICOU | C | +1.15 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** COU retained @47 (+3c) |
| ATPCH-05PRIROT | C | -0.40 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **-0.95** PRI LOST (floor 70 / t) -> -leg pnl 0.95 [pair breaks -> naked risk] |
| ATPCH-05RAMNEU | C | +1.30 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** NEU retained @58 (+3c) |
| ATPCH-05RAQMAS | A | +0.65 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **-0.45** RAQ LOST (floor 88 / t) -> -leg pnl 0.45 [pair breaks -> naked risk] |
| ATPCH-05RATRAH | C | +1.20 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** RAH retained @55 (+3c) |
| ATPCH-05RYBTUN | F | -3.65 | partner never reached: _v4_entry_anchor level vs tape / queue (:2194) / riser_post=0 aim (aim_table.json): bid at the go | — | — | **+0.15** TUN retained @70 (+3c) |
| ATPCH-05SANROD | F | -4.10 | partner never reached: _v4_entry_anchor level vs tape / queue (:2194) / riser_post=0 aim (aim_table.json): bid at the go | — | — | **+0.15** ROD retained @79 (+3c) |
| ATPCH-05SCHDE | C | +1.30 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** DE retained @72 (+3c) |
| ATPCH-05SCIORA | B | +1.10 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** ORA retained @78 (+3c) |
| ATPCH-05SEGHAB | A | +0.35 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **-0.40** SEG LOST (floor None / t) -> -leg pnl 0.40 [pair breaks -> naked risk] |
| ATPCH-05SEIMOL | C | +0.90 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** MOL retained @81 (+3c) |
| ATPCH-05SEKMAL | C | -2.80 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) / hold-to-settle on the losing leg (exit design; OUT OF | — | — | **+0.15** SEK retained @61 (+3c) |
| ATPCH-05SEYMAJ | F | -0.20 | partner never reached: _v4_entry_anchor level vs tape / queue (:2194) | — | — | — |
| ATPCH-05SLABAS | C | -1.20 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **-0.80** BAS LOST (floor 57 / t) -> -leg pnl 0.80 [pair breaks -> naked risk] |
| ATPCH-05SMIPIR | C | -0.35 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** PIR retained @68 (+3c) |
| ATPCH-05STALOC | A | +0.05 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** STA retained @91 (+3c) |
| ATPCH-05STEDIN | C | +1.30 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** DIN retained @68 (+3c) |
| ATPCH-05SUNBAR | C | -1.20 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) / hold-to-settle on the losing leg (exit design; OUT OF | — | — | **-0.80** BAR LOST (floor 57 / t) -> -leg pnl 0.80 [pair breaks -> naked risk] |
| ATPCH-05SZYSTR | B | +1.15 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** STR retained @50 (+3c) |
| ATPCH-05TENBER | C | +1.25 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** BER retained @54 (+3c) |
| ATPCH-05TIXLEC | A | +0.05 | none charged (grade A) | — | — | **+0.15** LEC retained @77 (+3c) |
| ATPCH-05URRMEL | D | +0.20 | partner never reached: _v4_entry_anchor level vs tape / queue (:2194) | — | — | — |
| ATPCH-05UTADEV | B | +1.25 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** UTA retained @56 (+3c) |
| ATPCH-05VALREJ | C | +1.25 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.12** VAL retained @64 (+3c) |
| ATPCH-05VANTRO | A | +1.10 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **-0.65** TRO LOST (floor 51 / t) -> -leg pnl 0.65 [pair breaks -> naked risk] |
| ATPCH-05VILKOV | A | +1.15 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** VIL retained @47 (+3c) |
| ATPCH-05VILPER | F | -4.35 | partner never reached: _v4_entry_anchor level vs tape / queue (:2194) | — | — | **+0.09** VIL retained @84 (+3c) |
| ATPCH-05VILPUR | D | +0.85 | partner never reached: _v4_entry_anchor level vs tape / queue (:2194) / riser_post=0 aim (aim_table.json): bid at the go | — | — | **+0.15** PUR retained @78 (+3c) |
| ATPCH-05WALVAR | F | -0.15 | partner never reached: _v4_entry_anchor level vs tape / queue (:2194) | — | — | — |
| ATPCH-05WEHIFI | A | +0.70 | none charged (grade A) | — | — | **+0.15** WEH retained @85 (+3c) |
| ATPCH-05WEIHOE | C | +1.20 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** HOE retained @54 (+3c) |
| ATP-05AUGDAV | D | +0.85 | partner never reached: _v4_entry_anchor level vs tape / queue (:2194) / riser_post=0 aim (aim_table.json): bid at the go | — | **-1.90** DAV bid 38c survives, fills, settles LOSS (counted) | — |
| ATP-05HURSTR | C | -3.20 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) / hold-to-settle on the losing leg (exit design; OUT OF | — | — | — |
| ATP-05SAFDJO | A | +0.90 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | — |
| ATP-05SINMOC | A | +0.30 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | — |
| ITFM-05BONBRA | F | -0.65 | partner never reached: _v4_entry_anchor level vs tape / queue (:2194) | — | — | — |
| ITFM-05BOUDOU | C | +1.25 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** DOU retained @72 (+3c) |
| ITFM-05CRIMAR | A | +0.45 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** CRI retained @90 (+3c) |
| ITFM-05DELNIC | C | -3.40 | pre-ruling bound hole (FIXED live 21eaad4 C-BOUND-RULING) (:3977) / riser_post=0 aim (aim_table.json): bid at the going  | — | — | **+3.70** NIC LOST (floor 80 / t) -> -leg pnl -3.70 [pair breaks -> naked risk] |
| ITFM-05ELIAZO | A | +0.05 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **-0.95** AZO LOST (floor 64 / t) -> -leg pnl 0.95 [pair breaks -> naked risk] |
| ITFM-05FARBRO | C | -2.80 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** FAR retained @61 (+3c) |
| ITFM-05GELBRE | A | +1.00 | none charged (grade A) | — | — | — |
| ITFM-05IONDAO | F | -0.50 | placeholder clock window (kalshi_schedule_primary) (:3339) + T-4h lead on that clock (:134) | 0.00 tape: leg1 catchable dip not before fader divot in honest window -> NO CLAIM | — | — |
| ITFM-05LENJON | C | +1.25 | riser adverse selection (C44: fills when the leg fades in) (:1579) | — | — | **+0.15** LEN retained @72 (+3c) |
| ITFM-05MASCIO | F | -1.65 | placeholder clock window (kalshi_schedule_primary) (:3339) + T-4h lead on that clock (:134) | 0.00 tape: leg1 catchable dip not before fader divot in honest window -> NO CLAIM | — | — |
| ITFM-05MCKBER | D | +0.10 | partner never reached: _v4_entry_anchor level vs tape / queue (:2194) / riser_post=0 aim (aim_table.json): bid at the go | — | — | **+0.15** BER retained @93 (+3c) |
| ITFM-05MILRAM | A | +0.30 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **-0.40** RAM LOST (floor None / t) -> -leg pnl 0.40 [pair breaks -> naked risk] |
| ITFM-05MORHAU | B | +0.95 | none charged (grade B) | — | — | **-0.75** HAU LOST (floor 83 / t) -> -leg pnl 0.75 [pair breaks -> naked risk] |
| ITFM-05RECDUB | A | +1.25 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** REC retained @56 (+3c) |
| ITFM-05SABMIS | F | -4.05 | placeholder clock window (kalshi_schedule_primary) (:3339) + T-4h lead on that clock (:134) | 0.00 tape: leg1 catchable dip not before fader divot in honest window -> NO CLAIM | — | — |
| ITFM-05SALCON | C | +0.90 | pre-ruling bound hole (FIXED live 21eaad4 C-BOUND-RULING) (:3977) / riser_post=0 aim (aim_table.json): bid at the going  | — | — | **+0.15** SAL retained @86 (+3c) |
| ITFM-05SHVFAU | F | -0.40 | partner never reached: _v4_entry_anchor level vs tape / queue (:2194) | — | — | — |
| ITFM-05SLOKHR | F | -1.95 | placeholder clock window (kalshi_schedule_primary) (:3339) + T-4h lead on that clock (:134) | 0.00 tape: leg1 catchable dip not before fader divot in honest window -> NO CLAIM | — | — |
| ITFM-05THUGRE | D | +0.00 | partner never reached: _v4_entry_anchor level vs tape / queue (:2194) / riser_post=0 aim (aim_table.json): bid at the go | — | — | 0.00 THU LOST (floor 98 / t) -> -leg pnl 0.00 |
| ITFM-05VANGAU | D | +0.30 | partner never reached: _v4_entry_anchor level vs tape / queue (:2194) | — | — | — |
| ITFM-05XUXCHE | F | -0.10 | placeholder clock window (kalshi_schedule_primary) (:3339) + T-4h lead on that clock (:134) | 0.00 no honest join -> NO CLAIM | — | — |
| ITFW-04BROKOI | F | -2.10 | placeholder clock window (kalshi_schedule_primary) (:3339) + T-4h lead on that clock (:134) | 0.00 tape: leg1 catchable dip not before fader divot in honest window -> NO CLAIM | — | — |
| ITFW-04MAXSTE | F | -0.70 | placeholder clock window (kalshi_schedule_primary) (:3339) + T-4h lead on that clock (:134) | 0.00 no honest join -> NO CLAIM | — | — |
| ITFW-05AITDAE | A | +1.00 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.10** DAE retained @79 (+2c) |
| ITFW-05ALVJOH | F | -3.65 | partner never reached: _v4_entry_anchor level vs tape / queue (:2194) / riser_post=0 aim (aim_table.json): bid at the go | — | — | **+0.10** JOH retained @71 (+2c) |
| ITFW-05BUYCOH | D | +0.20 | placeholder clock window (kalshi_schedule_primary) (:3339) + T-4h lead on that clock (:134) | 0.00 tape: leg1 catchable dip not before fader divot in honest window -> NO CLAIM | — | — |
| ITFW-05COHTSE | B | +0.80 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **-0.65** TSE LOST (floor 85 / t) -> -leg pnl 0.65 [pair breaks -> naked risk] |
| ITFW-05DEKCAK | F | -1.25 | placeholder clock window (kalshi_schedule_primary) (:3339) + T-4h lead on that clock (:134) | 0.00 no honest join -> NO CLAIM | — | — |
| ITFW-05KARMAT | F | -0.05 | placeholder clock window (kalshi_schedule_primary) (:3339) + T-4h lead on that clock (:134) | 0.00 tape: leg1 catchable dip not before fader divot in honest window -> NO CLAIM | — | — |
| ITFW-05KUHEBE | C | -1.15 | riser adverse selection (C44: fills when the leg fades in) (:1579) | — | — | — |
| ITFW-05KULVAN | A | +0.95 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.10** KUL retained @53 (+2c) |
| ITFW-05LIMHAG | F | -0.65 | placeholder clock window (kalshi_schedule_primary) (:3339) + T-4h lead on that clock (:134) | 0.00 tape: leg1 catchable dip not before fader divot in honest window -> NO CLAIM | — | — |
| ITFW-05MONFER | C | +1.15 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.10** FER retained @72 (+2c) |
| ITFW-05MUNGAD | C | -2.35 | riser adverse selection (C44: fills when the leg fades in) (:1579) | — | — | **+0.10** GAD retained @53 (+2c) |
| ITFW-05PRIYUL | A | +0.15 | none charged (grade A) | — | — | **+0.10** PRI retained @87 (+2c) |
| ITFW-05SPIGAR | F | -0.05 | placeholder clock window (kalshi_schedule_primary) (:3339) + T-4h lead on that clock (:134) | 0.00 tape: leg1 catchable dip not before fader divot in honest window -> NO CLAIM | — | — |
| ITFW-05TRAABB | C | +1.10 | riser adverse selection (C44: fills when the leg fades in) (:1579) | — | — | **+0.10** ABB retained @65 (+2c) |
| ITFW-05TUBSOB | B | +1.20 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.10** TUB retained @70 (+2c) |
| ITFW-05VARGRO | D | +0.06 | partner never reached: _v4_entry_anchor level vs tape / queue (:2194) | — | — | — |
| WTACH-05ARSOSU | C | +1.05 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** ARS retained @59 (+3c) |
| WTACH-05BARPOP | B | +1.15 | none charged (grade B) | — | — | **+0.15** POP retained @62 (+3c) |
| WTACH-05BAYMAR | C | -0.50 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) / hold-to-settle on the losing leg (exit design; OUT OF | — | — | **+0.15** MAR retained @68 (+3c) |
| WTACH-05DITLEW | C | +1.15 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** LEW retained @63 (+3c) |
| WTACH-05HERVAI | A | +1.05 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** HER retained @78 (+3c) |
| WTACH-05KOBLEW | A | +0.60 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** KOB retained @86 (+3c) |
| WTACH-05KUDBOU | A | +0.33 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** KUD retained @89 (+3c) |
| WTACH-05MONGIM | B | +1.20 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** MON retained @68 (+3c) |
| WTACH-05MORKOT | C | +0.50 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** KOT retained @88 (+3c) |
| WTACH-05MORNGU | A | +0.50 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **-0.35** NGU LOST (floor 91 / t) -> -leg pnl 0.35 [pair breaks -> naked risk] |
| WTACH-05SMIJAR | A | +0.05 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** SMI retained @78 (+3c) |
| WTACH-05YAMOVC | A | +1.20 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | **+0.15** YAM retained @66 (+3c) |
| WTA-05BENGAU | A | +1.20 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | — |
| WTA-05MUCKRE | D | +1.35 | none charged (grade D) | — | — | — |
| WTA-05PEGJOV | A | +1.30 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) | — | — | — |
| WTA-05SABOSA | C | -3.05 | riser_post=0 aim (aim_table.json): bid at the going rate (:1579) / hold-to-settle on the losing leg (exit design; OUT OF | — | — | — |

## THE LAW (operator ruling 2026-07-05 — same push, into the deploy gate + Vault; lesson C46)
> **NOTHING DEPLOYS WITHOUT OUTCOME PROOF — every code change must be replayed against the prior slate's
> full position set and shown to improve actual outcomes (grades/dollars) before it arms. Lint proves it
> parses, smoke proves it runs, the outcome replay proves it MATTERS. All three or no deploy.**

Enforced: `deploy/deploy_gate.sh` step [3/3] refuses without `OUTCOME_PROOF=<path>` naming a proof doc that
cites the candidate SHA; law text in LESSONS.md C46; Vault §0C (blend/agent-derivation). This document is the
first artifact of the law — and its own verdict is instructive: of the three candidate fixes, only FIX C
shows positive dollars on today's tape; FIX A arms on correctness with shadow-first; FIX B stays shadow.

*Machinery: `.claude/proof_20260705/proof_pass.py` (VPS, read-only) over the refreshed ftr_dump (147 games) +
state/schedule.json honest clock + Kalshi REST prints; raw rows in `proof_rows.json`.*
