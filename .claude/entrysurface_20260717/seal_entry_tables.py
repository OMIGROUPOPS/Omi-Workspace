#!/usr/bin/env python3
"""STAGE 5 — THE SEAL, 4b AMENDMENT (survivors only; the failed bands never speak).

Survivor law (from the Stage-4 report, stated plainly):
  SEALED  — CI-passing on holdout AND positive holdout ROC in at least one
            scoring frame (replay close-mark n>=10, or the Stage-3
            reach-frame holdout confirmation), at the depth that earned it.
  FAILED-HOLDOUT — CI fail or negative-both-frames: row present, marked,
            NEVER consulted.
  THIN    — insufficient holdout n: row present, marked, never consulted.
Output: state/entry_tables_sealed_v1.json + sha256 provenance in
.claude/entrysurface_20260717/LOCKED_DOWN_ENTRY.md (written by the
caller with the hashes this prints).
"""
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V1 = json.loads((ROOT / "state/entry_tables_v1.json").read_text())
V2 = json.loads((ROOT / "state/entry_tables_v2.json").read_text())
OUT = ROOT / "state/entry_tables_sealed_v1.json"

# survivor decisions, named (from LOOP_CAMPAIGN.md + ENTRY_SOLVE.md):
# [4b AMENDMENT 07-18] the re-framed drill (LOOP2) demoted both
# replay-frame survivors: ATP_MAIN-B8 park fills 9/10 but ROC -0.025
# (fills into losers on the close mark); WTA_CHALL-B3 drilled to 1c,
# 34/45 fills, ROC -0.049. The seal SHRINKS to the two reach-frame
# casts; own-frame holdout THIN for both (n=4 / phase-2 rare), both
# receipts shown. All ten 4a failures = STILL FAIL: REAL.
SEALED = {
    "ATP_MAIN-B2":  (25, "reach_frame", "Stage-3 holdout: realized 0.30 vs pred 0.24, ROC 0.218; own-frame 4b holdout THIN (phase-2 caller rare) — both receipts shown"),
    "WTA_CHALL-B1": (12, "reach_frame", "Stage-3 holdout: realized 0.18 vs pred 0.16, ROC 0.252; own-frame 4b holdout n=4 THIN — both receipts shown"),
}
REFUSE = {"ATP_CHALL-B5", "WTA_CHALL-B7", "ATP_MAIN-B6", "WTA_MAIN-B5",
          "ITF_M-B7", "ITF_W-B8"}   # violent fallers: the REFUSE is law

rows = {}
for band, r in V1["tables"].items():
    row = dict(r)
    row.pop("gated_levels", None)
    if band in SEALED:
        d, frame, rec = SEALED[band]
        row.update({"status": "SEALED", "depth": d, "frame": frame,
                    "receipt": rec})
    elif band in REFUSE or (r.get("kind") == "faller"
                            and (r.get("roc") or 0) <= 0):
        row.update({"status": "REFUSE", "receipt":
                    "violent faller / negative solve — the REFUSE is law"})
    elif r.get("thin"):
        row.update({"status": "THIN"})
    else:
        row.update({"status": "FAILED-HOLDOUT", "receipt":
                    "Stage-4 drill: CI fail or negative holdout ROC "
                    "(LOOP_CAMPAIGN.md) — never consulted"})
    rows[band] = row
sealed = {"sealed_at_stage": "5", "survivor_law":
          "CI-pass + positive holdout ROC in >=1 frame; failures marked, "
          "never consulted; violent-faller REFUSE is law",
          "n_sealed": sum(1 for r in rows.values()
                          if r["status"] == "SEALED"),
          "n_refuse": sum(1 for r in rows.values()
                          if r["status"] == "REFUSE"),
          "bands": rows}
OUT.write_text(json.dumps(sealed, sort_keys=True))
h = hashlib.sha256(OUT.read_bytes()).hexdigest()
print("SEALED", sealed["n_sealed"], "REFUSE", sealed["n_refuse"],
      "of", len(rows))
print("sha256(entry_tables_sealed_v1.json) =", h)
for name in ("band_map_v1.json", "drift_surfaces_v1.json",
             "divot_tables_v1.json", "entry_tables_v1.json",
             "entry_tables_v2.json"):
    p = ROOT / "state" / name
    print("sha256(%s) = %s" % (name,
                               hashlib.sha256(p.read_bytes()).hexdigest()))
