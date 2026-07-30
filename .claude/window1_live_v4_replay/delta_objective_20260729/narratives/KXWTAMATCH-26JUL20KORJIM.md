# KXWTAMATCH-26JUL20KORJIM — WTA_MAIN

Start evidence: **observed official exact**. Field contract repair: **on**. Wait for recognition: **on**.

The tape offered **−12¢ combined delta**, with both leg lows below their own closes. Only 0 of 2 legs filled; there is no completed-pair delta and no PC.

| leg | full-window low | W1 close | legacy aim (delta to close) | sealed aim (delta to close) | fills |
|---|---|---:|---:|---:|---|
| JIM | 30¢ at Tue Jul 21, 1:02:15 AM ET | 32¢ | 34¢ (+2¢) | 29¢ (−3¢) | none |
| KOR | 60¢ at Sun Jul 19, 11:07:59 PM ET | 70¢ | 58¢ (−12¢) | 50¢ (−20¢) | none |

## Chronological replay

- **Sun Jul 19, 11:00:00 PM ET:** The lawful evaluator window opened.
- **Sun Jul 19, 11:07:59 PM ET:** KOR: the tape reached its Window-1 low 60¢ (minute 8.0).
- **Sun Jul 19, 11:08:02 PM ET:** KOR: the OS withheld the path order because the leg band and pair recognition were not ready.
- **Sun Jul 19, 11:08:08 PM ET:** KOR: drift/band called WTA_MAIN-B3 flat (net 0, dip 0); recognition=false.
- **Mon Jul 20, 3:00:32 AM ET:** JIM: the OS withheld the path order because the leg band and pair recognition were not ready.
- **Mon Jul 20, 6:06:20 AM ET:** JIM: cohort WTA_MAIN|dog|26_50 proposed 35¢ from 37¢.
- **Mon Jul 20, 6:07:00 AM ET:** JIM: drift/band called WTA_MAIN-B3 flat (net 0, dip 0); recognition=true.
- **Mon Jul 20, 6:07:00 AM ET:** JIM: legacy/path aimed 34¢ from WTA_MAIN|underdog|26_50.
- **Mon Jul 20, 6:07:00 AM ET:** JIM: posted buy 5 at 29¢ under SEAL; status resting.
- **Mon Jul 20, 6:07:00 AM ET:** JIM: sealed authority overrode 34¢ to 29¢.
- **Mon Jul 20, 6:07:00 AM ET:** KOR: legacy/path aimed 58¢ from WTA_MAIN|leader|51_75.
- **Mon Jul 20, 6:07:00 AM ET:** KOR: posted buy 5 at 50¢ under SEAL; status resting.
- **Mon Jul 20, 6:07:00 AM ET:** KOR: sealed authority overrode 58¢ to 50¢.
- **Mon Jul 20, 6:07:00 AM ET:** The two bands produced pair class flat_flat.
- **Mon Jul 20, 7:00:31 AM ET:** JIM: canceled the resting bid because bid_marketable_stale (book 34/35).
- **Mon Jul 20, 7:06:59 AM ET:** The two bands produced pair class neither.
- **Mon Jul 20, 1:18:04 PM ET:** The two bands produced pair class mirror.
- **Tue Jul 21, 1:02:15 AM ET:** JIM: the tape reached its Window-1 low 30¢ (minute 1562.3).
- **Tue Jul 21, 9:01:19 AM ET:** JIM: the authoritative Window-1 close was 32¢.
- **Tue Jul 21, 9:18:21 AM ET:** KOR: the authoritative Window-1 close was 70¢.
- **Tue Jul 21, 9:19:00 AM ET:** The guarded evaluator window closed.

## Read

A nonnegative aim-minus-low means the tape reached or passed the bid; a negative number means the authority aimed below the actual low. A negative aim-minus-close is the desired value direction, but it counts as PC only if both legs actually fill.
