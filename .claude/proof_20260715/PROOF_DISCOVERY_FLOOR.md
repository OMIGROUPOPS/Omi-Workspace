# OUTCOME PROOF — C-DISCOVERY-FLOOR v1 (C-MORNING-TRIAGE Part 2, 07-15)

**PROVEN SHA: ea0544c8** (`ea0544c802b947af4236daaa4837e19af08be89d` — the code commit this proof covers; cited post-commit per the gate's ancestry law, the 4ddf1083 re-cite pattern).

## PRIOR ART (C45 gate)
- `early_unlock_floor` = 2500 (RULING_EARLY_UNLOCK, 07-09): realized-lifetime-volume floor machinery EXISTS — `event_lifetime_vol` (REST `volume_fp`, rebuilt per discover cycle, atomic swap, live_v4.py ~5202/5343). **Delta: this build reuses that exact organ, adds ZERO new volume plumbing.**
- C-WINDOW-LAW (07-14): W1/CORRIDOR/W2 phase stamps via `_window_phase` (evidence gun closes the corridor). **Delta: the floor keys on the existing phase computation.**
- EARLY-CANVAS-2 / C-CONCEPTION-HORIZON: conception refusals at the path chokepoint with named events + dossier rows (`below_leg_floor_refused`, `no_path_page_refused` patterns). **Delta: one more refusal in the same chain, same emit pattern.**
- `MIN_VOLUME = 0` (live_v4.py:76): discovery currently admits zero-volume markets to conception. No prior floor at conception time exists — grep `discovery_floor` pre-change: 0 hits.

## THE EXHIBIT (VU = KXITFMATCH-26JUL14ALHVUX)
- 12:22:15 AM ET 07-15: path-mode conception, VUX aim 77 (page ITF_M|leader|ge75, discovery 90).
- Exchange tape at conception: **VUX 60 shares lifetime (11 trades), sibling ALH ZERO trades ever** (`skip_no_trade`, `last_trade_age_sec −1.0`) — the pair was one-sided BY CONSTRUCTION (sibling aim 8 on a never-traded book).
- The clock lied: kalshi_schedule said 5:00 AM; the in-play flood started 12:39 AM (tape). The conception was T−17min real, stamped W1 (min_to_scheduled 274).
- Fills 1.08+3.92 @77 (12:25:46 / 12:37:31 — the second tranche 3s before the percat gun); exit 96 never reachable; settled NO 7:10 AM → **−385¢**.
- Post-conception the event discovered 1.34M shares in-play. The 77 bid was filled by the collapse.
- Contrast same class, same minute: ALKLIM (26JUL14, 141 shares discovered) — aim reposted to 14, match_live cancelled both legs 12:40 AM, no fill. Luck of the aim, not design.

## THE ARM
- Operator word (verbatim, vaulted this push): "late buys are not preferable; corridor should only be happening as a fallback when vol is low with ITF."
- New refusal at the SINGLE path-entry chokepoint (all entries flow it — definitive line 07-14): conception REFUSED, named `below_discovery_floor_refused`, when
  (phase == CORRIDOR at placement) OR (event ticker-date < today ET — the lying-clock corridor-equivalent, ALHVUX's mode)
  AND `event_lifetime_vol[et]` < `discovery_floor_shares` (1500).
- Completions NOT gated (pair law: never strand a filled leg). W1 fresh-dated conceptions untouched — measured 8-sample census 07-15: lawful ITF W1 conception sits at 0–140 discovered shares; a blanket floor would starve the lane.
- Knobs: `discovery_floor_enabled=true`, `discovery_floor_shares=1500` — DECREED, cited in knob_citations.json.
- Dossier decision `refused:below_discovery_floor`; event added to `_WINDOW_STAMP_EVENTS`.

## PER-GAME OUTCOME REPLAY (today's slate, exchange tape at each conception instant; /root/proof_discovery_floor.json)
| event | discovered @ conception | verdict | actual outcome | floor's effect |
|---|---|---|---|---|
| KXITFMATCH-26JUL14ALHVUX | 59.9 | REFUSED | VUX 5@77 rode to zero, −385¢ | **+385¢ avoided** |
| KXITFMATCH-26JUL14KOAYAZ | 9.4 | REFUSED | YAZ 5@59→sell 5@76, +85¢ | **−85¢ forgone (named honestly — the operator's REACH-RECAL exhibit trade would not have existed)** |
| KXITFMATCH-26JUL14ALKLIM | 141.3 | REFUSED | no fill (match_live cancelled) | 0 |
| KXITFMATCH-26JUL14IBRBOB | 414.7 | REFUSED | no fill | 0 |
| KXITFMATCH-26JUL14FOMCHA | 12,191.9 | PASSES | unchanged | 0 |
| KXITFMATCH-26JUL14SIKMAT | 2,025.4 | PASSES | unchanged | 0 |
| KXITFMATCH-26JUL14OCODON | 2,588.0 | PASSES | unchanged | 0 |
| KXATPMATCH-26JUL15KYMTSI (corridor) | 20,814.6 | PASSES | unchanged | 0 |
| KXWTAMATCH-26JUL15AVAMAR (corridor) | 53,781.5 | PASSES | unchanged | 0 |

Net on this slate: **+300¢**, 2 no-op refusals, 5 pass untouched. Every other conception today (fresh-dated W1) is out of the predicate's scope — behavior isolation structural (one added refusal branch, no aim/exit/completion change).

## HONEST LIMITS
1. KOAYAZ: the floor kills a proven +85¢ maker round-trip along with the −385¢ ride. Slate net positive; the class balance is graded nightly via `below_discovery_floor_refused` lines (each refusal's counterfactual named in the census).
2. The corridor branch inherits the schedule clock; ALHVUX itself was caught by the STALE-DATE branch, not the corridor branch. Fresh-dated lying clocks (start pulled earlier same-day) remain a blind spot — the honest cure is flow-aware corridor detection (reach-refit territory, already the R1/onset-lag thread).
3. Mains/CHALL corridor placements above the floor still pass (KYMTSI, AVAMAR). The operator's W1-PREFERENCE rule (mains/CHALL corridor refused outright; ITF corridor = fallback only, volume-quiet, dossier-named) is PRICED as its own follow-on and awaits the word after THE MORNING GRADE is read.

## WATCHES
- `below_discovery_floor_refused` per night: each refusal named in the nightly census with its counterfactual outcome.
- Refusals on fresh-dated W1 conceptions = defect (predicate leak).
- `discovery_floor` knobs stay cited; uncited = NAKED (system page law).
