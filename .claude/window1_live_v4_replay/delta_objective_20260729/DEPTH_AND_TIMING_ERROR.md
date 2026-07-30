# Five-game authority depth and Atlas timing

**The five games do not support “timing accurate, depth inaccurate.” Both were inaccurate in this sample.** Atlas's median absolute bottom-time error was **405.3 minutes**. Sealed was more negative to the close, but also materially deeper than the reachable low.

Signs: aim − low below zero means too deep to touch; aim − close below zero means desired Window-1 value. Timing is predicted bottom minute − actual low minute.

| category | event | leg | low | close | legacy | L−low | L−close | sealed | S−low | S−close | predicted minute | actual minute | timing error |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ATP_CHALL | KXATPCHALLENGERMATCH-26JUL19HURBIG | BIG | 55 | 60 | 52 | −3¢ | −8¢ | 45 | −10¢ | −15¢ | 318.0 | 73.8 | +244.2m |
| ATP_CHALL | KXATPCHALLENGERMATCH-26JUL19HURBIG | HUR | 37 | 42 | 44 | +7¢ | +2¢ | 38 | +1¢ | −4¢ | 139.0 | 400.7 | −261.7m |
| ATP_CHALL | KXATPCHALLENGERMATCH-26JUL19NIKVRB | NIK | 18 | 19 | 24 | +6¢ | +5¢ | 23 | +5¢ | +4¢ | 139.0 | 428.8 | −289.8m |
| ATP_CHALL | KXATPCHALLENGERMATCH-26JUL19NIKVRB | VRB | 70 | 83 | 67 | −3¢ | −16¢ | 60 | −10¢ | −23¢ | 318.0 | 163.9 | +154.1m |
| ATP_MAIN | KXATPMATCH-26JUL12LAJVAN | LAJ | 43 | 45 | 41 | −2¢ | −4¢ | 43 | 0¢ | −2¢ | 639.0 | 1117.9 | −478.9m |
| ATP_MAIN | KXATPMATCH-26JUL12LAJVAN | VAN | 49 | 57 | 46 | −3¢ | −11¢ | 46 | −3¢ | −11¢ | 567.0 | 25.4 | +541.6m |
| WTA_CHALL | KXWTACHALLENGERMATCH-26JUL16BRAVED | BRA | 38 | 44 | 36 | −2¢ | −8¢ | 31 | −7¢ | −13¢ | 78.0 | 484.7 | −406.7m |
| WTA_CHALL | KXWTACHALLENGERMATCH-26JUL16BRAVED | VED | 55 | 57 | 58 | +3¢ | +1¢ | 50 | −5¢ | −7¢ | 114.0 | 517.9 | −403.9m |
| WTA_MAIN | KXWTAMATCH-26JUL20KORJIM | JIM | 30 | 32 | 34 | +4¢ | +2¢ | 29 | −1¢ | −3¢ | 547.0 | 1562.3 | −1015.3m |
| WTA_MAIN | KXWTAMATCH-26JUL20KORJIM | KOR | 60 | 70 | 58 | −2¢ | −12¢ | 50 | −10¢ | −20¢ | 685.0 | 8.0 | +677.0m |

## Aggregate

- Legacy was touch-reachable on **4/10** legs; sealed on **3/10**.
- Legacy selected negative close delta on **6/10** legs; sealed on **9/10**.
- Median absolute depth error: legacy **3.0¢**, sealed **5.0¢**.
- Mean aim-minus-close: legacy **−4.9¢**, sealed **−9.4¢**.
- The tape low had already happened before the comparable two-authority decision on **3/10** legs.
- Completed pairs: **0/5**. The tape offered negative combined delta with both legs below close in all five.

## Per category

| category | legs | legacy mean vs low | sealed mean vs low | legacy mean vs close | sealed mean vs close | median absolute timing error |
|---|---:|---:|---:|---:|---:|---:|
| ATP_CHALL | 4 | +1.8¢ | −3.5¢ | −4.2¢ | −9.5¢ | 253.0m |
| ATP_MAIN | 2 | −2.5¢ | −1.5¢ | −7.5¢ | −6.5¢ | 510.2m |
| WTA_CHALL | 2 | +0.5¢ | −6¢ | −3.5¢ | −10¢ | 405.3m |
| WTA_MAIN | 2 | +1¢ | −5.5¢ | −5¢ | −11.5¢ | 846.1m |

The causal read is stark: sealed generally improved the value sign relative to the close, but usually bought that improvement by moving below the tape's reachable depth. The Atlas clock did not rescue it; its errors here are measured in hours, not quarter-minutes.
