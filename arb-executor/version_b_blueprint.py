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

    # === ATP_MAIN ===
    ('ATP_MAIN', 'underdog', 10, 14): None,
    ('ATP_MAIN', 'underdog', 15, 19): {
        # STEP6 20260415: DISABLE — NEG EV -14.5% ROI n=10
        'entry_lo': 15,
        'entry_hi': 19,
        'dca_drop': 15,
        'exit_target': 20,
        'entry_size': 0,
        'dca_size': 0,
        'mode': 'underdog',
        'in_sample_ev_80_40': 11.4,
        'in_sample_n': 64,
        'in_sample_hit_rate': 0.64,
        'in_sample_daily_pnl': 7.37,
    },
    ('ATP_MAIN', 'underdog', 20, 24): {
        # STEP6: +31c/B off-1 n=11
        'entry_lo': 22,
        'entry_hi': 24,
        'dca_drop': 12,
        'exit_target': 31,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'underdog',
        'maker_bid_offset': -1,
        'in_sample_ev_80_40': 6.33,
        'in_sample_n': 56,
        'in_sample_hit_rate': 0.55,
        'in_sample_daily_pnl': 3.58,
    },
    ('ATP_MAIN', 'underdog', 25, 29): {
        # STEP6: +21c/B off+1 n=14
        'entry_lo': 26,
        'entry_hi': 28,
        'dca_drop': 24,
        'exit_target': 21,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'underdog',
        'maker_bid_offset': 1,
        'in_sample_ev_80_40': 9.66,
        'in_sample_n': 71,
        'in_sample_hit_rate': 0.7,
        'in_sample_daily_pnl': 6.93,
    },
    ('ATP_MAIN', 'underdog', 30, 34): {
        # STEP6: hold99 dca1 off-1 n=22
        'entry_lo': 31,
        'entry_hi': 33,
        'dca_drop': 1,
        'exit_target': None,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'underdog',
        'maker_bid_offset': -1,
        'in_sample_ev_80_40': 7.21,
        'in_sample_n': 75,
        'in_sample_hit_rate': 0.56,
        'in_sample_daily_pnl': 5.46,
    },
    ('ATP_MAIN', 'underdog', 35, 39): {
        # STEP6: re-enable +24c/A off-1 n=31
        'entry_lo': 37,
        'entry_hi': 39,
        'dca_drop': 1,
        'exit_target': 24,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'underdog',
        'maker_bid_offset': -1,
        'in_sample_ev_80_40': 12.5,
        'in_sample_n': 87,
        'in_sample_hit_rate': 0.66,
        'in_sample_daily_pnl': 10.98,
    },
    ('ATP_MAIN', 'underdog', 40, 44): {
        # STEP6 20260415: DISABLE — NEG EV borderline n=28
        'entry_lo': 40,
        'entry_hi': 42,
        'dca_drop': 30,
        'exit_target': 30,
        'entry_size': 0,
        'dca_size': 0,
        'mode': 'underdog',
        'in_sample_ev_80_40': 8.12,
        'in_sample_n': 102,
        'in_sample_hit_rate': 0.62,
        'in_sample_daily_pnl': 8.36,
    },
    ('ATP_MAIN', 'leader', 55, 59): {
        # STEP6: finite +10c off+1 n=26
        'entry_lo': 55,
        'entry_hi': 57,
        'dca_drop': 1,
        'exit_target': 10,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'leader',
        'maker_bid_offset': 1,
        'in_sample_ev_80_40': 11.57,
        'in_sample_n': 88,
        'in_sample_hit_rate': 0.92,
        'in_sample_daily_pnl': 10.29,
    },
    ('ATP_MAIN', 'leader', 60, 64): {
        # STEP6: +23c/B n=37
        'entry_lo': 60,
        'entry_hi': 64,
        'dca_drop': 10,
        'exit_target': 23,
        'entry_size': 80,
        'dca_size': 40,
        'mode': 'leader',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 6.4,
        'in_sample_n': 161,
        'in_sample_hit_rate': 0.88,
        'in_sample_daily_pnl': 10.41,
    },
    ('ATP_MAIN', 'leader', 65, 69): {
        # STEP6: tight +4c scalp off+2 n=27
        'entry_lo': 66,
        'entry_hi': 68,
        'dca_drop': 12,
        'exit_target': 4,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'leader',
        'maker_bid_offset': 2,
        'in_sample_ev_80_40': 8.96,
        'in_sample_n': 71,
        'in_sample_hit_rate': 0.76,
        'in_sample_daily_pnl': 6.43,
    },
    ('ATP_MAIN', 'leader', 70, 74): {
        # STEP6: +19c/A off-1 n=17
        'entry_lo': 70,
        'entry_hi': 72,
        'dca_drop': 14,
        'exit_target': 19,
        'entry_size': 80,
        'dca_size': 40,
        'mode': 'leader',
        'maker_bid_offset': -1,
        'in_sample_ev_80_40': 4.52,
        'in_sample_n': 102,
        'in_sample_hit_rate': 0.75,
        'in_sample_daily_pnl': 4.65,
    },
    ('ATP_MAIN', 'leader', 75, 79): {
        # STEP6: +12c/B off+1 n=11
        'entry_lo': 75,
        'entry_hi': 77,
        'dca_drop': 35,
        'exit_target': 12,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'leader',
        'maker_bid_offset': 1,
        'in_sample_ev_80_40': 7.49,
        'in_sample_n': 74,
        'in_sample_hit_rate': 0.88,
        'in_sample_daily_pnl': 5.6,
    },
    ('ATP_MAIN', 'leader', 80, 84): None,
    ('ATP_MAIN', 'leader', 85, 89): None,

    # === ATP_CHALL ===
    ('ATP_CHALL', 'underdog', 10, 14): {
        # STEP6: +21c/B off-1 n=19
        'entry_lo': 11,
        'entry_hi': 13,
        'dca_drop': 5,
        'exit_target': 21,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'underdog',
        'maker_bid_offset': -1,
        'in_sample_ev_80_40': 13.73,
        'in_sample_n': 90,
        'in_sample_hit_rate': 0.51,
        'in_sample_daily_pnl': 12.48,
    },
    ('ATP_CHALL', 'underdog', 15, 19): {
        # STEP6: +18c/B off-1 n=30
        'entry_lo': 17,
        'entry_hi': 19,
        'dca_drop': 8,
        'exit_target': 18,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'underdog',
        'maker_bid_offset': -1,
        'in_sample_ev_80_40': 10.93,
        'in_sample_n': 125,
        'in_sample_hit_rate': 0.83,
        'in_sample_daily_pnl': 13.81,
    },
    ('ATP_CHALL', 'underdog', 20, 24): {
        # STEP6: +27c/B off-1 n=44
        'entry_lo': 22,
        'entry_hi': 24,
        'dca_drop': 5,
        'exit_target': 27,
        'entry_size': 80,
        'dca_size': 40,
        'mode': 'underdog',
        'maker_bid_offset': -1,
        'in_sample_ev_80_40': 8.77,
        'in_sample_n': 154,
        'in_sample_hit_rate': 0.77,
        'in_sample_daily_pnl': 13.64,
    },
    ('ATP_CHALL', 'underdog', 25, 29): {
        # STEP6: re-enable +15c/A n=39
        'entry_lo': 26,
        'entry_hi': 28,
        'dca_drop': 16,
        'exit_target': 15,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'underdog',
        'maker_bid_offset': -1,
        'in_sample_ev_80_40': 10.09,
        'in_sample_n': 181,
        'in_sample_hit_rate': 0.62,
        'in_sample_daily_pnl': 18.44,
    },
    ('ATP_CHALL', 'underdog', 30, 34): {
        # STEP6 20260415: DISABLE — NEG EV -3.4% ROI n=67
        'entry_lo': 31,
        'entry_hi': 33,
        'dca_drop': 30,
        'exit_target': 10,
        'entry_size': 0,
        'dca_size': 0,
        'mode': 'underdog',
        'in_sample_ev_80_40': 9.01,
        'in_sample_n': 224,
        'in_sample_hit_rate': 0.79,
        'in_sample_daily_pnl': 20.4,
    },
    ('ATP_CHALL', 'underdog', 35, 39): {
        # STEP6: dca2/+11/B off0 n=67
        'entry_lo': 37,
        'entry_hi': 39,
        'dca_drop': 2,
        'exit_target': 11,
        'entry_size': 80,
        'dca_size': 40,
        'mode': 'underdog',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 7.87,
        'in_sample_n': 264,
        'in_sample_hit_rate': 0.78,
        'in_sample_daily_pnl': 20.98,
    },
    ('ATP_CHALL', 'underdog', 40, 44): {
        # STEP6: hold99 dca1 off+2 n=65
        'entry_lo': 42,
        'entry_hi': 44,
        'dca_drop': 1,
        'exit_target': None,
        'entry_size': 80,
        'dca_size': 40,
        'mode': 'underdog',
        'maker_bid_offset': 2,
        'in_sample_ev_80_40': 12.79,
        'in_sample_n': 241,
        'in_sample_hit_rate': 0.73,
        'in_sample_daily_pnl': 31.14,
    },
    ('ATP_CHALL', 'leader', 55, 59): {
        # STEP6: finite +21c n=57
        'entry_lo': 57,
        'entry_hi': 59,
        'dca_drop': 11,
        'exit_target': 21,
        'entry_size': 80,
        'dca_size': 40,
        'mode': 'leader',
        'maker_bid_offset': -1,
        'in_sample_ev_80_40': 10.96,
        'in_sample_n': 249,
        'in_sample_hit_rate': 0.85,
        'in_sample_daily_pnl': 27.58,
    },
    ('ATP_CHALL', 'leader', 60, 64): {
        # STEP6: finite +30c/B n=47
        'entry_lo': 60,
        'entry_hi': 62,
        'dca_drop': 15,
        'exit_target': 30,
        'entry_size': 80,
        'dca_size': 40,
        'mode': 'leader',
        'maker_bid_offset': -1,
        'in_sample_ev_80_40': 8.93,
        'in_sample_n': 277,
        'in_sample_hit_rate': 0.77,
        'in_sample_daily_pnl': 24.99,
    },
    ('ATP_CHALL', 'leader', 65, 69): {
        # STEP6: hold99 dca17 n=43
        'entry_lo': 67,
        'entry_hi': 69,
        'dca_drop': 17,
        'exit_target': None,
        'entry_size': 80,
        'dca_size': 40,
        'mode': 'leader',
        'maker_bid_offset': -1,
        'in_sample_ev_80_40': 15.68,
        'in_sample_n': 229,
        'in_sample_hit_rate': 0.83,
        'in_sample_daily_pnl': 36.27,
    },
    ('ATP_CHALL', 'leader', 70, 74): {
        # STEP6: hold99 dca11 off+1 n=38
        'entry_lo': 71,
        'entry_hi': 73,
        'dca_drop': 11,
        'exit_target': None,
        'entry_size': 80,
        'dca_size': 40,
        'mode': 'leader',
        'maker_bid_offset': 1,
        'in_sample_ev_80_40': 9.27,
        'in_sample_n': 194,
        'in_sample_hit_rate': 0.94,
        'in_sample_daily_pnl': 18.17,
    },
    ('ATP_CHALL', 'leader', 75, 79): {
        # STEP6: hold99 dca27 n=34
        'entry_lo': 77,
        'entry_hi': 79,
        'dca_drop': 27,
        'exit_target': None,
        'entry_size': 80,
        'dca_size': 40,
        'mode': 'leader',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 4.7,
        'in_sample_n': 161,
        'in_sample_hit_rate': 0.91,
        'in_sample_daily_pnl': 7.64,
    },
    ('ATP_CHALL', 'leader', 80, 84): {
        # STEP6: hold99 dca14 n=21
        'entry_lo': 80,
        'entry_hi': 82,
        'dca_drop': 14,
        'exit_target': None,
        'entry_size': 80,
        'dca_size': 40,
        'mode': 'leader',
        'maker_bid_offset': -1,
        'in_sample_ev_80_40': 4.35,
        'in_sample_n': 154,
        'in_sample_hit_rate': 0.9,
        'in_sample_daily_pnl': 6.77,
    },
    ('ATP_CHALL', 'leader', 85, 89): None,

    # === WTA_MAIN ===
    ('WTA_MAIN', 'underdog', 10, 14): None,
    ('WTA_MAIN', 'underdog', 15, 19): {
        # STEP6: re-enable +20c/B n=19
        'entry_lo': 15,
        'entry_hi': 19,
        'dca_drop': 5,
        'exit_target': 20,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'underdog',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 5.14,
        'in_sample_n': 61,
        'in_sample_hit_rate': 0.39,
        'in_sample_daily_pnl': 3.17,
    },
    ('WTA_MAIN', 'underdog', 20, 24): {
        # STEP6: hold99 dca14 off-1 n=8
        'entry_lo': 22,
        'entry_hi': 24,
        'dca_drop': 14,
        'exit_target': None,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'underdog',
        'maker_bid_offset': -1,
        'in_sample_ev_80_40': 9.96,
        'in_sample_n': 57,
        'in_sample_hit_rate': 0.65,
        'in_sample_daily_pnl': 5.74,
    },
    ('WTA_MAIN', 'underdog', 25, 29): {
        # STEP6: re-enable +21c/B off-1 n=17
        'entry_lo': 25,
        'entry_hi': 27,
        'dca_drop': 18,
        'exit_target': 21,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'underdog',
        'maker_bid_offset': -1,
        'in_sample_ev_80_40': 11.89,
        'in_sample_n': 62,
        'in_sample_hit_rate': 0.56,
        'in_sample_daily_pnl': 7.45,
    },
    ('WTA_MAIN', 'underdog', 30, 34): {
        # STEP6: re-enable +34c/A n=16
        'entry_lo': 31,
        'entry_hi': 33,
        'dca_drop': 17,
        'exit_target': 34,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'underdog',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 12.94,
        'in_sample_n': 88,
        'in_sample_hit_rate': 0.81,
        'in_sample_daily_pnl': 11.5,
    },
    ('WTA_MAIN', 'underdog', 35, 39): {
        # STEP6: +28c/A off+1 n=14
        'entry_lo': 35,
        'entry_hi': 37,
        'dca_drop': 2,
        'exit_target': 28,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'underdog',
        'maker_bid_offset': 1,
        'in_sample_ev_80_40': 9.96,
        'in_sample_n': 98,
        'in_sample_hit_rate': 0.81,
        'in_sample_daily_pnl': 9.86,
    },
    ('WTA_MAIN', 'underdog', 40, 44): {
        # STEP6: re-enable +33c/A off-1 n=32
        'entry_lo': 40,
        'entry_hi': 44,
        'dca_drop': 5,
        'exit_target': 33,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'underdog',
        'maker_bid_offset': -1,
        'in_sample_ev_80_40': 8.7,
        'in_sample_n': 148,
        'in_sample_hit_rate': 0.62,
        'in_sample_daily_pnl': 13.01,
    },
    ('WTA_MAIN', 'leader', 55, 59): {
        # STEP6: +7c/B n=24
        'entry_lo': 55,
        'entry_hi': 57,
        'dca_drop': 34,
        'exit_target': 7,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'leader',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 9.09,
        'in_sample_n': 94,
        'in_sample_hit_rate': 0.74,
        'in_sample_daily_pnl': 8.63,
    },
    ('WTA_MAIN', 'leader', 60, 64): {
        # STEP6: +31c/A n=12
        'entry_lo': 62,
        'entry_hi': 64,
        'dca_drop': 15,
        'exit_target': 31,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'leader',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 11.14,
        'in_sample_n': 80,
        'in_sample_hit_rate': 0.82,
        'in_sample_daily_pnl': 9.01,
    },
    ('WTA_MAIN', 'leader', 65, 69): {
        # STEP6: hold99 dca10 off-1 n=15
        'entry_lo': 66,
        'entry_hi': 68,
        'dca_drop': 10,
        'exit_target': None,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'leader',
        'maker_bid_offset': -1,
        'in_sample_ev_80_40': 6.89,
        'in_sample_n': 81,
        'in_sample_hit_rate': 0.72,
        'in_sample_daily_pnl': 5.64,
    },
    ('WTA_MAIN', 'leader', 70, 74): {
        # STEP6: hold99 dca27 off-1 n=12
        'entry_lo': 70,
        'entry_hi': 72,
        'dca_drop': 27,
        'exit_target': None,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'leader',
        'maker_bid_offset': -1,
        'in_sample_ev_80_40': 4.16,
        'in_sample_n': 81,
        'in_sample_hit_rate': 0.86,
        'in_sample_daily_pnl': 3.4,
    },
    ('WTA_MAIN', 'leader', 75, 79): {
        # STEP6: hold99 dca2 off+2 n=13
        'entry_lo': 76,
        'entry_hi': 78,
        'dca_drop': 2,
        'exit_target': None,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'leader',
        'maker_bid_offset': 2,
        'in_sample_ev_80_40': 3.1,
        'in_sample_n': 82,
        'in_sample_hit_rate': 0.79,
        'in_sample_daily_pnl': 2.57,
    },
    ('WTA_MAIN', 'leader', 80, 84): {
        # STEP6: hold99 keep n=7
        'entry_lo': 81,
        'entry_hi': 83,
        'dca_drop': 35,
        'exit_target': None,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'leader',
        'maker_bid_offset': 0,
        'in_sample_ev_80_40': 5.66,
        'in_sample_n': 56,
        'in_sample_hit_rate': 0.89,
        'in_sample_daily_pnl': 3.2,
    },
    ('WTA_MAIN', 'leader', 85, 89): {
        # STEP6: hold99 dca1 off-1 n=6
        'entry_lo': 85,
        'entry_hi': 87,
        'dca_drop': 1,
        'exit_target': None,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'leader',
        'maker_bid_offset': -1,
        'in_sample_ev_80_40': 4.31,
        'in_sample_n': 52,
        'in_sample_hit_rate': 0.9,
        'in_sample_daily_pnl': 2.26,
    },

    # === WTA_CHALL ===
    ('WTA_CHALL', 'underdog', 10, 14): None,
    ('WTA_CHALL', 'underdog', 15, 19): None,
    ('WTA_CHALL', 'underdog', 20, 24): None,
    ('WTA_CHALL', 'underdog', 25, 29): None,
    ('WTA_CHALL', 'underdog', 30, 34): None,
    ('WTA_CHALL', 'underdog', 35, 39): {
        # STEP6: hold99 dca15 off-1 n=6
        'entry_lo': 35,
        'entry_hi': 39,
        'dca_drop': 15,
        'exit_target': None,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'underdog',
        'maker_bid_offset': -1,
        'in_sample_ev_80_40': 10.97,
        'in_sample_n': 63,
        'in_sample_hit_rate': 0.73,
        'in_sample_daily_pnl': 6.98,
    },
    ('WTA_CHALL', 'underdog', 40, 44): {
        # STEP6: hold99 dca1 off-1 n=16
        'entry_lo': 40,
        'entry_hi': 44,
        'dca_drop': 1,
        'exit_target': None,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'underdog',
        'maker_bid_offset': -1,
        'in_sample_ev_80_40': 3.73,
        'in_sample_n': 62,
        'in_sample_hit_rate': 0.45,
        'in_sample_daily_pnl': 2.34,
    },
    ('WTA_CHALL', 'leader', 55, 59): None,
    ('WTA_CHALL', 'leader', 60, 64): {
        # STEP6: +15c/B off-1 n=4
        'entry_lo': 60,
        'entry_hi': 62,
        'dca_drop': 15,
        'exit_target': 15,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'leader',
        'maker_bid_offset': -1,
        'in_sample_ev_80_40': 1.97,
        'in_sample_n': 53,
        'in_sample_hit_rate': 0.77,
        'in_sample_daily_pnl': 1.05,
    },
    ('WTA_CHALL', 'leader', 65, 69): None,
    ('WTA_CHALL', 'leader', 70, 74): None,
    ('WTA_CHALL', 'leader', 75, 79): None,
    ('WTA_CHALL', 'leader', 80, 84): None,
    ('WTA_CHALL', 'leader', 85, 89): {
        # STEP6: hold99 dca25 off+1 n=2
        'entry_lo': 85,
        'entry_hi': 89,
        'dca_drop': 25,
        'exit_target': None,
        'entry_size': 40,
        'dca_size': 20,
        'mode': 'leader',
        'maker_bid_offset': 1,
        'in_sample_ev_80_40': 3.31,
        'in_sample_n': 56,
        'in_sample_hit_rate': 0.91,
        'in_sample_daily_pnl': 1.87,
    },
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
    ('ATP_CHALL', 'leader', 55, 59): False,
    ('ATP_CHALL', 'leader', 60, 64): True,
    ('ATP_CHALL', 'leader', 65, 69): False,
    ('ATP_CHALL', 'leader', 70, 74): False,
    ('ATP_CHALL', 'leader', 75, 79): False,
    ('ATP_CHALL', 'leader', 80, 84): False,
    ('ATP_CHALL', 'underdog', 10, 14): True,
    ('ATP_CHALL', 'underdog', 15, 19): True,
    ('ATP_CHALL', 'underdog', 20, 24): True,
    ('ATP_CHALL', 'underdog', 25, 29): False,
    ('ATP_CHALL', 'underdog', 30, 34): True,
    ('ATP_CHALL', 'underdog', 35, 39): True,
    ('ATP_CHALL', 'underdog', 40, 44): False,
    ('ATP_MAIN', 'leader', 55, 59): False,
    ('ATP_MAIN', 'leader', 60, 64): True,
    ('ATP_MAIN', 'leader', 65, 69): False,
    ('ATP_MAIN', 'leader', 70, 74): False,
    ('ATP_MAIN', 'leader', 75, 79): True,
    ('ATP_MAIN', 'underdog', 15, 19): False,
    ('ATP_MAIN', 'underdog', 20, 24): True,
    ('ATP_MAIN', 'underdog', 25, 29): True,
    ('ATP_MAIN', 'underdog', 30, 34): False,
    ('ATP_MAIN', 'underdog', 35, 39): False,
    ('ATP_MAIN', 'underdog', 40, 44): False,
    ('WTA_CHALL', 'leader', 60, 64): True,
    ('WTA_CHALL', 'leader', 85, 89): False,
    ('WTA_CHALL', 'underdog', 35, 39): False,
    ('WTA_CHALL', 'underdog', 40, 44): False,
    ('WTA_MAIN', 'leader', 55, 59): True,
    ('WTA_MAIN', 'leader', 60, 64): False,
    ('WTA_MAIN', 'leader', 65, 69): False,
    ('WTA_MAIN', 'leader', 70, 74): False,
    ('WTA_MAIN', 'leader', 75, 79): False,
    ('WTA_MAIN', 'leader', 80, 84): False,
    ('WTA_MAIN', 'leader', 85, 89): False,
    ('WTA_MAIN', 'underdog', 15, 19): True,
    ('WTA_MAIN', 'underdog', 20, 24): False,
    ('WTA_MAIN', 'underdog', 25, 29): True,
    ('WTA_MAIN', 'underdog', 30, 34): False,
    ('WTA_MAIN', 'underdog', 35, 39): False,
    ('WTA_MAIN', 'underdog', 40, 44): False,
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
