"""Read-only, paced public-trade lookup; exact identities only, no orders.

Transport limits are operational CLI choices, not feature/bench constants.
Only rows matching an already accepted library-print key are retained.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request

from feature_panel_taker_recovery import decimal, exact_trade_key

ROOT = 'https://external-api.kalshi.com/trade-api/v2'


def epoch(value):
    date = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if date.tzinfo is None:
        raise ValueError('API_TIMESTAMP_WITHOUT_ZONE')
    return date.timestamp()


def canonical_trade(row):
    sides = [row['taker_outcome_side']] if row.get('taker_outcome_side') in ('yes', 'no') else []
    book_side = row.get('taker_book_side')
    if book_side in ('bid', 'ask'):
        sides.append('yes' if book_side == 'bid' else 'no')
    # Legacy taker_side remains audit evidence, never a replacement for absent
    # canonical direction. Conflicting API fields are retained but fail closed.
    legacy = row.get('taker_side')
    conflict = len(set(sides)) > 1 or (sides and legacy in ('yes', 'no') and legacy != sides[0])
    direction = sides[0] if sides and not conflict else None
    status = 'CONFLICTING_API_DIRECTION' if conflict else 'CANONICAL_API_DIRECTION' if direction else 'CANONICAL_API_DIRECTION_ABSENT'
    price = decimal(row.get('yes_price_dollars'))
    if price is not None:
        price *= 100  # Filed cents/dollar unit conversion, not a fitted weight.
    else:
        price = decimal(row.get('yes_price'))
    size = decimal(row.get('count_fp', row.get('count')))
    if price is None or size is None or size <= 0 or not row.get('trade_id'):
        raise ValueError('API_TRADE_ID_PRICE_OR_POSITIVE_SIZE_MISSING')
    return dict(ticker=row['ticker'], ts=epoch(row['created_time']),
                price=str(price), size=str(size), trade_id=row['trade_id'],
                taker_side=direction, taker_outcome_side=row.get('taker_outcome_side'),
                taker_book_side=book_side, legacy_taker_side=legacy,
                direction_status=status,
                is_block_trade=row.get('is_block_trade') if isinstance(row.get('is_block_trade'), bool) else None)


class PublicTrades:
    def __init__(self, pause_seconds, page_limit, retry_limit, timeout):
        if pause_seconds <= 0 or not 0 < page_limit <= 1000 or retry_limit < 0:
            raise ValueError('INVALID_PUBLIC_API_TRANSPORT_LIMIT')
        self.pause, self.page_limit = pause_seconds, page_limit
        self.retries, self.timeout, self.last_request = retry_limit, timeout, None
        self.requests = 0
        self.cutoff, self.cutoff_proof = self.get('/historical/cutoff', {})
        self.split = epoch(self.cutoff['trades_created_ts'])

    def get(self, endpoint, params):
        url = ROOT + endpoint + ('?' + urllib.parse.urlencode(params) if params else '')
        for attempt in range(self.retries + 1):
            if self.last_request is not None:
                time.sleep(max(0, self.pause - (time.monotonic() - self.last_request)))
            self.last_request = time.monotonic()
            self.requests += 1
            try:
                request = urllib.request.Request(url, headers={'Accept': 'application/json'})
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    raw = response.read()
                return json.loads(raw), dict(endpoint=endpoint, parameters=params,
                    fetched_at=datetime.now(timezone.utc).isoformat(),
                    response_sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
            except urllib.error.HTTPError as error:
                if error.code not in (429, 500, 502, 503, 504) or attempt == self.retries:
                    raise
                time.sleep(self.pause * (2 ** (attempt + 1)))

    def matching(self, source_rows):
        """Fetch labels for accepted prints, independent of arithmetic agreement.

        Pagination may return unrequested prints; these are immediately filtered
        to exact input keys. Raw pages and non-library rows are never written.
        The caller decides identity uniqueness across the complete source set.
        """
        if not source_rows:
            return [], []
        tickers = {r['ticker'] for r in source_rows}
        if len(tickers) != 1:
            raise ValueError('API_LOOKUP_MUST_BE_ONE_LIBRARY_LEG')
        keys = {exact_trade_key(r['ticker'], r['ts'], r['price'], r['size']) for r in source_rows}
        low = min(key[1] for key in keys)
        high = max(key[1] for key in keys)
        bounds = []
        if low < self.split:
            bounds.append(('/historical/trades', low, min(high, math.ceil(self.split) - 1)))
        if high >= self.split:
            bounds.append(('/markets/trades', max(low, math.floor(self.split)), high))
        matches, proofs = [], []
        for endpoint, first, last in bounds:
            cursor, seen = '', set()
            while True:
                # Request through the end of the last recorded second, then
                # exact-key filter; fractional API timestamps must not vanish.
                params = dict(ticker=next(iter(tickers)), min_ts=first, max_ts=last + 1,
                              limit=self.page_limit)
                if cursor:
                    params['cursor'] = cursor
                page, proof = self.get(endpoint, params)
                for raw in page['trades']:
                    row = canonical_trade(raw)
                    if exact_trade_key(row['ticker'], row['ts'], row['price'], row['size']) in keys:
                        matches.append(dict(row, fetched_at=proof['fetched_at']))
                proofs.append(dict(proof, returned_rows=len(page['trades'])))
                cursor = page.get('cursor', '')
                if not cursor:
                    break
                if cursor in seen:
                    raise ValueError('API_PAGINATION_CURSOR_LOOP')
                seen.add(cursor)
        return matches, proofs
