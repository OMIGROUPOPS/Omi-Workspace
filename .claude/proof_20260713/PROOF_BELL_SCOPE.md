# PROOF — C-BELL-SCOPE v1 (the self-fill bell scoped to unsanctioned behavior; the false freezes lift at boot)

**Candidate SHA: 0a6ab782**
**Class cited: OVER-BROAD LOCK, instance 2** — one night apart from instance 1, same lesson: the bell's 4¢/30-min threshold was calibrated against the pre-arming 4¢-walk world; the −0j arming (ITF allowances 14–20¢) invalidated it the same day. The class lesson extends, and the code now embodies it: **a lock's threshold must scope against currently-sanctioned behavior DYNAMICALLY** — `_sanctioned_walk_cents_cat` reads the LIVE walk-cap table (honest-anchor when armed, legacy otherwise, config overrides included), so future re-ratifications can never strand the threshold again.

## Part 1 — the corrected scope (Lane 1 code)
The bell still requires the ≥4¢/30-min own-activity rise, and now fires ONLY when one of three conditions makes the rise evidence rather than sanctioned behavior:
(a) **leg_fill** — the leg has ≥1 fill (post-fill pursuit, the CORBRU shape);
(b) **exceeds_sanctioned_walk** — the window rise exceeds the armed walk allowance for the category (walking faster than the system itself sanctions);
(c) **tape_corroborated** — non-self prints in the same window (≥ `self_fill_corroborate_prints`=5, DECREED this dispatch) — the market moved with us.
Every fire logs its condition; the gun stamp carries it.

## Part 2 — the unfreeze audit (runs at this deploy's boot)
The gun rebuild now captures each fire's rise and confirm history; a rebuilt entry whose ONLY evidence is a self-fill fire with **no fills on either leg, no confirms from any other source, and a recorded rise within the sanctioned allowance** is popped from the gun state with `self_fill_unfrozen` logged (true state: premarket_quiet, allowance cited). Genuinely-live events re-fire via the other six sources within minutes. Verified live in the deploy report.

## Part 3 — replay-harness law, three lanes (run at the SHA on the box, REPLAY PASS)
- **(i) CORBRU still freezes** — fires at the 51 via **tape_corroborated** (its market printed 43 times in hour 00, feeding the harness's in-window tape); all 15 subsequent placements refused. (The dispatch's condition-(a) framing is honored in effect: the tape carried the freeze; CORBRU's fills came later and would arm (a) as well.)
- **(ii) RAIZHU still fires** — condition (c) is the mechanism, proven by the same corroborated-fire lane (RAIZHU's market was live and printing).
- **(iii) tonight's shapes re-run as NO-FIRE** — sanctioned pre-fill re-aims (8¢ window rise ≤ 20¢ ITF_W allowance) on quiet tape: every placement ACCEPTED, no cap, no bell. Plus both fire conditions proven live in the same run: 23¢ > 20¢ fires `exceeds_sanctioned_walk`; post-fill +6¢ fires `leg_fill`.

## Part 4 — the damage (filed to the class entry)
1:30 – 3:09 am, 24 events frozen on sanctioned behavior (the dispatch's eleven kept growing until this fix): **1,780 cumulative frozen-minutes (accruing until this deploy), 42 entries refused under the false freezes.** The 6:10 scorecard brands this as the night's SECOND suppressed window beside the cap window, and **two suppressed windows force DELETION GATE: REFUSED for insufficient clean tape, whatever the four proofs say — a clean night means clean.**

## Lane 2 — economics
Strictly participation-restoring: false freezes lift; the bell's real kills (post-fill chases, faster-than-sanctioned risers, tape-confirmed moves) all preserved by replay. §0A untouched.
