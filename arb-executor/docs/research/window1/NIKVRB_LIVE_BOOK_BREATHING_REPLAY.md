# NIKVRB live-book breathing replay

Current: VRB 69, NIK 21. Corrected: VRB 68, NIK 19.

## fv_anchor_placement truth

The deployed value is `false`. It gates only the downstream `_fv_anchor_price` placement override, whose source is the latest fresh true print. It does not call Pinnacle, Betfair, Matchbook, or the own BBO. With no print, `_v4_entry_anchor` returns before that hook is reachable; setting the flag true therefore leaves the T−317.817 no-print NO_CALL unchanged. The exact production lines are frozen in CODE_PATH_AUDIT.json.

The correction uses a separate quiet-book anchor contract. A complete fresh three-book sharp blend has first authority when it exists. NIKVRB contains no such historical external receipts, so the replay records that mechanism as NO_CALL and uses the lawful 67/68 own BBO midpoint: round((67+68)/2)=68. It initially rests maker-safe at 67, then recomputes min(ceiling 68, bid 69)=68 before the later 68 ask recurrence.

## Reprice-path autopsy

- **_resting_cancel_reason:** placement-time intended_join and intended_clamp exemptions clear bid_marketable_stale before cancellation.
- **cadence gate:** all ordinary walk decisions are suppressed for 60 seconds after a repost.
- **staircase hold:** staircase_hold returns unconditionally when its optional trail is disabled.
- **best-bid-aware repost:** deep-cast orders below touch return when the regime is unchanged; the old replay had no equivalent tick branch.
- **midpoint deadband:** 69.5 to 67.5 is only two cents.
- **cold replay resting hold:** ColdReplay.process:restingHold preserved the selected number and never recomputed it from BBO.

## Acceptance

- VRB: 68.
- NIK: 19.
- External sharp prices fabricated: 0.
- Population scoring/live execution: none.
- Full arithmetic table and four charts: `NIKVRB_LIVE_BOOK_BREATHING_TABLE_CHARTS.html`.
