# PLEX RISER BOUNCE — the full package (staged 2026-07-05, NOT yet relayed)

**Status: ready to relay on the operator's word.** The riser_post revision touches entry
doctrine and is Plex-gated by standing order; live config holds riser_post UNCHANGED
until the ruling. Everything below is on the public repo (raw URLs at the bottom) so
Plex reads ground truth, not prose.

---

## 1. The question for Plex

Approve, modify, or refuse the per-cat `riser_post` demand-depth revision (aim-table
change, currently 0¢ everywhere = join at window-open level):

| cat | today | proposed | replay basis |
|---|---|---|---|
| ATP_CHALL | 0 | **3** | 90% certain-fill retention at 3–4¢ |
| WTA_CHALL | 0 | **3** | structural sibling of ATP_CHALL (no direct replay N that night) |
| ITF_M | 0 | **3** | 75% retention at 3¢ |
| ITF_W | 0 | **2** | 79% retention at 2–3¢, steeper decay than ITF_M |
| ATP_MAIN | 0 | **0–1 (hold)** | 1¢ costs 50pts of fill-rate — depth = non-participation in liquid books |
| WTA_MAIN | 0 | **1–2** | 88% retention at 2¢, decays after |

**Honest framing (from the proposal, unchanged):** this is a price-improvement trade
(+2–3¢/leg on ~60–90% of Challenger/ITF riser fills), **NOT an adverse-selection fix**.
Below-FV share of fills is FLAT across depth (44→44→47→43→38%): the dumpers blow through
4¢ of depth all the same; the seesaw's negative selection is structural. What depth buys
is CENTS, not selection.

## 2. The replay retention curves (the evidence)

Method: every leg with window-open ≥50¢ across two logs (**N=69 riser legs with tape**),
replayed at demand-depths {0,1,2,3,4}¢ below window-open against the recorded trade
tape, premarket window = open→latch. *Certain* = print strictly below the level
(queue-independent); *at-touch* = print ≤ level.

| depth | ALL (certain) | ATP_CHALL | ATP_MAIN | ITF_M | ITF_W | WTA_MAIN | below-FV of fills |
|---|---|---|---|---|---|---|---|
| 0 (today) | 91% | 100% | 88% | 83% | 95% | 100% | 44% |
| 1 | 84% | 100% | **38%** | 83% | 95% | 88% | 44% |
| 2 | 77% | 90% | **25%** | 83% | 79% | 88% | 47% |
| 3 | 70% | 90% | 12% | 75% | 79% | 62% | 43% |
| 4 | 62% | 90% | 12% | 62% | 68% | 62% | 38% |

Per-leg detail (69 rows, every depth × fill verdict × FV): `riser_depth_legs.json`.
Replay code: `riser_depth_replay.py`.

## 3. The two fv_observe evidence streams — both n's explicit

The proposal's named caveat was "FV-subset thin (18 legs) — demand a week of fv_observe
accumulation." That accumulation is now in, in two distinct streams that must not be
conflated:

**(a) MARKET-SHAPE sample — N = 491** (recomputed 2026-07-05 evening; was 452 at the
morning report; gate target ~100, exceeded ~4.9×).
Definition: `fv_burst_anchor` observe-only rows where the riser-shaped candidate
(entry_price ≥50¢) has a recorded burst-FV mid. Measures where the tape's FV sits
relative to riser levels at the volume burst, across ALL tracked riser-shaped legs —
it does NOT depend on us filling. Daily accumulation: 141 (06-29), 139 (06-30),
69 (07-01), 25 (07-02), 17 (07-03), 49 (07-04), 51 (07-05, partial day).

**(b) OWN-FILL sample — N = 43 (night-1 ledger) / N = 76 (current full box).**
Definition: OUR filled riser legs carrying an own-fill `entry_minus_fv_burst` (emfb =
what we paid minus burst-FV; positive = paid above FV).
- Night-1 ledger split (the number the standing order tracks): riser mean emfb
  **+5.9¢, 37% under-FV, N=43** (vs faller −2.6¢, 53% under-FV, N=43).
- Current full box (night-1 + day, regrade population): **N=76** emfb-graded riser
  legs, mean emfb **+2.8¢**, 37/76 (49%) paid above FV.
The own-fill stream is the selection-cost measurement; the market-shape stream is the
denominator that says whether deeper posts would still have been reachable at
better-than-FV prints.

## 4. What would refute the proposal (pre-registered for the ruling)

- Retention on the accumulated sample materially below the replay table (the 69-leg
  replay was 07-03/07-04 tape; Plex can demand the same replay over the full week).
- Below-FV share RISING with depth on the bigger sample (would mean depth selects for
  fades — worse than flat).
- ATP_MAIN/WTA_MAIN: any proposal to add depth there contradicts the replay (main-tour
  books do not dip; depth = non-participation) — the proposal itself says hold/1¢.

## 5. Context Plex should have (one paragraph)

The bound side is now law, deployed tonight (C-BOUND-RULING, 21eaad4): every
resting/reprice/completion path bounds combined at ≤97; the emergency cross caps at
≤100 with a 5-95¢ leg range. So the riser ruling is purely about leg-1 entry price
improvement — pair-completion arithmetic no longer leaks above goal regardless of what
the riser does. The week's leak decomposition says the riser concession is a rounding
error next to ITF timing and structural no-dip — the operator knows; this revision is
the cheap-cents lever, not the central one.

## 6. Raw URLs (paste-ready for Plex)

- Proposal: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/blend/kalshi-occ-fallback/.claude/live_20260705/audit/RISER_REVISION_PROPOSAL.md
- Replay code: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/blend/kalshi-occ-fallback/.claude/live_20260705/audit/riser_depth_replay.py
- Per-leg replay detail (N=69): https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/blend/kalshi-occ-fallback/.claude/live_20260705/audit/riser_depth_legs.json
- Night-1 ledger + FV split (N=43/43): https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/blend/kalshi-occ-fallback/.claude/nightly_20260705/REPORT.md
- Full-box regrade (N=76 own-fill emfb source): https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/blend/kalshi-occ-fallback/.claude/nightly_20260705/FULL_TAPE_REGRADE.md
- This package: https://raw.githubusercontent.com/OMIGROUPOPS/Omi-Workspace/blend/kalshi-occ-fallback/.claude/nightly_20260705/PLEX_RISER_BOUNCE_PACKAGE.md
