# PENDULUM — Phase 2 Context Dump
## For Liam: ESPN Data Requirements + Combined Analysis Plan
### March 8, 2026

---

## SECTION 1: WHAT PENDULUM DOES (Quick Summary)

Pendulum is a binary volatility capture strategy on Kalshi. It buys the FAVORITE side when it dips (leg1), then reactively buys the opposing side when IT crashes during a momentum swing (leg2). If both sides are bought below a combined cost gate (currently 93c), the pair settles at $1.00 guaranteed — profit = 100c - combined cost - fees (~3.5c).

**The edge:** Favorites that dip in live games tend to mean-revert. The completion rate on lopsided favorites is 77-86%. The system captures both sides of the volatility swing.

**The problem we're solving in Phase 2:** The system currently uses ONE config for all sports. But each sport has fundamentally different volatility patterns, comeback dynamics, and blowout profiles. Phase 2 builds sport-specific parameters using real data.

---

## SECTION 2: WHAT WE HAVE (BBO Data)

### What BBO Data Contains
- **Best Bid/Best Ask** on every Kalshi market ticker, every tick (sub-second updates)
- **Ask size / Bid size** — depth at top of book
- **Whale trades** — large taker orders (500+ contracts)
- **Timestamps** — millisecond precision

### What BBO Data Tells Us
- Actual order flow and liquidity on Kalshi
- How fast the market reprices after in-game events (goals, runs, knockouts, aces)
- Fill rates and execution reality (can we actually get filled at the quoted price?)
- Where the smart money is flowing (whale activity, bid/ask imbalances)
- Price impact of large orders
- Spread behavior near game resolution

### What BBO Data Does NOT Tell Us
- **Win probability** — BBO shows prices, not probabilities. A 60c price ≈ 60% implied probability, but Kalshi prices include vig, spread, and market maker positioning
- **Game context** — BBO doesn't know the score, time remaining, who has momentum, injuries, timeouts, etc.
- **WHY a price moved** — just THAT it moved and how fast

### BBO Data Location & Format
```
Files: ~/Omi-Workspace/arb-executor/intra_kalshi/data/
  bbo_log_20260304.csv
  bbo_log_20260305.csv
  bbo_log_20260306.csv
  bbo_log_20260307.csv  (added March 7)
  bbo_log_20260308.csv  (accumulating now)

Format: CSV
Columns: timestamp, ticker, best_bid, best_ask, bid_size, ask_size, last_trade, volume_24h
Rows: ~2-3M per day
```

### BBO Ticker Format
```
KXNBAGAME-26MAR07PHIATL-PHI    → NBA, March 7, Philadelphia at Atlanta, Philadelphia side
KXNHLGAME-26MAR07NSHBUF-BUF    → NHL, March 7, Nashville at Buffalo, Buffalo side
KXNCAAMBGAME-26MAR07FURSAM-SAM → NCAAMB, March 7, Furman at Samford, Samford side
KXWTAMATCH-26MAR07KARNAV-KAR   → WTA Tennis, March 7, Kartal vs Navarro, Kartal side
KXUFCFIGHT-26MAR07TOBNUR-TOB   → UFC, March 7, Tobias vs Nurgozhay, Tobias side
KXMLBSTGAME-26MAR07NYMSTL-NYM  → MLB, March 7, NY Mets at St. Louis, Mets side
```

---

## SECTION 3: WHAT WE NEED FROM ESPN

### Core Data Required
For every game/match/fight that appears on Kalshi during the date range:

1. **Win probability curve over time**
   - ESPN's real-time win probability at every score change / major event
   - Timestamp + win probability for each team
   - This is the "true" probability that Kalshi prices should converge to

2. **Score timeline**
   - Every scoring event with timestamp
   - Running score at each point
   - Period/quarter/half/set markers

3. **Game metadata**
   - Sport, league, teams, date, start time, end time
   - Home/away designation
   - Pre-game odds/spread if available
   - Final result

### Specific Fields Per Sport

**Basketball (NBA, NCAAMB):**
- Score at each basket/free throw with timestamp
- Quarter/half breaks
- Timeout timestamps (momentum breakers)
- Run detection (e.g., "Team A on a 12-0 run")
- Lead changes count and timestamps
- Largest lead for each team

**Hockey (NHL):**
- Goal timestamps with score
- Period breaks
- Power play start/end times
- Shot counts per period
- Empty net situations (6th skater)

**Tennis (ATP, WTA):**
- Point-by-point if available, or game-by-game
- Set scores with timestamps
- Break of serve indicators
- Tiebreak details
- Match format (best of 3 vs best of 5)

**UFC/Fighting:**
- Round timestamps
- Significant strike counts per round if available
- Knockdown events
- Submission attempts
- Judge scorecards if decision

**Baseball (MLB):**
- Run scored per inning with timestamps
- Pitching changes
- Hit/error/walk counts
- Runners in scoring position situations

### Date Range
**Primary: March 4-8, 2026** — This aligns exactly with our BBO data. Same events, same timeframes. This is the critical overlap window.

**Extended (if feasible): February 15 - March 8, 2026** — More data = better models. We have some older BBO data archived and the more ESPN data we can correlate, the stronger the sport-specific profiles.

**Ongoing: March 9+ (daily collection)** — If we can automate ESPN data collection going forward, every day adds to the training set.

### Data Format
Ideally CSV or JSON with these core fields per event:
```
{
  "sport": "nba",
  "date": "2026-03-07",
  "teams": {"home": "ATL", "away": "PHI"},
  "kalshi_event_ticker": "KXNBAGAME-26MAR07PHIATL",  // for joining with BBO
  "start_time": "2026-03-07T19:30:00-05:00",
  "end_time": "2026-03-07T22:15:00-05:00",
  "final_score": {"home": 112, "away": 108},
  "winner": "home",
  "timeline": [
    {
      "timestamp": "2026-03-07T19:35:00",
      "event": "basket",
      "team": "PHI",
      "score": {"home": 0, "away": 3},
      "win_prob_home": 0.48,
      "win_prob_away": 0.52,
      "period": "Q1",
      "game_clock": "11:22"
    },
    ...
  ]
}
```

The critical field for joining is the **kalshi_event_ticker** or enough metadata (sport + date + teams) to match ESPN events to BBO data.

---

## SECTION 4: WHAT WE COMBINE AND WHY

### The Core Question
**"For each sport, what game conditions predict whether a favorite's dip will mean-revert (= profitable Pendulum trade) vs continue into a blowout (= naked loss)?"**

### Join Strategy
```
ESPN timeline (score, win_prob, game_clock)
    ↓ join on timestamp + event
BBO data (Kalshi price, ask/bid, depth, whale trades)
    ↓ produces
Combined dataset per tick:
    - ESPN win probability
    - Kalshi implied probability (from price)
    - Score differential
    - Time remaining
    - Period/quarter
    - Price momentum (Kalshi price change over last N ticks)
    - Depth available
    - Divergence = ESPN_prob - Kalshi_prob (mispricing signal)
```

### Analysis 1: Sport-Specific Volatility Profiles
**Question:** How does price volatility behave per sport over the course of a game?

| Metric | What It Tells Us |
|--------|-----------------|
| Avg price swing per scoring event | How much does a goal/basket/run move the market? |
| Swing decay over game time | Do late-game events move prices more than early? |
| Mean reversion rate after dips | What % of 10c+ dips recover within N minutes? |
| Blowout detection speed | How fast can we tell a dip is a blowout vs noise? |
| Comeback frequency by deficit size | At -15c from entry, what's the comeback rate per sport? |

**Output:** Volatility weight per sport (currently hardcoded: tennis 0.85, mlb 0.9, nhl 0.85, nba 0.8, ncaamb 0.75, fighting 0.7)

### Analysis 2: Optimal Entry Parameters Per Sport
**Question:** What entry cap, gap filter, and stabilization count maximize EV per sport?

Parameters to optimize per sport:
- **MAX_ENTRY_PRICE** — currently 62c global, 60c tennis. Should NHL be 62c? Should NCAAMB be 58c?
- **MAX_THRESHOLD_GAP** — currently 5c global. Should tennis be 3c? Should NHL be 7c?
- **STABILIZATION_TICKS** — currently 3 global. Should UFC be 5? (now killed entirely, but for future reference)
- **COMBINED_COST_MAX (gate)** — currently 93c global. NHL with 16.7% naked rate might handle 95c. Tennis at 40% needs 90c?
- **CLOSENESS_CEILING** — currently 0.50 global. NBA might need 0.40 (more blowout-prone when close).

**Method:** For each sport, run the backtest with the combined dataset varying one parameter at a time. Find the inflection point where EV peaks.

### Analysis 3: Time-Remaining Weighting
**Question:** Should we weight entries differently based on how much game time remains?

**Hypothesis from live trading:**
- Early game dips = noise, high reversion, GOOD entries
- Mid game dips = mixed, moderate reversion
- Late game dips = real (score reflects actual outcome), BAD entries
- Richmond tied 77-77 with 16 seconds left = coin flip = terrible entry

**ESPN provides:** Exact game clock, period, and win probability trajectory
**BBO provides:** When our system entered and at what price

**Combined:** For every entry, we know the game state (score, time remaining, period) AND the outcome (did it complete or blow out). Build a model: entry_quality = f(sport, time_remaining, score_differential, closeness)

### Analysis 4: ESPN Win Prob vs Kalshi Price Divergence
**Question:** When ESPN says 65% but Kalshi says 58%, who's right?

This is the deepest edge. If ESPN's model is more accurate than Kalshi's market price, the divergence IS the mispricing. If Kalshi is dipping below ESPN's fair value, that's a confirmed buyable dip (not a blowout in progress).

**Method:**
1. For every timestamp where we have both ESPN win_prob and Kalshi price
2. Calculate divergence = ESPN_prob - Kalshi_implied_prob
3. Track what happens after large divergences (>5%)
4. If ESPN is right more often → use divergence as an entry signal
5. If Kalshi is right more often → ESPN is lagging and not useful for real-time

### Analysis 5: Blowout Early Warning Signals
**Question:** Can we detect blowouts earlier using ESPN data?

**What a blowout looks like in BBO only:**
- Price drops fast
- No bounce
- One-sided whale activity
- Looks identical to a buyable dip for the first 5-10 seconds

**What a blowout looks like with ESPN context:**
- Score differential exceeding historical comeback threshold
- Win probability below sport-specific recovery zone
- Late game + large deficit = nearly certain loss
- Momentum indicators (runs, power plays, break of serve) all one-directional

**Combined signal:** If ESPN win_prob < 25% AND Kalshi price is still at 40c, don't buy — the market hasn't caught up to reality yet. This could prevent entries like TXAMLSU (entered at 56c, ESPN might have already shown LSU dominating).

---

## SECTION 5: CURRENT SYSTEM PARAMETERS (Reference)

```
SWING_COMBINED_COST_MAX = 93          # leg1 + leg2 must be ≤ 93c
SWING_MAX_CONTRACTS = 32              # max contracts per side
SWING_MAX_ACTIVE_PAIRS = 200          # max events to watch
SWING_MIN_BID = 5                     # minimum bid floor
SWING_MIN_VOLUME = 5000               # $50 volume floor
SWING_MAX_ENTRY_PRICE_DEFAULT = 62    # max leg1 price (non-tennis)
SWING_MAX_ENTRY_PRICE_TENNIS = 60     # max leg1 price (tennis)
SWING_MIN_CASH_FLOOR = 15000          # $150 cash floor
SWING_ENTRY_SCORE_MIN = 0.35          # minimum score for live entries
SWING_PREGAME_SCORE_MIN = 0.60        # higher bar for pregame
SWING_MAX_THRESHOLD_GAP = 5           # max gap below threshold at trigger
SWING_VPIN_MAX = 0.02                 # VPIN toxicity filter
CLOSENESS_CEILING = 0.50              # max closeness (blocks 50/50 games)
FAVORITE_WEAKNESS = crossing_fair > 52c  # only buy favorite side dips
STABILIZATION_TICKS = 3               # consecutive ticks below threshold
RETRY_GUARD = 8c                      # max drift below entry for retries
RETRY_CEILING = entry + 3c            # max price above entry for retries

DISABLED_CATEGORIES = cs2, dota2, valorant, lol, ncaawb, cod, esports, fighting

SPORT_VOLATILITY_WEIGHTS:
  tennis: 0.85, mlb: 0.9, nhl: 0.85, nba: 0.8, ncaamb: 0.75,
  hockey: 0.85, fighting: 0.7 (now disabled), soccer: 0.5, crypto: 0.4, politics: 0.2
```

---

## SECTION 6: BACKTEST RESULTS (Baseline for Comparison)

### Naked Loss Rates by Sport (from 3-day BBO backtest)
```
NHL:     16.7% — safest, best for Pendulum
NBA:     20.0% — good
NCAAMB:  26.9% — moderate, small school blowouts
Tennis:  40.8% — high overall, but ≤60c entry profitable
Esports: 42.1% — killed
Fighting: ~40%+ — killed (confirmed live: TOBNUR -$18)
```

### Closeness Breakdown (Counterintuitive)
```
0.20-0.40 (lopsided): 77.1% completion, 18.1% naked loss — BEST
0.40-0.60:            68.5% completion, 27.4% naked loss
0.60-0.80:            46.9% completion, 49.4% naked loss
0.80-1.00 (50/50):    45.0% completion, 51.7% naked loss — WORST
```

### Key Insight
Lopsided favorites that dip are the sweet spot. 50/50 games are traps. This is what Phase 2 should quantify per sport — what counts as "lopsided" in NBA vs NHL vs tennis?

---

## SECTION 7: LIVE TRADING RESULTS (March 7-8)

### Session Totals
```
Completed pairs:  30+
Paired profit:    ~$65
Naked losses:     ~$52 (TOBNUR UFC, ORLMIN, RICHDUQ, WKU, URI, Minnesota)
DETMIA force exit: -$0.96
Net:              ~+$12 (first full session with iterative fixes)
```

### Post-Fix Entry Quality (entries made after all filters deployed)
```
FGCUCARK: gap=0c, entry=56c, paired at 93c → +$2.24 ✓
VACBOR:   gap=2c, entry=54c, paired at 93c → +$2.24 ✓
WISPUR:   gap=0c, entry=57c, paired at 93c → +$2.24 ✓
INDOSU:   gap=0c, entry=58c, paired at 93c → +$2.24 ✓
KARNAV:   gap=2c, entry=54c, paired at 93c → +$2.24 ✓ (tennis, big swing)
TXAMLSU:  gap=1c, entry=56c, paired at 93c → +$2.24 ✓ (was -60%, came back!)
FURSAM:   gap=0c, entry=54c, paired at 93c → +$2.24 ✓ (was -50%, came back!)
NSHBUF:   gap=5c, entry=52c, paired at 99c → +$0.31 (tight, NHL)
```

---

## SECTION 8: PHASE 2 DELIVERABLES

### What Liam Builds
1. **ESPN data pipeline** — automated collection of win probability, scores, game timelines
2. **Event matching** — map ESPN events to Kalshi tickers (sport + date + teams)
3. **Combined dataset** — ESPN timeline joined with BBO data by timestamp
4. **Sport volatility profiles** — comeback rates, swing sizes, blowout speeds per sport
5. **Parameter optimization report** — recommended config per sport with supporting data

### What We Build (Claude Code)
1. **Sport-specific config loader** — different parameters per sport instead of global
2. **Time-remaining weighting** — entry quality adjusted by game clock
3. **ESPN divergence signal** (if Analysis 4 shows value) — real-time mispricing detection
4. **Blowout early warning** (if Analysis 5 shows value) — exit signal for positions going wrong
5. **Overshoot monitor rewrite** — capture +8c avg overshoot on completed pairs (+$30-40/day projected)

### Success Metrics
- Completion rate > 80% (currently ~75% post-fix)
- Naked loss rate < 15% across all sports (currently ~20% blended)
- Net daily P&L > $100 at 32ct scale
- Ratio of completions to blowouts > 5:1 (currently ~3.5:1)

---

## SECTION 9: PRIORITY ORDER

1. **ESPN data collection for March 4-8** — enables all analysis
2. **Analysis 1: Sport volatility profiles** — quick win, validates/updates sport weights
3. **Analysis 2: Optimal entry parameters** — biggest P&L impact, tunes per-sport config
4. **Analysis 3: Time-remaining weighting** — prevents late-game coin flip entries
5. **Analysis 4: ESPN vs Kalshi divergence** — deepest edge if ESPN is predictive
6. **Analysis 5: Blowout early warning** — hardest to implement, highest potential upside
7. **Overshoot monitor rewrite** — pure engineering, no data dependency

---

*End of context dump. Questions → Druid.*
