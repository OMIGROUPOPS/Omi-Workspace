# ADJUDICATION 20260712 (nightly conviction replay; gate 3a passed)

| id | ticker | cat | fill ET | paid | cyc | grade | posterior | legacy | pnl¢ |
|---|---|---|---|---|---|---|---|---|---|
| T-20260712-0235 | ATPCHALLENGERMATCH-26JUL12CA | ATP_CHALL | 04:22:26 PM | 40 | 1 | AGREE | 0.40 |  | 40.0 |
| T-20260712-0234 | ATPCHALLENGERMATCH-26JUL12YI | ATP_CHALL | 04:46:11 PM | 82 | 1 | AGREE | 0.82 |  | 85.0 |
| T-20260712-0249 | ITFWMATCH-26JUL12PANOUN-OUN | ITF_W | 06:52:06 PM | 55 | 1 | AGREE | 0.66 |  | open |

## LIVE-vs-REPLAY AGREEMENT (same-instrument law, live edition) — checked 2, **divergences: 1**
- **VIOLATION** T-20260712-0249: conf gap 0.58 live vs 0.80 replay (at the shadow's tick)

**MIGRATION METER: fitted-conviction AGREE 3/3 (100.0%) | WOULD-REFUSE 0 | NO-OPINION 0 | pair-97 touched 0 (0.0%)**

Per category: ATP_CHALL A2/R0/N0 p97:0 | ITF_W A1/R0/N0 p97:0

## COMPLETION-SHADOW (per-leg economics beside the live machinery; taker branch GATED behind operator_taker_word)

| cat | verdict | n |
|---|---|---|
| ATP_CHALL | NO-OPINION | 61 |
| ATP_CHALL | flatten_kept | 5 |
| ATP_CHALL | hold | 19 |
| ATP_CHALL | taker_complete | 4 |
| ATP_MAIN | NO-OPINION | 70 |
| ATP_MAIN | hold | 26 |
| ITF_W | NO-OPINION | 12 |
| ITF_W | flatten_kept | 1 |

kept-leg EV sums (¢, two-term frame, win-ride residual excluded): ATP_CHALL -21 | ATP_MAIN +13 | ITF_W -1

## COMPLETION LIVE-vs-SHADOW (operator word 07-12; the same-instrument law, completion edition) — actions: 3, divergences: 1
- action flatten_kept → flattening on KXATPCHALLENGERMATCH-26JUL12TOKROZ
- action flatten_kept → flattening on KXITFWMATCH-26JUL12PANOUN
- action taker_complete → crossed on KXATPCHALLENGERMATCH-26JUL13VILGAN
- **VIOLATION** shadow said flatten_kept on KXATPCHALLENGERMATCH-26JUL12CALRAD but NO action followed

## GOVERNOR SPLIT (whose hand moved — actions | exit ¢ attributed)
- per_leg_policy: 1 actions | +0¢
- pair97_bound: 8 actions | +0¢
- maker_exit: 1 actions | +305¢
- match_live_cancel: 0 actions | +0¢

## FULL-SLATE SUMMARY
FULL-SLATE: steps FITTED 44%/DECREED 52%/NAKED 1 | no-fill 17 (starved 8) | xt-violations 114
