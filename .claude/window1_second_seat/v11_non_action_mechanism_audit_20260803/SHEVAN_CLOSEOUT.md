# SHEVAN close-out + floor robustness [ANALYTICAL_ESTIMATE]

Analysis seat only. Read-only. Three parts, one dispatch. Artifacts: tape pack
`game_tape_packs/26JUL12SHEVAN/` (SHE/VAN `_book.csv` + `_trades.csv`, c09bde99 format + depth-5 columns) ·
`SHEVAN_LOWPRINT_FORENSICS.json` · `SHEVAN_V52E_DECISION_STORY.json` · `FLOOR_ROBUSTNESS.json`.
Window `[1783818706, 1783868880]` (T+0 … T+836.2 min); onsets (interim method): SHE T+758.0 · VAN T+752.1.

## PART A — the 1¢ forensics: EXCHANGE-REAL, COLLAPSE-CLASS. Zero strays, zero glitches.

Population: every SHE print ≤5¢ and VAN print ≤49¢ post-onset = **291 prints (SHE 288 / VAN 3)**. Kalshi
cross-check (iceberg method, pagination complete both legs): **291/291 present in the official record, prices
and sizes agreeing — NOT_IN_EXCHANGE_RECORD = 0. No escalation.** Verdicts: **EXCHANGE_REAL_SUSTAINED_MOVE
291 / ISOLATED_STRAY 0.**

What the tape shows, with the sibling beside it:

- **VAN's floor first**: T+772.0–772.3, three prints at **49¢, 3,988 contracts** (book 49/50 at the moment;
  **SHE's book simultaneously 49/45**) — a sustained cluster, 20 minutes *before* the collapse.
- **SHE's collapse**: T+792.5 → T+820.5, **288 prints ≤5¢, ~149,346 contracts**, prices walking 5→4→3→2→**1**
  (39 prints at 1¢, one of 3,350 contracts); taker side "no" throughout (sellers hitting bids); SHE's book
  going (10,7) → (3,2) as it fell. **The sibling did the mirror: VAN's book climbed 87→95→98 through the
  flood.** By the window edge SHE's book stood 22/26 — a partial recovery after the flood.
- Reading, evidence-only: the census's 1¢ SHE floor is not a stray and not a data defect — it is the bottom
  of a genuine, exchange-attested collapse with the pair constraint visibly intact (one side to ~1, the
  other to ~98). The 50¢ census margin is **sequential**, not simultaneous: VAN's 49 printed at T+772,
  SHE's 1 at T+802.

## PART B — the as-if-first-time placement review (V52e trace @ b09aa22b)

| T+min | leg | machine event | cited evidence / license | verified tape then |
|--:|---|---|---|---|
| 0–752 | both | **blocked: STABILITY_ONSET_NOT_REACHED** (SHE 10,010 / VAN 6,375 receipts); read flapping ABSENT ↔ formed (`POST_ONSET_EVIDENCE_GENUINELY_INSUFFICIENT_NO_COMPARABLE_TRANSITION`) | clause ① + clause ② horizon | books wide, thin trade |
| 752.1 | VAN | **ONSET PASSED**; first read **RISING** (`FULL_POST_ONSET_PRINT_AND_BOOK_HISTORY_RECENCY_WEIGHTED_BY_CAUSAL_RANK`) | | |
| 758.0 | SHE | **ONSET PASSED**; first read **RISING** (same evidence law) | | |
| 759.0 | SHE | **bid born @ 35** | authority **V52E_N4_PRIOR_INFORMED_LIVE_BOUND_LEVEL** (the library's level, live-bound); diary 41; pair-lows-sum 99 | |
| 759.0 | VAN | **bid born @ 58**, flickers 57↔58 ×4 on ask moves | authority V52B evidence-backed read level; diary 58; lows-sum 99 | |
| 761.1 | SHE | **reprice 35→34** on `POST_ONSET_BID_DOWN` | diary 36; lows-sum 93 | |
| **761.3 / 759.0** | both | **THE TRACE ENDS — named discrepancy, escalated:** the last receipts sit **4,497 s (~75 min) before the run's own `t_minus_pre_match_boundary`** (SHE receipt row-12317; VAN row-10266), while the verified tape continues to T+836 with 4,904 more SHE book rows. The machine never evaluated the last 75 minutes. Whether the V52e materialization's tape copy ends early or the export truncated is a **Codex-provenance question** — reported, not resolved. | | **T+772: VAN sells 3,988 @ 49** (≤ the standing 58) · **T+792–820: SHE flood to 1¢** (≤ the standing 34) · VAN book climbs to 98 |
| 836.2 | — | (window edge; outside trace) | | SHE book 22/26 |

The question, answered with rows and receipts and left at the operator's eyes: facing this game cold, the
machine waited out 752 minutes of formation lawfully, read RISING on both sides the moment each book woke,
and stood SHE 35→34 (library-informed level) and VAN 58 (read level = its diary) — **both bids standing as
of the trace's last receipt.** Against the verified anatomy: the tape then crossed *both* levels (VAN's
49-cluster at T+772; SHE's flood through 34 at T+792) — **conditional on the rests standing through those
moments, which the truncated trace cannot attest.** No scoring performed.

## PART C — floor robustness, all 612 offered games

Descriptive definition, stated (the operator rules the final line): a print is *isolated* if no other print
sits within 600 s AND within 3¢; a leg floor is *single-isolated* if the floor traded exactly once and that
print is isolated; the *non-isolated floor* is the cheapest print with at least one such neighbor. Both
floors side by side per game in the JSON; census classes untouched.

| | value |
|---|--:|
| offered games scored | 612/612 |
| legs whose floor rests on a single isolated print | **31 of 1,224 (2.5%)** |
| games with ≥1 such leg | 31 |
| floor-print total-size distribution (contracts sold at the floor) | p10 **13.1** · p25 116.9 · median **2,017.8** · p75 12,415.1 |
| games whose margin collapses ≥5¢ under the non-isolated floor | **9 of 612 (1.5%)** |
| margin-drop distribution (the 41 games with any drop) | p25 1 · median 2 · p75 4 |

**The 612 denominator is floor-robust**: the typical offered floor is a ~2,000-contract cluster, not a stray;
under the stated isolation reading only 9 games lose ≥5¢ of margin, and SHEVAN itself — the census's
deepest margin — is collapse-class, not stray-class (Part A).

## Conservation

A: 291 prints = SHE 288 + VAN 3 = 291 sustained + 0 isolated + 0 missing; Kalshi pagination complete 2/2.
B: every machine event carries its receipt; the trace-end discrepancy quantified (4,497 s) and escalated, not
resolved. C: 612 scored / 1,224 legs; 31+9 named; both floors reported per game; no re-cut, no threshold
ruling. Sources: fit-local tapes/prints, Kalshi public API (2026-08-12), V52e trace @ b09aa22b, offer census
@ 22441e05. ANALYTICAL_ESTIMATE.
