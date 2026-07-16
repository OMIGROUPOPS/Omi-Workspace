#!/usr/bin/env python3
"""THE GAME REPORT — the daily standard's artifact (C-DAILY-STANDARD v1
Part 2, 07-15; spec verbatim in docs/THE_DAILY_STANDARD.md).

Per game: header · the window timeline with every action plotted · Layer A
per leg (the individual, FIRST) · Layer B per pair (the composition,
SECOND, never instead) · the decision log with surfaces consulted · refusal
counterfactuals · the verdict line (grade, dollars, billed book, owning
fix).

Self-contained: reads the day's jsonl only. Columns that need the exchange
tape (TIGHT/EARLY vs own low) are graded by the nightly regrade and marked
here by name — a GAP is named, never guessed.

Usage:
  python3 analysis/game_report.py --date YYYYMMDD [--event KX...] [--active-only]
Output: .claude/game_reports/<date>/GR_<event>.md + INDEX.md
"""
import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "logs"
OUT_ROOT = ROOT.parent / ".claude" / "game_reports"

DECISION_EVENTS = frozenset((
    "v4_place", "trendpath_live_aim", "order_placed", "order_cancelled",
    "entry_filled", "exit_filled", "v4_exit_posted", "settled",
    "completion_action", "completion_no_attempt", "path_mode_hold",
    "gun_fired", "match_live_grace_armed", "match_live_resting_cancel",
    "below_leg_floor_refused", "no_path_page_refused",
    "below_discovery_floor_refused", "corridor_refused_w1_preference",
    "corridor_itf_fallback_placed", "pair_seesaw_refused",
    "selector_drop_refused", "w2_fill_violation", "cancel_fill_race",
    "fill_booked_reconcile", "schedule_match", "clock_liar",
    "bell_missing", "entry_dossier"))


def et_hm(ep):
    return (datetime.utcfromtimestamp(ep) - timedelta(hours=4)).strftime(
        "%I:%M:%S %p")


def load_day(ymd):
    p = LOG_DIR / ("live_v3_%s.jsonl" % ymd)
    ev = defaultdict(list)
    if not p.exists():
        return ev
    for line in open(p, encoding="utf-8", errors="replace"):
        if not any(('"%s"' % e) in line for e in DECISION_EVENTS):
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        e = d.get("event")
        if e not in DECISION_EVENTS:
            continue
        det = d.get("details") or {}
        etk = det.get("event") or (d.get("ticker", "").rsplit("-", 1)[0]
                                   if d.get("ticker") else "")
        if etk:
            ev[etk].append(d)
    return ev


def leg_of(d):
    return d.get("ticker") or ""


def render_event(etk, rows):
    rows.sort(key=lambda d: d.get("ts_epoch", 0))
    legs = sorted({leg_of(d) for d in rows if leg_of(d)})
    cat = next((d["details"].get("cat") for d in rows
                if (d.get("details") or {}).get("cat")), "?")
    sched = next((d["details"].get("start_time") for d in rows
                  if d["event"] == "schedule_match"), None)
    liar = next((d["details"] for d in rows if d["event"] == "clock_liar"),
                None)
    gun = next((d for d in rows if d["event"] == "gun_fired"), None)

    L = ["# GAME REPORT — %s" % etk,
         "(C-DAILY-STANDARD v1 — the standard's artifact; spec "
         "docs/THE_DAILY_STANDARD.md)", ""]
    # 1) header
    L += ["## HEADER",
          "- legs: %s" % (", ".join(l.rsplit("-", 1)[1] for l in legs)
                          or "none touched"),
          "- category: %s" % cat,
          "- scheduled clock: %s%s" % (sched or "no schedule join",
              " | CLOCK LIAR: disagreement %s min (%s)" % (
                  liar.get("disagreement_min"),
                  liar.get("anchor_source")) if liar else ""),
          "- gun: %s" % ("%s @ %s (tts_honest %s min)" % (
              gun["details"].get("source"), et_hm(gun["ts_epoch"]),
              gun["details"].get("tts_honest_min")) if gun
              else "NEVER FIRED"),
          ]
    dvol = next((d["details"].get("discovered_shares") for d in rows
                 if d["event"] == "below_discovery_floor_refused"), None)
    if dvol is not None:
        L.append("- discovery volume at refusal: %s (floor status: "
                 "REFUSED below 1,500)" % dvol)
    # dossier-carried vitality (Layer 3 stamps, when present)
    for d in rows:
        if d["event"] == "entry_dossier":
            s = (d["details"].get("surfaces") or {})
            cw = s.get("cash_window")
            if cw:
                L.append("- cash-window stamp (%s): %s p_w1_cash=%s" % (
                    leg_of(d).rsplit("-", 1)[-1], cw.get("verdict",
                    cw.get("status")), cw.get("p_w1_cash")))
    # 2) the window timeline
    L += ["", "## THE WINDOW TIMELINE (every action plotted)"]
    for d in rows:
        det = d.get("details") or {}
        w = det.get("window") or {}
        ph = w.get("phase", "")
        e = d["event"]
        if e == "entry_dossier":
            continue        # rendered in the decision log
        line = "- %s [%s] %s %s" % (
            et_hm(d.get("ts_epoch", 0)), ph or "—", e,
            leg_of(d).rsplit("-", 1)[-1] if leg_of(d) else "")
        if e == "order_placed":
            line += " %s %s@%s" % (det.get("action"), det.get("count"),
                                   det.get("price"))
        elif e in ("entry_filled", "exit_filled"):
            line += " px=%s qty=%s%s" % (
                det.get("fill_price", det.get("exit_price")),
                det.get("qty"),
                " pnl=%+.0fc" % det["pnl_cents"]
                if det.get("pnl_cents") is not None else "")
        elif e == "settled":
            line += " %s %+.0fc" % (det.get("settle"),
                                    det.get("pnl_cents") or 0)
        elif e == "order_cancelled":
            line += " label=%s ok=%s" % (det.get("label"),
                                         det.get("success"))
        elif e == "gun_fired":
            line += " source=%s" % det.get("source")
        elif e == "w2_fill_violation":
            line = "- %s [W2] **W2 FILL VIOLATION** %s px=%s (%s)" % (
                et_hm(d.get("ts_epoch", 0)),
                leg_of(d).rsplit("-", 1)[-1], det.get("fill_price"),
                det.get("booking_source"))
        L.append(line)
    # 3) Layer A — the leg as an individual, FIRST
    L += ["", "## LAYER A — the leg as an individual (first, always)"]
    for tk in legs:
        lr = [d for d in rows if leg_of(d) == tk]
        fill = next((d for d in lr if d["event"] == "entry_filled"), None)
        dossier = next((d for d in lr if d["event"] == "entry_dossier"
                        and str((d["details"] or {}).get(
                            "decision", "")).startswith("placed")), None)
        exitp = next((d for d in lr if d["event"] == "v4_exit_posted"),
                     None)
        exitf = next((d for d in lr if d["event"] == "exit_filled"), None)
        setl = next((d for d in lr if d["event"] == "settled"), None)
        leg = tk.rsplit("-", 1)[-1]
        if not (fill or dossier):
            L.append("- **%s**: no placement dossier and no fill today "
                     "(cancels/refusals only)" % leg)
            continue
        basis = (fill["details"].get("fill_price") if fill else None)
        band = (exitp["details"].get("band_x") if exitp else None)
        surf = (dossier["details"].get("surfaces") if dossier else {}) or {}
        med = None
        fs = surf.get("flow_state") or {}
        disc_bucket = "GAP (trailing traded mean not on this line)"
        rl = surf.get("reach_law") or {}
        if rl.get("status") == "CONSULTED":
            med = None  # median rides the reach consultation internally
        verdict = ("CASHED %+.0fc" % exitf["details"]["pnl_cents"]
                   if exitf and exitf["details"].get("pnl_cents") is not None
                   else "SETTLED-%s %+.0fc" % (
                       setl["details"].get("settle"),
                       setl["details"].get("pnl_cents") or 0)
                   if setl else
                   "OPEN (exit %s@%s resting)" % (
                       exitp["details"].get("qty"),
                       exitp["details"].get("exit_price"))
                   if fill and exitp else
                   "POSTED-UNFILLED" if not fill else "OPEN")
        wf = ((fill or {}).get("details") or {}).get("window") or {}
        wp = ((dossier or {}).get("details") or {}).get(
            "surfaces", {}).get("window_phase") or {}
        L += ["- **%s** basis=%s | required swing to band=%s beside it "
              "(favorites law: higher swings in great contention, dropped "
              "where the path shows no promise — selector said %s) | "
              "discount bucket: %s | TIGHT/EARLY vs own low: nightly "
              "regrade owns the tape column | placement-phase=%s "
              "fill-phase=%s | verdict: **%s**" % (
                  leg, basis if basis is not None else "—",
                  band if band is not None else "—",
                  (surf.get("contention_selector") or {}).get("verdict"),
                  disc_bucket,
                  wp.get("phase", "?"), wf.get("phase", "—"), verdict)]
    # 4) Layer B — the pair as a composition, SECOND, never instead
    L += ["", "## LAYER B — the pair as a composition (second, never "
              "instead; neither layer launders the other)"]
    fills = [(d["ts_epoch"], leg_of(d), d["details"].get("fill_price"))
             for d in rows if d["event"] == "entry_filled"]
    if len(fills) >= 2:
        fills.sort()
        combined = sum(px for _, _, px in fills[:2] if px)
        L.append("- combined at fills: **%d** (%s) — the <=97 scoreboard "
                 "is the measurement" % (
                     combined, "<=97 SUCCESS" if combined <= 97
                     else "OVER — %s" % ("PAR BREACH, total failure"
                                          if combined > 100 else "above 97")))
        L.append("- who-first: %s at %s, then %s at %s (fitted "
                 "orientation: riser early, faller late; favorite dips "
                 "first 2:1)" % (
                     fills[0][1].rsplit("-", 1)[-1], et_hm(fills[0][0]),
                     fills[1][1].rsplit("-", 1)[-1], et_hm(fills[1][0])))
    elif len(fills) == 1:
        L.append("- ONE-SIDED: only %s filled — pair never composed "
                 "(completion policy owns the remainder)"
                 % fills[0][1].rsplit("-", 1)[-1])
    else:
        L.append("- no fills — pair state is the refusal record below")
    # 5) the decision log
    L += ["", "## THE DECISION LOG (every placement/re-aim/refusal/cancel "
              "with surfaces consulted)"]
    for d in rows:
        if d["event"] != "entry_dossier":
            continue
        det = d["details"]
        surf = det.get("surfaces") or {}
        answered = ", ".join("%s:%s" % (k[:12], (v or {}).get(
            "status", "?")[:4]) for k, v in surf.items())
        L.append("- %s %s %s | %s" % (
            et_hm(d.get("ts_epoch", 0)), leg_of(d).rsplit("-", 1)[-1],
            det.get("decision"), answered[:220]))
    # 6) refusal counterfactuals
    refs = [d for d in rows if d["event"].endswith("_refused")]
    L += ["", "## REFUSAL COUNTERFACTUALS"]
    if refs:
        for d in refs[:20]:
            det = d["details"]
            L.append("- %s %s %s (%s) — counterfactual: the nightly "
                     "regrade prices refused aims vs realized lows "
                     "(tape column)" % (
                         et_hm(d.get("ts_epoch", 0)), d["event"],
                         leg_of(d).rsplit("-", 1)[-1] or det.get("cat"),
                         json.dumps({k: det.get(k) for k in
                                     ("path_aim", "discovery",
                                      "discovered_shares", "why")
                                     if det.get(k) is not None})[:120]))
    else:
        L.append("- none")
    # 7) verdict line
    pnl = sum((d["details"].get("pnl_cents") or 0) for d in rows
              if d["event"] in ("exit_filled", "settled"))
    w2v = sum(1 for d in rows if d["event"] == "w2_fill_violation")
    tid = next((d["details"].get("trade_id") for d in rows
                if d["event"] == "entry_filled"
                and d["details"].get("trade_id")), "")
    billed = ("TAIL" if tid.startswith("T-20260714") else
              "PATH" if tid else "—")
    grade = ("F (W2 violation on the book)" if w2v else
             "A" if pnl > 0 else "B" if pnl == 0 else "C")
    fix = ("the tape-bell + zero-tolerance own the W2 class" if w2v else
           "—")
    L += ["", "## VERDICT",
          "- grade: **%s** | dollars: %+.0fc realized today | billed: %s "
          "| owning fix: %s" % (grade, pnl, billed, fix)]
    return "\n".join(L) + "\n"


def daysheet_row(etk, rows):
    """[C-FUND-TRACKER Part 3] one row per game-leg for THE DAY SHEET —
    the game reports' front page. Cents beside basis, always."""
    out = []
    cat = next((d["details"].get("cat") for d in rows
                if (d.get("details") or {}).get("cat")), "?")
    fills = [(d["ts_epoch"], leg_of(d), d["details"]) for d in rows
             if d["event"] == "entry_filled"]
    combined = (sum(f[2].get("fill_price") or 0 for f in sorted(fills)[:2])
                if len(fills) >= 2 else
                (fills[0][2].get("fill_price") if fills else None))
    for d in rows:
        if d["event"] != "entry_filled":
            continue
        det = d["details"]
        tk = leg_of(d)
        w = det.get("window") or {}
        basis = det.get("fill_price") or 0
        setl = next((x["details"] for x in rows
                     if x["event"] == "settled" and leg_of(x) == tk), None)
        exitf = next((x["details"] for x in rows
                      if x["event"] == "exit_filled" and leg_of(x) == tk),
                     None)
        pnl = ((exitf or setl or {}).get("pnl_cents"))
        outcome = ("CASHED" if exitf else
                   ("SETTLED-%s" % setl.get("settle")) if setl else "OPEN")
        role = "fav" if basis >= 50 else "dog"
        grade = ("F(W2)" if w.get("phase") == "W2" else
                 "A" if (pnl or 0) > 0 else
                 "B" if pnl in (0, None) else "C")
        out.append({"game": etk[-16:], "cat": cat,
                    "leg": tk.rsplit("-", 1)[-1], "role": role,
                    "entry": "%d¢ (basis %d)" % (basis, basis),
                    "window": w.get("phase", "?"),
                    "combined": combined, "outcome": outcome,
                    "grade": grade,
                    "dollars": ("%+d¢ (%.0f%% of basis %d¢)"
                                % (pnl, pnl / basis * 100 if basis else 0,
                                   basis)) if pnl is not None else "open"})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    ap.add_argument("--event", default=None)
    ap.add_argument("--active-only", action="store_true",
                    help="only events with a fill, placement or refusal")
    args = ap.parse_args()
    ev = load_day(args.date)
    outdir = OUT_ROOT / args.date
    outdir.mkdir(parents=True, exist_ok=True)
    sheet = []
    idx = []
    for etk, rows in sorted(ev.items()):
        if args.event and args.event not in etk:
            continue
        if args.active_only and not any(
                d["event"] in ("entry_filled", "order_placed",
                               "entry_dossier")
                for d in rows):
            continue
        md = render_event(etk, rows)
        fp = outdir / ("GR_%s.md" % etk.replace("/", "_"))
        fp.write_text(md, encoding="utf-8")
        sheet.extend(daysheet_row(etk, rows))
        pnl = sum((d["details"].get("pnl_cents") or 0) for d in rows
                  if d["event"] in ("exit_filled", "settled"))
        idx.append("- [%s](GR_%s.md) events=%d pnl=%+.0fc" % (
            etk, etk, len(rows), pnl))
    (outdir / "INDEX.md").write_text(
        "# GAME REPORTS %s (%d games)\n\n%s\n"
        % (args.date, len(idx), "\n".join(idx)), encoding="utf-8")
    (outdir / "DAYSHEET.json").write_text(
        json.dumps(sheet, indent=1), encoding="utf-8")
    print("game_reports: %d games -> %s (+DAYSHEET.json %d rows)"
          % (len(idx), outdir, len(sheet)))


if __name__ == "__main__":
    main()
