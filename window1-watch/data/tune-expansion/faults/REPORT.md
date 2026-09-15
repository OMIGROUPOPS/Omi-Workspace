# Fault taxonomy — frozen 100, native OS 70b68856

No engine edit, replay, fitting or redraw. The remaining 704 were not run.
All evidence is derived from the saved native trace, corrected grade, selected
positive-size print tape, and pinned tick library. Original grade files remain
unchanged. See RECEIPT.json for exact source hashes and definitions.

## Counts

Multi-label counts below are **failed sides**, not games. There are 78 failed
sides after the three safety exclusions, plus 10 sides with unknown spans.
Unknown spans are E but are listed separately from execution failures.

| Tour | Failed sides | A below path | B first call >3¢ off | C safety | D thin tape | E other | E unknown span | A and B |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ATP_MAIN | 15 | 15 | 2 | 0 | 1 | 0 | 0 | 2 |
| ATP_CHALL | 38 | 28 | 3 | 2 | 7 | 4 | 4 | 1 |
| WTA_MAIN | 11 | 10 | 1 | 0 | 1 | 1 | 2 | 1 |
| WTA_CHALL | 14 | 12 | 1 | 1 | 1 | 1 | 4 | 1 |
| ALL | 78 | 65 | 7 | 3 | 10 | 6 | 10 | 5 |

Game incidence (overlapping): A 58, B 7, C 3, D 9; E 5 known-span games
plus 5 unknown-span games. Five games have A and B on the same failed side.

## A: floor already gone versus bid too deep

Use the first qualifying PLACE/REPRICE in receipt order for each A side.
All price-setting actions are retained in each game's JSON; no successful-side
first call was substituted. A needs a later observed positive print; an empty
future tape is not evidence that a bid was too deep.

| Tour | Floor before only | Bid below floor only | Both | Total A sides |
|---|---:|---:|---:|---:|
| ATP_MAIN | 2 | 4 | 9 | 15 |
| ATP_CHALL | 5 | 6 | 17 | 28 |
| WTA_MAIN | 1 | 2 | 7 | 10 |
| WTA_CHALL | 2 | 5 | 5 | 12 |
| ALL | 10 | 17 | 38 | 65 |

Thus 48/65 had already seen their full-span floor; 55/65 bid below that floor;
38 satisfy both. Across any qualifying price-setting action, 58 sides have a
floor-before-placement case, 56 have a below-floor bid, and 20 actually bid at
the recorded floor after it had passed. These are retrospective descriptions,
not proof that an earlier maker fill would have been available.

## D: thresholds from this draw, not trading parameters

N is the lower inverse-CDF 10th percentile of positive-print counts across all
known-span sides in each tour, including zeros; D means count strictly below N.

| Tour | Known-span sides | N |
|---|---:|---:|
| ATP_MAIN | 36 | 16 |
| ATP_CHALL | 88 | 7 |
| WTA_MAIN | 36 | 22 |
| WTA_CHALL | 30 | 3 |

Unknown spans never enter this calculation. Thin recorded tape is not proof of
an illiquid exchange market; it can also reflect incomplete observation.

## C: credit removed

GRESAN/GRE (Jul 16), ARNPOH/ARN (Jul 19), and GAOVAL/GAO (Jul 16) have stored
same-second fill flags. Consult each game's C record for the exact leg and
receipt. Each pair's 1¢ replay credit is excluded; the original F card remains.
Audited totals: **27 completed, 58 one-sided, 10 unfilled, 5 unknown spans;
32/361¢ captured on 83 positive-offer games (0.386¢ per offered game).**
The tied-open DROUGO denominator limitation and BARREI missing floor remain
explicit; this audit does not repair or silently change the grader.

## Open first

- A: GANZIN — GAN bid 20¢ with Q 20¢, 6.14 minutes after its 17¢ floor.
  The three later positive prints never fell below 30¢.
- B: URSPAL — URS first eligible Q 63¢ versus floor 57¢; pool 294, ESS 126.99;
  called CLIMBER versus realized NOT_CALLABLE. Its five highest-weight members
  and their first prices/dates are in the game JSON, reproduced with stored
  member-count/weight-sum/ESS parity, not falsely claimed to be logged IDs.
- C: GRESAN — GRE's fill has zero current-price age but 44.20 minutes of order
  lineage; the price change and its fill occurred in the same second.
- D: BINFUE — BIN has three positive prints versus this tour's N=7.
- E: DEMBIT — BIT never posted; the last stored reason is
  LOCKED_BOOK_PLACEMENT_ONLY_EXISTING_REST_HELD.

## Astra

A identifies our bid's mismatch with the later path, B a bad initial level,
and C an unequivocal execution-accounting failure; these are the machine's
responsibility to explain, although A alone does not prove that a better bid
was knowable then. D belongs to the available market evidence, not necessarily
the market itself. E is mixed: book constraints, pair-budget constraints, and
missing rulers must not be collapsed into a forecasting verdict. The clearest
first opens are GANZIN (A), URSPAL (B), GRESAN (C), BINFUE (D), and DEMBIT (E).
Only five of 65 A sides also meet B: a large first-call miss is not the dominant
description of the unfilled bids in this draw.

## Static delivery

Only the selected100 plus the existing four other demo games are allowlisted.
The four existing games retain their already-published asset bytes. Full stage
and accountability files total 2,536,473,842 bytes and stay local; no raw prints,
engine, credentials, or remaining704 assets are uploaded. Lossless HTTP gzip
preserves the original face/grade/oracle JSON hashes.
Routing uses the documented [Vercel Build Output API](https://vercel.com/docs/build-output-api/configuration).
