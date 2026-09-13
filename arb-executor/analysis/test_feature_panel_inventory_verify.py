import json
from pathlib import Path
import tempfile
import unittest

import feature_panel_inventory_verify as verify
import feature_panel_inventory_atlas_publish as publication
import feature_panel_run as launcher


class InventoryVerifyTests(unittest.TestCase):
    def test_publication_refuses_missing_population_or_first_parity_proof(self):
        with self.assertRaisesRegex(ValueError, 'PUBLICATION_REQUIRES'):
            publication.publish('not-read', 'not-written')
        with self.assertRaisesRegex(ValueError, 'PUBLICATION_REQUIRES'):
            publication.publish('not-read', 'not-written', prior_first='prior')

    def fixture(self, root, elapsed, score=1):
        root.mkdir()
        receipt = dict(evaluation_cadence='GATE-SIM', screen_only=True,
                       numerical_execution=dict(elapsed_seconds=elapsed), bell_epoch=123)
        (root/verify.RECEIPT).write_text(json.dumps(receipt))
        summary = dict(receipt_sha256=launcher.digest(root/verify.RECEIPT), score=score)
        (root/verify.SUMMARY).write_text(json.dumps(summary))
        (root/'array.bin').write_bytes(b'exact scientific array')

    def test_runtime_and_its_validated_link_only_are_normalized(self):
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory)/'a', Path(directory)/'b'
            self.fixture(a, 1)
            self.fixture(b, 2)
            self.assertEqual(verify.compare(a, b)['status'], 'DETERMINISTIC')
            self.assertNotEqual(launcher.digest(a/verify.RECEIPT), launcher.digest(b/verify.RECEIPT))

    def test_scientific_summary_change_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory)/'a', Path(directory)/'b'
            self.fixture(a, 1)
            self.fixture(b, 2, score=2)
            with self.assertRaisesRegex(ValueError, 'CONTENT_MISMATCH'):
                verify.compare(a, b)

    def test_bad_hash_link_fails_even_when_both_identically_wrong(self):
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory)/'a', Path(directory)/'b'
            for path in (a, b):
                self.fixture(path, 1)
                (path/verify.SUMMARY).write_text(json.dumps(dict(receipt_sha256='wrong', score=1)))
            with self.assertRaisesRegex(ValueError, 'HASH_LINK_MISMATCH'):
                verify.compare(a, b)

    def test_scientific_receipt_clock_and_binary_and_file_set_fail(self):
        for change in ('clock', 'binary', 'file_set'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as directory:
                a, b = Path(directory)/'a', Path(directory)/'b'
                self.fixture(a, 1)
                self.fixture(b, 2)
                if change == 'clock':
                    receipt = launcher.json_file(b/verify.RECEIPT)
                    receipt['bell_epoch'] += 1
                    (b/verify.RECEIPT).write_text(json.dumps(receipt))
                    summary = launcher.json_file(b/verify.SUMMARY)
                    summary['receipt_sha256'] = launcher.digest(b/verify.RECEIPT)
                    (b/verify.SUMMARY).write_text(json.dumps(summary))
                elif change == 'binary':
                    (b/'array.bin').write_bytes(b'different scientific array')
                else:
                    (b/'extra').write_bytes(b'new')
                with self.assertRaisesRegex(ValueError, 'DETERMINISM_'):
                    verify.compare(a, b)


if __name__ == '__main__':
    unittest.main()
