# Game-read rest placement — the adaptive read priced against fixed k

Analysis seat only. Read-only. V36 trace `bfde0d8` supplies per-receipt state + running
evidence low; **tape best-bid** supplies the placement (identical source to the sealed
baseline). Scored against certified seller flow (≥5 lots, level-touched, lazy-leg-1)
exactly as the k-curve. Baseline: `d40bc010` k=1 = $20.03 / 106 pairs. Machine artifact:
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/ADAPTIVE_REST_PLACEMENT.json`.

**The adaptive rule (the campaign's own reads):** at every receipt, place the rest per the
state machine — `FALLING → 1¢ below the fall's running evidence low`; `SETTLED / RISING →
1¢ under current best bid`. No constant k; the read moves the rest.

## Basis check

Recomputing fixed k on the tape best-bid reproduces the sealed baseline exactly:
**k=1 = $20.03, 106 pairs.** The comparison below is apples-to-apples on that source.

## The head-to-head (1-lot, maker-only, zero fee)

| placement | legs filled | pairs <100 | **book $** |
|---|--:|--:|--:|
| **fixed k=1** | 556 | **106** | **$20.03** |
| **game-read ADAPTIVE** | 583 | 102 | **$16.17** |
| fixed k=2 | 226 | 59 | $15.39 |
| fixed k=3 | 166 | 48 | $13.25 |
| fixed k=5 | 114 | 37 | $11.72 |
| fixed k=8 | 86 | 27 | $10.01 |

**The game-read adaptive placement LOSES to naive k=1 — $16.17 vs $20.03 (−19%).** It fills
more *legs* (583) but completes fewer *pairs* (102) at a lower book value. The read beats
every *deeper* fixed k (k≥2), but that is faint praise — the depth curve already showed
deeper is worse; adaptive is just a smarter way to be too deep some of the time.

## Per category (the category law, min-n)

| category | ADAPTIVE $ | k=1 $ | winner | evidence |
|---|--:|--:|---|---|
| ATP_CHALL | 7.27 | **9.71** | **k=1** | native n≥30 |
| ATP_MAIN | 4.19 | **4.80** | **k=1** | native n≥30 |
| WTA_CHALL | 3.05 | 3.05 | tie | POOLED (<30) |
| WTA_MAIN | 1.66 | **2.47** | **k=1** | POOLED (<30) |

**Fixed k=1 wins 3 of 4 categories** and ties the fourth; the two ATP cells (native
evidence) both favor k=1. Nowhere does the adaptive read win outright on native evidence.

## Where the read pays — and where it costs

- **BOSCOP-class (adaptive beats every fixed k): 26 games.** These are where the FALLING
  read placed *below* the running low and a deeper seller sweep paid: ECHMUN 20¢ vs 15¢,
  KUMTUR 35¢ vs 34¢, MARARS 21¢ vs 20¢, plus a handful (OUAFER, PALMAR) that **no fixed k
  completes at all**. Real, but the wins are mostly small (+1–5¢).
- **Read-wrong losses (k=1 beats adaptive): 39 games — and they are large.** BROGIU 43¢ vs
  65¢ (−22¢), HERALM 66¢ vs 92¢ (−26¢), HECISO 33¢ vs 58¢ (−25¢); BALPET/FORPAM the pair
  k=1 completes and adaptive does not. When the FALLING read placed below the evidence low
  and the seller *didn't* sweep that deep, the rest simply missed a fill that k=1's 1¢-under
  bid would have caught.

**26 small wins vs 39 large losses = the read is net-negative (−$3.86).** The asymmetry is
the story: reading FALLING and dropping deeper is a bet that the fall continues; when it
does you gain a few cents, when it stalls you lose the whole fill.

## Verdict

The drift thesis's *adaptive* form is **refuted**: letting the campaign's own state read
move the rest deeper on FALLING legs **loses 19% of book value** to a fixed 1¢-under-bid
tracker, and loses 3 of 4 categories on native evidence. The BOSCOP class is real (26
games where the read caught a deeper sweep) but rare and small, swamped by 39 larger
read-wrong misses. **The single best placement remains fixed k=1** — the naive tracker the
depth curve already crowned. Reading the game does not beat one cent under the bid.

## Conservation

1,608 legs; 1,268 with ≥5-lot seller flow. k=1 reproduces sealed $20.03 / 106 pairs
(basis validated). Adaptive 583 legs / 102 pairs / $16.17. Fixed-k ladder 106/59/48/37/27
pairs, $20.03/15.39/13.25/11.72/10.01. BOSCOP-class 26; read-wrong losses 39; net −$3.86.
Per category k=1 wins ATP_CHALL/ATP_MAIN/WTA_MAIN, ties WTA_CHALL.
