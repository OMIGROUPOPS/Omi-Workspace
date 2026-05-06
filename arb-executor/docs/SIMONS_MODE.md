# SIMONS_MODE.md — Operating Philosophy for OMI Tennis Bot Strategy

**Status:** Canonical doc. Lives alongside LESSONS / ROADMAP / ANALYSIS_LIBRARY / TAXONOMY. All strategy/operating decisions derive from this document. Anything not here that contradicts here is superseded.

**Created:** 2026-05-06 ET (Session 9).

**Purpose:** Establish the lens through which all OMI tennis bot work is interpreted, prioritized, and executed. Replaces the implicit lens that has been operating to date with an explicit, named philosophy. This document is meta — it doesn't contain analytical findings; it specifies how analytical findings should be acted upon.

---

## Section 1 — Core Philosophy

The operating frame is **Renaissance/Simons-style systematic alpha extraction**, adapted to the specific structure of Kalshi tennis binary markets. The lens is not folk-Simons ("math genius, mysterious"). It is operational-Simons:

1. **Pattern detection from massive data.** Decisions derive from statistical structure observable in the historical record, not from individual trade theses or player handicapping.
2. **No directional thesis on outcomes.** The bot does not predict who will win. It does not handicap matches. It does not compete on prediction accuracy with anyone.
3. **Mechanical execution.** Once a pattern is identified, execution is rule-based: post bid, post resting sell, wait. No active monitoring decisions. No "should I take profit now" judgment calls.
4. **Brutal selection discipline.** Most candidate strategies/cells lose money in expectation. Renaissance-style operation means committing capital only to the small fraction with verified edge above fee floor + costs.
5. **Willingness to abandon "intuitive" strategies for "weird but verified" ones.** If the data says cells that look uninteresting to human intuition have edge, capital goes there. If cells that look intuitively attractive have no statistical edge, capital does not go there regardless of how good the story sounds.
6. **Adaptive on regime change.** When something stops working, the response is to detect the regime change quickly and shut down the affected strategies, not to "wait for it to come back" or "trust the long-run statistics."

This is not a creative philosophy. It is an austere one. Most of the work is killing strategies that don't have edge so capital concentrates on the few that do.

---

## Section 2 — Market Structure (Axioms)

These axioms are load-bearing. All strategic reasoning in the new chat starts from these. If something contradicts an axiom, the axiom wins until proven otherwise empirically.

### Axiom 1 — Kalshi is a peer-to-peer prediction market, not a sportsbook.

CFTC-regulated as a Designated Contract Market. Every contract has a counterparty who is also a trader, not "the house." When the bot buys YES at 30¢, somebody else is selling YES at 30¢. The somebody is a person — usually retail — making a different judgment about the same event.

### Axiom 2 — The price is not trying to be fair value.

It is the clearing price between two counterparties with different information, different risk tolerances, and different time horizons. There is no market-maker keeping the line tight. There is no vig structure pulling prices toward efficiency. The price is wherever the marginal counterparty pushed it, and the marginal counterparty is usually retail.

### Axiom 3 — Mispricing is the default state, not the exception.

A market can sit 5-10c off any reasonable fair-value model for hours. It does not "snap back" because there is no professional flow keeping it tight. The mispricing is the structural condition, not a temporary anomaly.

### Axiom 4 — The bot's edge is not predictive sophistication.

It is mechanical, infrastructure-driven counter-positioning to retail behavior patterns that are persistent enough to trade against systematically.

### Axiom 5 — Tennis is a slow game.

Points: 5-30 seconds. Games: 4-8 minutes. Sets: 30-60 minutes. Match: 1.5-4 hours. **The mispricings the bot harvests happen at minute-to-tens-of-minutes timescale.** The bot does not need tick-level execution; it needs minute-level signal correctness. This is structurally favorable: the slowness creates room for resting orders to fill predictably.

### Axiom 6 — Two binary tickers per match, not one.

Every tennis match has two Kalshi tickers — one for each player's match-binary. They are economically linked (a YES on Player A is approximately a NO on Player B) but they are separate orderbooks with separate liquidity, separate OI, separate counterparty pools. This creates structural opportunities (B24 cross-ticker asymmetry, B23 bilateral capture) that single-ticker strategies cannot access.

---

## Section 3 — The Alpha Thesis

The bot extracts **bounce-capture** from intra-match volatility.

Even when a player will eventually win, the price path to settlement is non-linear. It oscillates as game state evolves: breaks of serve, holds, set wins, momentum shifts. **These oscillations are inefficiently priced in real-time** because retail counterparties:
- Overreact to in-game events (sell on a break of serve, buy on a hold)
- Position emotionally in premarket (positioning on news, late arrivers)
- Rarely run model-based fair-value calculations
- Do not arb across the two paired tickers

The bot's job is to identify market states (cells) where this oscillation is statistically reliable enough to harvest. Not predict the eventual winner. Not identify mispriced favorites. **Capture the path-to-settlement variance.**

### How the alpha is captured operationally

1. **Entries are premarket only.** Premarket is the semi-stable environment where resting maker bids fill predictably. Once a match starts, prices gap on early game events; resting bids either get blown through or fill at terrible prices. Do not chase live games. Position before the bell.
2. **Exits have two windows.** A position established premarket can be cashed:
   - **Exit Window 1 — premarket itself.** Price oscillates within premarket; if the target bounce hits before match start, exit in the calmer environment.
   - **Exit Window 2 — in_match.** If premarket didn't deliver, the position rides into the match and game momentum provides exit volatility.
3. **Exits are automatic.** Once a buy fills, a resting limit sell goes up at entry + cell-specific bounce target. If the price kisses, it fills. If not, time-stop or settlement closes the position. No active decisions after order placement.
4. **Bilateral capture (B23) is an amplifier, not a hedge.** When both sides of a paired event have entered cells that look attractive at sub-mid prices, both cells are entered independently. Premarket oscillations exit one side; in_match momentum exits the other. Same paired event, two independent profitable exits. This is feasible on ~30% of markets per Cat 6 (the 30% with ≥10c premarket trajectory).

### What the alpha is NOT

- ❌ Predicting outcomes
- ❌ Identifying mispriced favorites/underdogs by handicapping
- ❌ Running a directional strategy
- ❌ Beating a consensus model
- ❌ Sophisticated execution / HFT-style microstructure
- ✅ Selecting cells where retail-driven oscillation is statistically reliable, then mechanically harvesting

---

## Section 4 — The Two Distinct Problems

A common error is treating the bot's edge as a single problem. It is two distinct problems with very different difficulty profiles. This distinction is critical for prioritization.

### Problem 1 — Cell selection (the hard problem)

Which (cell, policy) combinations have positive expected value above fee floor + spread cost? Most do not. Per Cat 5 (commit 631e653), median EV across all (cell, policy) combinations is NEGATIVE; only the top 5% have positive EV. **The entire strategic question reduces to: are we trading in the 5%, or in the 95% sea?**

This is where energy goes. Forensic replay of the historical record. Validation that simulator predictions match real outcomes. Iteration on cell definitions. Identification of which counterparty behaviors create the harvestable patterns.

### Problem 2 — Execution (the easy problem)

Once a cell is selected:
- Entry: post a maker bid at cell's intended price. In premarket, books are slow and stable; queue position issues are not the dominant failure mode. The bid either fills cleanly or doesn't.
- Exit: post a maker sell at entry + bounce target. Order rests. Either kisses or doesn't.
- The bot's existing live_v3.py logic handles both. Cell-drift between post-time and fill-time is a real but second-order concern.

In premarket Kalshi tennis with slow books, "execution risk" in the HFT sense (queue position, partial fills, adverse selection in the same way it bites in equity HFT) is **largely irrelevant**. The bot is providing liquidity in a slow venue against retail flow. Once a cell is correctly selected, execution is mostly mechanical.

### The implication

Most analytical effort goes into Problem 1. Problem 2 is treated as solved-enough by existing infrastructure unless evidence suggests otherwise. The new chat should not get distracted building high-fidelity execution simulators. Effort goes into validating which cells have edge.

---

## Section 5 — Data Regimes Available

The new chat should understand precisely what each data source can and cannot answer.

### G9 historical corpus (load-bearing)

`data/durable/g9_metadata.parquet` — 20,110 markets × 48 cols. Per-market: ticker, _tier, open_time, close_time, event_ticker, final OI, volume, status, settlement value.

`data/durable/g9_trades.parquet` — 33,727,162 rows × 7 cols × 52 row groups. Microsecond-precision tick tape: ticker, count_fp, created_time, no_price_dollars, taker_side, trade_id, yes_price_dollars.

`data/durable/g9_candles.parquet` — 9,500,168 rows × ~24 cols × 24 row groups. Per-minute OHLC: price_close, yes_ask_close, yes_bid_close, end_period_ts (int64 epoch sec), open_interest_fp.

**What it answers:** Market microstructure history. What prices traded at, when. What the BBO looked like. What OI looked like (with caveats — see F31 amendment in LESSONS, commit 9c93505). **Tick-by-tick, minute-by-minute, market-by-market reconstruction is possible from these three files alone.**

**What it does NOT answer:** Pre-existing orderbook depth at non-BBO levels (queue position). This is F33 / G13 — the truly missing data piece. Forensic replay assuming idealized maker fill at price-touch is the closest available approximation.

### Layer A v1 / Layer B v1 derived parquets

`data/durable/layer_a_v1/cell_stats.parquet` — 671 cell aggregates.
`data/durable/layer_b_v1/exit_policy_per_cell.parquet` — 19,170 (cell, policy) rows with simulated EV, fire rate, capture distribution.

**What it answers:** What the simulator predicts each cell-policy combination will yield, given idealized assumptions.

**What it does NOT answer:** Whether those predictions hold up against real outcomes. The simulator imposes assumptions about cell handling that haven't been validated against tick-level reality (Layer C v1 / T32b is exactly this validation work).

### kalshi_fills_history.json — 7,489 actual historical fills

**What it answers:** What the bot actually did when it was live. Real fill prices, real fill times, real cell-state-at-fill, real realized P&L.

**What it does NOT answer:** Cells the bot didn't post in. The fills are conditional on the bot's prior strategy — they reflect what the bot looked at, not what the bot could have looked at.

### Paper mode (live_v3.py since Apr 29 with deploy_v4_paper.json)

**What it answers:** Whether the bot's signal generation logic produces sensible decisions on current real-time data.

**What it does NOT answer:** Whether those decisions would have actually filled at those prices, or what realized P&L would have been after queue dynamics. Paper mode pretends-fills, which collapses out the execution dynamics. **Paper mode is a strategic simulator, not an execution simulator.**

---

## Section 6 — The First Concrete Deliverable: Forensic Tick-Level Replay

The new chat's first major analytical deliverable is a **forensic tick-level replay framework** for evaluating cells against historical reality.

### What it does

For any candidate (cell, policy) combination:
1. Identify all moments in the G9 corpus where Cell X's conditions held during premarket.
2. Hypothetically post a maker bid at the cell's intended price.
3. Walk g9_trades forward second-by-second from T0. Record cell drift if/when it occurs.
4. First trade that prints at or below our bid → mark filled at our bid price.
5. Record fill-time cell state.
6. Hypothetically post a resting sell at fill price + target. Run TWO parallel scenarios:
   - **Scenario A:** Sell at fill price + post-time-cell's bounce target
   - **Scenario B:** Sell at fill price + fill-time-cell's bounce target
7. Walk forward through g9_trades. First trade at or above either sell price → exited.
8. Record realized capture, time-to-fill, time-to-exit, win/loss.
9. Aggregate across thousands of moments per cell.

### What it produces

Per (cell, policy) candidate:
- Distribution of realized capture vs Layer B v1 simulator's predicted capture
- Distribution of cell drift between post-time and fill-time
- Comparison of post-time-target vs fill-time-target outcomes (which is better?)
- Win rate, time-to-fill, time-to-exit
- Fee-adjusted realized EV per moment

### Why this is the right deliverable

- **It uses the data directly.** No simulator abstractions. No execution assumptions beyond "idealized maker fill at price-touch."
- **It answers the cell-drift question explicitly.** Not as a theoretical concern but as a measured empirical effect.
- **It validates Layer B v1's simulator against reality.** If realized tracks simulated, the alpha framework is sound and the bot can be pointed at the verified top cells. If realized diverges, we understand the bias and fix it.
- **It directly informs which cells the bot should fish in.** Output is actionable: a ranked list of cells with verified edge above fee floor.

### Output location

`data/durable/forensic_replay_v1/` (new). Per-(cell, policy) parquet outputs + summary.

### Caveats

This probe assumes idealized maker fill (the price touched our bid → we filled). Real queue position is not captured. This is the right caveat to live with for now because (a) tennis premarket books are slow enough that queue effects are second-order, (b) F33 / G13 orderbook-snapshot collection would be required to do better, and (c) the bot's existing live_v3.py mechanics already operate with these assumptions implicitly. **Calibrate against `kalshi_fills_history.json` realized fills as a sanity check** — if forensic replay predictions are systematically optimistic vs actual realized fills, the queue effect is calibratable.

---

## Section 7 — Rollback Discipline

When the new chat (or Druid, or any subsequent operator) feels lost, drifting, or uncertain, return to first principles in this order:

1. **Are we in Simons-mode?** Mechanical, pattern-based, no directional thesis, willing to abandon strategies that don't have edge.
2. **Are we honoring the market structure axioms?** Peer-to-peer venue, retail counterparties, mispricing as default state, oscillation-driven alpha.
3. **Are we working on Problem 1 (cell selection) or Problem 2 (execution)?** If Problem 1: continue. If Problem 2: ask whether this is necessary or whether we're getting distracted.
4. **Are we letting the data tell its own story?** Or are we overlaying our intuitions onto it? The data should be allowed to surprise us. If a cell looks uninteresting but has edge, it has edge. If a cell looks attractive but doesn't, it doesn't.
5. **Are we in the 5%, or the 95% sea?** Most cells lose money. The discipline is concentration on verified edge, not exploration of plausible-sounding ideas.

If any of those answers feels off, stop the current work and resolve the framing question first.

---

## Section 8 — Cross-References

### LESSONS.md (load empirically; treat as mostly correct but not infallible)
- **Category B (strategic):** B22 cell anchoring, B23 bilateral capture, B24 cross-ticker asymmetry. **Note:** B23 amended down — bilateral feasibility is 29.8% of markets, not the default. B24 amended down — 4× anchor is top 2-3% tail, 2× is the strategic threshold.
- **Category E (operational):** E16 in-match P&L dominance. **Note:** E16 needs refinement — aggregate-P&L dominance of in_match doesn't mean per-moment-EV dominance. Specific premarket cells have higher per-moment alpha density.
- **Category F (data layer):** F31 (OI partially tracked, see commit 9c93505 amendment), F32 (distortion events — Cat 9 found zero at ε=0.01, framing needs amendment), F33 (depth chain genuinely missing — true G13 collection gap), F34 (formation gate reconstructable).
- **Category C (process):** C28 streaming, C29 grep-c brittleness, C30 schema-probe-depth (commit 9c93505).
- **Category D (memory/context):** D14 handoff doc discipline, D15 chat-side draft drift.

### ROADMAP.md
- **T32a CLOSED** (Layer C spec). **T32b/T32c PENDING** — these are now reframed under Simons-mode as the forensic replay framework. The original "Layer C v1 producer" framing is superseded.
- **T33** (OI producer, commit 9c93505 amended) — much smaller now (~20-30 min compute via candle direct read).
- **T34** (formation gate producer) and **T35** (per-tier adaptive gate) — still pending; informed by Cat 8 finding (30-40% of markets fall outside uniform 4hr gate).
- **G13** (orderbook-snapshot collection) — blocked-track until forensic replay shows it's necessary.

### ANALYSIS_LIBRARY.md
- Section 4 (anchor evidence) is pending entries from the Session 9 diagnostic chain (commit 631e653). Top alpha cells (Cat 5), distortion absence (Cat 9), B24 distribution (Cat 10), bilateral feasibility (Cat 6) all become canonical anchor evidence.

### Diagnostic chain outputs
- Commit 631e653 — Session 9 chain run, all 9 cats OK. The six load-bearing findings in that commit message are the empirical foundation under this document.

### Trading infrastructure (current state of bot)
- **Active bot:** `live_v3.py` (binary version), config `deploy_v4_paper.json` (strategy version), running paper mode since Apr 29. PID 1905767. **Paper mode means real signals, no real fills.**
- **Strategy version "deploy_v4"** is the Mona Lisa config from Mar 13 (STB module + maker-to-maker module). Currently observation-mode pending validation.
- **VPS:** `ssh root@104.131.191.95`, working dir `~/Omi-Workspace/arb-executor`.

---

## Section 9 — Posture for the New Chat

The new chat (or whoever inherits this document) should:

1. **Read this document fully before doing any analytical work.** Take it as load-bearing.
2. **Read LESSONS.md, ROADMAP.md, ANALYSIS_LIBRARY.md, TAXONOMY.md** for empirical context. Read the Session 9 diagnostic chain outputs in `data/durable/diagnostics_session_8/` for the latest analytical findings.
3. **Be willing to web-search.** When something needs sharpening — Kalshi venue specifics, retail participation data, Renaissance methodology, prediction market microstructure literature — search. Don't rely on training data for a venue this specific.
4. **Probe before assuming.** Per LESSONS C30. Schema, semantics, population reliability, per-tier coverage all need empirical verification, not assumption.
5. **One CC prompt per turn.** Per LESSONS C1.
6. **Web-fetch every commit URL.** Per LESSONS C2.
7. **Single-concern commits.** Per LESSONS D9.
8. **Stay in Simons-mode.** Most candidate strategies fail. Concentration on verified edge is the discipline. Documentation is post-hoc cleanup, not the work itself.
9. **Push back on Druid when needed.** The collaboration works because the operator pushes back when Claude over-accepts CC's framing or presents unnecessary options. Do the same in reverse — push back on operator framings that drift from this document's discipline. Both directions of friction make the analysis better.
10. **Adapt without abandoning.** When the data surprises us, update the empirical foundation. When that requires updating this document, do it explicitly with a clear amendment. But the philosophical core (Simons-mode discipline, market structure axioms, Problem 1 priority) is durable and should survive specific tactical findings.

---

## Section 10 — What This Document Does NOT Specify

Deliberate omissions for the new chat to fill in via empirical work + web search:

- **Sizing.** How much capital per cell. Not specified here — needs to be derived from forensic replay's verified edge size and the operator's risk tolerance.
- **Kill-switches.** When to abandon a previously-working cell. Needs detection logic for regime change.
- **Position-level risk management.** How many concurrent positions, correlation between paired-event positions, etc. Standard portfolio risk treatment, but applied to this specific structure.
- **Specific top cells to target first.** Cat 5 named ATP_CHALL × in_match × 60-70 / tight / high / limit_c=30 / time_stop_240 as the highest simulated EV. This needs forensic-replay validation before becoming a "target this cell" instruction.
- **Counterparty behavior models.** What specific retail behaviors create the harvestable patterns. Hypothesized (favorite-set-loss overreaction, premarket emotional positioning) but not yet measured.

These are open research questions for the new chat's first weeks of work. Not gaps in the philosophy — the philosophy says "find them empirically, don't assume them."

---

## Document Maintenance

This document is amended when its empirical foundations or strategic implications materially change. Amendments preserve the original text for audit trail (AMENDMENT [DATE] sections), per LESSONS F31's pattern.

**Amendments append to a CHANGELOG at the bottom.**

---

## CHANGELOG

- 2026-05-06 ET (Session 9): SIMONS_MODE.md created. Establishes operating philosophy + market structure axioms + alpha thesis + Problem 1/Problem 2 distinction + forensic replay framework as first deliverable + rollback discipline + cross-references. Created concurrent with Session 9 diagnostic chain completion (commit 631e653) and F31 amendment (commit 9c93505). Counts at creation: LESSONS B=24, C=30, D=17, E=31, F=34, G=21.
