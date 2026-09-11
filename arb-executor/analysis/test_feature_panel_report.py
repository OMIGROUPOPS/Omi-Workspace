"""Synthetic manifest/coverage checks; no population or external resources."""
import json
import copy
import hashlib
from pathlib import Path
import tempfile
import unittest

import numpy as np

import feature_panel_report as report
from feature_panel_scoring import FeaturePanelScorer


def write(path, value):
    path.write_text(report.canonical(value)+"\n", encoding="utf-8")


def rebind(directory, name):
    receipt = json.loads((directory/report.RECEIPT).read_text())
    path = directory/name
    receipt["outputs"][name] = dict(bytes=path.stat().st_size, sha256=report.digest(path))
    write(directory/report.RECEIPT, receipt)


def fixture(directory, category):
    directory.mkdir()
    baseline = dict(organ_contract=dict(no_call_ess_floor=2, quantiles=[.1,.25,.5,.75,.9]),
        matched_step_first=dict(criterion=dict(minimum_matched_queries=1,
                                               minimum_step_strictly_closer_share=.5)))
    blocks = ["SOURCE", "WAKE", "FLOW", "INTENSITY", "OI", "PARTNER"]
    registry = [dict(name="FIRST",blocks=[])]
    registry += [dict(name=f"CUMULATIVE_{i}",blocks=blocks[:i]) for i in range(1,7)]
    registry += [dict(name="LEAVE_OUT_"+block,blocks=[other for other in blocks if other != block]) for block in blocks]
    variants = [row["name"] for row in registry]
    all_rows = FeaturePanelScorer(baseline, variants,
        groupings=(("category", "stream"),("category","stream","month")), authorization_streams=())
    gate_rows = FeaturePanelScorer(baseline, variants, groupings=(("category", "stream", "side", "gate"),),
                                   authorization_streams=())
    filed_rows = FeaturePanelScorer(baseline, variants, groupings=(("category", "stream", "side", "gate"),),
        authorization_streams=("PRIMARY_FILED_SCORABLE_GATES", "STRICT_HOLDOUT_FILED_SCORABLE_GATES"))
    event = category+"-event"
    arrays = directory/"receipt_diagnostics"
    arrays.mkdir()
    scale_name = "SCALES_2026-06.npz"
    np.savez_compressed(directory/scale_name, volume=np.array([0., 1.]))
    scale_sha = report.digest(directory/scale_name)
    diagnostics, queries = [], []
    for stream in ("PRIMARY", "STRICT_HOLDOUT"):
        for receipt, gate in (("a",10), ("b",5)):
            for side in ("A", "B"):
                identity = dict(category=category, event_id=event, month="2026-06", side=side,
                                receipt_id=receipt, gate=gate)
                targets = dict(carried=dict(floor_cents=10, floor_mtb=5, family="F"),
                               reachable=dict(floor_cents=10, floor_mtb=5, has_future_print=True, family="F"))
                forecasts = {variant: dict(values=[20,20] if variant=="FIRST" else [10,10],
                                            weights=[1,1],times=[5,5],families=["F","F"]) for variant in variants}
                all_rows.add_receipt(dict(identity, stream=stream+"_ALL_RECEIPTS"), targets, forecasts)
                gate_rows.add_receipt(dict(identity, stream=stream+"_GATES"), targets, forecasts)
                if gate == 10:
                    filed_rows.add_receipt(dict(identity, stream=stream+"_FILED_SCORABLE_GATES"), targets, forecasts)
        all_rows.add_conduct_event(dict(category=category,event_id=event,stream=stream,month="2026-06"),
            {variant:dict(rule="R0 CURRENT",completed=True,one_sided=False,captured_cents=10)
             for variant in variants})
        name = event+"__"+stream+".npz"
        np.savez_compressed(arrays/name, raw_value=np.array([[[0.],[np.nan]],[[np.nan],[1.]]]),
            empirical_rank=np.array([[[.1],[np.nan]],[[np.nan],[.9]]]),
            feature_names=np.array(["volume"]), epoch=np.array([0.,1.]),is_gate=np.ones(2,dtype=bool))
        diagnostics.append(dict(category=category, event_id=event, stream=stream,month="2026-06",receipts=2,
            path="receipt_diagnostics/"+name,sha256=report.digest(arrays/name),
            scale_file=scale_name,scale_sha256=scale_sha,scale_cutoff=0,
            coverage={leg:dict(receipts=2,fields=dict(volume=1,odds_available=None)) for leg in ("A","B")},
            diagnostics=[dict(ticker=event+"-"+leg) for leg in ("A","B")]))
        queries.append(dict(category=category,event_id=event,stream=stream,month="2026-06"))
    board = dict(all_receipts=all_rows.finish(),gates=gate_rows.finish(),filed_scorable_gates=filed_rows.finish())
    for name,value in ((report.ARTIFACTS[0],board),(report.ARTIFACTS[1],diagnostics),
                       (report.ARTIFACTS[2],queries),(report.ARTIFACTS[3],[])):
        write(directory/name,value)
    receipt = dict(status="BENCH_ONLY_NO_ENGINE_CHANGE",category=category,eligible_games=1,evaluated_stream_games=2,
        heldout_months=["2026-06"],source_registry=dict(extract_receipt_sha256="fixture-binding"),
        variants=registry,
        baseline_receipt_sha256=hashlib.sha256(report.canonical(baseline).encode()).hexdigest(),
        fields=[dict(name="volume" if i==0 else "field_"+str(i),block=block,kind="numeric") for i,block in enumerate(blocks)]
               +[dict(name="odds_available",block=None,kind="numeric")],
        outputs={path.name:dict(bytes=path.stat().st_size,sha256=report.digest(path))
                 for path in directory.iterdir() if path.is_file()})
    write(directory/report.RECEIPT,receipt)
    return directory


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="feature-report-test-")
        self.root = Path(self.temporary.name)
        self.main = fixture(self.root/"main","ATP_MAIN")
        self.chall = fixture(self.root/"chall","ATP_CHALL")

    def tearDown(self):
        self.temporary.cleanup()

    def test_deterministic_primary_coverage_separates_zero_missing_unknown(self):
        result = report.build_report([self.chall,self.main])
        self.assertEqual(report.canonical(result), report.canonical(report.build_report([self.main,self.chall])))
        rows = [row for row in result["coverage"] if row["category"]=="ATP_MAIN"]
        volume = next(row for row in rows if row["field"]=="volume")
        self.assertEqual((volume["eligible_receipts"],volume["available_receipts"],volume["missing_receipts"],
                          volume["unknown_receipts"],volume["observed_zero_values"]),(4,2,2,0,1))
        odds = next(row for row in rows if row["field"]=="odds_available")
        self.assertEqual(odds["unknown_receipts"],4)
        self.assertEqual(odds["available_receipts"],0)
        self.assertEqual(len([row for row in result["forecasts"] if row["stream"]=="STRICT_HOLDOUT_ALL_RECEIPTS"
                              and row["month"] is None]),52)
        self.assertTrue(all(row["stream"].endswith("_FILED_SCORABLE_GATES") for row in result["filed_qualifications"]))
        markdown = report.render_markdown(result)
        self.assertIn("new-experiment holdout—not historically unseen",markdown)
        self.assertIn("R0 conduct",markdown)

    def test_tampered_diagnostic_array_fails_hash_validation(self):
        manifest = report.load_json(self.main/report.ARTIFACTS[1])
        path = self.main/manifest[0]["path"]
        with path.open("ab") as file:
            file.write(b"tamper")
        with self.assertRaisesRegex(ValueError,"ARTIFACT_HASH_MISMATCH"):
            report.build_report([self.main,self.chall])

    def test_incomplete_population_and_missing_tour_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"REQUIRE_ONE_COMPLETED"):
            report.build_report([self.main])
        rows = report.load_json(self.main/report.ARTIFACTS[1])
        write(self.main/report.ARTIFACTS[1],rows[:1])
        rebind(self.main,report.ARTIFACTS[1])
        with self.assertRaisesRegex(ValueError,"INCOMPLETE_DIAGNOSTIC_POPULATION"):
            report.build_report([self.main,self.chall])

    def test_unfiled_qualification_is_rejected(self):
        board = report.load_json(self.main/report.ARTIFACTS[0])
        board["gates"]["groups"][0]["targets"]["carried"]["matched_to_first"]["CUMULATIVE_1"]["qualifies"] = True
        write(self.main/report.ARTIFACTS[0],board)
        rebind(self.main,report.ARTIFACTS[0])
        with self.assertRaisesRegex(ValueError,"UNFILED_QUALIFICATION"):
            report.build_report([self.main,self.chall])

    def test_coverage_must_match_derived_values(self):
        rows = report.load_json(self.main/report.ARTIFACTS[1])
        rows[0]["coverage"]["A"]["fields"]["volume"] = 2
        write(self.main/report.ARTIFACTS[1],rows)
        rebind(self.main,report.ARTIFACTS[1])
        with self.assertRaisesRegex(ValueError,"COVERAGE_ARRAY_COUNT_MISMATCH"):
            report.build_report([self.main,self.chall])

    def test_manifest_cannot_escape_run_directory(self):
        with self.assertRaisesRegex(ValueError,"UNSAFE_MANIFEST_PATH"):
            report.contained(self.main,"../secret.npz")

    def test_known_unavailable_flags_are_zero_without_becoming_unknown(self):
        rows = report.load_json(self.main/report.ARTIFACTS[1])
        primary = next(row for row in rows if row["stream"]=="PRIMARY")
        path = self.main/primary["path"]
        with np.load(path,allow_pickle=False) as source:
            values = {key:source[key] for key in source.files}
        values.update(A__odds_available=np.zeros(2),B__odds_available=np.zeros(2))
        np.savez_compressed(path,**values)
        primary["sha256"] = report.digest(path)
        for side in primary["coverage"].values():
            side["fields"]["odds_available"] = 0
        write(self.main/report.ARTIFACTS[1],rows)
        rebind(self.main,report.ARTIFACTS[1])
        result = report.build_report([self.main,self.chall])
        odds = next(row for row in result["coverage"] if row["category"]=="ATP_MAIN" and row["field"]=="odds_available")
        self.assertEqual((odds["available_receipts"],odds["missing_receipts"],odds["unknown_receipts"],odds["observed_zero_values"]),(0,4,0,4))

    def test_truncated_or_wrong_block_registry_fails_closed(self):
        original = report.load_json(self.main/report.RECEIPT)
        for transform in (lambda r:r.update(variants=r["variants"][:2]),
                          lambda r:r["variants"][2].update(blocks=["SOURCE"])):
            changed = copy.deepcopy(original)
            transform(changed)
            write(self.main/report.RECEIPT,changed)
            with self.assertRaisesRegex(ValueError,"INCOMPLETE_OR_INCORRECT_VARIANT_REGISTRY"):
                report.read_run(self.main)
        write(self.main/report.RECEIPT,original)

    def test_required_field_missing_everywhere_is_explicitly_unknown(self):
        result = report.build_report([self.main,self.chall])
        row = next(row for row in result["coverage"] if row["category"]=="ATP_MAIN" and row["field"]=="field_5")
        self.assertEqual((row["eligible_receipts"],row["available_receipts"],row["missing_receipts"],row["unknown_receipts"]),
                         (4,0,0,4))
        self.assertEqual(row["class_counts"],{})

    def test_unavailable_metrics_have_null_placeholders_and_status_counts(self):
        board = report.load_json(self.main/report.ARTIFACTS[0])
        omitted = ("floor_timing_absolute_error_minutes","family_accuracy")
        for scorer in board.values():
            for group in scorer["groups"]:
                for cell in group["targets"].values():
                    for own in cell["all_eligible"].values():
                        for key in omitted:
                            own["metrics"].pop(key,None)
                    for match in cell["matched_to_first"].values():
                        for key in omitted:
                            match["metrics"].pop(key,None)
        write(self.main/report.ARTIFACTS[0],board)
        rebind(self.main,report.ARTIFACTS[0])
        result = report.build_report([self.main,self.chall])
        row = next(row for row in result["forecasts"] if row["category"]=="ATP_MAIN"
                   and row["stream"]=="PRIMARY_ALL_RECEIPTS" and row["month"] is None
                   and row["target"]=="carried" and row["variant"]=="CUMULATIVE_1")
        for key in omitted:
            self.assertEqual(row["metrics"][key],dict(n=0,mean=None,availability="NO_FINITE_SCORED_OBSERVATIONS"))
            self.assertEqual(row["matched_to_first"]["metrics"][key]["delta"]["n"],0)
        self.assertEqual(row["statuses"],{"OK":4})
        self.assertEqual(row["target_available_receipts"],4)
        self.assertIn("— / 0",report.render_markdown(result))

    def test_primary_june_and_strict_june_remain_separate_not_summed(self):
        result = report.build_report([self.main,self.chall])
        rows = [row for row in result["forecasts"] if row["category"]=="ATP_MAIN"
                and row["variant"]=="FIRST" and row["target"]=="carried" and row["cohort"]=="all_receipts"]
        self.assertEqual({(row["stream"],row["month"]) for row in rows},
            {("PRIMARY_ALL_RECEIPTS",None),("PRIMARY_ALL_RECEIPTS","2026-06"),
             ("STRICT_HOLDOUT_ALL_RECEIPTS",None),("STRICT_HOLDOUT_ALL_RECEIPTS","2026-06")})
        self.assertTrue(all(row["eligible_receipts"]==4 and row["metrics"]["floor_crps_cents"]["n"]==4 for row in rows))
        self.assertIn("PRIMARY_ALL_RECEIPTS · 2026-06",report.render_markdown(result))

    def test_contract_binding_preserved_and_mismatch_rejected(self):
        result = report.build_report([self.main,self.chall])
        contract = result["score_contracts"][0]
        receipt = report.load_json(self.main/report.RECEIPT)
        self.assertEqual(contract["baseline_receipt_sha256"],receipt["baseline_receipt_sha256"])
        self.assertEqual(contract["minimum_matched_queries"],1)
        self.assertIn("n >= 1 and strictly closer >= 0.5",report.render_markdown(result))
        board = report.load_json(self.main/report.ARTIFACTS[0])
        board["gates"]["contract"]["minimum_matched_queries"] = 100
        write(self.main/report.ARTIFACTS[0],board)
        rebind(self.main,report.ARTIFACTS[0])
        with self.assertRaisesRegex(ValueError,"INCONSISTENT_BASELINE_SCORE_CONTRACT"):
            report.read_run(self.main)

    def test_missing_r0_or_gate_cells_fail_closed(self):
        original = report.load_json(self.main/report.ARTIFACTS[0])
        for section, key, expected in (("all_receipts","r0_conduct","MISSING_R0_CONDUCT_COHORT"),
                                       ("gates","groups","GATE_DIAGNOSTIC_DENOMINATOR_MISMATCH")):
            board = copy.deepcopy(original)
            board[section][key] = []
            write(self.main/report.ARTIFACTS[0],board)
            rebind(self.main,report.ARTIFACTS[0])
            with self.assertRaisesRegex(ValueError,expected):
                report.read_run(self.main)

    def test_month_and_metric_denominator_completeness(self):
        original = report.load_json(self.main/report.ARTIFACTS[0])
        board = copy.deepcopy(original)
        board["all_receipts"]["groups"] = [row for row in board["all_receipts"]["groups"] if "month" not in row["group"]]
        write(self.main/report.ARTIFACTS[0],board)
        rebind(self.main,report.ARTIFACTS[0])
        with self.assertRaisesRegex(ValueError,"MISSING_MONTHLY_RECEIPT_COHORT"):
            report.read_run(self.main)
        board = copy.deepcopy(original)
        own = board["all_receipts"]["groups"][0]["targets"]["carried"]["all_eligible"]["FIRST"]
        own["metrics"]["floor_crps_cents"]["n"] = own["eligible_receipts"]+1
        write(self.main/report.ARTIFACTS[0],board)
        rebind(self.main,report.ARTIFACTS[0])
        with self.assertRaisesRegex(ValueError,"INVALID_METRIC_DENOMINATOR"):
            report.read_run(self.main)

    def test_filed_criterion_is_rechecked_and_empty_cells_are_explicit(self):
        original = report.load_json(self.main/report.ARTIFACTS[0])
        board = copy.deepcopy(original)
        match = board["filed_scorable_gates"]["groups"][0]["targets"]["carried"]["matched_to_first"]["CUMULATIVE_1"]
        match["qualifies"] = not match["qualifies"]
        write(self.main/report.ARTIFACTS[0],board)
        rebind(self.main,report.ARTIFACTS[0])
        with self.assertRaisesRegex(ValueError,"FILED_QUALIFICATION_CONTRACT_MISMATCH"):
            report.read_run(self.main)
        board = copy.deepcopy(original)
        board["filed_scorable_gates"]["groups"] = []
        write(self.main/report.ARTIFACTS[0],board)
        rebind(self.main,report.ARTIFACTS[0])
        result = report.build_report([self.main,self.chall])
        rows = [row for row in result["cohort_status"] if row["category"]=="ATP_MAIN" and row["cohort"]=="filed_scorable_gates"]
        self.assertTrue(rows and all(row["status"]=="NO_CELLS_RECORDED" for row in rows))

    def test_navigable_diagnostic_manifest_and_primary_class_counts(self):
        receipt = report.load_json(self.main/report.RECEIPT)
        receipt["fields"][0]["kind"] = "categorical"
        write(self.main/report.RECEIPT,receipt)
        result = report.build_report([self.main,self.chall])
        row = next(row for row in result["coverage"] if row["category"]=="ATP_MAIN" and row["field"]=="volume")
        self.assertEqual(row["class_counts"],{"code:0":1,"code:1":1})
        self.assertEqual(len(result["diagnostic_index"]),4)
        diagnostic = next(row for row in result["diagnostic_index"] if row["category"]=="ATP_MAIN" and row["stream"]=="PRIMARY")
        self.assertEqual(report.digest(Path(diagnostic["run_directory"])/diagnostic["path"]),diagnostic["sha256"])
        self.assertEqual(len(diagnostic["side_order"]),2)


if __name__ == "__main__":
    unittest.main()
