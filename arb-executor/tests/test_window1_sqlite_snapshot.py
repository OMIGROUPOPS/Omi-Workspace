import importlib.util
import pathlib
import sqlite3


PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "analysis"
    / "window1_sqlite_snapshot.py"
)
SPEC = importlib.util.spec_from_file_location(
    "window1_sqlite_snapshot", PATH
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_hash_is_stable_for_snapshot_bytes(tmp_path):
    path = tmp_path / "tiny.db"
    connection = sqlite3.connect(path)
    connection.execute("create table t(v integer)")
    connection.execute("insert into t values (1)")
    connection.commit()
    connection.close()
    assert MODULE.sha256_file(path) == MODULE.sha256_file(path)
