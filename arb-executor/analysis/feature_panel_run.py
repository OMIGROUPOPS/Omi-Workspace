"""Hash-bound local launcher for the feature-panel bench; no store/engine writes.

Raw extracts, witnesses, per-receipt arrays and run output must be outside Git.
This launcher rejects partial/smoke extracts. Original objects without a simple
matching consolidation ETag are permitted only when the extractor explicitly
excluded all affected model features. A VERIFIED label alone is not evidence.
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
from contextlib import nullcontext
import gc
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess

import feature_panel as panel
import feature_panel_bench as bench
import feature_panel_scoring as scoring
import conduct_scoreboard as conduct
import tune_bench_v2_survivorship as reference
from feature_panel_checkpoint import CheckpointStore
from feature_panel_execution import compact_sampler_copy


BASELINES = {"ATP_MAIN": "c7825925", "ATP_CHALL": "969111f3"}
AUTHORIZATION_RECEIPT_COMMIT = "87049680"
HELDOUT_MONTHS = ("2026-06",)  # Operator-approved separate held-out month.
SOURCE_SCHEMA = "TICK_LIBRARY_FEATURE_SOURCES_V1"
SUPPLEMENTAL_SCHEMA = "FEATURE_SUPPLEMENTAL_AVAILABILITY_V1"
IDENTITY = ("event_id", "ticker", "category", "formation_end_epoch", "bell_epoch")
SUPPLEMENTAL_FIELDS = frozenset(IDENTITY + ("schema", "oi_columns", "oi", "oi_status",
    "odds_poll_epochs", "odds_status", "odds_span", "ws_depth_status"))
WALL_CLOCK_PATHS = {"FEATURE_PANEL_RECEIPT.json": (("numerical_execution", "elapsed_seconds"),)}


def digest(path):
    return panel.sha256(Path(path))


def json_file(path):
    with Path(path).open(encoding="utf-8-sig") as stream:
        return json.load(stream)


def valid_sha(value):
    return isinstance(value, str) and re.fullmatch("[0-9a-fA-F]{64}", value) is not None


def check_file(path, binding, label):
    path = Path(path).resolve(strict=True)
    expected = binding.get("sha256")
    if not valid_sha(expected) or digest(path) != expected.lower():
        raise ValueError("INPUT_SHA_MISMATCH_OR_UNBOUND:"+label)
    if binding.get("bytes") is not None and path.stat().st_size != binding["bytes"]:
        raise ValueError("INPUT_BYTE_SIZE_MISMATCH:"+label)
    return dict(path=str(path), sha256=expected.lower(), bytes=path.stat().st_size)


def git_json(root, commit, relative):
    raw = subprocess.check_output(["git", "show", commit+":"+relative], cwd=root)
    return json.loads(raw), dict(commit=commit, path=relative, sha256=hashlib.sha256(raw).hexdigest())


def bind_baseline(root, category):
    relative = "arb-executor/analysis/tune_bench_v2_ticks/"+category+"/TUNE_BENCH_RECEIPT.json"
    baseline, proof = git_json(root, BASELINES[category], relative)
    joined = copy.deepcopy(baseline)
    proofs = dict(corrected_numerical_baseline=proof)
    if "matched_step_first" not in joined:
        filed, auth_proof = git_json(root, AUTHORIZATION_RECEIPT_COMMIT,
            "arb-executor/analysis/tune_bench_v2_ticks/ATP_MAIN/TUNE_BENCH_RECEIPT.json")
        if (any(filed["organ_contract"].get(key) != value for key, value in baseline["organ_contract"].items())
                or set(filed["organ_contract"])-set(baseline["organ_contract"])-{"taxonomy_rules"}):
            raise ValueError("FILED_AUTHORIZATION_ORGAN_CONTRACT_DRIFT")
        joined["organ_contract"] = copy.deepcopy(filed["organ_contract"])
        joined["matched_step_first"] = {"criterion": filed["matched_step_first"]["criterion"]}
        proofs["matched_authorization_and_filed_taxonomy_only"] = dict(auth_proof,
            prior_existing_contract_keys_unchanged=True,
            newly_filed_contract_keys=sorted(set(filed["organ_contract"])-set(baseline["organ_contract"])))
    scoring.ScoreContract.from_baseline(joined)
    bound = conduct.bound_inputs(Path(root))
    equivalence = conduct.verify_reference(reference, root)
    return joined, dict(receipts=proofs, reference=equivalence,
        conduct=bound["conduct"], conduct_constants_rule="Read-only bound_inputs regex on real engine/functionable files; no imported OS"), bound["conduct"]


def validate_locked_store(receipt, library_receipt):
    """Require the full locked-store or sealed-spool proof, never smoke stats."""
    expected = library_receipt["source_snapshot"]["sha256"]
    source = receipt.get("source_store", {})
    if source.get("original_store_sha256_from_library") != expected:
        raise ValueError("SOURCE_STORE_NOT_LIBRARY_SNAPSHOT")
    spool = receipt.get("source_spool")
    if spool is not None:
        if (spool.get("status") != "SEALED_PRIVATE_SOURCE_SPOOL" or spool.get("limit_legs") is not None
                or spool.get("library_sha256") != receipt["library_sha256"]
                or spool.get("cutter_sha256") != receipt["cutter_sha256"]
                or not valid_sha(spool.get("output", {}).get("sha256"))
                or source.get("private_spool_sha256") != spool["output"]["sha256"]):
            raise ValueError("INVALID_SEALED_SOURCE_SPOOL_CHAIN")
        state, lock = spool.get("source_store", {}), spool.get("lock", {})
        if state.get("sha256_from_library") != expected:
            raise ValueError("SPOOL_STORE_NOT_LIBRARY_SNAPSHOT")
    else:
        state, lock = source, receipt.get("lock", {})
    if (state.get("full_hash_recomputed") is not True or state.get("sha256_start") != expected
            or state.get("sha256_end") != expected or lock.get("held_through_receipt_publication") is not True):
        raise ValueError("FULL_TWO_HASH_SHARED_LOCK_PROOF_REQUIRED")


def bind_odds_archives(supplemental, audit_path):
    observed = [row for row in supplemental["sources"] if row["kind"] == "ODDS_POLL_AVAILABILITY"]
    if not observed:
        return dict(status="NOT_EXTRACTED", archives=0)
    if audit_path is None:
        raise ValueError("LOCAL_ODDS_AUDIT_RECEIPT_REQUIRED")
    audit = json_file(audit_path)
    # Compare exact archive identity/hash, never just the remote VERIFIED label.
    names = lambda path: str(path).replace("\\", "/").rsplit("/", 1)[-1]
    filed = {names(row["path"]): row for row in audit["archive_files"]}
    for row in observed:
        name = names(row["path"])
        if name not in filed or row["sha256"] != filed[name]["sha256"]:
            raise ValueError("ODDS_ARCHIVE_NOT_LOCAL_AUDIT_PIN:"+name)
        if filed[name].get("bytes") is not None and row["bytes"] != filed[name]["bytes"]:
            raise ValueError("ODDS_ARCHIVE_PIN_BYTES_MISMATCH:"+name)
    return dict(status="LOCAL_FILED_ARCHIVE_HASHES_VERIFIED", archives=len(observed),
        audit_path=str(Path(audit_path).resolve()), audit_sha256=digest(audit_path),
        names=[names(row["path"]) for row in observed])


def verify_inputs(args, baseline):
    """Hash every immutable local input before opening any population rows."""
    durable = args.root/"arb-executor/data/durable"
    paths = dict(library=durable/"RANGE_OVERLAP_LIBRARY_TICKS.jsonl.gz",
        library_receipt=durable/"RANGE_OVERLAP_LIBRARY_TICKS_RECEIPT.json",
        counts=durable/"RANGE_OVERLAP_LIBRARY_TICKS_PRINT_COUNTS.jsonl.gz",
        counts_receipt=durable/"RANGE_OVERLAP_LIBRARY_TICKS_PRINT_COUNTS_RECEIPT.json")
    registry = dict(library=check_file(paths["library"], baseline["input_library"], "library"),
        library_receipt=check_file(paths["library_receipt"], baseline["source_receipt"], "library receipt"),
        counts=check_file(paths["counts"], {"sha256": baseline["exact_print_counts"]["sidecar_sha256"]}, "print counts"),
        counts_receipt=check_file(paths["counts_receipt"],
            {"sha256": baseline["exact_print_counts"]["sidecar_receipt_sha256"]}, "print count receipt"))
    library_receipt = json_file(paths["library_receipt"])
    count_receipt = json_file(paths["counts_receipt"])
    if (library_receipt["output"]["sha256"] != registry["library"]["sha256"]
            or count_receipt["library"]["sha256"] != registry["library"]["sha256"]
            or count_receipt["output"]["sha256"] != registry["counts"]["sha256"]):
        raise ValueError("DURABLE_RECEIPT_CHAIN_MISMATCH")
    source = json_file(args.source_receipt)
    supplemental = json_file(args.supplemental_receipt)
    if (source.get("schema") != SOURCE_SCHEMA or source.get("status") not in
            ("VERIFIED", "VERIFIED_WITH_UNVERIFIED_SOURCES_EXCLUDED")
            or source.get("limit_legs") is not None or args.category not in source.get("categories", [])):
        raise ValueError("COMPLETE_CATEGORY_SOURCE_EXTRACT_REQUIRED")
    if (source.get("library_sha256") != registry["library"]["sha256"]
            or source.get("library_receipt_sha256") != registry["library_receipt"]["sha256"]
            or source.get("cutter_sha256") != library_receipt["builder"]["sha256"]):
        raise ValueError("SOURCE_EXTRACT_LIBRARY_OR_CUTTER_MISMATCH")
    validate_locked_store(source, library_receipt)
    if (supplemental.get("schema") != SUPPLEMENTAL_SCHEMA or supplemental.get("status") not in
            ("VERIFIED", "REMOTE_HASH_RECORDED_REQUIRES_LOCAL_PIN_VALIDATION")
            or supplemental.get("limit_legs") is not None
            or supplemental.get("library_sha256") != registry["library"]["sha256"]):
        raise ValueError("SUPPLEMENTAL_LIBRARY_OR_COMPLETENESS_MISMATCH")
    extractor = args.root/"arb-executor/analysis/feature_panel_extract.py"
    extractor_sha = digest(extractor)
    core_extractor = getattr(args, "core_extractor", None) or extractor
    core_proof = check_file(core_extractor, {"sha256": source.get("extractor_sha256")}, "reviewed core extractor snapshot")
    if supplemental.get("extractor_sha256") != extractor_sha:
        raise ValueError("SUPPLEMENTAL_EXTRACTOR_NOT_LOCAL_REVIEWED_VERSION")
    odds_proof = bind_odds_archives(supplemental, getattr(args, "odds_audit_receipt", None))
    registry.update(sources=check_file(args.sources, source["outputs"]["FEATURE_SOURCES.jsonl.gz"], "feature sources"),
        witnesses=check_file(args.witnesses, source["outputs"]["POSITIVE_PRINT_WITNESSES.jsonl.gz"], "positive print witnesses"),
        supplemental=check_file(args.supplemental, supplemental["output"], "supplemental"),
        source_receipt=dict(path=str(args.source_receipt.resolve()), sha256=digest(args.source_receipt)),
        supplemental_receipt=dict(path=str(args.supplemental_receipt.resolve()), sha256=digest(args.supplemental_receipt)),
        extractor=dict(path=str(extractor.resolve()), sha256=extractor_sha),
        core_extractor=core_proof, local_odds_archive_validation=odds_proof,
        original_store=source["source_store"], sealed_spool=source.get("source_spool"),
        source_status=source["status"], source_rules=source["rules"], supplemental_sources=supplemental["sources"])
    for row in supplemental["sources"]:
        if not valid_sha(row.get("sha256")):
            raise ValueError("UNBOUND_SUPPLEMENTAL_SOURCE")
    return paths, registry, source, supplemental


def jsonl(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8-sig") as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def check_identity(row, metadata, label):
    ticker = row.get("ticker")
    if ticker not in metadata:
        raise ValueError("NON_LIBRARY_SOURCE_ROW:"+str(ticker))
    meta = metadata[ticker]
    for key in IDENTITY:
        if row.get(key) != meta[key]:
            raise ValueError("SOURCE_IDENTITY_OR_SPAN_MISMATCH:"+label+":"+str(ticker)+":"+key)
    return meta


def validate_source_row(row, meta):
    if row.get("schema") != SOURCE_SCHEMA:
        raise ValueError("FEATURE_SOURCE_SCHEMA_MISMATCH")
    proof = row.get("checks", {})
    if (proof.get("final_count_matches") is not True or proof.get("path_volume_matches") is not True
            or proof.get("accepted_count") != meta["true_print_count_in_span"]
            or proof.get("path_volume_points_checked") != meta["_path_point_count"]):
        raise ValueError("SOURCE_PATH_AND_COUNT_NOT_REPRODUCED:"+row["ticker"])
    manifests = row.get("source_manifest")
    if not isinstance(manifests, list):
        raise ValueError("SOURCE_OBJECT_MANIFEST_REQUIRED")
    objects = {}
    for entry in manifests:
        obj = entry.get("object")
        if not isinstance(obj, str) or obj in objects:
            raise ValueError("DUPLICATE_OR_MISSING_SOURCE_OBJECT")
        objects[obj] = entry
        if entry.get("model_eligible") is True:
            etag = entry.get("consolidation_etag")
            simple = etag.strip('"').lower() if isinstance(etag, str) else ""
            if (re.fullmatch("[0-9a-f]{32}", simple) is None or entry.get("compressed_md5") != simple
                    or not valid_sha(entry.get("compressed_sha256"))
                    or entry.get("consolidation_object_match") != "VERIFIED_MD5_ETAG"):
                raise ValueError("MODEL_SOURCE_ETAG_MISMATCH_OR_MISSING:"+obj)
        elif entry.get("model_eligible") is not False:
            raise ValueError("SOURCE_MODEL_ELIGIBILITY_NOT_EXPLICIT:"+obj)
    excluded = {key for key, entry in objects.items() if not entry["model_eligible"]}
    if excluded != set(row.get("excluded_unverified_objects", [])):
        raise ValueError("UNVERIFIED_SOURCE_EXCLUSIONS_NOT_EXPLICIT")
    for book in row.get("books", []):
        if book.get("source_object") not in objects or book["source_object"] in excluded:
            raise ValueError("UNVERIFIED_BOOK_RETAINED")
    bad_books = any(key.startswith("spaces:ticks/") for key in excluded)
    if bad_books and any(row.get(key) is not None for key in ("first_source_book_epoch",
            "first_two_sided_book_epoch", "first_source_book_in_span_epoch",
            "last_source_book_before_formation_epoch", "first_source_book_was_two_sided")):
        raise ValueError("UNVERIFIED_BOOK_WAKE_RETAINED")
    bad_trades = any(key.startswith("spaces:trades/") for key in excluded)
    if bad_trades:
        for minute in row.get("minute_features", []):
            if minute.get("positive_size_trade_count", 0) and (minute.get("known_taker_positive_print_count") != 0
                    or any(minute.get(k) is not None for k in
                           ("taker_flow_contracts", "taker_yes_contracts", "taker_no_contracts"))):
                raise ValueError("UNVERIFIED_AGGRESSOR_FLOW_RETAINED")
    return dict(unverified_objects=len(excluded), original_objects=len(objects),
        no_original_objects=not objects, book_wake_excluded=bad_books, aggressor_flow_excluded=bad_trades)


def validate_witness_row(row, meta):
    if row.get("columns") != ["ts", "price", "size", "rowid", "src"]:
        raise ValueError("POSITIVE_WITNESS_COLUMNS_MISMATCH")
    previous = None
    for item in row.get("positive_prints", []):
        if len(item) != len(row["columns"]):
            raise ValueError("POSITIVE_WITNESS_WIDTH_MISMATCH")
        ts, price, size, rowid, src = item
        if (not all(isinstance(v, (float, int)) and not isinstance(v, bool) and math.isfinite(v)
                    for v in (ts, price, size, rowid)) or size <= 0
                or not meta["formation_end_epoch"] <= ts < meta["bell_epoch"]
                or src in ("book_transition", "TUNE_SAMPLE") or not isinstance(src, str)):
            raise ValueError("INVALID_POSITIVE_PRINT_WITNESS")
        key = (ts, rowid)
        if previous is not None and key <= previous:
            raise ValueError("WITNESS_TIMESTAMP_ROWID_NOT_STRICTLY_ORDERED")
        previous = key
    if len(row.get("positive_prints", [])) > meta["true_print_count_in_span"]:
        raise ValueError("POSITIVE_PRINTS_EXCEED_ACCEPTED_COUNT")


def merge_supplemental(source, row):
    if row.get("schema") != SUPPLEMENTAL_SCHEMA or set(row)-SUPPLEMENTAL_FIELDS:
        raise ValueError("SUPPLEMENTAL_SCHEMA_OR_UNAUTHORIZED_KEYS")
    for key in IDENTITY:
        if source.get(key) != row.get(key):
            raise ValueError("SUPPLEMENTAL_IDENTITY_OR_SPAN_MISMATCH")
    if row.get("oi_columns") != ["available_epoch", "open_interest_at_minute_end",
            "open_interest_ffill", "open_interest_delta_from_prior_minute"]:
        raise ValueError("SUPPLEMENTAL_OI_COLUMNS_MISMATCH")
    formation, bell = row["formation_end_epoch"], row["bell_epoch"]
    epochs = [entry[0] for entry in row["oi"]]
    if any(len(entry) != len(row["oi_columns"]) for entry in row["oi"]):
        raise ValueError("SUPPLEMENTAL_OI_WIDTH_MISMATCH")
    if any(not formation <= epoch < bell for epoch in epochs) or epochs != sorted(set(epochs)):
        raise ValueError("SUPPLEMENTAL_OI_CLOCK_INVALID")
    odds = row.get("odds_poll_epochs", [])
    span = row.get("odds_span", {})
    if not formation <= span.get("formation", -math.inf) < span.get("bell", math.inf) <= bell:
        raise ValueError("SUPPLEMENTAL_ODDS_PAIR_SPAN_INVALID")
    if odds != sorted(set(odds)) or any(not span["formation"] <= epoch < span["bell"] for epoch in odds):
        raise ValueError("SUPPLEMENTAL_ODDS_CLOCK_INVALID")
    for key in SUPPLEMENTAL_FIELDS-set(IDENTITY)-{"schema"}:
        if key in source:
            raise ValueError("SUPPLEMENTAL_WOULD_OVERWRITE_SOURCE:"+key)
        if key in row:
            source[key] = row[key]
    source["supplemental_schema"] = row["schema"]
    return source


def load_sources(args, metadata, required, source_receipt, supplemental_receipt):
    """Validate all rows; retain only the requested tour's complete query/member set."""
    sources, witnesses, totals, extras = {}, {}, Counter(), {}
    seen = set()
    for row in jsonl(args.supplemental):
        check_identity(row, metadata, "supplemental")
        ticker = row["ticker"]
        if ticker in seen:
            raise ValueError("DUPLICATE_SUPPLEMENTAL_TICKER")
        seen.add(ticker)
        merge_supplemental({k: row[k] for k in IDENTITY}, row)
        if ticker in required:
            extras[ticker] = row
    if len(seen) != supplemental_receipt["counts"]["legs"] or required-seen:
        raise ValueError("INCOMPLETE_SUPPLEMENTAL_CENSUS")
    totals["supplemental_all_legs"] = len(seen)
    for label, path, keep in (("sources", args.sources, sources), ("witnesses", args.witnesses, witnesses)):
        seen = set()
        for row in jsonl(path):
            meta = check_identity(row, metadata, label)
            ticker = row["ticker"]
            if ticker in seen:
                raise ValueError("DUPLICATE_EXTRACT_TICKER:"+label+":"+ticker)
            seen.add(ticker)
            if label == "sources":
                checks = validate_source_row(row, meta)
                totals.update({name: int(value) for name, value in checks.items()})
            else:
                validate_witness_row(row, meta)
                totals["positive_prints"] += len(row["positive_prints"])
            if ticker in required:
                if label == "sources":
                    merge_supplemental(row, extras.pop(ticker))
                    panel.prepare_sources({ticker: row}, {})
                else:
                    panel.prepare_sources({}, {ticker: row})
                keep[ticker] = row
        if len(seen) != source_receipt["counts"]["legs"] or required-set(keep):
            raise ValueError("INCOMPLETE_EXTRACT_CENSUS:"+label)
        totals[label+"_all_legs"] = len(seen)
    if totals["unverified_objects"] != source_receipt["counts"].get("unverified_source_objects_excluded", 0):
        raise ValueError("UNVERIFIED_SOURCE_COUNT_MISMATCH")
    totals.update(required_legs=len(required))
    return sources, witnesses, dict(totals)


def load_metadata(library):
    metadata = {}
    for row in jsonl(library):
        if row["category"] in panel.TOURS:
            row["_path_point_count"] = len(row.pop("path"))
            metadata[row["ticker"]] = row
    return metadata


def ensure_external_output(root, output, *, resume=False):
    output = Path(output).resolve()
    try:
        output.relative_to(Path(root).resolve())
    except ValueError:
        pass
    else:
        raise ValueError("RAW_AND_PER_RECEIPT_OUTPUT_MUST_BE_OUTSIDE_REPOSITORY")
    if not resume and output.exists() and any(output.iterdir()):
        raise ValueError("REFUSE_NONEMPTY_RUN_OUTPUT")
    return output


def canonical_report(value, filename):
    result = copy.deepcopy(value)
    for path in WALL_CLOCK_PATHS.get(filename, ()):
        current = result
        for key in path[:-1]:
            current = current.get(key, {})
        current.pop(path[-1], None)
    return json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def compare_runs(first, second):
    """Only elapsed wall time is excluded; scientific clocks/hashes remain exact."""
    first, second = Path(first), Path(second)
    left = {p.relative_to(first).as_posix(): p for p in first.rglob("*") if p.is_file()}
    right = {p.relative_to(second).as_posix(): p for p in second.rglob("*") if p.is_file()}
    if set(left) != set(right):
        raise ValueError("DETERMINISM_FILE_SET_MISMATCH")
    manifest = {}
    for name in sorted(left):
        if name.endswith(".json"):
            a = canonical_report(json_file(left[name]), Path(name).name)
            z = canonical_report(json_file(right[name]), Path(name).name)
        else:
            a, z = left[name].read_bytes(), right[name].read_bytes()
        if a != z:
            raise ValueError("DETERMINISM_CONTENT_MISMATCH:"+name)
        manifest[name] = hashlib.sha256(a).hexdigest()
    return dict(status="DETERMINISTIC", files=len(manifest), canonical_sha256s=manifest,
        excluded_only={k: [".".join(p) for p in paths] for k, paths in WALL_CLOCK_PATHS.items()})


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, required=True)
    for name in ("sources", "witnesses", "supplemental", "source-receipt", "supplemental-receipt", "out"):
        p.add_argument("--"+name, type=Path, required=True)
    p.add_argument("--category", choices=tuple(BASELINES), required=True)
    p.add_argument("--core-extractor", type=Path, help="Reviewed frozen core extractor, if its bytes differ from current supplemental-capable script")
    p.add_argument("--odds-audit-receipt", type=Path, help="Local filed archive hash inventory; required whenever odds poll epochs were extracted")
    p.add_argument("--cache-budget-mib", type=int, required=True, help="Execution memory bound, not a scientific cutoff")
    p.add_argument("--batch-size", type=int, required=True, help="Member/receipt batching, not a member cap")
    p.add_argument("--workers", type=int, default=1, help="Execution-only ordered process workers; no change to scientific aggregation")
    p.add_argument("--checkpoint-dir", type=Path, help="Private durable exact-score checkpoints outside the artifact directory")
    p.add_argument("--resume", action="store_true", help="Restore a hash-bound completed evaluation prefix; fail closed on damage")
    p.add_argument("--import-models", type=Path, help="Explicitly recover validated fitted month models from the interrupted run; scores restart")
    p.add_argument("--verify-only", action="store_true", help="Hash/row/schema/lineage validation without fitting or scoring")
    return p


def run(args):
    if args.batch_size <= 0 or args.cache_budget_mib <= 0 or getattr(args, "workers", 1) <= 0:
        raise ValueError("POSITIVE_EXECUTION_BUDGETS_REQUIRED")
    args.root = args.root.resolve(strict=True)
    resume = getattr(args, "resume", False)
    checkpoint_dir = getattr(args, "checkpoint_dir", None)
    if resume and (checkpoint_dir is None or not (checkpoint_dir/"manifest.json").is_file()):
        raise ValueError("RESUME_REQUIRES_EXISTING_CHECKPOINT_MANIFEST")
    if checkpoint_dir is not None:
        # The store must also stay outside Git; it contains private exact score state.
        ensure_external_output(args.root, checkpoint_dir, resume=resume)
    output = ensure_external_output(args.root, args.out, resume=resume)
    baseline, baseline_proof, conduct_spec = bind_baseline(args.root, args.category)
    paths, registry, source_receipt, supplemental_receipt = verify_inputs(args, baseline)
    # No population decompression or fitting occurred before all SHA/receipt checks.
    metadata = load_metadata(paths["library"])
    pairs, census, _, counts_proof = reference.load_tick_library(paths["library"], {}, paths["counts"])
    pairs = [pair for pair in pairs if pair.category == args.category]
    if not pairs:
        raise ValueError("EMPTY_PINNED_CATEGORY")
    required = {pair.event_id+"-"+leg.leg_id for pair in pairs for leg in pair.legs}
    sources, witnesses, coverage = load_sources(args, metadata, required, source_receipt, supplemental_receipt)
    registry.update(baseline=baseline_proof, validated_source_coverage=coverage,
        category_census={k: v for k, v in census.items() if k.startswith(args.category+":")},
        exact_print_counts=counts_proof,
        code={name: digest(args.root/"arb-executor/analysis"/name) for name in
            ("feature_panel_run.py", "feature_panel.py", "feature_panel_bench.py", "feature_panel_model.py",
             "feature_panel_scoring.py", "feature_panel_parallel.py", "feature_panel_execution.py",
             "feature_panel_checkpoint.py", "feature_panel_recovery.py", "conduct_scoreboard.py", "conduct_scoreboard_v2.py",
             "tune_bench_v2_survivorship.py", "tune_bench_floor_calls.py")})
    registry["foundation_prior_art"] = {name: dict(path="arb-executor/data/scripts/"+name,
        sha256=digest(args.root/"arb-executor/data/scripts"/name)) for name in
        ("build_per_minute_universe.py", "cell_key_helpers.py")}
    registry["differs_from_foundation"] = [
        "BBO quote movement is expressed in cents, not Foundation probability-dollar units; not mislabeled as consumed order depth.",
        "Price breadth, clustering, intensity and fill witnesses use accepted positive-size prints; original library count includes zero-size rows separately.",
        "Full-lifetime intensity and full-span cadence are excluded; prefix cadence and completed-minute intensity use evidence available by the receipt.",
        "Spread band names come from the filed cell_key_helpers probability-unit classifier after converting cents by the bound par."]
    print("INPUTS_VERIFIED "+json.dumps(dict(category=args.category, queries=len(pairs), coverage=coverage)), flush=True)
    if args.verify_only:
        return dict(status="VERIFIED_NO_BENCH_RUN", sources=registry)
    sampler = compact_sampler_copy(bench.DirectFeatureSampler(
        metadata, sources, witnesses, baseline["organ_contract"], conduct_spec["par"]))
    del metadata, sources, witnesses
    gc.collect()
    binding = dict(source_registry=registry, code_sha256=registry["code"],
        protocol=dict(category=args.category, baseline=baseline, heldout_months=HELDOUT_MONTHS,
            batch_size=args.batch_size, cache_budget_bytes=args.cache_budget_mib*1024*1024))
    if getattr(args, "import_models", None) is not None:
        from feature_panel_recovery import recovered_model_evidence
        binding["explicit_model_recovery"] = dict(
            directory=str(args.import_models.resolve(strict=True)),
            models={month: recovered_model_evidence(args.import_models, month)
                    for month in sorted({p.date[:7] for p in pairs})})
    scope = (nullcontext(None) if checkpoint_dir is None else
             CheckpointStore(checkpoint_dir, binding, output_dir=output))
    with scope as store:
        receipt, _ = bench.run_category(pairs, sampler, baseline, conduct_spec, args.category, output,
            heldout_months=HELDOUT_MONTHS, batch_size=args.batch_size,
            cache_budget_bytes=args.cache_budget_mib*1024*1024, source_registry=registry,
            workers=getattr(args, "workers", 1), checkpoint_store=store,
            import_models=getattr(args, "import_models", None))
    print("CATEGORY_COMPLETE "+json.dumps(dict(category=args.category, output=str(output),
        receipt_sha256=digest(output/"FEATURE_PANEL_RECEIPT.json"))), flush=True)
    return receipt


def main():
    run(parser().parse_args())


if __name__ == "__main__":
    main()
