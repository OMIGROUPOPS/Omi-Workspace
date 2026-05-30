"""VERSION C Deployment Blueprint - v3 PER-CENT EXIT FLOOR (perfect blend)
========================================================================
Generated 2026-05-29 from the LOCKED ground-truth v3 pooled surfaces.

Every cent is its own cent. exit_target per cent = the v3 pooled-surface
achievable.bestX -- the PERFECT BLEND: per-cent CV decides own-N (where the
cent is credible) vs pooled neighborhood (where own-N is thin/unstable).
Strict own-N alone overfits thin cents; this is the validated balance.

LOOKUP: band keys (cat,dir,lo,hi) are the ENVELOPE; each cell's
percent_exits[cent] holds that cent's own exit_target/ev/hit/basis. The
executor resolves the band then reads the specific entry cent. A band is
SKIP only if EVERY cent in it is non-viable.

maker_bid_offset=0 (taker floor). Part 2 entry discount layers on top.
"""

DEPLOYMENT = {

    # ========================================================
    # ATP_MAIN
    # ========================================================
    ('ATP_MAIN', 'leader', 55, 59): {  # TRADE band_exit=26
        'entry_lo': 55, 'entry_hi': 59,
        'dca_drop': 5, 'exit_target': 26,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            55: {'exit_target': 28, 'ev': 7.25, 'hit': 75.0, 'basis': 'own-N', 'ownN': 48, 'effN': 863.2, 'cvErr': 10.7},
            56: {'exit_target': 33, 'ev': 4.474, 'hit': 67.95, 'basis': 'own-N', 'ownN': 78, 'effN': 685.9, 'cvErr': 2.5},
            57: {'exit_target': 8, 'ev': 0.587, 'hit': 88.6, 'basis': 'pooled', 'ownN': 61, 'effN': 791.4, 'cvErr': 10.0},
            58: {'exit_target': 18, 'ev': 2.8, 'hit': 80.0, 'basis': 'own-N', 'ownN': 65, 'effN': 782.0, 'cvErr': 7.9},
            59: {'exit_target': 40, 'ev': 11.5, 'hit': 71.21, 'basis': 'own-N', 'ownN': 66, 'effN': 789.4, 'cvErr': 50.5},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_MAIN', 'leader', 60, 64): {  # TRADE band_exit=25
        'entry_lo': 60, 'entry_hi': 64,
        'dca_drop': 30, 'exit_target': 25,
        'entry_size': 80, 'dca_size': 40,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            60: {'exit_target': 36, 'ev': 2.11, 'hit': 45.04, 'basis': 'pooled', 'ownN': 57, 'effN': 853.7, 'cvErr': 3.3},
            61: {'exit_target': 34, 'ev': 7.456, 'hit': 72.06, 'basis': 'own-N', 'ownN': 68, 'effN': 796.2, 'cvErr': 13.3},
            62: {'exit_target': 10, 'ev': 5.636, 'hit': 93.94, 'basis': 'own-N', 'ownN': 66, 'effN': 810.0, 'cvErr': 19.0},
            63: {'exit_target': 36, 'ev': 7.521, 'hit': 69.86, 'basis': 'own-N', 'ownN': 73, 'effN': 774.4, 'cvErr': 21.4},
            64: {'exit_target': 12, 'ev': 2.366, 'hit': 87.32, 'basis': 'own-N', 'ownN': 71, 'effN': 779.6, 'cvErr': 1.1},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_MAIN', 'leader', 65, 69): {  # TRADE band_exit=14
        'entry_lo': 65, 'entry_hi': 69,
        'dca_drop': 10, 'exit_target': 14,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            65: {'exit_target': 1, 'ev': 1.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 79, 'effN': 735.1, 'cvErr': 21.6},
            66: {'exit_target': 33, 'ev': 8.684, 'hit': 75.44, 'basis': 'own-N', 'ownN': 57, 'effN': 842.1, 'cvErr': 19.6},
            67: {'exit_target': 2, 'ev': 0.164, 'hit': 97.34, 'basis': 'pooled', 'ownN': 64, 'effN': 785.8, 'cvErr': 12.6},
            68: {'exit_target': None, 'ev': -0.27, 'hit': None, 'basis': 'pooled', 'ownN': 59, 'effN': 802.2, 'cvErr': 15.6},
            69: {'exit_target': 29, 'ev': 6.542, 'hit': 77.08, 'basis': 'own-N', 'ownN': 48, 'effN': 868.4, 'cvErr': 18.3},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_MAIN', 'leader', 70, 74): {  # TRADE band_exit=9
        'entry_lo': 70, 'entry_hi': 74,
        'dca_drop': 20, 'exit_target': 9,
        'entry_size': 80, 'dca_size': 40,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            70: {'exit_target': 20, 'ev': 5.0, 'hit': 83.33, 'basis': 'own-N', 'ownN': 48, 'effN': 851.3, 'cvErr': 9.4},
            71: {'exit_target': 5, 'ev': 3.643, 'hit': 98.21, 'basis': 'own-N', 'ownN': 56, 'effN': 773.0, 'cvErr': 6.8},
            72: {'exit_target': 2, 'ev': 2.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 50, 'effN': 798.2, 'cvErr': 27.3},
            73: {'exit_target': 2, 'ev': 0.857, 'hit': 98.48, 'basis': 'pooled', 'ownN': 59, 'effN': 718.4, 'cvErr': 4.3},
            74: {'exit_target': 17, 'ev': 3.119, 'hit': 84.75, 'basis': 'own-N', 'ownN': 59, 'effN': 700.3, 'cvErr': 3.8},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_MAIN', 'leader', 75, 79): {  # TRADE band_exit=9
        'entry_lo': 75, 'entry_hi': 79,
        'dca_drop': 30, 'exit_target': 9,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            75: {'exit_target': 8, 'ev': 3.212, 'hit': 94.23, 'basis': 'own-N', 'ownN': 52, 'effN': 724.4, 'cvErr': 2.8},
            76: {'exit_target': 8, 'ev': 3.154, 'hit': 94.23, 'basis': 'own-N', 'ownN': 52, 'effN': 703.5, 'cvErr': 2.2},
            77: {'exit_target': 1, 'ev': 1.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 54, 'effN': 669.5, 'cvErr': 7.3},
            78: {'exit_target': 11, 'ev': 9.022, 'hit': 97.78, 'basis': 'own-N', 'ownN': 45, 'effN': 706.4, 'cvErr': 48.5},
            79: {'exit_target': 19, 'ev': 5.0, 'hit': 85.71, 'basis': 'own-N', 'ownN': 35, 'effN': 767.3, 'cvErr': 8.0},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_MAIN', 'leader', 80, 84): {  # TRADE band_exit=7
        'entry_lo': 80, 'entry_hi': 84,
        'dca_drop': None, 'exit_target': 7,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            80: {'exit_target': 3, 'ev': 3.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 47, 'effN': 641.9, 'cvErr': 7.4},
            81: {'exit_target': 1, 'ev': 1.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 36, 'effN': 698.2, 'cvErr': 4.7},
            82: {'exit_target': None, 'ev': -2.489, 'hit': None, 'basis': 'pooled', 'ownN': 37, 'effN': 658.9, 'cvErr': 33.9},
            83: {'exit_target': 15, 'ev': 5.667, 'hit': 90.48, 'basis': 'own-N', 'ownN': 42, 'effN': 591.3, 'cvErr': 6.3},
            84: {'exit_target': 7, 'ev': 1.226, 'hit': 93.64, 'basis': 'pooled', 'ownN': 43, 'effN': 554.8, 'cvErr': 2.9},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_MAIN', 'leader', 85, 89): {  # TRADE band_exit=10
        'entry_lo': 85, 'entry_hi': 89,
        'dca_drop': None, 'exit_target': 10,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            85: {'exit_target': 13, 'ev': 9.938, 'hit': 96.88, 'basis': 'own-N', 'ownN': 32, 'effN': 602.0, 'cvErr': 31.3},
            86: {'exit_target': 8, 'ev': 5.389, 'hit': 97.22, 'basis': 'own-N', 'ownN': 36, 'effN': 535.5, 'cvErr': 2.0},
            87: {'exit_target': 7, 'ev': 3.24, 'hit': 96.0, 'basis': 'own-N', 'ownN': 25, 'effN': 596.4, 'cvErr': 1.3},
            88: {'exit_target': 11, 'ev': 2.75, 'hit': 91.67, 'basis': 'own-N', 'ownN': 24, 'effN': 567.7, 'cvErr': 2.0},
            89: {'exit_target': 9, 'ev': 4.917, 'hit': 95.83, 'basis': 'own-N', 'ownN': 24, 'effN': 526.9, 'cvErr': 2.1},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_MAIN', 'underdog', 10, 14): {  # TRADE band_exit=38
        'entry_lo': 10, 'entry_hi': 14,
        'dca_drop': None, 'exit_target': 38,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            10: {'exit_target': 54, 'ev': 4.34, 'hit': 22.41, 'basis': 'pooled', 'ownN': 31, 'effN': 408.1, 'cvErr': 113.5},
            11: {'exit_target': 18, 'ev': 6.607, 'hit': 60.71, 'basis': 'own-N', 'ownN': 28, 'effN': 458.8, 'cvErr': 8.0},
            12: {'exit_target': 20, 'ev': 10.857, 'hit': 71.43, 'basis': 'own-N', 'ownN': 21, 'effN': 560.4, 'cvErr': 15.1},
            13: {'exit_target': 42, 'ev': 8.522, 'hit': 39.13, 'basis': 'own-N', 'ownN': 23, 'effN': 568.9, 'cvErr': 5.1},
            14: {'exit_target': 51, 'ev': 6.0, 'hit': 30.77, 'basis': 'own-N', 'ownN': 26, 'effN': 567.1, 'cvErr': 1.7},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_MAIN', 'underdog', 15, 19): {  # TRADE band_exit=60
        'entry_lo': 15, 'entry_hi': 19,
        'dca_drop': 15, 'exit_target': 60,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            15: {'exit_target': 60, 'ev': 6.875, 'hit': 29.17, 'basis': 'own-N', 'ownN': 24, 'effN': 619.9, 'cvErr': 5.1},
            16: {'exit_target': 54, 'ev': 4.401, 'hit': 29.14, 'basis': 'pooled', 'ownN': 40, 'effN': 509.5, 'cvErr': 159.4},
            17: {'exit_target': 70, 'ev': 11.275, 'hit': 32.5, 'basis': 'own-N', 'ownN': 40, 'effN': 531.5, 'cvErr': 31.6},
            18: {'exit_target': 46, 'ev': 7.946, 'hit': 40.54, 'basis': 'own-N', 'ownN': 37, 'effN': 575.0, 'cvErr': 2.6},
            19: {'exit_target': 70, 'ev': 10.667, 'hit': 33.33, 'basis': 'own-N', 'ownN': 30, 'effN': 663.1, 'cvErr': 9.3},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_MAIN', 'underdog', 20, 24): {  # TRADE band_exit=39
        'entry_lo': 20, 'entry_hi': 24,
        'dca_drop': 20, 'exit_target': 39,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            20: {'exit_target': 66, 'ev': 11.943, 'hit': 37.14, 'basis': 'own-N', 'ownN': 35, 'effN': 637.8, 'cvErr': 9.5},
            21: {'exit_target': 45, 'ev': 4.093, 'hit': 37.93, 'basis': 'pooled', 'ownN': 33, 'effN': 681.0, 'cvErr': 19.4},
            22: {'exit_target': 47, 'ev': 16.132, 'hit': 55.26, 'basis': 'own-N', 'ownN': 38, 'effN': 656.8, 'cvErr': 56.7},
            23: {'exit_target': 22, 'ev': 6.189, 'hit': 64.86, 'basis': 'own-N', 'ownN': 37, 'effN': 688.7, 'cvErr': 24.8},
            24: {'exit_target': 16, 'ev': 7.765, 'hit': 79.41, 'basis': 'own-N', 'ownN': 34, 'effN': 742.5, 'cvErr': 6.5},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_MAIN', 'underdog', 25, 29): {  # TRADE band_exit=52
        'entry_lo': 25, 'entry_hi': 29,
        'dca_drop': 25, 'exit_target': 52,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            25: {'exit_target': 16, 'ev': 5.122, 'hit': 73.47, 'basis': 'own-N', 'ownN': 49, 'effN': 638.1, 'cvErr': 15.2},
            26: {'exit_target': 73, 'ev': 8.269, 'hit': 34.62, 'basis': 'own-N', 'ownN': 52, 'effN': 639.5, 'cvErr': 10.9},
            27: {'exit_target': 72, 'ev': 4.114, 'hit': 31.43, 'basis': 'own-N', 'ownN': 35, 'effN': 802.5, 'cvErr': 9.0},
            28: {'exit_target': 71, 'ev': 12.765, 'hit': 41.18, 'basis': 'own-N', 'ownN': 51, 'effN': 686.6, 'cvErr': 34.2},
            29: {'exit_target': 31, 'ev': 4.462, 'hit': 55.77, 'basis': 'own-N', 'ownN': 52, 'effN': 700.0, 'cvErr': 2.2},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_MAIN', 'underdog', 30, 34): {  # TRADE band_exit=25
        'entry_lo': 30, 'entry_hi': 34,
        'dca_drop': 5, 'exit_target': 25,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            30: {'exit_target': 34, 'ev': 7.475, 'hit': 55.93, 'basis': 'own-N', 'ownN': 59, 'effN': 676.7, 'cvErr': 7.3},
            31: {'exit_target': 6, 'ev': 2.558, 'hit': 90.7, 'basis': 'own-N', 'ownN': 43, 'effN': 808.5, 'cvErr': 28.1},
            32: {'exit_target': 14, 'ev': 4.316, 'hit': 78.95, 'basis': 'own-N', 'ownN': 57, 'effN': 724.1, 'cvErr': 17.6},
            33: {'exit_target': 44, 'ev': 10.195, 'hit': 56.1, 'basis': 'own-N', 'ownN': 41, 'effN': 863.7, 'cvErr': 29.0},
            34: {'exit_target': 29, 'ev': 2.602, 'hit': 57.76, 'basis': 'pooled', 'ownN': 53, 'effN': 781.8, 'cvErr': 4.8},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_MAIN', 'underdog', 35, 39): {  # TRADE band_exit=34
        'entry_lo': 35, 'entry_hi': 39,
        'dca_drop': 25, 'exit_target': 34,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            35: {'exit_target': 29, 'ev': 7.667, 'hit': 66.67, 'basis': 'own-N', 'ownN': 69, 'effN': 703.9, 'cvErr': 11.5},
            36: {'exit_target': 39, 'ev': 6.339, 'hit': 56.45, 'basis': 'own-N', 'ownN': 62, 'effN': 751.5, 'cvErr': 7.1},
            37: {'exit_target': 35, 'ev': 7.509, 'hit': 61.82, 'basis': 'own-N', 'ownN': 55, 'effN': 803.2, 'cvErr': 9.5},
            38: {'exit_target': None, 'ev': -0.169, 'hit': None, 'basis': 'pooled', 'ownN': 64, 'effN': 756.7, 'cvErr': 49.5},
            39: {'exit_target': None, 'ev': -0.285, 'hit': None, 'basis': 'pooled', 'ownN': 65, 'effN': 755.5, 'cvErr': 2.7},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_MAIN', 'underdog', 40, 44): {  # TRADE band_exit=26
        'entry_lo': 40, 'entry_hi': 44,
        'dca_drop': 30, 'exit_target': 26,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            40: {'exit_target': 12, 'ev': 1.27, 'hit': 79.37, 'basis': 'own-N', 'ownN': 63, 'effN': 767.5, 'cvErr': 10.8},
            41: {'exit_target': 33, 'ev': 9.875, 'hit': 68.75, 'basis': 'own-N', 'ownN': 64, 'effN': 760.6, 'cvErr': 31.0},
            42: {'exit_target': 31, 'ev': 2.742, 'hit': 61.29, 'basis': 'own-N', 'ownN': 62, 'effN': 767.8, 'cvErr': 2.8},
            43: {'exit_target': 54, 'ev': 5.5, 'hit': 50.0, 'basis': 'own-N', 'ownN': 50, 'effN': 842.7, 'cvErr': 3.2},
            44: {'exit_target': 6, 'ev': 3.368, 'hit': 94.74, 'basis': 'own-N', 'ownN': 57, 'effN': 785.1, 'cvErr': 1.9},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },

    # ========================================================
    # ATP_CHALL
    # ========================================================
    ('ATP_CHALL', 'leader', 55, 59): {  # TRADE band_exit=15
        'entry_lo': 55, 'entry_hi': 59,
        'dca_drop': 5, 'exit_target': 15,
        'entry_size': 80, 'dca_size': 40,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            55: {'exit_target': 11, 'ev': 3.96, 'hit': 89.33, 'basis': 'own-N', 'ownN': 75, 'effN': 444.3, 'cvErr': 4.1},
            56: {'exit_target': 13, 'ev': 3.282, 'hit': 85.92, 'basis': 'own-N', 'ownN': 71, 'effN': 473.6, 'cvErr': 4.1},
            57: {'exit_target': 11, 'ev': 3.747, 'hit': 89.33, 'basis': 'own-N', 'ownN': 75, 'effN': 476.3, 'cvErr': 1.8},
            58: {'exit_target': 25, 'ev': 6.957, 'hit': 78.26, 'basis': 'own-N', 'ownN': 69, 'effN': 510.6, 'cvErr': 9.7},
            59: {'exit_target': 15, 'ev': 4.696, 'hit': 86.08, 'basis': 'own-N', 'ownN': 79, 'effN': 490.0, 'cvErr': 3.0},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_CHALL', 'leader', 60, 64): {  # TRADE band_exit=12
        'entry_lo': 60, 'entry_hi': 64,
        'dca_drop': 20, 'exit_target': 12,
        'entry_size': 80, 'dca_size': 40,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            60: {'exit_target': 12, 'ev': 2.0, 'hit': 86.11, 'basis': 'own-N', 'ownN': 72, 'effN': 525.3, 'cvErr': 4.8},
            61: {'exit_target': 10, 'ev': 1.376, 'hit': 87.85, 'basis': 'pooled', 'ownN': 87, 'effN': 488.9, 'cvErr': 16.6},
            62: {'exit_target': 25, 'ev': 8.481, 'hit': 81.01, 'basis': 'own-N', 'ownN': 79, 'effN': 521.5, 'cvErr': 26.1},
            63: {'exit_target': 10, 'ev': 5.29, 'hit': 93.55, 'basis': 'own-N', 'ownN': 93, 'effN': 487.9, 'cvErr': 4.3},
            64: {'exit_target': 4, 'ev': 1.167, 'hit': 95.83, 'basis': 'own-N', 'ownN': 72, 'effN': 557.5, 'cvErr': 8.2},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_CHALL', 'leader', 65, 69): {  # TRADE band_exit=25
        'entry_lo': 65, 'entry_hi': 69,
        'dca_drop': None, 'exit_target': 25,
        'entry_size': 80, 'dca_size': 0,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            65: {'exit_target': 27, 'ev': 1.325, 'hit': 71.67, 'basis': 'pooled', 'ownN': 85, 'effN': 516.7, 'cvErr': 30.4},
            66: {'exit_target': 33, 'ev': 13.43, 'hit': 80.23, 'basis': 'own-N', 'ownN': 86, 'effN': 513.5, 'cvErr': 59.5},
            67: {'exit_target': 13, 'ev': 2.885, 'hit': 87.36, 'basis': 'own-N', 'ownN': 87, 'effN': 506.7, 'cvErr': 6.3},
            68: {'exit_target': 27, 'ev': 2.797, 'hit': 59.88, 'basis': 'pooled', 'ownN': 87, 'effN': 497.8, 'cvErr': 6.5},
            69: {'exit_target': 27, 'ev': 4.481, 'hit': 76.54, 'basis': 'own-N', 'ownN': 81, 'effN': 500.9, 'cvErr': 2.3},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_CHALL', 'leader', 70, 74): {  # TRADE band_exit=24
        'entry_lo': 70, 'entry_hi': 74,
        'dca_drop': 10, 'exit_target': 24,
        'entry_size': 80, 'dca_size': 40,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            70: {'exit_target': 28, 'ev': 14.77, 'hit': 85.14, 'basis': 'own-N', 'ownN': 74, 'effN': 505.0, 'cvErr': 77.0},
            71: {'exit_target': 27, 'ev': 3.26, 'hit': 49.63, 'basis': 'pooled', 'ownN': 68, 'effN': 505.7, 'cvErr': 8.5},
            72: {'exit_target': 27, 'ev': 3.228, 'hit': 45.37, 'basis': 'pooled', 'ownN': 79, 'effN': 449.2, 'cvErr': 21.3},
            73: {'exit_target': 13, 'ev': 8.77, 'hit': 95.08, 'basis': 'own-N', 'ownN': 61, 'effN': 490.8, 'cvErr': 21.4},
            74: {'exit_target': 25, 'ev': 7.148, 'hit': 81.97, 'basis': 'own-N', 'ownN': 61, 'effN': 471.3, 'cvErr': 2.6},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_CHALL', 'leader', 75, 79): {  # TRADE band_exit=18
        'entry_lo': 75, 'entry_hi': 79,
        'dca_drop': 10, 'exit_target': 18,
        'entry_size': 80, 'dca_size': 40,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            75: {'exit_target': 24, 'ev': 1.967, 'hit': 46.54, 'basis': 'pooled', 'ownN': 65, 'effN': 439.1, 'cvErr': 20.6},
            76: {'exit_target': 23, 'ev': 14.2, 'hit': 88.89, 'basis': 'own-N', 'ownN': 45, 'effN': 513.0, 'cvErr': 43.4},
            77: {'exit_target': 21, 'ev': 9.299, 'hit': 88.06, 'basis': 'own-N', 'ownN': 67, 'effN': 404.8, 'cvErr': 3.7},
            78: {'exit_target': 19, 'ev': 5.143, 'hit': 85.71, 'basis': 'own-N', 'ownN': 63, 'effN': 404.8, 'cvErr': 6.8},
            79: {'exit_target': 2, 'ev': 2.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 48, 'effN': 450.4, 'cvErr': 14.5},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_CHALL', 'leader', 80, 84): {  # TRADE band_exit=5
        'entry_lo': 80, 'entry_hi': 84,
        'dca_drop': 15, 'exit_target': 5,
        'entry_size': 80, 'dca_size': 40,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            80: {'exit_target': None, 'ev': -0.462, 'hit': None, 'basis': 'own-N', 'ownN': 52, 'effN': 419.5, 'cvErr': 1.9},
            81: {'exit_target': 2, 'ev': 0.463, 'hit': 98.15, 'basis': 'own-N', 'ownN': 54, 'effN': 400.0, 'cvErr': 12.5},
            82: {'exit_target': 12, 'ev': 1.318, 'hit': 88.64, 'basis': 'own-N', 'ownN': 44, 'effN': 434.5, 'cvErr': 2.5},
            83: {'exit_target': 2, 'ev': 2.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 50, 'effN': 398.2, 'cvErr': 21.5},
            84: {'exit_target': 7, 'ev': 2.081, 'hit': 94.59, 'basis': 'own-N', 'ownN': 37, 'effN': 455.8, 'cvErr': 6.8},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_CHALL', 'leader', 85, 89): {  # SKIP  band_exit=None
        'entry_lo': 85, 'entry_hi': 89,
        'dca_drop': None, 'exit_target': None,
        'entry_size': 0, 'dca_size': 0,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            85: {'exit_target': None, 'ev': -1.4, 'hit': None, 'basis': 'pooled', 'ownN': 58, 'effN': 358.5, 'cvErr': 7.5},
            86: {'exit_target': None, 'ev': -0.419, 'hit': None, 'basis': 'own-N', 'ownN': 43, 'effN': 406.4, 'cvErr': 9.4},
            87: {'exit_target': None, 'ev': -0.66, 'hit': None, 'basis': 'own-N', 'ownN': 53, 'effN': 360.2, 'cvErr': 2.0},
            88: {'exit_target': None, 'ev': -1.913, 'hit': None, 'basis': 'own-N', 'ownN': 46, 'effN': 369.6, 'cvErr': 5.5},
            89: {'exit_target': None, 'ev': -2.395, 'hit': None, 'basis': 'pooled', 'ownN': 48, 'effN': 344.4, 'cvErr': 14.7},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_CHALL', 'underdog', 10, 14): {  # TRADE band_exit=59
        'entry_lo': 10, 'entry_hi': 14,
        'dca_drop': None, 'exit_target': 59,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            10: {'exit_target': 57, 'ev': 7.106, 'hit': 25.53, 'basis': 'own-N', 'ownN': 47, 'effN': 341.7, 'cvErr': 1.0},
            11: {'exit_target': 72, 'ev': 8.367, 'hit': 23.33, 'basis': 'own-N', 'ownN': 30, 'effN': 437.2, 'cvErr': 2.3},
            12: {'exit_target': 78, 'ev': 12.231, 'hit': 26.92, 'basis': 'own-N', 'ownN': 52, 'effN': 357.1, 'cvErr': 11.9},
            13: {'exit_target': 43, 'ev': 6.584, 'hit': 34.97, 'basis': 'pooled', 'ownN': 51, 'effN': 372.2, 'cvErr': 6.6},
            14: {'exit_target': 49, 'ev': 16.333, 'hit': 48.15, 'basis': 'own-N', 'ownN': 54, 'effN': 371.7, 'cvErr': 21.0},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_CHALL', 'underdog', 15, 19): {  # TRADE band_exit=49
        'entry_lo': 15, 'entry_hi': 19,
        'dca_drop': 15, 'exit_target': 49,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            15: {'exit_target': 43, 'ev': 13.383, 'hit': 48.94, 'basis': 'own-N', 'ownN': 47, 'effN': 403.9, 'cvErr': 8.1},
            16: {'exit_target': 43, 'ev': 6.281, 'hit': 37.76, 'basis': 'pooled', 'ownN': 48, 'effN': 404.9, 'cvErr': 31.5},
            17: {'exit_target': 60, 'ev': 17.571, 'hit': 44.9, 'basis': 'own-N', 'ownN': 49, 'effN': 403.8, 'cvErr': 59.9},
            18: {'exit_target': 42, 'ev': 10.966, 'hit': 48.28, 'basis': 'own-N', 'ownN': 58, 'effN': 372.9, 'cvErr': 1.5},
            19: {'exit_target': 58, 'ev': 6.143, 'hit': 32.65, 'basis': 'own-N', 'ownN': 49, 'effN': 406.8, 'cvErr': 1.5},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_CHALL', 'underdog', 20, 24): {  # TRADE band_exit=36
        'entry_lo': 20, 'entry_hi': 24,
        'dca_drop': None, 'exit_target': 36,
        'entry_size': 80, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            20: {'exit_target': 33, 'ev': 14.512, 'hit': 65.12, 'basis': 'own-N', 'ownN': 43, 'effN': 436.9, 'cvErr': 25.3},
            21: {'exit_target': 22, 'ev': 5.914, 'hit': 62.59, 'basis': 'pooled', 'ownN': 44, 'effN': 435.0, 'cvErr': 25.9},
            22: {'exit_target': 22, 'ev': 8.462, 'hit': 69.23, 'basis': 'own-N', 'ownN': 52, 'effN': 403.0, 'cvErr': 20.8},
            23: {'exit_target': 47, 'ev': 5.519, 'hit': 40.74, 'basis': 'own-N', 'ownN': 54, 'effN': 400.4, 'cvErr': 3.5},
            24: {'exit_target': 52, 'ev': 6.667, 'hit': 40.35, 'basis': 'own-N', 'ownN': 57, 'effN': 395.5, 'cvErr': 7.0},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_CHALL', 'underdog', 25, 29): {  # TRADE band_exit=37
        'entry_lo': 25, 'entry_hi': 29,
        'dca_drop': 25, 'exit_target': 37,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            25: {'exit_target': 27, 'ev': 5.0, 'hit': 57.69, 'basis': 'own-N', 'ownN': 52, 'effN': 423.0, 'cvErr': 1.7},
            26: {'exit_target': 20, 'ev': 3.102, 'hit': 63.27, 'basis': 'own-N', 'ownN': 49, 'effN': 447.6, 'cvErr': 10.7},
            27: {'exit_target': 61, 'ev': 11.923, 'hit': 44.23, 'basis': 'own-N', 'ownN': 52, 'effN': 447.3, 'cvErr': 35.2},
            28: {'exit_target': 20, 'ev': 3.418, 'hit': 65.45, 'basis': 'own-N', 'ownN': 55, 'effN': 450.7, 'cvErr': 43.3},
            29: {'exit_target': 60, 'ev': 9.938, 'hit': 43.75, 'basis': 'own-N', 'ownN': 48, 'effN': 503.3, 'cvErr': 32.0},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_CHALL', 'underdog', 30, 34): {  # TRADE band_exit=18
        'entry_lo': 30, 'entry_hi': 34,
        'dca_drop': 30, 'exit_target': 18,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            30: {'exit_target': 15, 'ev': 5.217, 'hit': 78.26, 'basis': 'own-N', 'ownN': 69, 'effN': 439.0, 'cvErr': 5.5},
            31: {'exit_target': 16, 'ev': 4.25, 'hit': 75.0, 'basis': 'own-N', 'ownN': 80, 'effN': 427.1, 'cvErr': 3.5},
            32: {'exit_target': 2, 'ev': 0.622, 'hit': 95.95, 'basis': 'own-N', 'ownN': 74, 'effN': 455.8, 'cvErr': 20.8},
            33: {'exit_target': 9, 'ev': 0.945, 'hit': 80.82, 'basis': 'own-N', 'ownN': 73, 'effN': 466.0, 'cvErr': 10.5},
            34: {'exit_target': 52, 'ev': 10.387, 'hit': 51.61, 'basis': 'own-N', 'ownN': 62, 'effN': 506.9, 'cvErr': 34.1},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_CHALL', 'underdog', 35, 39): {  # TRADE band_exit=24
        'entry_lo': 35, 'entry_hi': 39,
        'dca_drop': None, 'exit_target': 24,
        'entry_size': 80, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            35: {'exit_target': 9, 'ev': 3.634, 'hit': 87.8, 'basis': 'own-N', 'ownN': 82, 'effN': 442.6, 'cvErr': 1.9},
            36: {'exit_target': 58, 'ev': 4.517, 'hit': 43.1, 'basis': 'own-N', 'ownN': 58, 'effN': 526.0, 'cvErr': 9.6},
            37: {'exit_target': 44, 'ev': 4.123, 'hit': 50.77, 'basis': 'own-N', 'ownN': 65, 'effN': 497.0, 'cvErr': 3.5},
            38: {'exit_target': 10, 'ev': 2.519, 'hit': 84.42, 'basis': 'own-N', 'ownN': 77, 'effN': 456.9, 'cvErr': 58.3},
            39: {'exit_target': 11, 'ev': 3.568, 'hit': 85.14, 'basis': 'own-N', 'ownN': 74, 'effN': 463.7, 'cvErr': 1.5},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('ATP_CHALL', 'underdog', 40, 44): {  # TRADE band_exit=52
        'entry_lo': 40, 'entry_hi': 44,
        'dca_drop': None, 'exit_target': 52,
        'entry_size': 80, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            40: {'exit_target': 59, 'ev': 8.162, 'hit': 48.65, 'basis': 'own-N', 'ownN': 74, 'effN': 458.7, 'cvErr': 13.5},
            41: {'exit_target': 37, 'ev': 7.082, 'hit': 61.64, 'basis': 'own-N', 'ownN': 73, 'effN': 454.5, 'cvErr': 3.8},
            42: {'exit_target': 53, 'ev': 5.5, 'hit': 50.0, 'basis': 'own-N', 'ownN': 56, 'effN': 510.8, 'cvErr': 2.1},
            43: {'exit_target': 56, 'ev': 3.306, 'hit': 46.77, 'basis': 'own-N', 'ownN': 62, 'effN': 478.4, 'cvErr': 1.3},
            44: {'exit_target': 55, 'ev': 11.18, 'hit': 55.74, 'basis': 'own-N', 'ownN': 61, 'effN': 476.4, 'cvErr': 8.1},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },

    # ========================================================
    # WTA_MAIN
    # ========================================================
    ('WTA_MAIN', 'leader', 55, 59): {  # TRADE band_exit=21
        'entry_lo': 55, 'entry_hi': 59,
        'dca_drop': 30, 'exit_target': 21,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            55: {'exit_target': 22, 'ev': 9.167, 'hit': 83.33, 'basis': 'own-N', 'ownN': 48, 'effN': 480.3, 'cvErr': 27.8},
            56: {'exit_target': 7, 'ev': 1.522, 'hit': 91.3, 'basis': 'own-N', 'ownN': 46, 'effN': 495.3, 'cvErr': 60.2},
            57: {'exit_target': 31, 'ev': 3.69, 'hit': 68.97, 'basis': 'own-N', 'ownN': 58, 'effN': 445.8, 'cvErr': 2.2},
            58: {'exit_target': 37, 'ev': 2.943, 'hit': 64.15, 'basis': 'own-N', 'ownN': 53, 'effN': 470.6, 'cvErr': 1.6},
            59: {'exit_target': 5, 'ev': 1.69, 'hit': 94.83, 'basis': 'own-N', 'ownN': 58, 'effN': 454.0, 'cvErr': 39.7},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_MAIN', 'leader', 60, 64): {  # TRADE band_exit=36
        'entry_lo': 60, 'entry_hi': 64,
        'dca_drop': None, 'exit_target': 36,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            60: {'exit_target': 39, 'ev': 6.541, 'hit': 65.57, 'basis': 'own-N', 'ownN': 61, 'effN': 445.1, 'cvErr': 10.9},
            61: {'exit_target': 38, 'ev': 5.717, 'hit': 67.39, 'basis': 'own-N', 'ownN': 46, 'effN': 509.8, 'cvErr': 1.6},
            62: {'exit_target': 36, 'ev': 5.586, 'hit': 68.97, 'basis': 'own-N', 'ownN': 58, 'effN': 455.1, 'cvErr': 2.3},
            63: {'exit_target': 36, 'ev': 3.717, 'hit': 65.22, 'basis': 'own-N', 'ownN': 46, 'effN': 505.4, 'cvErr': 8.3},
            64: {'exit_target': 31, 'ev': 10.754, 'hit': 78.69, 'basis': 'own-N', 'ownN': 61, 'effN': 437.0, 'cvErr': 38.9},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_MAIN', 'leader', 65, 69): {  # TRADE band_exit=15
        'entry_lo': 65, 'entry_hi': 69,
        'dca_drop': 20, 'exit_target': 15,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            65: {'exit_target': 29, 'ev': 4.031, 'hit': 73.44, 'basis': 'own-N', 'ownN': 64, 'effN': 421.6, 'cvErr': 3.5},
            66: {'exit_target': 20, 'ev': 5.667, 'hit': 83.33, 'basis': 'own-N', 'ownN': 36, 'effN': 550.7, 'cvErr': 5.2},
            67: {'exit_target': 14, 'ev': 5.321, 'hit': 89.29, 'basis': 'own-N', 'ownN': 56, 'effN': 436.5, 'cvErr': 9.8},
            68: {'exit_target': 3, 'ev': 3.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 46, 'effN': 473.4, 'cvErr': 20.4},
            69: {'exit_target': 5, 'ev': 0.811, 'hit': 94.34, 'basis': 'own-N', 'ownN': 53, 'effN': 433.6, 'cvErr': 2.0},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_MAIN', 'leader', 70, 74): {  # TRADE band_exit=21
        'entry_lo': 70, 'entry_hi': 74,
        'dca_drop': 20, 'exit_target': 21,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            70: {'exit_target': 23, 'ev': 6.467, 'hit': 82.22, 'basis': 'own-N', 'ownN': 45, 'effN': 462.2, 'cvErr': 6.3},
            71: {'exit_target': 26, 'ev': 6.946, 'hit': 80.36, 'basis': 'own-N', 'ownN': 56, 'effN': 407.0, 'cvErr': 14.1},
            72: {'exit_target': 2, 'ev': 2.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 28, 'effN': 562.7, 'cvErr': 24.6},
            73: {'exit_target': None, 'ev': -0.077, 'hit': None, 'basis': 'pooled', 'ownN': 59, 'effN': 381.8, 'cvErr': 27.0},
            74: {'exit_target': 23, 'ev': 6.13, 'hit': 82.61, 'basis': 'own-N', 'ownN': 46, 'effN': 422.6, 'cvErr': 11.3},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_MAIN', 'leader', 75, 79): {  # TRADE band_exit=10
        'entry_lo': 75, 'entry_hi': 79,
        'dca_drop': 30, 'exit_target': 10,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            75: {'exit_target': 1, 'ev': 1.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 44, 'effN': 422.0, 'cvErr': 59.8},
            76: {'exit_target': 16, 'ev': 8.333, 'hit': 91.67, 'basis': 'own-N', 'ownN': 36, 'effN': 453.9, 'cvErr': 25.5},
            77: {'exit_target': 10, 'ev': 2.75, 'hit': 91.67, 'basis': 'own-N', 'ownN': 36, 'effN': 441.8, 'cvErr': 4.7},
            78: {'exit_target': 18, 'ev': 4.286, 'hit': 85.71, 'basis': 'own-N', 'ownN': 56, 'effN': 344.9, 'cvErr': 12.4},
            79: {'exit_target': 3, 'ev': 0.897, 'hit': 97.44, 'basis': 'own-N', 'ownN': 39, 'effN': 400.3, 'cvErr': 24.4},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_MAIN', 'leader', 80, 84): {  # TRADE band_exit=12
        'entry_lo': 80, 'entry_hi': 84,
        'dca_drop': 30, 'exit_target': 12,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            80: {'exit_target': 11, 'ev': 8.242, 'hit': 96.97, 'basis': 'own-N', 'ownN': 33, 'effN': 422.2, 'cvErr': 29.8},
            81: {'exit_target': 7, 'ev': 4.25, 'hit': 96.88, 'basis': 'own-N', 'ownN': 32, 'effN': 415.8, 'cvErr': 4.7},
            82: {'exit_target': 17, 'ev': 4.625, 'hit': 84.38, 'basis': 'own-N', 'ownN': 32, 'effN': 402.9, 'cvErr': 10.8},
            83: {'exit_target': None, 'ev': -0.5, 'hit': None, 'basis': 'own-N', 'ownN': 36, 'effN': 367.9, 'cvErr': 4.6},
            84: {'exit_target': None, 'ev': -0.127, 'hit': None, 'basis': 'pooled', 'ownN': 25, 'effN': 423.6, 'cvErr': 69.9},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_MAIN', 'leader', 85, 89): {  # TRADE band_exit=7
        'entry_lo': 85, 'entry_hi': 89,
        'dca_drop': 30, 'exit_target': 7,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            85: {'exit_target': 13, 'ev': 8.545, 'hit': 95.45, 'basis': 'own-N', 'ownN': 44, 'effN': 312.3, 'cvErr': 34.7},
            86: {'exit_target': 3, 'ev': 3.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 29, 'effN': 363.3, 'cvErr': 2.4},
            87: {'exit_target': 4, 'ev': 4.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 30, 'effN': 340.1, 'cvErr': 34.0},
            88: {'exit_target': None, 'ev': -0.636, 'hit': None, 'basis': 'pooled', 'ownN': 35, 'effN': 300.2, 'cvErr': 12.7},
            89: {'exit_target': 3, 'ev': 3.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 26, 'effN': 316.1, 'cvErr': 4.6},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_MAIN', 'underdog', 10, 14): {  # TRADE band_exit=24
        'entry_lo': 10, 'entry_hi': 14,
        'dca_drop': None, 'exit_target': 24,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            10: {'exit_target': 52, 'ev': 10.667, 'hit': 33.33, 'basis': 'own-N', 'ownN': 27, 'effN': 290.5, 'cvErr': 5.2},
            11: {'exit_target': 9, 'ev': 5.19, 'hit': 80.95, 'basis': 'own-N', 'ownN': 21, 'effN': 346.5, 'cvErr': 38.8},
            12: {'exit_target': 42, 'ev': 12.75, 'hit': 45.83, 'basis': 'own-N', 'ownN': 24, 'effN': 347.9, 'cvErr': 23.7},
            13: {'exit_target': 11, 'ev': 4.231, 'hit': 71.79, 'basis': 'own-N', 'ownN': 39, 'effN': 294.1, 'cvErr': 2.0},
            14: {'exit_target': 10, 'ev': 3.159, 'hit': 71.5, 'basis': 'pooled', 'ownN': 31, 'effN': 341.0, 'cvErr': 9.2},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_MAIN', 'underdog', 15, 19): {  # TRADE band_exit=54
        'entry_lo': 15, 'entry_hi': 19,
        'dca_drop': 10, 'exit_target': 54,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            15: {'exit_target': 24, 'ev': 5.0, 'hit': 51.28, 'basis': 'own-N', 'ownN': 39, 'effN': 316.5, 'cvErr': 3.1},
            16: {'exit_target': 46, 'ev': 5.377, 'hit': 34.48, 'basis': 'pooled', 'ownN': 20, 'effN': 453.6, 'cvErr': 28.9},
            17: {'exit_target': 81, 'ev': 16.6, 'hit': 34.29, 'basis': 'own-N', 'ownN': 35, 'effN': 357.4, 'cvErr': 51.8},
            18: {'exit_target': 81, 'ev': 8.053, 'hit': 26.32, 'basis': 'own-N', 'ownN': 19, 'effN': 498.2, 'cvErr': 18.8},
            19: {'exit_target': 51, 'ev': 12.316, 'hit': 44.74, 'basis': 'own-N', 'ownN': 38, 'effN': 366.2, 'cvErr': 22.9},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_MAIN', 'underdog', 20, 24): {  # TRADE band_exit=41
        'entry_lo': 20, 'entry_hi': 24,
        'dca_drop': 20, 'exit_target': 41,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            20: {'exit_target': 33, 'ev': 9.732, 'hit': 56.1, 'basis': 'own-N', 'ownN': 41, 'effN': 364.3, 'cvErr': 19.5},
            21: {'exit_target': 40, 'ev': 7.154, 'hit': 46.15, 'basis': 'own-N', 'ownN': 39, 'effN': 384.8, 'cvErr': 16.3},
            22: {'exit_target': 46, 'ev': 13.619, 'hit': 52.38, 'basis': 'own-N', 'ownN': 42, 'effN': 381.8, 'cvErr': 53.3},
            23: {'exit_target': 40, 'ev': 5.159, 'hit': 44.7, 'basis': 'pooled', 'ownN': 40, 'effN': 399.8, 'cvErr': 105.9},
            24: {'exit_target': 45, 'ev': 5.133, 'hit': 42.22, 'basis': 'own-N', 'ownN': 45, 'effN': 385.5, 'cvErr': 5.2},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_MAIN', 'underdog', 25, 29): {  # TRADE band_exit=49
        'entry_lo': 25, 'entry_hi': 29,
        'dca_drop': 20, 'exit_target': 49,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            25: {'exit_target': 49, 'ev': 10.238, 'hit': 47.62, 'basis': 'own-N', 'ownN': 42, 'effN': 404.3, 'cvErr': 8.7},
            26: {'exit_target': 31, 'ev': 8.756, 'hit': 60.98, 'basis': 'own-N', 'ownN': 41, 'effN': 414.3, 'cvErr': 3.8},
            27: {'exit_target': 72, 'ev': 8.538, 'hit': 35.9, 'basis': 'own-N', 'ownN': 39, 'effN': 429.4, 'cvErr': 5.9},
            28: {'exit_target': 37, 'ev': 13.528, 'hit': 63.89, 'basis': 'own-N', 'ownN': 36, 'effN': 451.5, 'cvErr': 11.7},
            29: {'exit_target': 53, 'ev': 10.217, 'hit': 47.83, 'basis': 'own-N', 'ownN': 46, 'effN': 403.5, 'cvErr': 4.3},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_MAIN', 'underdog', 30, 34): {  # TRADE band_exit=41
        'entry_lo': 30, 'entry_hi': 34,
        'dca_drop': 30, 'exit_target': 41,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            30: {'exit_target': 69, 'ev': 10.765, 'hit': 41.18, 'basis': 'own-N', 'ownN': 34, 'effN': 474.6, 'cvErr': 4.8},
            31: {'exit_target': 17, 'ev': 7.222, 'hit': 79.63, 'basis': 'own-N', 'ownN': 54, 'effN': 380.1, 'cvErr': 3.1},
            32: {'exit_target': 34, 'ev': 8.333, 'hit': 61.11, 'basis': 'own-N', 'ownN': 54, 'effN': 384.1, 'cvErr': 3.4},
            33: {'exit_target': 66, 'ev': 8.25, 'hit': 41.67, 'basis': 'own-N', 'ownN': 36, 'effN': 476.7, 'cvErr': 8.5},
            34: {'exit_target': 34, 'ev': 11.333, 'hit': 66.67, 'basis': 'own-N', 'ownN': 39, 'effN': 463.3, 'cvErr': 15.6},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_MAIN', 'underdog', 35, 39): {  # TRADE band_exit=27
        'entry_lo': 35, 'entry_hi': 39,
        'dca_drop': None, 'exit_target': 27,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            35: {'exit_target': 64, 'ev': 17.105, 'hit': 52.63, 'basis': 'own-N', 'ownN': 38, 'effN': 475.3, 'cvErr': 102.4},
            36: {'exit_target': 9, 'ev': 3.057, 'hit': 86.79, 'basis': 'own-N', 'ownN': 53, 'effN': 407.4, 'cvErr': 3.7},
            37: {'exit_target': 1, 'ev': 1.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 44, 'effN': 453.1, 'cvErr': 149.2},
            38: {'exit_target': 37, 'ev': 4.111, 'hit': 53.7, 'basis': 'own-N', 'ownN': 54, 'effN': 414.9, 'cvErr': 5.1},
            39: {'exit_target': 30, 'ev': 5.467, 'hit': 64.44, 'basis': 'own-N', 'ownN': 45, 'effN': 458.2, 'cvErr': 8.9},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_MAIN', 'underdog', 40, 44): {  # TRADE band_exit=41
        'entry_lo': 40, 'entry_hi': 44,
        'dca_drop': 30, 'exit_target': 41,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            40: {'exit_target': 59, 'ev': 3.788, 'hit': 44.23, 'basis': 'own-N', 'ownN': 52, 'effN': 430.8, 'cvErr': 11.3},
            41: {'exit_target': 35, 'ev': 7.64, 'hit': 64.0, 'basis': 'own-N', 'ownN': 50, 'effN': 441.6, 'cvErr': 13.7},
            42: {'exit_target': 57, 'ev': 7.5, 'hit': 50.0, 'basis': 'own-N', 'ownN': 46, 'effN': 462.0, 'cvErr': 10.5},
            43: {'exit_target': 30, 'ev': 1.213, 'hit': 60.43, 'basis': 'pooled', 'ownN': 54, 'effN': 427.9, 'cvErr': 28.8},
            44: {'exit_target': 20, 'ev': 4.39, 'hit': 75.61, 'basis': 'own-N', 'ownN': 41, 'effN': 492.9, 'cvErr': 3.7},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },

    # ========================================================
    # WTA_CHALL
    # ========================================================
    ('WTA_CHALL', 'leader', 55, 59): {  # TRADE band_exit=25
        'entry_lo': 55, 'entry_hi': 59,
        'dca_drop': None, 'exit_target': 25,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            55: {'exit_target': 22, 'ev': 10.154, 'hit': 84.62, 'basis': 'own-N', 'ownN': 13, 'effN': 142.9, 'cvErr': 31.6},
            56: {'exit_target': 39, 'ev': 24.385, 'hit': 84.62, 'basis': 'own-N', 'ownN': 13, 'effN': 147.8, 'cvErr': 222.7},
            57: {'exit_target': 13, 'ev': 13.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 9, 'effN': 183.7, 'cvErr': 64.7},
            58: {'exit_target': 22, 'ev': 6.0, 'hit': 80.0, 'basis': 'own-N', 'ownN': 10, 'effN': 179.3, 'cvErr': 27.1},
            59: {'exit_target': None, 'ev': -0.326, 'hit': None, 'basis': 'pooled', 'ownN': 14, 'effN': 157.8, 'cvErr': 361.5},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_CHALL', 'leader', 60, 64): {  # TRADE band_exit=11
        'entry_lo': 60, 'entry_hi': 64,
        'dca_drop': 30, 'exit_target': 11,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            60: {'exit_target': 7, 'ev': 7.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 15, 'effN': 157.6, 'cvErr': 20.9},
            61: {'exit_target': 2, 'ev': 2.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 12, 'effN': 177.0, 'cvErr': 247.6},
            62: {'exit_target': 3, 'ev': 3.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 21, 'effN': 143.1, 'cvErr': 22.2},
            63: {'exit_target': 14, 'ev': 3.957, 'hit': 86.96, 'basis': 'own-N', 'ownN': 23, 'effN': 139.0, 'cvErr': 29.1},
            64: {'exit_target': 35, 'ev': 2.0, 'hit': 66.67, 'basis': 'own-N', 'ownN': 12, 'effN': 179.8, 'cvErr': 36.4},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_CHALL', 'leader', 65, 69): {  # TRADE band_exit=15
        'entry_lo': 65, 'entry_hi': 69,
        'dca_drop': None, 'exit_target': 15,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            65: {'exit_target': 9, 'ev': 9.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 14, 'effN': 167.1, 'cvErr': 47.9},
            66: {'exit_target': 32, 'ev': 18.0, 'hit': 85.71, 'basis': 'own-N', 'ownN': 14, 'effN': 164.0, 'cvErr': 215.0},
            67: {'exit_target': None, 'ev': -0.923, 'hit': None, 'basis': 'pooled', 'ownN': 17, 'effN': 146.3, 'cvErr': 328.3},
            68: {'exit_target': 4, 'ev': 4.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 11, 'effN': 173.4, 'cvErr': 27.9},
            69: {'exit_target': 11, 'ev': 12.9, 'hit': 90.0, 'basis': 'own-N', 'ownN': 10, 'effN': 176.1, 'cvErr': 117.1},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_CHALL', 'leader', 70, 74): {  # TRADE band_exit=7
        'entry_lo': 70, 'entry_hi': 74,
        'dca_drop': None, 'exit_target': 7,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            70: {'exit_target': 1, 'ev': 1.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 16, 'effN': 134.9, 'cvErr': 55.3},
            71: {'exit_target': 11, 'ev': 11.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 6, 'effN': 211.2, 'cvErr': 80.1},
            72: {'exit_target': 5, 'ev': 0.404, 'hit': 94.03, 'basis': 'pooled', 'ownN': 10, 'effN': 159.9, 'cvErr': 174.0},
            73: {'exit_target': 15, 'ev': 8.0, 'hit': 81.82, 'basis': 'own-N', 'ownN': 11, 'effN': 147.1, 'cvErr': 29.4},
            74: {'exit_target': 10, 'ev': 10.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 9, 'effN': 157.4, 'cvErr': 17.1},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_CHALL', 'leader', 75, 79): {  # TRADE band_exit=21
        'entry_lo': 75, 'entry_hi': 79,
        'dca_drop': None, 'exit_target': 21,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            75: {'exit_target': 21, 'ev': 21.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 12, 'effN': 131.0, 'cvErr': 104.2},
            76: {'exit_target': 23, 'ev': 8.857, 'hit': 85.71, 'basis': 'own-N', 'ownN': 7, 'effN': 167.1, 'cvErr': 13.8},
            77: {'exit_target': None, 'ev': -1.118, 'hit': None, 'basis': 'own-N', 'ownN': 17, 'effN': 102.4, 'cvErr': 6.4},
            78: {'exit_target': None, 'ev': -5.075, 'hit': None, 'basis': 'pooled', 'ownN': 8, 'effN': 145.3, 'cvErr': 192.2},
            79: {'exit_target': 20, 'ev': 7.625, 'hit': 87.5, 'basis': 'own-N', 'ownN': 8, 'effN': 140.3, 'cvErr': 17.0},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_CHALL', 'leader', 80, 84): {  # TRADE band_exit=10
        'entry_lo': 80, 'entry_hi': 84,
        'dca_drop': None, 'exit_target': 10,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            80: {'exit_target': 15, 'ev': 15.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 8, 'effN': 135.4, 'cvErr': 34.1},
            81: {'exit_target': 18, 'ev': 18.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 5, 'effN': 166.9, 'cvErr': 78.9},
            82: {'exit_target': 5, 'ev': 5.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 9, 'effN': 118.8, 'cvErr': 22.1},
            83: {'exit_target': 16, 'ev': 16.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 3, 'effN': 198.2, 'cvErr': 82.7},
            84: {'exit_target': 1, 'ev': 1.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 5, 'effN': 148.4, 'cvErr': 99.0},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_CHALL', 'leader', 85, 89): {  # TRADE band_exit=8
        'entry_lo': 85, 'entry_hi': 89,
        'dca_drop': 30, 'exit_target': 8,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'leader', 'maker_bid_offset': 0,
        'percent_exits': {
            85: {'exit_target': 7, 'ev': 7.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 13, 'effN': 89.2, 'cvErr': 24.2},
            86: {'exit_target': 13, 'ev': 13.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 3, 'effN': 173.1, 'cvErr': 34.4},
            87: {'exit_target': 12, 'ev': 12.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 8, 'effN': 104.7, 'cvErr': 5.8},
            88: {'exit_target': 11, 'ev': 11.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 9, 'effN': 95.0, 'cvErr': 91.2},
            89: {'exit_target': 2, 'ev': 2.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 7, 'effN': 100.2, 'cvErr': 653.4},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_CHALL', 'underdog', 10, 14): {  # TRADE band_exit=81
        'entry_lo': 10, 'entry_hi': 14,
        'dca_drop': None, 'exit_target': 81,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            10: {'exit_target': 89, 'ev': 6.5, 'hit': 16.67, 'basis': 'own-N', 'ownN': 6, 'effN': 112.2, 'cvErr': 20.0},
            11: {'exit_target': 88, 'ev': 17.286, 'hit': 28.57, 'basis': 'own-N', 'ownN': 7, 'effN': 111.0, 'cvErr': 67.3},
            12: {'exit_target': 67, 'ev': 5.556, 'hit': 22.22, 'basis': 'own-N', 'ownN': 9, 'effN': 104.5, 'cvErr': 7.4},
            13: {'exit_target': 83, 'ev': 2.541, 'hit': 14.0, 'basis': 'pooled', 'ownN': 9, 'effN': 107.5, 'cvErr': 44.9},
            14: {'exit_target': 83, 'ev': 22.375, 'hit': 37.5, 'basis': 'own-N', 'ownN': 8, 'effN': 115.9, 'cvErr': 143.4},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_CHALL', 'underdog', 15, 19): {  # TRADE band_exit=28
        'entry_lo': 15, 'entry_hi': 19,
        'dca_drop': None, 'exit_target': 28,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            15: {'exit_target': 84, 'ev': 13.286, 'hit': 28.57, 'basis': 'own-N', 'ownN': 7, 'effN': 126.2, 'cvErr': 22.8},
            16: {'exit_target': 18, 'ev': 18.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 2, 'effN': 225.5, 'cvErr': 164.5},
            17: {'exit_target': 4, 'ev': 2.091, 'hit': 90.91, 'basis': 'own-N', 'ownN': 11, 'effN': 104.7, 'cvErr': 86.2},
            18: {'exit_target': 12, 'ev': 7.714, 'hit': 85.71, 'basis': 'own-N', 'ownN': 7, 'effN': 134.8, 'cvErr': 10.7},
            19: {'exit_target': 18, 'ev': 3.207, 'hit': 60.02, 'basis': 'pooled', 'ownN': 1, 'effN': 282.9, 'cvErr': 340.0},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_CHALL', 'underdog', 20, 24): {  # TRADE band_exit=35
        'entry_lo': 20, 'entry_hi': 24,
        'dca_drop': None, 'exit_target': 35,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            20: {'exit_target': 18, 'ev': 9.231, 'hit': 76.92, 'basis': 'own-N', 'ownN': 13, 'effN': 101.2, 'cvErr': 24.7},
            21: {'exit_target': 15, 'ev': 3.516, 'hit': 68.1, 'basis': 'pooled', 'ownN': 11, 'effN': 113.2, 'cvErr': 13.4},
            22: {'exit_target': 37, 'ev': 11.714, 'hit': 57.14, 'basis': 'own-N', 'ownN': 7, 'effN': 147.1, 'cvErr': 88.2},
            23: {'exit_target': 37, 'ev': 3.151, 'hit': 43.59, 'basis': 'pooled', 'ownN': 5, 'effN': 178.7, 'cvErr': 338.5},
            24: {'exit_target': 75, 'ev': 30.0, 'hit': 54.55, 'basis': 'own-N', 'ownN': 11, 'effN': 122.0, 'cvErr': 222.7},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_CHALL', 'underdog', 25, 29): {  # TRADE band_exit=42
        'entry_lo': 25, 'entry_hi': 29,
        'dca_drop': None, 'exit_target': 42,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            25: {'exit_target': 38, 'ev': 17.0, 'hit': 66.67, 'basis': 'own-N', 'ownN': 12, 'effN': 119.9, 'cvErr': 39.0},
            26: {'exit_target': 1, 'ev': 1.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 8, 'effN': 151.0, 'cvErr': 233.6},
            27: {'exit_target': 27, 'ev': 9.0, 'hit': 66.67, 'basis': 'own-N', 'ownN': 9, 'effN': 145.9, 'cvErr': 55.5},
            28: {'exit_target': 71, 'ev': 14.429, 'hit': 42.86, 'basis': 'own-N', 'ownN': 7, 'effN': 168.4, 'cvErr': 29.9},
            29: {'exit_target': 65, 'ev': 14.467, 'hit': 46.24, 'basis': 'pooled', 'ownN': 13, 'effN': 128.0, 'cvErr': 9.2},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_CHALL', 'underdog', 30, 34): {  # TRADE band_exit=50
        'entry_lo': 30, 'entry_hi': 34,
        'dca_drop': None, 'exit_target': 50,
        'entry_size': 40, 'dca_size': 0,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            30: {'exit_target': 69, 'ev': 29.4, 'hit': 60.0, 'basis': 'own-N', 'ownN': 10, 'effN': 148.3, 'cvErr': 201.2},
            31: {'exit_target': 8, 'ev': 8.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 10, 'effN': 151.1, 'cvErr': 185.9},
            32: {'exit_target': 67, 'ev': 12.0, 'hit': 44.44, 'basis': 'own-N', 'ownN': 9, 'effN': 160.8, 'cvErr': 9.5},
            33: {'exit_target': 43, 'ev': 21.286, 'hit': 71.43, 'basis': 'own-N', 'ownN': 14, 'effN': 133.8, 'cvErr': 133.3},
            34: {'exit_target': 63, 'ev': 5.964, 'hit': 28.66, 'basis': 'pooled', 'ownN': 12, 'effN': 144.6, 'cvErr': 202.3},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_CHALL', 'underdog', 35, 39): {  # TRADE band_exit=46
        'entry_lo': 35, 'entry_hi': 39,
        'dca_drop': 30, 'exit_target': 46,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            35: {'exit_target': 64, 'ev': 17.412, 'hit': 52.94, 'basis': 'own-N', 'ownN': 17, 'effN': 124.6, 'cvErr': 42.4},
            36: {'exit_target': 63, 'ev': 17.308, 'hit': 53.85, 'basis': 'own-N', 'ownN': 13, 'effN': 140.1, 'cvErr': 28.7},
            37: {'exit_target': 62, 'ev': 4.391, 'hit': 35.15, 'basis': 'pooled', 'ownN': 10, 'effN': 157.1, 'cvErr': 16.6},
            38: {'exit_target': 4, 'ev': 4.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 8, 'effN': 173.2, 'cvErr': 104.3},
            39: {'exit_target': 20, 'ev': 6.385, 'hit': 76.92, 'basis': 'own-N', 'ownN': 13, 'effN': 136.9, 'cvErr': 47.9},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
    ('WTA_CHALL', 'underdog', 40, 44): {  # TRADE band_exit=39
        'entry_lo': 40, 'entry_hi': 44,
        'dca_drop': 15, 'exit_target': 39,
        'entry_size': 40, 'dca_size': 20,
        'mode': 'underdog', 'maker_bid_offset': 0,
        'percent_exits': {
            40: {'exit_target': 51, 'ev': 16.875, 'hit': 62.5, 'basis': 'own-N', 'ownN': 8, 'effN': 171.1, 'cvErr': 60.3},
            41: {'exit_target': 49, 'ev': 7.0, 'hit': 53.33, 'basis': 'own-N', 'ownN': 15, 'effN': 124.0, 'cvErr': 5.2},
            42: {'exit_target': 57, 'ev': 28.714, 'hit': 71.43, 'basis': 'own-N', 'ownN': 7, 'effN': 180.4, 'cvErr': 224.2},
            43: {'exit_target': 49, 'ev': 1.435, 'hit': 47.99, 'basis': 'pooled', 'ownN': 8, 'effN': 167.3, 'cvErr': 169.2},
            44: {'exit_target': 3, 'ev': 3.0, 'hit': 100.0, 'basis': 'own-N', 'ownN': 13, 'effN': 128.4, 'cvErr': 6.1},
        },
        'source': 'v3_pooled_blend_percent_2026-05-29',
    },
}


LEADER_TIERS_V5 = [(55, 59), (60, 64), (65, 69), (70, 74), (75, 79), (80, 84), (85, 89)]
UNDERDOG_TIERS_V5 = [(10, 14), (15, 19), (20, 24), (25, 29), (30, 34), (35, 39), (40, 44)]


def get_strategy(category, side, entry_price):
    """Resolve the band, then specialize to the ENTRY CENT's own exit.

    Returns a cell dict whose exit_target is the per-cent value for entry_price
    (every cent is its own cent). Returns None if the band is absent, the band
    is a full SKIP, or this specific cent is non-viable (percent_exits[cent]
    has exit_target None AND ev<=0). Drop-in for the version_b API.
    """
    tiers = LEADER_TIERS_V5 if side == 'leader' else UNDERDOG_TIERS_V5
    for lo, hi in tiers:
        if lo <= entry_price <= hi:
            cell = DEPLOYMENT.get((category, side, lo, hi))
            if cell is None or cell.get('entry_size', 0) == 0:
                return None
            pe = cell.get('percent_exits', {}).get(entry_price)
            if pe is None:
                return None
            # this cent is viable iff it has a positive-EV achievable read
            if (pe.get('ev') or 0) <= 0:
                return None  # cent-level SKIP even though the band trades
            out = dict(cell)
            out['exit_target'] = pe['exit_target']   # per-cent exit (None=hold)
            out['cent_ev'] = pe['ev']
            out['cent_hit'] = pe['hit']
            out['cent_basis'] = pe['basis']
            out['cent_ownN'] = pe['ownN']
            out['cent_effN'] = pe['effN']
            # in_sample_daily_pnl: dual-mode primary-side tiebreaker -> per-cent ev
            out['in_sample_daily_pnl'] = pe['ev']
            return out
    return None


def use_blended_target(category, direction, tier_lo, tier_hi):
    """Conservative FLOOR: always first-fill target (False). Blended-average
    auto-sell is a Part-2 entry-side enhancement; the floor never assumes it."""
    return False

