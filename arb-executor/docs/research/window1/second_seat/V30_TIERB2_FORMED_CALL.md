# Tier B2 — role-call at formed books (the game-row architecture test)

Analysis seat only. Read-only. Same oracle as `V30_READMOMENT_CEILING` (Tier A at
4aee323f) — unchanged. Only the **role-call instant** moves. Machine artifact:
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/V30_TIERB2_FORMED_CALL.json`.

## What changed

`call_moment` = the first instant **both** legs hold a two-sided book with
`0 ≤ spread ≤ 2c`, dwelled ≥10 s — admission descent no longer forces the call. Causal
signals in `[call−180s, call]`, plus a **fourth signal**: the crossed-book flag
(`bid ≥ ask` in the window ⇒ chased). Role rule:
`D = ask_walk_down − bid_stack − 2·crossed_flag`; **PATIENT = strictly higher D**.

## Conservation — 804

804 = **767 RESOLVED** + 19 READ_NEVER_RESOLVED + 13 UNDETERMINED_CLOSE + **5
CALL_NEVER_FORMED** (books never held two-sided ≤2c for 10 s).

## The headline — and the trap

| metric | value |
|---|---|
| role accuracy **as-run** (tie→patient) | 391/493 = **79.3%** |
| **ties** (`D_patient == D_chased`) | **270 / 493 = 54.8%** (258 are D=0, flat books) |
| role accuracy **tie-neutral** (ties = uncallable) | **121/223 = 54.3%** |
| read-moment baseline (Tier B1) | 57.1% |

The as-run 79.3% is an **artifact**. My tie-break assigned every `D_p == D_c` tie to
the oracle's patient side, auto-scoring all 270 ties "correct." **258 of those ties are
D=0** — at `call_moment` the best-ask has not walked, the best-bid has not stacked, and
there is no cross: the book is **flat**, carrying no micro-signal at all. Strip the
auto-scored ties and accuracy falls to **54.3%** — coin-flip, and *below* the 57.1%
read-moment baseline. Per category, tie-neutral: ATP_CHALL 53.6%, ATP_MAIN 53.8%,
WTA_CHALL 58.3%, WTA_MAIN 52.6% — uniformly at chance.

## The race (179 Tier A events)

Independent of the role call, the *timing* is fine: `call_moment` precedes the patient
floor in **162 / 179** (won), loses 16, never-forms 1. Won-slack is large — median
**273 min**, p90 802 min — so when you can call, you call hours before the floor. The
race is not the problem; the **call** is.

## Revised V30 ceiling

| definition | ceiling |
|---|---:|
| read-moment (Tier B1) | 24 |
| formed-call **as-run** (tie-inflated) | 86 |
| formed-call **tie-neutral** (honest) | **20** |

Tie-neutral revised ceiling = Tier A ∧ race-won ∧ strict-signal role-correct = **20**
(ATP_CHALL 12, ATP_MAIN 4, WTA_CHALL 2, WTA_MAIN 2). Of the as-run 86, **66 were flat
ties** that only "passed" by the tie-break.

## Verdict — with receipts

**COIN_FLIP_ON_INFORMATIVE_FORMED_BOOKS — the game-row role architecture is dead.**
Moving the call to formed books did not rescue it. Receipts:

1. **54.8% of scored calls are ties**, 258 of them perfectly flat (D=0) — the ARNROM
   micro-signature simply is not present in the book at the call instant.
2. On the **223 events that do carry a strict signal differential, accuracy is 54.3%** —
   statistically indistinguishable from a coin flip, and no better than the 57.1%
   read-moment call.
3. **ARNROM itself is a D=0 tie** at its call (07-13 04:07 ET; patient ROM / chased ARN
   signals both `ask_walk_down=0, bid_stack=0, crossed=0`). Its famous pinned-ask /
   walking-ask signature is a *macro-hour* phenomenon, not readable in the ±180 s book
   micro-window at any single call instant.

The role cannot be called from single-moment game-row book signals. If V30 is to
separate PATIENT from CHASED, it needs a path-integrated / cross-leg feature (the
trajectory over the descent, not a snapshot), not a formed-book micro-read. The
snapshot architecture is falsified here.
