# Maker-role receipt addendum

The previous blanket receipt-level TAKER ruling is retracted. All four actions were marketable if submitted unchanged, but the replay contains no exchange submission, acknowledgement, liquidity-role, or fee receipt. The receipt-proven role and fee treatment are NOT_ESTABLISHED. The delayed credit is imposed by the simulator and does not prove resting.

| event | leg | action clocks scheduled/bell | bid/ask/last | own-book age | X | displayed ask size | replay credit delay/rows | receipt role/fee | unchanged submission | live maker clamp | ask later reached clamp? | 10s/5-lot proof at clamp? |
|---|---|---|---|---:|---:|---:|---|---|---|---|---|---|
| KXATPCHALLENGERMATCH-26JUL19HURBIG | BIG | T-254:11 / T-344:11 | 54/55/55 | 0s | 55 | 817 | 5s / 5 | NOT_ESTABLISHED / NOT_ESTABLISHED | MARKETABLE_TAKER | 54 JOINING_BID | NO | NO |
| KXATPCHALLENGERMATCH-26JUL19HURBIG | HUR | T-98:34 / T-188:34 | 37/38/38 | 43s | 38 | 10113 | 1s / 2 | NOT_ESTABLISHED / NOT_ESTABLISHED | MARKETABLE_TAKER | 37 JOINING_BID | YES | YES |
| KXATPCHALLENGERMATCH-26JUL19NIKVRB | NIK | T-38:02 / T-43:02 | 17/18/18 | 0s | 18 | 1201 | 1s / 7 | NOT_ESTABLISHED / NOT_ESTABLISHED | MARKETABLE_TAKER | 17 JOINING_BID | NO | NO |
| KXATPCHALLENGERMATCH-26JUL19NIKVRB | VRB | T-314:06 / T-319:06 | 67/68/70 | 0s | 68 | 110 | 881s / 263 | NOT_ESTABLISHED / NOT_ESTABLISHED | MARKETABLE_TAKER | 67 JOINING_BID | NO | NO |

A buy cannot join an existing sell queue at the same price: if sent unchanged while that ask remains, it crosses. Conversely, the simulator's distinct later credit receipt does not prove that an exchange order rested; the replay intentionally withholds same-receipt credit. HUR is additionally based on a 43-second-old own-book snapshot at the sibling-triggered action instant.

At the live post-only clamp, only HUR has later 10-second/five-contract ask proof (37). BIG at 54, NIK at 17, and VRB at 67 do not. Therefore neither pair is maker-only complete under these replay receipts. That is a counterfactual replay classification, not an exchange liquidity-role receipt.

## BIG ask path

BIG's minimum best ask anywhere in the lawful window was 55; it never went below 55. The 55 episode containing the action spans 14807 seconds from first to last observed 55 receipt and 14815 seconds until the first changed-ask receipt, across 464 raw book receipts. Displayed size at the best ask ranged from 1 to 2044 contracts. Participant identities are absent, so the tape cannot establish whether one seller or many supplied that size.

| episode | start scheduled/bell | ask | observed receipt span | state until next change | receipts | bid range | last values | ask-size range |
|---:|---|---:|---:|---:|---:|---|---|---|
| 1 | T-478:30 / T-568:30 | 55 | 14807s | 14815s | 464 | 53-55 | 56,55 | 1-2044 |
| 2 | T-231:35 / T-321:35 | 57 | 4015s | 4055s | 482 | 55-56 | 55 | 347-395 |
| 3 | T-164:00 / T-254:00 | 58 | 1353s | 1395s | 36 | 56-57 | 55 | 4-4 |
| 4 | T-140:45 / T-230:45 | 60 | 0s | 0s | 1 | 57-57 | 55 | 1-1 |
| 5 | T-140:45 / T-230:45 | 61 | 7s | 7s | 11 | 57-58 | 55 | 625-626 |
| 6 | T-140:38 / T-230:38 | 60 | 1616s | 1904s | 58 | 58-60 | 55,60,61 | 1-65 |
| 7 | T-108:54 / T-198:54 | 61 | 122s | 122s | 57 | 60-60 | 61 | 2-969 |
| 8 | T-106:52 / T-196:52 | 62 | 0s | 0s | 2 | 60-60 | 61 | 56-203 |
| 9 | T-106:52 / T-196:52 | 63 | 4944s | 4944s | 371 | 60-63 | 61,62,63,64 | 1-2035 |
| 10 | T-24:28 / T-114:28 | 64 | 0s | 1s | 2 | 61-61 | 63 | 364-386 |
| 11 | T-24:27 / T-114:27 | 63 | 359s | 359s | 354 | 61-62 | 64,63 | 27-2266 |
| 12 | T-18:28 / T-108:28 | 62 | 513s | 523s | 577 | 61-62 | 63,62 | 1-227 |
| 13 | T-9:45 / T-99:45 | 63 | 1231s | 1245s | 5844 | 62-63 | 63,62,64 | 2-5989 |
| 14 | T+11:00 / T-79:00 | 64 | 470s | 471s | 1112 | 62-63 | 64,63,65 | 1-7682 |
| 15 | T+18:51 / T-71:09 | 63 | 34s | 34s | 64 | 61-62 | 65 | 78-487 |
| 16 | T+19:25 / T-70:35 | 62 | 825s | 825s | 1795 | 60-61 | 65,62,61 | 24-15749 |
| 17 | T+33:10 / T-56:50 | 61 | 283s | 283s | 215 | 59-60 | 62,61,60 | 41-8351 |
| 18 | T+37:53 / T-52:07 | 60 | 2496s | 2496s | 1730 | 58-59 | 60,59,61,58 | 1-9151 |
| 19 | T+79:29 / T-10:31 | 59 | 17s | 19s | 10 | 58-58 | 58 | 1-1 |
| 20 | T+79:48 / T-10:12 | 60 | 87s | 87s | 95 | 58-59 | 58,60 | 58-6642 |
| 21 | T+81:15 / T-8:45 | 59 | 233s | 243s | 107 | 58-58 | 60,59 | 14-1201 |
| 22 | T+85:18 / T-4:42 | 60 | 34s | 60s | 14 | 58-58 | 59,60 | 252-268 |
| 23 | T+86:18 / T-3:42 | 61 | 3s | 3s | 12 | 58-58 | 60 | 3304-3304 |
| 24 | T+86:21 / T-3:39 | 60 | 0s | 0s | 5 | 58-58 | 60 | 4941-4941 |
| 25 | T+86:21 / T-3:39 | 61 | 33s | 39s | 15 | 58-58 | 60,61 | 2303-7244 |
| 26 | T+87:00 / T-3:00 | 60 | 120s | 120s | 108 | 58-58 | 61,60 | 3-3694 |

The complete ordered ask-episode ledger and every action-to-credit raw receipt are frozen beside this report.
