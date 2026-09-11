"""Focused source/clock/dedupe checks; no remote resources or database writes."""
import io
import tempfile
from pathlib import Path
import unittest
import feature_panel_extract as feature


def accepted(ts, price, size, source="spaces_trades", rowid=1, taker="yes"):
    return dict(ts=ts,price=price,size=size,src=source,rowid=rowid,taker_side=taker)


class FeatureSourceTests(unittest.TestCase):
    def test_et_source_clock_is_not_utc(self):
        self.assertEqual(feature.source_epoch("1970-01-01 12:00:00 AM"),14400)
        for stamp in ("2026-04-19 11:11:32 AM","2026-07-10 12:00:01 PM","2026-05-20 01:55:42 PM"):
            expected=feature.datetime.strptime(stamp,"%Y-%m-%d %I:%M:%S %p").replace(tzinfo=feature.ET).timestamp()
            self.assertEqual(feature.source_epoch(stamp),expected)

    def test_completed_minute_only_and_no_bell_close(self):
        leg=dict(formation_end_epoch=31,bell_epoch=180)
        rows=[accepted(59,40,2),accepted(60,39,3),accepted(120,30,0)]
        result=feature.minute_features(leg,rows,[])
        self.assertEqual([r["available_epoch"] for r in result],[60,120])
        self.assertEqual(result[0]["interval_start_epoch"],31)
        self.assertTrue(result[0]["partial_formation_minute"])
        self.assertEqual(result[0]["contracts_total"],2)
        self.assertEqual(result[1]["contracts_total"],3)

    def test_aggressor_size_is_not_trade_count(self):
        rows=[accepted(1,40,8,taker="yes"),accepted(2,39,3,taker="no")]
        result=feature.minute_features(dict(formation_end_epoch=0,bell_epoch=121),rows,[])[0]
        self.assertEqual(result["positive_size_trade_count"],2)
        self.assertEqual(result["taker_yes_contracts"],8)
        self.assertEqual(result["taker_flow_contracts"],5)

    def test_missing_aggressor_makes_flow_unknown_not_zero(self):
        rows=[accepted(1,40,8,taker="yes"),accepted(2,39,3,source="backfill",taker=None)]
        result=feature.minute_features(dict(formation_end_epoch=0,bell_epoch=61),rows,[])[0]
        self.assertIsNone(result["taker_flow_contracts"])
        self.assertIsNone(result["taker_yes_contracts"])
        self.assertEqual(result["contracts_total"],11)
        self.assertEqual(result["known_taker_positive_print_count"],1)

    def test_zero_print_not_price_floor_or_positive_count(self):
        rows=[accepted(1,1,0,taker=None),accepted(2,40,3,taker="yes")]
        result=feature.minute_features(dict(formation_end_epoch=0,bell_epoch=61),rows,[])[0]
        self.assertEqual(result["accepted_print_count"],2)
        self.assertEqual(result["positive_size_trade_count"],1)
        self.assertEqual(result["price_min_cents"],40)
        self.assertEqual(result["distinct_print_prices"],1)
        self.assertEqual(result["taker_yes_contracts"],3)

    def test_clustering_is_std_of_intertrade_gaps(self):
        rows=[accepted(1,40,1),accepted(3,40,1),accepted(9,41,1)]
        result=feature.minute_features(dict(formation_end_epoch=0,bell_epoch=61),rows,[])[0]
        self.assertEqual(result["intertrade_gap_std_seconds"],2)
        self.assertEqual(result["distinct_print_prices"],2)

    def test_exact_join_uses_last_source_row_for_cross_source_survivor(self):
        rows=[accepted(10,40,2)]
        original={(10,40,2):[dict(taker_side="yes",source_row=0,source_object="a"),
                                  dict(taker_side="no",source_row=1,source_object="a")]}
        result=feature.attach_takers(rows,original)
        self.assertEqual(result[0]["taker_side"],"no")
        self.assertEqual(result[0]["original_source_row"],1)

    def test_same_source_repetitions_remain_distinct(self):
        rows=[accepted(10,40,2,rowid=1),accepted(10,40,2,rowid=2)]
        original={(10,40,2):[dict(taker_side="yes",source_row=0,source_object="a"),
                                  dict(taker_side="no",source_row=1,source_object="a")]}
        self.assertEqual([r["taker_side"] for r in feature.attach_takers(rows,original)],["yes","no"])

    def test_does_not_attach_spaces_aggressor_to_backfill(self):
        rows=[accepted(10,40,2,source="backfill")]
        self.assertIsNone(feature.attach_takers(rows,{})[0]["taker_side"])

    def test_missing_exact_join_fails(self):
        with self.assertRaisesRegex(ValueError,"JOIN_MISMATCH"):
            feature.attach_takers([accepted(10,40,2)],{})

    def test_unverified_original_is_not_used_for_aggressor(self):
        rows=[accepted(10,40,2)]
        original={(10,40,2):[dict(taker_side="yes",source_row=0,source_object="a")]}
        result=feature.attach_takers(rows,original,True)[0]
        self.assertIsNone(result["taker_side"])

    def test_checkpoint_roundtrip_and_binding_guard(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/"parts";leg=dict(ticker="test")
            binding=dict(library="a",extractor="b",source="c")
            feature.save_checkpoint(root,leg,dict(value=1),dict(positive_prints=[]),binding)
            self.assertEqual(feature.load_checkpoint(root,leg,binding),[dict(value=1),dict(positive_prints=[])])
            with self.assertRaisesRegex(ValueError,"CHECKPOINT_BINDING_CHANGED"):
                feature.load_checkpoint(root,leg,{**binding,"source":"changed"})

    def test_checkpoint_detects_tampered_part(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)/"parts";leg=dict(ticker="test");binding=dict(source="a")
            feature.save_checkpoint(root,leg,dict(value=1),dict(positive_prints=[]),binding)
            part=next(root.glob("*.feature.json.gz"))
            part.write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError,"CHECKPOINT_HASH_OR_PATH_ERROR"):
                feature.load_checkpoint(root,leg,binding)

    def test_archive_months_use_half_open_span_across_year(self):
        first=feature.datetime(2025,12,31,tzinfo=feature.ET).timestamp()
        bell=feature.datetime(2026,2,1,tzinfo=feature.ET).timestamp()
        self.assertEqual(feature.span_months(dict(pair=dict(formation=first,bell=bell))),{"2025-12","2026-01"})

    def test_all_second_prints_count_toward_original_volume_point(self):
        rows=[accepted(1.8,40,2,rowid=2),accepted(1.1,40,3,rowid=3),accepted(2,40,0,rowid=4)]
        leg=dict(ticker="x",true_print_count_in_span=3,path=[dict(ts=1.8,volume_cum=5),dict(ts=2,volume_cum=5)])
        self.assertEqual(feature.verify_library(leg,rows)["path_volume_points_checked"],2)
        leg["path"][1]["volume_cum"]=6
        with self.assertRaisesRegex(ValueError,"PATH_VOLUME_MISMATCH"):
            feature.verify_library(leg,rows)

    def test_book_schema_does_not_fabricate_absent_last_or_oi(self):
        raw=dict(ts_et="2026-04-19 11:11:32 AM",bid_1="6",bid_1_sz="316")
        row=feature.book_from_source(raw,1,"object")
        self.assertIsNone(row["last_trade"])
        self.assertEqual(row["open_interest"],{})
        self.assertIsNone(row["receipt_epoch"])
        self.assertIn("STORE_SILENT",row["depth_status"])

    def test_book_at_minute_boundary_not_used_in_preceding_minute(self):
        books=[dict(source_epoch=59,bids=[[40,2]],asks=[[42,2]]),
               dict(source_epoch=60,bids=[[39,2]],asks=[[41,2]])]
        result=feature.minute_features(dict(formation_end_epoch=0,bell_epoch=121),[],books)
        self.assertEqual(result[0]["bid_close_cents"],40)
        self.assertEqual(result[1]["bid_close_cents"],39)
        self.assertEqual(result[1]["bid_quote_delta_cents"],-1)

    def test_two_sided_book_rejects_crossed_zero_missing(self):
        self.assertTrue(feature.two_sided_book(dict(bids=[[40,1]],asks=[[41,1]])))
        for bid,ask in (([42,1],[41,1]),([41,1],[41,1]),([0,1],[41,1]),([40,0],[41,1]),([40,1],[None,1])):
            self.assertFalse(feature.two_sided_book(dict(bids=[bid],asks=[ask])))

    def test_empty_completed_minute_has_zero_observed_trades(self):
        row=feature.minute_features(dict(formation_end_epoch=0,bell_epoch=61),[],[])[0]
        self.assertEqual(row["positive_size_trade_count"],0)
        self.assertEqual(row["taker_flow_contracts"],0)
        self.assertIsNone(row["price_min_cents"])
        self.assertIsNone(row["bid_close_cents"])

    def test_density_bell_not_claimed_published(self):
        result=feature.clock_provenance(dict(bell_source="both_sides_trade_density"))
        self.assertEqual(result["bell_publication_status"],"RETROSPECTIVE_TRADE_DENSITY_INFERENCE")
        self.assertIsNone(result["bell_publication_epoch"])

    def test_hash_reader_hashes_complete_compressed_input(self):
        data=b"original compressed bytes"
        raw=feature.HashReader(io.BytesIO(data))
        with io.BufferedReader(raw) as stream:
            self.assertEqual(stream.read(),data)
        self.assertEqual(raw.bytes,len(data))
        self.assertEqual(raw.digest.hexdigest(),feature.hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    unittest.main()
