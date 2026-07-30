# NIK–VRB: one-game live_v4 deconstruction

**Fill model:** a resting maker order fills in full when a later true print or
opposite BBO touches or passes its limit; no depth proof and no five-contract
gate.

This was a lawful two-leg opportunity with exact start evidence. The tape
offered VRB at 70 and later NIK at 18. Their authoritative Window‑1 closes were
83 and 19, so the tape’s reachable pair cost was 88 and its combined close
reference was 102: **−14¢ combined delta, with both legs individually below
their own closes.**

The OS did not complete it. It filled only NIK at 24. The decisive mistake was
sequence: VRB’s 70 low arrived first, the OS aimed below it at 67 and 65, and
then it did not raise VRB to 73 until after NIK filled more than three hours
later.

## The clock

- Frozen evaluator window: 4:30:00 AM–12:34:00 PM ET.
- Scheduled start known to the live OS: 12:30:00 PM.
- OS gun: 12:30:12 PM from price divergence.
- Evaluator cutoff: 12:34:00 PM, using the exact guarded start evidence.
- Fill model saw 12,908 BBO ticks and 143 true prints.
- Archived history did not extend to the gate: first BBO was 6:14:33 AM,
  first NIK print 6:28:01, first VRB print 7:13:56.

## What happened, in order

### 4:30–6:14 AM — admitted, but blind because the retained tape had not begun

The T−8 admission gate opened at 4:30. The catalog and schedule matched the
event, but neither book had a retained BBO or print yet. Discovery kept the
event alive; it could not consult a lawful last-traded anchor.

At 6:14:33 the first BBO arrived. VRB still had no print, so the OS entered one
durable `skip_no_trade` state. It observed that same condition 349 times without
creating 349 incidents. The state ended at 7:13:58 when VRB’s first print became
available.

### 6:28:05 AM, T−361.9 — first NIK consultation

NIK printed 33. The book was 23 bid / 33 ask, so the live anchor was the fresh
33 print.

The organs said:

- **Orientation:** VRB is the riser, conviction 1.00, two voices. Cohort voted
  for VRB with weight 2; the current leader/dog role voted for VRB with weight 1.
  Chain orientation and external FV supplied no vote.
- **ATLAS shape:** NIK is on `ATP_CHALL|underdog|26_50`, n=1,470. Dip depth
  p25/p50/p75 = 2/4/7¢. Its old timing field was refused because its onset clock
  does not match the live scheduled-start clock.
- **Cohort:** `ATP_CHALL|dog|26_50`, n=2,053, dip p50=4¢,
  61% reach at 3¢, rose rate 34%. It moved the preliminary target from 30 to 29.
- **Flow/reach:** quiet, one print in 30 minutes, estimated one-hour reach at
  the 4¢ depth only 2.0%.
- **Contention:** TRADE-AT-PATH, best tier p75 at 26.1%.
- **Pair:** composed at a projected 93, using sibling estimate 67.
- **External books:** no Odds API rows; `stale_sources`, no FV.
- **Polymarket:** `NO-FEED`.
- **Library:** `NO-OPINION`, confidence 0.00.
- **Price authority:** `LEGACY:path_aim`, meaning the deployed ATLAS path.

ATLAS won and posted NIK 29. Fifty-two seconds later the band cascade called
NIK flat, band B4. That band read did not precede or price the order.

The tape then printed NIK 32 at 6:55.

### 7:07:33 AM, T−322.4 — NIK reprices

The book tightened to 29/30 while the last print remained 32. Because the print
sat outside the tight book, the live anchor switched to the 30 tight-mid.
The 29 order was cancelled as marketable-stale.

The organs were materially unchanged: VRB still the riser; ATLAS still 4¢
deep; cohort still 4¢; flow still quiet; pair still composed at 93; no external
FV, no Polymarket, no library opinion. Contention strengthened to 39.4%.

ATLAS posted NIK 26.

### 7:13:56–7:13:58 AM, T−316.1 — VRB reaches its Window‑1 low, then the OS aims below it

At 7:13:56 VRB’s first true print was **70**. This was also its lowest lawful
price of the entire window.

Two seconds later the OS consulted:

- Book 69/70, fresh last trade 70.
- Orientation: VRB riser, conviction 1.00.
- ATLAS leader page `ATP_CHALL|leader|51_75`, n=1,614,
  depth 1/3/6¢.
- Cohort `ATP_CHALL|fav|51_75`, n=2,008, dip p50=4¢,
  reach-at-3¢ 58.7%, rose rate 37.3%. Riser steering was barred.
- Flow quiet; one-hour reach estimate for 3¢ depth 3.7%.
- Pair composed at 93.
- External FV absent; Polymarket absent; library no-opinion.
- **Contention said DROP at −6.5%.**

The deployed flag did not enforce DROP. The wrongness monitor recorded
`VERDICT_IGNORED`, and ATLAS posted **67**, three cents below a tape whose
lowest price was 70. It could not fill.

### 7:14–7:15 AM — flat-flat is recognized, but the authority label and order diverge

At 7:14:42 the band cascade called VRB flat/B4 and the pair classifier called
the pair `flat_flat`.

At 7:15:43 the book was 67/68 and the fresh reference resolved to tight-mid 68.
ATLAS aimed 65. Contention again said DROP, now −4.2%, and was again ignored.

The dossier now named sealed authority and said its fish was **60**. But the
actual order was **65**, the ATLAS path aim, because
`pair_class_steer_enabled=false`. This is not two equivalent descriptions of
one order: it is a named authority that did not control the chokepoint. The
sealed 60 would also have missed the 70 low, but the structural discrepancy is
real.

The tape moved away: VRB printed 73 at 7:43 and 74 at 7:56.

### 7:51:21 AM, T−278.6 — final NIK conception

NIK printed 28 against a 24/27 book. The fresh last trade anchored the decision
at 28.

- Orientation still called VRB the riser.
- ATLAS NIK depth remained 4¢ and aimed **24**.
- Cohort remained 4¢; flow was quiet with two prints in 30 minutes.
- Contention said TRADE-AT-PATH at 50.5%.
- Pair projected 93 with sibling estimate 72.
- External FV and Polymarket remained absent; library remained no-opinion.
- The dossier named sealed fish 23, but the order again used ATLAS at 24.

The OS posted NIK 24. That order rested for 10,116.5 seconds.

### 10:39:57–10:40:14 AM, T−110 — NIK fills; coupling reacts too late

At 10:39:57 NIK printed 24 and filled the five-contract resting order. The bulk
receipt saw it immediately, the OS booked the entry at 10:40, and it posted the
NIK exit at 31.

This fill was not Window‑1 value: NIK later closed at 19, so the signed entry
delta was **+5¢**, and its eventual low was 18, making the fill **6¢ above its
own fillable low**.

After the fill the coupling code finally took control:

`97 combined goal − 24 filled basis = 73¢ sibling headroom`.

It raised VRB from 65 to 73. At that moment VRB was already 73/77 with a last
print of 76. Its 70 low had occurred about 206 minutes earlier. The coupling
used the current book and the arithmetic headroom; it had no state saying
“VRB’s low came first and is already gone.”

### 10:40–11:09 AM — mechanical chase, no second fill

VRB never printed below 74 after NIK filled. The OS toggled its resting order
between 72 and 73 as the BBO moved:

- Five print-backed `window_truth_reaim` changes.
- Nine move/repost cycles.
- No fill, because neither the true prints nor the opposite BBO reached 73.

This is what the BBO micro path does: book maintenance, fill tests, guard
reruns, and resting-order management. It did not produce a new directional
forecast.

At 11:09:33 the band cascade finally recalled VRB from flat/B4 to faller/B2,
after the tape had already moved through 77 and 81. It was descriptive, not an
early call.

### 11:38–12:34 — the other low arrives; the pair remains backward

NIK reached its true low, 18, at 11:38:49 and later closed at 19. This low came
about 265 minutes after VRB’s 70 low. The lawful opportunity therefore required
VRB first, NIK second.

At 12:10 the OS still capped VRB at 73 even though the book was 81/84. At
12:30:12 its price-divergence gun fired, and at 12:30:33 it cancelled the VRB
order. The evaluator continued to the 12:34 exact cutoff; no second fill
arrived.

## Outcome

- Tape opportunity: VRB 70 first, NIK 18 later; cost 88; combined delta −14.
- OS fill: NIK 24 only.
- NIK signed delta to its own close: +5¢.
- VRB signed delta: undefined, because it did not fill.
- Pair completed: no.
- Hypothetical 24+73 would have cost 97 and produced −5¢ combined delta, but
  the 73 never filled.

## What this game proves

The missing piece is not “leg coupling” in the binary sense. Coupling exists,
but it governs orientation, caps, and post-fill headroom. It does not choose the
chronological order of the two lows. In this game the OS correctly recognized
VRB as the riser, then used a symmetric dip aim that sat below VRB’s entire
lawful tape. It filled the late leg first and only then chased the early leg.

It also proves three silent control discrepancies on one game:

1. ATLAS was consulted on a last-trade/tight-mid key although its fit key was
   first-hour median: five `FIT_CONSULT_KEY_MISMATCH` alarms.
2. Cohort had no machine-readable fit contract: five `FIT_CONTRACT_MISSING`
   alarms.
3. Contention returned DROP twice and the order path posted twice: two
   `VERDICT_IGNORED` alarms.

The raw, chronological decision rows supporting this narrative are in
`NIKVRB_DECISION_TRACE.json`. The full local replay trace is
`../one_game_nikvrb_final_20260730/runs/KXATPCHALLENGERMATCH-26JUL19NIKVRB/trace.json`.
Its SHA-256 is
`5dd923fb3636926165e651668954f6b778e9d4c8811b2254f3102a9aa05302cc`;
the `live_v4.py` hash recorded both before and after that replay is
`f6fb1d20f3943f7bac26d94ccf1e9d98a5f22762cd3357394adfc8a3b108d760`.
