# ATP_MAIN Exit Atlas v1 — Validation Report

- status: **PASS**  | hard gates pass: **True**
- generated: 2026-05-28T21:45:45.449424+00:00  | runtime: 1.50s
- input sha256: `621c86340b90653e384720b1f10c4617f9fbd64d5f177cbfab0d2153c9ea960f`  | rows kept: 4137/4137
- producer commit at run: `83ef84ce0bcea645b5e9bc891f8569968869dd68`

## Gate table

| gate | hard | result | detail |
|------|------|--------|--------|
| G1 atlas 90x95 (8550 rows) + row_dims 90 rows | yes | PASS | atlas=8550 (exp 8550), row_dims=90 (exp 90) |
| G2 T<c+1 cells NaN; no T>99 (ceiling-aware) | yes | PASS | invalid-cell non-NaN count=0, Tmax=99 |
| G3 raw_reach[c,c+1] ~1.0 (SOFT, degenerate-aware) | soft | PASS | min=0.885 mean=0.9821; 47 cells <1.0 (degenerate N): [(6, 0.96), (10, 0.935), (11, 0.964), (15, 0.958), (16, 0.9), (17, 0.95), (19, 0.967), (20, 0.971)] |
| G4 raw_reach non-increasing in T per row | yes | PASS | violating rows=0 |
| G5 win_cond_reach >= loss_cond_reach (SOFT, flag) | soft | PASS | violations=0/4273 cells; examples (c,T,win,loss)=[] |
| G6 ev_full_own_basis argmax reproduces $1910.20 +/-$5 | yes | PASS | computed=$1910.20 delta=$-0.00 |
| G7 breakeven_floor_R[94]==5, [5]==1 | yes | PASS | R[94]=5, R[5]=1 |
| G8 ceiling_max_R[94]==5, [5]==94 | yes | PASS | max_R[94]=5, max_R[5]=94 |
| SPOT ev_full_cell_basis[38,70]==-1.96 (SOFT) | soft | PASS | computed=-1.9605 (expected -1.96, delta -0.0005) |

## Skipped slices

- **time_to_peak (slice 10)**: spike_perN lacks per-T first-reach timing (only time_to_max_min=time-to-single-peak); per_minute_universe sub-build deferred to atlas_v2
- **drift_signature (slice 13)**: premarket entry-side signal; deferred to entry_atlas_v1; out of scope for exit-only v1

## Spot checks at cells 9, 38, 65, 85, 94

### cent c=9
- ownN=23  effN=60.554  wins=7  win_rate_nbhd=0.1526  breakeven_floor_R=1  ceiling_max_R=90
- peak pctiles: p25=18.0 p50=39.0 p75=99.0 p90=99.0
- own_basis picked R=60  own-cell $@10ct=42.80

  | T | raw_reach | win_cond | loss_cond | nbhd_reach | ev_cell_basis | ev_own_basis | ev_bounce |
  |---|-----------|----------|-----------|------------|---------------|--------------|-----------|
  | 10 | 1.000 | 1.000 | 1.000 | 0.983 | 0.847 | 0.774 | 0.847 |
  | 12 | 0.913 | 1.000 | 0.875 | 0.865 | 1.514 | 1.136 | 1.514 |
  | 14 | 0.870 | 1.000 | 0.812 | 0.771 | 2.018 | 1.997 | 2.018 |
  | 19 | 0.652 | 1.000 | 0.500 | 0.561 | 2.102 | 2.027 | 2.102 |
  | 29 | 0.565 | 1.000 | 0.375 | 0.419 | 3.733 | 3.498 | 3.733 |
  | 99 | 0.304 | 1.000 | 0.000 | 0.153 | 6.951 | 6.775 | 6.951 |

### cent c=38
- ownN=64  effN=155.217  wins=15  win_rate_nbhd=0.2926  breakeven_floor_R=2  ceiling_max_R=61
- peak pctiles: p25=45.8 p50=59.0 p75=94.5 p90=99.0
- own_basis picked R=5  own-cell $@10ct=-10.00

  | T | raw_reach | win_cond | loss_cond | nbhd_reach | ev_cell_basis | ev_own_basis | ev_bounce |
  |---|-----------|----------|-----------|------------|---------------|--------------|-----------|
  | 39 | 0.969 | 1.000 | 0.959 | 0.986 | 0.463 | -0.022 | 0.463 |
  | 41 | 0.891 | 1.000 | 0.857 | 0.928 | 0.112 | -0.261 | 0.112 |
  | 43 | 0.844 | 1.000 | 0.796 | 0.882 | 0.040 | 0.027 | 0.040 |
  | 48 | 0.734 | 1.000 | 0.653 | 0.770 | -0.805 | -0.978 | -0.805 |
  | 58 | 0.578 | 1.000 | 0.449 | 0.613 | -2.050 | -1.856 | -2.050 |
  | 99 | 0.250 | 0.933 | 0.041 | 0.308 | -6.190 | -6.742 | -6.822 |

### cent c=65
- ownN=79  effN=176.605  wins=49  win_rate_nbhd=0.6477  breakeven_floor_R=4  ceiling_max_R=34
- peak pctiles: p25=78.5 p50=99.0 p75=99.0 p90=99.0
- own_basis picked R=1  own-cell $@10ct=7.90

  | T | raw_reach | win_cond | loss_cond | nbhd_reach | ev_cell_basis | ev_own_basis | ev_bounce |
  |---|-----------|----------|-----------|------------|---------------|--------------|-----------|
  | 66 | 1.000 | 1.000 | 1.000 | 0.985 | 0.044 | 0.665 | 0.044 |
  | 68 | 0.924 | 1.000 | 0.800 | 0.941 | -0.979 | -0.704 | -0.979 |
  | 70 | 0.899 | 1.000 | 0.733 | 0.920 | -0.520 | -0.630 | -0.520 |
  | 75 | 0.848 | 1.000 | 0.600 | 0.874 | 0.674 | -0.444 | 0.674 |
  | 85 | 0.709 | 1.000 | 0.233 | 0.739 | -1.912 | -1.830 | -1.912 |
  | 99 | 0.620 | 1.000 | 0.000 | 0.654 | 0.463 | -0.047 | 0.052 |

### cent c=85
- ownN=32  effN=89.681  wins=30  win_rate_nbhd=0.8849  breakeven_floor_R=5  ceiling_max_R=14
- peak pctiles: p25=99.0 p50=99.0 p75=99.0 p90=99.0
- own_basis picked R=13  own-cell $@10ct=31.90

  | T | raw_reach | win_cond | loss_cond | nbhd_reach | ev_cell_basis | ev_own_basis | ev_bounce |
  |---|-----------|----------|-----------|------------|---------------|--------------|-----------|
  | 86 | 1.000 | 1.000 | 1.000 | 0.983 | -0.449 | -0.170 | -0.449 |
  | 88 | 1.000 | 1.000 | 1.000 | 0.968 | 0.208 | 0.797 | 0.208 |
  | 90 | 1.000 | 1.000 | 1.000 | 0.966 | 1.998 | 2.020 | 1.998 |
  | 95 | 0.969 | 1.000 | 0.500 | 0.924 | 2.895 | 2.299 | 2.895 |
  | 99 | 0.938 | 1.000 | 0.000 | 0.902 | 4.356 | 3.582 | 4.356 |

### cent c=94
- ownN=21  effN=41.018  wins=20  win_rate_nbhd=0.8830  breakeven_floor_R=5  ceiling_max_R=5
- peak pctiles: p25=99.0 p50=99.0 p75=99.0 p90=99.0
- own_basis picked R=1  own-cell $@10ct=2.10

  | T | raw_reach | win_cond | loss_cond | nbhd_reach | ev_cell_basis | ev_own_basis | ev_bounce |
  |---|-----------|----------|-----------|------------|---------------|--------------|-----------|
  | 95 | 1.000 | 1.000 | 1.000 | 0.985 | -0.391 | 1.000 | -0.391 |
  | 97 | 1.000 | 1.000 | 1.000 | 0.941 | -2.705 | 0.190 | -2.705 |
  | 99 | 1.000 | 1.000 | 1.000 | 0.922 | -2.623 | -0.738 | -2.623 |
