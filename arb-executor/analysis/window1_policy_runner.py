#!/usr/bin/env python3
'''Causal policy-outcome producer for the strict Window-1 benchmark.

The runner consumes the normalized evidence contract, never raw production
state.  It refuses to run unless the live validation gate passed, emits every
floor-passing ledger event, and keeps fit and holdout physically separate.
'''

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from window1_benchmark import (
    BENCHMARK_VERSION,
    BenchmarkError,
    FULL_BOOK_SOURCE,
    REQUIRED_LOT,
    canonical_true_prints,
    load_holdout_declaration,
    parse_exchange_ts,
    read_jsonl,
    replay_resting_buy,
    resolve_window_end,
    sha256_file,
    valid_full_book,
    write_jsonl,
)


RUNNER_VERSION = 'window1-policy-runner-v1'


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        raise BenchmarkError(f'cannot read JSON {path}: {exc}') from exc
    if not isinstance(value, dict):
        raise BenchmarkError(f'JSON object required: {path}')
    return value


def require_validation(path: Path) -> dict[str, Any]:
    summary = load_json(path)
    if summary.get('gate_pass') is not True:
        raise BenchmarkError('policy outcomes forbidden: validation gate failed')
    return summary


def best_level(book: Mapping[str, Any], side: str) -> tuple[int, float] | None:
    ladder = book.get(side)
    if not isinstance(ladder, list):
        return None
    levels = []
    for level in ladder:
        if not isinstance(level, list) or len(level) != 2:
            continue
        try:
            price = int(level[0])
            quantity = max(0.0, float(level[1] or 0))
        except (TypeError, ValueError):
            continue
        levels.append((price, quantity))
    if not levels:
        return None
    if side == 'bids':
        return max(levels, key=lambda value: value[0])
    return min(levels, key=lambda value: value[0])


def ladder_levels(book: Mapping[str, Any], side: str) -> list[tuple[int, float]]:
    ladder = book.get(side)
    out = []
    if not isinstance(ladder, list):
        return out
    for level in ladder:
        if not isinstance(level, list) or len(level) != 2:
            continue
        try:
            out.append((int(level[0]), max(0.0, float(level[1] or 0))))
        except (TypeError, ValueError):
            continue
    return sorted(out, key=lambda value: value[0], reverse=(side == 'bids'))


def book_ts(book: Mapping[str, Any]) -> float:
    return parse_exchange_ts(book.get('exchange_ts'), 'book.exchange_ts')


def full_books_for(
    ticker: str,
    rows: Sequence[Mapping[str, Any]],
    left: float,
    right: float,
) -> tuple[list[Mapping[str, Any]], str | None]:
    valid = []
    for row in rows:
        if str(row.get('ticker') or '') != ticker:
            continue
        if row.get('exchange_ts') in (None, ''):
            if row.get('source') == FULL_BOOK_SOURCE:
                return [], 'ws_depth row lacks exchange timestamp'
            continue
        try:
            timestamp = book_ts(row)
        except BenchmarkError as exc:
            if row.get('source') == FULL_BOOK_SOURCE:
                return [], str(exc)
            continue
        if not left <= timestamp <= right:
            continue
        ok, reason = valid_full_book(row)
        if row.get('source') == FULL_BOOK_SOURCE and not ok:
            return [], reason
        if ok:
            valid.append(row)
    valid.sort(key=book_ts)
    if not valid:
        return [], 'no valid full ws_depth book in candidate window'
    epoch = valid[0].get('epoch_id')
    if any(row.get('epoch_id') != epoch for row in valid):
        return [], 'ws_depth epoch changes inside candidate window'
    try:
        sequences = [int(row['sequence']) for row in valid]
    except (KeyError, TypeError, ValueError):
        return [], 'ws_depth sequence missing or invalid'
    if any(b <= a for a, b in zip(sequences, sequences[1:])):
        return [], 'ws_depth sequence is not strictly increasing'
    return valid, None


def feature_receipt(
    event: Mapping[str, Any],
    leg: Mapping[str, Any],
    book: Mapping[str, Any],
    prints: Sequence[Mapping[str, Any]],
    timestamp: float,
    scheduled: float,
) -> dict[str, Any]:
    bids = ladder_levels(book, 'bids')
    asks = ladder_levels(book, 'asks')
    best_bid = bids[0][0] if bids else None
    best_ask = asks[0][0] if asks else None
    bid_total = sum(quantity for _, quantity in bids)
    ask_total = sum(quantity for _, quantity in asks)
    top5_bid = sum(quantity for _, quantity in bids[:5])
    top5_ask = sum(quantity for _, quantity in asks[:5])
    total = bid_total + ask_total
    recent = [row for row in prints
              if str(row.get('ticker') or '') == str(leg.get('ticker') or '')
              and timestamp - 300 <= float(row['exchange_ts']) <= timestamp]
    recent_size = sum(float(row['size']) for row in recent)
    mid = ((best_bid + best_ask) / 2
           if best_bid is not None and best_ask is not None else None)
    up_size = sum(float(row['size']) for row in recent
                  if mid is not None and int(row['price_cents']) >= mid)
    down_size = sum(float(row['size']) for row in recent
                    if mid is not None and int(row['price_cents']) < mid)
    ask_over_bid = ask_total / bid_total if bid_total > 0 else None
    return {
        'macrostructure': {
            'category': event.get('category'),
            'role': leg.get('role'),
            'shape_class': leg.get('shape_class'),
            'schedule_source': event.get('schedule_source'),
            'schedule_confidence': event.get('schedule_confidence'),
            'minutes_to_scheduled_start': (scheduled - timestamp) / 60,
            'cross_game_liquidity': event.get('cross_game_liquidity'),
        },
        'microstructure': {
            'best_bid_cents': best_bid,
            'best_ask_cents': best_ask,
            'spread_cents': (best_ask - best_bid
                             if best_bid is not None and best_ask is not None
                             else None),
            'bid_depth_full': bid_total,
            'ask_depth_full': ask_total,
            'bid_depth_top5': top5_bid,
            'ask_depth_top5': top5_ask,
            'bid_depth_below_top5': bid_total - top5_bid,
            'ask_depth_below_top5': ask_total - top5_ask,
            'full_ladder_imbalance': ((bid_total - ask_total) / total
                                      if total else None),
            'ask_over_bid_ratio': ask_over_bid,
            'extreme_ask_over_bid_sanity_class': (
                ask_over_bid is not None and ask_over_bid >= 4),
            'true_print_count_5m': len(recent),
            'true_print_size_5m': recent_size,
            'true_print_up_size_5m': up_size,
            'true_print_down_size_5m': down_size,
            'ws_epoch_id': book.get('epoch_id'),
            'ws_sequence': book.get('sequence'),
        },
    }


def price_for_policy(
    policy: Mapping[str, Any],
    event: Mapping[str, Any],
    leg: Mapping[str, Any],
    book: Mapping[str, Any],
) -> int | None:
    bid = best_level(book, 'bids')
    ask = best_level(book, 'asks')
    if bid is None or ask is None:
        return None
    best_bid = bid[0]
    maker_ceiling = ask[0] - 1
    rule = str(policy.get('placement_rule') or '')
    if rule in {'touch', 'walk_law'}:
        price = best_bid
    elif rule == 'depth_support':
        depth = max(0, int(policy.get('max_depth_cents', 5)))
        ladder = ladder_levels(book, 'bids')
        level_limit = policy.get('decision_ladder_level_limit')
        if level_limit is not None:
            ladder = ladder[:max(1, int(level_limit))]
        candidates = [level for level in ladder
                      if level[0] >= best_bid - depth]
        if not candidates:
            return None
        price = max(candidates, key=lambda level: (level[1], level[0]))[0]
    elif rule == 'category_offset':
        offsets = policy.get('category_offsets') or {}
        price = best_bid - int(offsets.get(str(event.get('category')), 0))
    elif rule == 'shape_cell_offset':
        offsets = policy.get('shape_offsets') or {}
        shape = str(leg.get('shape_class') or 'unknown')
        if shape not in offsets:
            return None
        price = best_bid - int(offsets[shape])
    elif rule == 'backwalk':
        price = best_bid - int(policy.get('initial_depth_cents', 2))
    else:
        raise BenchmarkError(f'unknown placement rule: {rule}')
    return min(99, maker_ceiling, max(1, int(price)))


def print_evidence_since(
    prints: Sequence[Mapping[str, Any]],
    ticker: str,
    start: float,
    end: float,
    held_price: int,
) -> bool:
    return any(str(row.get('ticker') or '') == ticker
               and start < float(row['exchange_ts']) <= end
               and float(row['size']) > 0
               and int(row['price_cents']) >= held_price
               for row in prints)


def action_schedule(
    policy: Mapping[str, Any],
    event: Mapping[str, Any],
    leg: Mapping[str, Any],
    books: Sequence[Mapping[str, Any]],
    prints: Sequence[Mapping[str, Any]],
    placement_not_before: float,
    scheduled: float,
) -> tuple[list[tuple[float, int, Mapping[str, Any]]], str | None]:
    first = next((row for row in books if book_ts(row) >= placement_not_before),
                 None)
    if first is None:
        return [], 'no full book at or after leg post time'
    first_price = price_for_policy(policy, event, leg, first)
    if first_price is None:
        return [], 'placement price unavailable for class or book'
    actions = [(book_ts(first), first_price, first)]
    rule = str(policy.get('placement_rule') or '')
    if rule not in {'walk_law', 'backwalk'}:
        return actions, None
    current = first_price
    last_action = book_ts(first)
    moves = 0
    max_moves = max(0, int(policy.get('max_moves', 2)))
    move_step = max(1, int(policy.get('move_step_cents', 1)))
    backwalk_start = scheduled - int(
        policy.get('backwalk_start_minutes_before_schedule', 120)) * 60
    ticker = str(leg.get('ticker') or '')
    for row in books:
        timestamp = book_ts(row)
        if timestamp <= last_action or moves >= max_moves:
            continue
        bid = best_level(row, 'bids')
        ask = best_level(row, 'asks')
        if bid is None or ask is None or bid[0] <= current:
            continue
        if rule == 'walk_law':
            if not print_evidence_since(prints, ticker, last_action,
                                        timestamp, current):
                continue
            target = min(bid[0], ask[0] - 1)
        else:
            if timestamp < backwalk_start:
                continue
            bids = ladder_levels(row, 'bids')
            asks = ladder_levels(row, 'asks')
            bid_qty = sum(quantity for _, quantity in bids)
            ask_qty = sum(quantity for _, quantity in asks)
            imbalance = ((bid_qty - ask_qty) / (bid_qty + ask_qty)
                         if bid_qty + ask_qty else -1)
            if imbalance < float(policy.get('move_imbalance_min', 0.0)):
                continue
            target = min(current + move_step, bid[0], ask[0] - 1)
        if target <= current:
            continue
        current = int(target)
        last_action = timestamp
        actions.append((timestamp, current, row))
        moves += 1
    return actions, None


def w1_close_reference(
    ticker: str,
    prints: Sequence[Mapping[str, Any]],
    left: float,
    right: float,
) -> int | None:
    eligible = [row for row in prints
                if str(row.get('ticker') or '') == ticker
                and left <= float(row['exchange_ts']) <= right
                and float(row['size']) > 0]
    if not eligible:
        return None
    return int(max(eligible, key=lambda row: float(row['exchange_ts']))[
        'price_cents'])


def simulate_leg(
    candidate_id: str,
    policy: Mapping[str, Any],
    event: Mapping[str, Any],
    leg: Mapping[str, Any],
    books_all: Sequence[Mapping[str, Any]],
    prints: Sequence[Mapping[str, Any]],
    left: float,
    right: float,
    scheduled: float,
    placement_not_before: float,
) -> dict[str, Any]:
    ticker = str(leg.get('ticker') or '')
    if not ticker:
        return {'status': 'missing', 'detail': 'leg ticker missing'}
    books, defect = full_books_for(ticker, books_all, left, right)
    if defect:
        return {'status': 'corrupt', 'ticker': ticker, 'detail': defect}
    actions, defect = action_schedule(policy, event, leg, books, prints,
                                      placement_not_before, scheduled)
    if defect:
        return {'status': 'unknown', 'ticker': ticker, 'detail': defect}
    initial_features = feature_receipt(event, leg, actions[0][2], prints,
                                       actions[0][0], scheduled)
    receipts = []
    for index, (timestamp, price, action_book) in enumerate(actions):
        lifetime_end = (actions[index + 1][0]
                        if index + 1 < len(actions) else right)
        synthetic = {
            'event_id': event.get('event_id'),
            'ticker': ticker,
            'leg': leg.get('leg'),
            'order_id': f'sim-{candidate_id}-{event.get("event_id")}-{ticker}-{index}',
            'client_order_id': f'sim-client-{candidate_id}-{event.get("event_id")}-{ticker}-{index}',
            'purpose': 'entry',
            'action': 'buy',
            'price_cents': price,
            'quantity': REQUIRED_LOT,
            'exchange_created_ts': timestamp,
            'evaluation_end_exchange_ts': lifetime_end,
        }
        replay = replay_resting_buy(synthetic, prints, books_all)
        receipts.append({
            'post_exchange_ts': timestamp,
            'stop_exchange_ts': lifetime_end,
            'price_cents': price,
            'queue_result': replay.status,
            'queue_detail': replay.detail,
        })
        if replay.status == 'unknown':
            return {
                'status': 'unknown',
                'ticker': ticker,
                'leg': leg.get('leg'),
                'detail': replay.detail,
                'required_quantity': REQUIRED_LOT,
                'filled_quantity': replay.predicted_fill_qty,
                'actions': receipts,
                'causal_features_at_first_post': initial_features,
            }
        if replay.status == 'filled':
            reference = w1_close_reference(ticker, prints, left, right)
            return {
                'status': 'filled',
                'ticker': ticker,
                'leg': leg.get('leg'),
                'required_quantity': REQUIRED_LOT,
                'filled_quantity': REQUIRED_LOT,
                'fill_vwap_cents': price,
                'first_fill_exchange_ts': replay.first_fill_latest,
                'completion_exchange_ts': replay.completion_latest,
                'w1_close_reference_cents': reference,
                'actions': receipts,
                'causal_features_at_first_post': initial_features,
            }
    reference = w1_close_reference(ticker, prints, left, right)
    return {
        'status': 'not_filled',
        'ticker': ticker,
        'leg': leg.get('leg'),
        'required_quantity': REQUIRED_LOT,
        'filled_quantity': 0,
        'fill_vwap_cents': None,
        'first_fill_exchange_ts': None,
        'completion_exchange_ts': None,
        'w1_close_reference_cents': reference,
        'actions': receipts,
        'causal_features_at_first_post': initial_features,
    }


def candidate_definitions(spec: Mapping[str, Any]) -> list[dict[str, Any]]:
    grid = spec.get('boundary_grid') or {}
    starts = grid.get('left_edge_hours_before_schedule') or []
    corridors = grid.get('schedule_only_corridor_minutes') or []
    policies = spec.get('policies') or []
    baseline_id = str(spec.get('boundary_baseline_policy_id') or '')
    baseline = next((policy for policy in policies
                     if policy.get('policy_id') == baseline_id), None)
    if baseline is None:
        raise BenchmarkError('boundary baseline policy is missing')
    out = []
    for start in starts:
        for corridor in corridors:
            boundary_id = f'tminus_{int(start)}h__corridor_{int(corridor)}m'
            window = {
                'boundary_id': boundary_id,
                'left_edge_hours_before_schedule': int(start),
                'schedule_only_corridor_minutes': int(corridor),
            }
            out.append({
                'candidate_id': f'BOUNDARY__{boundary_id}',
                'experiment_kind': 'boundary',
                'window_definition': window,
                'policy_definition': dict(baseline),
                'boundary_id': boundary_id,
                'policy_id': baseline_id,
            })
            for policy in policies:
                policy_id = str(policy.get('policy_id') or '')
                if not policy_id:
                    raise BenchmarkError('policy_id is required')
                out.append({
                    'candidate_id': f'POLICY__{boundary_id}__{policy_id}',
                    'experiment_kind': 'policy',
                    'window_definition': window,
                    'policy_definition': dict(policy),
                    'boundary_id': boundary_id,
                    'policy_id': policy_id,
                })
    return out


def ablated_policy(policy: Mapping[str, Any], family: str) -> dict[str, Any]:
    out = dict(policy)
    out['ablation_family_removed'] = family
    if family == 'macrostructure':
        if out.get('placement_rule') in {'category_offset',
                                         'shape_cell_offset'}:
            out['placement_rule'] = 'touch'
        if out.get('sequence_rule') == 'favorite_first':
            out['sequence_rule'] = 'simultaneous'
            out['sibling_delay_seconds'] = 0
    elif family == 'below_top5_ladder':
        out['decision_ladder_level_limit'] = 5
    elif family == 'true_print_direction_size_tempo':
        if out.get('placement_rule') == 'walk_law':
            out['max_moves'] = 0
    elif family == 'replenishment_cancellation_absorption':
        if out.get('placement_rule') == 'backwalk':
            out['max_moves'] = 0
    elif family == 'first_leg_fill_state':
        out['first_fill_response'] = 'hold'
    elif family == 'queue_and_own_volume':
        # Physical queue evidence remains mandatory.  This removes own-volume
        # awareness from the decision policy only, not from fill validation.
        out['decision_ignore_own_volume'] = True
    elif family == 'extreme_ask_over_bid_sanity_class':
        out['decision_ignore_extreme_imbalance_class'] = True
    elif family == 'full_ladder_placement':
        if out.get('placement_rule') == 'depth_support':
            out['placement_rule'] = 'touch'
    else:
        raise BenchmarkError(f'unknown ablation family: {family}')
    return out


def ablation_definitions(
    spec: Mapping[str, Any], freeze: Mapping[str, Any],
) -> list[dict[str, Any]]:
    window = freeze.get('selected_window_definition')
    policy = freeze.get('selected_policy_definition')
    if not isinstance(window, dict) or not isinstance(policy, dict):
        raise BenchmarkError('freeze lacks selected Window-1 definitions')
    families = spec.get('feature_ablations') or []
    if not families:
        raise BenchmarkError('candidate spec has no feature ablations')
    return [{
        'candidate_id': (f'{freeze["selected_candidate_id"]}'
                         f'__WITHOUT__{family}'),
        'experiment_kind': 'ablation',
        'window_definition': dict(window),
        'policy_definition': ablated_policy(policy, str(family)),
        'boundary_id': window['boundary_id'],
        'policy_id': policy['policy_id'],
        'feature_removed': str(family),
    } for family in families]


def simulate_event(
    event: Mapping[str, Any],
    candidate: Mapping[str, Any],
    books: Sequence[Mapping[str, Any]],
    prints: Sequence[Mapping[str, Any]],
    period: str,
) -> dict[str, Any]:
    window = candidate['window_definition']
    policy = candidate['policy_definition']
    base = {
        'runner_version': RUNNER_VERSION,
        'benchmark_version': BENCHMARK_VERSION,
        'event_id': event.get('event_id'),
        'candidate_id': candidate['candidate_id'],
        'experiment_kind': candidate['experiment_kind'],
        'boundary_id': candidate['boundary_id'],
        'policy_id': candidate['policy_id'],
        'period': period,
        'window_definition': window,
        'policy_definition': policy,
    }
    if candidate.get('feature_removed'):
        base['feature_removed'] = candidate['feature_removed']
    try:
        scheduled = parse_exchange_ts(event.get('scheduled_start_exchange_ts'),
                                      'scheduled_start_exchange_ts')
        right, edge_source = resolve_window_end(
            event, int(window['schedule_only_corridor_minutes']))
    except BenchmarkError as exc:
        return {**base, 'status': 'error', 'detail': str(exc), 'legs': []}
    left = scheduled - int(window['left_edge_hours_before_schedule']) * 3600
    base['left_edge_exchange_ts'] = left
    base['right_edge_exchange_ts'] = right
    base['right_edge_source'] = edge_source
    legs = event.get('legs')
    if not isinstance(legs, list) or len(legs) != 2:
        return {**base, 'status': 'missing',
                'detail': 'event does not have exactly two normalized legs',
                'legs': []}
    sequence = str(policy.get('sequence_rule') or 'simultaneous')
    delay = max(0, int(policy.get('sibling_delay_seconds', 0)))
    post_times = [left, left]
    if sequence == 'favorite_first':
        favorite = next((index for index, leg in enumerate(legs)
                         if isinstance(leg, dict)
                         and leg.get('role') == 'favorite'), None)
        if favorite is None:
            return {**base, 'status': 'unknown',
                    'detail': 'favorite-first policy lacks causal role label',
                    'legs': []}
        post_times[1 - favorite] = left + delay
    elif sequence != 'simultaneous':
        return {**base, 'status': 'error',
                'detail': f'unknown sequence rule: {sequence}', 'legs': []}
    leg_rows = [simulate_leg(
        str(candidate['candidate_id']), policy, event, leg, books, prints,
        left, right, scheduled, post_times[index])
        for index, leg in enumerate(legs) if isinstance(leg, dict)]
    if len(leg_rows) != 2:
        return {**base, 'status': 'missing',
                'detail': 'leg objects are malformed', 'legs': leg_rows}
    response = str(policy.get('first_fill_response') or 'hold')
    filled = [(index, row) for index, row in enumerate(leg_rows)
              if row.get('status') == 'filled'
              and row.get('completion_exchange_ts') is not None]
    if response in {'reaim_touch', 'reaim_depth_support'} and filled:
        first_index, first_row = min(
            filled, key=lambda item: float(item[1]['completion_exchange_ts']))
        sibling_index = 1 - first_index
        if leg_rows[sibling_index].get('status') == 'not_filled':
            response_policy = dict(policy)
            response_policy['placement_rule'] = (
                'touch' if response == 'reaim_touch' else 'depth_support')
            response_policy['max_moves'] = 0
            sibling = legs[sibling_index]
            assert isinstance(sibling, dict)
            leg_rows[sibling_index] = simulate_leg(
                str(candidate['candidate_id']) + '-firstfill', response_policy,
                event, sibling, books, prints, left, right, scheduled,
                float(first_row['completion_exchange_ts']))
            leg_rows[sibling_index]['first_leg_information_used'] = {
                'sibling_leg': first_row.get('leg'),
                'sibling_fill_price_cents': first_row.get('fill_vwap_cents'),
                'sibling_completion_exchange_ts': first_row.get(
                    'completion_exchange_ts'),
            }
    statuses = {str(row.get('status')) for row in leg_rows}
    status = ('unknown' if statuses & {'unknown', 'corrupt', 'error', 'missing'}
              else 'ok')
    return {**base, 'status': status, 'legs': leg_rows}


def run(args: argparse.Namespace) -> int:
    input_dir = Path(args.input_dir).resolve()
    output = Path(args.output).resolve()
    require_validation(Path(args.validation_summary).resolve())
    ledger, ledger_errors = read_jsonl(Path(args.event_ledger).resolve())
    if ledger_errors:
        raise BenchmarkError(f'event ledger errors: {len(ledger_errors)}')
    events, event_errors = read_jsonl(input_dir / 'events.jsonl')
    raw_prints, print_parse_errors = read_jsonl(input_dir / 'prints.jsonl')
    books, book_errors = read_jsonl(input_dir / 'books.jsonl')
    if event_errors or print_parse_errors or book_errors:
        raise BenchmarkError('normalized input contains parse errors')
    prints, print_errors = canonical_true_prints(raw_prints)
    if print_errors:
        raise BenchmarkError(
            f'normalized print contract errors: {len(print_errors)}')
    event_map = {str(row.get('event_id')): row for row in events}
    denominator = [row for row in ledger
                   if row.get('floor_pass') and row.get('period') == args.period]
    spec = load_json(Path(args.candidate_spec).resolve())
    if args.period == 'fit' and args.mode == 'candidates':
        candidates = candidate_definitions(spec)
    elif args.period == 'fit' and args.mode == 'ablations':
        if not args.freeze:
            raise BenchmarkError('--freeze is required for fit ablations')
        freeze = load_json(Path(args.freeze).resolve())
        if freeze.get('holdout_viewed') is True:
            raise BenchmarkError('holdout was already viewed before ablation')
        candidates = ablation_definitions(spec, freeze)
    else:
        if args.mode != 'candidates':
            raise BenchmarkError('holdout supports candidates mode only')
        if output.exists():
            raise BenchmarkError('holdout outcome file already exists')
        if not args.freeze:
            raise BenchmarkError('--freeze is required for holdout')
        freeze = load_json(Path(args.freeze).resolve())
        if not args.holdout_declaration:
            raise BenchmarkError(
                '--holdout-declaration is required before holdout access')
        load_holdout_declaration(
            Path(args.holdout_declaration).resolve(), freeze,
            Path(args.freeze).resolve())
        if freeze.get('holdout_viewed') is True:
            raise BenchmarkError('holdout was already viewed')
        if not freeze.get('selected_window_definition'):
            raise BenchmarkError('freeze lacks selected window definition')
        if not freeze.get('selected_policy_definition'):
            raise BenchmarkError('freeze lacks selected policy definition')
        candidates = [{
            'candidate_id': freeze['selected_candidate_id'],
            'experiment_kind': 'holdout',
            'window_definition': freeze['selected_window_definition'],
            'policy_definition': freeze['selected_policy_definition'],
            'boundary_id': freeze['selected_window_definition']['boundary_id'],
            'policy_id': freeze['selected_policy_definition']['policy_id'],
        }]
    outcomes = []
    for candidate in candidates:
        for ledger_row in denominator:
            event_id = str(ledger_row.get('event_id') or '')
            event = event_map.get(event_id)
            if event is None:
                outcomes.append({
                    'runner_version': RUNNER_VERSION,
                    'event_id': event_id,
                    'candidate_id': candidate['candidate_id'],
                    'experiment_kind': candidate['experiment_kind'],
                    'boundary_id': candidate['boundary_id'],
                    'policy_id': candidate['policy_id'],
                    'period': args.period,
                    'window_definition': candidate['window_definition'],
                    'policy_definition': candidate['policy_definition'],
                    'status': 'missing',
                    'detail': 'ledger event is absent from normalized events',
                    'legs': [],
                })
                continue
            outcomes.append(simulate_event(event, candidate, books, prints,
                                           args.period))
    write_jsonl(output, outcomes)
    receipt = {
        'runner_version': RUNNER_VERSION,
        'period': args.period,
        'denominator_rows': len(denominator),
        'candidates': len(candidates),
        'outcome_rows': len(outcomes),
        'output': str(output),
        'output_sha256': sha256_file(output),
        'window2_or_exit_fields_used': False,
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument('--period', required=True, choices=('fit', 'holdout'))
    root.add_argument('--mode', choices=('candidates', 'ablations'),
                      default='candidates')
    root.add_argument('--input-dir', required=True)
    root.add_argument('--event-ledger', required=True)
    root.add_argument('--validation-summary', required=True)
    root.add_argument('--candidate-spec', required=True)
    root.add_argument('--output', required=True)
    root.add_argument('--freeze')
    root.add_argument('--holdout-declaration')
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return run(args)
    except BenchmarkError as exc:
        print(f'WINDOW1-RUNNER-BLOCKED: {exc}', file=sys.stderr)
        return 4


if __name__ == '__main__':
    raise SystemExit(main())
