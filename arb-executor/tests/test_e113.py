"""[E113] Unit tests for the premarket movement-gate on _is_match_live.

Covers: FERCER flat-premarket-burst SUPPRESSED; premarket-with-movement fires;
TIAARN flat-LIVE backstop (tts<=0) fires; floor still blocks >30min-early; and
the binding fail-open case: a no-ref leg with a flat premarket burst does NOT
suppress (protection preserved when movement is unmeasurable).
"""
import importlib.util, pathlib, sys, time
_root = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))
_p = _root / "live_v4.py"
spec = importlib.util.spec_from_file_location("live_v4_e113mod", _p)
m = importlib.util.module_from_spec(spec); sys.modules["live_v4_e113mod"] = m
spec.loader.exec_module(m)
LiveV3, Book = m.LiveV3, m.Book


def _book(bid, ask):
    b = object.__new__(Book); b.best_bid, b.best_ask = bid, ask; b.last_trade_price = 0
    return b


def _bot():
    self = object.__new__(LiveV3)
    self._events_live = set(); self._live_stage1 = {}; self._live_skip_logged = set()
    self._trade_times = {}; self.event_tickers = {}; self.event_start_time = {}
    self._window_open = {}; self.books = {}; self.emits = []
    self._log = lambda ev, d, ticker=None: self.emits.append((ev, d, ticker))
    self._fv_burst_snapshot = lambda et, now: None   # stub the FV-patch call on latch
    return self


def _burst(self, et, legs, now, n=12):
    self.event_tickers[et] = set(legs)
    for tk in legs:
        self._trade_times[tk] = [now - 3 * i for i in range(n)]   # >=10 prints/60s


def test_e113_fercer_flat_premarket_suppressed():
    self = _bot(); now = time.time(); et = "E"; a, b = et + "-FER", et + "-CER"
    _burst(self, et, [a, b], now); self.event_start_time[et] = now + 1320  # tts=+22m premarket
    self._window_open[a] = {"price": 39}; self._window_open[b] = {"price": 61}
    self.books[a] = _book(38, 40); self.books[b] = _book(60, 62)            # FLAT vs ref
    assert self._is_match_live(et) is False
    assert et not in self._events_live and et not in self._live_stage1
    print("test_e113_fercer_flat_premarket_suppressed OK")


def test_e113_premarket_with_movement_fires():
    self = _bot(); now = time.time(); et = "E"; a, b = et + "-FER", et + "-CER"
    _burst(self, et, [a, b], now); self.event_start_time[et] = now + 600    # tts>0 premarket
    self._window_open[a] = {"price": 39}; self._window_open[b] = {"price": 61}
    self.books[a] = _book(46, 48); self.books[b] = _book(52, 54)            # FER 39->47 (>=7)
    self._live_stage1[et] = now - 70                                        # pre-arm -> confirm
    assert self._is_match_live(et) is True and et in self._events_live
    print("test_e113_premarket_with_movement_fires OK")


def test_e113_tiaarn_flat_live_backstop():
    self = _bot(); now = time.time(); et = "E"; a, b = et + "-TIA", et + "-ARN"
    _burst(self, et, [a, b], now); self.event_start_time[et] = now - 120    # tts<=0 POST-scheduled
    self._window_open[a] = {"price": 50}; self._window_open[b] = {"price": 50}
    self.books[a] = _book(50, 51); self.books[b] = _book(49, 50)            # FLAT-LIVE
    self._live_stage1[et] = now - 70
    assert self._is_match_live(et) is True                                  # backstop fires
    print("test_e113_tiaarn_flat_live_backstop OK")


def test_e113_floor_still_blocks():
    self = _bot(); now = time.time(); et = "E"; a, b = et + "-A", et + "-B"
    _burst(self, et, [a, b], now); self.event_start_time[et] = now + 3600   # tts=+60m > floor
    self._window_open[a] = {"price": 39}; self.books[a] = _book(46, 48)
    assert self._is_match_live(et) is False                                 # floor blocks pre-E113
    print("test_e113_floor_still_blocks OK")


def test_e113_noref_failopen():
    """BINDING: no window_open ref + flat premarket burst -> do NOT suppress
    (protection preserved when movement is unmeasurable)."""
    self = _bot(); now = time.time(); et = "E"; a, b = et + "-A", et + "-B"
    _burst(self, et, [a, b], now); self.event_start_time[et] = now + 600    # tts>0 premarket
    # NO window_open for either leg; books flat (irrelevant -- no ref to measure against)
    self.books[a] = _book(38, 40); self.books[b] = _book(60, 62)
    self._live_stage1[et] = now - 70                                        # pre-arm -> confirm
    assert self._is_match_live(et) is True and et in self._events_live      # FAIL OPEN -> latches
    print("test_e113_noref_failopen OK")


if __name__ == "__main__":
    test_e113_fercer_flat_premarket_suppressed()
    test_e113_premarket_with_movement_fires()
    test_e113_tiaarn_flat_live_backstop()
    test_e113_floor_still_blocks()
    test_e113_noref_failopen()
    print("\nALL E113 TESTS PASSED")
