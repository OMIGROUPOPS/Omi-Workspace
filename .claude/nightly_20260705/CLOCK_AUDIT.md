# CLOCK AUDIT — what "scheduled" actually is, and whether the time map survives

## Prior art (gate — added retroactively 2026-07-05 per PRIOR_ART_GATE.md / C45; this audit is the gate's EXHIBIT)
- Greps: `occurrence_datetime|expected_expiration|noon|placeholder|match.start` over LESSONS.md, JUNE_VAULT.md(+APPENDIX), ROADMAP.md, T51_HARDENING_SPEC.md.
- Established BEFORE this audit ran — i.e., §1/§2/§4's placeholder verdict was RE-DERIVED, not discovered:
  - ROADMAP T51:211 (2026-06-01): "`occurrence_datetime`/`expected_expiration_time` are frozen coarse placeholders"; LESSONS §6: "uniform noon-UTC across all main-draw matches".
  - T51_HARDENING_SPEC.md:8: entry buffer keys on a locked-on-first, stale/drifting placeholder ("the T-15m buffer fire[s] at the wrong wall-clock").
  - C32 (2026-05-12): expiration postdates settlement on 100% of the probe sample.
  - OSOWAL (OMQS_LIVE_DUMP_2026-06-30.md): fills 8–10h after "scheduled start". SHINIS (OMQS_LIVE_FORENSIC_SHINIS.md): live scheduled-vs-gun divergence.
  - And `kalshi_schedule_primary` was ARMED Jul 2 against that on-disk characterization (→ JUNE_VAULT §0B, MEASURE-BEFORE-READ).
- Genuine DELTA of this audit (what the record did NOT hold): the per-category offset quantification (+1.8h CHALL / +4.1–4.4h ITF / mains NEGATIVE); the duplication signature (card-marker proof); the tape gun CERTIFIED against an independent per-match anchor (valid ITF/CHALL/WTA_CHALL, INVALID on _MAIN); the time map restated on the honest clock — including **ITF has no premarket** (first posts T+7..+24m after true start), which is the half_timing leak's mechanism.

Measurement only, no builds, no config. Population = the 144 regrade-box games.
Artifacts: `clock_audit.txt` (source/mod-60/duplication/Kalshi fields),
`clock_audit2.txt` (three-clock cross-check vs the independent scheduler),
`clock_audit3.txt` (time map restated vs the honest anchor).

---

## (1) WHICH field the regrade used as "scheduled"

`schedule_match.details.start_time` from the bot log — **method =
`kalshi_schedule_primary` for 144/144 box events, all six categories. No fallback ever
fired, no start_time changed mid-window.** (The kalshi-occ fallback this branch stages is
gated OFF and never touched the box.)

And what that field IS on Kalshi's side: fetched `/events/{ev}` + markets for all 144 —
`strike_date` is not served on these events; the only start-shaped fields are
`open_time` / `close_time` / `expected_expiration_time`. **The stored scheduled field
equals `expected_expiration_time` to the minute on 144/144** (medians of gun−sched and
gun−expected_expiration are identical per category). So the bot's "schedule" and the
Kalshi listing are the same single quantity — Kalshi's expected-expiration placeholder —
and there is no per-match start time anywhere in the Kalshi API surface for these series.

## (2) Timezone check + duplication signature

**Mod-60 histogram of (onset − scheduled), 5-min bins:** spread, no hour spike.
ATP_CHALL 16% within ±5min of an exact hour (uniform expectation ≈17%), ITF_M 21%,
WTA_CHALL 0%. ITF_W shows 50% but n=18 and its stored times are themselves hour-quantized
(see below) — the offsets are NOT hour multiples anyway: the category medians vs true
match time are +1.8h (CHALL) and +4.1–4.4h (ITF), not 60/120/240. **Not a timezone bug.**

**Duplication (session-placeholder signature): LOUD.**
- ATP_MAIN: **one** start_time for all 4 events (09:00×4). WTA_MAIN: same (09:00×4).
- ITF_W: 5 distinct times over 18 events — 13:00×7, 12:00×4, 14:00×4.
- ATP_CHALL: 29 distinct over 87 — 07:00×13, 08:00×5, …
- Versus the independent per-match scheduler on the same events: ITF_W/ITF_M **zero
  duplicates** (16–17 distinct over 16–17). The Kalshi field is a card marker; real
  schedules don't share timestamps.

## (3) Ground-truth spot-check — three clocks

Independent anchor: `state/schedule.json` (TennisExplorer + ESPN overlay, refreshed
every 15min by `refresh_schedule.py`; per-match times, status). 135/144 box events
joined (9 misses are player-code mismatches: MAXSTE, MARNVS, DELNIC, DEKCAK, DESYEV,
PRICOU, RYBTUN, PDACAS, +1 — excluded from the comparison, nothing selected about them).

| event | cat | kalshi stored (=UI/API) | TE/ESPN match time | tape gun | gun−TE |
|---|---|---|---|---|---|
| ITFW BROKOI | ITF_W | 07-05 01:00 | 07-04 21:00 | 07-04 20:37 | −23m |
| ITFW SPIGAR | ITF_W | 07-05 11:00 | 07-05 05:43 | 07-05 06:05 | +22m |
| ITF BOUDOU | ITF_M | 07-05 10:30 | 07-05 04:30 | 07-05 05:41 | +71m |
| ATPCH LEGWIN | ATP_CHALL | 07-04 22:00 | 07-04 20:35 | 07-04 20:40 | +5m |
| WTACH KUDBOU | WTA_CHALL | 07-05 08:00 | 07-05 05:05 | 07-05 05:10 | +5m |
| WTA MUCKRE | WTA_MAIN | 07-05 09:00 | 07-05 08:40 | 07-05 06:11 | **−149m** |
| ATP AUGDAV | ATP_MAIN | 07-05 09:00 | 07-05 10:45 | 07-05 05:32 | **−313m** |

**They are not the same quantity.** Column 1 is a card/session placeholder (note 09:00
shared by every main-tour event). Column 2 is a per-match start. Column 3 (the tape gun)
agrees with column 2 within minutes on ITF/CHALL — and is **broken on main tour**, where
Wimbledon-scale premarket volume trips the burst threshold hours early (AUGDAV −313m,
MUCKRE −149m).

**Full-box validation of the gun (the part that matters):** gun − TE/ESPN median
**+4m ATP_CHALL (n=82), +9m ITF_M, +8m ITF_W, +4m WTA_CHALL**; 61% of all 135 within
±15min, 75% within ±30min. Two fully independent clocks — the volume burst on the Kalshi
tape and a scraped tennis schedule — land on the same instant. The gun is a real
match-onset detector everywhere except _MAIN.

## (4) VERDICT + the time map restated

**The stored "scheduled" field is a session/card marker (Kalshi's
expected_expiration_time placeholder): hour-quantized, duplicated across the card,
sitting ~1.8h (CHALL) to ~4.1–4.4h (ITF) after the true match start. It is not a match
time and it is not timezone-shifted.** The honest anchor is the TE/ESPN per-match time —
which independently certifies the tape gun on ITF/CHALL/WTA_CHALL and convicts it on
_MAIN.

Time map re-run against the honest anchor (`clock_audit3.txt`), minutes before TRUE start:

| cat | BEST median | FILL median | POST median | reading |
|---|---|---|---|---|
| ATP_CHALL | **T−1m** | T−1m | T−2h07m | 82% of best moments inside T-30m→post; we post 2h+ early and wait |
| WTA_CHALL | **T−5m** | T−5m | T−2h14m | same shape |
| ITF_M | **T+33m** (post) | T+31m | **T+24m (post!)** | even our first POSTS land after the match starts |
| ITF_W | **T+13m** (post) | T+17m | T+7m (post) | same — ITF premarket does not exist on the honest clock |
| MAIN (n=8) | T−3h35m | T−2h00m | T−5h06m | the ONLY tier whose money is genuinely premarket; small n |

**The engagement conclusion STANDS, and sharpens:**
- For CHALL: the money is start-adjacent (median best moment T−1..−5m); our engagement
  overlaps it only because bids posted 2h+ earlier survive into it at levels conceived
  before the war. Unchanged from the regrade — now certified against an independent clock.
- For ITF: stronger than the regrade said. It isn't "premarket traded in-play" — **there
  is no premarket at all**: the Kalshi window opens ≈ at the true start (card marker −4h
  ≈ match time), and even our first posts land a median 7–24min after the match begins.
  The half_timing leak (fader divots passing before bounds exist) is this fact wearing a
  leak costume. Deliverable (c)'s "pre-T-4h" window on the card clock is simply the real
  ITF premarket.
- For MAIN: **errata on the regrade** — the 8 main-tour games' per-leg T-gun numbers
  (and their gun-anchored FV-captures) are unreliable; the burst detector fires on
  premarket volume there. On the honest clock, mains are the one tier with a real,
  used premarket (fills median T−2h). The regrade's flaw lines for SABOSA/MUCKRE/HURSTR
  keep their price/level content but their "vs gun" T-stamps should be read against
  TE/ESPN instead.

**Downstream flags (measurement, not builds):** (a) every tts/T-minus quantity computed
off `kalshi_schedule_primary` anywhere in the stack inherits the card-marker distortion
— tier-dependent, ~2h to ~4.4h; (b) `state/schedule.json` (TE/ESPN per-match, already
refreshed every 15min on this VPS, with status transitions) is the honest anchor the
measurement work should use; (c) the gun stays valid as onset for ITF/CHALL analysis and
invalid for _MAIN.
