import importlib.util
from pathlib import Path


SCRIPT = (
    Path(__file__).parents[1]
    / "analysis" / "window1_public_coverage_merge.py"
)
SPEC = importlib.util.spec_from_file_location(
    "window1_public_coverage_merge", SCRIPT
)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(module)


def test_imports_coverage_contract():
    assert module.coverage.D == 804
    assert (
        module.coverage.VERSION == "window1-source-coverage-v1"
    )
