import copy
import gzip
from pathlib import Path
import tempfile
import unittest
import numpy as np
from absorption_residual_data import BLOCKS, selected_jsonl
from absorption_residual_run import Learner, MODELS, scored_rows, matrix
from resume_absorption_confirmation import verify_empty_guard


def row(event,month,formation,bell,target=12,book=True):
    return dict(event=event,date=month+'-01',month=month,category='TEST',side=0,leg='A',gate=10,
        formation=formation,bell=bell,q=10,target=target,ess=100,member_count=100,
        values=[8,10,12],weights=[1,2,1],
        first_scores=dict(q=10,mae=abs(10-target),signed=10-target,crps=1),
        base_features={'first_own':10,'first_partner':90,'log_mtb':1,
            'role:CLIMBER':1,'role:FALLER':0,'role:NOT_CALLABLE':0},
        blocks={b:{'value':1 if book else None} for b in BLOCKS},
        refill_status={'own:bid':dict(status='MEASURED' if book else 'UNOBSERVED')})


class RunTests(unittest.TestCase):
    def test_no_atlas_rows_produces_no_predictions_or_model_access(self):
        self.assertEqual(scored_rows([], {}, 100), [])

    def test_execution_guard_allows_no_other_change(self):
        old = 'def scored_rows(rows, fitted, par):\n    return rows\n'
        new = 'def scored_rows(rows, fitted, par):\n    if not rows:\n        return []\n    return rows\n'
        verify_empty_guard(old, new)
        with self.assertRaisesRegex(ValueError, 'NON_EXECUTION_CHANGE'):
            verify_empty_guard(old, new.replace('return rows', 'return [1]'))

    def test_no_inner_training_is_explicit_zero(self):
        a=row('a','2026-04',1,2)
        learner=Learner({'a':dict(event_date=a['date'],formation_epoch=1)},[.25,.5,.75])
        fit=learner.learn([a],'BASE_CORRECTION')
        self.assertEqual(fit['choice'],'ZERO')
        self.assertIn('NO_INNER_VALIDATION',fit['reason'])
        self.assertEqual(fit['folds'][0]['status'],'NO_INNER_VALIDATION_TRAINING')

    def test_resolved_by_inner_cutoff_required(self):
        a=row('a','2026-04',1,99)
        b=row('b','2026-05',10,11)
        metadata={r['event']:dict(event_date=r['date'],formation_epoch=r['formation']) for r in (a,b)}
        fit=Learner(metadata,[.25,.5,.75]).learn([a,b],'BASE_CORRECTION')
        self.assertEqual(fit['choice'],'ZERO')
        self.assertTrue(all(f['status']=='NO_INNER_VALIDATION_TRAINING' for f in fit['folds']))

    def test_learned_constant_residual_not_hand_selected(self):
        rows=[row('a','2026-04',1,2),row('b','2026-05',10,11)]
        metadata={r['event']:dict(event_date=r['date'],formation_epoch=r['formation']) for r in rows}
        fit=Learner(metadata,[.25,.5,.75]).learn(rows,'BASE_CORRECTION')
        self.assertNotEqual(fit['choice'],'ZERO')
        pred=fit['family'].predict(matrix(rows,fit['names'],'BASE_CORRECTION'),fit['choice'])
        np.testing.assert_allclose(pred,[2,2])

    def test_missing_book_falls_back_to_base_not_fake_measurement(self):
        rows=[row('a','2026-04',1,2),row('b','2026-05',10,11)]
        metadata={r['event']:dict(event_date=r['date'],formation_epoch=r['formation']) for r in rows}
        learner=Learner(metadata,[.25,.5,.75])
        fitted={m:learner.learn(rows,m) for m in MODELS}
        test=row('c','2026-06',20,21,book=False)
        score=scored_rows([test],fitted,100)[0]
        self.assertTrue(score['fallback']['BOOK_CORRECTION'])
        self.assertEqual(score['forecasts']['BASE_CORRECTION'],score['forecasts']['BOOK_CORRECTION'])
        self.assertFalse(score['book_supported']['BOOK_CORRECTION'])

    def test_reserved_payload_is_skipped_before_json_parse(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'source.jsonl.gz'
            with gzip.open(path,'wb') as out:
                out.write(b'{"event_id":"reserved","malformed": NOT_JSON}\n')
                out.write(b'{"event_id":"development","value":1}\n')
            result=list(selected_jsonl(path,{'development'}))
            self.assertEqual(result,[dict(event_id='development',value=1)])


if __name__=='__main__':
    unittest.main()
