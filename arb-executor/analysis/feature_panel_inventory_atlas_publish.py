"""Verified eleven-block publication; private depth, labels and arrays stay out."""
from __future__ import annotations
import argparse
from pathlib import Path

import feature_panel_atlas_publish as publication
import feature_panel_bench as bench
import feature_panel_inventory_atlas as inventory
import feature_panel_inventory_verify as verification
import feature_panel_report as report
import feature_panel_run as launcher


def publish(run, out, prior_first=None, second_pass=None):
    if prior_first is None or second_pass is None:
        raise ValueError('PUBLICATION_REQUIRES_POPULATION_TWO_PASS_AND_PRIOR_FIRST')
    determinism = verification.compare(run, second_pass)
    with inventory.registry_adapter():
        verified = report.read_run(run)
        coverage = report.coverage_rows(verified)
        result = publication.publish(run, out, prior_first)
        target = Path(out)
        bench.write_json(target/'LINEAGE_COVERAGE.json', dict(
            schema='FEATURE_PANEL_INVENTORY_LINEAGE_V2',
            category=verified['receipt']['category'], fields=verified['receipt']['fields'],
            source_receipt_sha256=launcher.digest(Path(run)/'FEATURE_PANEL_RECEIPT.json'),
            coverage_by_month=coverage, arithmetic_direction_is_not_a_flow_fallback=True,
            cadence='ATLAS gates, full query universe; PRIMARY counted once; frozen June scored separately'))
        # Extend only the versioned public receipt; its private source and v1
        # summaries remain immutable. No per-trade or book rows are copied.
        receipt_path = target/'ATLAS_SCREEN_RECEIPT.json'
        receipt = launcher.json_file(receipt_path)
        receipt.update(schema='FEATURE_PANEL_INVENTORY_ATLAS_PUBLICATION_V2',
            inventory_publisher_sha256=launcher.digest(Path(__file__)),
            population_determinism=determinism,
            determinism_verifier_sha256=launcher.digest(Path(verification.__file__)),
            lineage_coverage_sha256=launcher.digest(target/'LINEAGE_COVERAGE.json'))
        bench.write_json(receipt_path, receipt)
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--prior-first', type=Path, required=True)
    parser.add_argument('--second-pass', type=Path, required=True)
    args = parser.parse_args()
    publish(args.run, args.out, args.prior_first, args.second_pass)


if __name__ == '__main__':
    main()
