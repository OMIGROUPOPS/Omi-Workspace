# Honest fill-model receipt — NIKVRB and HURBIG

This package replaces the replay's later-receipt convention with three receipt classes. It is score-free and does not rerun either game.

Result: 0 PROVEN_MAKER, 3 PROVEN_TAKER, and 1 UNPROVEN leg rows. 3 of four leg credits survive. 1 of two pairs remains complete.

| category | price region | event/leg | action scheduled / bell | bid/ask/last; spread; dwell | X / ask capacity | seller prints through X before replay credit | class | honest credit |
|---|---|---|---|---|---|---:|---|---|
| ATP_CHALL | 51_75 | KXATPCHALLENGERMATCH-26JUL19HURBIG/BIG | T-254:11 / T-344:11 | 54/55/55; 1; 13459s | 55 / 817 | 0 | PROVEN_TAKER | YES |
| ATP_CHALL | 26_50 | KXATPCHALLENGERMATCH-26JUL19HURBIG/HUR | T-98:34 / T-188:34 | 37/38/38; 1; 446s | 38 / 10113 | 0 | UNPROVEN | NO |
| ATP_CHALL | 26_50 | KXATPCHALLENGERMATCH-26JUL19NIKVRB/NIK | T-38:02 / T-43:02 | 17/18/18; 1; 12s | 18 / 1201 | 0 | PROVEN_TAKER | YES |
| ATP_CHALL | 51_75 | KXATPCHALLENGERMATCH-26JUL19NIKVRB/VRB | T-314:06 / T-319:06 | 67/68/70; 1; 32s | 68 / 110 | 0 | PROVEN_TAKER | YES |

## Pair rescoring

| event | leg classes | completed? |
|---|---|---|
| KXATPCHALLENGERMATCH-26JUL19HURBIG | BIG=PROVEN_TAKER, HUR=UNPROVEN | NO |
| KXATPCHALLENGERMATCH-26JUL19NIKVRB | NIK=PROVEN_TAKER, VRB=PROVEN_TAKER | YES |

No PROVEN_MAKER fill survives. NIKVRB survives only as two PROVEN_TAKER legs and therefore requires taker-fee arithmetic outside this score-free receipt. HURBIG does not complete because HUR's own-leg book was 43 seconds old at the sibling-triggered action timestamp, so opposing size at submission is not proven.

The true-print and book clocks share normalized Unix epoch and are directly comparable across distinct seconds. Cross-stream order inside one second is not authoritative because the book stream has second precision while prints retain fractional seconds.
