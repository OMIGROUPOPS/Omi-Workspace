"""Bounded, private execution checkpoints for the feature-panel benchmark.

The parent applies prepared receipts in their original serial order, then
commits its exact scorer objects after each evaluation. Restoring those objects
preserves every accumulator bit and identity guard; no partial sums are merged.
One current snapshot and one in-progress replacement bound storage independently
of receipt count. Results/diagnostics and the completed ordered prefix belong in
the state. Immutable fitted models are retained separately.

This is a single-writer store for locally produced trusted pickles, never an
import format. SHA256 detects damaged/inconsistent files; it does not make an
untrusted pickle safe. The caller binds sources, code and protocol and excludes
execution-only worker counts. Keep the directory outside scientific artifacts.
"""
from __future__ import annotations

from collections import defaultdict
import copyreg
import gzip
import hashlib
import json
import os
from pathlib import Path
import pickle
import re
import shutil
import sys
import uuid

import numpy as np

import feature_panel_scoring as scoring


SCHEMA = "FEATURE_PANEL_EXACT_CHECKPOINT_V1"
_BLOB_NAME = re.compile(r"(?:state|model)-[0-9a-f]{32}\.pickle\.gz(?:\.partial)?\Z")
_MANIFEST_PARTIAL = re.compile(r"manifest-[0-9a-f]{32}\.json\.partial\Z")


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def _moments_triple():
    return scoring._Moments(), scoring._Moments(), scoring._Moments()


def _reduce_defaultdict(value):
    factory = value.default_factory
    if (getattr(factory, "__module__", None) == scoring.__name__
            and getattr(factory, "__qualname__", None) == "_Matched.__init__.<locals>.<lambda>"):
        # The sole local factory in the bound scorer. Replacing the factory,
        # not its existing values, leaves floating-point totals untouched.
        factory = _moments_triple
    return defaultdict, (factory,), None, None, iter(value.items())


class _CheckpointPickler(pickle.Pickler):
    dispatch_table = dict(copyreg.dispatch_table)
    dispatch_table[defaultdict] = _reduce_defaultdict


def _fsync_directory(directory):
    # Windows does not expose directory fsync through Python. File contents
    # are flushed before every atomic replace on both platforms.
    if os.name != "nt":
        descriptor = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def _atomic_replace(source, target):
    os.replace(source, target)
    _fsync_directory(Path(target).parent)


class _BudgetWriter:
    def __init__(self, stream, available):
        self.stream, self.remaining = stream, available

    def write(self, data):
        if len(data) > self.remaining:
            raise OSError("CHECKPOINT_DISK_BUDGET_EXCEEDED")
        written = self.stream.write(data)
        self.remaining -= written
        return written

    def flush(self):
        self.stream.flush()


class CheckpointStore:
    """Atomic rolling state with strict binding and exclusive writer ownership.

    ``binding`` must contain nonempty ``source_registry``, ``code_sha256`` and
    ``protocol`` values. Its complete JSON value must match on resume. Worker
    counts should not be included. ``output_dir`` additionally binds the exact
    resolved artifact location and rejects checkpoint storage beneath it.

    ``max_bytes`` optionally caps all files in this directory, including the
    old and new generation during a commit. Exhaustion preserves the last
    committed generation and aborts explicitly. ``min_free_bytes`` is an
    optional execution resource reserve, not a scientific parameter.
    """

    def __init__(self, directory, binding, *, max_bytes=None,
                 min_free_bytes=0, output_dir=None):
        if not isinstance(binding, dict) or any(not binding.get(key)
                for key in ("source_registry", "code_sha256", "protocol")):
            raise ValueError("CHECKPOINT_SOURCE_CODE_PROTOCOL_BINDING_REQUIRED")
        if max_bytes is not None and (isinstance(max_bytes, bool) or max_bytes <= 0):
            raise ValueError("POSITIVE_CHECKPOINT_BYTE_BUDGET_REQUIRED")
        if isinstance(min_free_bytes, bool) or min_free_bytes < 0:
            raise ValueError("NONNEGATIVE_CHECKPOINT_FREE_RESERVE_REQUIRED")
        self.directory = Path(directory).resolve()
        self.max_bytes, self.min_free_bytes = max_bytes, min_free_bytes
        self._lock, self._closed = None, False
        output = None if output_dir is None else str(Path(output_dir).resolve())
        if output is not None and self.directory.is_relative_to(Path(output)):
            raise ValueError("CHECKPOINT_MUST_BE_OUTSIDE_ARTIFACT_DIRECTORY")
        self.binding = json.loads(_canonical(dict(caller=binding,
            output_dir=output, python=list(sys.version_info[:3]), numpy=np.__version__,
            byteorder=sys.byteorder)))
        self.binding_sha256 = hashlib.sha256(_canonical(self.binding)).hexdigest()
        self.directory.mkdir(parents=True, exist_ok=True)
        try:
            self._acquire_lock()
            manifest = self.directory/"manifest.json"
            if manifest.exists():
                self._manifest = self._read_manifest(manifest)
                self._validate_manifest()
                # Verify every referenced byte before returning any state.
                for proof in self._proofs():
                    self._validate_proof(proof)
            else:
                if any(_BLOB_NAME.fullmatch(p.name) for p in self.directory.iterdir()):
                    # A lost manifest cannot safely designate which old
                    # generation (if any) was committed. Never reset silently.
                    raise ValueError("CHECKPOINT_MANIFEST_MISSING")
                unknown = [p for p in self.directory.iterdir()
                           if p.name != ".checkpoint.lock"
                           and not _BLOB_NAME.fullmatch(p.name)
                           and not _MANIFEST_PARTIAL.fullmatch(p.name)]
                if unknown:
                    raise ValueError("CHECKPOINT_DIRECTORY_NOT_EMPTY")
                self._manifest = dict(schema=SCHEMA, binding=self.binding,
                    binding_sha256=self.binding_sha256, completed=[], state=None, models={})
                self._publish_manifest(self._manifest)
            self._cleanup_orphans()
        except BaseException:
            self.close()
            raise

    def _acquire_lock(self):
        path = self.directory/".checkpoint.lock"
        if path.is_symlink():
            raise ValueError("CHECKPOINT_SYMLINK_FORBIDDEN")
        self._lock = path.open("a+b")
        self._lock.seek(0, os.SEEK_END)
        if not self._lock.tell():
            self._lock.write(b"0")
            self._lock.flush()
        self._lock.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self._lock.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self._lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            self._lock.close()
            self._lock = None
            raise ValueError("CHECKPOINT_ALREADY_OPEN") from error

    @staticmethod
    def _read_manifest(path):
        if path.is_symlink():
            raise ValueError("CHECKPOINT_SYMLINK_FORBIDDEN")
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError) as error:
            raise ValueError("CHECKPOINT_MANIFEST_CORRUPT") from error
        if not isinstance(value, dict):
            raise ValueError("CHECKPOINT_MANIFEST_CORRUPT")
        checksum = value.pop("manifest_sha256", None)
        if checksum != hashlib.sha256(_canonical(value)).hexdigest():
            raise ValueError("CHECKPOINT_MANIFEST_HASH_MISMATCH")
        return value

    def _validate_manifest(self):
        value = self._manifest
        if value.get("schema") != SCHEMA:
            raise ValueError("CHECKPOINT_SCHEMA_MISMATCH")
        if (value.get("binding") != self.binding
                or value.get("binding_sha256") != self.binding_sha256):
            raise ValueError("CHECKPOINT_BINDING_MISMATCH")
        if set(value) != {"schema", "binding", "binding_sha256", "completed", "state", "models"}:
            raise ValueError("CHECKPOINT_MANIFEST_CORRUPT")
        self._identities(value["completed"])
        if not isinstance(value["models"], dict) or any(not isinstance(k, str) or not k for k in value["models"]):
            raise ValueError("CHECKPOINT_MANIFEST_CORRUPT")
        if bool(value["completed"]) != (value["state"] is not None):
            raise ValueError("CHECKPOINT_STATE_PREFIX_MISMATCH")

    def _proofs(self):
        return ([self._manifest["state"]] if self._manifest["state"] else []) + list(self._manifest["models"].values())

    def _validate_proof(self, proof):
        if (not isinstance(proof, dict) or set(proof) != {"path", "bytes", "sha256"}
                or not isinstance(proof["path"], str)
                or not _BLOB_NAME.fullmatch(proof["path"])
                or proof["path"].endswith(".partial")
                or not isinstance(proof["bytes"], int) or proof["bytes"] <= 0
                or not isinstance(proof["sha256"], str)
                or not re.fullmatch(r"[0-9a-f]{64}", proof["sha256"])):
            raise ValueError("CHECKPOINT_BLOB_PROOF_INVALID")
        path = self.directory/proof["path"]
        if path.is_symlink():
            raise ValueError("CHECKPOINT_SYMLINK_FORBIDDEN")
        if not path.is_file() or path.stat().st_size != proof["bytes"] or file_sha256(path) != proof["sha256"]:
            raise ValueError("CHECKPOINT_BLOB_HASH_MISMATCH:"+proof["path"])
        return path

    def _ensure_open(self):
        if self._closed or self._lock is None:
            raise ValueError("CHECKPOINT_CLOSED")

    def _available_bytes(self):
        used = sum(path.stat().st_size for path in self.directory.iterdir() if path.is_file())
        available = shutil.disk_usage(self.directory).free - self.min_free_bytes
        if self.max_bytes is not None:
            available = min(available, self.max_bytes-used)
        if available <= 0:
            raise OSError("CHECKPOINT_DISK_BUDGET_EXCEEDED")
        return available

    def _publish_manifest(self, value):
        document = dict(value, manifest_sha256=hashlib.sha256(_canonical(value)).hexdigest())
        data = _canonical(document)+b"\n"
        temporary = self.directory/("manifest-"+uuid.uuid4().hex+".json.partial")
        try:
            if len(data) > self._available_bytes():
                raise OSError("CHECKPOINT_DISK_BUDGET_EXCEEDED")
            with temporary.open("xb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            _atomic_replace(temporary, self.directory/"manifest.json")
        finally:
            if temporary.exists():
                temporary.unlink()

    def _write_blob(self, kind, value):
        name = kind+"-"+uuid.uuid4().hex+".pickle.gz"
        path, temporary = self.directory/name, self.directory/(name+".partial")
        try:
            available = self._available_bytes()
            with temporary.open("xb") as raw:
                limited = _BudgetWriter(raw, available)
                with gzip.GzipFile(filename="", fileobj=limited, mode="wb", compresslevel=1, mtime=0) as stream:
                    _CheckpointPickler(stream, protocol=pickle.HIGHEST_PROTOCOL).dump(value)
                raw.flush()
                os.fsync(raw.fileno())
            _atomic_replace(temporary, path)
            return dict(path=name, bytes=path.stat().st_size, sha256=file_sha256(path))
        finally:
            if temporary.exists():
                temporary.unlink()

    def _load_blob(self, proof, kind):
        path = self._validate_proof(proof)
        try:
            with gzip.open(path, "rb") as stream:
                envelope = pickle.load(stream)
                if stream.read(1):
                    raise ValueError("CHECKPOINT_BLOB_TRAILING_DATA")
        except Exception as error:
            raise ValueError("CHECKPOINT_BLOB_DECODE_FAILED") from error
        if (not isinstance(envelope, dict) or envelope.get("schema") != SCHEMA
                or envelope.get("binding_sha256") != self.binding_sha256
                or envelope.get("kind") != kind):
            raise ValueError("CHECKPOINT_BLOB_BINDING_MISMATCH")
        return envelope

    @staticmethod
    def _identities(completed):
        if not isinstance(completed, (tuple, list)):
            raise ValueError("CHECKPOINT_INVALID_COMPLETED_PREFIX")
        if any(not isinstance(row, (tuple, list)) or len(row) != 3
               or any(not isinstance(item, str) or not item for item in row) for row in completed):
            raise ValueError("CHECKPOINT_INVALID_COMPLETED_PREFIX")
        identities = tuple(tuple(row) for row in completed)
        if len(set(identities)) != len(identities):
            raise ValueError("CHECKPOINT_DUPLICATE_EVALUATION")
        return identities

    @property
    def completed(self):
        return tuple(tuple(row) for row in self._manifest["completed"])

    @property
    def model_keys(self):
        return tuple(self._manifest["models"])

    def load_state(self):
        self._ensure_open()
        proof = self._manifest["state"]
        if proof is None:
            return None
        envelope = self._load_blob(proof, "state")
        if self._identities(envelope.get("completed")) != self.completed:
            raise ValueError("CHECKPOINT_STATE_PREFIX_MISMATCH")
        return envelope["value"]

    def commit_state(self, state, *, completed):
        """Publish exactly one new evaluation after ordered parent replay.

        On any exception, stop the run; in-memory channels may already contain
        the new evaluation. Reopen to recover the last committed prefix.
        """
        self._ensure_open()
        identities = self._identities(completed)
        if len(identities) != len(self.completed)+1 or identities[:-1] != self.completed:
            raise ValueError("CHECKPOINT_NONCONTIGUOUS_PREFIX")
        proof = self._write_blob("state", dict(schema=SCHEMA,
            binding_sha256=self.binding_sha256, kind="state", completed=identities, value=state))
        manifest = dict(self._manifest, state=proof, completed=[list(row) for row in identities])
        self._publish_manifest(manifest)
        self._manifest = manifest
        self._cleanup_orphans()
        return dict(proof)

    def save_model(self, key, value):
        self._ensure_open()
        if not isinstance(key, str) or not key:
            raise ValueError("CHECKPOINT_INVALID_MODEL_KEY")
        if key in self._manifest["models"]:
            raise ValueError("CHECKPOINT_MODEL_ALREADY_EXISTS:"+key)
        proof = self._write_blob("model", dict(schema=SCHEMA,
            binding_sha256=self.binding_sha256, kind="model", key=key, value=value))
        manifest = dict(self._manifest, models=dict(self._manifest["models"], **{key: proof}))
        self._publish_manifest(manifest)
        self._manifest = manifest
        self._cleanup_orphans()
        return dict(proof)

    def load_model(self, key):
        self._ensure_open()
        proof = self._manifest["models"].get(key)
        if proof is None:
            return None
        envelope = self._load_blob(proof, "model")
        if envelope.get("key") != key:
            raise ValueError("CHECKPOINT_MODEL_KEY_MISMATCH")
        return envelope["value"]

    def _cleanup_orphans(self):
        keep = {proof["path"] for proof in self._proofs()}
        removed = False
        for path in self.directory.iterdir():
            if path.name not in keep and (_BLOB_NAME.fullmatch(path.name) or _MANIFEST_PARTIAL.fullmatch(path.name)):
                if path.is_symlink() or not path.is_file():
                    raise ValueError("CHECKPOINT_ORPHAN_NOT_REGULAR_FILE")
                path.unlink()
                removed = True
        if removed:
            _fsync_directory(self.directory)

    def close(self):
        if self._lock is not None:
            self._lock.close()  # OS releases the lock even after process death.
            self._lock = None
        self._closed = True

    def __enter__(self):
        self._ensure_open()
        return self

    def __exit__(self, *_):
        self.close()
