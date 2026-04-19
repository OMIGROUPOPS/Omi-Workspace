"""VERSION B Final Deployment Blueprint
==========================================
Generated: 2026-04-10
Source: 5,889 events from Kalshi API tapes Jan 2 - Apr 10, 2026
Status: BLUEPRINT — not yet deployed (Phase 3 work)
Currently deployed: Option A (4 doubled leader cells, $63.70/day)
Target: $430/day in-sample, ~$258/day OOS-adjusted (×0.6)

DEPLOYMENT format per entry:
  ('CATEGORY', 'side', tier_lo, tier_hi): {
      'entry_lo':   <int>,           # buy when entry price >= this
      'entry_hi':   <int>,           # buy when entry price <= this
      'dca_drop':   <int|None>,      # DCA fires at entry - drop (None = no DCA)
      'exit_target':<int|None>,      # auto-sell at entry + target (None = hold to settle)
      'entry_size': <int>,           # contracts on initial entry
      'dca_size':   <int>,           # contracts on DCA fill (0 if no DCA)
      'mode':       <str>,           # 'leader' or 'underdog' direction
      'in_sample_ev_80_40': <float>, # in-sample EV per trade at 80/40 sizing
      'in_sample_n':       <int>,    # historical sample size
      'in_sample_hit_rate':<float>,  # hit rate (auto-sell trigger or settle win)
      'in_sample_daily_pnl':<float>, # estimated daily P&L contribution at the listed sizing
  }

41 active cells across 28 match-pairs:
  18 DUAL pairs        — both leader and underdog cells fire
   2 LEADER ONLY pairs — only leader cell viable
   3 UNDERDOG ONLY     — only underdog cell viable
   5 SKIP pairs        — neither side viable

Engineering features required to deploy this dict:
  1. AUTO-SELL at +X profit (38 of 41 cells use it — biggest unlock, build first)
  2. UNDERDOG betting logic (21 of 41 cells are underdog bets)
  3. Per-cell DCA drop (currently global 15c)
  4. Per-cell entry sub-range (currently 5c tiers, need 3c sub-ranges)
  5. Per-cell sizing (80/40 for 14 strong cells, 40/20 for 27 standard cells)
"""

DEPLOYMENT = {
    # ============================================================
    # ATP MAIN DRAW — 5 DUAL + 1 UNDERDOG_ONLY + 1 SKIP
    # subtotal: $80.06/day
    # ============================================================

    # Pair 1: Leader 55-59c | Underdog 40-44c — DUAL
    ('ATP_MAIN', 'leader', 55, 59): {
        # CHANGED 20260415 per Step 3+4 analysis: SWAP — -17.7% -> +4.7% ROI, n=44
        'entry_lo': 55, 'entry_hi': 57,
        'dca_drop': 5, 'exit_target': None,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 11.57, 'in_sample_n': 88,
        'in_sample_hit_rate': 0.92, 'in_sample_daily_pnl': 10.29,
    },
    ('ATP_MAIN', 'underdog', 40, 44): {
        # CHANGED 20260415 per Step 3+4 analysis: DISABLE — best ROI -15.0%, n=43
        'entry_lo': 40, 'entry_hi': 42,
        'dca_drop': 30, 'exit_target': 30,
        'entry_size': 0, 'dca_size': 0,
        'mode': 'underdog',
        'in_sample_ev_80_40': 8.12, 'in_sample_n': 102,
        'in_sample_hit_rate': 0.62, 'in_sample_daily_pnl': 8.36,
    },

    # Pair 2: Leader 60-64c | Underdog 35-39c — DUAL
    ('ATP_MAIN', 'leader', 60, 64): {
        'entry_lo': 60, 'entry_hi': 64,
        'dca_drop': 30, 'exit_target': 10,
        'entry_size': 80, 'dca_size': 40,
        'mode': 'leader',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 6.40, 'in_sample_n': 161,
        'in_sample_hit_rate': 0.88, 'in_sample_daily_pnl': 10.41,
    },
    ('ATP_MAIN', 'underdog', 35, 39): {
        # CHANGED 20260415 per Step 3+4 analysis: DISABLE — best ROI -1.2%, n=42
        'entry_lo': 37, 'entry_hi': 39,
        'dca_drop': 25, 'exit_target': 30,
        'entry_size': 0, 'dca_size': 0,
        'mode': 'underdog',
        'in_sample_ev_80_40': 12.50, 'in_sample_n': 87,
        'in_sample_hit_rate': 0.66, 'in_sample_daily_pnl': 10.98,
    },

    # Pair 3: Leader 65-69c | Underdog 30-34c — DUAL
    ('ATP_MAIN', 'leader', 65, 69): {
        'entry_lo': 66, 'entry_hi': 68,
        'dca_drop': 10, 'exit_target': None,  # hold to settle
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 8.96, 'in_sample_n': 71,
        'in_sample_hit_rate': 0.76, 'in_sample_daily_pnl': 6.43,
    },
    ('ATP_MAIN', 'underdog', 30, 34): {
        # CHANGED 20260415 per Step 3+4 analysis: SWAP — -10.1% -> +21.9% ROI, n=33
        'entry_lo': 31, 'entry_hi': 33,
        'dca_drop': 5, 'exit_target': None,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'underdog',
        'maker_bid_offset': -3,
        'in_sample_ev_80_40': 7.21, 'in_sample_n': 75,
        'in_sample_hit_rate': 0.56, 'in_sample_daily_pnl': 5.46,
    },

    # Pair 4: Leader 70-74c | Underdog 25-29c — DUAL
    ('ATP_MAIN', 'leader', 70, 74): {
        'entry_lo': 70, 'entry_hi': 72,
        'dca_drop': 20, 'exit_target': None,  # hold to settle
        'entry_size': 80, 'dca_size': 40,
        'mode': 'leader',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 4.52, 'in_sample_n': 102,
        'in_sample_hit_rate': 0.75, 'in_sample_daily_pnl': 4.65,
    },
    ('ATP_MAIN', 'underdog', 25, 29): {
        # CHANGED 20260415 per Step 3+4 analysis: DISABLE — best ROI -17.0%, n=22
        'entry_lo': 26, 'entry_hi': 28,
        'dca_drop': 25, 'exit_target': 15,
        'entry_size': 0, 'dca_size': 0,
        'mode': 'underdog',
        'in_sample_ev_80_40': 9.66, 'in_sample_n': 71,
        'in_sample_hit_rate': 0.70, 'in_sample_daily_pnl': 6.93,
    },

    # Pair 5: Leader 75-79c | Underdog 20-24c — DUAL
    ('ATP_MAIN', 'leader', 75, 79): {
        'entry_lo': 75, 'entry_hi': 77,
        'dca_drop': 30, 'exit_target': 15,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 7.49, 'in_sample_n': 74,
        'in_sample_hit_rate': 0.88, 'in_sample_daily_pnl': 5.60,
    },
    ('ATP_MAIN', 'underdog', 20, 24): {
        'entry_lo': 22, 'entry_hi': 24,
        'dca_drop': 20, 'exit_target': 20,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'underdog',
        'maker_bid_offset': -4,
        'in_sample_ev_80_40': 6.33, 'in_sample_n': 56,
        'in_sample_hit_rate': 0.55, 'in_sample_daily_pnl': 3.58,
    },

    # Pair 6: Leader 80-84c | Underdog 15-19c — UNDERDOG ONLY
    ('ATP_MAIN', 'leader', 80, 84): None,  # SKIP
    ('ATP_MAIN', 'underdog', 15, 19): {
        # CHANGED 20260415 per Step 3+4 analysis: DISABLE — best ROI -45.1%, n=22
        'entry_lo': 15, 'entry_hi': 19,
        'dca_drop': 15, 'exit_target': 20,
        'entry_size': 0, 'dca_size': 0,
        'mode': 'underdog',
        'in_sample_ev_80_40': 11.40, 'in_sample_n': 64,
        'in_sample_hit_rate': 0.64, 'in_sample_daily_pnl': 7.37,
    },

    # Pair 7: Leader 85-89c | Underdog 10-14c — SKIP
    ('ATP_MAIN', 'leader', 85, 89): None,
    ('ATP_MAIN', 'underdog', 10, 14): None,

    # ============================================================
    # ATP CHALLENGER — 6 DUAL + 1 UNDERDOG_ONLY (the workhorse, 59% of revenue)
    # subtotal: $252.30/day
    # ============================================================

    # Pair 1: Leader 55-59c | Underdog 40-44c — DUAL
    ('ATP_CHALL', 'leader', 55, 59): {
        # CHANGED 20260415 per Step 3+4 analysis: SWAP — -11.9% -> +5.7% ROI, n=101
        'entry_lo': 57, 'entry_hi': 59,
        'dca_drop': 5, 'exit_target': None,
        'entry_size': 80, 'dca_size': 40,
        'mode': 'leader',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 10.96, 'in_sample_n': 249,
        'in_sample_hit_rate': 0.85, 'in_sample_daily_pnl': 27.58,
    },
    ('ATP_CHALL', 'underdog', 40, 44): {
        # CHANGED 20260415 per Step 3+4 analysis: SWAP — -7.6% -> +20.9% ROI, n=88
        'entry_lo': 42, 'entry_hi': 44,
        'dca_drop': None, 'exit_target': None,
        'entry_size': 80, 'dca_size': 40,
        'mode': 'underdog',
        'maker_bid_offset': -1,
        'in_sample_ev_80_40': 12.79, 'in_sample_n': 241,
        'in_sample_hit_rate': 0.73, 'in_sample_daily_pnl': 31.14,
    },

    # Pair 2: Leader 60-64c | Underdog 35-39c — DUAL
    ('ATP_CHALL', 'leader', 60, 64): {
        # CHANGED 20260415 per Step 3+4 analysis: SWAP — -9.6% -> +1.4% ROI, n=79
        'entry_lo': 60, 'entry_hi': 62,
        'dca_drop': 20, 'exit_target': None,
        'entry_size': 80, 'dca_size': 40,
        'mode': 'leader',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 8.93, 'in_sample_n': 277,
        'in_sample_hit_rate': 0.77, 'in_sample_daily_pnl': 24.99,
    },
    ('ATP_CHALL', 'underdog', 35, 39): {
        # CHANGED 20260415 per Step 3+4 analysis: SWAP — -43% -> +1.4% ROI, n=95
        'entry_lo': 37, 'entry_hi': 39,
        'dca_drop': None, 'exit_target': 10,
        'entry_size': 80, 'dca_size': 40,
        'mode': 'underdog',
        'maker_bid_offset': -2,
        'in_sample_ev_80_40': 7.87, 'in_sample_n': 264,
        'in_sample_hit_rate': 0.78, 'in_sample_daily_pnl': 20.98,
    },

    # Pair 3: Leader 65-69c | Underdog 30-34c — DUAL  ★ #1 cell in dataset
    ('ATP_CHALL', 'leader', 65, 69): {
        # CHANGED 20260415 per Step 3+4 analysis: SWAP — +1.3% -> +4.5% ROI, n=79
        'entry_lo': 67, 'entry_hi': 69,
        'dca_drop': None, 'exit_target': None,
        'entry_size': 80, 'dca_size': 40,
        'mode': 'leader',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 15.68, 'in_sample_n': 229,
        'in_sample_hit_rate': 0.83, 'in_sample_daily_pnl': 36.27,
    },
    ('ATP_CHALL', 'underdog', 30, 34): {
        # CHANGED 20260415 per Step 3+4 analysis: DISABLE — best ROI -7.0%, n=81, live 0% WR
        'entry_lo': 31, 'entry_hi': 33,
        'dca_drop': 30, 'exit_target': 10,
        'entry_size': 0, 'dca_size': 0,
        'mode': 'underdog',
        'in_sample_ev_80_40': 9.01, 'in_sample_n': 224,
        'in_sample_hit_rate': 0.79, 'in_sample_daily_pnl': 20.40,
    },

    # Pair 4: Leader 70-74c | Underdog 25-29c — DUAL
    ('ATP_CHALL', 'leader', 70, 74): {
        # CHANGED 20260415 per Step 3+4 analysis: SWAP — -4.8% -> +16.1% ROI, n=65
        'entry_lo': 71, 'entry_hi': 73,
        'dca_drop': 10, 'exit_target': None,
        'entry_size': 80, 'dca_size': 40,
        'mode': 'leader',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 9.27, 'in_sample_n': 194,
        'in_sample_hit_rate': 0.94, 'in_sample_daily_pnl': 18.17,
    },
    ('ATP_CHALL', 'underdog', 25, 29): {
        # CHANGED 20260415 per Step 3+4 analysis: DISABLE — best ROI -8.3%, n=55
        'entry_lo': 26, 'entry_hi': 28,
        'dca_drop': 25, 'exit_target': 20,
        'entry_size': 0, 'dca_size': 0,
        'mode': 'underdog',
        'in_sample_ev_80_40': 10.09, 'in_sample_n': 181,
        'in_sample_hit_rate': 0.62, 'in_sample_daily_pnl': 18.44,
    },

    # Pair 5: Leader 75-79c | Underdog 20-24c — DUAL
    ('ATP_CHALL', 'leader', 75, 79): {
        # CHANGED 20260415 per Step 3+4 analysis: SWAP — -3.5% -> +3.6% ROI, n=52
        'entry_lo': 77, 'entry_hi': 79,
        'dca_drop': 10, 'exit_target': 22,
        'entry_size': 80, 'dca_size': 40,
        'mode': 'leader',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 4.70, 'in_sample_n': 161,
        'in_sample_hit_rate': 0.91, 'in_sample_daily_pnl': 7.64,
    },
    ('ATP_CHALL', 'underdog', 20, 24): {
        # CHANGED 20260415 per Step 3+4 analysis: SWAP — -51.7% -> +13.3% ROI, n=59
        'entry_lo': 22, 'entry_hi': 24,
        'dca_drop': None, 'exit_target': 10,
        'entry_size': 80, 'dca_size': 40,
        'mode': 'underdog',
        'maker_bid_offset': -4,
        'in_sample_ev_80_40': 8.77, 'in_sample_n': 154,
        'in_sample_hit_rate': 0.77, 'in_sample_daily_pnl': 13.64,
    },

    # Pair 6: Leader 80-84c | Underdog 15-19c — DUAL
    ('ATP_CHALL', 'leader', 80, 84): {
        # CHANGED 20260415 per Step 3+4 analysis: SWAP — +3.6% -> +15.6% ROI, n=36
        'entry_lo': 80, 'entry_hi': 82,
        'dca_drop': 15, 'exit_target': 25,
        'entry_size': 80, 'dca_size': 40,
        'mode': 'leader',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 4.35, 'in_sample_n': 154,
        'in_sample_hit_rate': 0.90, 'in_sample_daily_pnl': 6.77,
    },
    ('ATP_CHALL', 'underdog', 15, 19): {
        # CHANGED 20260415 per Step 3+4 analysis: DISABLE — best ROI -15.8%, n=51
        'entry_lo': 17, 'entry_hi': 19,
        'dca_drop': 15, 'exit_target': 10,
        'entry_size': 0, 'dca_size': 0,
        'mode': 'underdog',
        'in_sample_ev_80_40': 10.93, 'in_sample_n': 125,
        'in_sample_hit_rate': 0.83, 'in_sample_daily_pnl': 13.81,
    },

    # Pair 7: Leader 85-89c | Underdog 10-14c — UNDERDOG ONLY
    ('ATP_CHALL', 'leader', 85, 89): None,  # SKIP
    ('ATP_CHALL', 'underdog', 10, 14): {
        # CHANGED 20260415 per Step 3+4 analysis: SWAP — -48.4% -> +24.0% ROI, n=33
        'entry_lo': 11, 'entry_hi': 13,
        'dca_drop': None, 'exit_target': 30,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'underdog',
        'maker_bid_offset': -5,
        'in_sample_ev_80_40': 13.73, 'in_sample_n': 90,
        'in_sample_hit_rate': 0.51, 'in_sample_daily_pnl': 12.48,
    },

    # ============================================================
    # WTA MAIN DRAW — 6 DUAL + 1 LEADER_ONLY
    # subtotal: $85.43/day
    # ============================================================

    # Pair 1: Leader 55-59c | Underdog 40-44c — DUAL
    ('WTA_MAIN', 'leader', 55, 59): {
        # CHANGED 20260415 per Step 3+4 analysis: DISABLE — best ROI -5.3%, n=36
        'entry_lo': 55, 'entry_hi': 57,
        'dca_drop': 30, 'exit_target': 25,
        'entry_size': 0, 'dca_size': 0,
        'mode': 'leader',
        'in_sample_ev_80_40': 9.09, 'in_sample_n': 94,
        'in_sample_hit_rate': 0.74, 'in_sample_daily_pnl': 8.63,
    },
    ('WTA_MAIN', 'underdog', 40, 44): {
        # CHANGED 20260415 per Step 3+4 analysis: DISABLE — best ROI -5.8%, n=51
        'entry_lo': 40, 'entry_hi': 44,
        'dca_drop': 30, 'exit_target': 30,
        'entry_size': 0, 'dca_size': 0,
        'mode': 'underdog',
        'in_sample_ev_80_40': 8.70, 'in_sample_n': 148,
        'in_sample_hit_rate': 0.62, 'in_sample_daily_pnl': 13.01,
    },

    # Pair 2: Leader 60-64c | Underdog 35-39c — DUAL
    ('WTA_MAIN', 'leader', 60, 64): {
        # CHANGED 20260415 per Step 3+4 analysis: SWAP — -11.3% -> +6.5% ROI, n=30
        'entry_lo': 62, 'entry_hi': 64,
        'dca_drop': None, 'exit_target': 18,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 11.14, 'in_sample_n': 80,
        'in_sample_hit_rate': 0.82, 'in_sample_daily_pnl': 9.01,
    },
    ('WTA_MAIN', 'underdog', 35, 39): {
        # CHANGED 20260415 per Step 3+4 analysis: SWAP — -50.1% -> +12.2% ROI, n=25
        'entry_lo': 35, 'entry_hi': 37,
        'dca_drop': None, 'exit_target': 25,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'underdog',
        'maker_bid_offset': -2,
        'in_sample_ev_80_40': 9.96, 'in_sample_n': 98,
        'in_sample_hit_rate': 0.81, 'in_sample_daily_pnl': 9.86,
    },

    # Pair 3: Leader 65-69c | Underdog 30-34c — DUAL
    ('WTA_MAIN', 'leader', 65, 69): {
        'entry_lo': 66, 'entry_hi': 68,
        'dca_drop': 20, 'exit_target': None,  # hold to settle
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 6.89, 'in_sample_n': 81,
        'in_sample_hit_rate': 0.72, 'in_sample_daily_pnl': 5.64,
    },
    ('WTA_MAIN', 'underdog', 30, 34): {
        # CHANGED 20260415 per Step 3+4 analysis: DISABLE — best ROI -7.5%, n=25
        'entry_lo': 31, 'entry_hi': 33,
        'dca_drop': 30, 'exit_target': 15,
        'entry_size': 0, 'dca_size': 0,
        'mode': 'underdog',
        'in_sample_ev_80_40': 12.94, 'in_sample_n': 88,
        'in_sample_hit_rate': 0.81, 'in_sample_daily_pnl': 11.50,
    },

    # Pair 4: Leader 70-74c | Underdog 25-29c — DUAL
    ('WTA_MAIN', 'leader', 70, 74): {
        # CHANGED 20260415 per Step 3+4 analysis: SWAP — -3.4% -> +13.8% ROI, n=32
        'entry_lo': 70, 'entry_hi': 72,
        'dca_drop': 20, 'exit_target': None,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 4.16, 'in_sample_n': 81,
        'in_sample_hit_rate': 0.86, 'in_sample_daily_pnl': 3.40,
    },
    ('WTA_MAIN', 'underdog', 25, 29): {
        # CHANGED 20260415 per Step 3+4 analysis: DISABLE — best ROI -1.5%, n=29
        'entry_lo': 25, 'entry_hi': 27,
        'dca_drop': 20, 'exit_target': 30,
        'entry_size': 0, 'dca_size': 0,
        'mode': 'underdog',
        'in_sample_ev_80_40': 11.89, 'in_sample_n': 62,
        'in_sample_hit_rate': 0.56, 'in_sample_daily_pnl': 7.45,
    },

    # Pair 5: Leader 75-79c | Underdog 20-24c — DUAL
    ('WTA_MAIN', 'leader', 75, 79): {
        'entry_lo': 76, 'entry_hi': 78,
        'dca_drop': 30, 'exit_target': 20,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 3.10, 'in_sample_n': 82,
        'in_sample_hit_rate': 0.79, 'in_sample_daily_pnl': 2.57,
    },
    ('WTA_MAIN', 'underdog', 20, 24): {
        'entry_lo': 22, 'entry_hi': 24,
        'dca_drop': 20, 'exit_target': 20,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'underdog',
        'maker_bid_offset': -4,
        'in_sample_ev_80_40': 9.96, 'in_sample_n': 57,
        'in_sample_hit_rate': 0.65, 'in_sample_daily_pnl': 5.74,
    },

    # Pair 6: Leader 80-84c | Underdog 15-19c — DUAL
    ('WTA_MAIN', 'leader', 80, 84): {
        'entry_lo': 81, 'entry_hi': 83,
        'dca_drop': 30, 'exit_target': 10,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 5.66, 'in_sample_n': 56,
        'in_sample_hit_rate': 0.89, 'in_sample_daily_pnl': 3.20,
    },
    ('WTA_MAIN', 'underdog', 15, 19): {
        # CHANGED 20260415 per Step 3+4 analysis: DISABLE — best ROI -25.6%, n=30
        'entry_lo': 15, 'entry_hi': 19,
        'dca_drop': 10, 'exit_target': 30,
        'entry_size': 0, 'dca_size': 0,
        'mode': 'underdog',
        'in_sample_ev_80_40': 5.14, 'in_sample_n': 61,
        'in_sample_hit_rate': 0.39, 'in_sample_daily_pnl': 3.17,
    },

    # Pair 7: Leader 85-89c | Underdog 10-14c — LEADER ONLY
    ('WTA_MAIN', 'leader', 85, 89): {
        'entry_lo': 85, 'entry_hi': 87,
        'dca_drop': 30, 'exit_target': 10,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 4.31, 'in_sample_n': 52,
        'in_sample_hit_rate': 0.90, 'in_sample_daily_pnl': 2.26,
    },
    ('WTA_MAIN', 'underdog', 10, 14): None,  # SKIP

    # ============================================================
    # WTA CHALLENGER — sparse coverage (smallest dataset)
    # subtotal: $12.25/day
    # ============================================================

    # Pair 1: Leader 55-59c | Underdog 40-44c — UNDERDOG ONLY
    ('WTA_CHALL', 'leader', 55, 59): None,  # SKIP
    ('WTA_CHALL', 'underdog', 40, 44): {
        'entry_lo': 40, 'entry_hi': 44,
        'dca_drop': 15, 'exit_target': None,  # hold to settle
        'entry_size': 40, 'dca_size': 20,
        'mode': 'underdog',
        'maker_bid_offset': -1,
        'in_sample_ev_80_40': 3.73, 'in_sample_n': 62,
        'in_sample_hit_rate': 0.45, 'in_sample_daily_pnl': 2.34,
    },

    # Pair 2: Leader 60-64c | Underdog 35-39c — DUAL
    ('WTA_CHALL', 'leader', 60, 64): {
        'entry_lo': 60, 'entry_hi': 62,
        'dca_drop': 30, 'exit_target': 15,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 1.97, 'in_sample_n': 53,
        'in_sample_hit_rate': 0.77, 'in_sample_daily_pnl': 1.05,
    },
    ('WTA_CHALL', 'underdog', 35, 39): {
        'entry_lo': 35, 'entry_hi': 39,
        'dca_drop': 30, 'exit_target': 20,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'underdog',
        'maker_bid_offset': -2,
        'in_sample_ev_80_40': 10.97, 'in_sample_n': 63,
        'in_sample_hit_rate': 0.73, 'in_sample_daily_pnl': 6.98,
    },

    # Pairs 3-6: ALL SKIP (insufficient sample)
    ('WTA_CHALL', 'leader',   65, 69): None,
    ('WTA_CHALL', 'underdog', 30, 34): None,
    ('WTA_CHALL', 'leader',   70, 74): None,
    ('WTA_CHALL', 'underdog', 25, 29): None,
    ('WTA_CHALL', 'leader',   75, 79): None,
    ('WTA_CHALL', 'underdog', 20, 24): None,
    ('WTA_CHALL', 'leader',   80, 84): None,
    ('WTA_CHALL', 'underdog', 15, 19): None,

    # Pair 7: Leader 85-89c | Underdog 10-14c — LEADER ONLY
    ('WTA_CHALL', 'leader', 85, 89): {
        'entry_lo': 85, 'entry_hi': 89,
        'dca_drop': 30, 'exit_target': 10,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 3.31, 'in_sample_n': 56,
        'in_sample_hit_rate': 0.91, 'in_sample_daily_pnl': 1.87,
    },
    ('WTA_CHALL', 'underdog', 10, 14): None,  # SKIP
}


def active_cells():
    """Return only the active (non-None) cell configurations."""
    return {k: v for k, v in DEPLOYMENT.items() if v is not None}


def get_strategy(category, side, entry_price):
    """Lookup the strategy for a given category, side, and observed entry price.

    Returns the strategy dict if there's a viable cell that matches, else None.
    Caller is responsible for checking entry_lo <= entry_price <= entry_hi.
    """
    # Find the tier this entry price falls into
    if side == 'leader':
        tiers = [(55, 59), (60, 64), (65, 69), (70, 74), (75, 79), (80, 84), (85, 89)]
    else:
        tiers = [(10, 14), (15, 19), (20, 24), (25, 29), (30, 34), (35, 39), (40, 44)]
    for lo, hi in tiers:
        if lo <= entry_price <= hi:
            cell = DEPLOYMENT.get((category, side, lo, hi))
            if cell is None:
                return None
            # Apply the entry sub-range filter
            if cell['entry_lo'] <= entry_price <= cell['entry_hi']:
                return cell
            return None
    return None


# ---------------------------------------------------------------------------
# STRATEGY B (blended-target auto-sell) per-cell flag
#
# When DCA fires, recompute the auto-sell target against the BLENDED AVERAGE
# cost basis instead of the original entry price. A per-cell simulation showed
# Strategy B adds +$48.46/day in-sample on the 19 cells flagged True below,
# while the 18 cells flagged False (mostly cheap underdogs + hold-to-settle)
# prefer the original first-fill target.
#
# Grid evaluated in auto_sell_strategy_compare.py on 5,838 events (Jan-Apr).
# Cells not present in this dict default to False (first-fill target, safe).
#
# Format: (category, direction, tier_lo, tier_hi) -> bool
# ---------------------------------------------------------------------------
USE_BLENDED_TARGET = {
    # ===== ATP MAIN DRAW =====
    ('ATP_MAIN',  'leader',   55, 59): False,  # A wins (+5.14 vs B +4.76)
    ('ATP_MAIN',  'leader',   60, 64): True,   # B wins (+16.07 vs A +10.53, +5.54/day)
    ('ATP_MAIN',  'leader',   65, 69): False,  # hold-to-99c, flag irrelevant
    ('ATP_MAIN',  'leader',   70, 74): False,  # hold-to-99c, flag irrelevant
    ('ATP_MAIN',  'leader',   75, 79): False,  # A wins narrowly (C actually top, skip)
    ('ATP_MAIN',  'underdog', 15, 19): False,  # A wins (+3.69 vs B +3.01)
    ('ATP_MAIN',  'underdog', 20, 24): False,  # A wins (+1.79 vs B +1.73)
    ('ATP_MAIN',  'underdog', 25, 29): True,   # B wins (+4.03 vs A +3.46)
    ('ATP_MAIN',  'underdog', 30, 34): False,  # A wins narrowly (C actually top, skip)
    ('ATP_MAIN',  'underdog', 35, 39): True,   # B wins (+6.03 vs A +5.59)
    ('ATP_MAIN',  'underdog', 40, 44): False,  # A wins narrowly (C actually top, skip)

    # ===== ATP CHALLENGER =====
    ('ATP_CHALL', 'leader',   55, 59): False,   # B wins (+32.86 vs A +27.58, +5.28/day)
    ('ATP_CHALL', 'leader',   60, 64): False,   # B wins (+30.64 vs A +25.14, +5.50/day) - was C-top but use B
    ('ATP_CHALL', 'leader',   65, 69): False,   # B wins narrowly (+37.35 vs A +36.48, +0.87/day)
    ('ATP_CHALL', 'leader',   70, 74): False,   # B wins (+19.12 vs A +18.17, +0.95/day)
    ('ATP_CHALL', 'leader',   75, 79): True,   # B wins BIG (+15.73 vs A +7.64, +8.09/day) ★
    ('ATP_CHALL', 'leader',   80, 84): True,   # B wins BIG (+15.43 vs A +6.77, +8.66/day) ★
    ('ATP_CHALL', 'underdog', 10, 14): False,  # A wins (+6.25 vs B +5.82)
    ('ATP_CHALL', 'underdog', 15, 19): False,  # A wins (+13.81 vs B +10.84)
    ('ATP_CHALL', 'underdog', 20, 24): False,  # A wins (+13.64 vs B +12.38)
    ('ATP_CHALL', 'underdog', 25, 29): False,  # A wins narrowly (C actually top, skip)
    ('ATP_CHALL', 'underdog', 30, 34): True,   # B wins (+24.42 vs A +20.41, +4.01/day)
    ('ATP_CHALL', 'underdog', 35, 39): False,   # B wins BIG (+28.63 vs A +21.01, +7.62/day) ★
    ('ATP_CHALL', 'underdog', 40, 44): False,  # A wins narrowly (C actually top, skip)

    # ===== WTA MAIN DRAW =====
    ('WTA_MAIN',  'leader',   55, 59): True,   # B wins (+5.80 vs A +4.48, +1.32/day)
    ('WTA_MAIN',  'leader',   60, 64): False,   # B wins (+5.20 vs A +4.57, +0.63/day)
    ('WTA_MAIN',  'leader',   65, 69): False,  # hold-to-99c, flag irrelevant
    ('WTA_MAIN',  'leader',   70, 74): False,   # B wins (+4.22 vs A +1.70, +2.52/day) ★
    ('WTA_MAIN',  'leader',   75, 79): False,  # A wins narrowly (C actually top, skip)
    ('WTA_MAIN',  'leader',   80, 84): True,   # B wins (+2.54 vs A +1.71, +0.83/day)
    ('WTA_MAIN',  'leader',   85, 89): True,   # B wins (+2.59 vs A +1.13, +1.46/day)
    ('WTA_MAIN',  'underdog', 15, 19): False,  # A wins (+1.58 vs B +1.20)
    ('WTA_MAIN',  'underdog', 20, 24): False,  # A wins narrowly (C actually top, skip)
    ('WTA_MAIN',  'underdog', 25, 29): False,  # A wins narrowly (C actually top, skip)
    ('WTA_MAIN',  'underdog', 30, 34): False,  # A wins (+5.76 vs B +5.29)
    ('WTA_MAIN',  'underdog', 35, 39): False,  # A wins (+4.98 vs B +4.71)
    ('WTA_MAIN',  'underdog', 40, 44): False,  # A wins (+13.16 vs B +11.33)

    # ===== WTA CHALLENGER =====
    ('WTA_CHALL', 'leader',   60, 64): True,   # B wins (+1.76 vs A +0.53, +1.23/day) - C slightly higher, use B
    ('WTA_CHALL', 'leader',   85, 89): True,   # B wins (+2.67 vs A +0.94, +1.73/day) ★
    ('WTA_CHALL', 'underdog', 35, 39): True,   # B wins (+4.25 vs A +3.49, +0.76/day)
    ('WTA_CHALL', 'underdog', 40, 44): False,  # hold-to-99c, flag irrelevant
}


def use_blended_target(category, direction, tier_lo, tier_hi):
    """Return True if this cell should recompute its auto-sell target against
    the blended average after DCA fires. Defaults to False for unknown cells."""
    return USE_BLENDED_TARGET.get((category, direction, tier_lo, tier_hi), False)


# Quick reference: cells that need each engineering feature
CELLS_USING_AUTOSELL = sorted(
    [k for k, v in DEPLOYMENT.items() if v and v['exit_target'] is not None]
)
CELLS_USING_HOLD = sorted(
    [k for k, v in DEPLOYMENT.items() if v and v['exit_target'] is None]
)
CELLS_USING_UNDERDOG = sorted(
    [k for k, v in DEPLOYMENT.items() if v and v['mode'] == 'underdog']
)
CELLS_AT_8040 = sorted(
    [k for k, v in DEPLOYMENT.items() if v and v['entry_size'] == 80]
)
CELLS_AT_4020 = sorted(
    [k for k, v in DEPLOYMENT.items() if v and v['entry_size'] == 40]
)


if __name__ == '__main__':
    # Self-check / summary on import
    active = active_cells()
    total_daily = sum(v['in_sample_daily_pnl'] for v in active.values())
    print('VERSION B Blueprint loaded')
    print('  Active cells:                 {}'.format(len(active)))
    print('  Cells using auto-sell:        {} (build first — biggest unlock)'.format(
        len(CELLS_USING_AUTOSELL)))
    print('  Cells using hold-to-settle:   {}'.format(len(CELLS_USING_HOLD)))
    print('  Underdog cells:               {} (need direction-agnostic refactor)'.format(
        len(CELLS_USING_UNDERDOG)))
    print('  80/40 sized cells:            {}'.format(len(CELLS_AT_8040)))
    print('  40/20 sized cells:            {}'.format(len(CELLS_AT_4020)))
    print('  In-sample daily P&L:          ${:.2f}/day'.format(total_daily))
    print('  OOS-adjusted (×0.6):          ${:.2f}/day'.format(total_daily * 0.6))
