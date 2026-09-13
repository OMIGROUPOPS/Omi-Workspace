"""Opt-in eleven-block gate screen; v1 engine, features and reports stay intact.

Only authoritative recovered flow replaces B3's original direction fields.
Arithmetic is diagnostic, never a flow fallback. Queue references unchanged
FIRST under the SAME member-library freeze as the active projector.
"""
from __future__ import annotations

from contextlib import contextmanager, ExitStack
from dataclasses import replace
import gzip
import hashlib
import json
import math
from pathlib import Path
import struct
from unittest.mock import patch

import numpy as np

import feature_panel as panel
import feature_panel_atlas as atlas
import feature_panel_atlas_run as screen
import feature_panel_bench as bench
import feature_panel_inventory_features as features
import feature_panel_report as report
import feature_panel_run as launcher
from feature_panel_book_recovery import visible_depth, usable_book


BASE_FIELDS = panel.FIELDS
BASE_SAMPLER = bench.DirectFeatureSampler
BASE_PROJECTOR = bench.FeatureProjector
BASE_FIT = bench.fit_outer_month
BASE_CATEGORY = bench.run_category
BASE_DIAGNOSTICS = atlas.write_atlas_diagnostics
FLOW_FIELDS = ('taker_flow', 'taker_yes_contracts', 'taker_no_contracts')
QUEUE_FIELDS = ('displayed_depth_at_first_q', 'queue_decay_per_minute')
BLOCKS = panel.BLOCKS + features.ADDED_BLOCKS
INPUT_FIELDS = FLOW_FIELDS + tuple(name for name, _, _ in features.NEW_FIELDS if name not in QUEUE_FIELDS)


def field_registry():
    changed = []
    for field in BASE_FIELDS:
        if field.name in FLOW_FIELDS:
            field = replace(field, source='Exact-ID matched Kalshi authoritative on-book trade direction',
                exclusion='Arithmetic never substitutes. Off-book excluded; any unresolved on-book positive print makes completed-minute flow missing.')
        changed.append(field)
    changed.extend(panel.Field(name, block, 'Hash-bound amended recovery at exact atlas clock', definition)
                   for name, block, definition in features.NEW_FIELDS)
    return tuple(changed)


def exact_gate(gate):
    if not math.isfinite(float(gate)):
        raise ValueError('NONFINITE_GATE')
    return struct.pack('>d', float(gate))


def universe_hash(pairs):
    return hashlib.sha256(json.dumps(sorted((p.event_id, atlas.span_hash(p)) for p in pairs),
        separators=(',', ':')).encode()).hexdigest()


class GateInputs:
    """One derived row per pair; absent rows/fields are errors, explicit null isn't."""
    def __init__(self, rows, receipt, contract, library_sha256):
        if (receipt.get('schema') != 'FEATURE_INVENTORY_GATE_INPUTS_V2'
                or receipt.get('status') != 'VERIFIED' or receipt.get('complete') is not True
                or receipt.get('library_sha256') != library_sha256
                or receipt.get('gates_minutes_to_bell') != contract['gates_minutes_to_bell']):
            raise ValueError('INVENTORY_INPUT_CONTRACT_MISMATCH')
        self.receipt, self.rows, self.spans = receipt, {}, {}
        self._seconds = contract['minute_seconds']
        expected = [exact_gate(g) for g in contract['gates_minutes_to_bell']]
        for row in rows:
            event = row['event_id']
            if event in self.rows:
                raise ValueError('DUPLICATE_INVENTORY_PAIR:'+event)
            states = row['states']
            keys = [exact_gate(s['minutes_to_bell']) for s in states]
            if keys != expected:
                raise ValueError('INVENTORY_GATE_GRID_MISMATCH:'+event)
            for state in states:
                for leg_id, side in state['sides'].items():
                    missing = set(INPUT_FIELDS)-set(side['features'])
                    if missing:
                        raise ValueError('INVENTORY_FIELDS_MISSING:'+event+':'+leg_id+':'+','.join(sorted(missing)))
                    if any(value is not None and (not isinstance(value, (int, float)) or not math.isfinite(value))
                           for name, value in side['features'].items() if name in INPUT_FIELDS):
                        raise ValueError('INVENTORY_VALUE_NOT_FINITE_OR_NULL')
            self.rows[event] = (row, dict(zip(keys, states)))
        if receipt.get('output', {}).get('rows') != len(self.rows):
            raise ValueError('INVENTORY_ROW_COUNT_MISMATCH')

    @classmethod
    def read(cls, path, receipt_path, contract, library_sha256):
        receipt = launcher.json_file(receipt_path)
        launcher.check_file(path, receipt['output'], 'amended exact-gate inputs')
        return cls(launcher.jsonl(path), receipt, contract, library_sha256)

    def at(self, pair, gate):
        if pair.event_id not in self.rows:
            raise ValueError('INVENTORY_PAIR_MISSING:'+pair.event_id)
        row, states = self.rows[pair.event_id]
        identity = id(pair)
        if identity not in self.spans:
            self.spans[identity] = (pair, atlas.span_hash(pair))
        if row['span_sha256'] != self.spans[identity][1] or row['category'] != pair.category:
            raise ValueError('INVENTORY_PAIR_SPAN_MISMATCH:'+pair.event_id)
        key = exact_gate(gate)
        if key not in states:
            raise ValueError('NON_ATLAS_INVENTORY_LOOKUP:'+pair.event_id)
        state = states[key]
        if set(state['sides']) != {leg.leg_id for leg in pair.legs}:
            raise ValueError('INVENTORY_LEG_SET_MISMATCH')
        epoch = pair.bell-float(gate)*self.contract_seconds
        for side in state['sides'].values():
            if side['epoch'] != epoch:
                raise ValueError('INVENTORY_RECEIPT_CLOCK_MISMATCH')
            previous = side['previous_receipt_epoch']
            if previous is not None and previous >= epoch:
                raise ValueError('INVENTORY_PREVIOUS_CLOCK_NOT_CAUSAL')
            for name, cutoff in (('book_current', epoch), ('book_previous', previous)):
                book = side.get(name)
                if book is not None and (cutoff is None or book[0] > cutoff):
                    raise ValueError('INVENTORY_FUTURE_BOOK:'+name)
        return state

    @property
    def contract_seconds(self):
        return self._seconds

    def bind_contract(self, contract):
        self._seconds = contract['minute_seconds']
        return self


class FirstQueueReference:
    """No candidate-model Q; per-member own FIRST reference, exact universe key."""
    def __init__(self, contract):
        self.contract, self.rows, self.bindings = contract, {}, {}
        self.scopes = {}

    def scope(self, members):
        key = id(members)
        if key not in self.scopes:
            # Retain the list so Python cannot reuse its identity. Universe
            # lists are immutable for an active fold/stream.
            self.scopes[key] = (members, universe_hash(members))
        return self.scopes[key][1]

    def levels(self, pair, gate, members):
        scope = self.scope(members)
        if scope not in self.bindings:
            self.bindings[scope] = dict(member_library_pairs=len(members),
                member_library_sha256=scope, latest_member_bell=max((p.bell for p in members), default=None))
        key = (scope, pair.event_id, atlas.span_hash(pair))
        if key not in self.rows:
            reference = bench.cv2.ReceiptProjector(members, self.contract).project(pair, 'GATE-SIM')
            self.rows[key] = {exact_gate(row['source_gate_minutes']):
                {leg: state.get('floors', {}).get('q50', {}).get('level_cents')
                 for leg, state in row['sides'].items()} for row in reference}
        return self.rows[key].get(exact_gate(gate), {})


def queue_values(state, q, seconds):
    current, previous = state.get('book_current'), state.get('book_previous')
    depth = visible_depth(current[1], q, 'bid') if usable_book(current) and features.finite(q) else None
    prior = visible_depth(previous[1], q, 'bid') if usable_book(previous) and features.finite(q) else None
    delta = features.difference(prior, depth)
    previous_epoch = state['previous_receipt_epoch']
    minutes = (state['epoch']-previous_epoch)/seconds if previous_epoch is not None else None
    return dict(displayed_depth_at_first_q=float(depth) if depth is not None else None,
        queue_decay_per_minute=features.rate(float(delta) if delta is not None else None, minutes))


def sampler_type(inputs, source_scope, maximum_bytes):
    class InventorySampler(BASE_SAMPLER):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.inputs = inputs.bind_contract(self.contract)
            self.reference = FirstQueueReference(self.contract)
            self.all_pairs = None
            self.reference_members = None
            self.state_cache = atlas.ExactStateCache(None, source_scope, maximum_bytes)

        @contextmanager
        def use_library(self, members):
            old = self.reference_members
            self.reference_members = members
            try:
                yield
            finally:
                self.reference_members = old

        def sample(self, pair, gates):
            members = self.reference_members if self.reference_members is not None else self.all_pairs
            if members is None:
                raise ValueError('QUEUE_REFERENCE_UNIVERSE_UNBOUND')
            self.state_cache.scope = source_scope+':'+self.reference.scope(members)
            self.state_cache.sample_raw = lambda p, g: self.sample_raw(p, g, members)
            return self.state_cache.sample(pair, gates)

        def sample_raw(self, pair, gates, members):
            matrix = BASE_SAMPLER.sample(self, pair, gates)
            seconds = self.contract['minute_seconds']
            for index, gate in enumerate(gates):
                state = self.inputs.at(pair, gate)
                # Validation still occurs before returning pre-first missing states.
                if pair.bell-float(gate)*seconds < pair.first_epoch:
                    continue
                reference = self.reference.levels(pair, gate, members)
                for side, leg in enumerate(pair.legs):
                    row = state['sides'][leg.leg_id]
                    values = {name: row['features'][name] for name in INPUT_FIELDS}
                    values.update(queue_values(row, reference.get(leg.leg_id), seconds))
                    for name, value in values.items():
                        matrix[index, side, panel.FEATURE_INDEX[name]] = np.nan if value is None else value
                    flow = matrix[index, side, panel.FEATURE_INDEX['taker_flow']]
                    no = matrix[index, side, panel.FEATURE_INDEX['taker_no_contracts']]
                    velocity = matrix[index, side, panel.FEATURE_INDEX['bid_consumption_velocity']]
                    matrix[index, side, panel.FEATURE_INDEX['pressure_x_bid_response']] = flow*velocity
                    source = self.sources[pair.event_id+'-'+leg.leg_id]
                    end = math.floor(row['epoch']/seconds)*seconds
                    clocks = np.nextafter(np.asarray([end-seconds, end]), -np.inf)
                    depths = panel.source_column(source.get('books', []), 'bid_depth_5', clocks)
                    change = depths[1]-depths[0] if end-seconds >= leg.formation else np.nan
                    matrix[index, side, panel.FEATURE_INDEX['sell_pressure_x_replenishment']] = no*change
            return matrix
    return InventorySampler


class InventoryProjector(BASE_PROJECTOR):
    def receipts(self, query, mode='GATE-SIM'):
        with self.sampler.use_library(self.members):
            yield from super().receipts(query, 'GATE-SIM')


def required_variants(receipt):
    blocks = list(dict.fromkeys(f['block'] for f in receipt['fields'] if f.get('block') is not None))
    if blocks != list(BLOCKS):
        raise ValueError('REQUIRE_EXACT_ELEVEN_BLOCK_REGISTRY')
    expected = [dict(name=v.name, blocks=list(v.blocks)) for v in bench.variant_registry(blocks)]
    if receipt.get('variants') != expected:
        raise ValueError('INCOMPLETE_ELEVEN_BLOCK_VARIANTS')
    return expected


def diagnostics(output_dir, query, frozen, sampler, stream, scale_proof):
    members = sampler.all_pairs
    if stream == 'STRICT_HOLDOUT':
        heldout = set(frozen.receipt['heldout_months'])
        members = [p for p in members if p.bell < frozen.cutoff and p.date[:7] not in heldout]
    base_build = panel.build_pair_panel
    def enriched(*args, **kwargs):
        data = base_build(*args, **kwargs)
        with sampler.use_library(members):
            data['values'] = sampler.sample(query, data['gates'])
        for side, leg in enumerate(query.legs):
            data['coverage'][leg.leg_id]['fields'].update({name: int(np.isfinite(data['values'][:, side, index]).sum())
                for name, index in panel.FEATURE_INDEX.items()})
        return data
    # Cached numeric sampling calls build_pair_panel(values_only=True); don't
    # recurse into this diagnostic-only wrapper.
    def dispatcher(*args, **kwargs):
        return base_build(*args, **kwargs) if kwargs.get('values_only') else enriched(*args, **kwargs)
    with patch.object(panel, 'build_pair_panel', dispatcher):
        return BASE_DIAGNOSTICS(output_dir, query, frozen, sampler, stream, scale_proof)


@contextmanager
def registry_adapter():
    fields = field_registry()
    model_names = tuple(f.name for f in fields if f.block is not None)
    with ExitStack() as stack:
        for name, value in dict(FIELDS=fields, BLOCKS=BLOCKS, FIELD_NAMES=tuple(f.name for f in fields),
                MODEL_FIELDS=model_names, FEATURE_INDEX={name:i for i,name in enumerate(model_names)}).items():
            stack.enter_context(patch.object(panel, name, value))
        stack.enter_context(patch.object(report, 'required_variants', required_variants))
        yield


@contextmanager
def adapter(inputs, source_scope):
    def make_sampler(scope, maximum_bytes):
        return sampler_type(inputs, source_scope+':'+scope, maximum_bytes)

    def category(pairs, sampler, *args, **kwargs):
        sampler.all_pairs = pairs
        if {p.event_id for p in pairs}-set(inputs.rows):
            raise ValueError('INVENTORY_MISSING_FULL_CATEGORY')
        receipt, board = BASE_CATEGORY(pairs, sampler, *args, **kwargs)
        receipt['queue_reference_bindings'] = list(sampler.reference.bindings.values())
        receipt['inventory_schema'] = 'FEATURE_PANEL_INVENTORY_ATLAS_V2'
        return receipt, board

    def fit(plan, pairs, sampler, *args, **kwargs):
        members = [p for p in pairs if p.date[:7] not in set(kwargs['heldout_months'])]
        with sampler.use_library(members):
            return BASE_FIT(plan, pairs, sampler, *args, **kwargs)

    with registry_adapter(), \
         patch.object(atlas, 'cached_sampler_type', make_sampler), \
         patch.object(atlas, 'AtlasProjector', InventoryProjector), \
         patch.object(atlas, 'write_atlas_diagnostics', diagnostics), \
         patch.object(bench, 'run_category', category), \
         patch.object(bench, 'fit_outer_month', fit):
        yield
