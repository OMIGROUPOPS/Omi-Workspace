"""VERSION C Deployment Blueprint — v3 OWN-TAPE EXIT FLOOR (CORRECTED FOUNDATION)
========================================================================
Generated: 2026-05-29 from the corrected Foundation tapes.

REPLACES version_b_blueprint.py, which was built on the BROKEN foundation
(size_qual contamination + own-N false negatives + breakeven formula over
tape). vs v3 truth the old blueprint was wrong on 40/41 exit_targets, held
12 cells that should exit early, and skipped 12 profitable cells.

SCOPE: conservative EXIT FLOOR for LIVE capital.
  - VIABILITY GATE = OWN-TAPE realized EV>0. The pooled surface is for
    MAPPING/understanding; for live money the binding floor is what each
    band's own tapes actually did. Pooling can enrich but NEVER flips an
    own-tape-negative band into a trade (caught 15 such cells).
  - exit_target = OWN-TAPE argmax X (or None = hold to settle if holding
    beats every early exit).
  - maker_bid_offset = 0 (TAKER entry at the anchor). Part 2 entry discount
    layers on top and only LOOSENS exit requirements / lifts EV.

Each cell carries own_ev/own_hit/own_n (binding) + pooled_band_ev/pooled_hit
(context). Drop-in: same band structure as LEADER_TIERS_V5/UNDERDOG_TIERS_V5.
"""

DEPLOYMENT = {

    # ========================================================
    # ATP_MAIN
    # ========================================================
    ('ATP_MAIN', 'leader', 55, 59): {  # TRADE own_ev=3.006 own_n=318 own_hit=0.6384
        'entry_lo': 55, 'entry_hi': 57,
        'dca_drop': 5, 'exit_target': 37,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': 3.006, 'own_hit': 0.6384, 'own_n': 318,
        'in_sample_daily_pnl': 3.006,
        'pooled_band_ev': 5.264, 'pooled_hit': 0.7611,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_MAIN', 'leader', 60, 64): {  # TRADE own_ev=2.176 own_n=335 own_hit=0.6627
        'entry_lo': 60, 'entry_hi': 64,
        'dca_drop': 30, 'exit_target': 34,
        'entry_size': 80, 'dca_size': 40,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': 2.176, 'own_hit': 0.6627, 'own_n': 335,
        'in_sample_daily_pnl': 2.176,
        'pooled_band_ev': 5.123, 'pooled_hit': 0.7453,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_MAIN', 'leader', 65, 69): {  # TRADE own_ev=0.107 own_n=307 own_hit=0.987
        'entry_lo': 66, 'entry_hi': 68,
        'dca_drop': 10, 'exit_target': 1,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': 0.107, 'own_hit': 0.987, 'own_n': 307,
        'in_sample_daily_pnl': 0.107,
        'pooled_band_ev': 2.875, 'pooled_hit': 0.8923,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_MAIN', 'leader', 70, 74): {  # TRADE own_ev=1.449 own_n=272 own_hit=0.9926
        'entry_lo': 70, 'entry_hi': 72,
        'dca_drop': 20, 'exit_target': 2,
        'entry_size': 80, 'dca_size': 40,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': 1.449, 'own_hit': 0.9926, 'own_n': 272,
        'in_sample_daily_pnl': 1.449,
        'pooled_band_ev': 2.862, 'pooled_hit': 0.9305,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_MAIN', 'leader', 75, 79): {  # TRADE own_ev=2.45 own_n=238 own_hit=0.8824
        'entry_lo': 75, 'entry_hi': 77,
        'dca_drop': 30, 'exit_target': 13,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': 2.45, 'own_hit': 0.8824, 'own_n': 238,
        'in_sample_daily_pnl': 2.45,
        'pooled_band_ev': 4.059, 'pooled_hit': 0.9496,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_MAIN', 'leader', 80, 84): {  # SKIP  own_ev=-0.224 own_n=205 own_hit=0.9854
        'entry_lo': 80, 'entry_hi': 84,
        'dca_drop': None, 'exit_target': None,
        'entry_size': 0, 'dca_size': 0,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': -0.224, 'own_hit': 0.9854, 'own_n': 205,
        'in_sample_daily_pnl': -0.224,
        'pooled_band_ev': 1.832, 'pooled_hit': 0.9599,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_MAIN', 'leader', 85, 89): {  # TRADE own_ev=3.887 own_n=141 own_hit=0.773
        'entry_lo': 85, 'entry_hi': 89,
        'dca_drop': None, 'exit_target': 11,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': 3.887, 'own_hit': 0.773, 'own_n': 141,
        'in_sample_daily_pnl': 3.887,
        'pooled_band_ev': 5.511, 'pooled_hit': 0.9574,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_MAIN', 'underdog', 10, 14): {  # TRADE own_ev=2.791 own_n=129 own_hit=0.4574
        'entry_lo': 10, 'entry_hi': 14,
        'dca_drop': None, 'exit_target': 20,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 2.791, 'own_hit': 0.4574, 'own_n': 129,
        'in_sample_daily_pnl': 2.791,
        'pooled_band_ev': 6.973, 'pooled_hit': 0.4337,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_MAIN', 'underdog', 15, 19): {  # TRADE own_ev=4.643 own_n=171 own_hit=0.3041
        'entry_lo': 15, 'entry_hi': 19,
        'dca_drop': 15, 'exit_target': 54,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 4.643, 'own_hit': 0.3041, 'own_n': 171,
        'in_sample_daily_pnl': 4.643,
        'pooled_band_ev': 8.223, 'pooled_hit': 0.3313,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_MAIN', 'underdog', 20, 24): {  # TRADE own_ev=5.412 own_n=177 own_hit=0.435
        'entry_lo': 22, 'entry_hi': 24,
        'dca_drop': 20, 'exit_target': 41,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 5.412, 'own_hit': 0.435, 'own_n': 177,
        'in_sample_daily_pnl': 5.412,
        'pooled_band_ev': 9.373, 'pooled_hit': 0.5509,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_MAIN', 'underdog', 25, 29): {  # TRADE own_ev=4.18 own_n=239 own_hit=0.6109
        'entry_lo': 26, 'entry_hi': 28,
        'dca_drop': 25, 'exit_target': 24,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 4.18, 'own_hit': 0.6109, 'own_n': 239,
        'in_sample_daily_pnl': 4.18,
        'pooled_band_ev': 7.146, 'pooled_hit': 0.4812,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_MAIN', 'underdog', 30, 34): {  # TRADE own_ev=3.198 own_n=253 own_hit=0.5613
        'entry_lo': 31, 'entry_hi': 33,
        'dca_drop': 5, 'exit_target': 30,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 3.198, 'own_hit': 0.5613, 'own_n': 253,
        'in_sample_daily_pnl': 3.198,
        'pooled_band_ev': 5.348, 'pooled_hit': 0.6744,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_MAIN', 'underdog', 35, 39): {  # TRADE own_ev=0.952 own_n=315 own_hit=0.5714
        'entry_lo': 37, 'entry_hi': 39,
        'dca_drop': 25, 'exit_target': 29,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 0.952, 'own_hit': 0.5714, 'own_n': 315,
        'in_sample_daily_pnl': 0.952,
        'pooled_band_ev': 4.145, 'pooled_hit': 0.6183,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_MAIN', 'underdog', 40, 44): {  # TRADE own_ev=1.939 own_n=296 own_hit=0.6182
        'entry_lo': 40, 'entry_hi': 42,
        'dca_drop': 30, 'exit_target': 29,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 1.939, 'own_hit': 0.6182, 'own_n': 296,
        'in_sample_daily_pnl': 1.939,
        'pooled_band_ev': 4.557, 'pooled_hit': 0.7128,
        'source': 'v3_own_tape_floor_2026-05-29',
    },

    # ========================================================
    # ATP_CHALL
    # ========================================================
    ('ATP_CHALL', 'leader', 55, 59): {  # TRADE own_ev=3.818 own_n=369 own_hit=0.8943
        'entry_lo': 57, 'entry_hi': 59,
        'dca_drop': 5, 'exit_target': 11,
        'entry_size': 80, 'dca_size': 40,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': 3.818, 'own_hit': 0.8943, 'own_n': 369,
        'in_sample_daily_pnl': 3.818,
        'pooled_band_ev': 4.504, 'pooled_hit': 0.8591,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_CHALL', 'leader', 60, 64): {  # TRADE own_ev=0.891 own_n=403 own_hit=0.8859
        'entry_lo': 60, 'entry_hi': 62,
        'dca_drop': 20, 'exit_target': 9,
        'entry_size': 80, 'dca_size': 40,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': 0.891, 'own_hit': 0.8859, 'own_n': 403,
        'in_sample_daily_pnl': 0.891,
        'pooled_band_ev': 3.746, 'pooled_hit': 0.8894,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_CHALL', 'leader', 65, 69): {  # TRADE own_ev=2.087 own_n=426 own_hit=0.7347
        'entry_lo': 67, 'entry_hi': 69,
        'dca_drop': None, 'exit_target': 27,
        'entry_size': 80, 'dca_size': 0,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': 2.087, 'own_hit': 0.7347, 'own_n': 426,
        'in_sample_daily_pnl': 2.087,
        'pooled_band_ev': 4.988, 'pooled_hit': 0.7512,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_CHALL', 'leader', 70, 74): {  # TRADE own_ev=4.933 own_n=343 own_hit=0.4927
        'entry_lo': 71, 'entry_hi': 73,
        'dca_drop': 10, 'exit_target': 27,
        'entry_size': 80, 'dca_size': 40,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': 4.933, 'own_hit': 0.4927, 'own_n': 343,
        'in_sample_daily_pnl': 4.933,
        'pooled_band_ev': 7.407, 'pooled_hit': 0.7014,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_CHALL', 'leader', 75, 79): {  # TRADE own_ev=2.854 own_n=288 own_hit=0.691
        'entry_lo': 77, 'entry_hi': 79,
        'dca_drop': 10, 'exit_target': 21,
        'entry_size': 80, 'dca_size': 40,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': 2.854, 'own_hit': 0.691, 'own_n': 288,
        'in_sample_daily_pnl': 2.854,
        'pooled_band_ev': 6.284, 'pooled_hit': 0.803,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_CHALL', 'leader', 80, 84): {  # SKIP  own_ev=-0.46 own_n=237 own_hit=0.9705
        'entry_lo': 80, 'entry_hi': 82,
        'dca_drop': 15, 'exit_target': None,
        'entry_size': 0, 'dca_size': 0,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': -0.46, 'own_hit': 0.9705, 'own_n': 237,
        'in_sample_daily_pnl': -0.46,
        'pooled_band_ev': 0.996, 'pooled_hit': 0.9568,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_CHALL', 'leader', 85, 89): {  # SKIP  own_ev=-2.54 own_n=248 own_hit=0.9597
        'entry_lo': 85, 'entry_hi': 89,
        'dca_drop': None, 'exit_target': None,
        'entry_size': 0, 'dca_size': 0,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': -2.54, 'own_hit': 0.9597, 'own_n': 248,
        'in_sample_daily_pnl': -2.54,
        'pooled_band_ev': -1.359, 'pooled_hit': None,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_CHALL', 'underdog', 10, 14): {  # TRADE own_ev=8.128 own_n=234 own_hit=0.3248
        'entry_lo': 11, 'entry_hi': 13,
        'dca_drop': None, 'exit_target': 50,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 8.128, 'own_hit': 0.3248, 'own_n': 234,
        'in_sample_daily_pnl': 8.128,
        'pooled_band_ev': 10.422, 'pooled_hit': 0.3284,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_CHALL', 'underdog', 15, 19): {  # TRADE own_ev=9.263 own_n=251 own_hit=0.4382
        'entry_lo': 17, 'entry_hi': 19,
        'dca_drop': 15, 'exit_target': 43,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 9.263, 'own_hit': 0.4382, 'own_n': 251,
        'in_sample_daily_pnl': 9.263,
        'pooled_band_ev': 10.87, 'pooled_hit': 0.4268,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_CHALL', 'underdog', 20, 24): {  # TRADE own_ev=4.992 own_n=250 own_hit=0.616
        'entry_lo': 22, 'entry_hi': 24,
        'dca_drop': None, 'exit_target': 22,
        'entry_size': 80, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 4.992, 'own_hit': 0.616, 'own_n': 250,
        'in_sample_daily_pnl': 4.992,
        'pooled_band_ev': 8.009, 'pooled_hit': 0.5462,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_CHALL', 'underdog', 25, 29): {  # TRADE own_ev=3.301 own_n=256 own_hit=0.5938
        'entry_lo': 26, 'entry_hi': 28,
        'dca_drop': 25, 'exit_target': 24,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 3.301, 'own_hit': 0.5938, 'own_n': 256,
        'in_sample_daily_pnl': 3.301,
        'pooled_band_ev': 6.629, 'pooled_hit': 0.5508,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_CHALL', 'underdog', 30, 34): {  # TRADE own_ev=1.729 own_n=358 own_hit=0.7179
        'entry_lo': 31, 'entry_hi': 33,
        'dca_drop': 30, 'exit_target': 15,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 1.729, 'own_hit': 0.7179, 'own_n': 358,
        'in_sample_daily_pnl': 1.729,
        'pooled_band_ev': 4.075, 'pooled_hit': 0.7709,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_CHALL', 'underdog', 35, 39): {  # TRADE own_ev=2.146 own_n=356 own_hit=0.8511
        'entry_lo': 37, 'entry_hi': 39,
        'dca_drop': None, 'exit_target': 9,
        'entry_size': 80, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 2.146, 'own_hit': 0.8511, 'own_n': 356,
        'in_sample_daily_pnl': 2.146,
        'pooled_band_ev': 3.612, 'pooled_hit': 0.7247,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('ATP_CHALL', 'underdog', 40, 44): {  # TRADE own_ev=5.003 own_n=326 own_hit=0.4939
        'entry_lo': 42, 'entry_hi': 44,
        'dca_drop': None, 'exit_target': 53,
        'entry_size': 80, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 5.003, 'own_hit': 0.4939, 'own_n': 326,
        'in_sample_daily_pnl': 5.003,
        'pooled_band_ev': 7.104, 'pooled_hit': 0.5276,
        'source': 'v3_own_tape_floor_2026-05-29',
    },

    # ========================================================
    # WTA_MAIN
    # ========================================================
    ('WTA_MAIN', 'leader', 55, 59): {  # TRADE own_ev=1.133 own_n=263 own_hit=0.9087
        'entry_lo': 55, 'entry_hi': 57,
        'dca_drop': 30, 'exit_target': 7,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': 1.133, 'own_hit': 0.9087, 'own_n': 263,
        'in_sample_daily_pnl': 1.133,
        'pooled_band_ev': 3.719, 'pooled_hit': 0.8023,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_MAIN', 'leader', 60, 64): {  # TRADE own_ev=5.974 own_n=272 own_hit=0.5184
        'entry_lo': 62, 'entry_hi': 64,
        'dca_drop': None, 'exit_target': 36,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': 5.974, 'own_hit': 0.5184, 'own_n': 272,
        'in_sample_daily_pnl': 5.974,
        'pooled_band_ev': 6.665, 'pooled_hit': 0.6949,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_MAIN', 'leader', 65, 69): {  # TRADE own_ev=0.553 own_n=255 own_hit=0.7765
        'entry_lo': 66, 'entry_hi': 68,
        'dca_drop': 20, 'exit_target': 20,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': 0.553, 'own_hit': 0.7765, 'own_n': 255,
        'in_sample_daily_pnl': 0.553,
        'pooled_band_ev': 3.69, 'pooled_hit': 0.8745,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_MAIN', 'leader', 70, 74): {  # TRADE own_ev=0.641 own_n=234 own_hit=0.765
        'entry_lo': 70, 'entry_hi': 72,
        'dca_drop': 20, 'exit_target': 23,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': 0.641, 'own_hit': 0.765, 'own_n': 234,
        'in_sample_daily_pnl': 0.641,
        'pooled_band_ev': 4.331, 'pooled_hit': 0.8457,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_MAIN', 'leader', 75, 79): {  # TRADE own_ev=0.592 own_n=211 own_hit=0.8863
        'entry_lo': 76, 'entry_hi': 78,
        'dca_drop': 30, 'exit_target': 10,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': 0.592, 'own_hit': 0.8863, 'own_n': 211,
        'in_sample_daily_pnl': 0.592,
        'pooled_band_ev': 3.403, 'pooled_hit': 0.9289,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_MAIN', 'leader', 80, 84): {  # TRADE own_ev=0.38 own_n=158 own_hit=0.9367
        'entry_lo': 81, 'entry_hi': 83,
        'dca_drop': 30, 'exit_target': 6,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': 0.38, 'own_hit': 0.9367, 'own_n': 158,
        'in_sample_daily_pnl': 0.38,
        'pooled_band_ev': 3.385, 'pooled_hit': 0.9278,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_MAIN', 'leader', 85, 89): {  # TRADE own_ev=0.262 own_n=164 own_hit=0.9695
        'entry_lo': 85, 'entry_hi': 87,
        'dca_drop': 30, 'exit_target': 3,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': 0.262, 'own_hit': 0.9695, 'own_n': 164,
        'in_sample_daily_pnl': 0.262,
        'pooled_band_ev': 3.895, 'pooled_hit': 0.9845,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_MAIN', 'underdog', 10, 14): {  # TRADE own_ev=4.606 own_n=142 own_hit=0.2887
        'entry_lo': 10, 'entry_hi': 14,
        'dca_drop': None, 'exit_target': 46,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 4.606, 'own_hit': 0.2887, 'own_n': 142,
        'in_sample_daily_pnl': 4.606,
        'pooled_band_ev': 6.802, 'pooled_hit': 0.6138,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_MAIN', 'underdog', 15, 19): {  # TRADE own_ev=7.245 own_n=151 own_hit=0.2517
        'entry_lo': 15, 'entry_hi': 19,
        'dca_drop': 10, 'exit_target': 79,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 7.245, 'own_hit': 0.2517, 'own_n': 151,
        'in_sample_daily_pnl': 7.245,
        'pooled_band_ev': 9.964, 'pooled_hit': 0.4033,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_MAIN', 'underdog', 20, 24): {  # TRADE own_ev=5.498 own_n=207 own_hit=0.4444
        'entry_lo': 22, 'entry_hi': 24,
        'dca_drop': 20, 'exit_target': 40,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 5.498, 'own_hit': 0.4444, 'own_n': 207,
        'in_sample_daily_pnl': 5.498,
        'pooled_band_ev': 8.152, 'pooled_hit': 0.4825,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_MAIN', 'underdog', 25, 29): {  # TRADE own_ev=7.691 own_n=204 own_hit=0.598
        'entry_lo': 25, 'entry_hi': 27,
        'dca_drop': 20, 'exit_target': 31,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 7.691, 'own_hit': 0.598, 'own_n': 204,
        'in_sample_daily_pnl': 7.691,
        'pooled_band_ev': 10.191, 'pooled_hit': 0.5098,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_MAIN', 'underdog', 30, 34): {  # TRADE own_ev=6.641 own_n=217 own_hit=0.6129
        'entry_lo': 31, 'entry_hi': 33,
        'dca_drop': 30, 'exit_target': 31,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 6.641, 'own_hit': 0.6129, 'own_n': 217,
        'in_sample_daily_pnl': 6.641,
        'pooled_band_ev': 8.963, 'pooled_hit': 0.6037,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_MAIN', 'underdog', 35, 39): {  # TRADE own_ev=2.333 own_n=234 own_hit=0.8846
        'entry_lo': 35, 'entry_hi': 37,
        'dca_drop': None, 'exit_target': 7,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 2.333, 'own_hit': 0.8846, 'own_n': 234,
        'in_sample_daily_pnl': 2.333,
        'pooled_band_ev': 5.658, 'pooled_hit': 0.7179,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_MAIN', 'underdog', 40, 44): {  # TRADE own_ev=1.975 own_n=243 own_hit=0.4527
        'entry_lo': 40, 'entry_hi': 44,
        'dca_drop': 30, 'exit_target': 55,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 1.975, 'own_hit': 0.4527, 'own_n': 243,
        'in_sample_daily_pnl': 1.975,
        'pooled_band_ev': 4.813, 'pooled_hit': 0.5828,
        'source': 'v3_own_tape_floor_2026-05-29',
    },

    # ========================================================
    # WTA_CHALL
    # ========================================================
    ('WTA_CHALL', 'leader', 55, 59): {  # TRADE own_ev=1.746 own_n=59 own_hit=0.7458
        'entry_lo': 55, 'entry_hi': 59,
        'dca_drop': None, 'exit_target': 22,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': 1.746, 'own_hit': 0.7458, 'own_n': 59,
        'in_sample_daily_pnl': 1.746,
        'pooled_band_ev': 10.533, 'pooled_hit': 0.8667,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_CHALL', 'leader', 60, 64): {  # SKIP  own_ev=-0.373 own_n=83 own_hit=0.9639
        'entry_lo': 60, 'entry_hi': 62,
        'dca_drop': 30, 'exit_target': None,
        'entry_size': 0, 'dca_size': 0,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': -0.373, 'own_hit': 0.9639, 'own_n': 83,
        'in_sample_daily_pnl': -0.373,
        'pooled_band_ev': 3.699, 'pooled_hit': 0.9157,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_CHALL', 'leader', 65, 69): {  # SKIP  own_ev=-0.091 own_n=66 own_hit=0.9697
        'entry_lo': 65, 'entry_hi': 69,
        'dca_drop': None, 'exit_target': None,
        'entry_size': 0, 'dca_size': 0,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': -0.091, 'own_hit': 0.9697, 'own_n': 66,
        'in_sample_daily_pnl': -0.091,
        'pooled_band_ev': 8.111, 'pooled_hit': 0.9388,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_CHALL', 'leader', 70, 74): {  # TRADE own_ev=0.635 own_n=52 own_hit=0.9423
        'entry_lo': 70, 'entry_hi': 74,
        'dca_drop': None, 'exit_target': 5,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': 0.635, 'own_hit': 0.9423, 'own_n': 52,
        'in_sample_daily_pnl': 0.635,
        'pooled_band_ev': 5.078, 'pooled_hit': 0.9501,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_CHALL', 'leader', 75, 79): {  # TRADE own_ev=3.846 own_n=52 own_hit=0.6731
        'entry_lo': 75, 'entry_hi': 79,
        'dca_drop': None, 'exit_target': 21,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': 3.846, 'own_hit': 0.6731, 'own_n': 52,
        'in_sample_daily_pnl': 3.846,
        'pooled_band_ev': 6.065, 'pooled_hit': 0.9259,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_CHALL', 'leader', 80, 84): {  # TRADE own_ev=5.667 own_n=30 own_hit=0.9333
        'entry_lo': 80, 'entry_hi': 84,
        'dca_drop': None, 'exit_target': 12,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': 5.667, 'own_hit': 0.9333, 'own_n': 30,
        'in_sample_daily_pnl': 5.667,
        'pooled_band_ev': 10.267, 'pooled_hit': 1.0,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_CHALL', 'leader', 85, 89): {  # TRADE own_ev=2.0 own_n=40 own_hit=1.0
        'entry_lo': 85, 'entry_hi': 89,
        'dca_drop': 30, 'exit_target': 2,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader', 'maker_bid_offset': 0,
        'own_ev': 2.0, 'own_hit': 1.0, 'own_n': 40,
        'in_sample_daily_pnl': 2.0,
        'pooled_band_ev': 8.475, 'pooled_hit': 1.0,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_CHALL', 'underdog', 10, 14): {  # TRADE own_ev=7.41 own_n=39 own_hit=0.2051
        'entry_lo': 10, 'entry_hi': 14,
        'dca_drop': None, 'exit_target': 83,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 7.41, 'own_hit': 0.2051, 'own_n': 39,
        'in_sample_daily_pnl': 7.41,
        'pooled_band_ev': 10.561, 'pooled_hit': 0.2374,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_CHALL', 'underdog', 15, 19): {  # TRADE own_ev=2.107 own_n=28 own_hit=0.6786
        'entry_lo': 15, 'entry_hi': 19,
        'dca_drop': None, 'exit_target': 11,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 2.107, 'own_hit': 0.6786, 'own_n': 28,
        'in_sample_daily_pnl': 2.107,
        'pooled_band_ev': 7.472, 'pooled_hit': 0.7357,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_CHALL', 'underdog', 20, 24): {  # TRADE own_ev=5.894 own_n=47 own_hit=0.4255
        'entry_lo': 20, 'entry_hi': 24,
        'dca_drop': None, 'exit_target': 43,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 5.894, 'own_hit': 0.4255, 'own_n': 47,
        'in_sample_daily_pnl': 5.894,
        'pooled_band_ev': 12.477, 'pooled_hit': 0.6313,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_CHALL', 'underdog', 25, 29): {  # TRADE own_ev=4.98 own_n=49 own_hit=0.3469
        'entry_lo': 25, 'entry_hi': 29,
        'dca_drop': None, 'exit_target': 65,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 4.98, 'own_hit': 0.3469, 'own_n': 49,
        'in_sample_daily_pnl': 4.98,
        'pooled_band_ev': 11.879, 'pooled_hit': 0.6329,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_CHALL', 'underdog', 30, 34): {  # TRADE own_ev=6.745 own_n=55 own_hit=0.4182
        'entry_lo': 30, 'entry_hi': 34,
        'dca_drop': None, 'exit_target': 61,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 6.745, 'own_hit': 0.4182, 'own_n': 55,
        'in_sample_daily_pnl': 6.745,
        'pooled_band_ev': 15.483, 'pooled_hit': 0.608,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_CHALL', 'underdog', 35, 39): {  # TRADE own_ev=5.262 own_n=61 own_hit=0.2623
        'entry_lo': 35, 'entry_hi': 39,
        'dca_drop': 30, 'exit_target': 63,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 5.262, 'own_hit': 0.2623, 'own_n': 61,
        'in_sample_daily_pnl': 5.262,
        'pooled_band_ev': 11.146, 'pooled_hit': 0.615,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
    ('WTA_CHALL', 'underdog', 40, 44): {  # TRADE own_ev=6.059 own_n=51 own_hit=0.5294
        'entry_lo': 40, 'entry_hi': 44,
        'dca_drop': 15, 'exit_target': 49,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'own_ev': 6.059, 'own_hit': 0.5294, 'own_n': 51,
        'in_sample_daily_pnl': 6.059,
        'pooled_band_ev': 9.637, 'pooled_hit': 0.6831,
        'source': 'v3_own_tape_floor_2026-05-29',
    },
}


LEADER_TIERS_V5 = [(55, 59), (60, 64), (65, 69), (70, 74), (75, 79), (80, 84), (85, 89)]
UNDERDOG_TIERS_V5 = [(10, 14), (15, 19), (20, 24), (25, 29), (30, 34), (35, 39), (40, 44)]

def get_strategy(category, side, entry_price):
    """Lookup the strategy cell for (category, side, entry_price).

    Returns the cell dict if a viable cell matches and entry_price is within
    its [entry_lo, entry_hi] sub-range, else None. SKIP cells (entry_size==0)
    are returned as-is; caller checks entry_size. Drop-in for version_b API.
    """
    tiers = LEADER_TIERS_V5 if side == 'leader' else UNDERDOG_TIERS_V5
    for lo, hi in tiers:
        if lo <= entry_price <= hi:
            cell = DEPLOYMENT.get((category, side, lo, hi))
            if cell is None:
                return None
            if cell['entry_lo'] <= entry_price <= cell['entry_hi']:
                return cell
            return None
    return None


def use_blended_target(category, direction, tier_lo, tier_hi):
    """Conservative FLOOR: always first-fill target (False).

    The blended-average auto-sell optimization is an ENTRY-side (Part 2)
    enhancement; the exit floor never assumes it. Defaults False for all cells.
    """
    return False

