import ast
from pathlib import Path


SOURCE = (
    Path(__file__).resolve().parents[1] / "ws_depth_recorder.py"
).read_text(encoding="utf-8")


def load_apply_book():
    tree = ast.parse(SOURCE)
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "_apply_book_message"
    )
    namespace = {}
    module = ast.fix_missing_locations(ast.Module(
        body=[
            ast.Assign(
                targets=[ast.Name(id="_books", ctx=ast.Store())],
                value=ast.Dict(keys=[], values=[]),
            ),
            function,
        ],
        type_ignores=[],
    ))
    exec(
        compile(
            module,
            "<ws-depth-contract>",
            "exec",
        ),
        namespace,
    )
    return namespace["_apply_book_message"]


def test_current_fixed_point_snapshot_builds_two_sided_bbo():
    apply_book = load_apply_book()
    result = apply_book({
        "type": "orderbook_snapshot",
        "msg": {
            "market_ticker": "KXATPMATCH-X-A",
            "yes_dollars_fp": [["0.4200", "12.00"]],
            "no_dollars_fp": [["0.5500", "9.00"]],
        },
    })
    assert result == {
        "market_ticker": "KXATPMATCH-X-A",
        "yes_bid": 42,
        "yes_ask": 45,
        "no_bid": 55,
        "no_ask": 58,
        "denominator_status": "AVAILABLE",
    }


def test_current_fixed_point_delta_updates_reconstructed_book():
    apply_book = load_apply_book()
    ticker = "KXATPMATCH-X-A"
    apply_book({
        "type": "orderbook_snapshot",
        "msg": {
            "market_ticker": ticker,
            "yes_dollars_fp": [["0.4200", "12.00"]],
            "no_dollars_fp": [["0.5500", "9.00"]],
        },
    })
    result = apply_book({
        "type": "orderbook_delta",
        "msg": {
            "market_ticker": ticker,
            "side": "yes",
            "price_dollars": "0.4300",
            "delta_fp": "5.00",
        },
    })
    assert result["yes_bid"] == 43
    assert result["yes_ask"] == 45
    assert result["denominator_status"] == "AVAILABLE"
