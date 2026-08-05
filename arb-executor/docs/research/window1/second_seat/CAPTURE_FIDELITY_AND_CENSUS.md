# Capture fidelity, print autopsy, simultaneity verification, capture-gap census

Analysis seat only. Read-only; no live mutation, no orders/positions/credentials.
Item 1b/2 use an **unauthenticated public** `/markets/trades` read (operator-
requested market data). Machine artifacts under
`.claude/window1_second_seat/v11_non_action_mechanism_audit_20260803/`.

## 1a. Recorder architecture — verdict per channel

Source: `arb-executor/ws_depth_recorder.py` and
`arb-executor/analysis/window1_public_tape_export.py`.

- **Book channel — `ws_depth_recorder.py:3,175`**: subscribes the **WebSocket
  `orderbook_delta`** channel (plus `orderbook_snapshot`, applied at `:92-130`).
  Not REST snapshot polling. The recorder "logs RAW WS messages verbatim with
  receive-timestamps (book reconstructed offline)" (`:1-4`), and the tick tape is
  emitted **per book-change** (sub-second rows at the same `ts_et` prove
  per-delta, not time-sampled). **Verdict: LOSSLESS_BY_DESIGN.** Loss mode named:
  a dropped WS delta with no *online* sequence-gap resubscribe would silently
  drift the reconstructed book until the next snapshot; mitigated because the raw
  messages (carrying Kalshi's `seq`) are logged verbatim, so gaps are detectable
  in offline reconstruction rather than baked in by the capturer.
- **Trades channel — `window1_public_tape_export.py:2,34,90-125`**: prints are the
  exchange **REST `/markets/trades`** feed, **`trade_id`-identified** (`:91-93`),
  following every cursor (`:238-278`), written as canonical true-prints. **Prints
  are NOT inferred from last-price changes** — each exchange trade is a distinct
  `trade_id`, so consecutive same-price trades are **never merged**. **Verdict:
  LOSSLESS_BY_DESIGN.** Loss mode: none at the merge level; completeness is bounded
  only by cursor exhaustion, which the exporter enforces.

Our `prints.jsonl` **is** the exchange `/trades` pull (source `kalshi_public_trade`),
not a tape-inferred artifact.

## 1b. Trades re-pull diff — ARNROM + 20 random games

Re-pulled the complete public trades history **today** for ARNROM (both tickers)
and 20 random games (seed per Jul-22), window-filtered to the guarded window, and
diffed by `trade_id` against our `prints.jsonl`.

**Result: 21 / 21 games PRINTS_FAITHFUL. 0 defects.** Zero exchange trades we lack,
zero we have that the exchange lacks, zero price/size/side/timestamp mismatches,
zero same-price merges. ARNROM: **73 exchange trades = 73 ours**, exact. Full table
in `CAPTURE_FIDELITY_TRADES_DIFF.json`. The architecture's lossless-by-design claim
is confirmed empirically on 42 tickers.

## 1c. Sampling consequence — N/A

The book chain is **delta-based, not sampled**: the 10-second dwell qualifying a
floor is judged on the WS `orderbook_delta` stream (every book change), not on an
N-second sampler. So the dwell-qualified floor is the intended instrument — a
10-second dwell means ten seconds of *unchanged best-of-book across every delta*,
not ten seconds bracketed by two poll snapshots. No correction to the floor work is
implied.

## 2. ARNROM full-print autopsy — `ARNROM_PRINT_AUTOPSY.png`

Built from the **exchange trades re-pulled in 1b** (not our tape); our tape supplies
the bid/ask rails. Two panels (one per side, one clock), full Window 1 + zoom
18:35-18:55 ET Jul 12; every trade a point at its price, colored by rail location
(on-ask = buyer lift, on-bid = seller hit, mid-spread), sized by contracts; marks
at floor `1783896043`, refusal `+1s`, ROM fill `1783896551`, actual bell
`1783946100`. Header carries the schedule name-join (Jul-22 law): **ATP Challenger ·
Bailly vs Romano · Jul 12 2026** — ARN = Gilles Arnaud Bailly (climb), ROM = Filippo
Romano (decay).

**Aggressor story verified by count, not narration** (`ARNROM_PRINT_LOCATION_COUNTS.json`):

| side | on-ask (buyer lift) | on-bid (seller hit) | mid | total |
|---|---:|---:|---:|---:|
| ARN (Bailly, climb) | **41** | 10 | 1 | 52 |
| ROM (Romano, decay) | **19** | 2 | 0 | 21 |

ARN's climb is 41 buyer-lifts to 10 seller-hits (4:1); ROM's walk-down is 19
buyer-lifts to 2 seller-hits. The counts carry the story. This is the standing
autopsy template.

## 3. Sequential-ceiling simultaneity verification

The **390** joint achievable ceiling (`CLOSE_AUDIT_AND_JOINT_CEILING_SUMMARY.json`,
50ce0f49) is defined purely on price — *both maker floors strictly below own audited
close AND maker-floor sum < 100*. **It contains no time-coincidence term** (no
overlap, carry, dwell, or clock enters the count). Confirmed and stamped
`DENOMINATOR_PRICE_ONLY_NO_SIMULTANEITY_TERM`; no correction needed.

The **timing** analyses are the non-denominator sub-question. Stamped
`NON_DENOMINATOR_SIMULTANEITY_FRAMED` **and** `FEES_IMMATERIAL_MAKER_MODE` in the
machine files: `EXECUTABLE_CEILING_SUMMARY`, `CARRY_BUDGET_SUMMARY`,
`CARRY_CENTS_SUMMARY`, `PRINT_BACKED_HARVEST_SUMMARY`, `GATED_HARVEST_SUMMARY`,
`ASYMMETRIC_AUTHORITY_HARDENED`, `MIRROR_ARMING_CEILING_SUMMARY`. The 31-overlap /
359-disjoint counts are a lockability read, not the ceiling; all floors are
residency-maker, so maker-mode fees are immaterial and unmodeled.

## 4. Capture-gap census

Scanned all **1,608 tapes** (804 games × 2 legs) for the longest intra-window
inter-row silence, and built a corpus-wide active-tapes-per-30-min map. Method
(`CAPTURE_GAP_CENSUS.json`): a game is flagged **GAP** only when a ≥1h intra-window
silence **coincides with a corpus recorder-down window** — active tapes collapsing
to ≤25% of the local 3h median while ≥8 neighbours stay busy — which distinguishes a
recorder outage from an ordinary quiet-book overnight lull. Window-1 data is Jul
12–20, **entirely after** the Jul-6 disk crash, so that incident pre-dates the corpus
and cannot touch these tapes.

**Census — 804 games:**

| verdict | games |
|---|---:|
| CAPTURE_CLEAN | **765** |
| GAP | **39** |
| NO_TAPE | 0 |
| **total** | **804** |

Max intra-window silence per game: median **1,014s**, p90 **3,739s**, max **14,035s
(3.9h)** — the long tail is dominated by quiet overnight books, not outages.

**The 39 GAPs are not scattered — they fall in two synchronized recorder-down
episodes** (6 down-bins total, every gap ≥1h and coincident with the corpus dip):

| episode (ET) | games | tour | gap span (each) |
|---|---:|---|---|
| Jul 19 ~20:13–21:53 | 10 | ATP main (`KXATPMATCH-26JUL19*`) | ~1.2–1.8h |
| Jul 20 ~07:06–08:33 | 29 | Challenger (`KXATPCHALLENGERMATCH-26JUL20*`) | ~1.1–2.2h |

GAP durations: min 3,606s, median 5,522s, max **7,829s (2.2h)**. These are
**synchronized cross-tape silences** — dozens of independent markets going dark in
the same wall-clock band is the recorder, not the books. Every flagged game's span
is recorded in `CAPTURE_GAP_CENSUS.json` (`gaps[]`, with `coincides_recorder_down:
true`).

**ARNROM explicitly checked: CAPTURE_CLEAN.** Its longest single silence is 8,996s
(2.5h) but it is an **isolated quiet-book stretch** — it does *not* coincide with any
corpus recorder-down bin (no neighbour collapse), so it is an ordinary low-liquidity
lull, not a capture loss. The ARNROM floor/refusal/fill sequence sits well outside
any silence. The 73/73 print match in 1b corroborates: nothing was dropped on this
game.

**Bounding the impact on the ceiling work.** All 39 GAP games are Jul 19–20 (main +
challenger); none is in the ARNROM-anchored study set, and the outages are overnight
low-volume bands. A silence during a recorder outage means the *floor* on that leg
could be understated (an ask we never saw), which is conservative for a
maker-reachability ceiling — it can only *lower* our measured opportunity, never
inflate it. No GAP game is in the 45 joint-completable pairs.

## 4b. GAP × V28 ceiling cross (3339f30)

The 39 GAP games crossed against **V28's trace at 3339f30**
(`v28_anchor_cap_stack_20260804/EVENT_LEDGER`) — not V23. V28 totals reproduce
exactly: **307 completions** (`completed_pair`) and **65 joint pairs**
(`joint_objective_pass_audited_close`). Recomputing the achievable ceiling from V28's
own leg fields (both `maker_floor_cents` < `audited_close_cents` strict AND floor sum
< 100) reconstructs the canonical surface exactly: **390 WINNABLE / 383 NOT_WINNABLE
/ 31 UNDETERMINED** over 804 — self-check against the 390 (50ce0f49) and the 31
executable-overlap set. Machine artifact: `GAP_CEILING_CROSS.json`.

**Item 1 — 39 GAP vs V28:** **24 / 39** are in the 307 completions, **5 / 39** are in
the 65 joint pairs (MONNES, ALTCOL, STRSHE, LANRAD, PODSTU — all WINNABLE, gap
immaterial to the positive verdict). 18 GAP games are both WINNABLE *and*
V28-completed, so their capture gap can't have hidden the win.

**Item 2 — ceiling verdict cross:** **28 WINNABLE / 11 NOT_WINNABLE**. The 11
not-winnable GAP games are **stamped `CEILING_UNPROVEN_CAPTURE_GAP`** — their negative
verdict rests on a tape carrying a 1–2h synchronized recorder-down silence, so a
qualifying ask may have printed unseen. All 11 are single-cent-fragile, which is why
the gap matters:

| game | cat | floor sum | blocker | gap |
|---|---|---:|---|---:|
| KXATPCHALLENGERMATCH-26JUL20SEYKOL | ATP_CHALL | 100 | sum by 1c (both below close) | 4,730s |
| KXWTACHALLENGERMATCH-26JUL20KABCHI | WTA_CHALL | 100 | sum by 1c (both below close) | 3,905s |
| KXATPCHALLENGERMATCH-26JUL20PIRNAP | ATP_CHALL | 99 | a leg floor ≥ close | 3,964s |
| KXATPCHALLENGERMATCH-26JUL20ALKFIC | ATP_CHALL | 98 | a leg floor ≥ close | 5,831s |
| KXATPCHALLENGERMATCH-26JUL20ZHOGEE | ATP_CHALL | 98 | a leg floor ≥ close | 5,972s |
| KXWTAMATCH-26JUL20GAOTAG | WTA_MAIN | 98 | a leg floor ≥ close | 5,583s |
| KXATPCHALLENGERMATCH-26JUL20CRECOP | ATP_CHALL | 97 | a leg floor ≥ close | 7,829s |
| KXWTAMATCH-26JUL20PARHAV | WTA_MAIN | 97 | a leg floor ≥ close | 5,402s |
| KXWTAMATCH-26JUL20SEMKRA | WTA_MAIN | 97 | a leg floor ≥ close | 5,416s |
| KXWTAMATCH-26JUL20BARYUA | WTA_MAIN | 95 | a leg floor ≥ close | 5,562s |
| KXATPCHALLENGERMATCH-26JUL20GALARN | ATP_CHALL | 35 | a leg floor ≥ close | 4,911s |

Nine fail only on `both-below-close` (sum already < 100); two (SEYKOL, KABCHI) fail
the sum by exactly one cent with both legs already below close. A single unseen
lower ask on one leg flips any of them — hence *unproven*, not *proven-lost*.
ARNROM is CAPTURE_CLEAN (not a GAP game) and is WINNABLE in V28, so it carries no
stamp.

## 4c. Gap-print recovery — resolving the 11 stamps

For each of the 11 `CEILING_UNPROVEN_CAPTURE_GAP` games I re-pulled the public
`/markets/trades` feed over the outage span `[s,e]`, both legs, and set each leg's
floor to `min(recorded maker_floor, lowest missed gap-span print)`, then re-ran the
achievable-ceiling test. A game upgrades to **`WINNABLE_BY_GAP_PRINT`** only if a
missed print flips it. Machine artifact: `GAP_PRINT_UPGRADE.json`.

**N = 1.** Only **CRECOP** upgrades. Its blocker leg COP (recorded `maker_floor 62 =
close 62`) shows **six seller-aggressed prints at 61¢** during the outage (07:10–07:22
ET Jul 20, `taker=no`, sizes 6–64 lots) — the exact `seller_aggressed_traded_low`
term of the maker-floor law (rest-and-be-hit at 61). Our recorder missed all six, so
the recorded floor stayed at 62. True floor 61 → COP 61 < 62 and CRE 35 < 39, sum
**96 < 100** → WINNABLE.

The other **10 stay UNPROVEN** — the rigorous test rejects near-misses that only
print below the *non-blocker* leg's close. Examples: PARHAV had 65 gap-span prints
below close, but all on PAR (already 64 < 67); the blocker HAV (33 = 33) never printed
below 33. SEYKOL/KABCHI (sum = 100) needed a print below a leg's *floor*, and none
came. GALARN is structurally unflippable — its blocker leg GAL closes at **1¢**, and
no print can be below 1¢ (minimum tick). PIRNAP/BARYUA/GAOTAG/SEMKRA blocker legs had
no qualifying missed print.

**Final denominator: 390 + 1 = 391.** The single recovered event is CRECOP; the
capture outage cost the ceiling exactly one provable event, and ten remain genuinely
unproven (not proven-lost).

## Conservation

1a: 2 channels, both LOSSLESS_BY_DESIGN. 1b: 21 games, 21 PRINTS_FAITHFUL, 0 defect.
2: 52 + 21 = 73 ARNROM prints located. 3: 390 denominator clean, 7 timing artifacts
stamped. 4: **804 games = 765 CAPTURE_CLEAN + 39 GAP + 0 NO_TAPE**; 39 GAPs = 10
(Jul19 main) + 29 (Jul20 challenger); ARNROM CAPTURE_CLEAN. 4b: **39 GAP = 28 WINNABLE
+ 11 NOT_WINNABLE(stamped CEILING_UNPROVEN_CAPTURE_GAP)**; 24 in completions, 5 in the
65 joint pairs; achievable ceiling reconstructs 390/383/31. 4c: **11 stamped = 1
WINNABLE_BY_GAP_PRINT (CRECOP) + 10 remain UNPROVEN**; final denominator **391**.

## Artifacts

`CAPTURE_FIDELITY_TRADES_DIFF.json`, `ARNROM_PRINT_AUTOPSY.png`,
`ARNROM_PRINT_LOCATION_COUNTS.json`, `CAPTURE_GAP_CENSUS.json`, plus the
simultaneity/fee stamps written into the seven timing summaries and the 390 summary.
