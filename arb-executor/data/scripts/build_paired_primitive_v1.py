#!/usr/bin/env python3
"""
build_paired_primitive_v1.py — ATP_MAIN paired-event primitive emitter.

Single concern: emit the irreducible paired-event primitive from Druid's
Foundational (per_minute_features). One row per paired ATP_MAIN event where
BOTH legs are anchored at T-20m, both in the F35 live-era cohort, and both
have in-match forward tape to settlement.

NO bands, NO R sweep, NO fee model, NO analysis. The irreducible data only.

Path A (re-calibrated from halted run ec7cdae): halt thresholds tuned to the
F35 tier-1/2 live-era cohort itself, not the spike per-N universe. The cohort
is event-symmetric and pairs at ~100% by construction, so PROBE 1 is a
floor-only check (>= 95%), and PROBE 2's floor is 500 (cohort yields ~663
paired events). See PAIRING_DIAGNOSTIC.md for the spike per-N (~85.5%) numbers
that the prior [80,92] band came from.

Discipline: C37 pre-replace gate, C28 streaming/column-projected, D11 probe
before full run, G21 ET on operator surfaces, G23 honest provenance,
C20 event-grain check.
"""
from __future__ import annotations
import os, sys, json, time, hashlib, gc, random
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.dataset as ds
import pyarrow.compute as pc

ET = ZoneInfo("America/New_York")
BASE = Path("/root/Omi-Workspace/arb-executor")
PMF = BASE / "data/durable/per_minute_universe/per_minute_features.parquet"
NPROF = BASE / "data/durable/n_profile_v1/n_profile.parquet"
OUTDIR = BASE / "data/durable/paired_primitive_v1/atp_main"
HALT_LOG = OUTDIR / "halt_log.md"
RUN_SUMMARY = OUTDIR / "run_summary.json"
PRIMITIVE = OUTDIR / "primitive.parquet"

EXPECTED_SHA = {
    "per_minute_features.parquet": "9fde4b5d30e56d99efa0637fe042cb6ca4505274e85e42769b4cedc25e3e5ff4",
    "n_profile.parquet":           "a7ed11550e8226f18c22069cc5937d35b184e7f0d2a9264435604a0270c1837e",
}

# probe halt thresholds (path A — calibrated to F35 live-era cohort)
PAIR_FLOOR = 95.0         # floor-only; cohort is event-symmetric, pairs ~100%
P2_MIN_EVENTS = 500       # cohort yields ~663 paired events
T20_LO, T20_HI = 18.0, 22.0
SETTLE_TAIL_S = 300       # in-match window ends at settlement_ts - 300s
GAP_MAX_S = 3600          # > 60 min gap in in-match window = broken tape
SPIKE_PERN_PAIR_PCT = 85.52   # reference: PAIRING_DIAGNOSTIC spike per-N universe


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def now_stamps():
    u = datetime.now(timezone.utc)
    return u.strftime("%Y-%m-%d %H:%M:%S UTC"), u.astimezone(ET).strftime("%Y-%m-%d %H:%M:%S ET")


def git_head() -> str:
    import subprocess
    return subprocess.check_output(["git", "-C", str(BASE), "rev-parse", "HEAD"]).decode().strip()


def select_cohort():
    """F35-reliable tier-1/2 live-era ATP_MAIN cohort — same screen as
    inmatch_bounce_surface_v1 / atlas select_cohort()."""
    t = pq.read_table(NPROF, columns=[
        "ticker", "category", "match_start_method", "tier", "total_volume_in_match"])
    import pandas as pd
    df = t.to_pandas()
    coh = df[
        (df["category"] == "ATP_MAIN")
        & (df["match_start_method"].isin(["both_sides_price_discovery", "both_sides_trade_density"]))
        & (df["tier"] == "live")
        & (df["total_volume_in_match"] > 0)
    ]["ticker"].tolist()
    return sorted(set(coh))


def load_tape(cohort_tickers):
    """Column-projected, ticker-pushdown load of per_minute tape for the cohort.
    C28: never load full columns into pandas; filter to cohort first."""
    cols = ["ticker", "minute_ts", "time_to_match_start_min",
            "yes_ask_close", "yes_bid_close",
            "match_start_ts", "settlement_ts", "settlement_value"]
    dataset = ds.dataset(PMF, format="parquet")
    tbl = dataset.to_table(
        columns=cols,
        filter=pc.field("ticker").isin(pa.array(cohort_tickers)))
    return tbl


def event_of(ticker: str) -> str:
    return ticker.rsplit("-", 1)[0]


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    phase_t = {}
    t0 = time.time()

    # ---- input sha256 verification (two real inputs only; descriptive_1c
    #      dropped — it is cell-level, no per-ticker settlement) ----
    sha = {p.name: sha256_file(p) for p in (PMF, NPROF)}
    sha_ok = {}
    for name, exp in EXPECTED_SHA.items():
        got = sha[name]
        sha_ok[name] = got == exp
        if not sha_ok[name]:
            print(f"!! sha mismatch {name}: got {got[:12]} expected {exp[:12]}")
    phase_t["sha256_inputs_s"] = round(time.time() - t0, 2)

    # ---- cohort ----
    tc = time.time()
    cohort = select_cohort()
    phase_t["cohort_screen_s"] = round(time.time() - tc, 2)

    # ---- load tape ----
    tl = time.time()
    tbl = load_tape(cohort)
    import pandas as pd
    tape = tbl.to_pandas()
    phase_t["load_tape_s"] = round(time.time() - tl, 2)
    del tbl
    gc.collect()

    # group by ticker
    tape = tape.sort_values(["ticker", "minute_ts"])
    by_ticker = {tk: g for tk, g in tape.groupby("ticker", sort=False)}

    # ---- PROBE 1: pairing ----
    tp = time.time()
    ev_legs = {}
    for tk in cohort:
        ev_legs.setdefault(event_of(tk), []).append(tk)
    total_events = len(ev_legs)
    paired_ev = {e: ls for e, ls in ev_legs.items() if len(ls) == 2}
    singleton_ev = {e: ls for e, ls in ev_legs.items() if len(ls) == 1}
    over_ev = {e: ls for e, ls in ev_legs.items() if len(ls) > 2}
    pairing_rate = 100.0 * len(paired_ev) / total_events if total_events else 0.0
    probe1 = {
        "cohort_tickers": len(cohort),
        "total_events": total_events,
        "paired_events": len(paired_ev),
        "singleton_events": len(singleton_ev),
        "over_paired_events": len(over_ev),
        "pairing_rate_pct": round(pairing_rate, 2),
        "halt_floor_pct": PAIR_FLOOR,
        "spike_perN_reference_pct": SPIKE_PERN_PAIR_PCT,
        "halt_triggered": (pairing_rate < PAIR_FLOOR),
    }
    phase_t["probe1_pairing_s"] = round(time.time() - tp, 2)

    # ---- PROBE 2: T-20m coverage per leg ----
    tp = time.time()
    def t20_minute(g):
        """Return (idx, ttms) of minute with ttms closest to +20 within [18,22], else None."""
        m = g[(g["time_to_match_start_min"] >= T20_LO) & (g["time_to_match_start_min"] <= T20_HI)]
        if len(m) == 0:
            return None
        j = (m["time_to_match_start_min"] - 20.0).abs().idxmin()
        return j, float(m.loc[j, "time_to_match_start_min"])

    both_obs = []     # events where both legs T-20m observable
    one_obs = 0
    neither_obs = 0
    leg_t20 = {}      # ticker -> (idx, ttms)
    for e, ls in paired_ev.items():
        flags = []
        for tk in ls:
            g = by_ticker.get(tk)
            res = t20_minute(g) if g is not None else None
            if res is not None:
                leg_t20[tk] = res
            flags.append(res is not None)
        n_ok = sum(flags)
        if n_ok == 2:
            both_obs.append(e)
        elif n_ok == 1:
            one_obs += 1
        else:
            neither_obs += 1
    probe2 = {
        "paired_events_in": len(paired_ev),
        "both_legs_t20_observable": len(both_obs),
        "one_leg_only": one_obs,
        "neither_leg": neither_obs,
        "t20_window": [T20_LO, T20_HI],
        "halt_min_events": P2_MIN_EVENTS,
        "halt_triggered": len(both_obs) < P2_MIN_EVENTS,
    }
    phase_t["probe2_t20_s"] = round(time.time() - tp, 2)

    # ---- PROBE 3: in-match forward tape coverage per leg ----
    tp = time.time()
    def inmatch_ok(g):
        """settlement_value populated, match_start_ts present, in-match window
        has rows and no gap > GAP_MAX_S. Returns (ok, info)."""
        sv = g["settlement_value"].dropna()
        ms = g["match_start_ts"].dropna()
        st = g["settlement_ts"].dropna()
        if len(sv) == 0 or len(ms) == 0 or len(st) == 0:
            return False, None
        msv = int(ms.iloc[0]); stv = int(st.iloc[0])
        win = g[(g["minute_ts"] >= msv) & (g["minute_ts"] <= stv - SETTLE_TAIL_S)]
        if len(win) == 0:
            return False, None
        mt = win["minute_ts"].values
        max_gap = int((mt[1:] - mt[:-1]).max()) if len(mt) > 1 else 0
        if max_gap > GAP_MAX_S:
            return False, {"max_gap_s": max_gap}
        return True, {"match_start_ts": msv, "settlement_ts": stv,
                      "settle_value": float(sv.iloc[-1]), "max_gap_s": max_gap,
                      "win_rows": len(win)}

    p3_events = []
    p3_info = {}
    for e in both_obs:
        ls = paired_ev[e]
        oks = []
        for tk in ls:
            ok, info = inmatch_ok(by_ticker[tk])
            oks.append(ok)
            p3_info[tk] = info
        if all(oks):
            p3_events.append(e)
    drop_p2_p3 = (len(both_obs) - len(p3_events))
    drop_pct = (100.0 * drop_p2_p3 / len(both_obs)) if both_obs else 0.0
    probe3 = {
        "both_t20_in": len(both_obs),
        "both_legs_inmatch_tape_ok": len(p3_events),
        "dropped": drop_p2_p3,
        "drop_pct_from_probe2": round(drop_pct, 2),
        "severe_loss_flag": drop_pct > 20.0,
    }
    phase_t["probe3_inmatch_s"] = round(time.time() - tp, 2)

    # ---- PROBE 4: inversion structure sanity ----
    tp = time.time()
    import statistics as st
    sums = []
    off3 = 0
    for e in p3_events:
        ls = paired_ev[e]
        anchors = []
        for tk in ls:
            idx, _ = leg_t20[tk]
            anchors.append(round(float(by_ticker[tk].loc[idx, "yes_ask_close"]) * 100))
        s = sum(anchors)
        sums.append(s)
        if abs(s - 100) > 3:
            off3 += 1
    def pctl(a, q):
        if not a:
            return None
        a = sorted(a); k = (len(a) - 1) * q
        f = int(k); c = min(f + 1, len(a) - 1)
        return round(a[f] + (a[c] - a[f]) * (k - f), 2)
    probe4 = {
        "n": len(sums),
        "mean": round(st.mean(sums), 2) if sums else None,
        "median": round(st.median(sums), 2) if sums else None,
        "std": round(st.pstdev(sums), 2) if len(sums) > 1 else 0.0,
        "p10": pctl(sums, 0.10), "p25": pctl(sums, 0.25),
        "p75": pctl(sums, 0.75), "p90": pctl(sums, 0.90),
        "count_off_gt_3c": off3,
        "pct_within_3c": round(100.0 * (len(sums) - off3) / len(sums), 2) if sums else None,
    }
    phase_t["probe4_inversion_s"] = round(time.time() - tp, 2)

    probes = {"probe1_pairing": probe1, "probe2_t20": probe2,
              "probe3_inmatch": probe3, "probe4_inversion": probe4}

    halt = probe1["halt_triggered"] or probe2["halt_triggered"]

    # peak mem
    try:
        import resource
        peak_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        peak_mb = round(peak_kb / 1024, 1)
    except Exception:
        peak_mb = None

    u_utc, u_et = now_stamps()
    head = git_head()

    base_summary = {
        "producer_commit_hash": head,
        "run_timestamp_utc": u_utc,
        "run_timestamp_et": u_et,
        "path": "A (F35 tier-1/2 live-era cohort; thresholds calibrated to this universe)",
        "input_sha256": sha,
        "input_sha256_expected_match": sha_ok,
        "cohort_definition": "ATP_MAIN F35 tier-1/2 live-era (match_start_method in {both_sides_*}, tier==live, total_volume_in_match>0)",
        "n_at_each_step": {
            "cohort_tickers": len(cohort),
            "total_events": total_events,
            "paired_events": len(paired_ev),
            "both_legs_t20_observable": len(both_obs),
            "both_legs_inmatch_tape_ok": len(p3_events),
        },
        "runtime_per_phase_s": phase_t,
        "total_runtime_s": round(time.time() - t0, 2),
        "peak_rss_mb": peak_mb,
        "probes": probes,
        "halted": halt,
    }

    if halt:
        write_halt_log(probes, base_summary, u_et, u_utc)
        with open(RUN_SUMMARY, "w") as f:
            json.dump({**base_summary, "output_sha256": None,
                       "primitive_rows": 0}, f, indent=2)
        print("HALT: probes triggered halt. See halt_log.md. No primitive emitted.")
        print(json.dumps(probes, indent=2))
        return 0

    # ---- PRIMITIVE EMISSION (only if no halt) ----
    rows = build_rows(p3_events, paired_ev, by_ticker, leg_t20)
    emit_primitive(rows)
    out_sha = sha256_file(PRIMITIVE)
    summary = {**base_summary, "output_sha256": out_sha, "primitive_rows": len(rows)}
    with open(RUN_SUMMARY, "w") as f:
        json.dump(summary, f, indent=2)
    write_handoff(probes, summary, rows, u_et, u_utc)
    print(f"DONE: primitive emitted, {len(rows)} rows, sha {out_sha[:12]}")
    return 0


def build_rows(p3_events, paired_ev, by_ticker, leg_t20):
    rows = []
    for e in p3_events:
        ls = paired_ev[e]
        legs = []
        for tk in ls:
            idx, ttms = leg_t20[tk]
            g = by_ticker[tk]
            anchor_d = float(g.loc[idx, "yes_ask_close"])
            ms = int(g["match_start_ts"].dropna().iloc[0])
            stt = int(g["settlement_ts"].dropna().iloc[0])
            sv = float(g["settlement_value"].dropna().iloc[-1])
            win = g[(g["minute_ts"] >= ms) & (g["minute_ts"] <= stt - SETTLE_TAIL_S)]
            jb = win["yes_bid_close"].idxmax()
            peak_bid_c = round(float(win.loc[jb, "yes_bid_close"]) * 100)
            peak_bid_ts = int(win.loc[jb, "minute_ts"])
            legs.append(dict(
                ticker=tk, anchor_d=anchor_d, anchor_c=round(anchor_d * 100),
                ttms=int(round(ttms)), peak_bid_c=peak_bid_c, peak_bid_ts=peak_bid_ts,
                settle_v=sv, realized_c=round(sv * 100), ms=ms, st=stt))
        # leg labeling: A = higher anchor; tie-break alphabetical on ticker
        a, b = legs
        if (a["anchor_d"] < b["anchor_d"]) or (a["anchor_d"] == b["anchor_d"] and a["ticker"] > b["ticker"]):
            a, b = b, a
        match_start_ts = a["ms"]; settlement_ts = a["st"]
        winner = "A" if a["settle_v"] == 1.0 else ("B" if b["settle_v"] == 1.0 else "NONE")
        rows.append(dict(
            event_ticker=e, legA_ticker=a["ticker"], legB_ticker=b["ticker"],
            match_start_ts=match_start_ts, settlement_ts=settlement_ts,
            settlement_winner_side=winner,
            match_duration_min=round((settlement_ts - match_start_ts) / 60.0, 3),
            legA_anchor_cents=a["anchor_c"], legA_anchor_dollars=a["anchor_d"],
            legA_T20m_ttms_min=a["ttms"], legA_peak_bid_inmatch_cents=a["peak_bid_c"],
            legA_peak_bid_inmatch_ts=a["peak_bid_ts"], legA_settle_value=a["settle_v"],
            legA_realized_at_settlement_cents=a["realized_c"],
            legB_anchor_cents=b["anchor_c"], legB_anchor_dollars=b["anchor_d"],
            legB_T20m_ttms_min=b["ttms"], legB_peak_bid_inmatch_cents=b["peak_bid_c"],
            legB_peak_bid_inmatch_ts=b["peak_bid_ts"], legB_settle_value=b["settle_v"],
            legB_realized_at_settlement_cents=b["realized_c"],
            pair_combined_anchor_cents=a["anchor_c"] + b["anchor_c"],
            pair_skew_cents=a["anchor_c"] - b["anchor_c"],
            pair_anchor_sum_off_100c=(a["anchor_c"] + b["anchor_c"]) - 100,
        ))
    return rows


def emit_primitive(rows):
    """C37: write .new, reload + validate bytes, os.replace only on pass."""
    schema = pa.schema([
        ("event_ticker", pa.string()), ("legA_ticker", pa.string()),
        ("legB_ticker", pa.string()), ("match_start_ts", pa.int64()),
        ("settlement_ts", pa.int64()), ("settlement_winner_side", pa.string()),
        ("match_duration_min", pa.float64()),
        ("legA_anchor_cents", pa.int64()), ("legA_anchor_dollars", pa.float64()),
        ("legA_T20m_ttms_min", pa.int64()), ("legA_peak_bid_inmatch_cents", pa.int64()),
        ("legA_peak_bid_inmatch_ts", pa.int64()), ("legA_settle_value", pa.float64()),
        ("legA_realized_at_settlement_cents", pa.int64()),
        ("legB_anchor_cents", pa.int64()), ("legB_anchor_dollars", pa.float64()),
        ("legB_T20m_ttms_min", pa.int64()), ("legB_peak_bid_inmatch_cents", pa.int64()),
        ("legB_peak_bid_inmatch_ts", pa.int64()), ("legB_settle_value", pa.float64()),
        ("legB_realized_at_settlement_cents", pa.int64()),
        ("pair_combined_anchor_cents", pa.int64()), ("pair_skew_cents", pa.int64()),
        ("pair_anchor_sum_off_100c", pa.int64()),
    ])
    cols = {f.name: [r[f.name] for r in rows] for f in schema}
    tbl = pa.table(cols, schema=schema)
    new = PRIMITIVE.with_suffix(".parquet.new")
    pq.write_table(tbl, new)
    back = pq.read_table(new)
    assert back.num_rows == len(rows), "row count mismatch on reload"
    assert back.schema.equals(schema), "schema mismatch on reload"
    os.replace(new, PRIMITIVE)


def write_halt_log(probes, summary, u_et, u_utc):
    p1, p2 = probes["probe1_pairing"], probes["probe2_t20"]
    L = []
    L.append("# HALT — ATP_MAIN paired primitive (pre-flight probe gate)\n")
    L.append(f"_Generated {u_et} (= {u_utc})._\n")
    L.append("## Why halted\n")
    if p1["halt_triggered"]:
        L.append(f"- **PROBE 1 pairing rate = {p1['pairing_rate_pct']}%** is below the "
                 f"{PAIR_FLOOR}% floor.")
    if p2["halt_triggered"]:
        L.append(f"- **PROBE 2 fully T-20m-observable events = {p2['both_legs_t20_observable']}** "
                 f"is below the {P2_MIN_EVENTS}-event floor.")
    L.append("\nNo primitive emitted. No bands, no R sweep, no analysis performed.\n")
    L.append("## Probe results (verbatim)\n")
    L.append("```json")
    L.append(json.dumps(probes, indent=2))
    L.append("```")
    HALT_LOG.write_text("\n".join(L))


def write_handoff(probes, summary, rows, u_et, u_utc):
    d = datetime.now(ET).strftime("%Y-%m-%d")
    path = BASE / f"docs/handoffs/atp_main_paired_primitive_{d}.md"
    import statistics as st
    anc_sum = [r["pair_combined_anchor_cents"] for r in rows]
    aA = [r["legA_anchor_cents"] for r in rows]
    aB = [r["legB_anchor_cents"] for r in rows]
    ttA = [r["legA_T20m_ttms_min"] for r in rows]
    ttB = [r["legB_T20m_ttms_min"] for r in rows]
    dur = [r["match_duration_min"] for r in rows]
    winA = sum(1 for r in rows if r["settlement_winner_side"] == "A")
    winB = sum(1 for r in rows if r["settlement_winner_side"] == "B")
    winN = sum(1 for r in rows if r["settlement_winner_side"] == "NONE")
    samp = random.sample(rows, min(5, len(rows)))

    def dist(a):
        a2 = sorted(a)
        def q(p):
            k = (len(a2) - 1) * p; f = int(k); c = min(f + 1, len(a2) - 1)
            return round(a2[f] + (a2[c] - a2[f]) * (k - f), 2)
        return (f"min {min(a)}, p10 {q(.1)}, p25 {q(.25)}, median {st.median(a)}, "
                f"p75 {q(.75)}, p90 {q(.9)}, max {max(a)}, mean {round(st.mean(a),2)}")

    L = [f"# ATP_MAIN paired primitive — handoff ({u_et} = {u_utc})\n",
         f"**Path A** — F35 tier-1/2 live-era cohort, thresholds calibrated to this universe.\n",
         f"**Final N in primitive:** {len(rows)} paired events  |  "
         f"**producer commit:** `{summary['producer_commit_hash'][:12]}`  |  "
         f"**output sha256:** `{summary['output_sha256'][:16]}`\n",
         "## Probe results (verbatim)\n", "```json", json.dumps(probes, indent=2), "```\n",
         "## Anchor sum distribution (diagonal check)\n",
         f"- {dist(anc_sum)} (cents)\n",
         f"- count |sum-100c| > 3c: {probes['probe4_inversion']['count_off_gt_3c']} "
         f"({probes['probe4_inversion']['pct_within_3c']}% within 3c)\n",
         "## Per-leg anchor distribution (leg-labeling sanity — A must be >= B)\n",
         f"- legA (higher): {dist(aA)}\n",
         f"- legB (lower):  {dist(aB)}\n",
         f"- A>=B holds on all rows: {all(r['legA_anchor_cents']>=r['legB_anchor_cents'] for r in rows)}\n",
         "## T-20m ttms distribution (anchor tightness)\n",
         f"- legA: {dist(ttA)}\n",
         f"- legB: {dist(ttB)}\n",
         "## match_duration_min distribution\n",
         f"- {dist(dur)}\n",
         "## settlement winner side\n",
         f"- A: {winA}, B: {winB}, NONE: {winN}\n",
         "## 5 random sample rows\n", "```json", json.dumps(samp, indent=2), "```\n",
         "## Honest unknowns / calibration context (G23)\n",
         "- **Why the floor numbers differ from PAIRING_DIAGNOSTIC.md:** the prior halted "
         f"run (ec7cdae) used a [80, 92]% pairing band and a 1500-event floor. Those were "
         "calibrated against the **spike per-N universe** (`atp_main_spike_perN.parquet`, "
         f"N=4,137 → 2,230 events → 1,907 paired = {SPIKE_PERN_PAIR_PCT}%), a broader set "
         "than the cohort this producer actually uses. The **F35 tier-1/2 live-era cohort** "
         "(`tier==live` & `both_sides_*` & `total_volume_in_match>0`) is event-symmetric — if "
         "one leg passes the screen its partner almost always does too — so it pairs at ~100%, "
         "not ~85.5%. Path A re-calibrates to the cohort itself: PROBE 1 floor-only ≥ 95%, "
         "PROBE 2 floor 500. These are not a relaxation of quality gates; they match the gate "
         "shape to the universe being gated.\n",
         "- **descriptive_1c dropped from inputs:** `atp_main_descriptive_1c.parquet` is "
         "cell-level (90 rows, no ticker column), so it carries no per-ticker settlement. "
         "`settlement_value` is read directly from `per_minute_features` (the answer-key "
         "terminal value, E32(d)). Only two inputs are recorded in run_summary.json.\n",
         "- **settlement_winner_side = NONE** would indicate a paired event where neither leg "
         f"settled 1.0 (data anomaly). This run: {winN}.\n",
         "- **Premarket excluded by construction:** the forward walk is match_start → "
         "settlement-300s only. R hits in premarket (the +1c/+2c/+3c trap) are out of scope "
         "here and handled separately downstream.\n"]
    path.write_text("\n".join(L))


if __name__ == "__main__":
    sys.exit(main())
