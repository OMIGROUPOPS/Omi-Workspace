import importlib.util
import json
import sqlite3
from pathlib import Path


SCRIPT = (
    Path(__file__).parents[1] / "analysis" / "window1_start_ledger.py"
)
SPEC = importlib.util.spec_from_file_location("window1_start_ledger", SCRIPT)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(module)


def test_exact_precedes_bound_and_schedule():
    result = module.choose_start([
        {
            "source": "tape",
            "timestamp": 200.0,
            "confidence": "low",
            "authority_tier": 4,
            "exact_point": False,
        },
        {
            "source": "first_point",
            "timestamp": 100.0,
            "confidence": "high",
            "authority_tier": 2,
            "exact_point": True,
        },
    ], 50.0, 60)
    assert result["start_state"] == "verified_exact"
    assert result["selected_source"] == "first_point"
    assert result["boundary_censored"] is False
    assert result["safe_prestart_cutoff_inclusive"] is False


def test_schedule_fallback_is_censored():
    result = module.choose_start([], 100.0, 60)
    assert result["start_state"] == "schedule_only_censored"
    assert result["verified_start_utc"] is None
    assert result["boundary_censored"] is True


def test_nonlive_milestone_is_rejected():
    rows = module.official_and_bound_candidates([{
        "event_type": "gun_fired",
        "source": "milestone_official",
        "receipt_ts": 200.0,
        "details": {
            "ms_status": "SCH",
            "official_start_ep": 250.0,
        },
        "log_source": "test",
    }])
    assert rows[0]["authority_tier"] is None
    assert rows[0]["confidence"] == "rejected"


def test_te_live_page_first_sighting_is_a_bound_not_exact_start():
    rows = module.exact_te_candidates("E", [{
        "event_type": "gun_truth_delta",
        "source": "tape_latch",
        "receipt_ts": 300.0,
        "details": {
            "event": "E",
            "truth_src": "te_scoreboard",
            "te_first_inplay": "2026-07-12 04:00:00 PM",
            "te_match_id": "private-upstream-id",
            "match_how": "both_legs",
        },
        "log_source": "test",
    }])
    assert len(rows) == 1
    assert rows[0]["source"] == "te_scoreboard_first_observed_inplay"
    assert rows[0]["exact_point"] is False
    ruling = module.choose_start(rows, 100.0, 60)
    assert ruling["start_state"] == "bounded_live_by_timestamp"
    assert ruling["verified_start_utc"] is None


def test_earliest_accepted_transition_sets_the_safety_bound():
    ruling = module.choose_start([
        {
            "source": "higher-authority-later",
            "timestamp": 200.0,
            "confidence": "medium",
            "authority_tier": 2,
            "exact_point": False,
        },
        {
            "source": "lower-authority-earlier",
            "timestamp": 150.0,
            "confidence": "medium",
            "authority_tier": 3,
            "exact_point": False,
        },
    ], 100.0, 60)
    assert ruling["selected_source"] == "higher-authority-later"
    assert ruling["known_live_by_source"] == "lower-authority-earlier"
    assert module.parse_epoch(
        ruling["known_live_by_utc"]
    ) == 150.0


def test_bounded_interval_exposes_only_the_proven_prestart_cutoff():
    ruling = module.choose_start([
        {
            "source": "provider-not-started",
            "timestamp": 120.0,
            "confidence": "medium",
            "authority_tier": 2,
            "exact_point": False,
            "bound_direction": "not_live_through",
            "timestamp_basis": "provider_receipt",
        },
        {
            "source": "scoreboard-live",
            "timestamp": 180.0,
            "confidence": "medium",
            "authority_tier": 2,
            "exact_point": False,
            "bound_direction": "live_by",
            "timestamp_basis": "collector_receipt",
        },
    ], 100.0, 60)
    assert ruling["start_state"] == "bounded_start_interval"
    assert module.parse_epoch(ruling["not_live_through_utc"]) == 120
    assert module.parse_epoch(ruling["known_live_by_utc"]) == 180
    assert module.parse_epoch(ruling["safe_prestart_cutoff_utc"]) == 120
    assert ruling["definitely_prestart_scoring_available"] is True
    assert ruling["safe_prestart_cutoff_inclusive"] is True


def test_milestone_shadow_accepts_fresh_live_and_rejects_stale_live(
    tmp_path,
):
    path = tmp_path / "milestone.jsonl"
    rows = [
        {
            "event": "E-FRESH",
            "ts": 200.0,
            "ms_status": "live",
            "ms_start_ep": 100.0,
            "source_id": "public-provider-id",
        },
        {
            "event": "E-STALE",
            "ts": 100.0 + 7 * 3600,
            "ms_status": "live",
            "ms_start_ep": 100.0,
            "source_id": "public-provider-id",
        },
    ]
    path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )
    candidates, summary = module.milestone_shadow_candidates(
        path, {"E-FRESH", "E-STALE"}
    )
    assert candidates["E-FRESH"][0]["exact_point"] is True
    assert candidates["E-STALE"][0]["exact_point"] is False
    assert summary["accepted_exact_rows"] == 1
    assert summary["rejected_rows"] == 1


def test_public_final_milestone_requires_complete_manifest(tmp_path):
    normalized = tmp_path / "milestones.jsonl"
    normalized.write_text(json.dumps({
        "event_id": "E",
        "status": "P",
        "start_utc": "2026-07-12T12:00:00Z",
        "exported_utc": "2026-07-23T12:00:00Z",
        "milestone_identity_sha256": "m",
        "source_identity_sha256": "s",
    }) + "\n", encoding="utf-8")
    digest = __import__("hashlib").sha256(
        normalized.read_bytes()
    ).hexdigest()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({
        "scope": {"D": 804, "event_queries": 804},
        "pagination": {
            "all_terminal_cursors_empty": True,
            "failed_event_count": 0,
        },
        "artifacts": {"normalized_sha256": digest},
    }), encoding="utf-8")
    rows, summary = module.public_milestone_candidates(
        normalized, manifest, {"E"}
    )
    assert rows["E"][0]["exact_point"] is True
    assert summary["pagination_complete"] is True


def test_log_inventory_includes_july_19_archive(tmp_path):
    for day in (18, 19):
        (tmp_path / f"live_v3_202607{day}.jsonl.gz").write_bytes(b"x")
    (tmp_path / "live_v3_20260720.jsonl").write_bytes(b"x")
    names = {
        path.name for path in module.log_paths(
            tmp_path, "live_v3_20260720.jsonl"
        )
    }
    assert "live_v3_20260719.jsonl.gz" in names


def test_pc_nc_ic_semantics_are_not_partitions():
    completed = [
        {"under_par": True, "negative_pair": True, "both_negative": False},
        {"under_par": False, "negative_pair": True, "both_negative": True},
    ]
    C = len(completed)
    PC = sum(row["under_par"] for row in completed)
    NC = sum(row["negative_pair"] for row in completed)
    IC = sum(row["both_negative"] for row in completed)
    assert (C, PC, NC, IC) == (2, 1, 2, 1)
    assert PC + NC + IC > C


def test_live_scores_current_row_is_only_a_known_live_by_bound(tmp_path):
    database = tmp_path / "tennis.db"
    connection = sqlite3.connect(database)
    connection.executescript(
        """
        CREATE TABLE players (kalshi_code TEXT, name TEXT);
        CREATE TABLE live_scores (
            te_match_id TEXT, player1 TEXT, player2 TEXT,
            p1_sets INTEGER, p2_sets INTEGER, status TEXT,
            kalshi_ticker TEXT, last_updated TEXT
        );
        INSERT INTO players VALUES ('AAA', 'Alpha Person');
        INSERT INTO players VALUES ('BBB', 'Beta Person');
        INSERT INTO live_scores VALUES (
            'upstream-id', 'Alpha Person', 'Beta Person',
            1, 0, 'live', 'AAA', '2026-07-12 04:05:00 PM'
        );
        """
    )
    connection.close()
    events = [{
        "event_id": "E",
        "scheduled_start_exchange_ts": "2026-07-12T20:00:00Z",
        "legs": [{"leg": "AAA"}, {"leg": "BBB"}],
    }]
    rows, summary = module.live_score_candidates(database, events)
    assert summary["uniquely_joined_events"] == 1
    assert rows["E"][0]["exact_point"] is False
    assert rows["E"][0]["bound_direction"] == "live_by"
    assert rows["E"][0]["timestamp_basis"] == (
        "local_te_results_scrape_receipt_et"
    )


def test_post_sample_official_start_requires_consistent_inplay_evidence(
    tmp_path,
):
    shadow = tmp_path / "shadow.jsonl"
    shadow.write_text(
        "\n".join([
            json.dumps({
                "event": "E", "ts": 200,
                "ms_status": "interrupted", "ms_start_ep": 100,
            }),
            json.dumps({
                "event": "E", "ts": 300,
                "ms_status": "live", "ms_start_ep": 100,
            }),
        ]) + "\n",
        encoding="utf-8",
    )
    bells = tmp_path / "bells.json"
    bells.write_text(json.dumps({
        "E": {
            "status": "live", "start_ep": 100,
            "fetched_at": 400, "final": False,
        }
    }), encoding="utf-8")
    result = module.post_sample_official_start("E", shadow, bells)
    assert module.parse_epoch(result["verified_start_utc"]) == 100
    assert result["reported_starts_consistent_within_one_second"] is True
