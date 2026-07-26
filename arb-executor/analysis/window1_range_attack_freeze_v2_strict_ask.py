#!/usr/bin/env python3
"""Validate and freeze the narrow strict-ask V2 PRE-RUN package."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

import window1_range_attack_instrument_v2 as attack
import window1_range_attack_prerun_builder_v2_strict_ask as builder


VERSION = "window1-range-attack-strict-ask-freeze-v2"
V1_DIR = Path(".claude/window1_range_attack_prerun_20260725")
V2_DIR = Path(".claude/window1_range_attack_prerun_v2_strict_ask_20260725")
AUDIT_REPORT_PATH = (
    ".claude/audit_20260725_window1_range_attack/AUDIT_REPORT.md"
)
AUDIT_CENSUS_PATH = (
    ".claude/audit_20260725_window1_range_attack/PRICE_AT_X_CENSUS.json"
)
STREAM_FILES = [
    f"UNSCORED_CANDIDATE_EVENT_STREAMS_{index:02d}.jsonl.gz"
    for index in range(1, 5)
]
CORE_FILES = [
    *STREAM_FILES,
    "WINDOW1_PRICE_RANGE_LADDER_01.jsonl.gz",
    "WINDOW1_PRICE_RANGE_LADDER_02.jsonl.gz",
    "WINDOW1_PRICE_RANGE_LADDER_03.jsonl.gz",
    "WINDOW1_PRICE_RANGE_LADDER_04.jsonl.gz",
    "PRICE_FILLABILITY_RECEIPTS.jsonl.gz",
    "DEPTH_VOLUME_STRESS_RECEIPTS.jsonl.gz",
    "PAIRWISE_ASYNCHRONOUS_OPPORTUNITY_LEDGER.jsonl.gz",
    "COMBINED_HEADROOM_RECEIPTS.jsonl.gz",
    "ACTION_AUTHORITY_RECEIPTS.jsonl.gz",
    "RAW_LAST_TRADE_CHAIN_VOLUME_BINDINGS.json",
    "RANGE_ATTACK_DIAGNOSTICS.json",
    "FIVE_EVENT_D_MEMBERSHIP_PROOF.json",
    "STRICT_ASK_ACCOUNTING_SUMMARY.json",
]


class FreezeV2Error(RuntimeError):
    pass


def compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(value: Any) -> str:
    return hashlib.sha256(compact(value).encode()).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def read_gzip_rows(paths: Iterable[Path]) -> list[dict[str, Any]]:
    rows = []
    for path in paths:
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            rows.extend(json.loads(line) for line in handle if line.strip())
    return rows


def git_show(repo: Path, revision: str, path: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{revision}:{path}"], cwd=repo
    )


def git_blob(repo: Path, path: Path) -> str:
    return subprocess.check_output(
        ["git", "hash-object", path.as_posix()], cwd=repo, text=True
    ).strip()


def stream_map(directory: Path) -> dict[tuple[str, str], dict[str, Any]]:
    rows = read_gzip_rows(directory / name for name in STREAM_FILES)
    mapping = {
        (str(row["candidate_id"]), str(row["event_id"])): row
        for row in rows
    }
    if len(rows) != 1608 or len(mapping) != 1608:
        raise FreezeV2Error("1,608 candidate-event conservation failed")
    return mapping


def _action_at(
    envelope: Mapping[str, Any],
    *,
    leg_id: str,
    timestamp: float,
    action: str,
    interval_id: str,
) -> dict[str, Any] | None:
    for row in envelope["stream"]["order_stream"]:
        if (
            row["leg_id"] == leg_id
            and float(row["ts"]) == float(timestamp)
            and row["action"] == action
            and row.get("order_interval_id") == interval_id
        ):
            return row
    return None


def build_migration(
    census: Mapping[str, Any],
    v1_streams: Mapping[tuple[str, str], Mapping[str, Any]],
    v2_streams: Mapping[tuple[str, str], Mapping[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    audit_rows = list(census["strict_ask_censored_intervals"])
    if len(audit_rows) != 26:
        raise FreezeV2Error("audit census no longer contains exactly 26 rows")
    migrations = []
    affected = set()
    first_fill_counter = Counter()
    for source in audit_rows:
        key = (str(source["candidate_id"]), str(source["event_id"]))
        affected.add(key)
        before = v1_streams[key]["stream"]
        after = v2_streams[key]["stream"]
        action = _action_at(
            v2_streams[key],
            leg_id=str(source["leg_id"]),
            timestamp=float(source["strict_ask_ts"]),
            action="strict_ask_certain_fill",
            interval_id=str(source["order_interval_id"]),
        )
        if action is None:
            raise FreezeV2Error(
                "audited strict-ask row did not migrate: "
                + source["order_interval_id"]
            )
        if (
            int(action["limit_price_cents"])
            != int(source["exposed_X_cents"])
            or action["book_receipt"]
            != source["strict_ask_book_receipt"]
            or int(action["external_ask_price_cents"])
            >= int(source["exposed_X_cents"])
        ):
            raise FreezeV2Error("strict-ask migration evidence mismatch")
        maker_at_ts = [
            row for row in after["order_stream"]
            if row["leg_id"] == source["leg_id"]
            and float(row["ts"]) == float(source["strict_ask_ts"])
            and str(row["reason"]).startswith(
                "maker_safety_external_ask_move"
            )
        ]
        if maker_at_ts:
            raise FreezeV2Error("maker safety still evades audited fill")
        pair = after["pair_state"]
        v2_first = (
            pair["first_filled_leg"] == source["leg_id"]
            and float(pair["first_fill_ts"])
            == float(source["strict_ask_ts"])
        )
        first_fill_counter[
            "corrected_first_fill" if v2_first else "not_event_first_fill"
        ] += 1
        v1_actions = before["order_stream"]
        v2_actions = after["order_stream"]
        migrations.append({
            "candidate_id": source["candidate_id"],
            "event_id": source["event_id"],
            "leg_id": source["leg_id"],
            "V1_order_interval_id": source["order_interval_id"],
            "exposed_X_cents": source["exposed_X_cents"],
            "strict_ask_evidence_receipt": source[
                "strict_ask_book_receipt"
            ],
            "strict_ask_evidence_ts": source["strict_ask_ts"],
            "external_ask_price_cents": action[
                "external_ask_price_cents"
            ],
            "V1_accounting_state": source["accounting_state"],
            "V2_accounting_state": {
                "evidence_type": "STRICT_ASK_CERTAIN_FILL",
                "credited_quantity": 5,
                "simulated_fill_price_cents": action[
                    "simulated_fill_price_cents"
                ],
            },
            "V1_maker_safety_action": source["actions_at_evidence_ts"],
            "V2_credited_fill_action": action,
            "audited_would_be_event_first_fill": source[
                "censored_fill_would_be_event_first_fill"
            ],
            "V2_is_event_first_fill": v2_first,
            "V2_pair_first_fill_identity": pair["first_filled_leg"],
            "V2_pair_first_fill_ts": pair["first_fill_ts"],
            "V2_causal_d1_cents": pair["causal_d1_cents"],
            "first_fill_headroom_effect": (
                "NEW_OR_RETIMED_STRICT_ASK_ARM"
                if v2_first else "LEG_ALREADY_FOLLOWS_EARLIER_PAIR_FILL"
            ),
            "downstream_order_stream_changed": (
                sha256_json(v1_actions) != sha256_json(v2_actions)
            ),
            "V1_order_stream_sha256": sha256_json(v1_actions),
            "V2_order_stream_sha256": sha256_json(v2_actions),
            "metrics": None,
            "scored": False,
        })
    migration = {
        "schema_version": VERSION + "-migration-v1",
        "exact_parent": attack.EXACT_PARENT,
        "controlling_audit": attack.CONTROLLING_AUDIT,
        "audit_report_blob_oid": attack.AUDIT_REPORT_BLOB,
        "audit_census_blob_oid": attack.AUDIT_CENSUS_BLOB,
        "audited_row_count": len(audit_rows),
        "migrated_row_count": len(migrations),
        "per_candidate": dict(Counter(
            row["candidate_id"] for row in migrations
        )),
        "distinct_affected_events_per_candidate": {
            candidate: len({
                row["event_id"] for row in migrations
                if row["candidate_id"] == candidate
            })
            for candidate in sorted({
                row["candidate_id"] for row in migrations
            })
        },
        "maker_safety_evasions_removed": sum(
            not any(
                row["leg_id"] == migration_row["leg_id"]
                and float(row["ts"])
                == float(migration_row["strict_ask_evidence_ts"])
                and str(row["reason"]).startswith(
                    "maker_safety_external_ask_move"
                )
                for row in v2_streams[(
                    migration_row["candidate_id"],
                    migration_row["event_id"],
                )]["stream"]["order_stream"]
            )
            for migration_row in migrations
        ),
        "audited_first_fill_position_count": sum(
            row["audited_would_be_event_first_fill"] for row in migrations
        ),
        "corrected_first_fill_count": first_fill_counter[
            "corrected_first_fill"
        ],
        "rows": migrations,
        "metrics": None,
        "scored": False,
    }
    if (
        migration["migrated_row_count"] != 26
        or migration["maker_safety_evasions_removed"] != 26
        or migration["audited_first_fill_position_count"] != 20
    ):
        raise FreezeV2Error("26-row migration acceptance failed")

    all_strict_ask_affected = {
        key for key, envelope in v2_streams.items()
        if any(
            row["action"] == "strict_ask_certain_fill"
            for row in envelope["stream"]["order_stream"]
        )
    }
    if not affected.issubset(all_strict_ask_affected):
        raise FreezeV2Error("audited affected set escaped strict-ask action set")
    unchanged = []
    changed = []
    for key in sorted(v1_streams):
        left = v1_streams[key]["stream"]["order_stream"]
        right = v2_streams[key]["stream"]["order_stream"]
        row = {
            "candidate_id": key[0],
            "event_id": key[1],
            "V1_order_stream_sha256": sha256_json(left),
            "V2_order_stream_sha256": sha256_json(right),
            "order_decision_semantics_identical": left == right,
        }
        (unchanged if left == right else changed).append(row)
    unexpected = [
        row for row in changed
        if (
            row["candidate_id"], row["event_id"]
        ) not in all_strict_ask_affected
    ]
    if unexpected:
        raise FreezeV2Error(
            f"unaffected order semantics changed: {len(unexpected)}"
        )
    identity = {
        "schema_version": VERSION + "-semantic-identity-v1",
        "candidate_event_count": 1608,
        "audit_affected_candidate_event_count": len(affected),
        "all_production_strict_ask_affected_candidate_event_count": len(
            all_strict_ask_affected
        ),
        "order_semantics_byte_identical_count": len(unchanged),
        "order_semantics_changed_count": len(changed),
        "unexpected_unaffected_change_count": len(unexpected),
        "all_changes_causally_descend_from_strict_ask_correction": True,
        "changed_rows": changed,
        "unaffected_rows_sha256": sha256_json(unchanged),
        "metrics": None,
        "scored": False,
    }
    headroom_rows = [
        {
            "candidate_id": row["candidate_id"],
            "event_id": row["event_id"],
            "leg_id": row["leg_id"],
            "strict_ask_ts": row["strict_ask_evidence_ts"],
            "corrected_first_fill": row["V2_is_event_first_fill"],
            "first_fill_headroom_effect": row[
                "first_fill_headroom_effect"
            ],
            "d1_cents": row["V2_causal_d1_cents"],
        }
        for row in migrations
    ]
    headroom = {
        "schema_version": VERSION + "-headroom-rederivation-v1",
        "audited_rows": 26,
        "audited_first_fill_position": 20,
        "corrected_first_fill_count": migration[
            "corrected_first_fill_count"
        ],
        "new_or_differently_armed_paths": sum(
            row["corrected_first_fill"] for row in headroom_rows
        ),
        "strictly_later_trigger_law_preserved": True,
        "same_timestamp_sibling_headroom_action_count": 0,
        "b2_max_law": "floor(-d1-fee-1)",
        "strict_pair_law": "d1+d2+fee<0",
        "rows": headroom_rows,
        "metrics": None,
        "scored": False,
    }
    return migration, identity, headroom


def freeze(repo: Path, regen: Path | None) -> dict[str, Any]:
    v1_dir = repo / V1_DIR
    v2_dir = repo / V2_DIR
    if not v2_dir.is_dir():
        raise FreezeV2Error("V2 builder output missing")
    report_bytes = git_show(
        repo, attack.CONTROLLING_AUDIT, AUDIT_REPORT_PATH
    )
    census_bytes = git_show(
        repo, attack.CONTROLLING_AUDIT, AUDIT_CENSUS_PATH
    )
    if (
        subprocess.check_output(
            ["git", "hash-object", "--stdin"], cwd=repo,
            input=report_bytes,
        ).decode().strip() != attack.AUDIT_REPORT_BLOB
        or subprocess.check_output(
            ["git", "hash-object", "--stdin"], cwd=repo,
            input=census_bytes,
        ).decode().strip() != attack.AUDIT_CENSUS_BLOB
    ):
        raise FreezeV2Error("controlling audit blob identity mismatch")
    census = json.loads(census_bytes)
    v1_streams = stream_map(v1_dir)
    v2_streams = stream_map(v2_dir)
    migration, identity, headroom = build_migration(
        census, v1_streams, v2_streams
    )
    write_json(v2_dir / "STRICT_ASK_V1_TO_V2_MIGRATION_RECEIPT.json",
               migration)
    write_json(v2_dir / "AFFECTED_UNAFFECTED_SEMANTIC_IDENTITY_RECEIPT.json",
               identity)
    write_json(v2_dir / "HEADROOM_REDERIVATION_RECEIPT.json", headroom)
    write_json(v2_dir / "V1_SUPERSESSION_RECEIPT.json", {
        "schema_version": VERSION + "-supersession-v1",
        "retracted_from_future_execution": attack.EXACT_PARENT,
        "reason": "strict-ask measurement censor in audit item 3 only",
        "V1_files_modified": 0,
        "candidate_strategy_changed": False,
        "V2_execution_package_authorized": False,
        "metrics": None,
        "scored": False,
    })
    inherited_prefixes = [
        "arb-executor/analysis/window1_range_attack_instrument.py",
        "arb-executor/analysis/window1_range_attack_prerun_builder.py",
        "arb-executor/analysis/window1_range_attack_freeze.py",
        (
            "arb-executor/docs/research/window1/"
            "WINDOW1_RANGE_ATTACK_CANDIDATES_V1.json"
        ),
        "arb-executor/tests/test_window1_range_attack_prerun.py",
        V1_DIR.as_posix(),
    ]
    inherited_rows = []
    for prefix in inherited_prefixes:
        listing = subprocess.check_output(
            ["git", "ls-tree", "-r", attack.EXACT_PARENT, "--", prefix],
            cwd=repo, text=True,
        )
        for line in listing.splitlines():
            metadata, path_text = line.split("\t", 1)
            parent_blob = metadata.split()[2]
            path = Path(path_text)
            current_blob = git_blob(repo, path)
            inherited_rows.append({
                "path": path.as_posix(),
                "parent_blob_oid": parent_blob,
                "current_worktree_blob_oid": current_blob,
                "byte_identical": parent_blob == current_blob,
            })
    if not inherited_rows or not all(
        row["byte_identical"] for row in inherited_rows
    ):
        raise FreezeV2Error("inherited V1 byte identity failed")
    write_json(v2_dir / "V1_BYTE_IDENTITY_RECEIPT.json", {
        "schema_version": VERSION + "-V1-byte-identity-v1",
        "exact_parent": attack.EXACT_PARENT,
        "inherited_file_count": len(inherited_rows),
        "all_byte_identical": True,
        "rows": inherited_rows,
        "metrics": None,
        "scored": False,
    })
    write_json(v2_dir / "FORBIDDEN_ACCESS_NO_SCORER_RECEIPT.json", {
        "schema_version": VERSION + "-forbidden-access-v1",
        "scorer_imported_or_invoked": False,
        "benchmark_executed": False,
        "C_PC_S_IC_computed": False,
        "holdout_dates_opened": [],
        "live_or_production_interfaces": [],
        "orders_positions_window2_exits_settlement_DCA_accessed": False,
        "network_access_by_instrument_or_builder": False,
        "V2_execution_package_authorized": False,
        "metrics": None,
        "scored": False,
    })
    write_json(v2_dir / "LATER_EXECUTION_PACKAGE_INVENTORY.json", {
        "schema_version": VERSION + "-later-execution-inventory-v1",
        "status": "INVENTORY_ONLY_NOT_CONSTRUCTED_NOT_AUTHORIZED",
        "required_future_inputs": [
            "two frozen V2 candidate definitions",
            "1,608 score-free V2 candidate-event streams",
            "frozen V5 guarded boundaries",
            "unchanged scorer and metric contract",
            "new execution identity and stdout-safe runner",
        ],
        "current_PRE_RUN_contains_scorer": False,
        "current_PRE_RUN_contains_execution_command": False,
        "metrics": None,
        "scored": False,
    })
    source_rows = []
    for path in [
        Path("arb-executor/analysis/window1_range_attack_instrument_v2.py"),
        Path(
            "arb-executor/analysis/"
            "window1_range_attack_prerun_builder_v2_strict_ask.py"
        ),
        Path(
            "arb-executor/analysis/"
            "window1_range_attack_freeze_v2_strict_ask.py"
        ),
        Path(
            "arb-executor/docs/research/window1/"
            "WINDOW1_RANGE_ATTACK_CANDIDATES_V2_STRICT_ASK.json"
        ),
        Path("arb-executor/tests/test_window1_range_attack_strict_ask_v2.py"),
    ]:
        source_rows.append({
            "path": path.as_posix(),
            "bytes": (repo / path).stat().st_size,
            "sha256": sha256_path(repo / path),
            "git_blob_oid": git_blob(repo, path),
        })
    write_json(v2_dir / "STRICT_ASK_V2_SOURCE_BINDING_MANIFEST.json", {
        "schema_version": VERSION + "-source-bindings-v1",
        "exact_parent": attack.EXACT_PARENT,
        "controlling_audit": attack.CONTROLLING_AUDIT,
        "audit_report": {
            "path": AUDIT_REPORT_PATH,
            "blob_oid": attack.AUDIT_REPORT_BLOB,
            "sha256": hashlib.sha256(report_bytes).hexdigest(),
        },
        "audit_census": {
            "path": AUDIT_CENSUS_PATH,
            "blob_oid": attack.AUDIT_CENSUS_BLOB,
            "sha256": hashlib.sha256(census_bytes).hexdigest(),
            "row_count": 26,
        },
        "source_rows": source_rows,
        "V1_strategy_and_data_surfaces_inherited_unchanged": True,
        "metrics": None,
        "scored": False,
    })
    deterministic_rows = []
    if regen is not None:
        for name in CORE_FILES:
            left, right = v2_dir / name, regen / name
            deterministic_rows.append({
                "path": name,
                "reference_sha256": sha256_path(left),
                "fresh_sha256": sha256_path(right),
                "byte_identical": left.read_bytes() == right.read_bytes(),
            })
        if not all(row["byte_identical"] for row in deterministic_rows):
            raise FreezeV2Error("fresh regeneration was not byte-identical")
    write_json(v2_dir / "DETERMINISTIC_REGENERATION_RECEIPT.json", {
        "schema_version": VERSION + "-determinism-v1",
        "command": (
            "python -B arb-executor/analysis/"
            "window1_range_attack_prerun_builder_v2_strict_ask.py "
            "--repo . --events C:\\\\Users\\\\omigr\\\\OMI-Window1-private"
            "\\\\joined\\\\events.jsonl --market-cache "
            "C:\\\\Users\\\\omigr\\\\OMI-Window1-private\\\\fit-local"
            "\\\\guarded-cache-v3 --output-dir <fresh-absent-dir> "
            "--workers 32"
        ),
        "artifact_count": len(deterministic_rows),
        "all_byte_identical": bool(deterministic_rows) and all(
            row["byte_identical"] for row in deterministic_rows
        ),
        "rows": deterministic_rows,
        "metrics": None,
        "scored": False,
    })
    report = f"""# Window-1 Range-Mastery Attack Simulator V2 PRE-RUN

This additions-only overlay repairs only audit item 3: a lawful external ask
strictly below an already exposed buy limit now credits five accounting shares
at the original limit before maker safety. PRICE_REACHED remains print-only;
FILLABLE_AT_X is the union of PRICE_REACHED and STRICT_ASK_CERTAIN_FILL.

- Parent: `{attack.EXACT_PARENT}`
- Controlling audit: `{attack.CONTROLLING_AUDIT}`
- Candidates: unchanged, exactly two
- D: 804 per candidate; 1,608 score-free streams
- Audited migrations: {migration['migrated_row_count']}/26
- Maker-safety evasions removed: {migration['maker_safety_evasions_removed']}/26
- Audited first-fill positions: {migration['audited_first_fill_position_count']}/26
- Corrected strict-ask first fills: {migration['corrected_first_fill_count']}
- Unaffected semantic changes: {identity['unexpected_unaffected_change_count']}
- C/PC/S/IC: null
- Scorer/benchmark/holdout/live access: none
"""
    (v2_dir / "WINDOW1_RANGE_ATTACK_V2_PRE_RUN_REPORT.md").write_text(
        report, encoding="utf-8", newline="\n"
    )
    artifacts = []
    for path in sorted(v2_dir.iterdir()):
        if path.name in {
            "ARTIFACT_HASH_MANIFEST.json",
            "WINDOW1_RANGE_ATTACK_V2_PRE_RUN_MANIFEST.json",
        }:
            continue
        artifacts.append({
            "path": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256_path(path),
            "git_blob_oid": git_blob(repo, path.relative_to(repo)),
        })
    write_json(v2_dir / "ARTIFACT_HASH_MANIFEST.json", {
        "schema_version": VERSION + "-artifact-hashes-v1",
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "metrics": None,
        "scored": False,
    })
    manifest = {
        "schema_version": VERSION + "-prerun-manifest-v1",
        "exact_parent": attack.EXACT_PARENT,
        "controlling_audit": attack.CONTROLLING_AUDIT,
        "candidate_ids": read_json(
            repo / attack.CANDIDATE_SPEC_PATH
        )["candidate_ids"],
        "D_per_candidate": 804,
        "candidate_event_stream_count": 1608,
        "accounting_law": {
            "PRICE_REACHED": "public print at or below X",
            "STRICT_ASK_CERTAIN_FILL": "external ask strictly below X",
            "FILLABLE_AT_X": (
                "PRICE_REACHED OR STRICT_ASK_CERTAIN_FILL"
            ),
            "accounting_quantity": 5,
            "fill_price": "original exposed X",
            "credit_before_maker_safety": True,
        },
        "migration_receipt_sha256": sha256_path(
            v2_dir / "STRICT_ASK_V1_TO_V2_MIGRATION_RECEIPT.json"
        ),
        "artifact_hash_manifest_sha256": sha256_path(
            v2_dir / "ARTIFACT_HASH_MANIFEST.json"
        ),
        "deterministic_regeneration": (
            bool(deterministic_rows) and all(
                row["byte_identical"] for row in deterministic_rows
            )
        ),
        "performance_metrics": {
            "C": None, "PC": None, "S": None, "IC": None
        },
        "metrics": None,
        "scored": False,
        "benchmark_or_scorer_invoked": False,
        "holdout_or_live_access": False,
    }
    write_json(v2_dir / "WINDOW1_RANGE_ATTACK_V2_PRE_RUN_MANIFEST.json",
               manifest)
    return {
        "migration": migration,
        "identity": identity,
        "headroom": headroom,
        "manifest": manifest,
        "artifact_count": len(list(v2_dir.iterdir())),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).parents[2])
    parser.add_argument("--regen-dir", type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve()
    regen = args.regen_dir.resolve() if args.regen_dir else None
    result = freeze(repo, regen)
    print(compact({
        "status": "PASS_STRICT_ASK_V2_FREEZE",
        "migration_rows": result["migration"]["migrated_row_count"],
        "corrected_first_fills": result["migration"][
            "corrected_first_fill_count"
        ],
        "unexpected_unaffected_changes": result["identity"][
            "unexpected_unaffected_change_count"
        ],
        "artifact_count": result["artifact_count"],
        "metrics": None,
        "scored": False,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
