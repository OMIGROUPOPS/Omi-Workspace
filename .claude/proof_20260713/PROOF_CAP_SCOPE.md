# PROOF — C-CAP-SCOPE v1 (emergency rescope: the pursuit cap stops strangling premarket, keeps killing chases)

**Candidate SHA: 22039f30**
**Class cited: OVER-BROAD LOCK** (new, filed under the CAP-VOID lineage) — the chase-kill closing build redefined the operator's ruling: the DECREED constant was a CYCLE cap (buy→cash→re-buy, cycle ruling 07-08) and the build made it a PLACEMENT cap from the first buy; a protection over-rotated into a participation strangler within hours of arming.

## Part 1 — the scope, corrected (Lane 1 code)
`_pursuit_armed(tk)` gates counting AND both enforcement sites (chokepoint + organ): the cap counts from the leg's **first fill** or the event's **first bell**, whichever first — exactly where chasing becomes possible. Pre-fill pre-bell upward re-aims: unlimited in count, each bounded per placement by the armed honest-anchor walk cap (−0j, live since `9b26fc17`). Down/equal re-places pass always. Boot rebuild recomputes counts under armed semantics (placements since max(arming, latest own fill)); `_leg_filled` joins the lineage rebuild. The cap remains DECREED (cycle ruling 07-08), now scoped to its actual words — constraint #11 held.

## Part 2 — replay-harness law, three lanes (run at the SHA on the box, REPLAY PASS)
- **(i) CORBRU still freezes** — locks-off reproduces the tape (17/17 accepted); locks-on freezes at the 51: the self-fill bell (+10¢/30 min on own placements) fires at rung 2 and the fused gun refuses all 15 subsequent placements including the whole COR side. The chase-killer was always the bell; the rescope removes the strangler, not the kill.
- **(ii) tonight's refusal shapes re-run as PASSES** — WONBOW-shape pre-fill pre-bell upward re-aims: **zero chase_cap refusals** (the bell may still ring on ≥4¢/30-min risers — its designed behavior, metered by SELF-FILL-UNCONFIRMED). Post-arm discipline intact: with a fill on the leg, the 3rd upward re-aim refuses (`chase_cap`), proven in the same run.
- **(iii) the stranded bids re-aim on the first cycle after deploy** — verified live post-boot, prices cited in the deploy report (WONBOW held 6¢ vs mid 42.5; SARBOV 11¢ vs 51).

## Part 3 — the damage, counted (filed to the class entry)
Tonight, 4:23 pm 07-12 → 1:19 am 07-13 (the OVER-BROAD LOCK window; enforcement began at the 9:00 pm deploy): **931 refused re-aims across 20 legs / 15 events; 7 bids stranded stale at count time** (WONBOW +36¢ below mid, SARBOV +40¢, SARANG-ANG/-SAR +34¢ each, BONFAB-BON +23¢, HASZAG +21¢, DUHGAT +13¢); **539 sidelined leg-minutes**. Participation cost in the nightly's terms: 7 legs' bids sat unfillable-at-market through their events' premarket drift — the no-fill cohort's `queue_starved/aim_timing` taxonomy will carry them tonight; the refusal spam itself (215 refusals on one leg in 45 min) is the organ retry cadence hitting a wall it should never have met. Full table in the vault entry.

## Lane 2 — economics
The rescope RESTORES designed participation (PRIORITY-1 pairing: rest bids on both legs, always); enforcement narrows to the two tape-proven chase surfaces (post-fill, post-bell). Risk unchanged where it matters: CORBRU-class ladders still die at the bell; post-arm chases still cap at 2.

## The 6:10 honesty footer
`gun_scorecard` now prints, whenever the window contains cap refusals: refusal count + window bounds + "participation/fills in that span read LOW; grade the window accordingly" — tonight's regrade read carries it by construction (931 refusals in the scan window).
