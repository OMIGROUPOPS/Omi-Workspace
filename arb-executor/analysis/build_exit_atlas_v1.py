#!/usr/bin/env python3
"""
ATP_MAIN exit atlas v1 — descriptive multi-slice grid over (anchor cent c, target price T).

Single concern per slice; NO bands, NO clustering, NO optimizer picks. The atlas produces
every dimension at every (c,T). Picking R per cell is downstream and out of scope.

Coordinate system: c in 5..94 (90 cents) x T in 5..99 (95 targets). Cell (c,T) valid iff
T >= c+1 (T<c+1 -> NaN by construction). Per-row ceiling: row c only extends to T=99.

Foundation: data/durable/spike_volatility_map/atp_main_spike_perN.parquet, drop_reason.isna().
Read-only on the foundation. Hard gates must pass or artifacts go to _quarantine (no overwrite).
"""
import os, sys, json, hashlib, subprocess, datetime, shutil
import numpy as np
import pandas as pd

ROOT      = "/root/Omi-Workspace/arb-executor"
SRC       = os.path.join(ROOT, "data/durable/spike_volatility_map/atp_main_spike_perN.parquet")
OUT_DIR   = os.path.join(ROOT, "data/durable/exit_atlas_v1")
QUAR_DIR  = os.path.join(ROOT, "data/durable/_quarantine")
SIGMA     = 1.0
NB        = 100
CENTS     = np.arange(5, 95)      # 5..94  (90)
TARGETS   = np.arange(5, 100)     # 5..99  (95)
NC, NT    = len(CENTS), len(TARGETS)
REG_TARGET = 1910.20              # G6 regression target (sigma=1 picker, verified)
CELLBASIS_SPOT = (38, 70, -1.96)  # operator local check for ev_full_cell_basis
t0 = datetime.datetime.now()

# ============================ A. load + derive =============================
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

input_sha = sha256(SRC)
df = pd.read_parquet(SRC)
n_total = len(df)
df = df[df["drop_reason"].isna()].copy()
M = len(df)
a  = np.rint(df["anchor_price"].to_numpy() * 100).astype(int)
pk = np.rint(df["raw_max"].to_numpy()      * 100).astype(int)
st = df["settlement_value"].to_numpy().astype(int)
win = (st == 1)
loss = (st == 0)
h  = np.where(win, 99 - a, 1 - a).astype(float)   # per-N hold-to-settlement PnL (own basis)
m  = pk - a                                        # per-N achieved offset
mm = np.clip(m, 0, NB - 1)
print(f"[A] foundation rows total={n_total} kept(drop_reason.isna)={M}")
print(f"    anchor cents {a.min()}..{a.max()}  peak cents {pk.min()}..{pk.max()}  win={win.sum()} loss={loss.sum()}")

# ============================ weights / masks ==============================
diff = a[None, :] - CENTS[:, None]                 # (NC, M)
W = np.exp(-0.5 * (diff / SIGMA) ** 2)             # gaussian neighborhood weights
Wtot = W.sum(axis=1)                               # (NC,) == effN
reach_ind = (pk[:, None] >= TARGETS[None, :])      # (M, NT) bool: peak reached T
miss_ind = ~reach_ind

# validity mask: True where cell invalid (T < c+1) -> NaN
invalid = TARGETS[None, :] < (CENTS[:, None] + 1)  # (NC, NT)

def nanmask(mat):
    out = mat.astype(float).copy()
    out[invalid] = np.nan
    return out

# ============================ row-level dims ===============================
onehot = (a[None, :] == CENTS[:, None]).astype(float)   # (NC, M)
ownN = onehot.sum(axis=1).astype(int)
wins_row = (onehot * win[None, :]).sum(axis=1).astype(int)
effN = Wtot
win_rate_nbhd = (W * st[None, :]).sum(axis=1) / Wtot
breakeven_floor_R = np.ceil(0.05 * (CENTS - 1) / 0.95).astype(int)
ceiling_max_R = (99 - CENTS).astype(int)
pp = {q: np.full(NC, np.nan) for q in (25, 50, 75, 90)}
for k, c in enumerate(CENTS):
    pkown = pk[a == c]
    if pkown.size:
        for q in (25, 50, 75, 90):
            pp[q][k] = np.percentile(pkown, q)

# ============================ matrix slices ================================
# 1. raw_reach (own-cell)
with np.errstate(invalid="ignore", divide="ignore"):
    raw_reach = (onehot @ reach_ind) / ownN[:, None]
raw_reach[ownN == 0, :] = np.nan
raw_reach = nanmask(raw_reach)

# 2/3. win/loss conditional reach (own-cell, subset by settlement)
oh_win  = (onehot * win[None, :])
oh_loss = (onehot * loss[None, :])
cnt_win, cnt_loss = oh_win.sum(axis=1), oh_loss.sum(axis=1)
with np.errstate(invalid="ignore", divide="ignore"):
    win_cond  = (oh_win  @ reach_ind) / cnt_win[:, None]
    loss_cond = (oh_loss @ reach_ind) / cnt_loss[:, None]
win_cond[cnt_win == 0, :]   = np.nan
loss_cond[cnt_loss == 0, :] = np.nan
win_cond, loss_cond = nanmask(win_cond), nanmask(loss_cond)

# 4. neighborhood_reach (sigma=1 gaussian-weighted, absolute T)
nbhd_reach = (W @ reach_ind) / Wtot[:, None]
nbhd_reach = nanmask(nbhd_reach)

# 8a. ev_full_cell_basis (CANONICAL, absolute-T): PnL from cost basis c
Wwin_miss  = (W * win[None, :])  @ miss_ind
Wloss_miss = (W * loss[None, :]) @ miss_ind
TminusC = (TARGETS[None, :] - CENTS[:, None]).astype(float)
ev_cell = (TminusC * (W @ reach_ind) / Wtot[:, None]
           + ((99 - CENTS)[:, None] * Wwin_miss + (1 - CENTS)[:, None] * Wloss_miss) / Wtot[:, None])
ev_cell = nanmask(ev_cell)

# 9. ev_bounce_only: (T-c)*nbhd_reach - (c-1)*(1-nbhd_reach)
nr_raw = (W @ reach_ind) / Wtot[:, None]
ev_bounce = TminusC * nr_raw - (CENTS[:, None] - 1) * (1 - nr_raw)
ev_bounce = nanmask(ev_bounce)

# 8b. ev_full_own_basis (DIAGNOSTIC, anchor-relative offset X=T-c) + G6 regression
ev_own = np.full((NC, NT), np.nan)
reg_dollars = 0.0
reg_rows = []
for k, c in enumerate(CENTS):
    w = W[k]
    Wtotk = Wtot[k]
    hw = w * h
    Hwtotk = hw.sum()
    wc  = np.bincount(mm, weights=w,  minlength=NB)
    hwc = np.bincount(mm, weights=hw, minlength=NB)
    revW  = np.cumsum(wc[::-1])[::-1]
    revHW = np.cumsum(hwc[::-1])[::-1]
    Xmax = 99 - c
    Xs = np.arange(1, Xmax + 1)
    score = (Xs * revW[Xs] + (Hwtotk - revHW[Xs])) / Wtotk        # == picker score(X)
    # place into matrix at T = c + X
    Tcols = (c + Xs) - TARGETS[0]
    ev_own[k, Tcols] = score
    # --- G6 regression pick (replicate picker exactly: HOLD last -> earliest X wins ties) ---
    hold_score = Hwtotk / Wtotk
    all_scores = np.append(score, hold_score)
    idx = int(np.argmax(all_scores))
    if idx == len(score):
        R = "HOLD"; realized_own = h[a == c]
    else:
        R = int(Xs[idx]); mo = m[a == c]; ho = h[a == c]
        realized_own = np.where(mo >= R, float(R), ho)
    dol = float(realized_own.sum() * 10 / 100.0) if (a == c).sum() else 0.0
    reg_dollars += dol
    reg_rows.append((int(c), R, dol))
ev_own = nanmask(ev_own)

# ============================ assemble tables ==============================
CC, TT = np.meshgrid(CENTS, TARGETS, indexing="ij")
atlas = pd.DataFrame({
    "c": CC.ravel(), "T": TT.ravel(),
    "raw_reach": raw_reach.ravel(),
    "win_cond_reach": win_cond.ravel(),
    "loss_cond_reach": loss_cond.ravel(),
    "neighborhood_reach": nbhd_reach.ravel(),
    "ev_full_cell_basis": ev_cell.ravel(),
    "ev_full_own_basis": ev_own.ravel(),
    "ev_bounce_only": ev_bounce.ravel(),
    "time_to_peak": np.full(CC.size, np.nan),     # slice 10 skipped
})
row_dims = pd.DataFrame({
    "c": CENTS, "ownN": ownN, "effN": np.round(effN, 4), "wins": wins_row,
    "win_rate_neighborhood": np.round(win_rate_nbhd, 4),
    "breakeven_floor_R": breakeven_floor_R, "ceiling_max_R": ceiling_max_R,
    "peak_p25": pp[25], "peak_p50": pp[50], "peak_p75": pp[75], "peak_p90": pp[90],
    "drift_signature": np.full(NC, np.nan),       # slice 13 skipped
})

# ============================ validation gates =============================
gates = []   # (id, desc, hard, passed, detail)
def add(gid, desc, hard, passed, detail):
    gates.append((gid, desc, hard, bool(passed), detail))

# G1 shape
g1 = (atlas.shape[0] == NC * NT) and (row_dims.shape[0] == NC)
add("G1", "atlas 90x95 (8550 rows) + row_dims 90 rows", True, g1,
    f"atlas={atlas.shape[0]} (exp {NC*NT}), row_dims={row_dims.shape[0]} (exp {NC})")

# G2 ceiling-aware NaN: T<c+1 all-NaN in matrix slices; max T=99
slice_cols = ["raw_reach","win_cond_reach","loss_cond_reach","neighborhood_reach",
              "ev_full_cell_basis","ev_full_own_basis","ev_bounce_only"]
inv_rows = atlas[atlas["T"] < atlas["c"] + 1]
g2 = inv_rows[slice_cols].isna().all().all() and atlas["T"].max() == 99 and atlas["T"].min() == 5
add("G2", "T<c+1 cells NaN; no T>99 (ceiling-aware)", True, g2,
    f"invalid-cell non-NaN count={int((~inv_rows[slice_cols].isna()).sum().sum())}, Tmax={atlas['T'].max()}")

# G3 raw_reach[c,c+1] ~1.0 (soft, degenerate-aware)
edge = []
for k, c in enumerate(CENTS):
    if ownN[k] > 0 and c + 1 <= 99:
        edge.append((int(c), float(raw_reach[k, (c + 1) - TARGETS[0]])))
edge_vals = np.array([v for _, v in edge])
below = [(c, round(v, 3)) for c, v in edge if v < 0.999]
add("G3", "raw_reach[c,c+1] ~1.0 (SOFT, degenerate-aware)", False, True,
    f"min={edge_vals.min():.3f} mean={edge_vals.mean():.4f}; {len(below)} cells <1.0 (degenerate N): {below[:8]}")

# G4 monotone non-increasing reach within each row
viol4 = 0
for k, c in enumerate(CENTS):
    if ownN[k] == 0:
        continue
    r = raw_reach[k, (c + 1) - TARGETS[0]:]
    r = r[~np.isnan(r)]
    if r.size > 1 and np.any(np.diff(r) > 1e-9):
        viol4 += 1
add("G4", "raw_reach non-increasing in T per row", True, viol4 == 0, f"violating rows={viol4}")

# G5 win_cond_reach >= loss_cond_reach where both defined (soft, flag)
both = (~np.isnan(win_cond)) & (~np.isnan(loss_cond))
viol5_mask = both & (win_cond < loss_cond - 1e-9)
v5 = int(viol5_mask.sum())
ex5 = []
if v5:
    ii, jj = np.where(viol5_mask)
    for x, y in list(zip(ii, jj))[:8]:
        ex5.append((int(CENTS[x]), int(TARGETS[y]), round(float(win_cond[x, y]), 3), round(float(loss_cond[x, y]), 3)))
add("G5", "win_cond_reach >= loss_cond_reach (SOFT, flag)", False, True,
    f"violations={v5}/{int(both.sum())} cells; examples (c,T,win,loss)={ex5}")

# G6 regression vs sigma=1 picker $1910.20
g6 = abs(reg_dollars - REG_TARGET) <= 5.0
add("G6", f"ev_full_own_basis argmax reproduces ${REG_TARGET:.2f} +/-$5", True, g6,
    f"computed=${reg_dollars:.2f} delta=${reg_dollars - REG_TARGET:+.2f}")

# G7 breakeven floor sanity
g7 = (breakeven_floor_R[CENTS == 94][0] == 5) and (breakeven_floor_R[CENTS == 5][0] == 1)
add("G7", "breakeven_floor_R[94]==5, [5]==1", True, g7,
    f"R[94]={int(breakeven_floor_R[CENTS==94][0])}, R[5]={int(breakeven_floor_R[CENTS==5][0])}")

# G8 ceiling sanity
g8 = (ceiling_max_R[CENTS == 94][0] == 5) and (ceiling_max_R[CENTS == 5][0] == 94)
add("G8", "ceiling_max_R[94]==5, [5]==94", True, g8,
    f"max_R[94]={int(ceiling_max_R[CENTS==94][0])}, max_R[5]={int(ceiling_max_R[CENTS==5][0])}")

# cell_basis spot check (operator local value) — SOFT
sc_c, sc_t, sc_exp = CELLBASIS_SPOT
sc_val = float(ev_cell[(CENTS == sc_c), (TARGETS == sc_t)][0])
sc_ok = abs(sc_val - sc_exp) <= 0.05
add("SPOT", f"ev_full_cell_basis[{sc_c},{sc_t}]=={sc_exp} (SOFT)", False, sc_ok,
    f"computed={sc_val:.4f} (expected {sc_exp}, delta {sc_val - sc_exp:+.4f})")

hard_pass = all(p for _, _, hard, p, _ in gates if hard)

# ============================ git / meta ===================================
def git(*args):
    try:
        return subprocess.check_output(["git", "-C", ROOT, *args], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return None
producer_commit = git("rev-parse", "HEAD")

# ============================ write (quarantine on fail) ===================
if hard_pass:
    target_dir = OUT_DIR
    os.makedirs(target_dir, exist_ok=True)
    status = "PASS"
else:
    stamp = t0.strftime("%Y%m%dT%H%M%S")
    target_dir = os.path.join(QUAR_DIR, f"exit_atlas_v1_FAILED_{stamp}")
    os.makedirs(target_dir, exist_ok=True)
    status = "QUARANTINED"

atlas.to_parquet(os.path.join(target_dir, "atp_main_atlas.parquet"), index=False)
row_dims.to_parquet(os.path.join(target_dir, "atp_main_row_dims.parquet"), index=False)

runtime_s = (datetime.datetime.now() - t0).total_seconds()
meta = {
    "producer": "build_exit_atlas_v1.py",
    "producer_commit_at_run": producer_commit,
    "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "status": status,
    "runtime_seconds": round(runtime_s, 2),
    "input": {"path": os.path.relpath(SRC, ROOT), "sha256": input_sha,
              "rows_total": int(n_total), "rows_kept": int(M)},
    "coordinate_system": {"cents": "5..94 (90)", "targets": "5..99 (95)",
                          "valid_cell": "T>=c+1", "ceiling": "T<=99 per row"},
    "sigma": SIGMA,
    "slice_row_counts": {
        "atlas_rows": int(atlas.shape[0]),
        "atlas_valid_cells": int((atlas["T"] >= atlas["c"] + 1).sum()),
        "row_dims_rows": int(row_dims.shape[0]),
        "neighborhood_reach_defined": int((~atlas["neighborhood_reach"].isna()).sum()),
        "raw_reach_defined": int((~atlas["raw_reach"].isna()).sum()),
        "win_cond_defined": int((~atlas["win_cond_reach"].isna()).sum()),
        "loss_cond_defined": int((~atlas["loss_cond_reach"].isna()).sum()),
    },
    "ev_full_flavors": {
        "ev_full_cell_basis": "CANONICAL — absolute-T, PnL from cost basis c; coherent with reach slices; forward deployment view",
        "ev_full_own_basis": "DIAGNOSTIC — anchor-relative offset X=T-c, PnL from each N's own anchor; backward attribution; reproduces sigma=1 picker",
    },
    "skipped_slices": {
        "time_to_peak (slice 10)": "spike_perN lacks per-T first-reach timing (only time_to_max_min=time-to-single-peak); per_minute_universe sub-build deferred to atlas_v2",
        "drift_signature (slice 13)": "premarket entry-side signal; deferred to entry_atlas_v1; out of scope for exit-only v1",
    },
    "gates": [{"id": g, "desc": d, "hard": hd, "passed": p, "detail": dt} for g, d, hd, p, dt in gates],
    "hard_gates_pass": bool(hard_pass),
    "regression_dollars": round(reg_dollars, 2),
}
with open(os.path.join(target_dir, "meta.json"), "w") as f:
    json.dump(meta, f, indent=2)

# ============================ validation_report.md =========================
def fmt(x, p=3):
    return "NaN" if (x is None or (isinstance(x, float) and np.isnan(x))) else f"{x:.{p}f}"

lines = []
lines.append(f"# ATP_MAIN Exit Atlas v1 — Validation Report\n")
lines.append(f"- status: **{status}**  | hard gates pass: **{hard_pass}**")
lines.append(f"- generated: {meta['generated_utc']}  | runtime: {runtime_s:.2f}s")
lines.append(f"- input sha256: `{input_sha}`  | rows kept: {M}/{n_total}")
lines.append(f"- producer commit at run: `{producer_commit}`\n")
lines.append("## Gate table\n")
lines.append("| gate | hard | result | detail |")
lines.append("|------|------|--------|--------|")
for g, d, hd, p, dt in gates:
    lines.append(f"| {g} {d} | {'yes' if hd else 'soft'} | {'PASS' if p else 'FAIL'} | {dt} |")
lines.append("\n## Skipped slices\n")
for k, v in meta["skipped_slices"].items():
    lines.append(f"- **{k}**: {v}")
lines.append("\n## Spot checks at cells 9, 38, 65, 85, 94\n")
for c in (9, 38, 65, 85, 94):
    k = int(np.where(CENTS == c)[0][0])
    lines.append(f"### cent c={c}")
    lines.append(f"- ownN={ownN[k]}  effN={effN[k]:.3f}  wins={wins_row[k]}  "
                 f"win_rate_nbhd={win_rate_nbhd[k]:.4f}  breakeven_floor_R={breakeven_floor_R[k]}  ceiling_max_R={ceiling_max_R[k]}")
    lines.append(f"- peak pctiles: p25={fmt(pp[25][k],1)} p50={fmt(pp[50][k],1)} p75={fmt(pp[75][k],1)} p90={fmt(pp[90][k],1)}")
    # own_basis argmax R for this cent
    rr = dict((cc, (R, dd)) for cc, R, dd in reg_rows)[c]
    lines.append(f"- own_basis picked R={rr[0]}  own-cell $@10ct={rr[1]:.2f}")
    lines.append(f"")
    lines.append(f"  | T | raw_reach | win_cond | loss_cond | nbhd_reach | ev_cell_basis | ev_own_basis | ev_bounce |")
    lines.append(f"  |---|-----------|----------|-----------|------------|---------------|--------------|-----------|")
    sample_T = [t for t in (c+1, c+3, c+5, c+10, min(c+20, 99), 99) if t <= 99]
    sample_T = sorted(set(sample_T))
    for t in sample_T:
        j = int(np.where(TARGETS == t)[0][0])
        lines.append(f"  | {t} | {fmt(raw_reach[k,j])} | {fmt(win_cond[k,j])} | {fmt(loss_cond[k,j])} | "
                     f"{fmt(nbhd_reach[k,j])} | {fmt(ev_cell[k,j],3)} | {fmt(ev_own[k,j],3)} | {fmt(ev_bounce[k,j],3)} |")
    lines.append("")
with open(os.path.join(target_dir, "validation_report.md"), "w") as f:
    f.write("\n".join(lines))

# ============================ console summary ==============================
print("\n" + "=" * 70)
print(f"EXIT ATLAS v1 — {status}  (hard gates pass={hard_pass})  runtime={runtime_s:.2f}s")
print("=" * 70)
print(f"{'gate':5} {'hard':5} {'res':5} detail")
for g, d, hd, p, dt in gates:
    print(f"{g:5} {'Y' if hd else 'soft':5} {'PASS' if p else 'FAIL':5} {d}")
    print(f"        -> {dt}")
print(f"\nG6 regression: ${reg_dollars:.2f} (target ${REG_TARGET:.2f}, delta ${reg_dollars-REG_TARGET:+.2f})")
print(f"cell_basis spot ev[{sc_c},{sc_t}]={sc_val:.4f} (expected {sc_exp})")
print(f"\nwrote -> {target_dir}")
print("  atp_main_atlas.parquet, atp_main_row_dims.parquet, meta.json, validation_report.md")

print("\n--- SPOT-CHECK TABLE (cells 9, 38, 65, 85, 94) ---")
print(f"{'c':>3} {'ownN':>5} {'effN':>8} {'winrt':>6} {'beR':>4} {'maxR':>5} {'p50':>5} {'p90':>5} {'ownR':>5} {'own$':>8}")
regd = dict((cc, (R, dd)) for cc, R, dd in reg_rows)
for c in (9, 38, 65, 85, 94):
    k = int(np.where(CENTS == c)[0][0])
    R, dd = regd[c]
    print(f"{c:>3} {ownN[k]:>5} {effN[k]:>8.2f} {win_rate_nbhd[k]:>6.3f} {breakeven_floor_R[k]:>4} "
          f"{ceiling_max_R[k]:>5} {fmt(pp[50][k],0):>5} {fmt(pp[90][k],0):>5} {str(R):>5} {dd:>8.2f}")
print("\nDONE." if hard_pass else "\nHARD GATE FAILURE — artifacts quarantined, v1 dir untouched.")
sys.exit(0 if hard_pass else 1)
