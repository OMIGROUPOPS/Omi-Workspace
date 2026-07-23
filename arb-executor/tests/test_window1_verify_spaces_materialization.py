import hashlib
import importlib.util
import json
from pathlib import Path


PATH = (
    Path(__file__).resolve().parents[1]
    / "analysis"
    / "window1_verify_spaces_materialization.py"
)
SPEC = importlib.util.spec_from_file_location(
    "window1_verify_spaces_materialization", PATH
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_manifest_materialization_is_hash_and_size_bound(tmp_path):
    primary = tmp_path / "primary"
    recovered = tmp_path / "recovered"
    primary.mkdir()
    recovered.mkdir()
    raw = b"immutable recorder bytes\n"
    (recovered / "EVENT-A.csv.gz").write_bytes(raw)
    manifest = tmp_path / "manifest.jsonl"
    manifest.write_text(json.dumps({
        "prefix": "ticks",
        "event_id": "EVENT",
        "ticker": "EVENT-A",
        "path": "ticks/EVENT-A.csv.gz",
        "size_bytes": len(raw),
        "content_hashes": {
            "md5": hashlib.md5(
                raw, usedforsecurity=False
            ).hexdigest()
        },
    }) + "\n", encoding="utf-8")
    ledger = tmp_path / "ledger.jsonl"
    summary = tmp_path / "summary.json"
    args = MODULE.parser().parse_args([
        "--manifest", str(manifest),
        "--primary-dir", str(primary),
        "--recovered-dir", str(recovered),
        "--ledger-output", str(ledger),
        "--summary-output", str(summary),
    ])
    assert MODULE.run(args) == 0
    result = json.loads(summary.read_text())
    assert result["all_exact"] is True
    assert result["states"] == {"exact_spaces_object": 1}
    row = json.loads(ledger.read_text())
    assert row["logical_materialization"] == (
        "spaces_recovered_private"
    )
    assert row["state"] == "exact_spaces_object"
