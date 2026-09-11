"""Synthetic input/lineage guards; no population or remote access."""
from __future__ import annotations

import copy
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

import feature_panel_run as run


def fixture():
    meta = dict(event_id="event", ticker="event-LEG", category="ATP_MAIN",
        formation_end_epoch=10, bell_epoch=100, true_print_count_in_span=2,
        _path_point_count=3)
    manifest = dict(object="spaces:ticks/a.csv.gz", consolidation_etag="a"*32,
        compressed_md5="a"*32, compressed_sha256="b"*64, model_eligible=True,
        consolidation_object_match="VERIFIED_MD5_ETAG")
    source = dict({k: meta[k] for k in run.IDENTITY}, schema=run.SOURCE_SCHEMA,
        source_manifest=[manifest], excluded_unverified_objects=[],
        checks=dict(final_count_matches=True, path_volume_matches=True,
            accepted_count=2, path_volume_points_checked=3), minute_features=[], books=[],
        first_two_sided_book_epoch=None)
    witness = dict({k: meta[k] for k in run.IDENTITY}, columns=["ts", "price", "size", "rowid", "src"],
        positive_prints=[[12, 50, 1, 1, "spaces_trades"], [20, 51, 2, 2, "spaces_trades"]])
    supplemental = dict({k: meta[k] for k in run.IDENTITY}, schema=run.SUPPLEMENTAL_SCHEMA,
        oi_columns=["available_epoch", "open_interest_at_minute_end", "open_interest_ffill", "open_interest_delta_from_prior_minute"],
        oi=[[60, None, None, None]], oi_status="NULL", odds_poll_epochs=[30],
        odds_status="EXACT_EVENT_IN_SPAN_ARCHIVE_POLLS", odds_span=dict(formation=10, bell=100),
        ws_depth_status="UNVERIFIED_SEQUENCE_INTEGRITY")
    return meta, source, witness, supplemental


class InputTests(unittest.TestCase):
    def test_worker_count_is_execution_only_and_positive(self):
        arguments = ["--root", "repo", "--sources", "sources", "--witnesses", "witnesses",
            "--supplemental", "supplemental", "--source-receipt", "source-receipt",
            "--supplemental-receipt", "supplemental-receipt", "--out", "out",
            "--category", "ATP_MAIN", "--cache-budget-mib", "512", "--batch-size", "16"]
        self.assertEqual(run.parser().parse_args(arguments).workers, 1)
        self.assertEqual(run.parser().parse_args(arguments + ["--workers", "4"]).workers, 4)
        for workers in (0, -1):
            with self.assertRaisesRegex(ValueError, "POSITIVE_EXECUTION_BUDGETS"):
                run.run(SimpleNamespace(batch_size=16, cache_budget_mib=512, workers=workers))

    def test_input_sha_and_size_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"input.bin"
            path.write_bytes(b"bound")
            proof = dict(sha256=hashlib.sha256(b"bound").hexdigest(), bytes=5)
            self.assertEqual(run.check_file(path, proof, "fixture")["bytes"], 5)
            path.write_bytes(b"other")
            with self.assertRaisesRegex(ValueError, "INPUT_SHA"):
                run.check_file(path, proof, "fixture")

    def test_valid_original_etag_and_unknown_manifest_not_trusted(self):
        meta, source, _, _ = fixture()
        self.assertEqual(run.validate_source_row(source, meta)["unverified_objects"], 0)
        for change in (None, "not-simple-etag", "c"*32):
            changed = copy.deepcopy(source)
            changed["source_manifest"][0]["consolidation_etag"] = change
            with self.assertRaisesRegex(ValueError, "ETAG_MISMATCH_OR_MISSING"):
                run.validate_source_row(changed, meta)

    def test_excluded_object_requires_affected_features_absent(self):
        meta, source, _, _ = fixture()
        item = source["source_manifest"][0]
        item.update(model_eligible=False, compressed_sha256=None, consolidation_etag=None)
        source["excluded_unverified_objects"] = [item["object"]]
        self.assertTrue(run.validate_source_row(source, meta)["book_wake_excluded"])
        source["first_two_sided_book_epoch"] = 20
        with self.assertRaisesRegex(ValueError, "UNVERIFIED_BOOK_WAKE_RETAINED"):
            run.validate_source_row(source, meta)
        source["first_two_sided_book_epoch"] = None
        source["books"] = [dict(source_object=item["object"])]
        with self.assertRaisesRegex(ValueError, "UNVERIFIED_BOOK_RETAINED"):
            run.validate_source_row(source, meta)

    def test_unverified_aggressors_cannot_silently_be_zero(self):
        meta, source, _, _ = fixture()
        item = source["source_manifest"][0]
        item.update(object="spaces:trades/a.csv.gz", model_eligible=False, consolidation_etag=None)
        source["excluded_unverified_objects"] = [item["object"]]
        source["minute_features"] = [dict(positive_size_trade_count=1, known_taker_positive_print_count=0,
            taker_flow_contracts=None, taker_yes_contracts=None, taker_no_contracts=None)]
        run.validate_source_row(source, meta)
        source["minute_features"][0]["taker_flow_contracts"] = 0
        with self.assertRaisesRegex(ValueError, "UNVERIFIED_AGGRESSOR_FLOW_RETAINED"):
            run.validate_source_row(source, meta)
        source["minute_features"][0]["positive_size_trade_count"] = 0
        run.validate_source_row(source, meta)  # zero observed prints legitimately has zero flow

    def test_witness_size_clock_and_rowid(self):
        meta, _, witness, _ = fixture()
        run.validate_witness_row(witness, meta)
        for column, value in ((2, 0), (0, 100), (4, "book_transition")):
            changed = copy.deepcopy(witness)
            changed["positive_prints"][0][column] = value
            with self.assertRaisesRegex(ValueError, "INVALID_POSITIVE"):
                run.validate_witness_row(changed, meta)
        witness["positive_prints"].reverse()
        with self.assertRaisesRegex(ValueError, "NOT_STRICTLY_ORDERED"):
            run.validate_witness_row(witness, meta)

    def test_supplemental_is_allowlisted_and_does_not_replace_core(self):
        _, source, _, supplemental = fixture()
        merged = run.merge_supplemental(copy.deepcopy(source), supplemental)
        self.assertEqual(merged["schema"], run.SOURCE_SCHEMA)
        self.assertIsNone(merged["oi"][0][1])
        for field in ("books", "clock_provenance", "minute_features"):
            with self.assertRaisesRegex(ValueError, "UNAUTHORIZED_KEYS"):
                run.merge_supplemental(copy.deepcopy(source), dict(supplemental, **{field: []}))
        with self.assertRaisesRegex(ValueError, "WOULD_OVERWRITE"):
            run.merge_supplemental(merged, supplemental)

    def test_spool_requires_both_original_locked_hashes(self):
        sha = "a"*64
        source = dict(library_sha256="b"*64, cutter_sha256="c"*64,
            source_store=dict(original_store_sha256_from_library=sha, private_spool_sha256="d"*64),
            source_spool=dict(status="SEALED_PRIVATE_SOURCE_SPOOL", limit_legs=None,
                library_sha256="b"*64, cutter_sha256="c"*64, output=dict(sha256="d"*64),
                source_store=dict(full_hash_recomputed=True, sha256_start=sha, sha256_end=sha,
                    sha256_from_library=sha), lock=dict(held_through_receipt_publication=True)))
        library = dict(source_snapshot=dict(sha256=sha))
        run.validate_locked_store(source, library)
        source["source_spool"]["source_store"]["sha256_end"] = "e"*64
        with self.assertRaisesRegex(ValueError, "TWO_HASH_SHARED_LOCK"):
            run.validate_locked_store(source, library)

    def test_local_odds_pin_must_match_remote_observation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"audit.json"
            path.write_text(json.dumps(dict(archive_files=[dict(path="C:\\tmp\\june.parquet", sha256="a"*64, bytes=3)])))
            remote = dict(sources=[dict(kind="ODDS_POLL_AVAILABILITY", path="/archive/june.parquet", sha256="a"*64, bytes=3)])
            self.assertEqual(run.bind_odds_archives(remote, path)["archives"], 1)
            remote["sources"][0]["sha256"] = "b"*64
            with self.assertRaisesRegex(ValueError, "NOT_LOCAL_AUDIT_PIN"):
                run.bind_odds_archives(remote, path)

    def test_streamed_adapter_prepares_before_retaining_and_preserves_null(self):
        meta, source, witness, supplemental = fixture()
        with tempfile.TemporaryDirectory() as directory:
            paths = {}
            for name, row in (("sources", source), ("witnesses", witness), ("supplemental", supplemental)):
                path = Path(directory)/(name+".jsonl.gz")
                with gzip.open(path, "wt") as stream:
                    stream.write(json.dumps(row)+"\n")
                paths[name] = path
            sources, witnesses, totals = run.load_sources(SimpleNamespace(**paths), {meta["ticker"]: meta},
                {meta["ticker"]}, dict(counts=dict(legs=1)), dict(counts=dict(legs=1)))
            stored = sources[meta["ticker"]]
            self.assertIsInstance(stored["minute_features"], dict)
            self.assertIsInstance(stored["books"], dict)
            self.assertIsInstance(stored["open_interest"], dict)
            self.assertIn("_prefix", witnesses[meta["ticker"]])
            self.assertEqual(totals["required_legs"], 1)

    def test_determinism_ignores_only_explicit_elapsed_walltime(self):
        with tempfile.TemporaryDirectory() as directory:
            first, second = Path(directory)/"a", Path(directory)/"b"
            first.mkdir(); second.mkdir()
            content = dict(numerical_execution=dict(elapsed_seconds=1, batch_size=2),
                scientific_clock=dict(floor_mtb=480, elapsed_seconds=20))
            name = "FEATURE_PANEL_RECEIPT.json"
            (first/name).write_text(json.dumps(content))
            content["numerical_execution"]["elapsed_seconds"] = 9
            (second/name).write_text(json.dumps(content))
            self.assertEqual(run.compare_runs(first, second)["status"], "DETERMINISTIC")
            content["scientific_clock"]["elapsed_seconds"] = 21
            (second/name).write_text(json.dumps(content))
            with self.assertRaisesRegex(ValueError, "CONTENT_MISMATCH"):
                run.compare_runs(first, second)

    def test_external_output_only_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)/"repo"
            root.mkdir()
            with self.assertRaisesRegex(ValueError, "OUTSIDE_REPOSITORY"):
                run.ensure_external_output(root, root/"raw")
            external = Path(directory)/"run"
            self.assertEqual(run.ensure_external_output(root, external), external.resolve())
            external.mkdir(); (external/"prior.json").write_text("{}")
            with self.assertRaisesRegex(ValueError, "REFUSE_NONEMPTY"):
                run.ensure_external_output(root, external)


if __name__ == "__main__":
    unittest.main()
