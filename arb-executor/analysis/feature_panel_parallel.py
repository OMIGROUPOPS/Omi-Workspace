"""Execution-only ordered process workers for the feature-panel benchmark.

Workers score independent queries, never fit models or reduce population
statistics. The parent replays every scored receipt in the original serial
order. Private journals are bounded by the worker count and are not artifacts.
Numeric source arrays share one read-only packed mapping per snapshot on
Windows; object metadata is pickled once, not sent with every query.
"""
from __future__ import annotations

from collections import deque
from concurrent.futures import ProcessPoolExecutor
import gzip
import hashlib
import os
from pathlib import Path
import pickle
import tempfile
import time

import numpy as np

import feature_panel_execution as execution
import feature_panel_scoring as scoring


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class _ArrayPickler(pickle.Pickler):
    def __init__(self, stream, arrays):
        super().__init__(stream, protocol=pickle.HIGHEST_PROTOCOL)
        self.arrays, self.seen = arrays, {}

    def persistent_id(self, value):
        if not isinstance(value, np.ndarray) or value.dtype.hasobject:
            return None
        identity = id(value)
        if identity not in self.seen:
            offset = self.arrays.tell()
            # Preserve strides as well as values: changing C/F layout can
            # change a NumPy reduction's floating-point addition order.
            low = sum(min(0, (n-1)*stride) for n, stride in zip(value.shape, value.strides))
            high = sum(max(0, (n-1)*stride) for n, stride in zip(value.shape, value.strides))
            extent = high-low+value.dtype.itemsize if value.size else 0
            packed = np.zeros(extent, dtype=np.uint8)
            if extent:
                view = np.ndarray(value.shape, dtype=value.dtype, buffer=packed,
                    offset=-low, strides=value.strides)
                view[...] = value
            packed.tofile(self.arrays)
            dtype = value.dtype.descr if value.dtype.fields else value.dtype.str
            self.seen[identity] = ("READ_ONLY_ARRAY_V2", len(self.seen), offset, dtype,
                                   value.shape, value.strides, -low if extent else 0)
        return self.seen[identity]


class _ArrayUnpickler(pickle.Unpickler):
    def __init__(self, stream, arrays):
        super().__init__(stream)
        self.arrays = np.memmap(arrays, mode="r", dtype=np.uint8) if Path(arrays).stat().st_size else None
        self.loaded = {}

    def persistent_load(self, identity):
        if not isinstance(identity, tuple) or len(identity) != 7 or identity[0] != "READ_ONLY_ARRAY_V2":
            raise pickle.UnpicklingError("UNKNOWN_SHARED_ARRAY_REFERENCE")
        _, key, offset, dtype, shape, strides, anchor = identity
        if key not in self.loaded:
            dtype = np.dtype(dtype)
            if any(x == 0 for x in shape):
                value = np.empty(shape, dtype=dtype)
            else:
                value = np.ndarray(shape, dtype=dtype, buffer=self.arrays, offset=offset+anchor, strides=strides)
            value.setflags(write=False)
            self.loaded[key] = value
        return self.loaded[key]


def write_shared_snapshot(value, prefix):
    """Private, locally generated pickle only; never accepts an external pickle."""
    prefix = Path(prefix)
    data, arrays = prefix.with_suffix(".pickle"), prefix.with_suffix(".arrays")
    if data.exists() or arrays.exists():
        raise ValueError("SHARED_SNAPSHOT_ALREADY_EXISTS")
    data_tmp, arrays_tmp = Path(str(data)+".partial"), Path(str(arrays)+".partial")
    with data_tmp.open("wb") as stream, arrays_tmp.open("wb") as packed:
        _ArrayPickler(stream, packed).dump(value)
    os.replace(arrays_tmp, arrays)
    os.replace(data_tmp, data)
    return dict(data=str(data), arrays=str(arrays), data_sha256=file_sha256(data),
                arrays_sha256=file_sha256(arrays))


def load_shared_snapshot(proof):
    # Paths are created by this execution, not user/source pickle files.
    for key in ("data", "arrays"):
        if file_sha256(proof[key]) != proof[key+"_sha256"]:
            raise ValueError("SHARED_SNAPSHOT_HASH_MISMATCH:"+key)
    with Path(proof["data"]).open("rb") as stream:
        return _ArrayUnpickler(stream, proof["arrays"]).load()


def scorer_channels(baseline, variants):
    common = dict(identity_mode="contiguous_event", common_variant_metrics=False, metric_profile="core")
    return {
        "all": scoring.FeaturePanelScorer(baseline, variants,
            groupings=(("category", "stream"), ("category", "stream", "month"),
                       ("category", "stream", "month", "side")), authorization_streams=(), **common),
        "gates": scoring.FeaturePanelScorer(baseline, variants,
            groupings=(("category", "stream", "side", "gate"),), authorization_streams=(), **common),
        "filed": scoring.FeaturePanelScorer(baseline, variants,
            groupings=(("category", "stream", "side", "gate"),),
            authorization_streams=("PRIMARY_FILED_SCORABLE_GATES", "STRICT_HOLDOUT_FILED_SCORABLE_GATES"), **common),
    }


class _JournalScorer:
    def __init__(self, name, scorer, stream):
        self.name, self.scorer, self.stream = name, scorer, stream

    def add_receipt(self, identity, targets, forecasts, *, eligible=True):
        row = self.scorer.prepare_receipt(identity, targets, forecasts, eligible=eligible)
        # One independent frame avoids an ever-growing pickle memo. Within a
        # receipt, equal forecast aliases still share the already-scored row.
        pickle.dump(("receipt", self.name, row), self.stream, protocol=pickle.HIGHEST_PROTOCOL)

    def add_conduct_event(self, identity, results):
        pickle.dump(("conduct", self.name, identity, results), self.stream, protocol=pickle.HIGHEST_PROTOCOL)


_WORKER_DATA = None
_WORKER_MODELS = None
_WORKER_FAMILY_CACHE = None


def init_worker(snapshot):
    global _WORKER_DATA, _WORKER_MODELS, _WORKER_FAMILY_CACHE
    _WORKER_DATA = load_shared_snapshot(snapshot)
    _WORKER_DATA["lookup"] = {p.event_id: p for p in _WORKER_DATA["pairs"]}
    _WORKER_MODELS, _WORKER_FAMILY_CACHE = {}, {}


def worker_query(task):
    """Only this query writes its NPZ and private atomic journal."""
    import feature_panel_bench as bench
    data = _WORKER_DATA
    if data is None:
        raise RuntimeError("QUERY_WORKER_NOT_INITIALIZED")
    started = time.monotonic()
    model_key = task["model"]["data"]
    if model_key not in _WORKER_MODELS:
        # A worker never needs old month's mapped scales after a month barrier.
        _WORKER_MODELS.clear()
        _WORKER_MODELS[model_key] = load_shared_snapshot(task["model"])
    frozen, scale_proof = _WORKER_MODELS[model_key]
    query = data["lookup"][task["event_id"]]
    cutoff = task["library_cutoff"]
    library = data["pairs"] if cutoff is None else [p for p in data["pairs"]
        if p.bell < cutoff and p.date[:7] not in set(data["heldout_months"])]
    projector = bench.FeatureProjector(library, data["sampler"], data["baseline"]["organ_contract"],
        frozen.kernel, batch_size=data["batch_size"])
    journal, partial = Path(task["journal"]), Path(task["journal"]+".partial")
    if journal.exists() or partial.exists():
        raise ValueError("QUERY_JOURNAL_ALREADY_EXISTS")
    identity = (query.event_id, task["stream"], frozen.month)
    with partial.open("wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", compresslevel=1, mtime=0) as output:
        pickle.dump(("header", identity), output, protocol=pickle.HIGHEST_PROTOCOL)
        channels = {name: _JournalScorer(name, scorer, output)
                    for name, scorer in scorer_channels(data["baseline"], [v.name for v in data["registry"]]).items()}
        result = bench.evaluate_query(query, projector, frozen, data["registry"], channels["all"],
            data["pairs"], data["sampler"].witnesses, data["conduct_spec"], data["heldout_months"],
            stream=task["stream"], family_cache=_WORKER_FAMILY_CACHE, frozen_library_cutoff=cutoff,
            gate_scorer=channels["gates"], filed_gate_scorer=channels["filed"])
        diagnostic = bench.write_query_diagnostics(data["output_dir"], query, frozen,
            data["sampler"], task["stream"], scale_proof)
        result["receipt_diagnostics"] = diagnostic["path"]
        pickle.dump(("complete", identity), output, protocol=pickle.HIGHEST_PROTOCOL)
    os.replace(partial, journal)
    return dict(result=result, diagnostic=diagnostic, journal=str(journal),
        journal_sha256=file_sha256(journal), identity=identity,
        worker_pid=os.getpid(), query_seconds=time.monotonic()-started)


def replay_journal(result, channels):
    path = Path(result["journal"])
    if file_sha256(path) != result["journal_sha256"]:
        raise ValueError("QUERY_JOURNAL_HASH_MISMATCH")
    completed = False
    with gzip.open(path, "rb") as stream:
        if pickle.load(stream) != ("header", result["identity"]):
            raise ValueError("QUERY_JOURNAL_IDENTITY_MISMATCH")
        while True:
            try:
                row = pickle.load(stream)
            except EOFError:
                if not completed:
                    raise ValueError("INCOMPLETE_QUERY_JOURNAL")
                break
            if completed:
                raise ValueError("QUERY_JOURNAL_TRAILING_RECORD")
            if row[0] == "receipt":
                channels[row[1]].apply_prepared_receipt(row[2])
            elif row[0] == "conduct":
                channels[row[1]].add_conduct_event(row[2], row[3])
            elif row == ("complete", result["identity"]):
                completed = True
            else:
                raise ValueError("UNKNOWN_QUERY_JOURNAL_RECORD")


def ordered_bounded_map(executor, function, tasks, limit):
    """Original task order, at most `limit` submitted futures/journals at once."""
    if limit <= 0:
        raise ValueError("POSITIVE_INFLIGHT_LIMIT_REQUIRED")
    tasks, pending = iter(tasks), deque()
    for _ in range(limit):
        task = next(tasks, None)
        if task is None:
            break
        pending.append(executor.submit(function, task))
    try:
        while pending:
            yield pending.popleft().result()
            task = next(tasks, None)
            if task is not None:
                pending.append(executor.submit(function, task))
    finally:
        for future in pending:
            future.cancel()


class QueryPool:
    def __init__(self, pairs, sampler, baseline, conduct_spec, registry, heldout_months,
                 batch_size, output_dir, workers):
        if workers <= 0:
            raise ValueError("POSITIVE_WORKER_COUNT_REQUIRED")
        self.workers = workers
        self.output_dir = Path(output_dir).resolve(strict=True)
        self.private = Path(tempfile.mkdtemp(prefix=".feature-workers-", dir=self.output_dir.parent)).resolve(strict=True)
        self.models, self.executor = {}, None
        # These existing pure caches otherwise get rebuilt separately in every
        # child. Snapshot their exact values into the read-only array mapping.
        for pair in pairs:
            _ = pair._cache, pair._grid, pair.first
            for leg in pair.legs:
                _ = leg.remaining_floor_index
        self.snapshot = write_shared_snapshot(dict(pairs=pairs, sampler=execution.compact_sampler_copy(sampler), baseline=baseline,
            conduct_spec=conduct_spec, registry=registry, heldout_months=tuple(heldout_months),
            batch_size=batch_size, output_dir=str(self.output_dir)), self.private/"context")

    def evaluate(self, queries, frozen, scale_proof, stream, library_cutoff, channels):
        if frozen.month not in self.models:
            self.models[frozen.month] = write_shared_snapshot((frozen, scale_proof), self.private/("model_"+frozen.month))
        if self.executor is None:
            self.executor = ProcessPoolExecutor(max_workers=self.workers, initializer=init_worker,
                initargs=(self.snapshot,))
        tasks = (dict(event_id=query.event_id, stream=stream, model=self.models[frozen.month],
            library_cutoff=library_cutoff,
            journal=str(self.private/(query.event_id+"__"+stream+".journal.gz"))) for query in queries)
        for result in ordered_bounded_map(self.executor, worker_query, tasks, self.workers):
            replay_journal(result, channels)
            path = Path(result["journal"]).resolve(strict=True)
            if path.parent != self.private:
                raise ValueError("QUERY_JOURNAL_OUTSIDE_PRIVATE_DIRECTORY")
            path.unlink()
            yield result

    def close(self, *, success=False):
        if self.executor is not None:
            self.executor.shutdown(wait=True, cancel_futures=True)
            self.executor = None
        if success:
            # Workers have exited and released their Windows mappings. Remove
            # only known files created by this execution, never recurse.
            for proof in [self.snapshot, *self.models.values()]:
                for key in ("data", "arrays"):
                    path = Path(proof[key]).resolve(strict=True)
                    if path.parent != self.private:
                        raise ValueError("SNAPSHOT_OUTSIDE_PRIVATE_DIRECTORY")
                    path.unlink()
            self.private.rmdir()  # Unexpected/partial files prevent removal.
        # Failure retains this execution's snapshots/partial journals outside
        # the artifact tree for diagnosis; they never enter Git or parity.

    def __enter__(self):
        return self

    def __exit__(self, exception_type, *_):
        self.close(success=exception_type is None)
