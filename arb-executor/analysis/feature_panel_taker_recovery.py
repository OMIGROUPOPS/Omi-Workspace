"""Causal trade-direction recovery primitives; no engine imports or orders.

Arithmetic attribution is an estimate from the last completed book second.
It never supplies the authoritative flow label. An absent/locked/crossed book and
inside-spread prints stay AMBIGUOUS. Exact API identity recovery is opt-in;
multiple source/API matches cannot be resolved by arbitrarily choosing a row.
"""
from __future__ import annotations

from bisect import bisect_left
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
import math


def decimal(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    return result if result.is_finite() else None


def arithmetic_aggressor(price, bid, ask):
    """YES-price coordinates: at/above offer buys YES; at/below bid sells YES."""
    price, bid, ask = map(decimal, (price, bid, ask))
    if price is None:
        return dict(side=None, status='AMBIGUOUS', reason='MISSING_PRICE')
    if bid is None or ask is None:
        return dict(side=None, status='AMBIGUOUS', reason='MISSING_TWO_SIDED_BOOK')
    if bid >= ask:
        return dict(side=None, status='AMBIGUOUS', reason='LOCKED_OR_CROSSED_BOOK')
    if price >= ask:
        return dict(side='yes', status='ARITHMETIC_ESTIMATE', reason='AT_OR_ABOVE_ASK')
    if price <= bid:
        return dict(side='no', status='ARITHMETIC_ESTIMATE', reason='AT_OR_BELOW_BID')
    return dict(side=None, status='AMBIGUOUS', reason='INSIDE_SPREAD')


def preceding_book(books, epochs, print_epoch):
    """Exclude the print's entire second: its final book could follow the print."""
    index = bisect_left(epochs, math.floor(print_epoch)) - 1
    return None if index < 0 else books[index]


def same_second_quote_change(books, epochs, print_epoch):
    """Post-second diagnostic, unavailable at the trade's intra-second time.

    The extract holds the final state of each observed second. A missing prior
    book cannot establish change/no-change. Absence of a changed compacted state
    is not evidence that no intra-second transient quote change occurred.
    """
    second = math.floor(print_epoch)
    prior = preceding_book(books, epochs, print_epoch)
    current_index = bisect_left(epochs, second + 1) - 1
    if prior is None:
        changed = None
    elif current_index >= 0 and math.floor(epochs[current_index]) == second:
        current = books[current_index]
        changed = any(current[side][0][0] != prior[side][0][0] for side in ('bids', 'asks'))
    else:
        changed = False
    return dict(top_quote_changed_in_print_second=changed,
                top_quote_change_available_epoch=second + 1,
                top_quote_change_scope='FINAL_STORED_SECOND_VS_PRIOR; transient changes not observable')


def exact_trade_key(ticker, epoch, price, size):
    price, size = decimal(price), decimal(size)
    if not ticker or not math.isfinite(float(epoch)) or price is None or size is None:
        raise ValueError('INCOMPLETE_EXACT_TRADE_KEY')
    return ticker, math.floor(float(epoch)), price, size


def unique_identity_matches(source_rows, api_rows):
    """Opt-in one-to-one key recovery; repeated API pages deduped by trade ID.

Callers must explicitly authorize key recovery before using these matches.
An API ID with conflicting payloads and any multiple matching IDs fail closed.
No nearest-time, float-tolerance, row-order or side-vote matching is used.
"""
    source_counts = Counter(exact_trade_key(r['ticker'], r['ts'], r['price'], r['size'])
                            for r in source_rows)
    by_id, conflicts, conflicting_keys, payloads = {}, set(), set(), {}
    for row in api_rows:
        identity = row.get('trade_id')
        if not identity:
            continue
        canonical = (exact_trade_key(row['ticker'], row['ts'], row['price'], row['size']),
                     row.get('taker_side'), row.get('is_block_trade'),
                     row.get('taker_outcome_side'), row.get('taker_book_side'), row.get('direction_status'))
        if identity in by_id and by_id[identity] != canonical:
            conflicts.add(identity)
            conflicting_keys.update((by_id[identity][0], canonical[0]))
        by_id[identity] = canonical
        payloads[identity] = row
    by_key = defaultdict(list)
    for identity, canonical in by_id.items():
        if identity not in conflicts:
            # Even an unlabeled/block row participates in identity ambiguity.
            by_key[canonical[0]].append(identity)
    result = []
    for row in source_rows:
        key = exact_trade_key(row['ticker'], row['ts'], row['price'], row['size'])
        matches = by_key.get(key, [])
        stored_id = row.get('trade_id')
        if stored_id and stored_id in by_id and stored_id not in conflicts and by_id[stored_id][0] == key:
            identity, status = stored_id, 'EXACT_TRADE_ID'
        elif not stored_id and source_counts[key] == 1 and len(matches) == 1 and key not in conflicting_keys:
            identity, status = matches[0], 'UNIQUE_EXACT_IDENTITY_RECOVERY'
        else:
            result.append(dict(trade_id=None, taker_side=None,
                               status='UNRESOLVED_IDENTITY', api_candidates=len(matches),
                               source_candidates=source_counts[key]))
            continue
        payload = payloads[identity]
        result.append(dict(trade_id=identity, status=status,
            **{field: payload.get(field) for field in ('taker_side', 'taker_outcome_side', 'taker_book_side',
                'legacy_taker_side', 'direction_status', 'is_block_trade', 'fetched_at')}))
    return result


def authoritative_direction(match):
    """No block/unknown-block/legacy/estimated direction enters the flow block."""
    if match.get('status') not in ('EXACT_TRADE_ID', 'UNIQUE_EXACT_IDENTITY_RECOVERY'):
        return dict(side=None, basis='UNRESOLVED_IDENTITY', direction_authoritative=False)
    if match.get('is_block_trade') is True:
        return dict(side=None, basis='EXCLUDED_OFF_BOOK_TRADE', direction_authoritative=False)
    if match.get('is_block_trade') is not False:
        return dict(side=None, basis='UNRESOLVED_BLOCK_STATUS', direction_authoritative=False)
    if match.get('direction_status') != 'CANONICAL_API_DIRECTION' or match.get('taker_side') not in ('yes', 'no'):
        return dict(side=None, basis=match.get('direction_status') or 'CANONICAL_API_DIRECTION_ABSENT', direction_authoritative=False)
    basis = 'API_EXACT_TRADE_ID' if match['status'] == 'EXACT_TRADE_ID' else 'API_UNIQUE_EXACT_IDENTITY'
    return dict(side=match['taker_side'], basis=basis, direction_authoritative=True)


def net_maker_residual(previous_size, current_size, executed_size):
    """Displayed Δsize + executed size = net maker addition (not gross flow).

Executions remove displayed liquidity; adding their size back removes that
effect. Missing level visibility or incomplete execution attribution is None,
not zero. A level outside a top-five snapshot is not an observed empty queue.
"""
    values = tuple(map(decimal, (previous_size, current_size, executed_size)))
    if any(v is None or v < 0 for v in values):
        return None
    previous, current, executed = values
    return current - previous + executed
