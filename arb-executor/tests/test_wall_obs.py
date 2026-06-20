"""[WALL-OBS] Unit tests for _wall_observe (would_skip_walled_post observe-log).

Covers: emits once on a >1000 wall with right fields + fire-once; thin book
(<bar) emits none; sell (exit) emits none (entry-only); 1-wide book reports
jump_available=False.
"""
import importlib.util, pathlib, sys
_root = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))
_p = _root / "live_v4.py"
spec = importlib.util.spec_from_file_location("live_v4_wallmod", _p)
m = importlib.util.module_from_spec(spec); sys.modules["live_v4_wallmod"] = m
spec.loader.exec_module(m)
LiveV3, Book, Position = m.LiveV3, m.Book, m.Position


def _book(bid, ask, bids=None):
    b = object.__new__(Book)
    b.best_bid, b.best_ask, b.last_trade_price = bid, ask, 0
    b.bids = dict(bids or {})
    return b


def _pos(cell="C", pt="v4_engagement_join"):
    p = object.__new__(Position)
    p.cell_name, p.play_type = cell, pt
    return p


def _bot():
    self = object.__new__(LiveV3)
    self.books = {}; self.positions = {}; self.ticker_to_event = {}
    self.emits = []
    self._log = lambda ev, d, ticker=None: self.emits.append((ev, d, ticker))
    return self


def _wse(self):
    return [d for ev, d, t in self.emits if ev == "would_skip_walled_post"]


def test_wall_obs_emits():
    self = _bot(); tk = "KXATPMATCH-26JUN19ALTMED-ALT"
    self.books[tk] = _book(38, 40, {38: 1500})           # wall 1500 > 1000, spread 2
    self.ticker_to_event[tk] = tk.rsplit("-", 1)[0]
    self.positions[tk] = _pos("ALT_cell", "v4_fallback_maker")
    self._wall_observe(tk, "buy", 38, 5)
    em = _wse(self)
    assert len(em) == 1, "exactly one walled-post log"
    d = em[0]
    assert d["depth_at_price"] == 1500 and d["our_size"] == 5 and d["price"] == 38
    assert d["spread"] == 2 and d["jump_available"] is True
    assert d["event"] == tk.rsplit("-", 1)[0] and d["play_type"] == "v4_fallback_maker" and d["cell"] == "ALT_cell"
    self._wall_observe(tk, "buy", 38, 5)                 # fire-once
    assert len(_wse(self)) == 1, "fire-once per leg"
    print("test_wall_obs_emits OK")


def test_wall_obs_thin_no_emit():
    self = _bot(); tk = "E-A"
    self.books[tk] = _book(38, 40, {38: 50})             # 50 < 1000
    self._wall_observe(tk, "buy", 38, 5)
    assert _wse(self) == []
    print("test_wall_obs_thin_no_emit OK")


def test_wall_obs_sell_no_emit():
    self = _bot(); tk = "E-A"
    self.books[tk] = _book(38, 40, {38: 1500})           # walled but it's a SELL (exit)
    self._wall_observe(tk, "sell", 38, 5)
    assert _wse(self) == []
    print("test_wall_obs_sell_no_emit OK")


def test_wall_obs_1wide_jump_unavailable():
    self = _bot(); tk = "E-A"
    self.books[tk] = _book(38, 39, {38: 1500})           # spread 1 -> jump would cross
    self.ticker_to_event[tk] = "E"
    self._wall_observe(tk, "buy", 38, 5)
    d = _wse(self)[0]
    assert d["spread"] == 1 and d["jump_available"] is False
    print("test_wall_obs_1wide_jump_unavailable OK")


if __name__ == "__main__":
    test_wall_obs_emits()
    test_wall_obs_thin_no_emit()
    test_wall_obs_sell_no_emit()
    test_wall_obs_1wide_jump_unavailable()
    print("\nALL WALL-OBS TESTS PASSED")
