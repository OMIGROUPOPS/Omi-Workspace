"""Publish a completed first-pass report WITHOUT claiming two-pass proof.

Separate from the guarded final publisher. This is operator-requested early
reporting; it cannot authorize advancement or replace the final receipt.
"""
import argparse
from pathlib import Path
import feature_panel_atlas_publish as publication
import feature_panel_inventory_atlas as inventory
import feature_panel_report as report
import feature_panel_run as launcher
import feature_panel_bench as bench


def publish(run, prior_first, out):
    out = Path(out)
    if not out.name.endswith('_PASS1'):
        raise ValueError('PROVISIONAL_DIRECTORY_MUST_END_IN_PASS1')
    with inventory.registry_adapter():
        verified, counts = publication.validate_screen(run)
        result = launcher.json_file(Path(run)/'ATLAS_SCREEN_RESULTS.json')
        if result['receipt_sha256'] != launcher.digest(Path(run)/'FEATURE_PANEL_RECEIPT.json'):
            raise ValueError('RECEIPT_HASH_LINK_MISMATCH')
        result['score_contract'] = verified['contract']
        result['conduct_gate_sim'] = [cell for cell in result['conduct_gate_sim']
            if set(cell['group']) == {'category', 'stream'}]
        result['gate_counts'] = counts
        result['first_parity'] = publication.first_gate_parity(verified, prior_first)
        result['publication_status'] = 'PASS_1_DETERMINISM_PENDING_NOT_FINAL'
        result['source_summary_sha256'] = launcher.digest(Path(run)/'ATLAS_SCREEN_RESULTS.json')
        result['advancement_authorized'] = False
        coverage = report.coverage_rows(verified)
        out.mkdir(parents=True, exist_ok=True)
        bench.write_json(out/'PASS1_REPORT.json', result)
        bench.write_json(out/'LINEAGE_COVERAGE.json', dict(
            publication_status=result['publication_status'], category=result['category'],
            fields=verified['receipt']['fields'], coverage_by_month=coverage,
            source_receipt_sha256=result['receipt_sha256']))
        bench.write_json(out/'OPTIMIZER_OUTCOMES.json', result['optimizer_outcomes'])
        (out/'SUMMARY.md').write_text(
            '# PASS 1 — DETERMINISM PENDING\n\n'
            'Completed first-pass scores, not a final verified tour publication. '
            'No advancement is authorized by this provisional report.\n\n'+publication.markdown(result),
            encoding='utf-8', newline='\n')
        print(result['category'], result['publication_status'], counts, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('run','prior-first','out'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    publish(args.run, args.prior_first, args.out)
