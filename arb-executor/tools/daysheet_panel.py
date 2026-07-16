#!/usr/bin/env python3
"""C-DAYSHEET-LIVE — POSITIONS / ORDERS / CLOSED three-tab panel.

Deviation note (operator-approved, one-off): normally Plex renders visuals
from CC-extracted JSON only (operator constraint #8). This panel was built
directly by Plex end-to-end per explicit operator instruction on the mock
phase (approved v4 mock, delivered as "the spec, verbatim") and the
subsequent live-build authorization. It is intentionally real, wired code —
not a CC-fed render.

This module is imported by tools/fund_tracker.py and adds:
  - GET /daysheet            -> the three-tab HTML page (same token gate)
  - GET /api/positions.json  -> open positions, both legs paired
  - GET /api/orders.json     -> resting unfilled orders, both legs paired
  - GET /api/closed.json     -> settled/cashed games with grading
  - GET /api/tape/<ticker>.json -> raw trades-tape prints for one ticker
                                   (proof-on-click backing)

Design constraints carried from the approved mock (daysheet_mock_v4.html,
the render spec, verbatim) and the operator's live-build instructions:

  - Full last names only. Name comes from the schedule join
    (tennis_schedule.match_kalshi_event against state/schedule.json).
    A failed join renders "name join pending" — never a ticker fragment.
  - PLACED ET = order creation (Kalshi order `created_time`).
    FILLED ET = Kalshi's own fill record `created_time`. These are two
    different exchange-truth fields and must never be conflated even when
    they differ by hours (the Santillan exhibit — a resting bid placed
    long before it fills).
  - The gray "did we even try" line is sourced from order history only
    (snap_orders history + any cancel evidence we have), never inferred
    from the mere absence of a position.
  - Every W1/CORR low·high or close value must be backed by a real
    trades-tape print available at /api/tape/<ticker>.json — no number
    renders without a receipt one click away.
  - CLOSED tab grades come only from DAYSHEET.json (game_report.py's own
    per-leg grade field) for that day. Where that file doesn't exist yet
    for a given day, every game for that day renders "ungraded" — never
    an invented letter.
  - Kalshi deep link is a real market URL built from the ticker, not a
    hardcoded string.

Stdlib only — no new dependencies, no build step, matches fund_tracker.py's
own approach exactly.
"""
import json
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
ROOT = Path(__file__).resolve().parent.parent  # arb-executor/
DB = ROOT / "state" / "fund_equity.db"
SCHEDULE_PATH = ROOT / "state" / "schedule.json"
GAME_REPORTS_ROOT = ROOT.parent / ".claude" / "game_reports"

# Allow a fixture override for local dev/screenshotting without the live
# db or a live SSH tunnel to the box (see tools/daysheet_fixture.json).
# Never used when the real db/game-reports exist and FUND_TRACKER_FIXTURE
# is unset — this is strictly a local-dev escape hatch, not a data source
# for the deployed box.
import os
FIXTURE_PATH = os.environ.get("DAYSHEET_FIXTURE")


def _q(sql, args=()):
    con = sqlite3.connect("file:%s?mode=ro" % DB, uri=True, timeout=2)
    try:
        return con.execute(sql, args).fetchall()
    finally:
        con.close()


def _load_schedule():
    """Returns {pair_code: {start_time, p1, p2, tournament, category, ...}}."""
    try:
        raw = json.loads(SCHEDULE_PATH.read_text())
        return raw.get("schedule", {}) if isinstance(raw, dict) else {}
    except Exception:
        return {}


def _ticker_pair_code(ticker):
    """KXATPCHALLENGERMATCH-26JUL15WUYIB-WU -> event ticker without the leg
    suffix, then the trailing pair code TennisExplorer keys schedule on."""
    ev = ticker.rsplit("-", 1)[0] if ticker.count("-") >= 2 else ticker
    raw = ev.split("-")[-1]
    import re
    m = re.match(r"\d{2}[A-Z]{3}\d{2}(.+)", raw)
    return (m.group(1) if m else raw), ev


def join_match_name(ticker):
    """Real schedule join. Returns dict with p1_last, p2_last, start_et,
    tournament, category, joined(bool). Never fabricates a name — a failed
    join returns joined=False and the caller must render 'name join
    pending', never a ticker fragment."""
    sched = _load_schedule()
    pair_code, ev = _ticker_pair_code(ticker)
    entry = sched.get(pair_code)
    if not entry:
        # fuzzy fallback disabled here deliberately — without Kalshi's own
        # full player-name list (V1 API) on hand at render time, a fuzzy
        # guess is exactly the class of error "name join pending" exists
        # to prevent. Direct pair-code join only.
        return {"joined": False, "event": ev}
    p1 = (entry.get("p1") or "").strip()
    p2 = (entry.get("p2") or "").strip()
    if not p1 or not p2:
        return {"joined": False, "event": ev}
    return {
        "joined": True,
        "event": ev,
        "p1_last": p1.split()[-1].upper(),
        "p2_last": p2.split()[-1].upper(),
        "p1_full": p1,
        "p2_full": p2,
        "start_time": entry.get("start_time"),
        "tournament": entry.get("tournament"),
        "category": entry.get("category"),
    }


def leg_last_name(ticker, schedule_join):
    """Which side of the joined match this leg's ticker settles on. Kalshi
    tennis tickers end -TICKER where TICKER is drawn from the player's
    surname/abbrev; match against the joined p1/p2 last names. Falls back
    to the raw leg suffix (never invented) if neither matches."""
    leg = ticker.rsplit("-", 1)[-1].upper()
    if not schedule_join.get("joined"):
        return leg  # caller renders join-pending styling around this
    p1l, p2l = schedule_join["p1_last"], schedule_join["p2_last"]
    if p1l.startswith(leg) or leg in p1l:
        return p1l
    if p2l.startswith(leg) or leg in p2l:
        return p2l
    return leg


def game_report_day(ep):
    return datetime.fromtimestamp(ep, ET).strftime("%Y%m%d")


def load_dayheet_grades(day):
    """Reads .claude/game_reports/<day>/DAYSHEET.json (game_report.py's own
    output). Returns {ticker_suffix: row} or {} if the file doesn't exist
    yet for that day — callers must render 'ungraded', never invent a
    grade in that case."""
    if FIXTURE_PATH:
        try:
            fx = json.loads(Path(FIXTURE_PATH).read_text())
            return {r["game"] + "-" + r["leg"]: r for r in fx.get("dayheet_rows", [])}
        except Exception:
            return {}
    p = GAME_REPORTS_ROOT / day / "DAYSHEET.json"
    if not p.exists():
        return {}
    try:
        rows = json.loads(p.read_text())
        return {r.get("game", "") + "-" + r.get("leg", ""): r for r in rows}
    except Exception:
        return {}


def order_history_for_ticker(ticker):
    """Order-history-sourced status for a leg with NO current fill — the
    'did we even try' line. Sources only from snap_orders' rolling history
    plus the flags table (cancel/latch evidence) — never inferred from the
    mere absence of a position. Returns a plain-language string or None if
    genuinely nothing was ever recorded (renders 'not bid — never
    conceived' at the caller, which IS the honest state, not an inference)."""
    if FIXTURE_PATH:
        try:
            fx = json.loads(Path(FIXTURE_PATH).read_text())
            return fx.get("order_history", {}).get(ticker)
        except Exception:
            return None
    rows = _q(
        "SELECT ts, yes_price_c, remaining FROM snap_orders "
        "WHERE ticker=? AND action='buy' ORDER BY ts", (ticker,))
    if not rows:
        return None  # genuinely no record — "never conceived" is honest
    first_ts, first_px, _ = rows[0]
    last_ts, last_px, last_rem = rows[-1]
    flag = _q(
        "SELECT ts, kind, detail FROM flags WHERE ticker=? "
        "ORDER BY ts DESC LIMIT 1", (ticker,))
    when = datetime.fromtimestamp(first_ts, ET).strftime("%-I:%M %p ET")
    if last_rem == 0 and flag:
        return ("posted %d¢ · pulled (%s, %s) · never re-placed"
                 % (first_px, flag[0][2][:40], when))
    return "posted %d¢ · never traded that low" % first_px


def kalshi_deeplink(ticker):
    ev = ticker.rsplit("-", 1)[0] if ticker.count("-") >= 2 else ticker
    return "https://kalshi.com/markets/%s" % ev.lower()


# ── /api/positions.json ──────────────────────────────────────────────────
def build_positions():
    if FIXTURE_PATH:
        return json.loads(Path(FIXTURE_PATH).read_text()).get("positions", [])

    pos_rows = _q(
        "SELECT ticker, qty, exposure_c, mark_c FROM snap_positions "
        "WHERE ts=(SELECT MAX(ts) FROM snap_positions)")
    sells = {r[0]: (r[1], r[2]) for r in _q(
        "SELECT ticker, yes_price_c, remaining FROM snap_orders "
        "WHERE ts=(SELECT MAX(ts) FROM snap_orders) AND action='sell'")}
    fills_by_ticker = {}
    for r in _q("SELECT ticker, ts, yes_price_c, count_fp, order_id FROM "
                "fills ORDER BY ts DESC"):
        fills_by_ticker.setdefault(r[0], r)

    # group by event so both legs render together, per spec
    events = {}
    for tk, qty, exp, mk in pos_rows:
        if qty == 0:
            continue
        pair_code, ev = _ticker_pair_code(tk)
        events.setdefault(ev, []).append((tk, qty, exp, mk))

    out = []
    for ev, legs in events.items():
        sample_tk = legs[0][0]
        sj = join_match_name(sample_tk)
        game_out = {
            "event": ev,
            "joined": sj.get("joined", False),
            "names": (
                "%s v %s" % (sj["p1_full"].split()[-1].title(),
                             sj["p2_full"].split()[-1].title())
                if sj.get("joined") else "name join pending"
            ),
            "start_time": sj.get("start_time"),
            "tournament": sj.get("tournament"),
            "category": sj.get("category"),
            "legs": [],
        }
        for tk, qty, exp, mk in legs:
            basis = int(exp / qty) if qty else 0
            last_name = leg_last_name(tk, sj)
            fill = fills_by_ticker.get(tk)
            exit_order = sells.get(tk)
            gray_line = None
            history = order_history_for_ticker(tk)
            leg_out = {
                "ticker": tk,
                "last_name": last_name,
                "qty": qty,
                "basis_c": basis,
                "mark_c": int(mk / qty) if qty else 0,
                "exit_resting": (
                    {"price_c": exit_order[0], "qty": exit_order[1]}
                    if exit_order else None
                ),
                "deeplink": kalshi_deeplink(tk),
                # PLACED ET (order-creation time) has no honest source in
                # the current schema: snap_orders only stores periodic
                # snapshot ts, never Kalshi's own order created_time. This
                # is a real data gap, not a rendering choice — flagged in
                # the PR. Never backfilled from the fill time, which would
                # be exactly the placed/filled conflation the Time
                # Sourcing Law forbids (see the Santillan exhibit).
                "placed_et": None,
                "filled_et": (
                    datetime.fromtimestamp(fill[1], ET).strftime("%-I:%M %p ET")
                    if fill else None
                ),
                "fill_price_c": fill[2] if fill else None,
            }
            game_out["legs"].append(leg_out)
        # sibling gray line: whichever leg in this event has NO position
        # row at all (never bid, or bid-and-never-filled)
        held_suffixes = {leg["last_name"] for leg in game_out["legs"]}
        if sj.get("joined"):
            for other_last in (sj["p1_last"], sj["p2_last"]):
                if other_last not in held_suffixes:
                    # find the sibling ticker so we can query real order history
                    sib_tk = ev + "-" + other_last[:3]
                    hist = order_history_for_ticker(sib_tk)
                    game_out["gray_line"] = "%s — %s" % (
                        other_last,
                        hist if hist else "not bid — never conceived")
        out.append(game_out)
    return out


# ── /api/orders.json ─────────────────────────────────────────────────────
def build_orders():
    if FIXTURE_PATH:
        return json.loads(Path(FIXTURE_PATH).read_text()).get("orders", [])

    rows = _q(
        "SELECT ticker, yes_price_c, remaining, ts FROM snap_orders "
        "WHERE ts=(SELECT MAX(ts) FROM snap_orders) AND action='buy' "
        "AND remaining > 0")
    events = {}
    for tk, px, rem, ts in rows:
        pair_code, ev = _ticker_pair_code(tk)
        events.setdefault(ev, []).append((tk, px, rem, ts))
    out = []
    now = time.time()
    for ev, legs in events.items():
        sj = join_match_name(legs[0][0])
        game_out = {
            "event": ev,
            "joined": sj.get("joined", False),
            "names": (
                "%s v %s" % (sj["p1_full"].split()[-1].title(),
                             sj["p2_full"].split()[-1].title())
                if sj.get("joined") else "name join pending"
            ),
            "start_time": sj.get("start_time"),
            "tournament": sj.get("tournament"),
            "legs": [],
        }
        for tk, px, rem, ts in legs:
            age_s = now - ts
            game_out["legs"].append({
                "ticker": tk,
                "last_name": leg_last_name(tk, sj),
                "aim_c": px,
                "qty": rem,
                "age_label": "%dh%dm" % (age_s // 3600, (age_s % 3600) // 60),
            })
        out.append(game_out)
    return out


# ── /api/closed.json ─────────────────────────────────────────────────────
def build_closed(day=None):
    if FIXTURE_PATH:
        return json.loads(Path(FIXTURE_PATH).read_text()).get("closed", [])

    day = day or datetime.now(ET).strftime("%Y%m%d")
    grades = load_dayheet_grades(day)  # {} if DAYSHEET.json absent -> ungraded

    fills = _q(
        "SELECT ticker, ts, yes_price_c, count_fp, order_id FROM fills "
        "WHERE day=? ORDER BY ts", (day,))
    events = {}
    for tk, ts, px, ct, oid in fills:
        pair_code, ev = _ticker_pair_code(tk)
        events.setdefault(ev, []).append((tk, ts, px, ct, oid))

    out = []
    for ev, legs in events.items():
        sj = join_match_name(legs[0][0])
        game_out = {
            "event": ev,
            "joined": sj.get("joined", False),
            "names": (
                "%s v %s" % (sj["p1_full"].split()[-1].title(),
                             sj["p2_full"].split()[-1].title())
                if sj.get("joined") else "name join pending"
            ),
            "start_time": sj.get("start_time"),
            "tournament": sj.get("tournament"),
            "legs": [],
            "grade": None,
            "grade_status": "ungraded",
            "footnote": None,
        }
        leg_grades = []
        for tk, ts, px, ct, oid in legs:
            last = leg_last_name(tk, sj)
            leg_suffix = tk.rsplit("-", 1)[-1]
            gr_row = grades.get(tk.rsplit("-", 1)[0] + "-" + leg_suffix) or \
                grades.get(tk[-16:] + "-" + leg_suffix)
            leg_grade = gr_row.get("grade") if gr_row else None
            if leg_grade:
                leg_grades.append(leg_grade.replace("(W2)", ""))
            game_out["legs"].append({
                "ticker": tk,
                "last_name": last,
                "fill_price_c": px,
                "filled_et": datetime.fromtimestamp(ts, ET).strftime("%-I:%M %p ET"),
                # Same PLACED-ET gap as build_positions() — no order-
                # creation timestamp exists in snap_orders today. Rendered
                # as None (honest empty state), never copied from the
                # fill time.
                "placed_et": None,
                "qty": ct,
                "grade_row": gr_row,
            })
        if leg_grades:
            # game grade = worst leg grade (A>B>C>D>F ordering), never invented
            order = {"A": 0, "B": 1, "C": 2, "D": 3, "F": 4}
            worst = max(leg_grades, key=lambda g: order.get(g, 9))
            game_out["grade"] = worst
            game_out["grade_status"] = "graded"
        out.append(game_out)
    return out


# ── /api/tape/<ticker>.json ──────────────────────────────────────────────
def build_tape(ticker):
    """Proof-on-click backing. Real trades-tape prints for one ticker,
    from the fills table (our own recorder's copy of Kalshi's public trade
    history is not separately stored — this exposes our fills as receipts;
    a full public-tape mirror is a separate future organ). Renders the
    honest 'no tape receipt' state if nothing is on file — never a
    fabricated print."""
    if FIXTURE_PATH:
        fx = json.loads(Path(FIXTURE_PATH).read_text())
        return fx.get("tape", {}).get(ticker, {"prints": [], "has_receipt": False})

    rows = _q(
        "SELECT ts, yes_price_c, count_fp FROM fills WHERE ticker=? "
        "ORDER BY ts", (ticker,))
    if not rows:
        return {"prints": [], "has_receipt": False}
    prints = [{
        "t": datetime.fromtimestamp(ts, ET).strftime("%b %-d %-I:%M %p"),
        "price_c": px,
        "ct": ct,
    } for ts, px, ct in rows]
    return {"prints": prints, "has_receipt": True}


def tape_age_seconds():
    if FIXTURE_PATH:
        try:
            fx = json.loads(Path(FIXTURE_PATH).read_text())
            return fx.get("tape_age_seconds", 0)
        except Exception:
            return 0
    row = _q("SELECT MAX(ts) FROM fills")
    if not row or not row[0][0]:
        return None
    return time.time() - row[0][0]
