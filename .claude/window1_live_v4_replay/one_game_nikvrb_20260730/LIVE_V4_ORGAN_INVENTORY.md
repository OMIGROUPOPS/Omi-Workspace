# live_v4 organ inventory — code versus replay availability

The organs exist, but several are passive, mis-keyed, or not authoritative. The
ALVVAN trace was not proof that they were absent. In NIK–VRB the unchanged live
decision chain ran; the gaps below are either missing replay data or live code
that computes an opinion without controlling the order.

| Organ | What exists in live code | NIK–VRB input/output | Does it control an order? |
|---|---|---|---|
| Discovery and schedule | `discover_markets`, catalog matching, observed-start reads, and the 8-hour conception gate | Event discovered; scheduled start 12:30 PM ET; guarded evaluator cutoff 12:34 PM | Admission and gun handling, yes |
| Odds API / sharp-book FV | `tennis_odds.py` stores every book; the blend uses Pinnacle, Betfair Exchange EU, and Matchbook. `fv_quote.sharp_fv` requires all three fresh within 60 minutes and averages their no-vig prices | The frozen `tennis.db` has zero `book_prices` rows for this event, so every consultation returned `stale_sources` with an empty source list | As a fresh orientation vote, potentially. Direct FV pricing is disabled in the deployed config |
| BetExplorer | A fallback reader exists in `fv_quote.py` | No usable row in this trace | Display-only; never blended or authoritative |
| Polymarket reference | `live_v4` reads `state/polymarket_ref.json` into the dossier | File absent in the replay worktree; every consultation said `NO-FEED` | No. Even with data it is dossier-only |
| Orientation / directional prior | `_orientation_prior` combines chain-tape orientation, sharp FV, cohort rose rate, and incumbent leader/dog role | Chain and FV supplied no vote. Cohort plus anchor role both called VRB the riser: conviction 1.00, two voices | Yes, but only as the shallow/deep park role. It does not sign a directional price forecast |
| Cohort | `cohort_surface_v1.json` is loaded; faller steering is live | NIK cell: dip p50 4¢, n=2,053, reach-at-3¢ 61%, rose 34%. VRB cell: dip p50 4¢, n=2,008, reach-at-3¢ 58.7%, rose 37.3% | NIK could steer because it was the faller. VRB was the riser and riser steering is disabled |
| Drift and band cascade | `drift_surfaces_v1.json` and `band_map_v1.json` are present and loaded by the cascade | Both legs were called flat/B4 after their first orders. VRB was recalled as faller/B2 at 11:09 AM, after its price had already risen from 70 to 77–81 | Read-side in this trace. It did not set the initial order |
| ATLAS path aim | ATLAS pages are consulted in `_v4_entry_anchor`; deployed mode is `ATLAS` | NIK page predicted 4¢ p50 depth; VRB page predicted 3¢. It produced all five initial aims | Yes. This was the actual initial-order signer |
| ATLAS timing | The pages carry old onset-relative timing | Every dossier refused the timing field because the live consumer clock is scheduled-start-relative | No timing trigger |
| Guidebook/library | `liveaim_shadow` consults the guidebook/library | `lib_conf=0.00`, `NO-OPINION` on all five decisions | No; shadow only |
| Contention selector | Computes `TRADE-AT-PATH` or `DROP` | NIK: TRADE. VRB: DROP twice, at −6.5% and −4.2% | No. `contention_drop_enforced=false`; both DROP verdicts still posted and raised `VERDICT_IGNORED` alarms |
| Pair composition | Pair verdict composes own and sibling pages against 97 | `PAIR-COMPOSED`, projected cost 93 on all five consultations | It can refuse at the seesaw guard, but it does not optimize both legs jointly |
| Sealed authority | `_price_authority` can name `SEAL`; sealed pair and entry files are present | At 7:15 it named VRB seal fish=60 while the order posted 65. At 7:51 it named NIK seal fish=23 while the order posted 24 | Not on initial entry because `pair_class_steer_enabled=false`. The dossier’s authority label can therefore disagree with the actual signer |
| BBO/micro mechanics | Every BBO update refreshes the book, tests resting fills, routes the event, and manages resting orders. Production coalesces repeated frames to the latest state | 12,908 replay BBO ticks drove cancellations, reposts, pair checks, and fill tests | Mechanics, yes; predictive micro signal, no |
| Round-5 micro detector | A four-signal detector is named in code | `round5_detector_fire` is an explicit `return False` stub | No |
| Flow state and reach law | Trade deque, volume tracker, 30-minute print count, quiet/active bucket, and reach estimate exist | Every consultation said `quiet`; one or two prints in 30 minutes; one-hour reach estimates 1.0%–3.7% | Dossier/shadow only. Flow does not open the aim window |
| Fill receipt | Paper/order state, bulk fill poll, and reconciliation paths exist | NIK’s 24¢ trade touch was seen by the bulk receipt at 10:40 and booked without a late reconciliation miss | Yes; state booking |
| Leg coupling before a fill | Orientation reads both books. Pair composition and `_pair_seesaw_state` read the sibling’s current BBO and fitted deep aim | The OS understood VRB as riser and kept projected pair cost inside 97 | Yes as roles/caps/refusals, but not as a two-leg sequence optimizer |
| Leg coupling after a fill | `_reaim_sibling_on_arrival` carries `combined_goal - filled_basis` | NIK filled at 24, so VRB headroom became 73. The OS moved the sibling from 65 to 73 and then oscillated 72/73 | Yes, but only after the first fill and with no memory that VRB’s 70 low had occurred 206 minutes earlier |
| Gun and evaluator horizon | The OS may sweep at its gun; replay evaluator continues to the guarded actual-start cutoff | OS gun fired 12:30:12; evaluator continued to 12:34 | Yes |
| Pre-gate tape | Production discovers/subscribes as far as 36 hours out. Replay streams only the frozen interval plus one prior BBO seed | For this event the archived BBO begins 6:14 AM, NIK prints begin 6:28, and VRB prints begin 7:13. There are zero retained prints or BBO rows before the 4:30 AM T−8 gate | Absence in retained data for this game, not an intentional replay exclusion of available pre-gate rows |

## Plain-English answers

**External blend:** the organ exists. NIK–VRB had no Odds API rows in the frozen
database, so it produced no FV. The blend’s docstring calls it logging-only,
but `_orientation_prior` also consumes a fresh FV gap as a weighted directional
vote. Direct FV price anchoring is a separate legacy path and is disabled.
Polymarket is another read-only dossier input; its missing file caused
`NO-FEED`, but even a present file would not price or veto an order.

**Leg coupling:** it exists in fragments: orientation, a pre-fill pair cap and
seesaw test, and post-fill headroom carry. What does not exist is a joint,
time-aware policy that chooses which low to catch first or remembers that one
leg’s lawful low has already passed.

**Micro layer:** the live BBO path is operational mechanics, not a predictive
micro organ. It updates the book, checks fills, reruns gates, and moves resting
orders. The named four-signal micro detector is still a stub. Flow is measured
and logged but does not activate or price an aim.

**Directional call:** orientation calls a riser/faller before aiming, but ATLAS
still applies a dip-depth page. Direction changes which leg parks shallow versus
deep; it is not a forecast that says “this leg will rise now, so join it before
the move.” Band direction arrived after the first orders in this game.

**Gate versus market history:** T−8 is only an admission gate in live code.
The production subscriber can watch markets up to 36 hours out. The retained
NIK–VRB archive, however, starts inside T−8, so there was no earlier tape for
this replay to use.

## Code anchors

- Odds ingestion and sharp-book list: `arb-executor/tennis_odds.py:49`,
  `arb-executor/tennis_odds.py:256`, `arb-executor/tennis_odds.py:348`
- Sharp FV contract: `arb-executor/analysis/fv_quote.py:39`,
  `arb-executor/analysis/fv_quote.py:77`,
  `arb-executor/analysis/fv_quote.py:118`
- FV and Polymarket dossier reads: `arb-executor/live_v4.py:3465`,
  `arb-executor/live_v4.py:3486`, `arb-executor/live_v4.py:8942`
- Orientation and FV vote: `arb-executor/live_v4.py:4191`,
  `arb-executor/live_v4.py:4236`
- Pair seesaw and post-fill carry: `arb-executor/live_v4.py:3057`,
  `arb-executor/live_v4.py:7263`
- Actual initial aim and sealed authority: `arb-executor/live_v4.py:4943`,
  `arb-executor/live_v4.py:4141`
- BBO ingest and routing: `arb-executor/live_v4.py:6518`,
  `arb-executor/live_v4.py:12378`
- Stub micro detector: `arb-executor/live_v4.py:10980`
- Admission horizons: `arb-executor/live_v4.py:88`,
  `arb-executor/live_v4.py:1867`
- Replay clipping and prior seed: `arb-executor/analysis/window1_live_v4_replay.py:358`,
  `arb-executor/analysis/window1_live_v4_replay.py:922`
