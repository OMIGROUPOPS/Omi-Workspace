"""Causal, selected-event inputs for the frozen absorption residual experiment.

Never opens a live store. Unselected JSONL payloads are skipped before decoding.
The FIRST projection reproduces conduct_scoreboard_v2.ReceiptProjector, with
historical member states cached at the exact atlas clocks; no query future grid.
"""
from __future__ import annotations
from collections import defaultdict
from decimal import Decimal
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import numpy as np

import tune_bench_v2_survivorship as reference
from feature_panel_bench import PositivePrintTarget
from feature_panel_run import validate_witness_row
from feature_panel_scoring import weighted_quantile, weighted_crps
from feature_panel_inventory_gate_extract import encoded


BLOCKS = ('API_FLOW', 'PER_LEVEL_MAKER', 'CONSUMED_LEVEL_REFILL',
          'IMBALANCE', 'SPREAD', 'PAIR_GAP')
BASE_FIELDS = ('first_own', 'first_partner', 'log_mtb',
               'role:CLIMBER', 'role:FALLER', 'role:NOT_CALLABLE')


def selected_jsonl(path, events, *, identity='event_id'):
    """No reserved row is JSON-decoded during development; hash scan is separate."""
    pattern = re.compile(rb'"'+identity.encode()+rb'"\s*:\s*"([^"\\]+)"')
    with gzip.open(path, 'rb') as stream:
        for line in stream:
            match = pattern.search(line)
            if match is None:
                raise ValueError('MISSING_SELECTION_IDENTITY:'+identity)
            key = match[1].decode()
            event = key.rsplit('-', 1)[0] if identity == 'ticker' else key
            if event in events:
                yield json.loads(line)


def load_selected_pairs(library, count_path, metadata):
    """Reference Leg adapter, without whole-library taxonomy/outcome scans."""
    count_groups = defaultdict(list)
    for row in selected_jsonl(count_path, metadata, identity='ticker'):
        if set(row) != {'ticker', 'second', 'true_print_count_cum'}:
            raise ValueError('COUNT_SCHEMA_MISMATCH')
        count_groups[row['ticker']].append(row)
    grouped, leg_meta = defaultdict(list), {}
    for row in selected_jsonl(library, metadata):
        event, ticker = row['event_id'], row['ticker']
        meta = metadata[event]
        if row['grain'] != 'TICK' or row['category'] != meta['category']:
            raise ValueError('LIBRARY_GRAIN_CATEGORY_DRIFT')
        day = reference.date_key(event)
        if row['event_date'] != day or '2026-07-11' <= day <= '2026-07-21':
            raise ValueError('DATE_OR_EXAM_COHORT_VIOLATION')
        if row['bell_epoch'] != meta['bell_epoch'] or row['formation_end_epoch'] > meta['formation_epoch']:
            raise ValueError('RESERVATION_SPAN_DRIFT')
        counts = count_groups.pop(ticker)
        seconds = np.asarray([r['second'] for r in counts], dtype=float)
        cumulative = np.asarray([r['true_print_count_cum'] for r in counts], dtype=np.int64)
        if (not len(seconds) or np.any(seconds != np.floor(seconds)) or np.any(np.diff(seconds) <= 0)
                or np.any(np.diff(np.r_[0, cumulative]) <= 0)
                or seconds[0] < math.floor(row['formation_end_epoch']) or seconds[-1] >= row['bell_epoch']
                or cumulative[-1] != row['true_print_count_in_span']):
            raise ValueError('COUNT_SPAN_ORDER_OR_TOTAL_MISMATCH:'+ticker)
        points = row['path']
        ep = np.asarray([p['ts'] for p in points], dtype=float)
        leg = reference.Leg(row['leg_id'], float(row['anchor_cents']), float(row['formation_end_epoch']),
            float(row['bell_epoch']), ep,
            np.asarray([[p[k] for k in ('last_cents', 'bid_cents', 'ask_cents')] for p in points], dtype=float),
            np.asarray([p['volume_cum'] for p in points], dtype=float), seconds,
            np.asarray([p['seen_true_trade_low_cents'] for p in points], dtype=float), None,
            row.get('onset_epoch'), postformation_open=float(row.get('postformation_open_cents', row['anchor_cents'])),
            count_epoch=seconds, print_count_cum=cumulative)
        leg.second_close = leg.count_second_grid = True
        available = np.flatnonzero(np.floor(ep) >= seconds[0])
        if not len(available):
            raise ValueError('NO_NATIVE_STATE_AFTER_FIRST_PRINT')
        leg.first_observation_epoch = ep[available[0]]
        grouped[event].append(leg)
        leg_meta[ticker] = {k: row[k] for k in ('event_id', 'ticker', 'category',
            'formation_end_epoch', 'bell_epoch', 'true_print_count_in_span')}
    if count_groups or set(grouped) != set(metadata):
        raise ValueError('SELECTED_LIBRARY_OR_COUNT_SET_MISMATCH')
    pairs = []
    for event, legs in sorted(grouped.items()):
        if len(legs) != 2 or legs[0].bell != legs[1].bell:
            raise ValueError('SELECTED_PAIR_WITHOUT_TWO_COMMON_CLOCK_LEGS')
        first = max(l.first_observation_epoch for l in legs)
        prices = [l.sample([first])[0, 0] for l in legs]
        if not all(np.isfinite(prices)) or prices[0] == prices[1]:
            raise ValueError('UNORIENTABLE_SELECTED_PAIR')
        ordered = tuple(sorted(legs, key=lambda l: -l.sample([first])[0, 0]))
        pair = reference.Pair(event, metadata[event]['category'], reference.date_key(event), ordered, first, 'TICK')
        if pair.formation != metadata[event]['formation_epoch']:
            raise ValueError('PAIR_FORMATION_DRIFT')
        pairs.append(pair)
    return pairs, leg_meta


def span_hash(pair):
    value = dict(event=pair.event_id, category=pair.category, legs=[dict(leg=l.leg_id,
        formation=float(l.formation).hex(), bell=float(l.bell).hex()) for l in pair.legs])
    return hashlib.sha256(encoded(value)).hexdigest()


class FirstAtlas:
    def __init__(self, members, contract):
        self.members, self.c = members, contract
        self.gates = np.asarray(contract['gates_minutes_to_bell'], dtype=float)
        self.cache = {}

    def member_state(self, member):
        key = (member.event_id, tuple(float(g).hex() for g in self.gates), span_hash(member))
        if key not in self.cache:
            current = member.levels(self.gates)
            floors, times, roles = [], [], []
            for side, leg in enumerate(member.legs):
                ts = leg.bell-self.gates*self.c['minute_seconds']
                last = leg.sample(ts)[:, 0]
                ix = np.searchsorted(leg.epoch, ts, side='right')
                fi = leg.remaining_floor_index[np.minimum(ix, len(leg.epoch)-1)]
                future = leg.values[fi, 0]
                carried = (ix == len(leg.epoch)) | (last <= future)
                floors.append(np.where(carried, last, future))
                times.append(np.where(carried, self.gates, (leg.bell-leg.epoch[fi])/self.c['minute_seconds']))
                drift = current[:, side*3]-leg.open
                roles.append(np.where(drift >= self.c['role_drift_cents'], 'CLIMBER',
                    np.where(drift <= -self.c['role_drift_cents'], 'FALLER', 'NOT_CALLABLE')))
            self.cache[key] = (current, np.asarray(floors).T, np.asarray(times).T, np.asarray(roles).T)
        return self.cache[key]

    def project(self, query):
        members, weights = reference.initial_pool(query, self.members)
        selected = [i for i, g in enumerate(self.gates) if 0 < g <= query.first_mtb]
        own = query.levels(self.gates)
        historical = [self.member_state(m) for m in members]
        first_mtb = np.asarray([m.first_mtb for m in members])
        rows = []
        for gi in selected:
            gate = float(self.gates[gi])
            for side, leg in enumerate(query.legs):
                role = query.roles(gate)[side]
                mask = np.asarray([((r[3][gi, side] == role) or role == 'NOT_CALLABLE')
                    and np.isfinite(r[0][gi, side*3:side*3+3]).all() for r in historical], dtype=bool)
                mask &= first_mtb >= gate
                sw = weights*mask
                ess = float(reference.ess(sw) or 0)
                row = dict(event=query.event_id, date=query.date, month=query.date[:7], category=query.category,
                    formation=query.formation, bell=query.bell, side=side, leg=leg.leg_id,
                    gate=gate, epoch=query.bell-gate*self.c['minute_seconds'], role=role,
                    ess=ess, member_count=int(np.count_nonzero(sw)), q=None, values=[], weights=[],
                    first_own=float(query.first[side*3]), first_partner=float(query.first[(1-side)*3]),
                    book=own[gi, :6].tolist())
                if ess >= self.c['no_call_ess_floor']:
                    atoms = np.asarray([own[gi, side*3]+r[1][gi, side]-r[0][gi, side*3] for r in historical])[mask]
                    mass = sw[mask]
                    if not np.isfinite(atoms).all():
                        raise ValueError('NONFINITE_FIRST_ATOM')
                    # No compression before the reference inverse-CDF calculation.
                    delta = np.asarray([r[1][gi, side]-r[0][gi, side*3] for r in historical])[mask]
                    row.update(q=float(own[gi, side*3]+reference.inverse_weighted_quantile(delta, mass, .5)),
                               values=atoms.tolist(), weights=mass.tolist())
                rows.append(row)
        return rows


def corrected_refill(proof, side, epoch, formation, bell):
    """Recompute consumed-level ratio from existing private gate proof, fail closed."""
    invalid = proof.get('reason') if proof else 'NO_CONSECUTIVE_SNAPSHOTS'
    interval = proof.get('interval') if proof else None
    if not interval or interval[0] < formation or math.floor(interval[1])+1 > epoch or math.floor(interval[1])+1 >= bell:
        invalid = invalid or 'ENDPOINT_NOT_COMPLETELY_OBSERVED_IN_SPAN'
    levels = [r for r in (proof or {}).get('per_level', []) if r['side'] == side]
    consumed = []
    for row in levels:
        amount = row.get('on_book_executed_contracts')
        if amount is None:
            invalid = invalid or 'UNRESOLVED_EXECUTION_ATTRIBUTION_OR_ORDER'
        elif amount > 0:
            if any(row.get(k) is None for k in ('start_displayed_contracts', 'end_displayed_contracts', 'net_displayed_residual')):
                invalid = invalid or 'CONSUMED_LEVEL_NOT_VISIBLE'
            else:
                a, z, net = (Decimal(str(row[k])) for k in ('start_displayed_contracts', 'end_displayed_contracts', 'net_displayed_residual'))
                expected = z-a+Decimal(str(amount))
                if not math.isclose(float(net), float(expected), rel_tol=np.finfo(float).eps*len(row), abs_tol=np.finfo(float).eps*len(row)):
                    raise ValueError('GATE_PROOF_ACCOUNTING_MISMATCH')
                consumed.append((float(net), amount))
    if invalid:
        return dict(status='UNOBSERVED', reason=invalid, value=None)
    denominator = math.fsum(x[1] for x in consumed)
    if not denominator:
        return dict(status='ZERO_DENOMINATOR', reason=None, value=None)
    return dict(status='MEASURED', reason=None, value=math.fsum(max(0, x[0]) for x in consumed)/denominator)


def book_features(pair, row, gate_state, par):
    blocks = {b: {} for b in BLOCKS}
    refill_status = {}
    for relation, side in (('own', row['side']), ('partner', 1-row['side'])):
        leg = pair.legs[side]
        state = gate_state['sides'][leg.leg_id]
        if state['epoch'] != row['epoch']:
            raise ValueError('FEATURE_CLOCK_DRIFT')
        fields = state['features']
        for k in ('taker_flow', 'taker_yes_contracts', 'taker_no_contracts'):
            blocks['API_FLOW'][relation+':'+k] = fields.get(k) if state.get('flow_complete') else None
        for k in ('book_imbalance_top', 'book_imbalance_five', 'book_imbalance_top_change', 'book_imbalance_five_change'):
            blocks['IMBALANCE'][relation+':'+k] = fields.get(k)
        for k in ('behavior_spread_cents', 'spread_rate_per_minute'):
            blocks['SPREAD'][relation+':'+k] = fields.get(k)
        proof = state.get('maker') or {}
        valid_time = bool(proof.get('interval') and proof['interval'][0] >= leg.formation
            and math.floor(proof['interval'][1])+1 <= row['epoch'] and math.floor(proof['interval'][1])+1 < leg.bell)
        for bi, book_side in ((1, 'bid'), (2, 'ask')):
            refill = corrected_refill(proof, book_side, row['epoch'], leg.formation, leg.bell)
            key = relation+':'+book_side
            refill_status[key] = refill
            blocks['CONSUMED_LEVEL_REFILL'][key+':refill'] = refill['value']
            flow_name = 'taker_no_contracts' if book_side == 'bid' else 'taker_yes_contracts'
            flow = blocks['API_FLOW'][relation+':'+flow_name]
            blocks['CONSUMED_LEVEL_REFILL'][key+':pressure_x_refill'] = (
                flow*refill['value'] if flow is not None and refill['value'] is not None else None)
            previous = proof.get('raw_previous_snapshot')
            ranked = sorted((p for p, q in previous[bi] if q is not None and q > 0), reverse=book_side == 'bid') if previous else []
            per_level = {r['yes_price_cents']: r for r in proof.get('per_level', []) if r['side'] == book_side}
            # Rank width is from the recorded capture, not a tuned model cutoff.
            for rank, price in enumerate(ranked):
                item = per_level.get(price, {})
                net = item.get('net_displayed_residual') if valid_time and not proof.get('reason') else None
                name = key+':rank'+str(rank+1)
                blocks['PER_LEVEL_MAKER'][name+':add'] = max(0, net) if net is not None else None
                blocks['PER_LEVEL_MAKER'][name+':pull'] = max(0, -net) if net is not None else None
                blocks['PER_LEVEL_MAKER'][name+':distance'] = item.get('distance_from_price_cents') if net is not None else None
    book = row['book']
    bid, ask, other_bid, other_ask = book[row['side']*3+1], book[row['side']*3+2], book[(1-row['side'])*3+1], book[(1-row['side'])*3+2]
    blocks['PAIR_GAP'].update(partner_bid=other_bid, partner_ask=other_ask,
        paired_bid_sum=bid+other_bid, paired_ask_sum=ask+other_ask,
        paired_arb_gap_maker=par-bid-other_bid, paired_arb_gap_taker=ask+other_ask-par,
        pair_gap_abs=abs((bid+ask+other_bid+other_ask)/len(pair.legs)-par))
    return blocks, refill_status


def prepare_rows(pairs, member_pairs, gate_path, witness_path, leg_meta, contract, par):
    wanted = {p.event_id for p in pairs}
    gate_inputs = {r['event_id']: r for r in selected_jsonl(gate_path, wanted)}
    witnesses = {}
    for r in selected_jsonl(witness_path, wanted):
        ticker = r['ticker']
        meta = leg_meta[ticker]
        for k in ('event_id', 'ticker', 'category', 'formation_end_epoch', 'bell_epoch'):
            if r[k] != meta[k]:
                raise ValueError('WITNESS_IDENTITY_DRIFT')
        validate_witness_row(r, meta)
        witnesses[ticker] = PositivePrintTarget(r['positive_prints'], meta['formation_end_epoch'], meta['bell_epoch'], contract['minute_seconds'])
    projector = FirstAtlas(member_pairs, contract)
    verified_months = set()
    for pair in sorted(pairs, key=lambda p: (p.formation, p.event_id)):
        gates = gate_inputs.pop(pair.event_id)
        if (gates['span_sha256'] != span_hash(pair) or gates['first_epoch'] != pair.first_epoch or gates['bell_epoch'] != pair.bell):
            raise ValueError('GATE_SOURCE_SPAN_DRIFT')
        by_gate = {r['minutes_to_bell']: r for r in gates['states']}
        rows = projector.project(pair)
        if pair.date[:7] not in verified_months:
            # Numerical adapter check only: fixed first game per event month,
            # no target selected and no named tune game read.
            from conduct_scoreboard_v2 import ReceiptProjector
            reference_rows=ReceiptProjector(member_pairs,contract).project(pair,'GATE-SIM')
            reference_states={(r['source_gate_minutes'],leg):s for r in reference_rows for leg,s in r['sides'].items()}
            for row in rows:
                old=reference_states[(row['gate'],row['leg'])]
                if (old['member_count']!=row['member_count'] or old['ess']!=row['ess'] or old['role']!=row['role']
                    or old.get('floors',{}).get('q50',{}).get('level_cents')!=row['q']):
                    raise ValueError('CACHED_FIRST_REFERENCE_DRIFT')
                row['reference_adapter_verified']=True
            verified_months.add(pair.date[:7])
        for row in rows:
            blocks, statuses = book_features(pair, row, by_gate[row['gate']], par)
            row['blocks'], row['refill_status'] = blocks, statuses
            target = witnesses[pair.event_id+'-'+row['leg']].at(row['epoch'])
            row.update(target=target['floor_cents'], target_mtb=target['floor_mtb'])
            row['base_features'] = dict(first_own=row['first_own'], first_partner=row['first_partner'], log_mtb=math.log1p(row['gate']),
                **{'role:'+r: float(row['role'] == r) for r in ('CLIMBER', 'FALLER', 'NOT_CALLABLE')})
            if row['q'] is not None and row['target'] is not None:
                row['first_scores'] = dict(q=row['q'], signed=row['q']-row['target'], mae=abs(row['q']-row['target']),
                    crps=weighted_crps(np.asarray(row['values']), np.asarray(row['weights']), row['target']))
        yield pair.event_id, rows
