# POST-FLIP AUDIT — Plex's five questions, answered from the live box (2026-07-06 00:0x ET)

**Flip deployed `6770a7c` (armed state `297a7086`), PID 3799064, boot 23:50:39 ET, full four-bar gate, one
restart, 0 errors.** Ruling: `PLEX_FLIP_RULING.md` (Ratification #20, verbatim).

## Q1 — the config diff is literally the one key ✓
`git diff bf1a25d4..HEAD -- config/deploy_v5_live.json` = `+ "per_match_clock": true` (the +2/−1 line count
is the JSON trailing comma added to the preceding `scale_gun_shadow` line; the SEMANTIC diff was
machine-verified pre-commit as exactly `{per_match_clock}`).

## Q2 — shadow still emitting AND the consumer branch actually took ✓
205 `pm_clock_shadow` rows post-flip (stream intact). Consumer proof: **13 events carry BUY placements at
legacy-tts 489–579 min — impossible under the legacy T-240 window — at honest-tts 129–234 min**, i.e.
`time_to_start` is being computed from `_pm_start − now` on honest-mode events. PASCOP among them.

## Q3 — honest start vs tape latch: no latches yet (slate starts ~02:00 ET) — monitor grades overnight ⏳
0 `match_live_detected` since flip at audit time. **Rollback is armed per condition 3:** any unanticipated
honest-mode delta >30 min at the tape latch → `per_match_clock` flips back through this same gate; the
nightly pass computes latch-vs-honest per event and any outlier gets a per-event writeup.

## Q4 — fallback events governed by the ratified widening, not a narrower legacy envelope ✓
100 known fallback-mode events (no honest join); **zero** `inside_buffer`/`match_already_started` skips
post-flip on any of them (zero on the whole box, in fact — nothing is being locked out on placeholder edges).

## Q5 — grep-proof on the RUNNING source ✓
AST scan: `_pm_honest`/`_pm_clock_resolve`/`_pm_window_closed`/`PM_CLOCK_WIDEN` appear in NO function outside
the sanctioned set (`_route_event`, `_pm_resolve_honest`, `__init__`, `_apply_schedule_data`, the two pure
helpers). `_is_match_live`, `_sustained_flow_live`, `_completion_target` verified clean — liveness/abandon,
exit, cancels, completion, meter, `latch_tape_override` all still read the legacy clock.

## (4) THE BEFORE/AFTER WINDOW TABLE — tonight's live slate (honest-joined, starting ≤12h; 121 events total)
| event | legacy start | honest start | legacy window opens | honest window opened | bid since flip |
|---|---|---|---|---|---|
| ITFW SIMCIR | 08:00 | 02:00 | 04:00 (2h AFTER true start) | **21:00→22:00 Jul 5** | **YES** |
| ITFW LUCGAD | 08:00 | 02:00 | 04:00 | **22:00 Jul 5** | **YES** |
| **ITFW PASCOP (Exhibit A)** | 08:00 | 02:00 | 04:00 | **22:00 Jul 5** | **YES** |
| ITFW SACLAZ / TODSAG / BRESAF | 09:00 | 03:00 | 05:00 | **23:00 Jul 5** | **YES ×3** |
| ITFW VAJRAM / ZRNLUE | 09:00 | 03:15 | 05:00 | **23:15 Jul 5** | **YES ×2** |
| ITFM VULCOU / GENAZO / SALNGW | 09:30 | 03:30 | 05:30 | **23:30 Jul 5** | **YES ×3** |
| ITFM BEASCO | 09:30 | 03:45 | 05:30 | **23:45 Jul 5** | **YES** |
| (13 more, honest windows opening 00:00–01:00 — KRACRI, KARBAS, OLIUCH…) | 07:00–11:00 | 04:00–05:00 | 03:00–07:00 | 00:00–01:00 | correctly not yet (T-240 not reached) |

**12 events have bids resting RIGHT NOW in windows that did not exist before this boot** — every one an ITF
event whose legacy window would have opened 2–6 hours after the true start. The no-bid rows are events whose
honest T-240 hasn't arrived yet — correct sequencing, not a miss. **The ITF premarket is being traded for
the first time.** Tomorrow's pass grades the first honest-clock slate in both C46 lanes.
