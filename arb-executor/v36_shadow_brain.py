"""No-order V36 shadow brain for the Stage-C migration-doctrine lane.

The authoritative policy is the byte-frozen JS package at ``POLICY_COMMIT``.
This port owns hypothetical state only; its constructor receives a log emitter,
not an exchange/session/order object.  Tests exhaustively compare the pure
decision seam to the frozen JS implementation.
"""

from collections import defaultdict, deque
from dataclasses import dataclass, field


POLICY_COMMIT = "bfde0d8d1135f5c5f48a5f3d619ab30050efab83"
LOOKBACK_SECONDS = 300.0
PRESSURE_RISING_MIN = 0.60
PRESSURE_FALLING_MAX = 0.40
QUALIFIED_SPREAD_MAX_CENTS = 1
QUALIFIED_DWELL_MIN_SECONDS = 10.0
QUALIFIED_SIZE_MIN = 5


def _cent(value):
    return isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 99


def pressure_state(depth_ratio):
    if depth_ratio >= PRESSURE_RISING_MIN:
        return "RISING"
    if depth_ratio <= PRESSURE_FALLING_MAX:
        return "FALLING"
    return "SETTLED"


def combine_state(quote_state, pressure):
    valid = ("FALLING", "RISING", "SETTLED")
    if quote_state not in valid or pressure not in valid:
        raise ValueError("valid state required")
    return {
        "state": pressure if quote_state == "SETTLED" else quote_state,
        "quote_state": quote_state,
        "pressure_state": pressure,
        "disagreement": quote_state != "SETTLED" and pressure != "SETTLED" and quote_state != pressure,
        "authority": "JUL6_DEPTH_PRESSURE" if quote_state == "SETTLED" else "TRAILING_300S_QUOTE_PATH_PRIMARY",
    }


def state_directional_rest_target(state, bid, active_target=None, pair_cap=None):
    target = bid - 1
    if state == "FALLING" and _cent(active_target):
        target = min(target, active_target)
    if isinstance(pair_cap, int) and not isinstance(pair_cap, bool):
        target = min(target, pair_cap)
    return target if _cent(target) else None


def displayed_ask_has_evidence_capacity(book):
    return (isinstance(book.get("bid"), int) and isinstance(book.get("ask"), int)
            and float(book.get("ask_dwell_seconds", -1)) >= QUALIFIED_DWELL_MIN_SECONDS
            and float(book.get("top_ask_size", -1)) >= QUALIFIED_SIZE_MIN)


def qualifying_ask_evidence(book):
    if not displayed_ask_has_evidence_capacity(book):
        return False
    return book["bid"] >= book["ask"] or (
        isinstance(book.get("spread"), int) and 0 <= book["spread"] <= QUALIFIED_SPREAD_MAX_CENTS)


def evidence_take_permission(book, pair_cap, active_floor, first_flicker):
    if not displayed_ask_has_evidence_capacity(book):
        return {"permitted": False, "reason": "DISPLAYED_ASK_NOT_DWELL_AND_FIVE_LOT_QUALIFIED"}
    if isinstance(pair_cap, int) and book["ask"] > pair_cap:
        return {"permitted": False, "reason": "DISPLAYED_ASK_ABOVE_PAIR_CAP"}
    if not _cent(active_floor):
        return {"permitted": False, "reason": "NO_ACTIVE_DISCOUNT_EVIDENCE_FLOOR"}
    if book["ask"] > active_floor:
        return {"permitted": False, "reason": "UNABSORBED_DOWNWARD_EVIDENCE_ASK_ABOVE_FLOOR"}
    if first_flicker:
        return {"permitted": False, "reason": "CURRENT_ASK_CREATED_FLOOR_WHILE_DOWNWARD_SEQUENCE_UNABSORBED"}
    return {"permitted": True, "reason": "ASK_AT_OR_BELOW_ACTIVE_EVIDENCE_FLOOR"}


def v36_decide(state, book, active_target=None, pair_cap=None,
               active_evidence_floor=None, floor_first_flicker_live=False,
               floor_mature=False):
    if state not in ("FALLING", "RISING", "SETTLED"):
        raise ValueError("valid state required")
    rest = state_directional_rest_target(state, book["bid"], active_target, pair_cap)
    if active_target is None:
        return {"action": "HOLD_REST" if rest is None else "PLACE_REST",
                "target_cents": rest,
                "reason": "NO_LAWFUL_ONE_CENT_UNDER_BID_TARGET" if rest is None else
                          "FIRST_TWO_SIDED_BOOK_FALLING_NO_CHASE_REST_ONE_CENT_UNDER_BID" if state == "FALLING" else
                          "FIRST_TWO_SIDED_BOOK_LIVING_REST_ONE_CENT_UNDER_BID",
                "take_permission": None}
    take = evidence_take_permission(book, pair_cap, active_evidence_floor,
                                    floor_first_flicker_live)
    if take["permitted"] and not floor_mature:
        take = {"permitted": False,
                "reason": "ACTIVE_EVIDENCE_FLOOR_NOT_MATURE_NEW_LOW_INSIDE_TRAILING_HORIZON"}
    elif take["permitted"]:
        take = {"permitted": True,
                "reason": "MATURE_EVIDENCE_FLOOR_NO_NEW_LOW_INSIDE_TRAILING_HORIZON"}
    if take["permitted"]:
        return {"action": "TAKE", "target_cents": book["ask"],
                "reason": "MATURE_EVIDENCE_FLOOR_TAKE", "take_permission": take}
    if rest is None:
        return {"action": "CANCEL_REST", "target_cents": None,
                "reason": "NO_LAWFUL_ONE_CENT_UNDER_BID_OR_PAIR_CAP_LEVEL",
                "take_permission": take}
    if rest != active_target:
        return {"action": "REPRICE_REST", "target_cents": rest,
                "direction": "UP" if rest > active_target else "DOWN",
                "reason": "FALLING_REST_ONE_CENT_UNDER_BEST_BID_NO_UPWARD_CHASE" if state == "FALLING" else
                          "LIVING_REST_REANCHOR_EVERY_BOOK_RECEIPT",
                "take_permission": take}
    return {"action": "HOLD_REST", "target_cents": active_target,
            "reason": take["reason"], "take_permission": take}


@dataclass
class _Evidence:
    ts: float
    ordinal: int
    direction: str
    kind: str
    receipt: str


@dataclass
class _Leg:
    previous_bid: int = None
    previous_ask: int = None
    ask_since: float = None
    ordinal: int = 0
    evidence: deque = field(default_factory=deque)
    active_target: int = None
    target_action_ts: float = None
    seller_low: int = None
    ask_low: int = None
    latest_downward_ts: float = None
    latest_downward_receipt: str = None
    fill_price: int = None
    fill_ts: float = None


class V36ShadowBrain:
    """Receipt-driven hypothetical brain with no exchange mutation surface."""

    def __init__(self, emit):
        self._emit = emit
        self._legs = defaultdict(_Leg)
        self._fills = defaultdict(dict)

    @staticmethod
    def _event(ticker, event_ticker):
        return event_ticker or (ticker.rsplit("-", 1)[0] if "-" in ticker else ticker)

    @staticmethod
    def _ratio(bids, asks):
        b = sum(max(0, int(size)) for _, size in list(bids)[:5])
        a = sum(max(0, int(size)) for _, size in list(asks)[:5])
        return b / (a + b) if a + b else 0.5

    def _add(self, leg, ts, direction, kind, receipt):
        leg.ordinal += 1
        leg.evidence.append(_Evidence(ts, leg.ordinal, direction, kind, receipt))
        while leg.evidence and leg.evidence[0].ts < ts - LOOKBACK_SECONDS:
            leg.evidence.popleft()

    @staticmethod
    def _quote(leg, ts):
        live = [x for x in leg.evidence if ts - LOOKBACK_SECONDS <= x.ts <= ts]
        if not live:
            return "SETTLED", None
        row = max(live, key=lambda x: (x.ts, x.ordinal))
        return row.direction, row

    def _cap(self, event, ticker):
        for other, price in self._fills[event].items():
            if other != ticker:
                return 99 - price
        return None

    def _fill(self, event, ticker, leg, price, ts, fill_class, receipt):
        if leg.fill_price is not None:
            return
        leg.fill_price, leg.fill_ts = price, ts
        self._fills[event][ticker] = price
        self._emit("v36_shadow_fill", {
            "policy_commit": POLICY_COMMIT, "shadow_only": True,
            "no_order_authority": True, "event_ticker": event,
            "fill_price_cents": price, "fill_class": fill_class,
            "receipt": receipt, "pair_cap_armed_for_sibling_cents": 99 - price,
        }, ticker)

    def on_trade(self, ticker, event_ticker, ts, price, size, taker_side, receipt):
        event, leg = self._event(ticker, event_ticker), self._legs[ticker]
        direction = "FALLING" if taker_side == "no" else "RISING" if taker_side == "yes" else "SETTLED"
        kind = "SELLER_AGGRESSED_PRINT" if taker_side == "no" else "BUYER_AGGRESSED_PRINT" if taker_side == "yes" else "UNSIDED_PRINT"
        self._add(leg, ts, direction, kind, receipt)
        if taker_side == "no":
            leg.seller_low = price if leg.seller_low is None else min(leg.seller_low, price)
            leg.latest_downward_ts, leg.latest_downward_receipt = ts, receipt
            if (leg.fill_price is None and _cent(leg.active_target)
                    and leg.target_action_ts is not None and ts > leg.target_action_ts
                    and size >= QUALIFIED_SIZE_MIN and price <= leg.active_target):
                self._fill(event, ticker, leg, leg.active_target, ts,
                           "PROVEN_MAKER_SELLER_AGGRESSED_PRINT_SIZE_FIVE_AT_OR_BELOW_REST", receipt)

    def on_book(self, ticker, event_ticker, ts, bid_levels, ask_levels, receipt):
        if not bid_levels or not ask_levels:
            return None
        event, leg = self._event(ticker, event_ticker), self._legs[ticker]
        if leg.fill_price is not None:
            return None
        bid, _ = max(bid_levels, key=lambda x: x[0])
        ask, ask_size = min(ask_levels, key=lambda x: x[0])
        bid, ask, ask_size = int(bid), int(ask), int(ask_size)
        if not _cent(bid) or not _cent(ask):
            return None
        if leg.previous_ask != ask:
            leg.ask_since = ts
        dwell = max(0.0, ts - (leg.ask_since if leg.ask_since is not None else ts))
        falling = leg.previous_ask is not None and ask < leg.previous_ask
        rising = leg.previous_bid is not None and bid > leg.previous_bid
        if falling and rising:
            self._add(leg, ts, "SETTLED", "SIMULTANEOUS_NEW_LOW_ASK_AND_NEW_HIGH_BID", receipt)
        elif falling:
            self._add(leg, ts, "FALLING", "NEW_LOW_ASK", receipt)
            leg.latest_downward_ts, leg.latest_downward_receipt = ts, receipt
        elif rising:
            self._add(leg, ts, "RISING", "NEW_HIGH_BID", receipt)
        book = {"bid": bid, "ask": ask, "spread": ask - bid,
                "ask_dwell_seconds": dwell, "top_ask_size": ask_size}
        local_floor = ask if qualifying_ask_evidence(book) else None
        old_ask_low = leg.ask_low
        if local_floor is not None:
            leg.ask_low = local_floor if old_ask_low is None else min(old_ask_low, local_floor)
            if old_ask_low is None or local_floor < old_ask_low:
                leg.latest_downward_ts, leg.latest_downward_receipt = ts, receipt
        quote, state_receipt = self._quote(leg, ts)
        ratio = self._ratio(sorted(bid_levels, reverse=True), sorted(ask_levels))
        combined = combine_state(quote, pressure_state(ratio))
        state = combined["state"]
        mature = leg.latest_downward_ts is None or ts - leg.latest_downward_ts >= LOOKBACK_SECONDS
        if state == "FALLING":
            floors = [p for p in (leg.seller_low, leg.ask_low) if _cent(p)]
            active_floor = min(floors) if floors else None
        elif local_floor is not None:
            active_floor = local_floor
        elif mature and leg.ask_low is not None:
            active_floor = leg.ask_low
        else:
            floors = [p for p in (leg.seller_low, leg.ask_low) if _cent(p)]
            active_floor = min(floors) if floors else None
        flicker = leg.latest_downward_receipt == receipt and local_floor is not None and active_floor == local_floor
        cap = self._cap(event, ticker)
        decision = v36_decide(state, book, leg.active_target, cap,
                              active_floor, flicker, mature)
        decision.update({
            "policy_commit": POLICY_COMMIT, "shadow_only": True,
            "no_order_authority": True, "event_ticker": event,
            "receipt": receipt, "receipt_ts": ts, "book": book,
            "depth_ratio_top5": round(ratio, 6), "state": state,
            "state_receipt": state_receipt.receipt if state_receipt else None,
            "state_authority": combined["authority"],
            "state_disagreement": combined["disagreement"],
            "active_target_before_cents": leg.active_target,
            "active_evidence_floor_cents": active_floor,
            "floor_mature": mature, "pair_cap_cents": cap,
        })
        self._emit("v36_shadow_decision", decision, ticker)
        if decision["action"] in ("PLACE_REST", "REPRICE_REST"):
            leg.active_target, leg.target_action_ts = decision["target_cents"], ts
        elif decision["action"] == "CANCEL_REST":
            leg.active_target, leg.target_action_ts = None, None
        elif decision["action"] == "TAKE":
            self._fill(event, ticker, leg, int(decision["target_cents"]), ts,
                       "PROVEN_TAKER_DISPLAYED_ASK_SIZE_AT_SUBMISSION", receipt)
        leg.previous_bid, leg.previous_ask = bid, ask
        return decision

    def snapshot(self):
        return {"policy_commit": POLICY_COMMIT, "shadow_only": True,
                "legs": {ticker: {"active_target_cents": leg.active_target,
                                   "filled_price_cents": leg.fill_price,
                                   "filled_ts": leg.fill_ts}
                         for ticker, leg in sorted(self._legs.items())}}
