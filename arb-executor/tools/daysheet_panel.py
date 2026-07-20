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
                     "schedule_live", "self_fill",
                     "milestone_official"}


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


def _kalshi_get(path):
    url = "https://api.elections.kalshi.com/trade-api/v2" + path
    req = urllib.request.Request(url, headers={"User-Agent":
                                               "omi-daysheet-panel"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)


def _structured_target(cid):
    """Third name-law source (C-MILESTONE-SHADOW word, 07-16): Kalshi's
    structured target carries the player's AUTHORITATIVE last_name and
    the exact ticker abbreviation. Cached forever per competitor id."""
    NAMES_DIR.mkdir(parents=True, exist_ok=True)
    p = NAMES_DIR / ("st_%s.json" % cid)
    try:
        return json.loads(p.read_text())
    except Exception:
        pass
    try:
        d = _kalshi_get("/structured_targets/%s" % cid)
    except Exception:
        return None  # never cache a failure
    st = (d.get("structured_target") or {})
    det = st.get("details") or {}
    out = {"last": det.get("last_name"), "abbr": det.get("abbreviation"),
           "name": st.get("name")}
    if out["last"] or out["name"]:
        try:
            p.write_text(json.dumps(out), encoding="utf-8")
        except OSError:
            pass
        return out
    return None


def _kalshi_event_names(ev):
    """Exchange-truth name fallback: Kalshi's own event object carries
    the surnames in the title ('Wu vs Bu') and each leg's full player
    name in yes_sub_title — keyed by the ticker itself, never a fuzzy
    guess; enriched with the structured target's authoritative
    last_name + abbreviation per leg. Disk-cached forever. Needed
    because Kalshi keys pair codes on GIVEN names (YIBYUN =
    Yibing/Yunchaokete) where TennisExplorer keys surnames (WUYUN)."""
    NAMES_DIR.mkdir(parents=True, exist_ok=True)
    p = NAMES_DIR / ("%s.json" % ev)
    stale = None
    try:
        c = json.loads(p.read_text())
        if c.get("v") == 2:
            return c
        stale = c  # v1 format — still valid for names/suffixes
    except Exception:
        pass
    try:
        d = _kalshi_get("/events/%s?with_nested_markets=true" % ev)
    except Exception:
        return stale  # transient fetch failure: the stale cache beats
        # nothing (never cache the failure itself)
    e = d.get("event") or {}
    legs = {}
    for m in e.get("markets") or []:
        suffix = (m.get("ticker") or "").rsplit("-", 1)[-1]
        nm = (m.get("yes_sub_title") or "").strip()
        if not (suffix and nm):
            continue
        entry = {"full": nm, "last": None, "abbr": None}
        cid = (m.get("custom_strike") or {}).get("tennis_competitor")
        if cid:
            st = _structured_target(cid)
            if st:
                entry["last"] = st.get("last")
                entry["abbr"] = st.get("abbr")
        legs[suffix] = entry
    title = (e.get("title") or "").strip()
    if not legs or " vs " not in title:
        return None
    out = {"v": 2, "title": title, "legs": legs}
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
                _st_ep = _log_scan()["starts"].get(ev)
                return {
                    "joined": True,
                    "source": "kalshi_event",
                    "event": ev,
                    "p1_last": t1.upper(),
                    "p2_last": t2.upper(),
                    "p1_disp": t1,
                    "p2_disp": t2,
                    "kalshi_legs": kn["legs"],
                    # sched anchor from the engine's own logged join —
                    # survives TE forgetting finished games
                    "start_time": None,
                    "start_ep": _st_ep,
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
        entry = kl[leg]
        if isinstance(entry, dict):
            if entry.get("last"):  # structured target: authoritative
                return entry["last"].upper()
            full = (entry.get("full") or "")
        else:
            full = entry  # pre-v2 cache format
        nm = full.upper()
        for last in (sj["p1_last"], sj["p2_last"]):
            if nm.endswith(last):
                return last
        return full or None  # full player name — never a fragment
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
_bells_mem = {"files": {}, "bells": {}, "orders": {}, "starts": {},
              "loaded": False, "checked": 0.0}


def _log_scan():
    """One incremental pass over live_v3_<day>.jsonl (today + yesterday;
    log files roll mid-day) collecting BOTH bells (gun_fired) and the
    per-ticker BUY-ORDER HISTORY (order_placed/order_cancelled) — the
    sibling-disposition source. snap_orders only retains 2h, so it
    CANNOT answer 'was the missing side honestly attempted' for a
    morning game; the engine's own log can. Byte-offset incremental,
    persisted to state/daysheet_bells.json (v2)."""
    with _bells_lock:
        now = time.time()
        if not _bells_mem["loaded"]:
            try:
                disk = json.loads(BELLS_CACHE.read_text())
                if disk.get("v") == 3:
                    _bells_mem["files"] = disk.get("files", {})
                    _bells_mem["bells"] = disk.get("bells", {})
                    _bells_mem["orders"] = disk.get("orders", {})
                    _bells_mem["starts"] = disk.get("starts", {})
                # older cache: leave offsets empty -> full rescan once
            except Exception:
                pass
            _bells_mem["loaded"] = True
        if now - _bells_mem["checked"] < 30:
            return _bells_mem
        _bells_mem["checked"] = now
        days = [(datetime.now(ET) - timedelta(days=n)).strftime("%Y%m%d")
                for n in (2, 1, 0)]  # day-2: schedule_match anchors log at first sight
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
                    is_gun = b'"gun_fired"' in line
                    is_place = b'"order_placed"' in line
                    is_cancel = b'"order_cancelled"' in line
                    is_sched = b'"schedule_match"' in line
                    if not (is_gun or is_place or is_cancel or is_sched):
                        continue
                    try:
                        j = json.loads(line)
                    except ValueError:
                        continue
                    e = j.get("event")
                    det = j.get("details") or {}
                    ts = j.get("ts_epoch")
                    if e == "gun_fired":
                        ev = det.get("event") or (j.get("ticker", "")
                                                  .rsplit("-", 1)[0])
                        if not ev or ev in _bells_mem["bells"]:
                            continue
                        th = det.get("tts_honest_min")
                        _bells_mem["bells"][ev] = {
                            "gun_ts": ts,
                            "bell_ts": ((ts + th * 60)
                                        if (ts and th is not None)
                                        else ts),
                            "source": det.get("source") or "unknown"}
                        changed = True
                    elif e == "order_placed" \
                            and det.get("action") == "buy":
                        tk = j.get("ticker")
                        if not tk:
                            continue
                        o = _bells_mem["orders"].setdefault(
                            tk, {"first_ts": ts,
                                 "first_px": det.get("price"),
                                 "n_posts": 0, "last_post_ts": ts,
                                 "last_cancel_ts": None,
                                 "last_cancel_label": None})
                        o["n_posts"] += 1
                        o["last_post_ts"] = ts
                        changed = True
                    elif e == "order_cancelled":
                        tk = j.get("ticker")
                        o = _bells_mem["orders"].get(tk)
                        if o is not None:
                            o["last_cancel_ts"] = ts
                            o["last_cancel_label"] = det.get("label")
                            changed = True
                    elif e == "schedule_match":
                        # [07-17] the sched anchor banked from the
                        # engine's own join — it survives TE's midnight
                        # forgetting of finished games (the no_anchor
                        # regression on yesterday's sheet)
                        ev = det.get("event")
                        _st = _iso_ep(det.get("start_time") or "")
                        if ev and _st:
                            _bells_mem["starts"][ev] = _st
                            changed = True
                _bells_mem["files"][key] = size - tail
                changed = True
            except OSError:
                continue
        if changed:
            try:
                BELLS_CACHE.write_text(json.dumps(
                    {"v": 3, "files": _bells_mem["files"],
                     "bells": _bells_mem["bells"],
                     "orders": _bells_mem["orders"],
                     "starts": _bells_mem["starts"]}), encoding="utf-8")
            except OSError:
                pass
        return _bells_mem


def _bells():
    return _log_scan()["bells"]


def log_order_history(ticker):
    """Sibling disposition from the engine's own log (full-day truth,
    unlike snap_orders' 2h window). Returns (text, cap) where cap is
    'C' (honestly attempted — posted lawful, never traded there) or
    'D' (pulled-and-abandoned / never conceived), per the pair law."""
    o = _log_scan()["orders"].get(ticker)
    if not o:
        hist = order_history_for_ticker(ticker)  # snap_orders fallback
        if hist:
            return (hist, "D" if "pulled" in hist else "C")
        return ("not bid — never conceived", "D")
    px = o.get("first_px")
    when = _hm(o["first_ts"]) if o.get("first_ts") else "?"
    if o.get("last_cancel_ts") and (o.get("last_post_ts") or 0) \
            <= o["last_cancel_ts"]:
        label = o.get("last_cancel_label") or "cancel"
        # the BELL SWEEP is not abandonment: a bid that rested until
        # match_live/settlement swept it was the honest attempt (C).
        # A pull by our own machinery mid-window with no re-place is
        # pulled-and-abandoned (D).
        swept = ("match_live" in label or "settlement" in label
                 or "shutdown" in label)
        if swept:
            return ("posted %s¢ (%s, ×%d) · held to the bell sweep "
                    "(%s %s) · never traded that low"
                    % (px, when, o.get("n_posts", 1), label,
                       _hm(o["last_cancel_ts"])), "C")
        return ("posted %s¢ (%s, ×%d) · pulled (%s %s) · never re-placed"
                % (px, when, o.get("n_posts", 1), label,
                   _hm(o["last_cancel_ts"])), "D")
    return ("posted %s¢ (%s, ×%d) · never traded that low"
            % (px, when, o.get("n_posts", 1)), "C")


def log_order_history_dict(ticker):
    """Structured sibling disposition (Plex render-ownership, 07-17).
    Reads the exact same log lines log_order_history() reads. Returns a
    dict the template renders as digits/icons only, no prose."""
    o = _log_scan()["orders"].get(ticker)
    if not o:
        hist = order_history_for_ticker(ticker)
        if hist:
            return {"kind": "pulled" if "pulled" in hist else "held",
                    "px": None, "qty": None, "ep": None,
                    "pulled_by": None, "pulled_ep": None,
                    "cap": "D" if "pulled" in hist else "C",
                    "source": "snap_orders_fallback"}
        return {"kind": "never_bid",
                "px": None, "qty": None, "ep": None,
                "pulled_by": None, "pulled_ep": None,
                "cap": "D", "source": "none"}
    px = o.get("first_px")
    ep = o.get("first_ts")
    qty = o.get("n_posts", 1)
    cancel_ts = o.get("last_cancel_ts")
    post_ts = o.get("last_post_ts") or 0
    if cancel_ts and post_ts <= cancel_ts:
        label = o.get("last_cancel_label") or "cancel"
        swept = ("match_live" in label or "settlement" in label
                 or "shutdown" in label)
        return {"kind": "held" if swept else "pulled",
                "px": px, "qty": qty, "ep": ep,
                "pulled_by": label, "pulled_ep": cancel_ts,
                "cap": "C" if swept else "D",
                "source": "engine_log"}
    return {"kind": "held",
            "px": px, "qty": qty, "ep": ep,
            "pulled_by": None, "pulled_ep": None,
            "cap": "C", "source": "engine_log"}


OFFICIAL_BELLS = ROOT / "state" / "daysheet_bells_official.json"
_official_lock = threading.Lock()
_official_mem = {"loaded": False, "data": {}}


def official_bell(ev):
    """C-OFFICIAL-BELL v1 (07-16): the OFFICIAL record — Kalshi's
    milestone start_date (Sportradar-fed, second precision; finished
    games retain the actual start). status 'not_started' means the
    start_date is still the schedule, NOT an observation — no official
    bell. Disk-cached; final once status='P'."""
    with _official_lock:
        if not _official_mem["loaded"]:
            try:
                _official_mem["data"] = json.loads(
                    OFFICIAL_BELLS.read_text())
            except Exception:
                _official_mem["data"] = {}
            _official_mem["loaded"] = True
        now = time.time()
        e = _official_mem["data"].get(ev)
        if e is not None and (e.get("final")
                              or now - e.get("fetched_at", 0) < 300):
            pass
        else:
            try:
                d = _kalshi_get("/milestones?related_event_ticker=%s"
                                "&limit=5" % ev)
                ms = (d.get("milestones") or [None])[0]
            except Exception:
                ms = None
                d = None
            if d is not None:
                if ms:
                    det = ms.get("details") or {}
                    e = {"fetched_at": now,
                         "status": det.get("status"),
                         "start_date": ms.get("start_date"),
                         "start_ep": _iso_ep(ms.get("start_date") or ""),
                         "final": det.get("status") == "P"}
                else:
                    e = {"fetched_at": now, "status": None,
                         "start_date": None, "start_ep": None,
                         "final": False}
                _official_mem["data"][ev] = e
                try:
                    OFFICIAL_BELLS.write_text(
                        json.dumps(_official_mem["data"]),
                        encoding="utf-8")
                except OSError:
                    pass
        if not e or not e.get("start_ep") \
                or e.get("status") in (None, "not_started"):
            return None
        return {"ts": e["start_ep"], "label": _hm(e["start_ep"]),
                "status": e.get("status")}


def _est_note(ev):
    """The demoted estimate/evidence hover note (never THE bell)."""
    b = _bells().get(ev)
    if not b or not b.get("bell_ts"):
        return None
    src = b.get("source") or "unknown"
    kind = "our evidence" if src in LIVE_BELL_SOURCES else "est"
    return "%s %s (%s) — demoted to note" % (kind, _hm(b["bell_ts"]), src)


def first_point_for(ev, sched_ep=None):
    """THE BELL under C-OFFICIAL-BELL v1: (1) the OFFICIAL milestone
    start (badge OFFICIAL [KALSHI]); (2) else our own LIVE first-point
    evidence (scoreboard/tape/divergence — the corridor-truth sources);
    (3) estimates NEVER serve as a clock — demoted to the hover note.
    Pre-sched bells file BELL-BEFORE-SCHED (observations stand, filed;
    the estimate class census keeps accruing). Returns None when no
    official record and no evidence — render 'bell not observed
    (>= sched)', never a fabricated time."""
    ob = official_bell(ev)
    note = _est_note(ev)
    if ob:
        defect = None
        if sched_ep and ob["ts"] < sched_ep - 60:
            defect = "official %s BEFORE sched %s" % (ob["label"],
                                                      _hm(sched_ep))
            _file_miss("bell_before_sched", "%s|official=%s|sched=%s"
                       % (ev, ob["label"], _hm(sched_ep)))
        return {"raw_ts": ob["ts"], "ts": ob["ts"], "label": ob["label"],
                "src": "official [KALSHI]", "badge": "OFFICIAL",
                "observed": True, "est_note": note, "defect": defect}
    b = _bells().get(ev)
    if b and b.get("bell_ts") \
            and (b.get("source") or "unknown") in LIVE_BELL_SOURCES:
        src = b["source"]
        raw = b["bell_ts"]
        defect = None
        if sched_ep and raw < sched_ep - 60:
            # [ENTRY-MECHANICS P6a 07-17 + P0v3 (1)] THE GLASS TELLS THE
            # ADJUDICATED TRUTH: a pre-sched evidence fire is a PHANTOM
            # BELL — VOID as a clock (sched is the floor of time). The
            # clock CLAMPS to sched, the badge carries the void, and the
            # W1/CORR/W2 cut downstream grades fills against the clamped
            # clock (the census's phantom-relabeled fills render W1 with
            # their earned grades; true post-bell fills still wear F).
            defect = "raw %s BEFORE sched %s — VOID, clamped" % (
                _hm(raw), _hm(sched_ep))
            _file_miss("bell_before_sched", "%s|raw=%s|sched=%s|src=%s"
                       % (ev, _hm(raw), _hm(sched_ep), src))
            return {"raw_ts": raw, "ts": sched_ep, "label": _hm(sched_ep),
                    "src": src, "badge": "VOID(pre-sched)→SCHED",
                    "observed": True, "est_note": note, "defect": defect}
        return {"raw_ts": raw, "ts": raw, "label": _hm(raw), "src": src,
                "badge": "LIVE", "observed": True, "est_note": note,
                "defect": defect}
    if b and b.get("bell_ts") and sched_ep \
            and b["bell_ts"] < sched_ep - 60:
        # estimate-quality census stays alive even though estimates no
        # longer serve as clocks
        _file_miss("bell_before_sched", "%s|raw=%s|sched=%s|src=%s"
                   % (ev, _hm(b["bell_ts"]), _hm(sched_ep),
                      b.get("source")))
    return None


def bell_for(ev):
    """Back-compat shim (first_point_for is the law)."""
    return first_point_for(ev)


# ── PUBLIC TRADES TAPE (Kalshi /markets/trades — no auth) ────────────────
_tape_lock = threading.Lock()


def _trades_fetch(ticker, min_ts):
    """Newest-first pages. Pages until the fetch REACHES min_ts (or the
    tape's own beginning) so W1 is never silently truncated on
    high-volume games; if the page cap trips first, coverage is reported
    honestly (covered_from = oldest fetched print), never rendered as
    'no prints' [De Santis exhibit / SILENT-EMPTY TAPE LOOKUP]."""
    prints = []
    cursor = None
    complete = False
    for _ in range(40):
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
            complete = True
            break
        time.sleep(0.12)
    prints.sort(key=lambda x: x["ts"])
    covered_from = (min_ts if complete
                    else (prints[0]["ts"] if prints else None))
    return prints, covered_from


def tape_for(ticker, sched_ep=None, bell_ts=None):
    """Disk-cached public tape. Settled/old games cache as final (their
    tape can't change); live games refresh on a 600s TTL. Returns
    {'prints': ascending list, 'covered_from': epoch|None} or None on
    fetch failure (never cached). covered_from = the honest left edge
    of coverage; a window cut left of it is a TAPE GAP, not a fact."""
    TAPE_DIR.mkdir(parents=True, exist_ok=True)
    p = TAPE_DIR / ("%s.json" % ticker)
    now = time.time()
    with _tape_lock:
        try:
            c = json.loads(p.read_text())
            # v2 = coverage-aware entries only; v1 caches refetch once
            if c.get("v") == 2 and (c.get("final")
                                    or now - c.get("fetched_at", 0) < 600):
                return {"prints": c.get("prints") or [],
                        "covered_from": c.get("covered_from")}
        except Exception:
            pass
    min_ts = None
    anchor = sched_ep or bell_ts
    if anchor:
        min_ts = anchor - 30 * 3600  # T-30h covers the whole W1 horizon
    try:
        prints, covered_from = _trades_fetch(ticker, min_ts)
    except Exception:
        _file_miss("tape_fetch_error", ticker)
        return None
    last = prints[-1]["ts"] if prints else 0
    final = bool(bell_ts and now > bell_ts + 6 * 3600
                 and now - last > 6 * 3600)
    with _tape_lock:
        try:
            p.write_text(json.dumps({"v": 2, "fetched_at": now,
                                     "final": final,
                                     "covered_from": covered_from,
                                     "prints": prints}), encoding="utf-8")
        except OSError:
            pass
    return {"prints": prints, "covered_from": covered_from}


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
            "close_t": _hm(close["ts"]),
            # [DISPATCH-2 PHASE A rider (a) 07-17] the W1 low CARRIES ITS
            # TIME — raw epoch so renders can say "12c @T-14h"
            "lo_ts": lo["ts"]}


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
    tp = tape_for(ticker, sched_ep, fp_ts)
    base = {"sched_ep": sched_ep,
            "sched_label": _hm(sched_ep) if sched_ep else None,
            "fp": fp, "bell": fp}  # bell key kept for back-compat
    if tp is None:
        base.update({"state": "tape_error", "w1": None, "corr": None,
                     "w1_state": "tape_error", "corr_state": "tape_error",
                     "tape_n": 0})
        return base
    prints, covered_from = tp["prints"], tp.get("covered_from")
    if not prints:
        _file_miss("no_tape", ticker)
        base.update({"state": "no_tape", "w1": None, "corr": None,
                     "w1_state": "no_tape", "corr_state": "no_tape",
                     "tape_n": 0})
        return base
    # W1 ends at the SCHED anchor only (corridor law). Without a sched
    # anchor W1 is UNKNOWABLE — an empty cut against an EST bell must
    # never render as 'no W1 prints' [De Santis exhibit].
    w1 = corr = None
    if sched_ep:
        w1 = _win_cut(prints, None, sched_ep)
        if w1 is None and covered_from is not None \
                and covered_from >= sched_ep:
            _file_miss("tape_coverage_gap", "%s|w1" % ticker)
            w1_state = "tape_gap"
        else:
            w1_state = "ok" if w1 else "none"
        corr = _win_cut(prints, sched_ep, fp_ts)  # fp None = ongoing
        corr_state = "ok" if corr else "none"
    else:
        _file_miss("w1_anchor_gap", ticker)
        w1_state = "no_anchor"
        corr_state = "no_anchor"
    base.update({"state": "ok", "w1": w1, "corr": corr,
                 "w2": (_win_cut(prints, fp_ts, None) if fp_ts else None),
                 "w1_state": w1_state, "corr_state": corr_state,
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


_l1_lock = threading.Lock()
_l1_mem = {}


def l1_best(ticker):
    """[4b, 07-17] FRESH level-1 best on demand (public market object,
    30s TTL) — the resting-order row shows the book top NOW, not the
    recorder's last snapshot."""
    now = time.time()
    with _l1_lock:
        c = _l1_mem.get(ticker)
        if c and now - c[0] < 30:
            return c[1]
    try:
        m = (_kalshi_get("/markets/%s" % ticker) or {}).get("market") or {}
        out = {"bid": int(round(float(m.get("yes_bid_dollars") or 0) * 100)),
               "ask": int(round(float(m.get("yes_ask_dollars") or 0) * 100))}
        if not (0 < out["bid"] <= 99 or 0 < out["ask"] <= 100):
            out = None
    except Exception:
        out = None  # transient: render the recorder mark, never cache
    if out is not None:
        with _l1_lock:
            _l1_mem[ticker] = (now, out)
    return out


def order_created_et(order_ids):
    """[4c PLACED-ET, 07-17] earliest Kalshi order created_time among the
    given order ids, from the recorder's permanent orders_ledger. None =
    genuinely absent (pre-build orders) — the gap stays named, never
    backfilled from fill time."""
    ids = [o for o in (order_ids or []) if o]
    if not ids:
        return None
    qmarks = ",".join("?" * len(ids))
    rows = _q("SELECT MIN(created_ep) FROM orders_ledger "
              "WHERE order_id IN (%s) AND created_ep IS NOT NULL"
              % qmarks, tuple(ids))
    ep = rows[0][0] if rows and rows[0] else None
    return _hm(ep) if ep else None


def order_created_ep(order_ids):
    """Raw-epoch twin of order_created_et (Plex T−X law wants epochs)."""
    ids = [o for o in (order_ids or []) if o]
    if not ids:
        return None
    rows = _q("SELECT MIN(created_ep) FROM orders_ledger "
              "WHERE order_id IN (%s) AND created_ep IS NOT NULL"
              % ",".join("?" * len(ids)), tuple(ids))
    return rows[0][0] if rows and rows[0] else None


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
        # both anchors, always (corridor law): sched + THE bell
        # (official > our LIVE evidence > not-observed; estimates
        # demoted to the hover note)
        "anchors": {"sched": _hm(sched_ep) if sched_ep else None,
                    "sched_ep": sched_ep,
                    "fp": fp,
                    "est_note": (fp.get("est_note") if fp
                                 else _est_note(ev))},
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
                "l1": l1_best(tk),
                # [4c] PLACED ET now sourced from the orders_ledger via
                # the fill's own order_id; None = pre-build order (the
                # gap stays named, never backfilled from fill time)
                "placed_et": (order_created_et([fill[4]])
                              if fill else None),
                "placed_ep": (order_created_ep([fill[4]])
                              if fill else None),
                "filled_et": (_hm(fill[1]) if fill else None),
                "fill_ep": (fill[1] if fill else None),
                "fill_price_c": fill[2] if fill else None,
            })
        # [4a quadruplet + honest suffixes] the unworked side resolves
        # its TRUE ticker from the Kalshi event object (never the
        # surname[:3] guess — the YIBYUN lesson) and carries its own
        # tape row (W1+CORR) beside the disposition line.
        game_out["sibling_tape"] = None
        kn_p = _kalshi_event_names(ev)
        if kn_p and isinstance(kn_p.get("legs"), dict):
            _held_sfx = {l["ticker"].rsplit("-", 1)[-1]
                         for l in game_out["legs"]}
            _miss_p = [x for x in kn_p["legs"] if x not in _held_sfx]
            if _miss_p:
                _sfx_p = _miss_p[0]
                _stk_p = ev + "-" + _sfx_p
                _en_p = kn_p["legs"].get(_sfx_p)
                _nm_p = ((_en_p.get("last") or _en_p.get("full"))
                         if isinstance(_en_p, dict) else
                         (_en_p if isinstance(_en_p, str) else _sfx_p))
                hist, _cap_p = log_order_history(_stk_p)
                game_out["gray_line"] = "%s — %s" % (
                    (_nm_p or _sfx_p).upper(), hist)
                game_out["sibling_tape"] = {
                    "ticker": _stk_p,
                    "last_name": (_nm_p or _sfx_p).upper(),
                    "win": window_summary(_stk_p, sj, ev)}
        elif sj.get("joined"):
            held = {l["last_name"] for l in game_out["legs"]
                    if l["last_name"]}
            for other in (sj["p1_last"], sj["p2_last"]):
                if other not in held:
                    hist = order_history_for_ticker(
                        ev + "-" + other.replace(" ", "")[:3])
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
        "SELECT ticker, yes_price_c, remaining, ts, order_id "
        "FROM snap_orders "
        "WHERE ts=(SELECT MAX(ts) FROM snap_orders) AND action='buy' "
        "AND remaining > 0")
    events = {}
    for tk, px, rem, ts, oid in rows:
        _, ev = _ticker_pair_code(tk)
        events.setdefault(ev, []).append((tk, px, rem, ts, oid))
    out = []
    now = time.time()
    for ev, legs in events.items():
        sj, game_out = _game_head(legs[0][0])
        game_out["legs"] = []
        for tk, px, rem, ts, oid in legs:
            age_s = now - ts
            game_out["legs"].append({
                "ticker": tk,
                "last_name": leg_last_name(tk, sj),
                "aim_c": px,
                "qty": rem,
                "win": window_summary(tk, sj, ev),
                "l1": l1_best(tk),
                "placed_et": order_created_et([oid]),
                "placed_ep": order_created_ep([oid]),
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

    # [ENTRY-MECHANICS P6b 07-17 — the DAY-KEY fix] a closed game files
    # under the day it DIED: settlement day where the settlements record
    # has it, else the day of its LAST fill (the terminal disposition) —
    # never the day its entry buy filled. The old key (any fill's day)
    # filed today's dead under yesterday (entry filled 07-16, settled
    # 07-17 → keyed 0716) and double-listed sold games on both days.
    # Banked past days stay frozen verbatim (the freeze scope untouched).
    _last_fill_day = {}   # ev -> max fill day across legs
    for tk_, mts_ in _q("SELECT ticker, MAX(ts) FROM fills "
                        "GROUP BY ticker"):
        _, ev_ = _ticker_pair_code(tk_)
        d_ = datetime.fromtimestamp(mts_, ET).strftime("%Y%m%d") \
            if mts_ else None
        if d_ and (ev_ not in _last_fill_day or d_ > _last_fill_day[ev_]):
            _last_fill_day[ev_] = d_
    _settle_day = {}      # ev -> max settlement day across legs
    try:
        for tk_, sd_ in _q("SELECT ticker, day FROM settlements"):
            _, ev_ = _ticker_pair_code(tk_)
            if sd_ and (ev_ not in _settle_day or sd_ > _settle_day[ev_]):
                _settle_day[ev_] = sd_
    except Exception:
        pass   # settlements table absent on an old DB — last-fill day governs
    day_tickers = sorted({r[0] for r in _q(
        "SELECT DISTINCT ticker FROM fills")})
    # [P2b, 07-17 — the BROBRA misfile] CLOSED excludes events with an
    # OPEN position (market active, result pending): a filled-today,
    # still-open game is a POSITION, not a closed card; it joins
    # CLOSED when it actually closes.
    _open_evs = {_ticker_pair_code(r[0])[1] for r in _q(
        "SELECT ticker FROM snap_positions "
        "WHERE ts=(SELECT MAX(ts) FROM snap_positions) AND qty > 0")}
    events = {}
    for tk in day_tickers:
        _, ev = _ticker_pair_code(tk)
        if ev in _open_evs:
            continue
        _death = _settle_day.get(ev) or _last_fill_day.get(ev)
        if _death != day:
            continue
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
            rows = _q("SELECT ts, action, yes_price_c, count_fp, "
                      "order_id FROM fills WHERE ticker=? ORDER BY ts",
                      (tk,))
            buys = [(ts, px, ct) for ts, a, px, ct, _o in rows
                    if a == "buy"]
            buy_oids = [_o for ts, a, px, ct, _o in rows if a == "buy"]
            sells = [(ts, px, ct) for ts, a, px, ct, _o in rows
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
            # W1 < sched · CORR in [sched, first point) · W2 >= first pt.
            # Without a sched anchor, only an OBSERVED first point can
            # place a fill (in W2); everything else is UNCLASSIFIABLE —
            # an EST bell alone is not window evidence.
            fill_window = None
            if buys:
                fts = buys[-1][0]
                sched_ep = win.get("sched_ep")
                fpd = win.get("fp") or {}
                fpts = fpd.get("ts")
                if sched_ep:
                    if fts < sched_ep:
                        fill_window = "W1"
                    elif fpts and fts >= fpts:
                        fill_window = "W2"
                    else:
                        fill_window = "CORR"
                elif fpd.get("observed") and fpts and fts >= fpts:
                    fill_window = "W2"
            # THE GRADE-EVIDENCE LAW (De Santis exhibit): a grade chip
            # prints only when the row shows its evidence — fill time,
            # a lawfully classified window, and (on W1 fills) a real Δ.
            # Missing evidence renders UNGRADED (gap filed), never a
            # letter.
            grade_note = None
            evidence_ok = bool(
                buys and fill_window in ("W1", "CORR", "W2")
                and win.get("state") == "ok"
                and (fill_window != "W1" or win.get("w1") is not None))
            if leg_grade and not evidence_ok:
                _file_miss("grade_without_evidence", tk)
                grade_note = ("UNGRADED (%s — filed)" % (
                    "no sched anchor" if not win.get("sched_ep")
                    else "tape gap" if win.get("w1_state") == "tape_gap"
                    else "no tape" if win.get("state") != "ok"
                    else "window unclassifiable"))
                leg_grade = None
            # RE-GRADE, same rubric both directions (C-OFFICIAL-BELL):
            # an F whose only charge was post-bell by a clock the
            # official record refutes is EXONERATED; a non-F on a fill
            # the official/observed clock places in W2 is CONVICTED FOR
            # REAL (the engine's stamp missed it).
            grade_was = None
            if (leg_grade and leg_grade.startswith("F")
                    and fill_window in ("W1", "CORR")):
                grade_was = leg_grade
                leg_grade = ("A" if (realized_c or 0) > 0 else
                             "B" if realized_c in (0, None) else "C")
            elif (leg_grade and not leg_grade.startswith("F")
                    and fill_window == "W2"):
                grade_was = leg_grade
                leg_grade = "F(W2)"
            if leg_grade:
                leg_grades.append(re.sub(r"\(.*\)", "", leg_grade))
            game_out["legs"].append({
                "ticker": tk,
                "last_name": leg_last_name(tk, sj),
                "ours_c": ours,
                "n_entry_fills": len(buys),
                "qty": bct,
                "filled_et": _hm(buys[-1][0]) if buys else None,
                "fill_ep": (buys[-1][0] if buys else None),
                # [4c] PLACED ET from the entry orders' created_time
                "placed_et": order_created_et(buy_oids),
                "placed_ep": order_created_ep(buy_oids),
                "fill_window": fill_window,
                "exit": ({"price_c": int(round(avg_sell)), "qty": sct,
                          "at": _hm(sells[-1][0]),
                          "ep": sells[-1][0]} if sct else None),
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
                "grade_note": grade_note,
                "grade_row": gr_row,
            })
        # ── PAIR LAW (grader amend, 07-16): the grade is per GAME,
        # never per leg. A requires BOTH legs W1; one-sided caps at C
        # (missing side honestly attempted) or D (never conceived /
        # pulled-and-abandoned); the sibling disposition line is
        # MANDATORY — absent = UNGRADED, filed.
        order = {"A": 0, "B": 1, "C": 2, "D": 3, "F": 4}
        filled = [l for l in game_out["legs"] if l["qty"]]
        filled_suffixes = {l["ticker"].rsplit("-", 1)[-1]
                           for l in filled}
        sib_line = None
        sib_cap = None
        missing = None
        if len(filled) >= 2:
            # pair already complete — no lookup needed for disposition
            kn = {"legs": {s: s for s in filled_suffixes}}
        else:
            kn = _kalshi_event_names(ev)
        if kn and len(kn.get("legs") or {}) >= 2:
            missing = [s for s in kn["legs"] if s not in filled_suffixes]
            if not missing:
                times = " → ".join(l["filled_et"] or "?"
                                   for l in game_out["legs"]
                                   if l["qty"])
                sib_line = "pair complete: both legs filled (%s)" % times
            else:
                parts = []
                for s in missing:
                    entry = kn["legs"][s]
                    nm = (entry.get("last") or entry.get("full")
                          if isinstance(entry, dict) else entry) or s
                    hist, cap = log_order_history(ev + "-" + s)
                    parts.append("%s — %s" % (nm.upper(), hist))
                    if sib_cap is None or order[cap] > order[sib_cap]:
                        sib_cap = cap
                sib_line = "sibling: " + " · ".join(parts)
        else:
            _file_miss("sibling_disposition_missing", ev)
        game_out["sibling_line"] = sib_line
        # [4a, 07-17 — THE SIBLING TAPE QUADRUPLET] every game box
        # carries BOTH legs x W1+CORR from the real tape: when a side
        # is unworked, its tape renders as a muted sibling row (the
        # window truth exists whether or not we bid it).
        game_out["pair_complete"] = (missing == [] if missing
                                     is not None else None)
        game_out["siblings"] = []
        if missing:
            for _sfx2 in missing:
                _stk2 = ev + "-" + _sfx2
                _en2 = (kn["legs"].get(_sfx2)
                        if isinstance(kn.get("legs"), dict) else None)
                _nm2 = ((_en2.get("last") or _en2.get("full"))
                        if isinstance(_en2, dict) else
                        (_en2 if isinstance(_en2, str) else _sfx2))
                game_out["siblings"].append(dict(
                    log_order_history_dict(_stk2),
                    ticker=_stk2, last_name=(_nm2 or _sfx2).upper(),
                    win=window_summary(_stk2, sj, ev)))
        game_out["sibling_tape"] = None
        if missing:
            _sfx = missing[0]
            _stk = ev + "-" + _sfx
            _entry = (kn["legs"].get(_sfx)
                      if isinstance(kn.get("legs"), dict) else None)
            _snm = ((_entry.get("last") or _entry.get("full"))
                    if isinstance(_entry, dict) else
                    (_entry if isinstance(_entry, str) else None))
            game_out["sibling_tape"] = {
                "ticker": _stk,
                "last_name": (_snm or _sfx).upper(),
                "win": window_summary(_stk, sj, ev)}
        any_ungraded_leg = any(l.get("grade_note")
                               for l in game_out["legs"])
        if sib_line is None:
            game_out["grade"] = None
            game_out["grade_status"] = "ungraded"
            game_out["footnote"] = ("UNGRADED (sibling disposition "
                                    "unresolvable — filed)")
        elif any_ungraded_leg or not leg_grades:
            game_out["grade"] = None
            game_out["grade_status"] = "ungraded"
        else:
            g = max(leg_grades, key=lambda x: order.get(x, 9))
            cap_note = None
            if missing:
                if order.get(sib_cap, 9) > order.get(g, 9):
                    cap_note = ("capped %s: one-sided (%s)"
                                % (sib_cap,
                                   "missing side honestly attempted"
                                   if sib_cap == "C" else
                                   "missing side abandoned or never "
                                   "conceived"))
                    g = sib_cap
            elif g == "A" and not (
                    len(filled) >= 2
                    and all(l.get("fill_window") == "W1"
                            for l in filled)):
                g = "B"
                cap_note = ("capped B: pair complete but not both legs "
                            "W1 (A requires both W1, sequenced)")
            game_out["grade"] = g
            game_out["grade_status"] = "graded"
            game_out["grade_cap_note"] = cap_note
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


def build_slate(day=None):
    """Slate-level counts for the dead-space strip above each tab
    (Plex 07-17, digit-grammar). Aggregation ONLY over the payload rows
    the three build_*() functions already emit — no new fetches. On the
    fixture harness the counts are read from fixtures[\"slate\"] if
    present, else computed the same way.

    Per-tab fields:
      games         # cards on the tab
      both_filled   # cards with 2+ filled legs (⇒ Σ foot eligible)
      red_slot      # cards with a missing side (⇒ red PAIR ✕)
      resting       # (CLOSED only) cards whose sibling has a bid but no
                    # fill — the operator's "resting" bucket in
                    # \"7 games · 2Σ · 3 (red) · 2 resting\"
    """
    if FIXTURE_PATH:
        fx = json.loads(Path(FIXTURE_PATH).read_text())
        if "slate" in fx:
            return fx["slate"]
    pos = build_positions()
    ords = build_orders()
    clsd = build_closed(day)

    pos_stats = {
        "games": len(pos),
        "both_filled": sum(
            1 for g in pos
            if len([l for l in (g.get("legs") or [])
                    if (l.get("qty") or 0) > 0]) >= 2),
        "red_slot": sum(
            1 for g in pos
            if len([l for l in (g.get("legs") or [])
                    if (l.get("qty") or 0) > 0]) < 2
            and g.get("gray_line") is not None),
    }
    ord_stats = {
        "games": len(ords),
        "red_slot": sum(1 for g in ords
                        if len(g.get("legs") or []) < 2),
    }
    cls_stats = {
        "games": len(clsd),
        "both_filled": sum(1 for g in clsd if g.get("pair_complete")),
        "red_slot": sum(
            1 for g in clsd
            if any(s.get("kind") == "never_bid"
                   for s in (g.get("siblings") or []))),
        "resting": sum(
            1 for g in clsd
            if any(s.get("kind") in ("held", "pulled")
                   for s in (g.get("siblings") or []))),
    }
    return {"positions": pos_stats, "orders": ord_stats,
            "closed": cls_stats}


# ── /api/tape/<ticker>.json — proof-on-click, REAL public tape ─────────


def bank_days():
    """[P1 day toggle] every banked closed day + today, newest first."""
    bank = ROOT / "state" / "daysheet_bank"
    days = set()
    if bank.exists():
        for f in bank.glob("closed_*.json"):
            d = f.stem.replace("closed_", "")
            if d.isdigit() and len(d) == 8:
                days.add(d)
    days.add(datetime.now(ET).strftime("%Y%m%d"))
    return sorted(days, reverse=True)


def build_alerts(limit=30):
    """[P4 ALERTS ON THE PANEL, operator 07-17: the render IS the alert
    surface; ntfy demoted to backup; the 07-14 phone decree struck]
    typed engine-log lines + fund flags, newest first, digits only.
    Tail-reads the newest log file (last ~3MB) per request."""
    # [P0v3 (5) 07-17 — EVERY DEFECT CLASS ON THE GLASS] the feed carries ALL
    # typed defect/violation lines: nothing detectable is invisible to the
    # operator. law_collision renders RED per the permanent protocol (P0v3 4);
    # window_truth_bind / phantom_bell_void are guard-working lines (amber).
    KINDS = ("pair_incomplete_violation",
             "below_discovery_floor_refused",
             "below_discovery_floor_retreat", "w2_fill_violation",
             "gun_feed_error", "gun_feed_ambiguous", "bell_missing",
             "floor_retreat_error", "window_truth_reaim",
             "law_collision", "window_truth_bind", "phantom_bell_void",
             "cancel_fill_race", "gun_fire_sweep_error",
             # [SAFETY-TEETH P3(a) 07-20] the naked tooth's three classes
             # — red by default (not in the amber set): the operator's
             # eyes found GNI at ~09:40; the tooth names it at ~09:29.
             "naked_leg_defect", "unbooked_fill_defect",
             "phantom_position_defect")
    out = []
    # [ENTRY-MECHANICS P2b+P5 07-17] the CHURN METER (reposts/leg over the
    # trailing hour; bar 6/hr — BURMER's 42 and the 40-53/leg/hr 07-17
    # sheet are the sizing exhibits) and the FV FRESHNESS METER (share of
    # trailing-hour placements priced without the sharp blend — metered at
    # the consumption site, fv_reason on v4_place) ride the same tail scan.
    _now_m = time.time()
    _churn = {}
    _fv_tot = _fv_stale = 0
    _fv_last_fresh = None
    try:
        logs = sorted(LOG_DIR.glob("live_v3_*.jsonl"))
        if logs:
            p = logs[-1]
            size = p.stat().st_size
            with open(p, "rb") as fh:
                if size > 3_000_000:
                    fh.seek(size - 3_000_000)
                    fh.readline()
                data = fh.read()
            for line in data.split(b"\n"):
                if b'"v4_move_repost"' in line or (b'"v4_place"' in line
                                                   and b'"fv' in line):
                    try:
                        jm = json.loads(line)
                        if (jm.get("ts_epoch") or 0) >= _now_m - 3600:
                            if jm.get("event") == "v4_move_repost":
                                _tkm = jm.get("ticker", "")
                                _churn[_tkm] = _churn.get(_tkm, 0) + 1
                            elif jm.get("event") == "v4_place":
                                _fv_tot += 1
                                if (jm.get("details") or {}).get(
                                        "fv_reason"):
                                    _fv_stale += 1
                                else:
                                    _fv_last_fresh = jm.get("ts_epoch")
                    except ValueError:
                        pass
                if not any(k.encode() in line for k in KINDS):
                    continue
                try:
                    j = json.loads(line)
                except ValueError:
                    continue
                e = j.get("event")
                if e not in KINDS:
                    continue
                d = j.get("details") or {}
                ev = (d.get("event") or j.get("ticker", "")
                      .rsplit("-", 1)[0]).split("-")[-1]
                if e == "below_discovery_floor_refused":
                    dig = "%s vol %s<%s" % (
                        ev, d.get("discovered_shares"),
                        int(d.get("floor") or 0))
                elif e == "below_discovery_floor_retreat":
                    dig = "%s vol %s · %d legs pulled" % (
                        ev, d.get("discovered_shares"),
                        len(d.get("legs") or []))
                elif e == "pair_incomplete_violation":
                    dig = "%s %s" % (ev,
                                     json.dumps(d.get("legs") or {}))
                elif e == "window_truth_reaim":
                    dig = "%s %s→%s (bb %s)" % (
                        ev, d.get("old"), d.get("new"),
                        d.get("best_bid"))
                elif e == "w2_fill_violation":
                    dig = "%s fill %s post-bell" % (ev,
                                                    d.get("fill_price"))
                elif e == "law_collision":
                    dig = "%s %s: %s=%s vs %s=%s" % (
                        ev, d.get("knob"), d.get("law_a"),
                        d.get("verdict_a"), d.get("law_b"),
                        d.get("verdict_b"))
                elif e == "window_truth_bind":
                    dig = "%s hold %s (bb %s, quote-only)" % (
                        ev, d.get("held_price"), d.get("best_bid"))
                elif e == "phantom_bell_void":
                    dig = "%s %s voided %smin pre-sched" % (
                        ev, d.get("source"), d.get("min_to_sched_min"))
                elif e == "cancel_fill_race":
                    dig = "%s %s filled %s in cancel window" % (
                        ev, d.get("label"), d.get("fill_price"))
                elif e == "naked_leg_defect":
                    dig = "%s NAKED %ssh no exit (cycle %s, %s)" % (
                        ev, d.get("held"), d.get("consecutive_cycles"),
                        "engine-known" if d.get("engine_known")
                        else "ORPHAN")
                elif e == "unbooked_fill_defect":
                    dig = "%s exch %s > booked %s (cycle %s)" % (
                        ev, d.get("exchange_qty"), d.get("engine_qty"),
                        d.get("consecutive_cycles"))
                elif e == "phantom_position_defect":
                    dig = "%s engine %ssh, exchange EMPTY (cycle %s)" % (
                        ev, d.get("engine_qty"),
                        d.get("consecutive_cycles"))
                else:
                    dig = "%s %s" % (ev, str(d)[:60])
                out.append({"ts": j.get("ts_epoch"),
                            "et": (_hm(j["ts_epoch"])
                                   if j.get("ts_epoch") else ""),
                            "kind": e, "digits": dig[:110],
                            "red": e not in ("window_truth_reaim",
                                             "window_truth_bind",
                                             "phantom_bell_void")})
        # churn meter rows (legs over the 6/hr bar, worst first)
        for _tkm, _n in sorted(_churn.items(), key=lambda x: -x[1])[:5]:
            if _n > 6:
                out.append({"ts": _now_m, "et": _hm(_now_m),
                            "kind": "churn_meter",
                            "digits": "%s %d reposts/hr (bar 6; P2 "
                                      "evidence-only law live)"
                                      % (_tkm.split("-")[-2][-8:] + "-"
                                         + _tkm.split("-")[-1], _n),
                            "red": True})
        # fv freshness meter row (only when the blend is degraded)
        if _fv_tot and _fv_stale * 2 >= _fv_tot:
            out.append({"ts": _now_m, "et": _hm(_now_m),
                        "kind": "fv_freshness",
                        "digits": "sharp blend STALE on %d/%d placements "
                                  "last hr%s" % (
                                      _fv_stale, _fv_tot,
                                      (" · last fresh %s"
                                       % _hm(_fv_last_fresh))
                                      if _fv_last_fresh else ""),
                        "red": False})
    except OSError:
        pass
    try:
        for ts, kind, tk, det in _q(
                "SELECT ts, kind, ticker, detail FROM flags "
                "WHERE ts > ? ORDER BY ts DESC LIMIT 10",
                (time.time() - 6 * 3600,)):
            out.append({"ts": ts, "et": _hm(ts),
                        "kind": "fund:" + kind,
                        "digits": "%s %s" % ((tk or "")[-12:],
                                             (det or "")[:80]),
                        "red": True})
    except Exception:
        pass
    out.sort(key=lambda x: -(x["ts"] or 0))
    return out[:limit]


def tape_age_seconds():
    """Age of OUR LAST PORTFOLIO FILL — lawfully grows for hours on a
    quiet book. NOT a feed-liveness signal (the 07-16 9:26 PM catch:
    8,846s here read as a dead feed when the recorder was 70s fresh
    and the book simply quiet). Render it as 'last fill', never as
    'tape'."""
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


def recorder_age_seconds():
    """The ACTUAL feed-liveness signal: age of the recorder's last
    equity heartbeat (written every poll cycle). >300s = the feed is
    genuinely stale and the panel must say so loudly."""
    if FIXTURE_PATH:
        return 30
    row = _q("SELECT MAX(ts) FROM equity")
    if not row or not row[0][0]:
        return None
    return time.time() - row[0][0]
