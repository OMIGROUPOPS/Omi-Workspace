# Stable same-price ask confirmation — two-game and five-game cold replay

Score-free. No 804 replay. All five validation events were excluded before the quote-shape library was fitted.

Raw five-game replay: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/quote_shape_stable_ask_20260731/FIVE_GAME_REPLAY.json

Summary and per-leg references: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/quote_shape_stable_ask_20260731/FIVE_GAME_SUMMARY.json

Transition receipt: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/refs/heads/codex/window1-live-consolidated/.claude/window1_live_v4_replay/quote_shape_stable_ask_20260731/STABLE_SAME_PRICE_TRANSITION_RECEIPT.json

## Per-leg result

| Event | Category | Leg | Status | Entry | Independent pair ref | Pair delta | Own W1 close | Delta | Bell | Delta | Ask-reachable low | Delta | Stable same-price rule |
|---|---|---|---|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| KXATPCHALLENGERMATCH-26JUL19HURBIG | ATP_CHALL | BIG | CREDITED | 55 | NOT_BOUND | NOT_BOUND | 60 | -5 | 60 | -5 | 55 | +0 | FIRED |
| KXATPCHALLENGERMATCH-26JUL19HURBIG | ATP_CHALL | HUR | CREDITED | 38 | NOT_BOUND | NOT_BOUND | 42 | -4 | 42 | -4 | 37 | +1 | DID_NOT_FIRE |
| KXATPCHALLENGERMATCH-26JUL19NIKVRB | ATP_CHALL | NIK | CREDITED | 18 | NOT_BOUND | NOT_BOUND | 19 | -1 | 19 | -1 | 18 | +0 | DID_NOT_FIRE |
| KXATPCHALLENGERMATCH-26JUL19NIKVRB | ATP_CHALL | VRB | CREDITED | 68 | NOT_BOUND | NOT_BOUND | 83 | -15 | 83 | -15 | 68 | +0 | DID_NOT_FIRE |
| KXATPMATCH-26JUL12LAJVAN | ATP_MAIN | LAJ | INSUFFICIENT_EVIDENCE | NULL | NOT_BOUND | NOT_BOUND | 45 | NULL | 45 | NULL | 45 | NULL | DID_NOT_FIRE |
| KXATPMATCH-26JUL12LAJVAN | ATP_MAIN | VAN | INSUFFICIENT_EVIDENCE | NULL | NOT_BOUND | NOT_BOUND | 57 | NULL | 57 | NULL | 50 | NULL | DID_NOT_FIRE |
| KXWTACHALLENGERMATCH-26JUL16BRAVED | WTA_CHALL | BRA | INSUFFICIENT_EVIDENCE | NULL | NOT_BOUND | NOT_BOUND | 44 | NULL | 44 | NULL | 40 | NULL | DID_NOT_FIRE |
| KXWTACHALLENGERMATCH-26JUL16BRAVED | WTA_CHALL | VED | INSUFFICIENT_EVIDENCE | NULL | NOT_BOUND | NOT_BOUND | 57 | NULL | 57 | NULL | 57 | NULL | DID_NOT_FIRE |
| KXWTAMATCH-26JUL20KORJIM | WTA_MAIN | JIM | INSUFFICIENT_EVIDENCE | NULL | NOT_BOUND | NOT_BOUND | 32 | NULL | 32 | NULL | 30 | NULL | DID_NOT_FIRE |
| KXWTAMATCH-26JUL20KORJIM | WTA_MAIN | KOR | INSUFFICIENT_EVIDENCE | NULL | NOT_BOUND | NOT_BOUND | 70 | NULL | 70 | NULL | 60 | NULL | DID_NOT_FIRE |

## Pair delta against both own closes

| Event | Completed | Combined entry | Combined own closes | Signed delta |
|---|---|---:|---:|---:|
| KXATPCHALLENGERMATCH-26JUL19HURBIG | true | 93 | 102 | -9 |
| KXATPCHALLENGERMATCH-26JUL19NIKVRB | true | 86 | 102 | -16 |
| KXATPMATCH-26JUL12LAJVAN | false | NULL | 102 | NULL |
| KXWTACHALLENGERMATCH-26JUL16BRAVED | false | NULL | 101 | NULL |
| KXWTAMATCH-26JUL20KORJIM | false | NULL | 102 | NULL |

## Causal law

The same-price confirmation is an own-book receipt, not elapsed sibling-clock time. Placement may use it only after the inverse sibling direction is independently resolved. The placement receipt cannot fill the new order; credit requires a distinct own ask receipt with a strictly later source timestamp and proven five-contract displayed capacity.

## Validation boundary

This is five predeclared exact-start games, not the 804. No scoring, tuning, ranking, or population conclusion is authorized.
