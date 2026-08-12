# Queue + formation + reflex census — every credited fill, dev-804 [ANALYTICAL_ESTIMATE]

Analysis seat only. Read-only. Machine records only. **Ledger caveat (reported, not forced): the staged V49b
carries 393 completes vs the official 405 (open §5 contradiction, owner Codex provenance) — "the 405" maps
here to the staged 393 completes' 786 legs + 357 credited partial legs = 1,143 credited fills.** Terminology
binding honored: prints are **contracts sold at P**; the book side is **contracts of standing bids at P**.
Machine artifact with every per-fill row: `QUEUE_FORMATION_REFLEX_CENSUS.json`.

Methods: ① book row at/just-before the sale's moment (≤600 s old, else NO_BOOK — never guessed), standing =
displayed size at our price among the top-5 bid levels (price absent from display → no real bids at P →
plausible by construction, noted per row); sold = contracts sold at-or-below entry within ±2 s of the fill.
② per-leg earliest candidate = spread-collapse shift, latest = trade-cadence-arrival shift, both by the
`9eff493b` neutral two-segment SSE split; the fill's T-minus against both. ③ posting moment =
`first_action_timestamp_epoch`; REFLEX_POST if posted ≤300 s after window open (the trailing-300s read organ
cannot yet have existed — the bid predates any belief); READ_LICENSED_POST otherwise.

## The three stamps (1,143 credited fills)

| stamp | counts |
|---|---|
| ① QUEUE | PLAUSIBLE **469** · **IMPROBABLE 643 (56.3%)** · NO_BOOK_AT_MOMENT 31 (named gap) |
| ② FORMATION | PRE_ONSET_UNDER_ALL **518** · BRACKET_DEPENDENT **478** · POST_ONSET_UNDER_ALL **144** · NO_SPLIT 3 (named gap) |
| ③ REFLEX | **REFLEX_POST 1,140 (99.7%)** · READ_LICENSED_POST 3 |

**Posting T-minus distribution (all 1,143): p25 886 · median 889 · p75 1,291 minutes before the scheduled
bell; 1,140 of 1,143 rests were posted within 300 s of window open.** The answer to the ordered question —
how much of everything we've ever been credited traces to bids placed before the machine had read a single
tick — is **all but three fills**. This is structural, and the census states it as such: V49b's law posts at
the first two-sided receipt, so the posting is a standing policy, never a licensed decision. The read organs
operate the rest *afterward*; they never authorize its birth.

Top stamp-triples: QI|PRE|REFLEX 304 · QI|BRACKET|REFLEX 255 · QP|BRACKET|REFLEX 207 · QP|PRE|REFLEX 199 ·
QI|POST|REFLEX 81 · QP|POST|REFLEX 60 (full triple × category grid in the JSON).

## The honest completes number

Of the staged 393 completes: **games with both legs QUEUE_PLAUSIBLE + POST_ONSET_UNDER_ALL +
READ_LICENSED_POST = 0.** Zero. The binding constraint is ③ (universal), but ① and ② would each gut the
number alone: relaxing ③ entirely still leaves only the queue-plausible × post-onset intersection, and
POST_ONSET_UNDER_ALL covers just 144 of 1,143 legs.

**Money attached to each excluded class (staged completes' pair delta = 1,666¢ total; overlaps stated):**

| excluded class | games | ¢ |
|---|--:|--:|
| ≥1 leg QUEUE_IMPROBABLE | 324 | **1,436** |
| ≥1 leg PRE_ONSET (formation-era) | 247 | 1,266 |
| ≥1 leg REFLEX_POST (reflex-born) | 393 | **1,666 — the entire book** |
| overlaps | q∩f 208 · q∩r 324 · f∩r 247 · q∩f∩r 208 | |

**BRACKET_DEPENDENT — what the operator's wake-up ruling moves: 478 legs; 228 complete games / 964¢** sit
between the earliest and latest onset candidates and will fall to one side or the other of whichever
qualifier is ruled.

## Reading it plainly

The credited book, viewed through these three lenses, is: bids born at window-open by policy (not by read),
majority-filled by sales smaller than the queues displayed at their price (a joining live order likely
watches those sales absorbed ahead), heavily during formation chaos before any onset candidate fires. The
144 post-onset + 469 queue-plausible minorities mark where replay credits most resemble something a live
order could have captured — the pilot's natural first territory, and the same zones the discriminator table
(35ac1f5b) already ranked first.

## Conservation

1,143 = 469+643+31 = 518+478+144+3 = 1,140+3; completes 786 legs / partials 357; honest 0; excluded-class
game sets over 393 staged completes with all pairwise/triple overlaps stated; 31 NO_BOOK and 3 NO_SPLIT are
named gaps (recorder quiet-or-outage undistinguishable — never smoothed). Sources: V49b staged ledger,
fit-local dev tapes (top-5 bid display) and prints, scheduled bells from machine t_minus fields.
ANALYTICAL_ESTIMATE.
