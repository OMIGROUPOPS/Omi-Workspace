import unittest
import gzip
import json
from pathlib import Path
import tempfile
import feature_panel_actions_plan as p


class ActionsPlanTests(unittest.TestCase):
    def test_tune_by_date_and_nested_tag(self):
        for day in range(11,22):
            with self.assertRaises(ValueError):p.reject_tune({'ticker':f'KXATPMATCH-26JUL{day:02}PAIR-A'})
        with self.assertRaises(ValueError):p.reject_tune({'sources':[{'src_role':'TUNE_SAMPLE'}]})
        p.reject_tune({'event_id':'KXATPMATCH-26JUL10PAIR'})

    def test_sharding_is_atomic_and_input_order_independent(self):
        rows=[dict(event_id=str(i),stream='PRIMARY',month='2026-05',receipt_cost=i+1) for i in range(17)]
        a=p.shard_queries(rows,5);b=p.shard_queries(rows[::-1],5)
        self.assertEqual(a,b)
        self.assertEqual(sorted(q['event_id'] for x in a for q in x['queries']),sorted(q['event_id'] for q in rows))
        with self.assertRaises(ValueError):p.shard_queries(rows+rows[:1],5)

    def test_no_finalists_means_no_jobs(self):
        r={c:{'advancement':{'variants':[],'june_may_select':False}} for c in p.TOURS}
        self.assertEqual(p.matrix(r,5),{'include':[]})
        r['ATP_MAIN']['advancement']['variants']=['CUMULATIVE_1']
        self.assertEqual(len(p.matrix(r,5)['include']),10)
        r['ATP_MAIN']['advancement']['june_may_select']=True
        with self.assertRaises(ValueError):p.matrix(r,5)

    def test_raw_artifacts_never_allowlisted(self):
        for name in ('FEATURE_SOURCES.jsonl.gz','POSITIVE_PRINT_WITNESSES.jsonl.gz','context.pickle','receipt_diagnostics'):
            self.assertNotIn(name,p.PUBLIC_ARTIFACTS)

    def test_exact_release_and_hidden_tune_row(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            event='KXATPMATCH-26JUN01PAIR'
            for name in p.INPUT_NAMES:
                path=root/name
                if name.endswith('.gz'):
                    with gzip.open(path,'wt') as f:
                        f.write(json.dumps({'event_id':event,'ticker':event+'-ONE'})+'\n')
                else:
                    # The source receipt describes the prohibition, not data.
                    path.write_text(json.dumps({'excluded_role':'TUNE_SAMPLE'}))
            def manifest():
                return dict(schema='FEATURE_PANEL_ACTIONS_RELEASE_V1',tune_sample_allowed=False,
                    public_artifacts=sorted(p.PUBLIC_ARTIFACTS),files=[dict(name=name,
                    bytes=(root/name).stat().st_size,sha256=p.sha(root/name)) for name in sorted(p.INPUT_NAMES)])
            self.assertEqual(p.validate_bundle(root,manifest())['library_events'],1)
            extra=root/'named-check.json';extra.write_text('{}')
            with self.assertRaisesRegex(ValueError,'UNALLOWLISTED_RELEASE_FILE'):
                p.validate_bundle(root,manifest())
            extra.unlink()
            with gzip.open(root/'FEATURE_SOURCES.jsonl.gz','at') as f:
                f.write(json.dumps({'ticker':'KXATPMATCH-26JUL12PAIR-ONE'})+'\n')
            with self.assertRaisesRegex(ValueError,'TUNE_EVENT_FORBIDDEN'):
                p.validate_bundle(root,manifest())


if __name__=='__main__':unittest.main()
