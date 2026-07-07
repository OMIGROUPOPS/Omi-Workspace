import py_compile
P = r"C:\Users\omigr\OMI-Workspace\arb-executor\live_v4.py"
s = open(P, encoding="utf-8").read()

# 1. flag init
s = s.replace("""        self.aim_shadow = bool(self.config.get("aim_shadow", False))
        self._aim_shadow_tbl = None""",
"""        self.aim_shadow = bool(self.config.get("aim_shadow", False))
        self._aim_shadow_tbl = None
        # [C-EXPRESSION-INVARIANT, PLEX ruling: join/improve ratified vs the NON-SELF
        # chain; default OFF = byte-identical. Arm waits on the recount + shadow nights
        # + the four-bar gate. The never-marketable clamp is ARMED (unconditional per
        # the same ruling) at the maker chokepoint in place_order.]
        self.expression_invariant = bool(self.config.get("expression_invariant", False))""")

# 2. root helper + express helper
s = s.replace("    def _join_trial_resolve(self, pos, outcome, book, price, tk):",
'''    def _book_ex_self(self, tk):
        """[C-EX-SELF root] (best_bid_ex_self, best_ask): the live book NET of our own
        resting entry order on tk (positions registry: phase entry_resting carries the
        px; our size empties a level -> fall through to the next real level). Bids only;
        asks untouched (we rest bids only). PURE read; None-safe."""
        b = self.books.get(tk)
        if b is None:
            return None, None
        ask = int(b.best_ask) if getattr(b, "best_ask", 0) else None
        own_px = None
        pos = self.positions.get(tk)
        if (pos is not None and getattr(pos, "phase", "") == "entry_resting"
                and getattr(pos, "entry_order_id", "") and (pos.entry_price or 0) > 0):
            own_px = int(round(pos.entry_price))
        try:
            levels = sorted(((int(p), float(sz)) for p, sz in (b.bids or {}).items()
                             if sz and int(p) > 0), reverse=True)
        except Exception:
            return (int(b.best_bid) if getattr(b, "best_bid", 0) else None), ask
        for px, sz in levels:
            adj = sz - (float(self.entry_size) if own_px == px else 0.0)
            if adj > 0.01:
                return px, ask
        return None, ask

    def _express_target(self, tk, target, site=""):
        """[C-EXPRESSION-INVARIANT, gated default-OFF] express a buy target vs the
        NON-SELF chain: rest AT target when target <= bid_ex_self; a target above the
        chain joins it or improves by EXACTLY 1c -- expressed = min(target, bid_ex+1).
        A walk step above bid_ex_self+1 is structurally impossible with the flag on
        (every step joins/improves the MARKET's chain, never our own reflection).
        Composes with the walk cap: invariant = step law, cap = journey bound."""
        if not getattr(self, "expression_invariant", False) or target is None:
            return target
        try:
            bx, _ = self._book_ex_self(tk)
            if bx is None or target <= bx + 1:
                return target
            self._log("expression_clamped", {"from": int(target), "to": bx + 1,
                                             "bid_ex_self": bx, "site": site}, ticker=tk)
            return bx + 1
        except Exception:
            return target

    def _join_trial_resolve(self, pos, outcome, book, price, tk):''')

# 3. NEVER-MARKETABLE armed clamp
s = s.replace('''        """Place a real order on Kalshi. Returns (order_id, response_dict) or ("", error_dict)."""
        # Position accumulation guard: cap total buy exposure per ticker
        if action == "buy":''',
'''        """Place a real order on Kalshi. Returns (order_id, response_dict) or ("", error_dict)."""
        # [C-NEVER-MARKETABLE, ARMED unconditional per the Plex expression ruling]
        # no MAKER buy may post at >= best_ask -- enforced at the single chokepoint
        # every placement site flows through. post_only=False (the deliberate taker
        # paths: complete_cross <=100, gated marketable_taker) bypasses BY DESIGN --
        # "post" means maker intent.
        if action == "buy" and post_only:
            _bk = self.books.get(ticker)
            _ask = int(_bk.best_ask) if (_bk and getattr(_bk, "best_ask", 0)) else None
            if _ask and price >= _ask:
                self._log("never_marketable_clamped", {
                    "from": int(price), "to": max(1, _ask - 1), "best_ask": _ask}, ticker=ticker)
                price = max(1, _ask - 1)
        # Position accumulation guard: cap total buy exposure per ticker
        if action == "buy":''')

# 4. invariant call sites
s = s.replace("""                # [C-JOIN-TRIAL] pre-registered abort halts NEW join entries once tripped.
                if self.join_trial_aborted and reference_source == "join_bid":""",
"""                # [C-EXPRESSION-INVARIANT] gated; default OFF = byte-identical
                target_bid = self._express_target(tk, target_bid, "fresh")
                # [C-JOIN-TRIAL] pre-registered abort halts NEW join entries once tripped.
                if self.join_trial_aborted and reference_source == "join_bid":""")
s = s.replace("""        # Fix-3 (reprice-maker-only): NEVER cross on a reprice. A marketable re-evaluated
        # target is clamped to a resting bid one below the ask and re-rested as a maker.
        new_target, po = self._reprice_target(new_target, current_ask)""",
"""        # [C-EXPRESSION-INVARIANT] gated; the walk step joins/improves the MARKET's chain
        new_target = self._express_target(tk, new_target, "walk")
        # Fix-3 (reprice-maker-only): NEVER cross on a reprice. A marketable re-evaluated
        # target is clamped to a resting bid one below the ask and re-rested as a maker.
        new_target, po = self._reprice_target(new_target, current_ask)""")
s = s.replace("""                _ask = int(sb.best_ask) if (sb and sb.best_ask) else 100
                price, po = self._reprice_target(level, _ask)""",
"""                level = self._express_target(sib, level, "sibling_repost")
                _ask = int(sb.best_ask) if (sb and sb.best_ask) else 100
                price, po = self._reprice_target(level, _ask)""")

# 5. shadow honesty: dual posture
s = s.replace('''            _ob = self.books.get(tk)
            _obb = getattr(_ob, "best_bid", None) if _ob else None
            _oba = getattr(_ob, "best_ask", None) if _ob else None
            def _posture(lvl):
                if lvl is None or not _obb: return None
                if lvl < _obb: return "below_chain"
                if lvl == _obb: return "join"
                if lvl == _obb + 1: return "improve1"
                if _oba and lvl >= _oba: return "marketable"
                return "mid_spread"''',
'''            _ob = self.books.get(tk)
            _obb = getattr(_ob, "best_bid", None) if _ob else None
            _oba = getattr(_ob, "best_ask", None) if _ob else None
            _bx, _ = self._book_ex_self(tk)   # [C-EX-SELF] the market's chain, not our mirror
            def _mk_posture(ref_bid):
                def _p(lvl):
                    if lvl is None or not ref_bid: return None
                    if lvl < ref_bid: return "below_chain"
                    if lvl == ref_bid: return "join"
                    if lvl == ref_bid + 1: return "improve1"
                    if _oba and lvl >= _oba: return "marketable"
                    return "mid_spread"
                return _p
            _posture = _mk_posture(_obb)          # raw (transition dual-logging)
            _posture_x = _mk_posture(_bx)         # ex-self''')
s = s.replace('''                    "book_spread": (_oba - _obb) if (_obb and _oba) else None,
                    "actual_posture": _posture(actual_bid)}''',
'''                    "book_spread": (_oba - _obb) if (_obb and _oba) else None,
                    "bid_ex_self": _bx,
                    "actual_posture": _posture(actual_bid),
                    "actual_posture_ex_self": _posture_x(actual_bid)}''')
s = s.replace('''                             "shadow_posture25": _posture(max(1, px + _d25) if _d25 is not None else None),
                             "shadow_posture50": _posture(max(1, px + _d50) if _d50 is not None else None),''',
'''                             "shadow_posture25": _posture(max(1, px + _d25) if _d25 is not None else None),
                             "shadow_posture50": _posture(max(1, px + _d50) if _d50 is not None else None),
                             "shadow_posture50_ex_self": _posture_x(max(1, px + _d50) if _d50 is not None else None),''')

open(P, "w", encoding="utf-8").write(s)
py_compile.compile(P, doraise=True)
print("all five pieces in; compiles")
