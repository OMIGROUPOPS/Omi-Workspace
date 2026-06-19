"""[C-FV-BURST] Unit test for _fv_burst_snapshot (observe-only instrumentation).

Verifies: per-leg FV snapshot, entry_minus_fv_burst math (positive = entered ABOVE
FV), slice keys present, pre-burst filled vs resting tagging, solo/pair, age-prune,
idempotency, and empty-book (mid=None) handling. Pure: constructs the bot via
object.__new__ (no heavy __init__) and stubs _log to capture emits.
"""
import importlib.util, pathlib, sys

_root = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))   # so live_v4's own `import fv` etc. resolve
_p = _root / "live_v4.py"
spec = importlib.util.spec_from_file_location("live_v4_mod", _p)
m = importlib.util.module_from_spec(spec)
sys.modules["live_v4_mod"] = m
spec.loader.exec_module(m)
LiveV3, Book, Position = m.LiveV3, m.Book, m.Position


def _book(bid, ask, last=0):
    b = object.__new__(Book)
    b.best_bid, b.best_ask, b.last_trade_price = bid, ask, last
    return b


def _pos(entry_price, target_price, filled_ts, cat="ATP_MAIN", cell="ATP_MAIN_underdog_25-29",
         regime="r25_34", ref="engagement"):
    p = object.__new__(Position)
    p.entry_price, p.target_price = entry_price, target_price
    p.entry_filled_ts = filled_ts
    p.category, p.cell_name, p.regime_at_posting, p.reference_source = cat, cell, regime, ref
    return p


def _bot():
    self = object.__new__(LiveV3)
    self._fv_burst = {}
    self.event_tickers = {}
    self.positions = {}
    self.books = {}
    self._trade_times = {}
    self.event_start_time = {}
    self._fv_burst_done = set()
    self.emits = []
    self._log = lambda ev, d, ticker=None: self.emits.append((ev, d, ticker))
    return self


def test_fv_burst_ready():
    self = _bot()
    et = "E"; a, b = et + "-AAA", et + "-BBB"
    self.event_tickers[et] = {a, b}
    now = 10000.0
    # 12 trade prints across legs within last 60s -> recent>=10
    self._trade_times[a] = [now - 5*i for i in range(7)]   # 7 in window
    self._trade_times[b] = [now - 4*i for i in range(6)]   # 6 in window  => 13 total
    self.event_start_time[et] = now - 60          # tts = -60 (past start, floor passes)
    assert self._fv_burst_ready(et, now) is True, "burst>=10 + past start -> True"
    # tts > floor (premarket) -> False even with burst
    self.event_start_time[et] = now + m.LIVE_DETECT_TTS_FLOOR_SEC + 100
    assert self._fv_burst_ready(et, now) is False, "tts>floor -> False"
    # no start time -> floor cannot apply -> True
    self.event_start_time.pop(et)
    assert self._fv_burst_ready(et, now) is True, "tts None -> floor n/a -> True"
    # sub-threshold -> False
    self._trade_times[a] = [now - 1, now - 2]; self._trade_times[b] = [now - 3]
    assert self._fv_burst_ready(et, now) is False, "recent<10 -> False"
    # stale prints (outside 60s window) -> False
    self._trade_times[a] = [now - 100 - i for i in range(20)]; self._trade_times[b] = []
    assert self._fv_burst_ready(et, now) is False, "all stale -> False"
    print("test_fv_burst_ready OK")


def test_regate_both_filled_emits():
    """The re-gate's purpose: a both-filled event with NO resting bid emits via the
    routing-sweep observe block (ready -> snapshot -> done)."""
    self = _bot()
    et = "KXATPMATCH-26JUN19TIAAUG"; a, b = et + "-AUG", et + "-TIA"
    self.event_tickers[et] = {a, b}
    now = 5000.0
    self._trade_times[a] = [now - 3*i for i in range(8)]   # burst
    self._trade_times[b] = [now - 3*i for i in range(8)]
    self.event_start_time[et] = now - 120                  # live
    self.books[a] = _book(60, 62); self.books[b] = _book(38, 40)
    self.positions[a] = _pos(61, 61, 999.0)               # both FILLED, no resting bid
    self.positions[b] = _pos(39, 39, 999.0)
    # simulate the Hunk C routing-sweep block
    tickers = self.event_tickers[et]
    if et not in self._fv_burst_done and any(t in self.positions for t in tickers):
        if self._fv_burst_ready(et, now):
            self._fv_burst_snapshot(et, now)
            self._fv_burst_done.add(et)
    emits = {t: d for (ev, d, t) in self.emits if ev == "fv_burst_anchor"}
    assert set(emits) == {a, b}, "both-filled event emits for BOTH legs"
    assert et in self._fv_burst_done, "fire-once marked"
    assert emits[a]["entry_minus_fv_burst"] == 61 - 61.0
    assert emits[b]["entry_minus_fv_burst"] == 39 - 39.0
    print("test_regate_both_filled_emits OK")


def test_pre_burst_tag_and_math():
    self = _bot()
    et = "KXATPMATCH-26JUN19FERCER"
    tk_f, tk_r = et + "-CER", et + "-FER"
    self.event_tickers[et] = {tk_f, tk_r}
    # filled leg: bought @61, book now 60/62 -> mid 61.0 ; resting leg @38, book 39/41 -> mid 40.0
    self.books[tk_f] = _book(60, 62, 61)
    self.books[tk_r] = _book(39, 41, 0)
    self.positions[tk_f] = _pos(61, 61, 12345.0, cat="ATP_MAIN", cell="cF", regime="r55_64", ref="engagement")
    self.positions[tk_r] = _pos(0, 38, 0.0, cat="ATP_MAIN", cell="cR", regime="r35_44", ref="engagement")

    self._fv_burst_snapshot(et, now=1000.0)

    # both legs snapshotted
    assert set(self._fv_burst) == {tk_f, tk_r}
    assert self._fv_burst[tk_f]["mid"] == 61.0
    assert self._fv_burst[tk_r]["mid"] == 40.0
    emits = {t: d for (ev, d, t) in self.emits if ev == "fv_burst_anchor"}
    assert len(emits) == 2
    # filled leg: entry_minus_fv = 61 - 61 = 0 ; filled_pre_burst True
    f = emits[tk_f]
    assert f["filled_pre_burst"] is True and f["entry_price"] == 61 and f["fill_price"] == 61
    assert f["entry_minus_fv_burst"] == 0.0
    # resting leg: entry_price = target 38, entry_minus_fv = 38 - 40 = -2 (DISCOUNT) ; not filled
    r = emits[tk_r]
    assert r["filled_pre_burst"] is False and r["entry_price"] == 38 and r["fill_price"] is None
    assert r["entry_minus_fv_burst"] == -2.0
    # solo/pair: only 1 leg filled -> "solo"
    assert f["solo_or_pair"] == "solo" and r["solo_or_pair"] == "solo"
    # slice keys present
    for d in (f, r):
        for k in ("cat", "cell", "regime", "reference_source", "fv_mid", "fv_bid", "fv_ask", "fv_last"):
            assert k in d
    print("test_pre_burst_tag_and_math OK")


def test_above_fv_positive_and_pair():
    self = _bot()
    et = "E2"
    a, b = et + "-AAA", et + "-BBB"
    self.event_tickers[et] = {a, b}
    self.books[a] = _book(80, 82)   # mid 81
    self.books[b] = _book(18, 20)   # mid 19
    self.positions[a] = _pos(85, 85, 1.0)  # filled @85, FV 81 -> +4 ABOVE FV
    self.positions[b] = _pos(16, 16, 1.0)  # filled @16, FV 19 -> -3 DISCOUNT
    self._fv_burst_snapshot(et, now=500.0)
    emits = {t: d for (ev, d, t) in self.emits if ev == "fv_burst_anchor"}
    assert emits[a]["entry_minus_fv_burst"] == 4.0   # positive = entered ABOVE FV
    assert emits[b]["entry_minus_fv_burst"] == -3.0
    assert emits[a]["solo_or_pair"] == "pair"        # both filled
    print("test_above_fv_positive_and_pair OK")


def test_idempotent_relatch():
    self = _bot()
    et = "E3"; tk = et + "-X"
    self.event_tickers[et] = {tk}
    self.books[tk] = _book(50, 51)
    self.positions[tk] = _pos(49, 49, 1.0)
    self._fv_burst_snapshot(et, now=100.0)
    n1 = len(self.emits)
    self._fv_burst_snapshot(et, now=200.0)   # re-latch: tk already snapped -> no re-emit
    assert len(self.emits) == n1
    assert self._fv_burst[tk]["ts"] == 100.0  # keeps FIRST anchor
    print("test_idempotent_relatch OK")


def test_age_prune():
    self = _bot()
    self._fv_burst["OLD-X"] = {"mid": 50, "bid": 50, "ask": 51, "last": 0,
                               "ts": 1000.0 - m.FV_BURST_RETENTION_SEC - 10}
    et = "E4"; tk = et + "-Y"
    self.event_tickers[et] = {tk}
    self.books[tk] = _book(30, 31)
    self.positions[tk] = _pos(29, 29, 1.0)
    self._fv_burst_snapshot(et, now=1000.0)
    assert "OLD-X" not in self._fv_burst   # stale pruned
    assert tk in self._fv_burst
    print("test_age_prune OK")


def test_empty_book_mid_none():
    self = _bot()
    et = "E5"; tk = et + "-Z"
    self.event_tickers[et] = {tk}
    self.books[tk] = _book(0, 100)   # empty book
    self.positions[tk] = _pos(40, 40, 1.0)
    self._fv_burst_snapshot(et, now=1.0)
    assert self._fv_burst[tk]["mid"] is None
    emits = {t: d for (ev, d, t) in self.emits if ev == "fv_burst_anchor"}
    assert emits[tk]["entry_minus_fv_burst"] is None  # math skipped when mid None
    print("test_empty_book_mid_none OK")


if __name__ == "__main__":
    test_fv_burst_ready()
    test_regate_both_filled_emits()
    test_pre_burst_tag_and_math()
    test_above_fv_positive_and_pair()
    test_idempotent_relatch()
    test_age_prune()
    test_empty_book_mid_none()
    print("\nALL FV-BURST TESTS PASSED")
