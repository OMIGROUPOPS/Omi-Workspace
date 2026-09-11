import copy
import json
from pathlib import Path
import tempfile
import unittest
import feature_panel_atlas_publish as p
from test_feature_panel_report import fixture,write,rebind


class AtlasPublicationTests(unittest.TestCase):
    def setup_screen(self,root):
        path=fixture(root/'screen','ATP_MAIN')
        q=json.loads((path/'FEATURE_PANEL_QUERIES.json').read_text())
        for row in q:row['counts']={'receipts':2,'atlas_receipts':2}
        write(path/'FEATURE_PANEL_QUERIES.json',q);rebind(path,'FEATURE_PANEL_QUERIES.json')
        b=json.loads((path/'FEATURE_PANEL_SCOREBOARD.json').read_text())
        b['selection_filed_scorable_gates']=dict(b['filed_scorable_gates'],groups=[])
        write(path/'FEATURE_PANEL_SCOREBOARD.json',b);rebind(path,'FEATURE_PANEL_SCOREBOARD.json')
        r=json.loads((path/'FEATURE_PANEL_RECEIPT.json').read_text());r.update(screen_only=True,evaluation_cadence='GATE-SIM')
        write(path/'FEATURE_PANEL_RECEIPT.json',r)
        return path

    def test_no_holdout_selection_and_no_private_array_publication(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);path=self.setup_screen(root)
            self.assertTrue(p.screen.summaries(path)['conduct_gate_sim'])
            result=p.publish(path,root/'public')
            self.assertEqual(result['advancement']['variants'],[])
            self.assertEqual(result['gate_counts']['PRIMARY']['gate_receipts'],2)
            self.assertTrue(result['conduct_gate_sim'])
            self.assertEqual({x.name for x in (root/'public').iterdir()},
                {'SUMMARY.md','ATLAS_SCREEN_RESULTS.json','ATLAS_SCREEN_RECEIPT.json','OPTIMIZER_OUTCOMES.json'})

    def test_full_cadence_cannot_be_mislabeled_as_screen(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);path=self.setup_screen(root)
            q=json.loads((path/'FEATURE_PANEL_QUERIES.json').read_text());q[0]['counts']['receipts']=3
            write(path/'FEATURE_PANEL_QUERIES.json',q);rebind(path,'FEATURE_PANEL_QUERIES.json')
            with self.assertRaisesRegex(ValueError,'NON_ATLAS_RECEIPT'):p.validate_screen(path)

    def test_first_gate_comparison_fails_on_any_drift(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);path=self.setup_screen(root);run,_=p.validate_screen(path)
            p.first_gate_parity(run,path)
            changed=copy.deepcopy(run)
            changed['board']['gates']['groups'][0]['targets']['carried']['all_eligible']['FIRST']['called_receipts']+=1
            with self.assertRaisesRegex(ValueError,'FIRST_GATE_PARITY'):p.first_gate_parity(changed,path)


if __name__=='__main__':unittest.main()
