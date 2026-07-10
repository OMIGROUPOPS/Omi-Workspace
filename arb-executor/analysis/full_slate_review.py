#!/usr/bin/env python3
"""C-FULL-SLATE-REVIEW — grade the LOGIC, not just the fills (read-only).
Consumed by conviction_replay (the nightly instrument inherits everything).
Part 1: per-step L1-L9 grades per trade id (rule cited / FITTED-DECREED-NAKED
/ composer verdict at that tick / disagreement dollars where priceable).
Part 2: the no-fill cohort taxonomy + forgone band + the June strand test.
Part 3: exchange-truth three-way reconciliation (bot report vs log vs REST).
Part 4: class filings + fix queue ranked by measured cost.
Exits GRADED ONLY (§0A). pair-97 graded as legacy exposure (#11)."""
import glob, gzip, json, sys
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ET = timezone(timedelta(hours=-4))

# classification tables: marker -> (rule fired, code cite, FITTED/DECREED/NAKED, registry/ruling cite)
L1_CLOCK = {"kalshi_schedule_primary": ("kalshi schedule clock", "discover_markets/schedule resolver",
                                        "DECREED", "census 07-10: Kalshi = card markers; ITF live-era only"),
            "te": ("TE honest schedule", "pm-honest matcher", "FITTED", "M-external truth (TE bank)")}
L3_BELL = {"te_scoreboard": ("gun: TE in-play transition", "_gun_poll src1", "FITTED", "external truth feed"),
           "schedule_live": ("gun: schedule status live", "_gun_poll src2", "FITTED", "external truth feed"),
           "tape_latch": ("gun: tape burst latch", "_is_match_live", "DECREED", "M10 constants, scorecard-graded"),
           "price_divergence": ("gun: 10c ref divergence", "_gun_poll src4", "DECREED", "M10 constants"),
           "fallback_bell": ("fallback bell rate+rise", "_gun_poll src5", "DECREED", "M10/M13 constants, scorecard-graded")}
L4_TABLE = {"per_cell": ("entry table per-cell offset", "v4 entry tables", "DECREED", "M5 era-mixed, refit queued"),
            "regime": ("entry table regime offset", "v4 entry tables", "DECREED", "M5 era-mixed"),
            "no_trade_staircase": ("staircase no-trade placement", "staircase_hold_place", "DECREED", "walking-staircase spec"),
            "engagement_join": ("engagement join-the-bid", "engagement path", "DECREED", "join doctrine"),
            "aim_table": ("per-cat dip depth", "_aim_faller_depth", "FITTED", "M2 aim_table (RULING_DYNAMIC_S_CELL_AIM)")}


def _load_m1():
    try:
        return json.loads((ROOT.parent / ".claude/seqfloor_20260708/recut_cells.json").read_text())
    except OSError:
        return {}


def collect_day(ymd, log):
    """One pass: per-ticker decision events + per-event context."""
    day0 = datetime.strptime(ymd, "%Y%m%d").replace(tzinfo=ET).timestamp()
    day1 = day0 + 86400
    KEEP = ('"v4_place"', '"order_placed"', '"order_cancelled"', '"v4_move_repost"',
            '"v4_exit_posted"', '"exit_filled"', '"entry_filled"', '"settled"',
            '"window_open_set"', '"early_unlock_open"', '"gun_fired"', '"bell_missing"',
            '"sibling_repost_placed"', '"reaim_sibling_arrival"', '"schedule_match"',
            '"premarket_walk_capped"', '"v4_repost_hold_same_price"', '"scalp_filled"',
            '"fill_booked_reconcile"', '"match_live_resting_cancel"', '"skipped"')
    per_tk, per_ev = defaultdict(list), defaultdict(dict)
    for line in open(log, encoding="utf-8", errors="replace"):
        if not any(k in line for k in KEEP):
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        ts = d.get("ts_epoch", 0)
        if not (day0 <= ts < day1):
            continue
        e, det, tk = d["event"], d.get("details") or {}, d.get("ticker", "")
        ev = det.get("event", "") or (tk.rsplit("-", 1)[0] if tk else "")
        if e == "schedule_match":
            per_ev[ev]["clock_method"] = det.get("method", "")
        elif e == "early_unlock_open":
            per_ev[ev]["unlock"] = det
        elif e == "gun_fired":
            per_ev[ev]["gun"] = {"ts": ts, "source": det.get("source")}
        elif e == "bell_missing":
            per_ev[ev]["bell_missing"] = True
        elif tk:
            if e == "skipped":
                sk = per_tk[tk]
                if not (sk and sk[-1]["e"] == "skipped"):   # dedup runs
                    per_tk[tk].append({"e": e, "ts": ts, "d": {"reason": det.get("reason")}})
            else:
                per_tk[tk].append({"e": e, "ts": ts, "d": det})
    return per_tk, per_ev


def grade_steps(trade, per_tk, per_ev, composer, obs, m1):
    """L1-L9 rows for one trade id."""
    tk, ev = trade["tk"], trade["tk"].rsplit("-", 1)[0]
    cat = trade["cat"]
    evc = per_ev.get(ev, {})
    tkev = [x for x in per_tk.get(tk, [])]
    rows = []
    def add(step, rule, cite, cls, anchor, verdict="", dollars=None):
        rows.append({"id": trade["id"], "step": step, "rule": rule, "cite": cite,
                     "class": cls, "anchor": anchor, "verdict": verdict,
                     "dollars": dollars})
    def post_at(ts):
        o = [x for x in obs if x[0] <= ts]
        if not o or trade.get("prior") is None:
            return None
        s = composer.tick_posterior(trade["prior"], o)
        return s[-1][1] if s else trade["prior"].get("confidence")
    # L1 discovery/clock
    cm = evc.get("clock_method", "")
    key = "te" if cm.startswith("te") else "kalshi_schedule_primary"
    r = L1_CLOCK[key]
    add("L1", r[0] + " (%s)" % (cm or "?"), r[1], r[2], r[3])
    # L2 qualification
    if evc.get("unlock"):
        add("L2", "early unlock (realized vol %.0f >= 2500)" % (evc["unlock"].get("vol") or 0),
            "router gate unlock branch", "FITTED", "M3 + RULING_EARLY_UNLOCK")
    else:
        add("L2", "universal T-240 window", "V4_MAX_PLACEMENT_SEC", "DECREED",
            "constraint #4 named constant (universal window)")
    # L3 bell
    g = evc.get("gun")
    if g:
        r = L3_BELL.get(g["source"], ("gun: %s" % g["source"], "_gun_poll", "DECREED", "M10"))
        add("L3", r[0], r[1], r[2], r[3])
    elif evc.get("bell_missing"):
        add("L3", "NO BELL past anchored start", "bell_missing invariant", "NAKED",
            "C-REALITY-BELL coverage violation")
    else:
        add("L3", "premarket throughout / no bell needed", "-", "FITTED", "reality invariant live")
    # L4 aim + L5 placement
    vps = [x for x in tkev if x["e"] == "v4_place" and x["ts"] <= trade["ts"] + 1]
    p_conf = post_at(trade["ts"])
    if vps:
        v = vps[-1]["d"]
        tsrc = v.get("table_src", "?")
        r = L4_TABLE.get(tsrc, (tsrc, "v4 place", "DECREED", "unmapped table source"))
        add("L4", "%s (anchor %s, cell %s)" % (r[0], v.get("anchor_src"), v.get("cell")),
            r[1], r[2], r[3],
            verdict=("posterior %.2f at aim tick" % p_conf) if p_conf is not None else "NO-OPINION")
    else:
        add("L4", "no v4_place recorded (adopted/booked path)", "-", "NAKED", "lineage-only aim")
    pair97 = any(x["e"] in ("sibling_repost_placed", "reaim_sibling_arrival") for x in tkev)
    edge = (p_conf * 100 - trade["px"]) if p_conf is not None else None
    add("L5", "maker placement @%s%s" % (trade["px"], " [pair-97 arithmetic touched]" if pair97 else ""),
        "place_order chokepoint battery", "DECREED" if pair97 else "FITTED",
        "RULING_PAIR_ECONOMICS legacy exposure" if pair97 else "chokepoint guards (law)",
        verdict=("edge %+.1f vs posterior" % edge) if edge is not None else "NO-OPINION",
        dollars=(round(edge * trade["qty"] / 100.0, 2) if (edge is not None and edge < -2) else None))
    # L6 hold/repost/walk
    nrep = sum(1 for x in tkev if x["e"] == "v4_move_repost")
    nhold = sum(1 for x in tkev if x["e"] == "v4_repost_hold_same_price")
    ncap = sum(1 for x in tkev if x["e"] == "premarket_walk_capped")
    add("L6", "reposts=%d holds=%d walk-caps=%d" % (nrep, nhold, ncap),
        "_v4_manage_resting", "DECREED" if nrep else "FITTED",
        "M5 offset remap (era-mixed)" if nrep else "churn-fix hold (law)")
    # L7 exit (GRADED ONLY, §0A)
    exf = [x for x in tkev if x["e"] == "exit_filled" and x["ts"] >= trade["ts"]]
    exp_ = [x for x in tkev if x["e"] == "v4_exit_posted" and x["ts"] >= trade["ts"] - 2]
    if exf:
        xe = exf[0]
        pc = post_at(xe["ts"])
        gap = (pc * 100 - xe["d"].get("exit_price", 0)) if pc is not None else None
        add("L7", "band exit filled @%s (band from cell table)" % xe["d"].get("exit_price"),
            "exit_rule_for (FV-blind by design)", "DECREED", "M6 + pending -0g ruling",
            verdict=("posterior %.2f at exit tick -> gap %+.1f" % (pc, gap)) if pc is not None else "NO-OPINION",
            dollars=(round(gap * xe["d"].get("qty", 5) / 100.0, 2) if (gap is not None and gap > 2) else None))
    elif exp_:
        add("L7", "band exit resting @%s" % exp_[0]["d"].get("exit_price"),
            "exit_rule_for (FV-blind by design)", "DECREED", "M6 + pending -0g ruling")
    else:
        add("L7", "NO EXIT POSTED", "-", "NAKED", "CLASS UNBOOKED FILL signature")
    # L8 booking
    booked = any(x["e"] == "fill_booked_reconcile" for x in tkev)
    add("L8", "fill booked%s (cycle %s)" % (" via reconcile healer" if booked else " via check_fills",
                                            trade.get("cycle", 1)),
        "_book_v4_entry_fill / C-BOOK-THE-FILL", "FITTED", "booking law + cycle stamps")
    # L9 settlement/grading
    st = [x for x in tkev if x["e"] == "settled"]
    add("L9", "settled %s" % (st[0]["d"].get("settle") if st else "open"),
        "settlement vocabulary + bot-only basis", "FITTED", "rulings 07-09/07-10")
    return rows


def no_fill_cohort(per_tk, per_ev, composer, m1, leg_obs_fn, filled_tks, settles):
    rows = []
    for tk, evs in per_tk.items():
        buys = [x for x in evs if x["e"] == "order_placed" and x["d"].get("action") == "buy"]
        if not buys or tk in filled_tks:
            continue
        cat = None
        for pre, c in (("KXITFWMATCH", "ITF_W"), ("KXITFMATCH", "ITF_M"),
                       ("KXATPCHALLENGERMATCH", "ATP_CHALL"), ("KXWTACHALLENGERMATCH", "WTA_CHALL"),
                       ("KXATPMATCH", "ATP_MAIN"), ("KXWTAMATCH", "WTA_MAIN")):
            if tk.startswith(pre):
                cat = c
                break
        b0 = buys[0]
        px = b0["d"].get("price", 0)
        obs = leg_obs_fn(tk)
        after = [o for o in obs if o[0] >= b0["ts"] and o[1] == "print"]
        before = [o for o in obs if o[0] < b0["ts"] and o[1] == "print"]
        lo_after = min((o[2] for o in after), default=None)
        lo_before = min((o[2] for o in before), default=None)
        gate_cancelled = any(x["e"] == "match_live_resting_cancel" for x in evs)
        if not after and not before:
            tax = "anchor_refused_or_dead_book"
        elif gate_cancelled and (lo_after is None or lo_after > px):
            tax = "gate_blocked (match-live cancel before reachable)"
        elif lo_after is not None and lo_after <= px:
            tax = "queue_starved (tape printed at/below our level, no fill -- adverse-selection signature)"
        elif lo_before is not None and lo_before <= px:
            tax = "late_vs_dip (the dip printed before our placement)"
        else:
            tax = "aim_below_achievable (tape low %.0f > bid %d)" % (lo_after or 999, px)
        edge = None
        try:
            edge = ((m1.get(cat) or {}).get(str(int(px))) or {}).get("edge_p50")
        except Exception:
            pass
        # strand test: sibling filled? did OUR unfilled side win?
        ev = tk.rsplit("-", 1)[0]
        sibs = [t for t in filled_tks if t.startswith(ev + "-") and t != tk]
        strand = bool(sibs)
        won = None
        st = settles.get(tk)
        if st is not None:
            won = (st.get("settle") == "WIN") if "settle" in st else None
        rows.append({"tk": tk, "cat": cat, "bid": px, "n_buys": len(buys),
                     "taxonomy": tax, "forgone_edge_p50_cents": edge,
                     "strand_of_filled_sibling": strand, "unfilled_side_won": won})
    return rows


def healed_bookings(per_tk):
    """[C-DAYLIGHT-ROOTS] fill_booked_reconcile = a booking the healer made
    (the UNBOOKED FILL class's forward closure); the reconciliation counts it
    as log truth so healed fills never re-flag as missing."""
    out = defaultdict(float)
    for tk, evs in per_tk.items():
        for x in evs:
            if x["e"] == "fill_booked_reconcile":
                out[tk] += float(x["d"].get("held", 0) or 0)
    return out


def exchange_truth(ymd, trades, log_fills_by_tk):
    """Three-way reconciliation via the audited REST path (kalshi_reconciler auth)."""
    sys.path.insert(0, str(ROOT))
    try:
        from kalshi_reconciler import _headers, _load_private_key
        import requests
    except Exception as e:
        return {"error": "REST path unavailable: %s" % str(e)[:100], "violations": []}
    pk = _load_private_key()
    B = "https://api.elections.kalshi.com"
    day0 = datetime.strptime(ymd, "%Y%m%d").replace(tzinfo=ET)
    fills, cur = defaultdict(lambda: {"qty": 0.0, "px": []}), None
    n_pages = 0
    while n_pages < 60:
        n_pages += 1
        p = "/trade-api/v2/portfolio/fills"
        params = {"limit": 200}
        if cur:
            params["cursor"] = cur
        r = requests.get(B + p, headers=_headers(pk, "GET", p), params=params, timeout=20).json()
        rows_ = r.get("fills", [])
        stop = False
        for f in rows_:
            try:
                fts = datetime.fromisoformat(f["created_time"].replace("Z", "+00:00")).astimezone(ET)
            except Exception:
                continue
            if fts.strftime("%Y%m%d") < ymd:
                stop = True
                break
            if fts.strftime("%Y%m%d") != ymd or f.get("action") != "buy":
                continue
            tk = f.get("ticker", "")
            q = float(f.get("count_fp", f.get("count", 0)) or 0)
            fills[tk]["qty"] += q
            try:
                fills[tk]["px"].append(round(float(f.get("yes_price_dollars")) * 100))
            except Exception:
                pass
        cur = r.get("cursor")
        if stop or not cur or not rows_:
            break
    violations = []
    seen = set()
    for t in trades:
        tk = t["tk"]
        if tk in seen:
            continue
        seen.add(tk)
        log_q = log_fills_by_tk.get(tk, 0)
        ex = fills.get(tk, {"qty": 0.0, "px": []})
        if abs(ex["qty"] - log_q) >= 1:
            violations.append({"tk": tk, "kind": "qty_mismatch",
                               "bot_report_and_log": log_q, "exchange": ex["qty"]})
        elif ex["px"] and t["px"] not in ex["px"] and abs(t["px"] - ex["px"][0]) > 1:
            violations.append({"tk": tk, "kind": "price_mismatch",
                               "log_px": t["px"], "exchange_px": ex["px"][:3]})
    for tk, ex in fills.items():
        if ex["qty"] >= 1 and tk not in log_fills_by_tk:
            violations.append({"tk": tk, "kind": "exchange_fill_missing_from_log",
                               "exchange_qty": ex["qty"]})
    return {"n_exchange_buy_fills_day": int(sum(v["qty"] for v in fills.values())),
            "n_tickers_exchange": len(fills), "violations": violations}


def run(ymd, trades, per_tk, per_ev, composer, obs_cache, settles, leg_obs_fn):
    m1 = _load_m1()
    step_rows = []
    for t in trades:
        obs = obs_cache.get(t["tk"], [])
        step_rows += grade_steps(t, per_tk, per_ev, composer, obs, m1)
    filled_tks = {t["tk"] for t in trades}
    log_fills_by_tk = defaultdict(float)
    for t in trades:
        log_fills_by_tk[t["tk"]] += t.get("qty", 5)
    cohort = no_fill_cohort(per_tk, per_ev, composer, m1, leg_obs_fn, filled_tks, settles)
    for tk, q in healed_bookings(per_tk).items():
        log_fills_by_tk[tk] += q          # healer bookings are log truth
    xt = exchange_truth(ymd, trades, log_fills_by_tk)
    # Part 4: class filings + ranked fix queue
    filings = defaultdict(lambda: {"instances": 0, "dollars": 0.0})
    for r in step_rows:
        if r["class"] == "NAKED":
            filings["NAKED-STEP %s" % r["step"]]["instances"] += 1
        if r["dollars"]:
            key = ("DOCTRINE CONFLICT (exit-band vs conviction)" if r["step"] == "L7"
                   else "conviction-gap placements")
            filings[key]["instances"] += 1
            filings[key]["dollars"] += abs(r["dollars"])
    for cr in cohort:
        if cr["taxonomy"].startswith("queue_starved"):
            filings["ADVERSE-SELECTION STRAND (live population)"]["instances"] += 1
            if cr["forgone_edge_p50_cents"]:
                filings["ADVERSE-SELECTION STRAND (live population)"]["dollars"] += cr["forgone_edge_p50_cents"] * 5 / 100.0
        elif cr["taxonomy"].startswith(("aim_below", "late_vs_dip")):
            filings["AIM/TIMING MISS (no-fill)"]["instances"] += 1
            if cr["forgone_edge_p50_cents"]:
                filings["AIM/TIMING MISS (no-fill)"]["dollars"] += cr["forgone_edge_p50_cents"] * 5 / 100.0
    for v in xt.get("violations", []):
        filings["EXCHANGE-TRUTH DAYLIGHT"]["instances"] += 1
    fixq = sorted(filings.items(), key=lambda kv: -kv[1]["dollars"])
    # render
    L = ["# FULL SLATE REVIEW %s (grade the logic; read-only; §0A held)" % ymd, "",
         "## Part 1 — per-step grades (%d trades x L1-L9 = %d rows)" % (len(trades), len(step_rows)),
         "", "| id | step | rule (cite) | class | anchor | composer verdict | $ |",
         "|---|---|---|---|---|---|---|"]
    for r in step_rows:
        L.append("| %s | %s | %s (%s) | %s | %s | %s | %s |" % (
            r["id"], r["step"], r["rule"][:70].replace("|", "/"), r["cite"][:40],
            r["class"], r["anchor"][:55].replace("|", "/"), r["verdict"], r["dollars"] or ""))
    nf = sum(1 for r in step_rows if r["class"] == "FITTED")
    nd = sum(1 for r in step_rows if r["class"] == "DECREED")
    nn = sum(1 for r in step_rows if r["class"] == "NAKED")
    tot = max(1, len(step_rows))
    L += ["", "**STEP-LEVEL MIGRATION METER: FITTED %d (%.0f%%) | DECREED %d (%.0f%%) | NAKED %d (%.1f%%)**"
          % (nf, 100.0 * nf / tot, nd, 100.0 * nd / tot, nn, 100.0 * nn / tot),
         "", "## Part 2 — the no-fill cohort (%d legs placed, never filled)" % len(cohort), "",
         "| ticker | cat | bid | buys | taxonomy | forgone edge_p50 ¢ | strand? | unfilled side won? |",
         "|---|---|---|---|---|---|---|---|"]
    for c in sorted(cohort, key=lambda x: x["taxonomy"]):
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            c["tk"].replace("KX", "")[:26], c["cat"], c["bid"], c["n_buys"],
            c["taxonomy"][:70], c["forgone_edge_p50_cents"], c["strand_of_filled_sibling"],
            c["unfilled_side_won"]))
    strands = [c for c in cohort if c["strand_of_filled_sibling"]]
    sw = [c for c in strands if c["unfilled_side_won"] is True]
    L += ["", "**Strand test (June mechanism):** %d strands; unfilled-side-won verified on %d "
              "(settlement rows where determinable)." % (len(strands), len(sw)),
          "", "## Part 3 — exchange truth (three-way, audited REST path)", "",
          "exchange day buy-fills: %s across %s tickers | **violations: %d**" % (
              xt.get("n_exchange_buy_fills_day"), xt.get("n_tickers_exchange"),
              len(xt.get("violations", [])))]
    for v in xt.get("violations", [])[:20]:
        L.append("- **VIOLATION** %s: %s" % (v["kind"], json.dumps(v)[:150]))
    if xt.get("error"):
        L.append("- REST error: %s" % xt["error"])
    L += ["", "## Part 4 — class filings + fix queue (ranked by measured cost)", "",
          "| filing | instances | $ weight |", "|---|---|---|"]
    for k, v in fixq:
        L.append("| %s | %d | %.2f |" % (k, v["instances"], v["dollars"]))
    out = ROOT.parent / (".claude/adjudication/FULL_SLATE_REVIEW_%s.md" % ymd)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    summary = ("FULL-SLATE: steps FITTED %.0f%%/DECREED %.0f%%/NAKED %d | no-fill %d "
               "(starved %d) | xt-violations %d"
               % (100.0 * nf / tot, 100.0 * nd / tot, nn, len(cohort),
                  sum(1 for c in cohort if c["taxonomy"].startswith("queue_starved")),
                  len(xt.get("violations", []))))
    return out, summary, fixq
