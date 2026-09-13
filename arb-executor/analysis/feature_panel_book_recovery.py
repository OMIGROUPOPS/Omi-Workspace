"""Causal displayed-depth primitives for the eleven-block screen.

Top-five absence is not zero depth beyond the visible fifth level. Snapshot
residuals are net changes, never identified individual orders or queue priority.
"""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
import math

from feature_panel_taker_recovery import decimal, net_maker_residual


def book_invalid_reason(book):
    """Verify a two-sided, noncrossed captured book without repairing prices."""
    if book is None or len(book)<3:
        return 'NO_TWO_SIDED_VISIBLE_CAPTURE'
    sides=[]
    for rows in book[1:3]:
        prices=[]
        for raw_price,raw_size in rows:
            price,size=decimal(raw_price),decimal(raw_size)
            if price is not None and size is not None and size>0:
                prices.append(price)
        sides.append(prices)
    if not all(sides):
        return 'NO_TWO_SIDED_VISIBLE_CAPTURE'
    if max(sides[0])>=min(sides[1]):
        return 'LOCKED_OR_CROSSED_CAPTURE'
    return None


def usable_book(book):
    return book_invalid_reason(book) is None


def visible_depth(levels, price, side, *, full=False):
    """Return displayed size or missing, with a proven visibility interval."""
    price = decimal(price)
    rows = [(decimal(p), decimal(q)) for p, q in levels]
    rows = [(p,q) for p,q in rows if p is not None and q is not None and q > 0]
    if price is None or any(p < 0 for p,q in rows):
        return None
    found = [q for p,q in rows if p == price]
    if len(found) > 1:
        raise ValueError('DUPLICATE_DISPLAYED_PRICE_LEVEL')
    if found:
        return found[0]
    if full:
        return Decimal(0)
    if not rows:
        return None
    bound = min(p for p,q in rows) if side == 'bid' else max(p for p,q in rows)
    visible = price >= bound if side == 'bid' else price <= bound
    return Decimal(0) if visible else None


def snapshot_residual(previous, current, prints, *, full=False, known_at_epoch=None):
    """Net maker residual at levels visible at both snapshots.

    Source timestamps have second precision. An accepted print in either
    snapshot's second has unknown ordering relative to that snapshot; affected
    levels are missing, never allocated by an invented within-second sequence.
    Only exact API-authoritative, explicitly non-block directions allocate an
    execution. Arithmetic/original labels alone never do. Returned rows are
    [book side, YES cents, net contracts, executed contracts]. Both snapshots
    are already normalized to YES cents by the capture-specific decoder.

    known_at_epoch is the receipt cutoff, not the final snapshot timestamp.
    Once known, a fractional print anywhere in a boundary second makes that
    level unresolved, even when its timestamp follows the snapshot's recorded
    second. Omitted cutoff preserves the historical as-of-current contract.
    """
    start, end = previous[0], current[0]
    if end <= start:
        raise ValueError('NONINCREASING_SNAPSHOT_INTERVAL')
    cutoff=end if known_at_epoch is None else known_at_epoch
    if not math.isfinite(cutoff) or cutoff<end:
        raise ValueError('MAKER_SNAPSHOT_AFTER_RECEIPT_CUTOFF')
    interval_invalid=book_invalid_reason(previous) or book_invalid_reason(current)
    executions, ambiguous = defaultdict(Decimal), set()
    for row in prints:
        if row['ts'] > cutoff:
            continue  # Even missingness may not depend on a future print.
        if math.floor(row['ts']) < math.floor(start) or math.floor(row['ts']) > math.floor(end):
            continue
        price, size = decimal(row['price']), decimal(row['size'])
        if size is None or size <= 0:
            continue
        if row.get('is_block_trade') is True:
            continue  # An off-book execution did not consume displayed depth.
        authoritative = (row.get('direction_authoritative') is True
                         and row.get('is_block_trade') is False)
        side = {'yes':'ask','no':'bid'}.get(row.get('side')) if authoritative else None
        targets = ('bid','ask') if side is None else (side,)
        boundary = math.floor(row['ts']) in (math.floor(start), math.floor(end))
        for target in targets:
            if boundary or side is None or row.get('interval_ordering_unresolved') is True:
                ambiguous.add((target,price))
            elif start < row['ts'] < end:
                executions[(target,price)] += size
    result = []
    for index, side in ((1,'bid'),(2,'ask')):
        levels = {decimal(p) for source in (previous[index],current[index]) for p,q in source
                  if decimal(p) is not None and decimal(q) is not None and decimal(q)>0}
        levels.update(p for s,p in executions if s==side)
        levels.update(p for s,p in ambiguous if s==side and p is not None)
        for price in sorted(levels):
            before = visible_depth(previous[index],price,side,full=full)
            after = visible_depth(current[index],price,side,full=full)
            executed = None if (side,price) in ambiguous else executions[(side,price)]
            net = None if interval_invalid else net_maker_residual(before,after,executed)
            result.append([side,float(price),None if net is None else float(net),
                           None if executed is None else float(executed)])
    return result


def imbalance(bids, asks, *, top_only=False):
    def sizes(rows):
        use = rows[:1] if top_only else rows
        values = [decimal(q) for p,q in use]
        if not values or any(v is None or v < 0 for v in values):
            return None
        return sum(values, Decimal(0))
    bid,ask = sizes(bids),sizes(asks)
    if bid is None or ask is None or bid+ask == 0:
        return None
    return float((bid-ask)/(bid+ask))


def spike_reversion(prints, start, end, formation):
    """Largest consecutive positive-print move in [start,end), earliest tie.

    The pre-window seed is the last in-span print before start, if present.
    Retracement at the completed close is signed in units of that move: zero
    means no retracement, one a full return, >one an overshoot, <zero extension.
    It is not clipped and never reads a print at/after the close.
    """
    previous, close, largest = None, None, None
    for row in prints:
        ts,price,size = row[:3]
        if ts < formation or size <= 0:
            continue
        if ts >= end:
            break
        if ts < start:
            previous = price
            continue
        close = price
        if previous is not None:
            move = price-previous
            if largest is None or abs(move)>abs(largest[0]):
                largest = (move,price)
        previous = price
    if largest is None:
        return None,None
    move,peak = largest
    return move, None if move == 0 else (peak-close)/move


class DepthDecoder:
    """Capture-declared NO-leg WS price scale, with explicit sequence custody.

    Feed every frame, not just library frames, so SID gaps cannot disappear.
    A recorder-started sequence and an actual snapshot are both required.
    A gap invalidates affected ladders until a new snapshot arrives. New raw
    units/unknown conventions fail closed instead of being guessed.
    """
    def __init__(self, required, *, no_price_convention='LEGACY_NO'):
        if no_price_convention not in ('LEGACY_NO','YES'):
            raise ValueError('UNDECLARED_WS_PRICE_CONVENTION')
        self.required = set(required)
        self.no_price_convention = no_price_convention
        self.capture_no_price_convention = no_price_convention
        self.started, self.sequence, self.books = False, {}, {}
        self.counters = defaultdict(int)
        self.invalidated = []

    def reset(self):
        self.started, self.sequence, self.books = True, {}, {}

    def invalidate_archive(self):
        """A skipped archive is a sequence gap, not an empty hour of trading."""
        invalidated=list(self.books)
        self.books,self.sequence={},{}
        self.counters['excluded_archive_gaps'] += 1
        return invalidated

    def yes_cents(self, raw_price, side):
        return ((1-raw_price)*100 if side=='ask' and self.no_price_convention=='LEGACY_NO'
                else raw_price*100)

    def state(self, ticker, available_epoch, sid, seq):
        book=self.books.get(ticker)
        if book is None:
            return dict(ticker=ticker,available_epoch=available_epoch,sid=sid,seq=seq,
                        valid=False,reason='DEPTH_CUSTODY_INVALIDATED')
        return dict(ticker=ticker,available_epoch=available_epoch,sid=sid,seq=seq,valid=True,
            no_price_convention=self.no_price_convention,
            bids=[[float(p),float(q)] for p,q in sorted(book['bid'].items(),reverse=True)],
            asks=[[float(p),float(q)] for p,q in sorted(book['ask'].items())])

    def consume(self, row, *, materialize=True):
        self.invalidated=[]
        if row.get('ev')=='recorder_start':
            self.invalidated=list(self.books)
            self.reset()
            declared=row.get('use_yes_price')
            if declared is not None and not isinstance(declared,bool):
                self.started=False
                self.counters['unknown_capture_price_convention'] += 1
                return None
            self.no_price_convention=('YES' if declared is True else 'LEGACY_NO'
                if declared is False else self.capture_no_price_convention)
            self.counters['recorder_starts'] += 1
            return None
        wrapper = row.get('m', {})
        sid,seq = wrapper.get('sid'),wrapper.get('seq')
        if sid is not None and seq is not None:
            old = self.sequence.get(sid)
            if old is not None and seq != old+1:
                self.counters['sequence_gaps'] += 1
                self.invalidated.extend(ticker for ticker,book in self.books.items() if book['sid']==sid)
                self.books = {ticker:book for ticker,book in self.books.items() if book['sid']!=sid}
            self.sequence[sid] = seq
        msg = wrapper.get('msg', {})
        ticker = msg.get('market_ticker') if isinstance(msg,dict) else None
        typ = wrapper.get('type')
        if ticker not in self.required or typ not in ('orderbook_snapshot','orderbook_delta'):
            return None
        if not self.started:
            self.counters['unverified_recorder_epoch'] += 1
            return None
        if sid is None or seq is None or decimal(row.get('t')) is None:
            self.counters['missing_sequence_or_receipt_clock'] += 1
            return None
        if typ=='orderbook_snapshot':
            if 'yes_dollars_fp' not in msg or 'no_dollars_fp' not in msg:
                self.counters['unsupported_snapshot_units'] += 1
                self.invalidated.append(ticker)
                self.books.pop(ticker,None)
                return None
            book = dict(sid=sid,bid={},ask={})
            for key,side in (('yes_dollars_fp','bid'),('no_dollars_fp','ask')):
                for raw_price,raw_size in msg[key]:
                    price,size = decimal(raw_price),decimal(raw_size)
                    if price is None or size is None or size<0:
                        raise ValueError('INVALID_WS_LADDER_VALUE')
                    cents = self.yes_cents(price,side)
                    if size>0:
                        if cents in book[side]:
                            raise ValueError('DUPLICATE_WS_SNAPSHOT_LEVEL')
                        book[side][cents]=size
            if not book['bid'] and not book['ask']:
                self.counters['empty_snapshot_not_seeded'] += 1
                self.invalidated.append(ticker)
                self.books.pop(ticker,None)
                return None
            self.books[ticker]=book
            self.counters['seeded_snapshots'] += 1
        else:
            book = self.books.get(ticker)
            if book is None or book['sid']!=sid:
                self.counters['unseeded_delta'] += 1
                return None
            price,delta = decimal(msg.get('price_dollars')),decimal(msg.get('delta_fp'))
            side = {'yes':'bid','no':'ask'}.get(msg.get('side'))
            if price is None or delta is None or side is None:
                self.counters['unsupported_delta_units'] += 1
                self.invalidated.append(ticker)
                self.books.pop(ticker,None)
                return None
            cents = self.yes_cents(price,side)
            size = book[side].get(cents,Decimal(0))+delta
            if size<0:
                self.counters['negative_depth_invalidated'] += 1
                self.invalidated.append(ticker)
                self.books.pop(ticker,None)
                return None
            if size:
                book[side][cents]=size
            else:
                book[side].pop(cents,None)
            self.counters['applied_deltas'] += 1
        if not materialize:
            return dict(ticker=ticker,available_epoch=float(row['t']),sid=sid,seq=seq)
        return self.state(ticker,float(row['t']),sid,seq)
