import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / ".claude" / "boot_gate_stage_a_audit_20260806"


def test_stage_a_receipt_is_read_only_and_conserves_exchange_rows():
    audit = json.loads((OUT / "VPS_AND_EXCHANGE_READONLY_SNAPSHOT.json").read_text())
    receipt = json.loads((OUT / "STAGE_A_READINESS_RECEIPT.json").read_text())
    assert receipt["stage_A"] == "COMPLETED_READ_ONLY"
    assert receipt["stage_B"] == "NOT_AUTHORIZED_NOT_STARTED"
    assert receipt["stage_C"] == "NOT_AUTHORIZED_NOT_STARTED"
    assert set(audit["mutations"].values()) == {0}
    counts = audit["exchange"]["counts"]
    assert counts["resting_orders"] == len(audit["exchange"]["resting_orders"])
    assert counts["positions"] == len(audit["exchange"]["positions"])
    assert sum(audit["exchange"]["reconciliation_counts"].values()) == counts["positions"]
    assert audit["processes"]["live_v4_count"] == 0
    manifest = json.loads((OUT / "ARTIFACT_HASH_MANIFEST.json").read_text())
    for name, expected in manifest["files"].items():
        data = (OUT / name).read_bytes()
        assert len(data) == expected["bytes"]
        assert hashlib.sha256(data).hexdigest() == expected["sha256"]
