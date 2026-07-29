# ALVVAN — live_v4 thinking aloud with the nine installed VPS inputs

This is an honest diagnostic trace, not a valid score and not yet a literally complete dossier. The eight installed model/state files and the historical `observed_starts.db` all loaded. The transaction-consistent VPS `tennis.db` snapshot is still absent, so the sharp-FV surface returned `NO-READ` at every consultation. Although `_fv_observe_fields` describes itself as observe-only, the orientation prior consumes its result as a weight-two vote, so the missing surface is potentially behavioral and cannot be waved away as logging. It cast no vote here. The trace is invalid for scoring because a required input was missing.

The fill rule for this replay was: **we rest orders; a later true print or opposite BBO touching or passing the limit fills the whole order. No depth proof and no five-contract gate.**

The one-sentence result is: **cohort and atlas both found VAN 22; atlas put ALV at 74 even though its own contention selector said DROP; drift/band later recognized a flat-flat B4/B6 pair, but the orders remained signed by `LEGACY:path_aim` because the calls arrived after placement and a field-name defect in `live_v4` made its authority sweep treat its own order as foreign. VAN filled at 22. ALV never reached 74. The pair did not complete.**

## The story, in replay-clock order

### 11:00 PM ET, eight hours before the scheduled bell

The replay opened at 11:00 PM on July 11. Kalshi's schedule identified the match bell as 7:00 AM ET. The historical observed-start database was present and was read under the replay clock, but it had no ALVVAN start row visible by this time. Therefore the schedule, not an observed start, was the clock authority.

The books initially had no usable traded anchor. The OS discovered both tickers but did not conceive an entry until a true print supplied a Window-1 anchor.

### 12:46:45 AM, 373.2 minutes before the bell — VAN wakes first

The first true VAN print was 26. Its book was 22 bid for 97 and 26 ask for 587, a four-cent spread. The OS froze 26 as VAN's Window-1 open.

Seventeen seconds later, at 12:47:02, every entry layer was consulted:

- **Orientation:** ALV was called the presumed riser with conviction 1.00 from two voices. The cohort voice examined `ATP_CHALL|dog|le25`, with 866 examples and a 23.6% dog-rise rate, and voted for ALV. The anchor-role voice also voted for ALV because ALV was the incumbent leader. `ORIENT_V1` was present, but its first-hour chain-tape call was not yet available this early, so it cast no vote. Sharp FV would have been a fourth voice, but `tennis.db` was unavailable and it cast no vote.
- **Cohort:** VAN matched `ATP_CHALL|dog|26_50`, with 2,053 examples. The fitted median dip was four cents, the three-cent reach rate was 0.61, the four-cent reach rate was 0.534, and the historical rise rate was 34.0%. Because VAN was the presumed faller, cohort steering was live. It changed the preliminary target from 23 to **22**.
- **Staircase/entry table:** the fitted per-cell entry row also landed at **22**, with a four-cent offset, expected fill rate 0.585, and expected net ROI 17.53%. The book was not locked, runway was classified `full`, and the order would be a post-only resting maker.
- **Atlas:** `ATLAS_V1` matched `ATP_CHALL|underdog|26_50`, with 1,470 examples. Its fitted bottom depths were 2/4/7 cents at p25/p50/p75. The p50 path aim was therefore **22**. Its median fitted bottom time was 139 minutes after the atlas clock's onset.
- **Contention selector:** it found a best fitted completion probability of 63.8% at the p75 tier and said `TRADE-AT-PATH`; its deeper contention aim was 19.
- **Live-aim library:** the library file was present, but the separate live-confidence calculation was 0.00 because this worktree had no qualifying archived ATP_CHALL trade files at the path that calculation scans. The result was `NO-OPINION`. It did not steer.
- **W1 cohort library:** the shadow page `ATP_CHALL|26_50|lo` had 587 examples, dip frequency 0.656, depth quantiles 4/6/10, and median time 78 minutes on its known mis-anchored `-0k` clock. It wrote to the dossier only.
- **Reach law:** at four cents of depth, the fitted one-hour fill probability was 0.020 on the quiet/rest-seeded gauge. It wrote evidence but did not veto.
- **Range cell, cash window, vitality fits:** range-to-entry mapping was unfitted; cash-window gun-axis lawful share was unfitted; volume-path and wall-versus-theater fits were also absent. Each was named `GAP`, and none controlled the order.
- **Pair arithmetic:** the live path numbers were 22 plus a 74 sibling estimate, or 96. The saved dossier nevertheless recorded `combined_at_path: 93` beside `sib_px_est: 74`. That 93 equals the separate contention aim 19 plus 74, but the dossier does not label the switch of aim. The fields are arithmetically inconsistent if read as one surface. The 97-cent cap still admitted the 22-cent order.
- **Sizing:** the shadow would have used 15 contracts because contention exceeded 50%, but sizing was not armed. The live order remained five.

The final signer was **`LEGACY:path_aim`**, and the OS posted five VAN contracts at **22**. Here, cohort and atlas agreed, so cohort changed the preliminary path but made no marginal difference to the final number.

### 12:47:46 AM, 372.2 minutes before the bell — drift and band finally speak

Forty-four seconds after the VAN order was already resting, the recognition cascade saw open 26, last 26, net drift 0, and dip 0.

Drift's six-hour recognition cell was `ATP_CHALL|h6 / a50|flat|d0`. It cleared the 0.50 purity rule and called **`ATP_CHALL-B4`**. The B4 fitted band had 1,511 examples, median anchor 50, median net move 0, median dip 2, and p75 width 6. In plain English: **VAN looked like a flat, middle-priced market, not a falling knife.**

This was a real recognition call, but it did not sign or move the existing order. It arrived after placement. More importantly, the unchanged live OS immediately mishandled ownership of its own resting order: reconcile normalized the exchange row as `order_id` and `price`, but the authority sweep read `oid` and `px`. It therefore saw an empty ID and null price, labeled the order “unattributable/manual,” and invoked its own rule: **flag, never touch**.

That field mismatch is in `live_v4`, not in the replay shell. It is why the later authority could not heal the legacy order.

### 1:05:15 AM, 354.7 minutes before the bell — ALV wakes

The first true ALV print was 79. Its book was 74 bid for 21 and 79 ask for 1,328, a five-cent spread. The OS froze 79 as ALV's Window-1 open.

At 1:05:21 it consulted the same layers:

- **Orientation:** ALV remained the presumed riser with conviction 1.00. As the riser, ALV did not receive the live faller-only cohort-depth steer.
- **Cohort:** `ATP_CHALL|fav|ge76` had 967 examples, historical rise rate 38.4%, median dip 2, and three-cent reach 0.49. It was consulted and printed in the dossier, but the faller-only law kept it from choosing ALV's price.
- **Staircase/entry table:** the preliminary target was **73**, although the current best bid was 74.
- **Atlas:** `ATP_CHALL|leader|ge75` had 759 examples and bottom depths of 2/5/12 cents. Its p50 path aim was **74**. Its median bottom time was **384 minutes**, which would fall around 7:29 AM—well after this replay's 5:00 AM cutoff and even after the scheduled bell.
- **Contention selector:** the best fitted completion probability was only **2.4%**, below the standing 8% bar, so the selector explicitly said **`DROP`**.
- **The live path governor nevertheless acted:** the current code checks only whether a fitted atlas depth exists, enters an unconditional `if True` branch, and posts the p50 path aim. It does not enforce the selector's `DROP`. The selector wrote a warning; the path governor won.
- **Live-aim library:** again `NO-OPINION`, confidence 0.00.
- **W1 cohort library:** `ATP_CHALL|ge75|lo`, 280 examples, dip frequency 0.714, depths 6/14/37, median time 106 minutes on the mis-anchored clock. Shadow only.
- **Reach law:** at five cents of depth, fitted one-hour fill probability 0.012. Evidence only.
- **Pair arithmetic:** the atlas shadow correctly showed 74 + VAN's saved 22 = 96. A separate dossier surface recorded `combined_at_path: 88` beside `sib_px_est: 21`; 74 + 21 is 95, not 88. This is another unlabeled mixed-state/mixed-aim figure inside the dossier. The actual post still cleared the 97-cent cap.

The final signer was again **`LEGACY:path_aim`**, and the OS posted five ALV contracts at **74**.

### 1:06:04 AM, 353.9 minutes before the bell — the pair is finally recognized

Forty-three seconds after the ALV order was posted, drift saw ALV open 79, last 79, net 0, dip 0. Its cell was `ATP_CHALL|h6 / a95|flat|d0`; it called **`ATP_CHALL-B6`**. B6 had 1,376 examples, median anchor 78, median net +1, median dip 2, and p75 width 8. In plain English: **ALV also looked flat, not like a leg currently making its fitted five-cent dip.**

With VAN B4 and ALV B6, the pair classifier called **`flat_flat`**.

The installed sealed pair policy had valid rows for both bands:

- VAN B4: depth-p90 10, so sealed fish = open 26 - 10 = **16**.
- ALV B6: depth-p90 9, so sealed fish = open 79 - 9 = **70**.

Had sealed authority owned the pair at this point, its alternative numbers were therefore **16 and 70**. It did not own them in this trace. The first orders had already been signed by legacy, and the order-ID normalization defect caused the authority sweep to classify its own resting order as foreign and untouchable. There was no authority re-anchor, no dual-divot steer, and no band recall.

There is also an internal policy contradiction worth naming. The recognition-cascade docstring and its `band_call` log say “READ-SIDE ONLY—no pair policy steers,” while `_price_authority` and the one-authority sweep contain code intended to enforce sealed prices. In this trace the contradiction resolves in favor of legacy because placement precedes the band call and the later sweep loses ownership.

### 1:07 AM through 1:19 AM — hold

The OS repeatedly reviewed both resting orders. Its OS and conviction layers were shadow-only:

- VAN was described as the decay side and repeatedly told to `wait_window`.
- ALV was described as the climb side and repeatedly told to `wait_t90`.
- Both hold reviews initially said projected volume was below the 2,500-share pace target.

No live walk, park, re-aim, cohort re-aim, band recall, or sibling repost occurred. The live orders stayed VAN 22 and ALV 74.

### 1:19:15 AM, 340.8 minutes before the bell — VAN fills

VAN's book moved to 21 bid / 22 ask. The tape printed 22 in three receipts totaling 102 contracts at the same timestamp. Under the stated resting-touch model, five VAN contracts filled at **22**, 1,933 seconds after posting.

Two seconds later reconcile discovered the fill before the per-order fill poll had booked it. The OS logged both a naked-leg defect and an unbooked-fill defect, adopted the five-contract position at 22, and posted a five-contract sell at **28**, using the six-cent B4 width.

For the sibling, the 97-cent headroom after a 22-cent first leg was **75**. The existing ALV bid was already 74, so it fit inside that headroom. The sibling scanner reported `sibling_bid_alive` and did not cancel or re-aim it.

The completion evaluator briefly said a taker completion had positive cross-side EV, but the live operator taker word was false. That layer stayed shadow-only and took no action.

### What the tape did after the decisions

ALV never traded at 74 in the replay window. Its true-print path was:

- 79 at 1:05:15 AM;
- 78 at 2:04:07 AM;
- 78 at 2:06:21 AM;
- 78 at 2:11:27 AM.

Its true low was therefore **78**, four cents above the resting bid. The atlas's five-cent p50 dip did not occur before the replay stopped; its fitted 384-minute bottom time had not arrived.

VAN printed 22 again at 2:15:38 AM and 2:46:01 AM. Its true path low and close in this replay were both **22**.

The lowest tape-proven pair inside this replay was 78 + 22 = **100 cents before fees**. ALVVAN was not a sub-par tape opportunity in this partial window. The OS ended with one filled leg, one live unfilled sibling order, and no completed pair.

At 5:00 AM, 120 minutes before the scheduled bell, the evaluator stopped at the guarded cutoff supplied by the same frozen game tape. This trace does not claim what happened between 5:00 AM and the bell.

## Why legacy won, in code terms

The priority was not “legacy outranked a complete dossier.” It was a sequence-and-ownership failure:

1. The entry path computed and posted the atlas p50 aim before the band cascade had state for that leg.
2. `_price_authority` returns `LEGACY:path_aim` unless the event is already `flat_flat`, the leg already has a band, and the sealed row is loaded.
3. Band state appeared 44 seconds after VAN's post and 43 seconds after ALV's post.
4. The intended later authority sweep could have re-anchored the orders, but reconcile constructed rows with `order_id`/`price` while the sweep consumed `oid`/`px`. It treated the bot's own order as foreign and refused to touch it.
5. Separately, the atlas selector's `DROP` result for ALV was not enforced because path placement enters an unconditional branch whenever a fitted depth exists.

## Decision-layer census for this trace

“Present” means the installed bytes matched the VPS-input manifest at replay time. These model files were built after the July 12 game; this is a replay of the current OS against old tape, not a reconstruction of what the July 12 deployment knew.

| Decision layer | Source read | Source status | Fitted model? | What it said here | Influence on a live order |
|---|---|---|---|---|---|
| Discovery | Frozen Kalshi BBO and true prints | Present | No; deterministic feed handling | Both tickers discovered; waited for traded anchors | Yes; opened the two entry evaluations |
| Bell/window clock | Kalshi schedule plus `observed_starts.db` | Present; no ALVVAN observed row visible on replay clock | No | Scheduled bell 7:00 AM; W1 active | Yes; admitted the entries |
| Sharp FV | VPS `tennis.db` via `analysis/fv_quote.py` | **Absent**; quarantined main-file copy is inconsistent | Yes, external sharp-book blend | `NO-READ` | No vote existed here, but this surface can influence the orientation prior despite its helper's observe-only docstring |
| Orientation prior | `ORIENT_V1`, cohort, sharp FV, anchor role | Present, except FV absent | Yes | ALV riser, conviction 1.00, two voices | Yes for role selection; no role swap was needed |
| Chain-tape orientation | `ORIENT_V1` | Present/current VPS bytes; insufficient first-hour state at entry | Yes | No call yet | No |
| Cohort recognition/aim | `cohort_surface_v1.json` | Present/current VPS bytes | Yes | VAN dog 26–50: median dip 4, aim 22; ALV fav ≥76: median dip 2 | VAN yes at the preliminary target; ALV no because steer is faller-only |
| Entry table/staircase | `entry_tables_sealed_v1.json` plus live book | Present/current VPS bytes | Yes | VAN 22; ALV preliminary 73 | Yes, but atlas later set the final aims |
| Atlas/path aim | `ATLAS_V1.json` | Present/current VPS bytes | Yes | VAN 22, bottom-time median 139m; ALV 74, bottom-time median 384m | **Yes; this was the final pricing path and signer** |
| Contention selector | Atlas contention fields | Present/current VPS bytes | Yes | VAN `TRADE-AT-PATH` 63.8%; ALV `DROP` 2.4% | VAN aligned; **ALV no—the DROP was logged but not enforced** |
| Live-aim posterior | GUIDEBOOK plus local archive-file count | Guidebook readable; archive confidence effectively stale/empty in this worktree | Partly | Confidence 0.00, `NO-OPINION` on both | No; shadow only |
| W1 cohort library | `LIBRARY_V1.json` | Present/current VPS bytes; timing axis explicitly mis-anchored | Yes | VAN 4/6/10, 78m; ALV 6/14/37, 106m | No; shadow only |
| Drift recognizer | `drift_surfaces_v1.json` plus live tape state | Present/current VPS bytes | Yes | VAN B4; ALV B6, both flat | No at placement; calls arrived after orders |
| Band taxonomy | `band_map_v1.json` | Present/current VPS bytes | Yes | B4 flat for VAN; B6 flat for ALV | No direct placement effect in this trace |
| Pair classifier | Two band states and live net moves | Present once both legs had bands | Yes | `flat_flat` | It made sealed authority eligible, but did not move orders |
| Sealed pair authority | `pair_policies_sealed_v1.json` | Present/current VPS bytes | Yes | Alternative fish prices VAN 16 / ALV 70 | No; late state plus ownership-field defect blocked re-anchor |
| Price-authority chooser | `_price_authority` in unchanged `live_v4` | Present code; internally contradictory comments | Deterministic | Legacy at both posts; SEAL eligible only later | **Yes: `LEGACY:path_aim` signed both posts** |
| Order ownership/re-anchor | Exchange-order normalization in unchanged `live_v4` | Present code, **defective field contract** | No | Own order appeared foreign because `order_id/price` became `oid/px` reads | **Yes by omission: prevented sealed re-anchor** |
| Post/hold/walk/park | Live book, order state, OS-shadow state | Present | Mixed rules and shadow models | Post 22/74; repeated hold; no walk or park | Posting and holding yes; shadow recommendations no |
| Fill | Frozen BBO/prints through resting-touch seam | Present | Named deterministic model | VAN filled 5 at 22; ALV no fill | Yes |
| Fill booking/exit | Paper position/order truth through unchanged reconciliation | Present; booking race exposed | No | Adopted VAN at 22; exit posted at 28 | Yes |
| Headroom carry/sibling | Filled basis, 97-cent cap, live sibling order | Present | No | Headroom 75; existing sibling 74 already lawful | Yes; decided to leave ALV unchanged |
| Completion EV | Range-layer model | Present where run-mid existed, otherwise no opinion | Yes | Sometimes `taker_complete`, later `NO-OPINION` | No; operator taker word was false, so shadow only |
| Range-cell-at-entry | Completion-frame band mapping | **Unfitted** | No | `GAP` | No |
| Cash-window timing | Gun-axis lawful-share fit | **Unfitted** | No | `GAP` | No |
| PM reference | PM feed | **Absent** | No | `NO-FEED` | No |

## Artifact status

- Raw trace: `runs/KXATPCHALLENGERMATCH-26JUL12ALVVAN/trace.json`
- Replay summary: `REPLAY_SUMMARY.json`
- Valid for scoring: **no**
- Reason: required transaction-consistent `tennis.db` snapshot absent
- 804-game replay run: **no**
- Proxy work performed: **no**
