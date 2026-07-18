# THE HANDS TABLE — every code path that can place, move, cancel, buy, or sell
> Founded 2026-07-17 (P0 completion-disarm dispatch, operator's standing word).
> PERMANENT; panel-linked (`/hands` on the fund tracker); gate-checked with the
> ledger. One plain-English sentence per hand + the consent on record +
> whether that consent is OPERATOR-TYPED or seat-drafted. **An acting hand
> without a plain-English typed yes is disarmed in the same commit that
> documents it.**

## THE CONSENT LAW (permanent, this dispatch)
Only words the operator actually typed may be recorded as his. Text drafted
by a seat and approved by him is **DRAFT-APPROVED** and must be shown with
BOTH texts. Jargon that conceals a plain action ("never-hold-naked verdicts
enforced" concealing "sell filled positions at the bid") is neither.

## THE JULY 12 RECLASSIFICATION (the class-closer)
The vault's 07-12 entry recorded three "operator arming words," including:
> *"Taker word: operator_taker_word = true. The completion policy goes live
> per its shadow-graded design: per-leg economics, taker-completion only
> when its own math clears, never-hold-naked verdicts enforced, pair-97
> arithmetic consulted nowhere. Its first live day is graded against its own
> shadow record in tonight's adjudication — any live-versus-shadow
> divergence is a named violation."*

**RECLASSIFIED: seat-drafted arming text, not operator verbatim.**
"Never-hold-naked verdicts enforced" was jargon concealing "sell filled
positions at the bid, cancel their maker exits, and cross siblings at the
ask." The operator's actual instruction — cancel UNFILLED bids at the bell —
is the gun sweep: a different law, correctly implemented elsewhere. Consent
was laundered through vocabulary. Both taker branches are disarmed on these
grounds (plus the record: −$0.264/leg vs ride on its own 07-13 study, N=36;
win-ride payouts excluded from its EV by design).

## THE TABLE
Legend: consent class = **TYPED** (operator's own words on the record) /
**DRAFT-APPROVED** (seat text he approved; lineage cited) / **JARGON**
(no plain-English yes). State = ARMED / DISARMED / SHADOW / OFF.

| # | Hand (code path) | What it does, plainly | Consent on record | Class | State |
|---|---|---|---|---|---|
| 1 | Router conception (`_route_event`→`v4_place`) | Rests a maker BUY on each leg at its fitted aim when an event enters the window | Cutover 07-14 "PATH-MODE IS THE LAW — entries at fitted path aims"; ENTRY-MECHANICS 07-17 "discovery IS the entry hour... both legs park at discovery" | TYPED (dispatch) | ARMED |
| 2 | Move/repost (`_v4_manage_resting_inner`→`v4_move_repost`) | Cancels and re-rests an entry bid when the best bid mismatches a touch posture or the regime re-orients | P2 07-17 "Reposts fire on evidence only: best-bid mismatch or a dial re-orientation — never on a timer" | TYPED (dispatch) | ARMED |
| 3 | ⑮ window-truth re-aim (`window_truth_reaim`) | Joins/improves the best bid when a rise is print-backed; holds on quote-only rises | ⑮ arm 07-17 (operator delegation) + P0v3 (3) print-backed seam | TYPED (dispatch) | ARMED |
| 4 | Sibling completion re-price (`completion_reprice`, maker) | After one leg fills, re-prices the sibling's resting MAKER bid toward pair completion under the combined ceiling | C-COMPLETION-CEILING arm 06-30 (operator arm) + C-PAIR-LAW 07-15/16 (Priority-1 verbatim) | TYPED | ARMED |
| 5 | Engagement join (`v4_engagement_join`, maker) | Rests a maker buy AT the standing bid in the engagement window | Engagement re-arm 06-12 (operator-directed after E3 tripwire review); graded nightly since | DRAFT-APPROVED | ARMED |
| 6 | Staircase walk (`staircase_hold_place`, maker) | Rests no-trade-anchor maker bids that walk a fitted knot schedule | Staircase Ship 3 go (operator, 06-18, Path A live) | TYPED | ARMED |
| 7 | T−20m fallback maker clamp (`fallback_maker`) | At T−20m re-rests the entry as a maker at ask−1 instead of crossing | RUN-7 config flip (seat-initiated; REPLACED a taker cross with a maker rest) | DRAFT-APPROVED (protective; disarming would restore a taker) | ARMED |
| 8 | Marketable clamp (`marketable_clamp`) | When a target would cross, rests at ask−1 instead of lifting | Site-clamp family (same protective class as 7) | DRAFT-APPROVED (protective) | ARMED |
| 9 | Maker exits (`v4_exit_posted`, sell) | Rests the validated band exit as a maker SELL on every filled leg | §0A operator frame: "The exit strategy is SOLVED and VALIDATED" (typed, standing order) | TYPED | ARMED |
| 10 | Gun sweep (`gun_fire_sweep` / `match_live_cancel`) | Cancels resting entry bids the moment live evidence fires at/after sched | P0v3 (2) 07-17 "SWEEP BEATS FILL... cancel resting entry bids FIRST" | TYPED (dispatch) | ARMED |
| 11 | Horizon sweep (`horizon_cancel`) | Cancels entry bids resting beyond T−8h honest | C-CONCEPTION-HORIZON 07-08 (operator ruling; map edge moves on his word only) | TYPED | ARMED |
| 12 | Floor retreat (`below_discovery_floor_retreat`) | Withdraws BOTH bids of an unfilled sub-floor ITF pair on volume refresh | P6 07-17 (operator live) | TYPED | ARMED |
| 13 | Pair seesaw scoreboard/refusal (`pair_seesaw_*`) | Logs pair arithmetic; refuses nothing at conception (exemption per the operator's Priority-1 verbatim) | PAIR-PRIORITY 07-16 (verbatim) | TYPED | ARMED (scoreboard) |
| 14 | Migration pass (`migration_reaim`/`migration_retreat`) | One-time re-judgment of pre-epoch bids: hold / re-park via the router / pair-level withdraw | ENTRY-MECHANICS ADDENDUM (b) 07-17 | TYPED (dispatch) | ARMED (one-shot) |
| 15 | **Flatten (`flatten_kept`)** | **Sold a FILLED position at the bid as a taker and cancelled its maker exit** | 07-12 "taker word" — RECLASSIFIED seat-drafted (above); own study −$0.264/leg N=36 | JARGON | **DISARMED this commit** (`completion_live_enabled=false`) |
| 16 | **Taker-complete (`taker_complete`)** | **Crossed the sibling at the ask as a deliberate taker after one leg filled** | Same 07-12 text — RECLASSIFIED | JARGON | **DISARMED this commit** (`operator_taker_word=false`) |
| 17 | **Complete-cross (`complete_cross`)** | **On a match-live cancel with a filled partner, crossed this leg's ask (IOC taker) to complete the pair** | C-COMPLETE-CROSS flag (seat-staged; no typed yes found on the record) | JARGON | **DISARMED this commit** (`complete_cross_enabled=false`) |
| 18 | Monotonic cut (§4 downside flatten) | Would taker-sell a falling leg mid-match | Gated OFF at build (b1aaef9); shadow-first arm doctrine | — | OFF (never armed) |
| 19 | Freeze-at-gun (4c) | Would hold entry bids static through the gun instead of sweeping | SHELVED 07-03; collision-benched vs sweep law (law_collision founding wire) | — | OFF |
| 20 | ITM exit-take / no-rebuy (07-07 containment) | Takes an in-the-money exit at settlement-adjacent prices; blocks rebuys after cash | Operator-directed containment sweep 07-07 | TYPED | ARMED |
| 21 | Deploy drain (`shutdown_cancel` + drain replay) | Cancels resting bids at graceful shutdown; replays them through the chokepoint at boot | C-DRAIN-REPLAY 07-10 (gated deploy, operator-reviewed) | DRAFT-APPROVED | ARMED |
| 22 | Expiration probe (one-shot, this dispatch) | One 1-share far-from-touch bid with exchange-side expiration, then cancelled | This dispatch's (6), operator-authorized | TYPED (dispatch) | ONE-SHOT tonight |

**Disarm summary this commit: hands 15, 16, 17 — the only acting hands whose
consent was jargon. Hands 5, 7, 8, 21 are DRAFT-APPROVED with lineage shown
(5 and 21 operator-directed in substance; 7 and 8 protective clamps whose
removal would RESTORE taker behavior) — flagged for the operator's typed
ratification at his convenience, not disarmed: they place nothing the entry
law doesn't already govern and un-arming them worsens the taker surface.**
