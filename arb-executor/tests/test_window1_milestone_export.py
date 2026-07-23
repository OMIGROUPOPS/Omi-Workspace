import importlib.util
import json
from pathlib import Path


PATH = (
    Path(__file__).resolve().parents[1]
    / "analysis"
    / "window1_milestone_export.py"
)
SPEC = importlib.util.spec_from_file_location(
    "window1_milestone_export", PATH
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_normalizer_hashes_public_source_identity():
    result = {
        "event_id": "E",
        "receipt": {
            "fetched_utc": "2026-07-23T00:00:00+00:00",
            "pages": [{
                "response": {
                    "milestones": [{
                        "id": "milestone-public-id",
                        "source_id": "provider-public-id",
                        "details": {"status": "P"},
                        "start_date": "2026-07-12T12:00:00Z",
                        "last_updated_ts": "2026-07-12T14:00:00Z",
                    }]
                }
            }],
        },
    }
    rows = MODULE.normalized_rows(result)
    assert len(rows) == 1
    assert rows[0]["status"] == "P"
    assert rows[0]["milestone_identity_sha256"]
    assert rows[0]["source_identity_sha256"]
    assert "milestone-public-id" not in json.dumps(rows)
