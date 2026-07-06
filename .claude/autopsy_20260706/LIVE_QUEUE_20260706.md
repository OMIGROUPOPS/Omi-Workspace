# DAY QUEUE — LIVE EVIDENCE CLOSE-OUT (2026-07-06, afternoon session 12:15 ET boot)

Standing frame honored: every number below is from the CURRENT session's log + exchange
(or the overnight session where the item's sample spans both), timestamped. Machinery:
`riser_live.py`, `live_evidence.py`, `/tmp/live_evidence.json` (this dir).

## (1) RISER — LIVE VERDICT → **DISARMED THROUGH THE GATE**
Armed at read time: `riser_post_revision=true` (config, 15:15:41 ET). Live session bars
(12:15→15:16): riser posts 2, fills 1, the one fill −8¢ discount (BERMEL-BER, posted 76 →
filled 84, ERODED) — n=1, consistent with the overnight breach ((a) median −1¢, n=130),
incapable of rescuing it today. **The pre-registered letter executed:** "the fix MISSED
and comes out (disarm, one config flip through the gate)." Config commit `b0d1bcff`,
C46 doc `.claude/proof_20260706/RISER_DISARM.md`, deployed via `deploy_live_v4.sh`
(gate: lint+smoke+proof). Live verification line: appended to RISER_DISARM.md post-boot.

## (2) THIN-GUN — the combined-sample verdict is HONEST-MIXED; package OUT, arming NOT requested
Live+overnight `gun_scale_shadow` joined to true tape onset (172 fires with onset):
**52 on-time · 47 late · 7 early · 52 FALSE_PREGAME (>10min pre-onset) · 14 no-onset — and
123 of the fires landed where the legacy gun was SILENT.** The n=4 pre-registration bar
("zero false pregame fires") does NOT survive scale on this join — with the stated caveat
that on thin books the reference onset is itself the fallback estimator (P3a: ITF onset
undetectable 50–60%), so part of the FALSE_PREGAME mass is reference noise, not detector
noise. **Live blindness today: 18 matches started silently (onset seen, no latch) since
12:15 alone.** Verdict: the blind-class value is real and measured; the graduation bar is
not met as pre-registered → the package goes to Plex with these numbers for a bar retune
(e.g. false-fire tolerance vs blind-coverage tradeoff), NOT an arm request. Raw:
`/tmp/live_evidence.json` → `live_evidence_20260706.json` (committed).

## (3) WALK-CAP HONEST ANCHOR — census harvested LIVE, fix specced, build STAGED gated-OFF
Conception(first-post)→fill drift, both sessions (the distributions the cap re-anchors to):
| cat | n | med | p75 | p90 | max |
|---|---|---|---|---|---|
| ITF_W | 123 | +8 | +20 | +36 | +76 |
| ITF_M | 81 | +6 | +14 | +27 | +60 |
| ATP_CHALL | 89 | 0 | 0 | +1 | +8 |
| WTA_CHALL | 35 | 0 | 0 | +1 | +4 |
| mains | 10 | 0 | 0 | +1 | +1 |
Read: the ITF honest window is NOT the card premarket — legs legitimately re-anchor tens
of cents; the aim-table 4¢ cap would have clipped the p75+ half of ITF fills (the
participation-loss the triple-check feared, now measured). **Spec: conception = FIRST
placed target in the honest window (set-once `pos.honest_anchor`); cap = census-derived
per-cat cents (defaults p75: ITF_W 20 / ITF_M 14 / CHALL 2 / MAIN 1, config-overridable
`walk_cap_honest_by_cat`), subtractive, fallback branch only (fires solely when the
legacy conception doesn't exist yet).** Staged in live_v4.py gated `walk_cap_honest_anchor`
default-OFF (byte-identical; lint PASS, zero new test failures). Cap sizes to Plex with
this census before any arm (standing bar: ships with or before the aim-layer arm).

## (4) MONITOR GRADING FIXES — both fixed; proof on the next cycle
- **ZT2 (A54 mark-to-market adoptions):** grades adopted legs at TRUE basis via the bot's
  `adoption_true_basis` event (C-TRUE-BASIS, live since 12:15); an adopted leg with no
  true-basis event (pre-fix booking) renders the pair `combined_over_goal_UNVERIFIED_BASIS`
  — a pattern, never a ZT row.
- **ZT3 (future-conception grading):** a buy that PREDATES the `window_open_set` stamp is
  ungradeable against it → `pre_conception_buy` pattern, never a ZT row (the honest-window
  false-positive class: 10/19 overnight).
Expected re-grade of the overnight board under the fix: 36 violations → ~19 true
(7 fabricated ZT2 + 10 retroactive ZT3 reclassified to patterns). Live verification:
before/after counts from the first monitor cycle after restart, appended below.

## (5) THIN-BOOK DEPTH (I-4) — live exhibits + spec direction
**29 priced-out legs in the current session alone** (bid below where the tape then traded;
list in `live_evidence_20260706.json`). Spec direction for the refinement (NO build yet, and
per OPERATOR_RULING_2C_BRANCH no sibling-conditional shapes): depth chosen book-relative —
offset as a function of (spread, resting size at level, prints/hour) instead of flat per-cat
cents; the aim-layer (AIM_V2_SPEC) is the natural carrier since dip quantiles already
encode book physics per bucket. Parked as spec-input to the V2 estimator, not a separate
patch (a separate depth ruleset would be exactly the banned patchwork class).

## (6) SERIALIZATION'S COST — the nightly figure, stated
Overnight (pre-guard): **12 same-pass duplicate sibling-reposts; 4 double-filled to ~10
shares (POTFEL/TEUHAS/HERNAG/PACLOV ≈ $9.80 unintended extra basis); 1 orphan filled
in-play 23min past latch (KEYNOS, $2.70 exposure)** → ≈ **$10–13/night unintended basis +
one in-play naked entry**, per night, before 12:15. Current session (guards live): 30
sibling reposts placed, **0 dup-guard skips needed, 0 ownership aborts** — no same-pass
collisions this slate; the guards are armed and silent. Residual unguarded: the
reaim×walk place-await micro-window (log-visible `move_repost_ownership_abort`), plus the
full serialization design parked behind the §4H cancel-rework lock. Priority figure for
the operator: ~$10–13/night was the pre-guard cost; the placement-side guards took the
measured mechanisms to zero occurrences today.

## (7) GIT VERIFY
`PLEX_REGRESSION_RULING.md` committed verbatim-as-relayed at `cefd987f` (54 lines,
provenance header + relay text + extracted constraints); rulings dir current:
AIM_V2_SPEC · OPERATOR_RULING_2C_BRANCH · PLEX_REGRESSION_RULING alongside the standing
seven. Ledger state (ONE_AIM_FIX §LEDGER): aim fix BLOCKED-ON-DATA (coverage trigger),
≤2¢ branch INTERIM-ARCHAIC (ruled), riser DISARMED (this doc §1).

---
## LIVE VERIFICATION LINES (post-action, appended as they land)

- **15:25:58 ET — RISER DISARM LIVE:** `=== DEPLOYED 3db9af8 (PID 57639) ===`, GATE PASS (lint · smoke PASS · proof cites b0d1bcff, no code delta to HEAD). Running config echo: `riser_post_revision = False`. Bot trading; first post-disarm riser placements accrue at the bid (pre-revision baseline).
- **15:26:34 ET — MONITOR LIVE ON PATCHED GRADING:** cycle 1 fresh session scope, 485 events, 0 violations, git=pushed. Overnight-list re-grade under the fix (from the committed ordering proofs): **36 → 10 true ZT rows** — all 19 walk_cap rows predate their conception stamps (→ `pre_conception_buy` patterns), 7 combined rows are unverified mark-to-market adoptions (→ `UNVERIFIED_BASIS` patterns); surviving: 9 combined_over_goal (6 same-tick races, TSIAND, SILDIG, GARCIO) + 1 grace (KEYNOS). False-positive count before/after: **17 → 0 of the identified classes.**
- **15:26 ET — accumulator/cron state:** nightly 04:45 ET installed; day-0 coverage 0/500 target cells (honest-era corpus building, 1,464 honest samples registered from night 1).
