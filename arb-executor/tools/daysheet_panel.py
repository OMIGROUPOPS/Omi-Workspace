#!/usr/bin/env python3
"""C-DAYSHEET-LIVE + C-PANEL-TRUTH — POSITIONS / ORDERS / CLOSED panel.

This module is imported by tools/fund_tracker.py and adds:
  - GET /daysheet            -> the three-tab HTML page (same token gate)
  - GET /api/positions.json  -> open positions, both legs paired
  - GET /api/orders.json     -> resting unfilled orders, both legs paired
  - GET /api/closed.json     -> settled/cashed games, ONE ROW PER LEG
  - GET /api/tape/<ticker>.json -> real Kalshi public trades tape for one
                                   ticker (proof-on-click backing)

RENDER LAWS enforced here (C-PANEL-TRUTH v1, 07-16):
  1. NAME LAW — full surnames from the schedule join everywhere. The
     TennisExplorer schedule stores "Surname I." — the trailing initial
     token is NEVER the surname (the "H. v E." bug this dispatch kills).
     A failed join renders "name join pending"; ticker fragments and
     initials are banned output. Every remaining miss is FILED to
     state/daysheet_misses.jsonl.
  2. ONE ROW PER LEG — the closed builder aggregates fills: OURS = the
     count-weighted average of BUY fills (DCA collapses to one row);
     SELL fills render as the leg's exit in its own place, never as a
     sibling row.
  3. BELL JOIN — bells come from the engine's own gun_fired log lines,
     keyed by the game's OWN event, scanned incrementally across the
     day-files that actually contain the event (a game's overnight action
     lives in the prior day's file). Rendered with source + EST/LIVE
     badge. With the bell, W1/CORR LO·HI populate from the public trades
     tape; a ticker with no tape coverage renders "no tape" (never a
     dash) and is FILED.
  4. GRADES INTRADAY — grades join DAYSHEET.json from the queried day AND
     the prior log-day (log files roll mid-day; a game settled this
     morning grades in yesterday's file). Walk files
     (.claude/walks/<d>/WALK_<pair>.md) wire into the game's footnote
     slot in the standing format: charge -> amendment -> verdict.
  5. DEEP LINKS — a real Kalshi market URL per game.

PLACED ET still has no honest source (snap_orders lacks order
created_time) — the column renders None; the gap is on the open ledger.

Stdlib only — urllib for the public tape (no auth needed on
/markets/trades), no new dependencies, no build step.
"""
import json
import re
import sqlite3
import threading
import time
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
ROOT = Path(__file__).resolve().parent.parent  # arb-executor/
DB = ROOT / "state" / "fund_equity.db"
SCHEDULE_PATH = ROOT / "state" / "schedule.json"
GAME_REPORTS_ROOT = ROOT.parent / ".claude" / "game_reports"
WALKS_ROOT = ROOT.parent / ".claude" / "walks"
LOG_DIR = ROOT / "logs"
BELLS_CACHE = ROOT / "state" / "daysheet_bells.json"
TAPE_DIR = ROOT / "state" / "daysheet_tape"
MISS_FILE = ROOT / "state" / "daysheet_misses.jsonl"

# Fixture override for local dev/screenshotting without the live db —
# strictly a local-dev escape hatch, never a data source on the box.
import os
FIXTURE_PATH = os.environ.get("DAYSHEET_FIXTURE")

# gun sources that are live evidence vs fitted/fallback estimates
LIVE_BELL_SOURCES = {"te_scoreboard", "tape_latch", "tape_flow",
                     "schedule_live", "self_fill"}


def _q(sql, args=()):
    con = sqlite3.connect("file:%s?mode=ro" % DB, uri=True, timeout=2)
    try:
        return con.execute(sql, args).fetchall()
    finally:
        con.close()


def _iso_ep(s):
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except Exception:
        return None


def _hm(ep):
    return datetime.fromtimestamp(ep, ET).strftime("%-I:%M:%S %p ET")


# ── miss filing (render-law: misses are FILED, never silently styled) ────
_missed = set()
_miss_lock = threading.Lock()


def _file_miss(kind, key):
    k = "%s:%s" % (kind, key)
    with _miss_lock:
        if k in _missed:
            return
        _missed.add(k)
        try:
            MISS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(MISS_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps({"ts": time.time(), "kind": kind,
                                    "key": key}) + "\n")
        except OSError:
            pass


# ── NAME LAW ─────────────────────────────────────────────────────────────
_INITIALS = re.compile(r"^(?:[A-Z]\.)+$")


def surname_of(full):
    """TennisExplorer format is 'Surname I.' (possibly multi-word surname,
    possibly stacked initials 'Y.D.'). The trailing initial tokens are
    NEVER the surname — strip them; what remains is the full surname."""
    toks = [t for t in (full or "").strip().split() if t]
    while toks and _INITIALS.match(toks[-1]):
        toks.pop()
    return " ".join(toks)


def _load_schedule():
    try:
        raw = json.loads(SCHEDULE_PATH.read_text())
        return raw.get("schedule", {}) if isinstance(raw, dict) else {}
    except Exception:
        return {}


def _ticker_pair_code(ticker):
    """KXATPCHALLENGERMATCH-26JUL15WUYIB-WU -> ('WUYIB', event ticker)."""
    ev = ticker.rsplit("-", 1)[0] if ticker.count("-") >= 2 else ticker
    raw = ev.split("-")[-1]
    m = re.match(r"\d{2}[A-Z]{3}\d{2}(.+)", raw)
    return (m.group(1) if m else raw), ev


NAMES_DIR = ROOT / "state" / "daysheet_names"


def _kalshi_event_names(ev):
    """Exchange-truth name fallback: Kalshi's own event object carries
    the surnames in the title ('Wu vs Bu') and each leg's full player
    name in yes_sub_title — keyed by the ticker itself, never a fuzzy
    guess. Disk-cached forever (an event's players never change).
    Needed because Kalshi keys pair codes on GIVEN names (YIBYUN =
    Yibing/Yunchaokete) where TennisExplorer keys surnames (WUYUN)."""
    NAMES_DIR.mkdir(parents=True, exist_ok=True)
    p = NAMES_DIR / ("%s.json" % ev)
    try:
        return json.loads(p.read_text())
    except Exception:
        pass
    try:
        url = ("https://api.elections.kalshi.com/trade-api/v2/events/"
               "%s?with_nested_markets=true" % ev)
        req = urllib.request.Request(url, headers={"User-Agent":
                                                   "omi-daysheet-panel"})
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.load(r)
    except Exception:
        return None  # never cache a failure
    e = d.get("event") or {}
    legs = {}
    for m in e.get("markets") or []:
        suffix = (m.get("ticker") or "").rsplit("-", 1)[-1]
        nm = (m.get("yes_sub_title") or "").strip()
        if suffix and nm:
            legs[suffix] = nm
    title = (e.get("title") or "").strip()
    if not legs or " vs " not in title:
        return None
    out = {"title": title, "legs": legs}
    try:
        p.write_text(json.dumps(out), encoding="utf-8")
    except OSError:
        pass
    return out


def join_match_name(ticker):
    """Real schedule join, Kalshi event-object fallback. A failed join
    returns joined=False and the caller renders 'name join pending' —
    never a ticker fragment. Every remaining miss is filed."""
    sched = _load_schedule()
    pair_code, ev = _ticker_pair_code(ticker)
    entry = sched.get(pair_code)
    s1 = s2 = None
    if entry:
        s1 = surname_of(entry.get("p1"))
        s2 = surname_of(entry.get("p2"))
    if not s1 or not s2:
        kn = _kalshi_event_names(ev)
        if kn:
            t1, _, t2 = kn["title"].partition(" vs ")
            t1, t2 = t1.strip(), t2.strip()
            if t1 and t2:
                return {
                    "joined": True,
                    "source": "kalshi_event",
                    "event": ev,
                    "p1_last": t1.upper(),
                    "p2_last": t2.upper(),
                    "p1_disp": t1,
                    "p2_disp": t2,
                    "kalshi_legs": kn["legs"],
                    "start_time": None,
                    "start_ep": None,
                    "tournament": (entry or {}).get("tournament"),
                    "category": (entry or {}).get("category"),
                }
        _file_miss("name_join", ev)
        return {"joined": False, "event": ev}
    return {
        "joined": True,
        "event": ev,
        "p1_last": s1.upper(),
        "p2_last": s2.upper(),
        "p1_disp": s1,
        "p2_disp": s2,
        "start_time": entry.get("start_time"),
        "start_ep": _iso_ep(entry.get("start_time") or ""),
        "tournament": entry.get("tournament"),
        "category": entry.get("category"),
    }


def leg_last_name(ticker, sj):
    """Which side of the joined match this leg settles on. Returns the
    FULL SURNAME or None — never a ticker fragment (banned output; the
    caller renders 'join pending' and the miss is filed). Some schedule
    sources store 'First Last' with no trailing initial — when the whole
    name matched, prefer the token(s) the ticker suffix actually keys on
    (SAMSON, not LAURA SAMSON); fall back to the full matched name."""
    leg = ticker.rsplit("-", 1)[-1].upper()
    if not sj.get("joined"):
        return None
    kl = sj.get("kalshi_legs") or {}
    if leg in kl:
        nm = kl[leg].upper()
        for last in (sj["p1_last"], sj["p2_last"]):
            if nm.endswith(last):
                return last
        return kl[leg]  # full player name — never a fragment
    for last in (sj["p1_last"], sj["p2_last"]):
        flat = last.replace(" ", "").replace("-", "")
        if flat.startswith(leg) or leg in flat:
            toks = last.split()
            if len(toks) > 1:
                for i in range(len(toks)):
                    tail = " ".join(toks[i:])
                    tflat = tail.replace(" ", "").replace("-", "")
                    if tflat.startswith(leg):
                        return tail
            return last
    _file_miss("leg_name", ticker)
    return None


def kalshi_deeplink(ticker_or_event):
    ev = (ticker_or_event.rsplit("-", 1)[0]
          if ticker_or_event.count("-") >= 2 else ticker_or_event)
    return "https://kalshi.com/markets/%s" % ev.lower()


# ── BELL JOIN (engine gun_fired lines, incremental, disk-persisted) ─────
_bells_lock = threading.Lock()
_bells_mem = {"files": {}, "bells": {}, "loaded": False, "checked": 0.0}


def _bells():
    """{event_ticker: {gun_ts, bell_ts, source}} from live_v3_<day>.jsonl
    gun_fired lines — today's and yesterday's files (log files roll
    mid-day; an event's bell can live in either). Incremental by byte
    offset, persisted to state/daysheet_bells.json."""
    with _bells_lock:
        now = time.time()
        if not _bells_mem["loaded"]:
            try:
                disk = json.loads(BELLS_CACHE.read_text())
                _bells_mem["files"] = disk.get("files", {})
                _bells_mem["bells"] = disk.get("bells", {})
            except Exception:
                pass
            _bells_mem["loaded"] = True
        if now - _bells_mem["checked"] < 30:
            return _bells_mem["bells"]
        _bells_mem["checked"] = now
        days = [(datetime.now(ET) - timedelta(days=n)).strftime("%Y%m%d")
                for n in (1, 0)]
        changed = False
        for d in days:
            p = LOG_DIR / ("live_v3_%s.jsonl" % d)
            if not p.exists():
                continue
            key = str(p)
            off = int(_bells_mem["files"].get(key, 0))
            try:
                size = p.stat().st_size
                if size <= off:
                    continue
                with open(p, "rb") as fh:
                    fh.seek(off)
                    data = fh.read()
                tail = 0
                if data and not data.endswith(b"\n"):
                    cut = data.rfind(b"\n") + 1
                    tail = len(data) - cut
                    data = data[:cut]
                for line in data.split(b"\n"):
                    if b'"gun_fired"' not in line:
                        continue
                    try:
                        j = json.loads(line)
                    except ValueError:
                        continue
                    if j.get("event") != "gun_fired":
                        continue
                    det = j.get("details") or {}
                    ev = det.get("event") or (j.get("ticker", "")
                                              .rsplit("-", 1)[0])
                    if not ev or ev in _bells_mem["bells"]:
                        continue
                    gts = j.get("ts_epoch")
                    th = det.get("tts_honest_min")
                    _bells_mem["bells"][ev] = {
                        "gun_ts": gts,
                        "bell_ts": ((gts + th * 60)
                                    if (gts and th is not None) else gts),
                        "source": det.get("source") or "unknown"}
                _bells_mem["files"][key] = size - tail
                changed = True
            except OSError:
                continue
        if changed:
            try:
                BELLS_CACHE.write_text(json.dumps(
                    {"files": _bells_mem["files"],
                     "bells": _bells_mem["bells"]}), encoding="utf-8")
            except OSError:
                pass
        return _bells_mem["bells"]


def first_point_for(ev, sched_ep=None):
    """C-CORRIDOR-TRUTH (operator ruling, 07-16): the bell MEANS
    first-point evidence. A match cannot start before its scheduled
    time, so any bell ESTIMATE earlier than sched is by definition
    wrong — clamped to >= sched and filed BELL-BEFORE-SCHED. Evidence
    observations (scoreboard/tape/divergence) stand as observed, but a
    pre-sched observation is the same named contradiction, filed.
    Returns None when no gun row exists at all (render: 'first pt not
    observed (>= sched)')."""
    b = _bells().get(ev)
    if not b or not b.get("bell_ts"):
        return None
    src = b.get("source") or "unknown"
    observed = src in LIVE_BELL_SOURCES
    raw = b["bell_ts"]
    ts = raw
    defect = None
    if sched_ep and raw < sched_ep - 60:
        defect = "raw %s BEFORE sched %s" % (_hm(raw), _hm(sched_ep))
        _file_miss("bell_before_sched", "%s|raw=%s|sched=%s|src=%s"
                   % (ev, _hm(raw), _hm(sched_ep), src))
        if not observed:
            ts = sched_ep  # estimates clamp; observations stand, filed
    return {"raw_ts": raw, "ts": ts, "label": _hm(ts), "src": src,
            "observed": observed,
            "badge": "LIVE" if observed else "EST",
            "defect": defect}


def bell_for(ev):
    """Back-compat shim (first_point_for is the law)."""
    return first_point_for(ev)


# ── PUBLIC TRADES TAPE (Kalshi /markets/trades — no auth) ────────────────
_tape_lock = threading.Lock()


def _trades_fetch(ticker, min_ts):
    prints = []
    cursor = None
    for _ in range(6):
        url = ("https://api.elections.kalshi.com/trade-api/v2/markets/"
               "trades?ticker=%s&limit=1000" % ticker)
        if min_ts:
            url += "&min_ts=%d" % int(min_ts)
        if cursor:
            url += "&cursor=%s" % cursor
        req = urllib.request.Request(url, headers={"User-Agent":
                                                   "omi-daysheet-panel"})
        with urllib.request.urlopen(req, timeout=15) as r:
            d = json.load(r)
        rows = d.get("trades") or []
        for t in rows:
            ep = _iso_ep(t.get("created_time") or "")
            if ep is None:
                continue
            prints.append({
                "ts": ep,
                "price_c": int(round(float(t.get("yes_price_dollars")
                                           or 0) * 100)),
                "ct": float(t.get("count_fp") or 0)})
        cursor = d.get("cursor")
        if not cursor or not rows:
            break
        time.sleep(0.12)
    prints.sort(key=lambda x: x["ts"])
    return prints


def tape_for(ticker, sched_ep=None, bell_ts=None):
    """Disk-cached public tape. Settled/old games cache as final (their
    tape can't change); live games refresh on a 600s TTL. Returns the
    ascending prints list, or None on fetch failure (never cached)."""
    TAPE_DIR.mkdir(parents=True, exist_ok=True)
    p = TAPE_DIR / ("%s.json" % ticker)
    now = time.time()
    with _tape_lock:
        try:
            c = json.loads(p.read_text())
            if c.get("final") or now - c.get("fetched_at", 0) < 600:
                return c.get("prints") or []
        except Exception:
            pass
    min_ts = None
    anchor = sched_ep or bell_ts
    if anchor:
        min_ts = anchor - 30 * 3600  # T-30h covers the whole W1 horizon
    try:
        prints = _trades_fetch(ticker, min_ts)
    except Exception:
        _file_miss("tape_fetch_error", ticker)
        return None
    last = prints[-1]["ts"] if prints else 0
    final = bool(bell_ts and now > bell_ts + 6 * 3600
                 and now - last > 6 * 3600)
    with _tape_lock:
        try:
            p.write_text(json.dumps({"fetched_at": now, "final": final,
                                     "prints": prints}), encoding="utf-8")
        except OSError:
            pass
    return prints


def _win_cut(prints, lo_ts, hi_ts):
    sel = [x for x in prints
           if (lo_ts is None or x["ts"] >= lo_ts)
           and (hi_ts is None or x["ts"] < hi_ts)]
    if not sel:
        return None
    lo = min(sel, key=lambda x: x["price_c"])
    hi = max(sel, key=lambda x: x["price_c"])
    close = sel[-1]
    return {"lo": lo["price_c"], "hi": hi["price_c"],
            "close": close["price_c"], "n": len(sel),
            "lo_t": _hm(lo["ts"]), "hi_t": _hm(hi["ts"]),
            "close_t": _hm(close["ts"])}


def window_summary(ticker, sj, ev=None):
    """W1 / CORRIDOR cuts of the real tape for one leg under the
    CORRIDOR LAW (operator ruling 07-16): corridor = scheduled start ->
    first point, and it ALWAYS exists when the schedule anchor is known.
    W1 = before scheduled start. W2 = at/after the (clamped) first
    point. 'no corridor prints' renders only when the tape is genuinely
    empty in that span."""
    ev = ev or _ticker_pair_code(ticker)[1]
    sched_ep = sj.get("start_ep") if sj else None
    fp = first_point_for(ev, sched_ep)
    fp_ts = fp["ts"] if fp else None
    prints = tape_for(ticker, sched_ep, fp_ts)
    base = {"sched_ep": sched_ep,
            "sched_label": _hm(sched_ep) if sched_ep else None,
            "fp": fp, "bell": fp}  # bell key kept for back-compat
    if prints is None:
        base.update({"state": "tape_error", "w1": None, "corr": None,
                     "tape_n": 0})
        return base
    if not prints:
        _file_miss("no_tape", ticker)
        base.update({"state": "no_tape", "w1": None, "corr": None,
                     "tape_n": 0})
        return base
    w1_end = sched_ep or fp_ts
    corr = None
    if sched_ep:
        corr = _win_cut(prints, sched_ep, fp_ts)  # fp_ts None = ongoing
    base.update({"state": "ok",
                 "w1": _win_cut(prints, None, w1_end),
                 "corr": corr,
                 "tape_n": len(prints)})
    return base


def game_report_day(ep):
    return datetime.fromtimestamp(ep, ET).strftime("%Y%m%d")


# ── grades: DAYSHEET.json from the day + the prior log-day, merged ──────
def load_dayheet_grades(day):
    """Log files roll mid-day, so a game settled this morning grades in
    the PRIOR day's DAYSHEET.json. Merge both; the day's own rows win."""
    if FIXTURE_PATH:
        try:
            fx = json.loads(Path(FIXTURE_PATH).read_text())
            return {r["game"] + "-" + r["leg"]: r
                    for r in fx.get("dayheet_rows", [])}
        except Exception:
            return {}
    out = {}
    try:
        prev = (datetime.strptime(day, "%Y%m%d")
                - timedelta(days=1)).strftime("%Y%m%d")
    except ValueError:
        return {}
    for d in (prev, day):
        p = GAME_REPORTS_ROOT / d / "DAYSHEET.json"
        if not p.exists():
            continue
        try:
            for r in json.loads(p.read_text()):
                out[r.get("game", "") + "-" + r.get("leg", "")] = r
        except Exception:
            continue
    return out


def _grade_lookup(grades, ev, leg_suffix):
    for gk in (ev[-16:], ev.split("-", 1)[-1], ev):
        row = grades.get(gk + "-" + leg_suffix)
        if row:
            return row
    for k, row in grades.items():
        g, _, l = k.rpartition("-")
        if l == leg_suffix and g and ev.endswith(g):
            return row
    return None


# ── walk footnotes (the standing format: charge -> amendment -> verdict) ─
def walk_footnote(ev):
    code, _ = _ticker_pair_code(ev + "-X")
    if not WALKS_ROOT.exists():
        return None
    for d in sorted(WALKS_ROOT.iterdir(), reverse=True):
        p = d / ("WALK_%s.md" % code)
        if not p.is_file():
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None

        def _first(pattern, n=260):
            m = re.search(pattern, txt, re.S)
            if not m:
                return None
            s = re.sub(r"\*+", "", m.group(1)).strip()
            s = re.sub(r"\s+", " ", s)
            return (s[:n] + "…") if len(s) > n else s
        charge = _first(r"\*\*THE CHARGE[^:]*:\*\*\s*(.+?)(?:\n\n|\n#)")
        amend = _first(r"Spoken as consultation, by the OS:\*\*\s*[\"“]?"
                       r"(.+?[.!])", 200)
        verdict = _first(r"Verdict in window terms:?\s*(.+?)(?:\n|$)", 220)
        return {"walk": "%s/%s" % (d.name, p.name), "charge": charge,
                "amendment": amend, "verdict": verdict}
    return None


def order_history_for_ticker(ticker):
    """Order-history-sourced status for a leg with NO current fill — the
    'did we even try' line, from snap_orders history + flags only."""
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


def _game_head(sample_ticker):
    sj = join_match_name(sample_ticker)
    ev = sj["event"]
    sched_ep = sj.get("start_ep")
    fp = first_point_for(ev, sched_ep)
    return sj, {
        "event": ev,
        "joined": sj.get("joined", False),
        "names": ("%s v %s" % (sj["p1_disp"], sj["p2_disp"])
                  if sj.get("joined") else "name join pending"),
        "start_time": sj.get("start_time"),
        "tournament": sj.get("tournament"),
        "category": sj.get("category"),
        # both anchors, always (corridor law): sched + first point
        "anchors": {"sched": _hm(sched_ep) if sched_ep else None,
                    "fp": fp},
        "bell": fp,  # back-compat
        "deeplink": kalshi_deeplink(ev),
    }


# ── /api/positions.json ──────────────────────────────────────────────────
def build_positions():
    if FIXTURE_PATH:
        return json.loads(Path(FIXTURE_PATH).read_text()).get(
            "positions", [])

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

    events = {}
    for tk, qty, exp, mk in pos_rows:
        if qty == 0:
            continue
        _, ev = _ticker_pair_code(tk)
        events.setdefault(ev, []).append((tk, qty, exp, mk))

    out = []
    for ev, legs in events.items():
        sj, game_out = _game_head(legs[0][0])
        game_out["legs"] = []
        game_out["walk"] = walk_footnote(ev)  # provisional walks render
        for tk, qty, exp, mk in legs:
            basis = int(exp / qty) if qty else 0
            fill = fills_by_ticker.get(tk)
            exit_order = sells.get(tk)
            win = window_summary(tk, sj, ev)
            game_out["legs"].append({
                "ticker": tk,
                "last_name": leg_last_name(tk, sj),
                "qty": qty,
                "basis_c": basis,
                "mark_c": int(mk / qty) if qty else 0,
                "win": win,
                "exit_resting": (
                    {"price_c": exit_order[0], "qty": exit_order[1]}
                    if exit_order else None),
                "deeplink": kalshi_deeplink(tk),
                # PLACED ET: no honest source in the schema (open-ledger
                # gap) — never backfilled from the fill time.
                "placed_et": None,
                "filled_et": (_hm(fill[1]) if fill else None),
                "fill_price_c": fill[2] if fill else None,
            })
        held = {l["last_name"] for l in game_out["legs"] if l["last_name"]}
        if sj.get("joined"):
            for other in (sj["p1_last"], sj["p2_last"]):
                if other not in held:
                    sib_tk = ev + "-" + other.replace(" ", "")[:3]
                    hist = order_history_for_ticker(sib_tk)
                    game_out["gray_line"] = "%s — %s" % (
                        other, hist if hist else
                        "not bid — never conceived")
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
        _, ev = _ticker_pair_code(tk)
        events.setdefault(ev, []).append((tk, px, rem, ts))
    out = []
    now = time.time()
    for ev, legs in events.items():
        sj, game_out = _game_head(legs[0][0])
        game_out["legs"] = []
        for tk, px, rem, ts in legs:
            age_s = now - ts
            game_out["legs"].append({
                "ticker": tk,
                "last_name": leg_last_name(tk, sj),
                "aim_c": px,
                "qty": rem,
                "win": window_summary(tk, sj, ev),
                "age_label": "%dh%dm" % (age_s // 3600,
                                         (age_s % 3600) // 60),
            })
        out.append(game_out)
    return out


# ── /api/closed.json — ONE ROW PER LEG ───────────────────────────────────
def build_closed(day=None):
    if FIXTURE_PATH:
        return json.loads(Path(FIXTURE_PATH).read_text()).get("closed", [])

    day = day or datetime.now(ET).strftime("%Y%m%d")
    grades = load_dayheet_grades(day)

    day_tickers = sorted({r[0] for r in _q(
        "SELECT DISTINCT ticker FROM fills WHERE day=?", (day,))})
    events = {}
    for tk in day_tickers:
        _, ev = _ticker_pair_code(tk)
        events.setdefault(ev, []).append(tk)

    out = []
    for ev, tickers in events.items():
        sj, game_out = _game_head(tickers[0])
        game_out.update({"legs": [], "grade": None,
                         "grade_status": "ungraded",
                         "footnote": None,
                         "walk": walk_footnote(ev)})
        leg_grades = []
        for tk in tickers:
            # ALL fills for the leg (entry may predate the queried day) —
            # ONE ROW PER LEG: buys average to OURS, sells are the exit.
            rows = _q("SELECT ts, action, yes_price_c, count_fp FROM "
                      "fills WHERE ticker=? ORDER BY ts", (tk,))
            buys = [(ts, px, ct) for ts, a, px, ct in rows if a == "buy"]
            sells = [(ts, px, ct) for ts, a, px, ct in rows
                     if a == "sell"]
            bct = sum(c for _, _, c in buys)
            sct = sum(c for _, _, c in sells)
            avg_buy = (sum(p * c for _, p, c in buys) / bct) if bct \
                else None
            avg_sell = (sum(p * c for _, p, c in sells) / sct) if sct \
                else None
            leg_suffix = tk.rsplit("-", 1)[-1]
            gr_row = _grade_lookup(grades, ev, leg_suffix)
            leg_grade = (gr_row.get("grade") if gr_row else None)
            if leg_grade:
                leg_grades.append(re.sub(r"\(.*\)", "", leg_grade))
            outcome = (gr_row or {}).get("outcome")
            realized_c = None
            dollars = (gr_row or {}).get("dollars") or ""
            m = re.match(r"([+-]\d+)¢", dollars)
            if m:
                realized_c = int(m.group(1))
            elif avg_sell is not None and avg_buy is not None:
                realized_c = int(round((avg_sell - avg_buy)
                                       * min(bct, sct)))
            result = ("99" if outcome == "SETTLED-WIN" else
                      "1" if outcome == "SETTLED-LOSS" else
                      "cashed" if (outcome == "CASHED" or
                                   (sct and bct and sct >= bct)) else
                      "open")
            win = window_summary(tk, sj, ev)
            ours = int(round(avg_buy)) if avg_buy is not None else None
            w1c = ((win.get("w1") or {}).get("close")
                   if win.get("w1") else None)
            # fill window under the CLAMPED clocks (corridor law):
            # W1 < sched · CORR in [sched, first point) · W2 >= first pt
            fill_window = None
            if buys:
                fts = buys[-1][0]
                sched_ep = win.get("sched_ep")
                fpts = (win.get("fp") or {}).get("ts")
                if sched_ep and fts < sched_ep:
                    fill_window = "W1"
                elif fpts and fts >= fpts:
                    fill_window = "W2"
                elif sched_ep:
                    fill_window = "CORR"
                elif fpts:
                    fill_window = "W1" if fts < fpts else "W2"
            # RE-GRADE (part 4): an F whose only charge was post-bell by
            # an EST bell earlier than sched dissolves when the clamped
            # clock says the fill was NOT W2 — regrade by the same
            # pnl rubric game_report uses.
            grade_was = None
            if (leg_grade and leg_grade.startswith("F")
                    and fill_window in ("W1", "CORR")):
                grade_was = leg_grade
                leg_grade = ("A" if (realized_c or 0) > 0 else
                             "B" if realized_c in (0, None) else "C")
                leg_grades[-1] = leg_grade
            game_out["legs"].append({
                "ticker": tk,
                "last_name": leg_last_name(tk, sj),
                "ours_c": ours,
                "n_entry_fills": len(buys),
                "qty": bct,
                "filled_et": _hm(buys[-1][0]) if buys else None,
                "placed_et": None,  # schema gap, open ledger
                "fill_window": fill_window,
                "exit": ({"price_c": int(round(avg_sell)), "qty": sct,
                          "at": _hm(sells[-1][0])} if sct else None),
                "win": win,
                # Δ only has meaning on W1 fills (time law, part 5)
                "delta_c": ((ours - w1c)
                            if (fill_window == "W1"
                                and ours is not None
                                and w1c is not None) else None),
                "result": result,
                "realized_c": realized_c,
                "grade": leg_grade,
                "grade_was": grade_was,
                "grade_row": gr_row,
            })
        if leg_grades:
            order = {"A": 0, "B": 1, "C": 2, "D": 3, "F": 4}
            game_out["grade"] = max(leg_grades,
                                    key=lambda g: order.get(g, 9))
            game_out["grade_status"] = "graded"
        out.append(game_out)
    return out


# ── /api/tape/<ticker>.json — proof-on-click, REAL public tape ───────────
def build_tape(ticker):
    if FIXTURE_PATH:
        fx = json.loads(Path(FIXTURE_PATH).read_text())
        return fx.get("tape", {}).get(ticker,
                                      {"prints": [], "has_receipt": False})

    sj = join_match_name(ticker)
    ev = sj["event"]
    bell = bell_for(ev)
    prints = tape_for(ticker, sj.get("start_ep"),
                      bell["ts"] if bell else None)
    if prints is None:
        return {"prints": [], "has_receipt": False,
                "source": "kalshi_public_trades", "error": "fetch_error"}
    if not prints:
        _file_miss("no_tape", ticker)
        return {"prints": [], "has_receipt": False,
                "source": "kalshi_public_trades"}
    ws = window_summary(ticker, sj, ev)
    recent = [{
        "t": datetime.fromtimestamp(x["ts"], ET).strftime(
            "%b %-d %-I:%M %p"),
        "price_c": x["price_c"], "ct": round(x["ct"], 1),
    } for x in prints[-25:]]
    return {"prints": recent, "n_total": len(prints), "has_receipt": True,
            "source": "kalshi_public_trades",
            "windows": {"w1": ws.get("w1"), "corr": ws.get("corr")},
            "bell": ws.get("bell")}


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
