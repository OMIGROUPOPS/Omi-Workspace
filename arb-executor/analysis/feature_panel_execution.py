"""Execution-only storage for already validated feature-panel witness rows.

No row is filtered, sorted, rounded, or interpreted here. Numeric payloads use
non-object arrays so the process snapshot can map them read-only on Windows;
Python row/scalar objects are reconstructed only as a consumer requests them.
"""
from __future__ import annotations

from collections.abc import Sequence
import copy
import operator

import numpy as np


class CompactPrintRows(Sequence):
    """Immutable, exact storage for four numeric fields and an optional source.

    Lists and tuples are returned in their original form, as fresh rows. The
    numeric fields accept native Python floats, bools, and integers in the
    signed/unsigned 64-bit range; unsupported values fail rather than coerce.
    The optional fifth field accepts a string or None. Float bit patterns,
    including negative zero and NaNs, and integer precision remain unchanged.
    Slices return ordinary lists of rows, like slicing a witness payload.
    """

    __slots__ = ("_bits", "_kinds", "_source_ids", "_sources", "_tuple_rows")

    def __init__(self, rows):
        count = len(rows)
        bits = np.empty((count, 4), dtype=np.uint64)
        kinds = np.empty((count, 4), dtype=np.uint8)
        source_ids = np.full(count, -2, dtype=np.int32)
        tuple_rows = np.zeros(count, dtype=np.bool_)
        float_bits = bits.view(np.float64)
        signed_bits = bits.view(np.int64)
        sources, source_lookup = [], {}
        for index, row in enumerate(rows):
            if type(row) not in (list, tuple) or len(row) not in (4, 5):
                raise ValueError("UNSUPPORTED_PRINT_ROW_SHAPE:"+str(index))
            tuple_rows[index] = type(row) is tuple
            for column in range(4):
                value = row[column]
                if type(value) is float:
                    kinds[index, column] = 0
                    float_bits[index, column] = value
                elif type(value) is int:
                    if not -(1 << 63) <= value < (1 << 64):
                        raise ValueError("PRINT_INTEGER_OUT_OF_64_BIT_RANGE:"+str(index)+":"+str(column))
                    if value < 0:
                        kinds[index, column] = 2
                        signed_bits[index, column] = value
                    else:
                        kinds[index, column] = 1
                        bits[index, column] = value
                elif type(value) is bool:
                    kinds[index, column] = 3
                    bits[index, column] = value
                else:
                    raise TypeError("UNSUPPORTED_PRINT_NUMERIC_TYPE:"+str(index)+":"+str(column))
            if len(row) == 5:
                source = row[4]
                if source is None:
                    source_ids[index] = -1
                elif type(source) is str:
                    if source not in source_lookup:
                        source_lookup[source] = len(sources)
                        sources.append(source)
                    source_ids[index] = source_lookup[source]
                else:
                    raise TypeError("UNSUPPORTED_PRINT_SOURCE_TYPE:"+str(index))
        self._install(bits, kinds, source_ids, tuple(sources), tuple_rows)

    def _install(self, bits, kinds, source_ids, sources, tuple_rows):
        for value in (bits, kinds, source_ids, tuple_rows):
            value.setflags(write=False)
        for name, value in zip(self.__slots__, (bits, kinds, source_ids, sources, tuple_rows)):
            object.__setattr__(self, name, value)

    def __setattr__(self, name, value):
        raise AttributeError("CompactPrintRows is immutable")

    def __delattr__(self, name):
        raise AttributeError("CompactPrintRows is immutable")

    def __len__(self):
        return len(self._bits)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return [self._row(i) for i in range(*index.indices(len(self)))]
        index = operator.index(index)
        if index < 0:
            index += len(self)
        if index < 0 or index >= len(self):
            raise IndexError("CompactPrintRows index out of range")
        return self._row(index)

    def __iter__(self):
        for index in range(len(self)):
            yield self._row(index)

    def _row(self, index):
        bits = self._bits[index]
        kinds = self._kinds[index]
        floats = bits.view(np.float64)
        signed = bits.view(np.int64)
        row = []
        for column in range(4):
            kind = kinds[column]
            if kind == 0:
                value = float(floats[column])
            elif kind == 1:
                value = int(bits[column])
            elif kind == 2:
                value = int(signed[column])
            else:
                value = bool(bits[column])
            row.append(value)
        source_id = int(self._source_ids[index])
        if source_id != -2:
            row.append(None if source_id == -1 else self._sources[source_id])
        return tuple(row) if self._tuple_rows[index] else row

    def __reduce_ex__(self, protocol):
        return (_restore_print_rows, tuple(getattr(self, name) for name in self.__slots__))


def _restore_print_rows(bits, kinds, source_ids, sources, tuple_rows):
    """Restore regular pickle or shared-array snapshots without copying arrays."""
    rows = object.__new__(CompactPrintRows)
    rows._install(bits, kinds, source_ids, sources, tuple_rows)
    return rows


def compact_sampler_copy(sampler):
    """Copy execution metadata and compact witness aliases, leaving input intact.

    Source and witness records are shallow copies. Non-null prints and
    positive_prints payloads become compact sequences, retaining their aliases.
    Prepared sources can discard redundant raw OI and odds-poll payloads; all
    other fields and caches remain. Metadata is restricted to these source and
    witness keys, but the sampler's original global codebooks are retained.
    """
    result = copy.copy(sampler)
    payloads, records, mappings = {}, {}, {}

    def compact_payload(rows):
        if rows is None or isinstance(rows, CompactPrintRows):
            return rows
        identity = id(rows)
        if identity not in payloads:
            payloads[identity] = CompactPrintRows(rows)
        return payloads[identity]

    def copy_mapping(mapping):
        identity = id(mapping)
        if identity not in mappings:
            copied = copy.copy(mapping)
            mappings[identity] = copied
            for key, record in mapping.items():
                record_id = id(record)
                if record_id not in records:
                    changed = copy.copy(record)
                    for field in ("prints", "positive_prints"):
                        if field in record:
                            changed[field] = compact_payload(record[field])
                    records[record_id] = changed
                copied[key] = records[record_id]
        return mappings[identity]

    result.sources = copy_mapping(sampler.sources)
    result.witnesses = copy_mapping(sampler.witnesses)
    for source in result.sources.values():
        # prepare_sources skips its raw conversion once minute_features is a
        # dict. After validation/preparation, sampling and diagnostic readers
        # use only open_interest and odds_snapshot_epochs (feature_panel.py).
        if not isinstance(source.get("minute_features"), dict):
            continue
        interest = source.get("open_interest")
        if (isinstance(interest, dict) and isinstance(interest.get("__epochs__"), np.ndarray)
                and isinstance(interest.get("__columns__"), dict)
                and all(isinstance(interest["__columns__"].get(key), np.ndarray)
                        for key in ("open_interest", "open_interest_delta"))):
            source.pop("oi", None)
        snapshots = source.get("odds_snapshot_epochs")
        if (isinstance(snapshots, np.ndarray)
                or ("odds_snapshot_epochs" in source and snapshots is None
                    and source.get("odds_status") == "NOT_EXTRACTED")):
            source.pop("odds_poll_epochs", None)
    retained = result.sources.keys() | result.witnesses.keys()
    result.metadata = {key: value for key, value in sampler.metadata.items() if key in retained}
    return result
