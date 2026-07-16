#!/usr/bin/env python3
"""LIVE VALIDATION LOOP — read-only, on-box, 10-min cycle (2026-07-04).

Makes the bot's night legible in real time. NEVER touches the bot: reads the
session jsonl log + config + aim table, writes only its own artifacts and
pushes them to git so Fable can read LIVE_STATUS.md off GitHub anytime.

Per cycle over the CURRENT session (latest system_start in the newest log):
 1. ZERO-TOLERANCE doctrine violations, flagged the cycle they occur:
      grace_breach        fill past latch+300s on a latch-detected match
      combined_over_goal  completed pair combined basis > combined_goal (97)
      walk_cap_breach     premarket entry buy above conception_cell + per-cat cap
                          (only while the event has NO fills — completion/reshuffle
                          legitimately price differently after leg-1 fills)
      handler_error       any error / on_bbo_update_error event (tripwire feed)
 2. EVERY NEW FILL graded on arrival: leg, fill vs aim-table level, FV-capture
    when the gun prints (entry_minus_fv_burst), pair state (combined so far).
 3. One structured line per violation/fill/pattern -> live_validation.jsonl
    (append-once, keyed) + rolling LIVE_STATUS.md, committed+pushed on change.
 4. >=2 fires of one zero-tolerance class inside any 60-min window -> a live
    defect, not a stat: FORENSIC_<class>.md written immediately (events,
    timeline, code path) so the patch conversation starts that hour.

Usage: python3 live_validation_loop.py [--once] [--interval 600]
"""
import argparse
import json
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO = Path("/root/Omi-Workspace")
ARB = REPO / "arb-executor"
OUT = REPO / ".claude" / "live_20260705"
JSONL = OUT / "live_validation.jsonl"
STATUS = OUT / "LIVE_STATUS.md"
ET = timezone(timedelta(hours=-4))

GRACE_SEC = 300
CAT_MAP = {"KXATPMATCH": "ATP_MAIN", "KXWTAMATCH": "WTA_MAIN",
           "KXATPCHALLENGERMATCH": "ATP_CHALL", "KXWTACHALLENGERMATCH": "WTA_CHALL",
           "KXITFMATCH": "ITF_M", "KXITFWMATCH": "ITF_W"}
WALK_CAP = {"ATP_MAIN": 2, "WTA_MAIN": 2, "ATP_CHALL": 3, "WTA_CHALL": 3,
            "ITF_M": 4, "ITF_W": 4}
CODE_PATHS = {
    "grace_breach": ("latch: _is_match_live (live_v4.py ~3889, two-stage + tape-override); "
                     "grace: _v4_manage_resting_inner -> _grace_kill_action (~3260) -> "
                     "_cancel_entry_and_resolve 'match_live_cancel' (~6716). If the cancel was LATE, "
                     "check on_bbo_update ordering (_route_event before _v4_manage_resting, ~6216) "
                     "and validate_resting_buys cadence (~7372) — the 07-04 crash starved exactly this."),
    "combined_over_goal": ("entry leg2: _v4_entry_anchor leg2_reshuffle branch (~2073); walk re-aim: "
                           "_reshuffle_leg2_target (~1952); completion: _completion_target combined "
                           "ceiling; pair cap: _paired_basis_ok (T50, cap 99). combined_goal=97."),
    "walk_cap_breach": ("_walk_cap_cents (~2040); premarket walk clamp emits premarket_walk_capped in "
                        "the move_repost path (~7050). A breach = a buy above conception+cap WITHOUT "
                        "the clamp event — check liquid_repost_at_touch / join paths for a bypass."),
    "handler_error": ("traceback embedded in the event details. run() catch ~8345 (skips the rest of "
                      "the loop turn incl. last_routing_sweep update), on_bbo_update catch ~6221 "
                      "(skips _v4_manage_resting). Tripwire: [C-ERROR-TRIPWIRE] in _log."),
}


def now_et():
    return datetime.now(ET).strftime("%Y-%m-%d %I:%M:%S %p ET")


def cat_of(tk):
    return next((v for k, v in CAT_MAP.items() if tk.startswith(k)), "?")


def bucket_of(price):
    for lo, hi, name in ((1, 20, "01-20"), (21, 40, "21-40"), (41, 49, "41-49"),
                         (50, 59, "50-59"), (60, 79, "60-79"), (80, 99, "80-99")):
        if lo <= price <= hi:
            return name
    return None


def load_aim():
    try:
        return json.loads((ARB / "docs/policy/aim_table.json").read_text())["aim"]
    except Exception:
        return {}


def aim_level(aim, cat, cell):
    """Aim-table level for a leg conceived at `cell`: faller aims cell-depth,
    riser posts cell-riser_post (usually at bid)."""
    b = bucket_of(cell or 0)
    row = (aim.get(cat) or {}).get(b or "", {})
    if not row:
        return None
    off = row.get("faller_depth", 0) if (cell or 0) < 50 else row.get("riser_post", 0)
    return max(1, int(cell) - int(off or 0))


def newest_log():
    logs = sorted((ARB / "logs").glob("live_v3_*.jsonl"), key=lambda f: f.stat().st_mtime)
    return logs[-1] if logs else None


def parse_session(log_path):
    """Parse only the CURRENT session (from the last system_start)."""
    boot_ts = 0.0
    with open(log_path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if '"system_start"' in line:
                try:
                    boot_ts = json.loads(line)["ts_epoch"]
                except Exception:
                    pass
    S = {"boot": boot_ts, "fills": {}, "latch": {}, "wopen": {}, "vplace": defaultdict(list),
         "buys": defaultdict(list), "emfb": {}, "true_basis": {}, "errors": [], "graced": {}, "cancels": [],
         "capped": [], "exits": {}, "settled": {}, "events": 0, "open_bids": {}}
    with open(log_path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if '"event"' not in line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            ts = o.get("ts_epoch", 0)
            if ts < boot_ts:
                continue
            e, tk, d = o.get("event"), o.get("ticker") or "", o.get("details", {})
            S["events"] += 1
            if e == "entry_filled" and tk:
                if tk not in S["fills"]:
                    S["fills"][tk] = {"ts": ts, "fill": d.get("fill_price"), "posted": d.get("posted_price"),
                                      "dir": d.get("direction"), "play": d.get("play_type"),
                                      "qty": d.get("qty"), "src": d.get("source")}
                for oid, b in list(S["open_bids"].items()):
                    if b["tk"] == tk:
                        S["open_bids"].pop(oid, None)
            elif e == "match_live_detected":
                ev = d.get("event")
                if ev and ev not in S["latch"]:
                    S["latch"][ev] = {"ts": ts, "tts": d.get("tts_min"), "trades": d.get("trades_in_window")}
            elif e == "window_open_set" and tk and tk not in S["wopen"]:
                S["wopen"][tk] = {"cell": d.get("cell"), "price": d.get("price"), "ts": ts}
            elif e == "v4_place" and tk:
                S["vplace"][tk].append({"ts": ts, "ref": d.get("reference_source"),
                                        "anchor": d.get("anchor_src"), "tgt": d.get("target_bid"),
                                        "cell": d.get("cell"), "cur": d.get("current_price")})
            elif e == "order_placed" and d.get("action") == "buy" and tk:
                S["buys"][tk].append({"ts": ts, "price": d.get("price"), "oid": d.get("order_id")})
                oid = d.get("order_id")
                if oid and d.get("response_status") == "resting":
                    S["open_bids"][oid] = {"tk": tk, "price": d.get("price"), "ts": ts}
            elif e == "conception_stamp" and tk and tk not in S["wopen"]:
                # [C-REALITY-BELL Part 4] unlock-time conception: early-window
                # buys grade against THIS stamp; window_open_set (later) never
                # overwrites it -- the "ungradeable" lines end
                S["wopen"][tk] = {"cell": None, "price": None, "ts": ts}
            elif e == "reality_divergence" and tk:
                all_extra = S.setdefault("_extra_pats", [])
                all_extra.append({"type": "pattern", "pattern": "reality_divergence",
                                  "ticker": tk, "ts": ts, "key": f"rd|{tk}|{int(ts)}",
                                  "kind": d.get("kind"), "ref": d.get("ref"),
                                  "market_mid": d.get("market_mid"),
                                  "divergence": d.get("divergence")})
            elif e in ("chase_cap_refused", "chase_cap_hold"):
                # [C-CHASE-KILL 07-12] the named refusal IS the violation line
                # (every key the violation renderers read is present: cls,
                # detail, ticker, ts -- the MONITOR-BLIND lesson)
                all_extra = S.setdefault("_extra_pats", [])
                all_extra.append({"type": "violation", "pattern": "chase_cap",
                                  "cls": "chase_cap", "ticker": tk, "ts": ts,
                                  "key": "cc|%s|%d" % (tk, int(ts // 600)),
                                  "detail": "chase ladder refused: pursuit_buys %s >= cap %s (proposed %s)"
                                            % (d.get("pursuit_buys"), d.get("cap"),
                                               d.get("proposed", d.get("price")))})
            elif e in ("completion_flatten_capped", "completion_flatten_deferred"):
                # [C-ADJUDICATION-READ Part 4] the flatten leash's named lines
                all_extra = S.setdefault("_extra_pats", [])
                all_extra.append({"type": "violation", "pattern": "flatten_leash",
                                  "cls": "flatten_leash", "ticker": tk, "ts": ts,
                                  "key": "fl|%s|%s" % (d.get("event"), e[-8:]),
                                  "detail": ("flatten DEFERRED: ev %s above margin floor %s"
                                             % (d.get("ev_cents"), d.get("margin_floor")))
                                            if e.endswith("deferred") else
                                            ("flatten CAPPED at %s/day (%s today)"
                                             % (d.get("cap"), d.get("flatten_actions_today")))})
            elif e == "completion_taker_capped":
                # [C-DELETION-GATE Part 4] cap hits are NAMED lines, never silent
                all_extra = S.setdefault("_extra_pats", [])
                all_extra.append({"type": "violation", "pattern": "taker_capped",
                                  "cls": "taker_capped", "ticker": tk, "ts": ts,
                                  "key": "tcap|%s" % d.get("event"),
                                  "detail": "taker verdict DEFERRED at daily cap %s (%s today; sunset n>=30 graded)"
                                            % (d.get("cap"), d.get("taker_actions_today"))})
            elif e == "self_fill_bell":
                all_extra = S.setdefault("_extra_pats", [])
                all_extra.append({"type": "violation", "pattern": "self_fill_bell",
                                  "cls": "self_fill_bell",
                                  "ticker": tk or d.get("event"), "ts": ts,
                                  "key": "sfb|%s" % d.get("event"),
                                  "detail": "own buys rose %sc (%s->%s) in %ss -> match-live presumption, entry buys FROZEN"
                                            % (d.get("rise"), d.get("from_cents"),
                                               d.get("to_cents"), d.get("window_sec"))})
            elif e == "w2_fill_violation":
                # [C-TAPE-BELL v1 Part 2, 07-15] W2 fill = ZERO TOLERANCE,
                # no exceptions (the 75-fill morning; LEOTSI -315c the
                # walked example). booking_source distinguishes adoption
                # lag IN the forensic, never exempts it.
                all_extra = S.setdefault("_extra_pats", [])
                all_extra.append({"type": "violation", "pattern": "w2_fill",
                                  "cls": "w2_fill",
                                  "ticker": tk or d.get("event"), "ts": ts,
                                  "key": "w2f|%s|%d" % (tk or d.get("event"),
                                                        int(ts)),
                                  "detail": "W2 FILL (buy after start): %sc x%s "
                                            "booking=%s gun=%s"
                                            % (d.get("fill_price"), d.get("qty"),
                                               d.get("booking_source"),
                                               d.get("gun_source"))})
            elif e == "bell_missing":
                all_extra = S.setdefault("_extra_pats", [])
                # [07-11 FIX] every type=="violation" item MUST carry "cls" --
                # forensic_check groups on it; this one shipped without it and
                # the first live bell_missing (04:10 am) crashed every cycle after.
                all_extra.append({"type": "violation", "pattern": "bell_missing",
                                  "cls": "bell_missing",
                                  "event": d.get("event"), "ticker": d.get("event"),
                                  "ts": ts, "key": f"bm|{d.get('event')}",
                                  "min_past_start": d.get("min_past_start")})
            elif e == "orphan_readopted_fingerprint" and tk:
                # [RENDER FIX 07-10, the PAPJER-PAP question] boot-readopted
                # resting bids emit no v4_place/order_placed this session --
                # without this branch they are bot-OWNED but monitor-INVISIBLE
                # (the render-only gap the adoption dispatch named).
                oid = d.get("order_id")
                if oid and oid not in S["open_bids"]:
                    S["open_bids"][oid] = {"tk": tk, "price": d.get("price"), "ts": ts}
                    S["buys"][tk].append({"ts": ts, "price": d.get("price"), "oid": oid})
            elif e == "fv_burst_anchor" and tk:
                S["emfb"][tk] = d.get("entry_minus_fv_burst")
            elif e == "adoption_true_basis" and tk:
                # [ZT2-FIX 07-06] the bot's C-TRUE-BASIS event: cost basis for an adopted
                # fill (pos_map avg is mark-to-market, A54 — the 7 fabricated overnight
                # combined_over_goal rows). Recorded per ticker; ZT2 grades with THIS.
                S["true_basis"][tk] = d.get("true_basis")
            elif e in ("reconcile_v4_adopted", "reconcile_v4_exit_found") and tk and tk not in S["fills"]:
                # boot re-adoptions that do NOT re-emit entry_filled (exit_found path):
                # without these the board loses open pairs across restarts. exit_found
                # carries no avg -> cell_id (derived from entry basis) stands in.
                _basis = d.get("avg", d.get("cell_id"))
                S["fills"][tk] = {"ts": ts, "fill": _basis, "posted": _basis, "dir": "",
                                  "play": e, "qty": d.get("qty"), "src": e}
            elif e in ("error", "on_bbo_update_error"):
                S["errors"].append({"ts": ts, "kind": e, "err": str(d.get("error"))[:160]})
            elif e == "match_live_grace_armed":
                S["graced"][tk or d.get("event")] = ts
            elif e in ("match_live_resting_cancel", "order_cancelled"):
                S["cancels"].append({"ts": ts, "tk": tk, "e": e,
                                     "label": d.get("label"), "ok": d.get("success"), "graced": d.get("graced")})
                if e == "order_cancelled" and d.get("success") is not False:
                    S["open_bids"].pop(d.get("order_id"), None)
            elif e == "premarket_walk_capped" and tk:
                S["capped"].append({"ts": ts, "tk": tk, **{k: d.get(k) for k in
                                    ("proposed_target", "walk_ceiling", "conception_cell", "cap")}})
            elif e == "exit_filled" and tk:
                S["exits"][tk] = {"ts": ts, "pnl": d.get("pnl_cents")}
            elif e == "settled" and tk:
                S["settled"][tk] = {"ts": ts, "settle": d.get("settle"), "pnl": d.get("pnl_cents")}
    return S


def _read_tape_since(tk, since_ts):
    """Prints on `tk` since epoch since_ts, from the bot's own trade CSV recorder."""
    f = ARB / "analysis" / "trades" / (tk + ".csv")
    out = []
    if not f.exists():
        return out
    try:
        for ln in f.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
            p = ln.split(",")
            if len(p) < 5:
                continue
            try:
                ts = datetime.strptime(p[0], "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=ET).timestamp()
            except Exception:
                continue
            if ts >= since_ts:
                out.append({"ts": ts, "price": int(p[2]), "count": int(float(p[3])), "side": p[4]})
    except Exception:
        pass
    return out


def _read_bbo(tk):
    """Latest recorded top-of-book for `tk` from the premarket_ticks recorder."""
    f = ARB / "analysis" / "premarket_ticks" / (tk + ".csv")
    if not f.exists():
        return None
    try:
        with open(f, "rb") as fh:
            fh.seek(0, 2)
            fh.seek(max(0, fh.tell() - 4096))
            last = fh.read().decode("utf-8", "replace").strip().splitlines()[-1].split(",")
        return {"bid": int(last[2]), "ask": int(last[12]), "ts_et": last[0]}
    except Exception:
        return None


# [C-FLOW-STATE 07-08] provisional per-cat thresholds -- the early-canvas study
# fits the real ones from the corpus; until then these encode the HOURLY_APPENDIX
# shape (ITF: wide silent lattice -> prints appear late; mains: 1c-spread liquid
# all day so rate alone separates; CHALL intermediate). PROVISIONAL by name.
FLOW_OPEN_RATE = {"ITF_M": 0.2, "ITF_W": 0.2, "ATP_CHALL": 0.3, "WTA_CHALL": 0.3,
                  "ATP_MAIN": 0.5, "WTA_MAIN": 0.5}
FLOW_OPEN_SPREAD = {"ITF_M": 3, "ITF_W": 3, "ATP_CHALL": 2, "WTA_CHALL": 2,
                    "ATP_MAIN": 1, "WTA_MAIN": 1}
FLOW_WINDOW_MIN = 30


def flow_state_gauge(S, now=None):
    """[C-FLOW-STATE 07-08] per-game, per-cat print-rate / flow-state gauge
    (operator doctrine 2026-07-08: early quiet is VOLUME-conditional, not
    time-conditional -- the per-game flow-state is the primitive). Read-only
    over the same local tape the bid-grader uses. States:
      QUIET   no prints in the window and the lattice is wide
      WAKING  prints exist OR the spread has tightened to near-open
      OPEN    sustained prints (rate >= per-cat) AND spread <= per-cat
    One gauge row per tracked game; one append-once jsonl line per state first
    reached per session (key carries the boot ts). Thresholds provisional until
    the early-canvas study fits them."""
    now = now or time.time()
    events = {}
    for tk in set(list(S["fills"].keys())
                  + [b["tk"] for b in S["open_bids"].values()]):
        ev = tk.rsplit("-", 1)[0]
        events.setdefault(ev, set()).add(tk)
    rows, lines = [], []
    for ev, tks in sorted(events.items()):
        cat = cat_of(ev)
        prints, spreads = [], []
        for tk in tks:
            prints += _read_tape_since(tk, now - FLOW_WINDOW_MIN * 60)
            b = _read_bbo(tk)
            if b and 0 < b["bid"] < b["ask"]:
                spreads.append(b["ask"] - b["bid"])
        rate = round(len(prints) / float(FLOW_WINDOW_MIN), 3)
        spread = min(spreads) if spreads else None
        o_rate = FLOW_OPEN_RATE.get(cat, 0.3)
        o_spr = FLOW_OPEN_SPREAD.get(cat, 2)
        if rate >= o_rate and spread is not None and spread <= o_spr:
            state = "OPEN"
        elif prints or (spread is not None and spread <= o_spr + 2):
            state = "WAKING"
        else:
            state = "QUIET"
        rows.append({"event": ev, "cat": cat, "rate": rate, "spread": spread,
                     "prints": len(prints), "state": state})
        lines.append({"key": "flow:%d:%s:%s" % (int(S["boot"]), ev, state),
                      "type": "flow_state", "ts": now, "event": ev, "cat": cat,
                      "state": state, "prints_per_min": rate, "spread": spread,
                      "window_min": FLOW_WINDOW_MIN, "provisional": True})
    return rows, lines


def grade_resting_bids(S, aim, goal):
    """Tape-grade every open resting entry bid. Classes (honest, per doctrine):
    FLOW_AT_LEVEL  prints AT/below our bid but we're unfilled -> queue problem
    FLOW_ABOVE     prints above our bid (gap 1-4c = the near-miss REPRICEABLE class,
                   bounded by min(aim, goal - sibling_basis) -- chasing flow past
                   that bound breaks the 97 doctrine and is NOT recommended)
    NO_FLOW        genuinely no prints since post -- the ONLY class that earns
                   the word starvation."""
    graded = []
    for oid, b in S["open_bids"].items():
        tk, lvl, ts0 = b["tk"], int(b["price"] or 0), b["ts"]
        ev = tk.rsplit("-", 1)[0]
        tape = _read_tape_since(tk, ts0)
        bbo = _read_bbo(tk)
        sib_fill = next((f["fill"] for x, f in S["fills"].items()
                         if x.rsplit("-", 1)[0] == ev and x != tk), None)
        cell = (S["wopen"].get(tk) or {}).get("cell")
        al = aim_level(aim, cat_of(tk), cell) if cell else None
        bound = min(x for x in (al, (goal - sib_fill) if sib_fill else None, 99) if x is not None)
        if tape:
            min_p = min(t["price"] for t in tape)
            max_p = max(t["price"] for t in tape)
            sz = sum(t["count"] for t in tape)
            gap = min_p - lvl
            if gap <= 0:
                cls = "FLOW_AT_LEVEL"
            else:
                cls = "FLOW_ABOVE"
        else:
            min_p = max_p = sz = None
            gap = None
            cls = "NO_FLOW"
        reprice = min(min_p, bound) if min_p is not None else None
        graded.append({
            "oid": oid, "ticker": tk, "event": ev, "level": lvl,
            "age_min": round((time.time() - ts0) / 60.0),
            "prints": len(tape), "print_min": min_p, "print_max": max_p, "print_sz": sz,
            "bbo": bbo, "gap": gap, "cls": cls,
            "sib_basis": sib_fill, "aim_level": al, "reprice_bound": bound,
            "repriceable": (cls == "FLOW_ABOVE" and gap is not None and gap <= 4
                            and reprice is not None and reprice > lvl),
            "reprice_to": reprice,
            "doctrine_note": ("flow above but bound %sc < flow -- chasing breaks goal" % bound
                              if (cls == "FLOW_ABOVE" and min_p is not None and bound < min_p) else "")})
    return graded


def could_have_filled(S, goal):
    """Per open pair (one leg filled, sibling not): achievable-combined-RIGHT-NOW =
    filled basis + sibling's current fillable level (its ask). What the board is
    leaving on the table while bids rest."""
    rows = []
    ev_fills = defaultdict(list)
    for tk, f in S["fills"].items():
        ev_fills[tk.rsplit("-", 1)[0]].append((tk, f))
    for ev, legs in ev_fills.items():
        if len(legs) != 1:
            continue
        tk, f = legs[0]
        sib = None
        for otk in list(S["wopen"]) + [b["tk"] for b in S["open_bids"].values()]:
            if otk.rsplit("-", 1)[0] == ev and otk != tk:
                sib = otk
                break
        if not sib:
            continue
        bbo = _read_bbo(sib)
        if not bbo or not bbo.get("ask"):
            continue
        ach = (f["fill"] or 0) + bbo["ask"]
        rows.append({"event": ev, "filled_tk": tk, "basis": f["fill"], "sib": sib,
                     "sib_ask": bbo["ask"], "achievable": ach, "goal": goal,
                     "vs_goal": ach - goal})
    return rows


def analyze(S, aim, goal, bid_grades=None):
    items = []   # structured jsonl candidates, each with a unique 'key'
    bid_grades = bid_grades or []
    ev_fills = defaultdict(list)
    for tk, f in S["fills"].items():
        ev_fills[tk.rsplit("-", 1)[0]].append((tk, f))
    grade_by_tk = {g["ticker"]: g for g in bid_grades}

    # ---- resting bids: emit one line per (bid, class) -- re-emits only on class change ----
    for g in bid_grades:
        items.append({"key": f"bidgrade:{g['oid']}:{g['cls']}", "type": "bid_grade",
                      "ts": time.time(), **{k: g[k] for k in
                      ("ticker", "event", "level", "age_min", "prints", "print_min",
                       "print_max", "print_sz", "gap", "cls", "sib_basis",
                       "reprice_bound", "repriceable", "reprice_to", "doctrine_note")}})

    # ---- fills graded ----
    for tk, f in sorted(S["fills"].items(), key=lambda x: x[1]["ts"]):
        ev = tk.rsplit("-", 1)[0]
        # Δaim resolution chain (NO '?' allowed): placement cell -> window-open
        # cell -> the fill price's own bucket (estimate). Adoptions of positions
        # the bot never aimed are labeled, not question-marked.
        vp_cells = [v["cell"] for v in S["vplace"].get(tk, []) if v.get("cell") is not None
                    and v["ts"] <= f["ts"]]
        cell = (vp_cells[-1] if vp_cells else None) or (S["wopen"].get(tk) or {}).get("cell")
        aim_src = "place_cell" if vp_cells else ("window_cell" if cell else None)
        adopted = str(f.get("play") or "").startswith(("v4_manual", "v4_reconciled",
                     "reconcile_v4")) or (f.get("src") or "").startswith("reconcile")
        if cell is None and f["fill"] is not None:
            cell = f["fill"]
            aim_src = "adopted_est" if adopted else "fill_est"
        al = aim_level(aim, cat_of(tk), cell) if cell is not None else None
        sibs = [x for x in ev_fills[ev] if x[0] != tk]
        combined = (f["fill"] or 0) + sum((x[1]["fill"] or 0) for x in sibs) if sibs else None
        lat = S["latch"].get(ev)
        mins_after_latch = round((f["ts"] - lat["ts"]) / 60.0, 1) if lat and f["ts"] >= lat["ts"] else None
        dam = (f["fill"] - al) if (al is not None and f["fill"] is not None) else None
        # [CAUSAL-AUDIT STANDING] EARNED/GIFT stamp + chain on every ledger row.
        # EARNED = the doctrine's mechanism demonstrably produced the price:
        # faller filled below window-open (dip delivered to our level) or entry
        # below burst-FV. GIFT = price at/above open/FV, outcome rides the tape
        # (the riser-side concession class: riser_post~0 = zero-discount by design).
        wo_price = (S["wopen"].get(tk) or {}).get("price")
        disc = (wo_price - f["fill"]) if (wo_price is not None and f["fill"] is not None) else None
        emfb0 = S["emfb"].get(tk)
        side = "faller" if ((f["dir"] == "underdog") or ((f["fill"] or 50) < 50)) else "riser"
        if (side == "faller" and disc is not None and disc >= 3) or (emfb0 is not None and emfb0 <= -3):
            stamp = "EARNED"
        elif (emfb0 is not None and emfb0 >= 3) or (side == "riser" and disc is not None and disc <= 2):
            stamp = "GIFT_CLASS"   # design-conceded discount; outcome = tape
        else:
            stamp = "MIXED" if disc is not None or emfb0 is not None else "PENDING"
        chain = sorted({m for v in S["vplace"].get(tk, []) if v.get("ref") for m in [v["ref"]]})
        items.append({"key": f"fill:{tk}", "type": "fill", "ts": f["ts"], "ticker": tk,
                      "stamp": stamp, "side": side, "disc_vs_open": disc, "chain": chain,
                      "cat": cat_of(tk), "dir": f["dir"], "play": f["play"], "fill": f["fill"],
                      "posted": f["posted"], "conception_cell": cell, "aim_level": al,
                      "aim_src": aim_src, "fill_minus_aim": dam,
                      "mins_after_latch": mins_after_latch,
                      "pair_state": ("pair" if sibs else "single"), "combined": combined})
        if al is not None:
            # one-time regrade line (the Δaim backfill for fills first seen with '?')
            items.append({"key": f"fillaim:{tk}", "type": "fill_regrade", "ts": f["ts"],
                          "ticker": tk, "fill": f["fill"], "aim_level": al,
                          "aim_src": aim_src, "fill_minus_aim": dam})
        emfb = S["emfb"].get(tk)
        if emfb is not None:
            items.append({"key": f"fv:{tk}", "type": "fv_capture", "ts": f["ts"], "ticker": tk,
                          "entry_minus_fv_burst": emfb,
                          "verdict": ("paid_by_dip" if emfb > 0 else "zero_or_above_FV")})
            if emfb <= -8:
                items.append({"key": f"deepneg:{tk}", "type": "pattern", "pattern": "deep_neg_fv",
                              "ts": f["ts"], "ticker": tk, "entry_minus_fv_burst": emfb})

    # ---- ZT 1: grace_breach ----
    for tk, f in S["fills"].items():
        ev = tk.rsplit("-", 1)[0]
        lat = S["latch"].get(ev)
        if lat and f["ts"] > lat["ts"] + GRACE_SEC:
            items.append({"key": f"zt:grace_breach:{tk}", "type": "violation", "cls": "grace_breach",
                          "ts": f["ts"], "ticker": tk, "event": ev,
                          "mins_past_latch": round((f["ts"] - lat["ts"]) / 60.0, 1),
                          "latch_ts": lat["ts"], "fill": f["fill"], "detail":
                          f"fill {f['fill']}c {round((f['ts']-lat['ts'])/60.0,1)}min past latch (grace {GRACE_SEC}s)"})

    # ---- ZT 2: combined_over_goal (path-tagged: defect vs armed-design bounds) ----
    # [ZT2-FIX 07-06] adopted fills grade at TRUE basis (adoption_true_basis event,
    # C-TRUE-BASIS b8a73a55). An adopted leg with NO true-basis event (pre-fix booking,
    # mark-to-market) is UNVERIFIED -> the pair emits a pattern, never a ZT violation
    # (the 07-06 autopsy: 7/16 overnight rows were booking artifacts, orders AT bound).
    for ev, legs in ev_fills.items():
        if len(legs) >= 2:
            comb = 0; unverified = False
            for tk, f in legs:
                px = f["fill"] or 0
                if S["true_basis"].get(tk) is not None:
                    px = S["true_basis"][tk]
                elif (f.get("src") or "").startswith("reconcile") or f.get("play") in ("v4_reconciled", "reconcile_v4_adopted"):
                    unverified = True
                comb += px
            if comb > goal and unverified:
                items.append({"key": f"ubc:{ev}", "type": "pattern",
                              "pattern": "combined_over_goal_UNVERIFIED_BASIS", "ts": max(f["ts"] for _, f in legs),
                              "event": ev, "combined": comb,
                              "detail": f"pair combined {comb}c > {goal}c but an adopted leg has mark-to-market basis (pre-TRUE-BASIS booking) — exchange-truth check required, NOT a ZT row"})
                continue
            if comb > goal:
                last_ts = max(f["ts"] for _, f in legs)
                plays = {(f.get("play") or "") + "/" + (f.get("src") or "") for _, f in legs}
                blob = " ".join(plays)
                if "complete_cross" in blob:
                    path, design = "complete_cross_insurance", "cap102 by design (d?)"
                elif "completion_reprice" in blob:
                    path, design = "completion_ceiling", "cap99 by design (d2ac207)"
                elif "fallback" in blob:
                    path, design = "t20m_fallback", "DEFECT until C-FALLBACK-BOUND (733341f)"
                else:
                    path, design = "organic", "DEFECT-CLASS"
                items.append({"key": f"zt:combined_over_goal:{ev}", "type": "violation",
                              "cls": "combined_over_goal", "ts": last_ts, "event": ev,
                              "combined": comb, "goal": goal, "path": path,
                              "legs": [{"tk": tk, "fill": f["fill"]} for tk, f in legs],
                              "detail": f"pair combined {comb}c > goal {goal}c [{path}: {design}]"})

    # ---- ZT 3: walk_cap_breach (premarket only: event has NO fills yet at buy time) ----
    for tk, buys in S["buys"].items():
        ev = tk.rsplit("-", 1)[0]
        cell = (S["wopen"].get(tk) or {}).get("cell")
        if not cell:
            continue
        ceiling = int(cell) + WALK_CAP.get(cat_of(tk), 3)
        _wo_ts = (S["wopen"].get(tk) or {}).get("ts")
        for b in buys:
            ev_fill_before = any(f["ts"] <= b["ts"] for x, f in S["fills"].items()
                                 if x.rsplit("-", 1)[0] == ev)
            if ev_fill_before or b["price"] is None or b["price"] <= ceiling:
                continue
            # [ZT3-FIX 07-06] a buy that PRECEDES the conception stamp is ungradeable
            # against it — the honest clock opens windows hours before the legacy T-240
            # stamp exists (10/19 overnight rows were retroactive false positives).
            # Info pattern, never a ZT row.
            if _wo_ts is not None and b["ts"] < _wo_ts:
                items.append({"key": f"precon:{tk}:{int(b['ts'])}", "type": "pattern",
                              "pattern": "pre_conception_buy", "ts": b["ts"], "ticker": tk,
                              "price": b["price"], "conception_ts": _wo_ts,
                              "detail": f"buy {b['price']}c predates the conception stamp by {round((_wo_ts-b['ts'])/60)}min — honest-window buy, cap not yet defined (ungradeable)"})
                continue
            vp = [v for v in S["vplace"][tk] if abs(v["ts"] - b["ts"]) < 10]
            ref = vp[-1]["ref"] if vp else None
            if ref is None:
                # no v4_place correlation = completion/fallback/cross posting sites
                # (their pricing is governed by their own bounds, not the premarket
                # walk cap -- JANRYA 07-05 false positive). Info line, not ZT.
                items.append({"key": f"uncorr:{tk}:{int(b['ts'])}", "type": "pattern",
                              "pattern": "uncorrelated_buy_above_ceiling", "ts": b["ts"],
                              "ticker": tk, "price": b["price"], "ceiling": ceiling})
                continue
            items.append({"key": f"zt:walk_cap_breach:{tk}:{int(b['ts'])}", "type": "violation",
                          "cls": "walk_cap_breach", "ts": b["ts"], "ticker": tk,
                          "price": b["price"], "conception_cell": cell, "ceiling": ceiling,
                          "ref_source": ref, "detail":
                          f"buy {b['price']}c > ceiling {ceiling}c (conception {cell} + cap) ref={ref}"})

    # ---- ZT 4: handler_error ----
    for er in S["errors"]:
        items.append({"key": f"zt:handler_error:{int(er['ts']*1000)}", "type": "violation",
                      "cls": "handler_error", "ts": er["ts"], "kind": er["kind"],
                      "detail": er["err"]})

    # ---- pattern: half-arm aging (single fill >30min, sibling unfilled) ----
    # mode comes from the SIBLING BID'S TAPE, not from whether it merely rested:
    # NO_FLOW is the only case that earns the word starvation.
    now = time.time()
    for ev, legs in ev_fills.items():
        if len(legs) == 1 and (now - legs[0][1]["ts"]) > 1800:
            tk, f = legs[0]
            sib_g = next((g for g in bid_grades if g["event"] == ev and g["ticker"] != tk), None)
            if sib_g is None:
                sib_rested = any(x.rsplit("-", 1)[0] == ev and x != tk for x in S["buys"])
                mode = "NO_BID(sib rested earlier, none now)" if sib_rested else "PAIRING(sib never rested)"
            else:
                mode = {"NO_FLOW": "STARVATION(no prints since post)",
                        "FLOW_AT_LEVEL": "QUEUE(flow at/below our level, unfilled)",
                        "FLOW_ABOVE": "SET_BELOW_FLOW(prints %sc above)" % sib_g["gap"]}[sib_g["cls"]]
            items.append({"key": f"halfarm:{ev}", "type": "pattern", "pattern": "half_arm_aging",
                          "ts": f["ts"], "event": ev, "ticker": tk, "fill": f["fill"],
                          "age_min": round((now - f["ts"]) / 60.0), "mode": mode})
    return items


def forensic_check(all_lines, S, log_path):
    """>=2 fires of one ZT class inside any 60-min window -> forensic block file."""
    written = []
    by_cls = defaultdict(list)
    for it in all_lines:
        if it.get("type") == "violation":
            by_cls[it["cls"]].append(it)
    for cls, vs in by_cls.items():
        vs.sort(key=lambda x: x["ts"])
        burst = None
        for i in range(1, len(vs)):
            if vs[i]["ts"] - vs[i - 1]["ts"] <= 3600:
                burst = (vs[i - 1], vs[i])
        if not burst:
            continue
        fp = OUT / f"FORENSIC_{cls}.md"
        stamp = f"{int(burst[1]['ts'])}"
        if fp.exists() and stamp in fp.read_text(encoding="utf-8", errors="replace"):
            continue    # this exact pair already written
        lines = [f"# FORENSIC — {cls} — LIVE DEFECT (>=2 in 60min)  <!-- {stamp} -->",
                 f"written {now_et()} by live_validation_loop (read-only). "
                 f"Patch conversation starts NOW.", "",
                 f"## Events ({len(vs)} total this session)"]
        for v in vs:
            # [07-11 FIX] not every violation item carries "detail" (bell_missing
            # doesn't) -- render whatever fields it has instead of crashing.
            det = v.get("detail") or json.dumps({k: x for k, x in v.items()
                                                 if k not in ("type", "key", "ts", "cls")})
            lines.append(f"- {datetime.fromtimestamp(v['ts'], ET).strftime('%H:%M:%S')} "
                         f"{v.get('ticker') or v.get('event') or ''} — {det}")
        lines += ["", "## Timeline (raw log lines for the burst pair)"]
        keys = {v.get("ticker") or v.get("event") or "" for v in burst if (v.get("ticker") or v.get("event"))}
        if keys:
            with open(log_path, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if any(k and k in line for k in keys):
                        lines.append("    " + line.strip()[:400])
        lines += ["", "## Code path", CODE_PATHS.get(cls, "?"), ""]
        fp.write_text("\n".join(lines), encoding="utf-8")
        written.append(fp.name)
    return written


def drain_replay_violations(log_path):
    """[C-DRAIN-REPLAY watch 07-10] ZERO-TOLERANCE: every entry order alive
    pre-drain (order_cancelled label=shutdown_cancel in the 30 min before the
    last boot) must be filled, re-placed, or refusal-NAMED (drain_replay /
    order_placed buy / entry_filled on the same ticker) within 10 min
    post-boot -- else VIOLATION. The PAPJER-PAP class (45f12259, 07-09
    11:14 pm): the old monitor watched it happen and said zero violations."""
    ev = []
    try:
        for line in open(log_path, encoding="utf-8", errors="replace"):
            if not any(k in line for k in ('"shutdown_cancel"', '"system_start"',
                                           '"drain_replay"', '"order_placed"',
                                           '"entry_filled"')):
                continue
            try:
                ev.append(json.loads(line))
            except ValueError:
                continue
    except OSError:
        return []
    boots = [d.get("ts_epoch", 0) for d in ev if d.get("event") == "system_start"]
    if not boots:
        return []
    boot = boots[-1]
    drained = {}
    for d in ev:
        if (d.get("event") == "order_cancelled"
                and (d.get("details") or {}).get("label") == "shutdown_cancel"
                and boot - 1800 <= d.get("ts_epoch", 0) <= boot):
            drained[d.get("ticker", "")] = d.get("ts", "?")
    if not drained:
        return []
    resolved = set()
    for d in ev:
        ts = d.get("ts_epoch", 0)
        if not (boot < ts <= boot + 600):
            continue
        det = d.get("details") or {}
        if (d.get("event") == "drain_replay"
                or (d.get("event") == "order_placed" and det.get("action") == "buy")
                or d.get("event") == "entry_filled"):
            resolved.add(d.get("ticker", ""))
    if time.time() < boot + 600:
        return []   # window still open -- judge only after it closes
    return [{"ticker": tk, "drained_at": ts} for tk, ts in sorted(drained.items())
            if tk not in resolved]


def write_status(S, all_lines, log_path, cycle_n, forensics, bid_grades=None, chf=None,
                 chf_cum=(0, 0), flow_rows=None):
    v = [x for x in all_lines if x.get("type") == "violation"]
    fills = [x for x in all_lines if x.get("type") == "fill"]
    pats = [x for x in all_lines if x.get("type") == "pattern"]
    fvs = {x["ticker"]: x for x in all_lines if x.get("type") == "fv_capture"}
    bid_grades = bid_grades or []
    chf = chf or []
    sha = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
                         capture_output=True, text=True).stdout.strip()
    L = [f"# LIVE VALIDATION — rolling status", "",
         f"- cycle {cycle_n} @ **{now_et()}** | build `{sha}` | session boot "
         f"{datetime.fromtimestamp(S['boot'], ET).strftime('%m-%d %H:%M ET') if S['boot'] else '?'} "
         f"| log `{log_path.name}` | {S['events']} session events | monitor READ-ONLY",]
    # [C-WINDOW-LAW Part 5, 07-14] gun-feed staleness header tripwire:
    # > 30 min since the last NEW in-play sighting prints at the top
    # (arrival-gap honest label; the corridor's closing boundary is only
    # as honest as this feed).
    try:
        import sqlite3 as _sq9
        _osdb = REPO / "arb-executor/state/observed_starts.db"
        _src9 = str(_osdb) if _osdb.exists() else \
            str(REPO / "arb-executor/tennis.db")
        _con9 = _sq9.connect("file:%s?mode=ro" % _src9, uri=True, timeout=2)
        _mx9 = _con9.execute(
            "SELECT MAX(inserted_at) FROM observed_starts").fetchone()[0]
        _con9.close()
        if _mx9:
            _age9 = (datetime.now() - datetime.strptime(
                _mx9, "%Y-%m-%d %H:%M:%S")).total_seconds() / 60.0
            if _age9 > 30:
                L.append("")
                L.append("## ⚠ GUN FEED: last new in-play sighting %.0f "
                         "min ago (>30 tripwire; source %s)" %
                         (_age9, Path(_src9).name))
    except Exception:
        pass
    # [C-RESUME-CHECK Part 4, 07-14, DECREED] the ntfy channel publishes to
    # an UNSUBSCRIBED topic — THIS RENDER is the operator's real phone.
    # While the packet is fired and the default-GO clock runs, the numbers,
    # the deadline, and the STOP procedure lead the render, verbatim.
    try:
        _pk9 = json.loads((REPO / ".claude/trendpath/PACKET_STATUS.json")
                          .read_text(encoding="utf-8"))
        if _pk9.get("fired") and not (_pk9.get("cutover_done")
                                      or {}).get("verified"):
            _dl9 = _pk9.get("go_deadline_epoch")
            _dls9 = (datetime.fromtimestamp(_dl9, ET).strftime(
                "%m-%d %I:%M %p ET") if _dl9 else "?")
            _sm9 = _pk9.get("summary", {})

            def _pl9(k):
                s9 = _sm9.get(k, {})
                return ("- %s: n=%s | delta $%+.2f (CI %s) | yield %.1f%% "
                        "(pess %.1f%%) | **%s**"
                        % (k.upper(), s9.get("n"), s9.get("delta", 0),
                           s9.get("ci"), s9.get("yield_pct", 0),
                           s9.get("yield_pess_pct", 0), s9.get("door", "?")))
            L += ["",
                  "## ⚠ CONSOLIDATED PACKET FIRED — DEFAULT-GO DEADLINE "
                  "**" + _dls9 + "** ⚠",
                  _pl9("path"), _pl9("reach"), _pl9("selector"),
                  "- go_state: %s" % _pk9.get("go_state"),
                  "- **STOP PROCEDURE (verbatim): say STOP to the relay; "
                  "CC creates `.claude/trendpath/OPERATOR_STOP` on the VPS; "
                  "its presence permanently halts auto_cutover. Silence "
                  "past the deadline = `trendpath_live` flips on the next "
                  "boot with full audit (deploy/auto_cutover.sh, 30-min "
                  "cron).**"]
    except Exception:
        pass
    # [C-VAULT-WIRED-ENTRY v1 Part 4, 07-14] dossier lines on the render:
    # the last placements/refusals with their consulted surfaces, compact.
    try:
        _dos9 = []
        for _ln9 in open(log_path, encoding="utf-8", errors="replace"):
            if '"entry_dossier"' in _ln9:
                try:
                    _dos9.append(json.loads(_ln9))
                except Exception:
                    pass
        _dos9 = _dos9[-4:]
        if _dos9:
            L += ["", "## ENTRY DOSSIERS (vault-wired: every surface "
                      "consulted or named — last %d)" % len(_dos9)]
            for x9 in _dos9:
                d9 = x9.get("details") or {}
                sf9 = d9.get("surfaces") or {}
                stat9 = ",".join("%s:%s" % (k[:12],
                                            (v or {}).get("status", "?")[:4])
                                 for k, v in sf9.items())
                L.append("- %s %s aim=%s | %s" % (
                    d9.get("decision"), (x9.get("ticker") or "")[-14:],
                    d9.get("aim"), stat9[:220]))
    except Exception:
        pass
    # [MORNING REVIEW 07-10, operator standing order] watches that fire
    # overnight are the FIRST thing read at the AM checkpoint, never buried
    # at line 396 (deep_neg_fv was). Overnight = midnight..9am ET today.
    try:
        _now = datetime.now(ET)
        _mid = datetime(_now.year, _now.month, _now.day, tzinfo=ET).timestamp()
        _nine = _mid + 9 * 3600
        _overnight = [p for p in pats if _mid <= p.get("ts", 0) <= _nine]
        _dv0 = drain_replay_violations(log_path)
        L += ["", f"## MORNING REVIEW — overnight watch fires (12:00 AM–9:00 AM ET)"
                  f" — {len(_overnight) + len(_dv0)} item(s)"]
        if _overnight or _dv0:
            for p in sorted(_overnight, key=lambda y: y["ts"]):
                L.append(f"- **{p['pattern']}**: {p.get('ticker') or p.get('event')} "
                         f"{json.dumps({k: p[k] for k in p if k not in ('key','type','pattern','ts','ticker','event')})}")
            for x in _dv0:
                L.append(f"- **DRAIN-REPLAY VIOLATION**: `{x['ticker']}` drained {x['drained_at']}")
        else:
            L.append("clean overnight — no watch fires")
    except Exception:
        pass
    L += [
         f"- tripwire artifact: "
         f"{'**PRESENT — CHECK /tmp/live_v4_TRIPWIRE.json**' if Path('/tmp/live_v4_TRIPWIRE.json').exists() else 'absent (quiet)'}",
         "", f"## ZERO-TOLERANCE — {len(v)} violation(s)"]
    if not v:
        L.append("**NONE.** grace_breach / combined_over_goal(97) / walk_cap_breach / handler_error all clean.")
    else:
        L.append("| ET | class | who | detail |")
        L.append("|---|---|---|---|")
        for x in sorted(v, key=lambda y: y["ts"]):
            # [07-11 FIX, 3rd site of the family] bell_missing carries no "detail"
            xdet = x.get("detail") or ("min_past_start %s" % x.get("min_past_start")
                                       if x.get("pattern") == "bell_missing" else "")
            L.append(f"| {datetime.fromtimestamp(x['ts'], ET).strftime('%H:%M:%S')} | **{x['cls']}** | "
                     f"{x.get('ticker') or x.get('event') or x.get('kind','')} | {xdet[:140]} |")
    if forensics:
        L += ["", f"**LIVE DEFECT(S) — forensic blocks written: {', '.join(forensics)}**"]
    L += ["", f"## FILLS — {len(fills)} graded (session)"]
    if fills:
        L += ["| ET | ticker | cat | dir | fill | aim | Δaim | FV(emfb) | latch+min | pair | comb | stamp |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for f in sorted(fills, key=lambda y: y["ts"]):
            fv = fvs.get(f["ticker"], {}).get("entry_minus_fv_burst")
            dam = (f"{f['fill_minus_aim']:+d}" if f["fill_minus_aim"] is not None else "n/a")
            src = f.get("aim_src") or "none"
            L.append(f"| {datetime.fromtimestamp(f['ts'], ET).strftime('%H:%M')} | {f['ticker'].replace('KX','')[:34]} "
                     f"| {f['cat']} | {f['dir'] or '?'} | {f['fill']} | {f['aim_level'] if f['aim_level'] is not None else 'n/a'} "
                     f"| {dam} ({src}) "
                     f"| {fv if fv is not None else '—'} | {f['mins_after_latch'] if f['mins_after_latch'] is not None else 'pre'} "
                     f"| {f['pair_state']} | {f['combined'] or ''} | {f.get('stamp','')} |")
    else:
        L.append("none yet this session")
    cls_ct = defaultdict(int)
    rp_t = rp_f = 0
    for g in bid_grades:
        cls_ct[g["cls"]] += 1
        if g["repriceable"]:
            rp_t += 1
        else:
            rp_f += 1
    cum = chf_cum if isinstance(chf_cum, tuple) else (0, 0)
    L += ["", f"## RESTING BIDS — {len(bid_grades)} tape-graded (starvation = NO_FLOW only)",
          f"- classes now: {dict(cls_ct) or '{}'} | repriceable now: true {rp_t} / false {rp_f} "
          f"| **cumulative bid_grade lines: {cum[0] + cum[1]} (repriceable true {cum[0]} / false {cum[1]})** "
          f"-- the liquid_repost re-arm evidence accumulates here"]
    if bid_grades:
        L += ["| ticker | lvl | age | prints n/rng/sz | book | gap | class | bound(min aim,goal−basis) | note |",
              "|---|---|---|---|---|---|---|---|---|"]
        for g in sorted(bid_grades, key=lambda x: x["ticker"]):
            pr = (f"{g['prints']}/{g['print_min']}-{g['print_max']}/{g['print_sz']}"
                  if g["prints"] else "0")
            bb = f"{g['bbo']['bid']}-{g['bbo']['ask']}" if g.get("bbo") else "?"
            note = ("REPRICEABLE→%s" % g["reprice_to"]) if g["repriceable"] else (g["doctrine_note"] or "")
            L.append(f"| {g['ticker'].replace('KX','')[:34]} | {g['level']} | {g['age_min']}m "
                     f"| {pr} | {bb} | {g['gap'] if g['gap'] is not None else '—'} "
                     f"| **{g['cls']}** | {g['reprice_bound']} | {note[:60]} |")
    else:
        L.append("no resting entry bids")
    L += ["", f"## COULD-HAVE-FILLED — open pairs, achievable-combined RIGHT NOW"]
    if chf:
        L += ["| event | basis | sib ask | achievable | goal | vs goal |",
              "|---|---|---|---|---|---|"]
        for r in sorted(chf, key=lambda x: x["vs_goal"]):
            L.append(f"| {r['event'].replace('KX','')[:34]} | {r['basis']} | {r['sib_ask']} "
                     f"| **{r['achievable']}** | {r['goal']} | {r['vs_goal']:+d} |")
    else:
        L.append("no open half-pairs")
    flow_rows = flow_rows or []
    _fs_ct = defaultdict(int)
    for fr in flow_rows:
        _fs_ct[fr["state"]] += 1
    L += ["", f"## FLOW-STATE — {len(flow_rows)} tracked game(s) "
              f"({dict(_fs_ct) or '{}'}; thresholds PROVISIONAL, refit by the early-canvas study; "
              f"window {FLOW_WINDOW_MIN}m)"]
    if flow_rows:
        L += ["| game | cat | prints/min | spread | state |", "|---|---|---|---|---|"]
        for fr in sorted(flow_rows, key=lambda x: (x["state"], x["event"])):
            L.append(f"| {fr['event'].replace('KX','')[:34]} | {fr['cat']} | {fr['rate']} "
                     f"| {fr['spread'] if fr['spread'] is not None else '—'} | **{fr['state']}** |")
    else:
        L.append("no tracked games")
    L += ["", f"## PATTERNS (sub-B) — {len(pats)}"]
    for p in sorted(pats, key=lambda y: y["ts"]):
        L.append(f"- {p['pattern']}: {p.get('ticker') or p.get('event')} "
                 f"{json.dumps({k: p[k] for k in p if k not in ('key','type','pattern','ts','ticker','event')})}")
    dv = drain_replay_violations(log_path)
    L += ["", f"## DRAIN-REPLAY (zero-tolerance) — "
              f"{('**' + str(len(dv)) + ' VIOLATION' + ('S' if len(dv) != 1 else '') + '**') if dv else '0 violations'}"]
    if dv:
        for x in dv:
            L.append(f"- **VIOLATION**: `{x['ticker']}` drained {x['drained_at']} — "
                     f"neither filled, re-placed, nor refusal-named within 10 min post-boot")
    else:
        L.append("every drained entry bid accounted for (replayed / refused-named / none drained)")
    L += ["", f"## ERRORS — {len(S['errors'])} handler errors this session "
              f"{'(ZERO — clean loop)' if not S['errors'] else '(SEE ZERO-TOLERANCE)'}", ""]
    txt = "\n".join(L)
    old = STATUS.read_text(encoding="utf-8", errors="replace") if STATUS.exists() else ""
    # ignore the cycle-stamp line when deciding "changed"
    strip = lambda t: "\n".join(l for l in t.splitlines() if not l.startswith("- cycle"))
    changed = strip(old) != strip(txt)
    STATUS.write_text(txt, encoding="utf-8")
    return changed


def git_push(msg):
    def run(*a):
        return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True)
    run("fetch", "origin")
    r = run("merge", "--ff-only", "origin/blend/kalshi-occ-fallback")
    run("add", str(OUT))
    c = run("-c", "user.name=live-monitor", "-c", "user.email=omigroup.ops@outlook.com",
            "commit", "-m", msg)
    if "nothing to commit" in (c.stdout + c.stderr):
        return "nothing-to-commit"
    p = run("push", "origin", "blend/kalshi-occ-fallback")
    return "pushed" if p.returncode == 0 else f"PUSH-FAIL: {p.stderr.strip()[:200]}"


def cycle(n):
    OUT.mkdir(parents=True, exist_ok=True)
    aim = load_aim()
    try:
        goal = int(json.loads((ARB / "config/deploy_v5_live.json").read_text()).get("combined_goal", 97))
    except Exception:
        goal = 97
    log_path = newest_log()
    if not log_path:
        print(f"[{now_et()}] no log found", flush=True)
        return
    S = parse_session(log_path)
    bid_grades = grade_resting_bids(S, aim, goal)
    chf = could_have_filled(S, goal)
    items = analyze(S, aim, goal, bid_grades)
    items += S.get("_extra_pats", [])   # [C-REALITY-BELL] reality_divergence + bell_missing
    # [C-FLOW-STATE 07-08] per-game gauge rows into the status page; state
    # transitions into the jsonl through the same append-once dedup below.
    flow_rows, flow_lines = flow_state_gauge(S)
    items += flow_lines
    # dedup against the committed jsonl (the jsonl IS the state) + cumulative
    # repriceable counters (the liquid_repost re-arm evidence base)
    seen = set()
    cum_rp = [0, 0]   # [true, false]
    if JSONL.exists():
        for line in JSONL.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                o = json.loads(line)
                seen.add(o["key"])
                if o.get("type") == "bid_grade":
                    cum_rp[0 if o.get("repriceable") else 1] += 1
            except Exception:
                pass
    new = [it for it in items if it["key"] not in seen]
    if new:
        with open(JSONL, "a", encoding="utf-8") as fh:
            for it in sorted(new, key=lambda x: x.get("ts", 0)):
                it["emitted_et"] = now_et()
                fh.write(json.dumps(it) + "\n")
    for it in items:
        if it.get("type") == "bid_grade" and it["key"] not in seen:
            cum_rp[0 if it.get("repriceable") else 1] += 1
    forensics = forensic_check(items, S, log_path)
    changed = write_status(S, items, log_path, n, forensics, bid_grades, chf,
                           chf_cum=tuple(cum_rp), flow_rows=flow_rows)
    # [C-FUND-TRACKER Part 4a — THE SIGNAL LAW, 07-15] every alarm
    # self-grades at emission: DEFECT / GUARD-WORKING / CHATTER — only
    # DEFECT presents as a problem (the [N VIOLATION] tag). The nightly
    # census re-grades mislabels; ungraded classes default DEFECT (loud
    # beats silent).
    SIGNAL_GRADE = {
        "w2_fill": "DEFECT", "grace_breach": "DEFECT",
        "handler_error": "DEFECT", "walk_cap_breach": "DEFECT",
        "combined_over_goal": "DEFECT",
        "chase_cap": "GUARD-WORKING", "flatten_leash": "GUARD-WORKING",
        "taker_capped": "GUARD-WORKING", "self_fill_bell": "GUARD-WORKING",
        "bell_missing": "CHATTER"}   # coverage counter; the scorecard
                                     # owns the real BELLS-MISSING number
    for x in new:
        if x.get("type") == "violation" and "grade" not in x:
            x["grade"] = SIGNAL_GRADE.get(x.get("cls"), "DEFECT")
    nv = sum(1 for x in new if x.get("type") == "violation"
             and x.get("grade", "DEFECT") == "DEFECT")
    n_guard = sum(1 for x in new if x.get("type") == "violation"
                  and x.get("grade") == "GUARD-WORKING")
    n_chat = sum(1 for x in new if x.get("type") == "violation"
                 and x.get("grade") == "CHATTER")
    # [07-09 RE-ENTRY WATCH] open-cycle-2 counter until the re-entry ruling
    # ships its fix: legs whose CURRENT open entry has a prior completed
    # buy->cash cycle in the same log lineage (DAALU class). Count-only.
    oc2 = 0
    try:
        _seq = {}
        for _ln in open(log_path, errors="replace"):
            if '"entry_filled"' not in _ln and '"exit_filled"' not in _ln:
                continue
            try:
                _d = json.loads(_ln)
            except ValueError:
                continue
            _det = _d.get("details") or {}
            if _d["event"] == "entry_filled" and "adopt" in _det.get("source", ""):
                continue
            _seq.setdefault(_d.get("ticker", ""), []).append(
                (_d.get("ts_epoch", 0), "B" if _d["event"] == "entry_filled" else "S"))
        for _tk, _evs in _seq.items():
            _evs.sort()
            _cyc, _st, _openB = 0, None, False
            for _ts, _k in _evs:
                if _k == "B":
                    _st = _ts; _openB = True
                elif _k == "S" and _st is not None:
                    _cyc += 1; _st = None; _openB = False
            if _openB and _cyc >= 1:
                oc2 += 1
    except Exception:
        oc2 = -1
    res = "no-change"
    if new or changed or forensics:
        res = git_push(f"live-monitor cycle {n}: +{len(new)} lines"
                       f"{' [' + str(nv) + ' DEFECT]' if nv else ''}"
                       f"{' [' + str(n_guard) + ' guard]' if n_guard else ''}"
                       f"{' [' + str(n_chat) + ' chatter]' if n_chat else ''}"
                       f"{' [FORENSIC ' + ','.join(forensics) + ']' if forensics else ''}"
                       f"{' [OPEN-CYCLE2 ' + str(oc2) + ']' if oc2 > 0 else ''}")
    print(f"[{now_et()}] cycle {n}: events={S['events']} fills={len(S['fills'])} "
          f"new_lines={len(new)} violations_new={nv} open_cycle2={oc2} "
          f"forensics={forensics or '—'} git={res}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--interval", type=int, default=600)
    args = ap.parse_args()
    n = 0
    crashes = 0   # [07-11 MONITOR-BLIND class] nobody watches the watcher:
    # 7h of every-cycle crashes rendered nothing and nothing said so.
    # >=3 consecutive crashed cycles -> the BOT_DOWN ntfy channel.
    while True:
        n += 1
        try:
            cycle(n)
            crashes = 0
        except Exception as e:
            import traceback
            print(f"[{now_et()}] CYCLE {n} CRASHED (loop continues): {e}\n{traceback.format_exc()}",
                  flush=True)
            crashes += 1
            if crashes == 3:
                try:
                    subprocess.run(["/root/notify.sh",
                                    "live_monitor: 3 consecutive cycles CRASHED -- "
                                    "LIVE_STATUS is stale; last error: %s" % e],
                                   timeout=30)
                except Exception:
                    pass
        if args.once:
            break
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
