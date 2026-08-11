# The ratchet audit — riser dips at climbing rungs, and the last profitable rung

Analysis seat only. Read-only. Population = `f40ac8ea` (sealed 12 + dev 62 riser-side unfilled) **plus 30 credited dev risers as calibration** (sha1-deterministic pick). Per leg, the full post-lawful-stand ask series: every dip-and-resume at **any** level. Boundary **B(t) = 99 − sibling's contemporaneous qualified-ask-low** (running ≥10 s-dwell ask minimum — decision-time observable, the machine's own organ). A dip is **catchable** iff its trough ≤ B(t). Machine artifact: `…/RATCHET_AUDIT.json` (per-leg rows incl. miss points).

## The three sets, side by side

| set | n | legs w/ dips | no-dip | median dips | median rungs | asc share | catchable legs | best ¢ | all-over-par legs |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| sealed unfilled | 12 | 4 | 8 | 0 | 1 | 0.2 | 0 | 0 | 4 |
| dev unfilled | 62 | 27 | 35 | 0 | 1 | 0.0 | 5 | 5 | 22 |
| **filled calibration** | 30 | 28 | 2 | 5 | 2 | 0.02 | 11 | 27 | 17 |

## (1) The ratchet — there isn't one

Median ascending-share of successive troughs: **0.0 (dev unfilled), 0.2 (sealed), 0.02 (filled)** — successive dips do **not** climb an orderly ladder anywhere; median rung count is 1-2. The 'climbing rungs' picture is wrong on this tape: dips are sparse, irregular, and non-monotone.

## (2) The catchable set — thin to empty

- **Sealed unfilled**: of the 4 legs with dips, **0 catchable** — every trough sat above the last profitable rung.
- **Dev unfilled**: **5 of 27** dip-legs had a catchable rung, worth **+5¢ total** (~1¢ each); **22** legs' dips were all over-par.
- **Filled calibration**: 11 of 28 catchable (+27¢) — even on winners the boundary admits under half.

**The controlling contrast is dip supply, not policy**: the filled risers saw a **median 5 dips** post-stand; the unfilled saw a **median 0**. Risers that fill are risers that dip. The unfilled class isn't refusing catchable rungs — the rungs never formed (43 of 74 legs dipless), and where they formed they sat over par.

## (3) The miss point + patience gauge

Per-leg miss points (last catchable dip, remaining window, sibling read at that moment) are in the JSON rows. On the 5 dev catchable legs the sibling side stayed collectable to the window edge (the boundary B(t) is monotone non-decreasing — the sibling's observed floor only deepens), so **patience was never the binding constraint**: the riser's rung supply was. Where a catchable rung existed, hours typically remained after it — the miss is placement at the rung, not haste.

## Named exemplars

- **26JUL13BOUZHA·ZHA** (dev, catchable missed): 109 dips / 2 rungs, 108 catchable, best +1¢; last rung 07-13 14:35, 9h left, sibling read RISING
- **26JUL19PALMUN·MUN** (dev, catchable missed): 3 dips / 1 rungs, 1 catchable, best +1¢; last rung 07-19 12:58, 0h left, sibling read FALLING
- **26JUL19VUKGEA·GEA** (dev, catchable missed): 59 dips / 5 rungs, 5 catchable, best +1¢; last rung 07-19 19:16, 0h left, sibling read RISING
- **26JUL20WINARS·ARS** (dev, catchable missed): 1 dips / 1 rungs, 1 catchable, best +1¢; last rung 07-20 15:07, 0h left, sibling read FALLING
- **26JUL13TIMANN·TIM** (dev, catchable missed): 4 dips / 3 rungs, 1 catchable, best +1¢; last rung 07-13 18:50, 23h left, sibling read RISING
- **26JUL13WINKIR·KIR** (dev, all-over-par): 25 dips / 2 rungs, 0 catchable
- **26JUL15LAJKRU·LAJ** (dev, all-over-par): 3 dips / 1 rungs, 0 catchable
- **26JUL15SHIBOU·BOU** (dev, all-over-par): 2 dips / 1 rungs, 0 catchable
- **26JUL27BOSROD·BOS** (sealed): 1 dips, 0 catchable
- **26JUL27MONMAZ·MON** (sealed): 1 dips, 0 catchable
- **26JUL28POLDAL·DAL** (sealed): 6 dips, 0 catchable

## Conservation

Sealed 12 + dev 62 + calibration 30 legs, all analyzed (0 no-tape). Catchable pairs: sealed 0 · dev 5 (+5¢) · calibration 11 (+27¢). Boundary = 99 − sibling running qualified-ask-low (≥10 s dwell). Dip = ask run below both neighbors, post-lawful-stand. Sources f40ac8ea, b26cf548, e177c2fb, 2bae8931, fb74c8b8; tapes fit-local + exam private + holdout-exam.