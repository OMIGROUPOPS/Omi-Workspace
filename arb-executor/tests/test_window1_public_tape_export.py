import importlib.util
import gzip
import json
import tempfile
from contextlib import contextmanager
from pathlib import Path


PATH = (
    Path(__file__).resolve().parents[1]
    / "analysis"
    / "window1_public_tape_export.py"
)
SPEC = importlib.util.spec_from_file_location("window1_public_tape_export", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


@contextmanager
def raises(error_type, text):
    try:
        yield
    except error_type as exc:
        assert text in str(exc)
    else:
        raise AssertionError(f"expected {error_type.__name__}")


def test_canonical_trade_uses_receipt_exchange_clock_and_verified_size():
    row = {
        "trade_id": "tr-1",
        "ticker": "T-A",
        "created_time": "2026-07-12T12:34:56.123Z",
        "yes_price_dollars": "0.37",
        "count_fp": "5.00",
        "taker_side": "yes",
    }
    got = MODULE.canonical_trade(row, "T-A")
    assert got["receipt_id"] == "tr-1"
    assert got["exchange_ts"] == "2026-07-12T12:34:56.123000Z"
    assert got["price_cents"] == 37
    assert got["size"] == 5
    assert got["true_print"] is True


def test_zero_or_missing_size_stays_zero():
    assert MODULE.nonnegative_size(None) == 0
    assert MODULE.nonnegative_size("") == 0
    assert MODULE.nonnegative_size("0.00") == 0


def test_ticker_mismatch_fails_closed():
    row = {
        "trade_id": "tr-1",
        "ticker": "OTHER",
        "created_time": "2026-07-12T12:34:56Z",
        "yes_price_dollars": "0.37",
        "count_fp": "5",
    }
    with raises(MODULE.ExportError, "ticker mismatch"):
        MODULE.canonical_trade(row, "REQUESTED")


def test_request_json_rejects_non_object_payload():
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b"[]"

    def opener(*args, **kwargs):
        return Response()

    with raises(MODULE.ExportError, "non-object"):
        MODULE.request_json(
            "https://example.test",
            attempts=1,
            timeout_seconds=1,
            opener=opener,
        )


def test_load_tickers_enforces_immutable_804_game_denominator(tmp_path=None):
    temporary = (
        tempfile.TemporaryDirectory() if tmp_path is None else None
    )
    root = Path(temporary.name) if temporary else tmp_path
    path = root / "events.jsonl"
    rows = []
    for index in range(804):
        rows.append({
            "event_id": f"E{index}",
            "event_date": "2026-07-12",
            "legs": [
                {"ticker": f"E{index}-A"},
                {"ticker": f"E{index}-B"},
            ],
        })
    path.write_text(
        "".join(json.dumps(row) + "\n" for row in rows),
        encoding="utf-8",
    )
    tickers, days = MODULE.load_tickers(path)
    assert len(tickers) == 1608
    assert days["E0-A"] == "2026-07-12"
    if temporary:
        temporary.cleanup()


def test_resume_revalidates_raw_terminal_page_without_network(tmp_path=None):
    temporary = (
        tempfile.TemporaryDirectory() if tmp_path is None else None
    )
    root = Path(temporary.name) if temporary else tmp_path
    raw_dir = root / "raw"
    raw_dir.mkdir()
    page = [{
        "page": 1,
        "request": {"ticker": "T-A", "limit": 1000, "cursor": ""},
        "response": {
            "trades": [{
                "trade_id": "tr-1",
                "ticker": "T-A",
                "created_time": "2026-07-12T12:34:56Z",
                "yes_price_dollars": "0.37",
                "count_fp": "5",
            }],
            "cursor": "",
        },
    }]
    with gzip.open(raw_dir / "T-A.json.gz", "wt", encoding="utf-8") as handle:
        json.dump(page, handle)
    got = MODULE.fetch_ticker(
        "T-A", "https://should-not-be-queried.test", raw_dir,
        page_limit=1000, attempts=1, timeout_seconds=1, resume=True,
    )
    assert got["resumed"] is True
    assert got["trade_count"] == 1
    if temporary:
        temporary.cleanup()
