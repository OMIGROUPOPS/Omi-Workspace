# LOCKED_DOWN — gated_optima exit surface (the live per-cell exit table)

Sealed 2026-06-12 (C-EXIT-SEAL, Plex-countersigned). This directory is the
**live exit surface** read by `live_v4._load_exit_table` for all four enabled
categories AND (lookup-borrowed) the ITF_M/ITF_W visibility categories.

## 1. Identity

| File | sha256 |
|---|---|
| atp_main_adaptive_exit_bands.parquet | `d1a59020d475d015c2d30108f9925dc248acca06e91a74cead2fc4dc9e63bd27` |
| wta_main_adaptive_exit_bands.parquet | `94e9a4f2baf0ffe2cb08af10bd6e2e347d15e0a1afd519c048c49d5f9b86a60e` |
| atp_chall_adaptive_exit_bands.parquet | `3e6eb5a6e5706cec9a63e612a19812e57522fc1bdd620e165b85c5fb117f4a88` |
| wta_chall_adaptive_exit_bands.parquet | `3bd995b7328e0119a152c87073f06815096932879948c92862721f1f13a61258` |

- Config: `deploy_v5_live.json` → `"exit_table_dir": "data/durable/exit_surface_gated_optima/"`,
  `"exit_band_resolution": "gated_optima_validated_2026-06-01"`.
- Parquets authored at commit `b4311ba0` (2026-06-01 10:55 ET, DRAFT);
  config flipped live at commit `1775b453` (2026-06-01 14:21 ET, WHEN-FLAT).
- 2026-06-12 verification: all four VPS files byte-identical to the repo
  blobs at HEAD (sha-for-sha above).

## 2. Provenance

- **Solve method:** post-unity fill-realism gated optima — the exit-charts
  per-cell optimization with fill-realism gating applied after the unity
  correction; return-on-capital (`exp_ret/c`) as the primary deploy metric
  (exit-charts pipeline, see commit `a208c594`).
- **Input data (validated per-cell CSVs, `analysis/exit_charts/`):**
  - `deploy_gated_optima.csv` (ATP_MAIN) `9da0c3f6165050dde22edba1dd3af87cdb2d3ef7a3ec8fc882c4bfb81e12d2b8`
  - `deploy_gated_optima_WTA_MAIN.csv` `3fc8a3880fac1a2590094b6d36117f48271346361410a3772e1f68a69b086a46`
  - `deploy_gated_optima_ATP_CHALL.csv` `ee6377c5146caeae9c93701ee412b4ec7ecee06975222024218875e1dd532df9`
  - `deploy_gated_optima_WTA_CHALL.csv` `3416a87b8e64040f0a315a73e3870b5038905d8fee9a23c07bcfc92c644062c4`
- **Producing script:** `tools/build_validated_exit_parquets.py`
  (CSV(c,X) → one row per 1c cell, all-exit; loader-verified by
  `tools/test_validated_exit_table.py`, 32/32), commit `b4311ba0`.
- **Solve date:** 2026-06-01.

## 3. Validation

### Smoothness (analysis/exit_surface_smoothness.py, 2026-06-12 run)

```
=== exit_surface_gated_optima ===
ATP_MAIN   PASS  cells=90  maxD=15 medD=1  steps>1c=14  jumps>5c=1  HOLDs=0
           (all 14 steps NAMED structural; the single >5c step is the
            deep-favorite regime turnover cell 55(X=14) -> 56(X=29))
WTA_MAIN   PASS  cells=90  maxD=1  medD=0  steps>1c=0   jumps>5c=0  HOLDs=0
ATP_CHALL  PASS  cells=90  maxD=1  medD=0  steps>1c=0   jumps>5c=0  HOLDs=0
WTA_CHALL  PASS  cells=90  maxD=1  medD=0  steps>1c=0   jumps>5c=0  HOLDs=0
SURFACE VERDICT: PASS
```

### Live verification (2026-06-12, every exit posted today)

| Leg | Cat | Fill cell | Table X | Posted exit | Match |
|---|---|---|---|---|---|
| Zeynep Sonmez | WTA_MAIN | 50 | +13 | 63 | ✓ |
| Tomas Daniel | ATP_CHALL | 34 | +8 | 42 | ✓ |
| R. Carballes Baena | ATP_CHALL | 66 | +19 | 85 | ✓ |
| Donna Vekic | WTA_MAIN | 49 | +12 | 61 | ✓ |
| Daniil Medvedev | ATP_MAIN | 35 | +8 | 43 | ✓ |
| Harmony Tan | WTA_CHALL | 40 | +7 | 47 | ✓ |
| Celine Naef | WTA_CHALL | 62 | +14 | 76 | ✓ |
| Ben Shelton | ATP_MAIN | 89 | +10 | 98 | ✓ (99 capped at EXIT_PRICE_CAP 98) |
| Kamilla Rakhimova | WTA_MAIN | 20 | +6 | 26 | ✓ |
| Emma Raducanu (manual adoption) | WTA_MAIN | 77 | +19 | **96** | ✓ |

### Anomaly status — RESOLVED, no shape

The reported "Raducanu exit 84 (+7)" anomaly does not exist on the exchange
or in the journal: `v4_exit_posted 15:23:41 ET = exit_price 96, band_x 19,
cell_id 77, order d3b7cda5` — exactly this table. The 84/+7 figure was a
**reporting error in the session chat** (an unverified inference from a test
stub constant), not data drift (shape 1: shas identical), not a wrong
artifact (shape 2: config verified), not foreign-adoption divergence
(shape 3: the adoption path calls the same `exit_rule_for`), not cell
misclassification (shape 4: cell_id 77 = avg 77). No code or data fix
required; the exit rests at 96; no re-post decision needed.

## 4. Supersession

This surface **replaces** the spike-map adaptive surface
(`data/durable/spike_volatility_map/`), which **failed smoothness
catastrophically** (2026-06-12 gate run on the deployed copies: maxΔ up to
57c, 19–42 unnamed >5c jumps per category, HOLD cells present; repo and VPS
copies of that directory have additionally drifted apart historically). The
spike map remains on disk as the named rollback only and carries a
`SUPERSEDED.md` marker; rollback, if ever, must re-pull from repo blobs and
re-clear the smoothness gate.

## 5. Change protocol (the smoothness gate)

Any candidate replacement surface MUST, before a config flip:
1. clear `analysis/exit_surface_smoothness.py`: **zero HOLD cells, zero
   adjacent steps >1c outside the NAMED_STEPS allowlist** (a new structural
   step requires amending the allowlist by name, with rationale, in the same
   review);
2. be sha-pinned (per-file sha256 quoted in the deploy commit, repo blob ==
   deployed file);
3. operator + Plex countersign; config flip WHEN FLAT per the standing
   deploy checklist.
