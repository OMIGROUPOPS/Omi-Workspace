# Asymmetric + spread-split re-score of the predictability census

Analysis seat only. Descriptive. Read-only, same isolation (no estimator
artifacts), same population and read-moments as `LANDING_PREDICTABILITY_CEILING.md`,
audited closes from commit 50ce0f49. Maker's one-sided loss on BID and MID reads,
split by spread-at-read regime. Rows in `ASYMMETRIC_SPREAD_LEGS.csv`; grids in
`ASYMMETRIC_SPREAD_SUMMARY.json`.

## Method

Qualified row = ≥10s dwell at the read book (all covered legs qualify by the
read-moment construction). Each cell scored separately by spread-at-read regime:
**≤1c / 2-3c / >3c**. Maker = one-sided entrant; per predictor (BID, MID):

- **P** = P(predictor ≤ audited close) — the good-entry probability (landed at/below
  the close).
- **shortfall** = mean(predictor − close | predictor > close) — the one-sided loss
  when you buy above the landing.
- **drift** = mean(close − predictor), signed.

## Conservation

**1,512 covered + 96 uncovered = 1,608** (printed beside every table). Scoring is on
the 1,512 covered; the 16 cells × 3 regimes partition them exactly.

## The climb cells — BID / MID by spread regime

| cell | regime | n | qshr | BID P | BID sf | BID drift | MID P | MID sf | MID drift |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ATP_CHALL 51_75 | ≤1c | 118 | .48 | .83 | 6.50 | +1.64 | .72 | 4.44 | +1.14 |
| | 2-3c | 110 | .45 | .84 | 3.22 | +2.94 | .78 | 3.58 | +1.78 |
| | >3c | 17 | .07 | 1.00 | 0.0 | +38.9 | .88 | 5.75 | +11.5 |
| ATP_MAIN 51_75 | ≤1c | 70 | .67 | .73 | 2.37 | +3.33 | .67 | 2.46 | +2.88 |
| | 2-3c | 24 | .23 | .92 | 2.00 | +3.12 | .88 | 2.33 | +2.04 |
| | >3c | 10 | .10 | .90 | 21.0 | +16.1 | .60 | 12.0 | +3.20 |
| WTA_MAIN 51_75 | ≤1c | 58 | .70 | .91 | 5.80 | +3.09 | .79 | 2.92 | +2.59 |
| | 2-3c | 20 | .24 | .90 | 1.00 | +2.90 | .80 | 1.38 | +1.82 |
| | >3c | 5 | .06 | 1.00 | 0.0 | +8.20 | 1.00 | 0.0 | +5.50 |
| WTA_CHALL 51_75 | ≤1c | 57 | .68 | .91 | 24.8 | +4.33 | .81 | 11.8 | +3.83 |
| | 2-3c | 26 | .31 | .89 | 37.3 | +3.23 | .77 | 19.8 | +2.12 |
| | >3c | 1 | .01 | 1.00 | 0.0 | +5.00 | 1.00 | 0.0 | +3.00 |
| WTA_CHALL ge76 | ≤1c | 25 | .60 | .80 | 8.20 | +1.60 | .68 | 5.62 | +1.10 |
| | 2-3c | 14 | .33 | .86 | 38.5 | +2.64 | .86 | 39.8 | +1.50 |
| | >3c | 3 | .07 | 1.00 | 0.0 | +55.0 | 1.00 | 0.0 | +25.7 |

Full 16-cell × 3-regime grid in the JSON.

## THE KILLER TEST — does the climb survive tight (≤1c) books?

MID drift (close − mid) by regime, and the share of the all-book climb surviving in
≤1c:

| cell | drift all | drift ≤1c | n ≤1c | drift >3c | survival | verdict |
|---|---:|---:|---:|---:|---:|---|
| ATP_MAIN 51_75 | +2.72 | **+2.88** | 70 | +3.20 | 106% | **REAL_CLIMB** |
| WTA_MAIN 51_75 | +2.58 | **+2.59** | 58 | +5.50 | 100% | **REAL_CLIMB** |
| WTA_CHALL 51_75 | +3.29 | **+3.83** | 57 | +3.00 | 116% | **REAL_CLIMB** |
| ATP_CHALL 51_75 | +2.14 | +1.14 | 118 | +11.5 | 53% | MARGINAL |
| WTA_CHALL ge76 | +2.99 | +1.10 | 25 | +25.7 | **37%** | **SPREAD_DOMINATED — do not wire** |

Three cells (ATP_MAIN, WTA_MAIN, WTA_CHALL 51_75) carry their full climb into tight
books — a real, wire-worthy signal. ATP_CHALL 51_75 keeps half (+1.14 tight vs
+2.14 all). **WTA_CHALL ge76 keeps only 37%** — its "+2.99" climb is really a
wide-book effect (+25.7 in >3c books, +1.10 in tight). It fails the killer test:
the ge76 climb is a spread artifact and must never be wired.

## AUTHORITY MAP — BID-anchored, P ≥ 70% AND shortfall ≤ 2c

The one-sided maker's real risk is the **fall-tail**: when the leg drops below your
resting bid it settles well above the close. That tail sets the shortfall.

**Zero ≤1c cells qualify.** Every tight-book cell has BID shortfall > 2c — even the
strongest climb cells (WTA_MAIN 51_75 ≤1c: P .91 but shortfall 5.80; WTA_CHALL
51_75 ≤1c: shortfall 24.8). In tight books there is no cell where resting at the
bid reliably lands at/below close with a bounded downside.

**Genuine authority = 5 cells, all 2-3c (105 legs):**

| cell | regime | n | BID P | shortfall | drift |
|---|---|---:|---:|---:|---:|
| WTA_MAIN ge76 | 2-3c | 11 | 1.00 | 0.0 | +2.27 |
| ATP_MAIN 51_75 | 2-3c | 24 | .92 | 2.0 | +3.12 |
| WTA_MAIN 51_75 | 2-3c | 20 | .90 | 1.0 | +2.90 |
| ATP_CHALL le25 | 2-3c | 36 | .89 | 2.0 | +3.22 |
| WTA_MAIN le25 | 2-3c | 14 | .86 | 2.0 | +1.29 |

**Excluded — 8 wide-book (>3c) spread artifacts (47 legs):** ATP_CHALL 51_75/ge76,
ATP_MAIN le25, WTA_MAIN 51_75/ge76/26_50, WTA_CHALL 51_75/ge76 — all show BID P=1.0
with drift +4 to +55, because a >3c bid is trivially far below the close. That is
not authority; it is the spread. V26 authorizing on any of these is leaning on
wide-book noise.

**The map V26's fitted authority must land inside is the 5 genuine 2-3c cells.**
Any cell × regime V26 authorizes outside it — in particular any ≤1c bid-anchored
authorization (the fall-tail forbids it here) or any >3c authorization — is a
cross-seat finding to reconcile against this independent map.

## Reading

Splitting by spread turns the earlier "climb" flags into a sharper verdict: the
51_75 climb is real and survives tight books in three categories (ATP_MAIN,
WTA_MAIN, WTA_CHALL), half-real in ATP_CHALL, and a pure wide-book artifact in
WTA_CHALL ge76. But a real climb is not a safe entry: the one-sided maker's
fall-tail keeps shortfall above 2c in every tight book, so BID-anchored authority
exists only in the moderate 2-3c regime, and only in 5 cells / 105 legs. The
independent authority map is small and specific; it is the boundary V26's fitted
authority is checked against.

## Artifacts

`ASYMMETRIC_SPREAD_LEGS.csv` (per leg: spread regime, bid, mid, close, signed
errors) and `ASYMMETRIC_SPREAD_SUMMARY.json` (per cell × regime, killer test,
authority map).
