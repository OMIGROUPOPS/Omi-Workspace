#!/usr/bin/env python3
"""Independent refusal-fixture campaign against the Round-2 grid runner at
codex 4b243bab. Auditor-authored; uses tampered in-memory/scratch copies of
the committed package only. Never runs execute mode, never scores, never
touches the holdout.

Usage: python refusal_fixtures.py <worktree> <out-json>
"""

import copy
import json
import sys
from pathlib import Path

WT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
SCRATCH = OUT.parent.parent / "_pkg_scratch"
SCRATCH.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(WT / "arb-executor/analysis"))

import window1_round2_grid_runner as runner  # noqa: E402

PKG = WT / ".claude/window1_round2_execution_package_20260724/SCORING_INPUT_BUNDLE.json"
package = json.loads(PKG.read_text(encoding="utf-8"))
findings = {}


def expect_refusal(name, mutate, expect_substring):
    tampered = copy.deepcopy(package)
    mutate(tampered)
    path = SCRATCH / f"{name}.json"
    path.write_text(json.dumps(tampered), encoding="utf-8")
    try:
        runner.validate_package(WT, path, mode="validate-only")
        findings[name] = {"refused": False, "VIOLATION": True}
    except runner.GridExecutionError as err:
        findings[name] = {
            "refused": True,
            "error": str(err)[:120],
            "expected_reason_matched": expect_substring in str(err),
        }


def rehash(pkg):
    material = dict(pkg)
    material.pop("input_bundle_sha256", None)
    pkg["input_bundle_sha256"] = runner.canonical_sha256(material)


# 1. bundle-hash tamper (content changed, hash left stale)
expect_refusal(
    "bundle_hash_mismatch",
    lambda p: p.update({"target_PC": 500}),
    "input-bundle hash",
)

# 2-5. candidate grid tampering (rehashed so the grid check is reached)
def drop_candidate(p):
    p["candidate_ids"] = p["candidate_ids"][:-1]
    rehash(p)


def add_candidate(p):
    p["candidate_ids"] = p["candidate_ids"] + ["r2_new__x__hold"]
    rehash(p)


def dup_candidate(p):
    p["candidate_ids"] = p["candidate_ids"][:-1] + [p["candidate_ids"][0]]
    rehash(p)


def reorder_candidate(p):
    p["candidate_ids"] = list(reversed(p["candidate_ids"]))
    rehash(p)


expect_refusal("candidate_missing", drop_candidate, "candidate grid refused")
expect_refusal("candidate_additional", add_candidate, "candidate grid refused")
expect_refusal("candidate_duplicated", dup_candidate, "duplicated")
expect_refusal("candidate_reordered", reorder_candidate, "reordered")

# 6. execution identity / command tamper
def change_id(p):
    p["execution_id"] = "w1r2-dev-EVIL-grid2"
    rehash(p)


expect_refusal("execution_id_changed", change_id, "identity/command")


def change_cmd(p):
    p["exact_execution_command"] = p["exact_execution_command"] + " --fast"
    rehash(p)


expect_refusal("command_changed", change_cmd, "identity/command")

# 7. holdout / date tamper
def holdout_dates(p):
    p["development_dates"] = p["development_dates"][:-1] + ["2026-07-25"]
    rehash(p)


expect_refusal("holdout_in_dev_dates", holdout_dates, "contract changed")

# 8. denominator tamper
def change_d(p):
    p["D"] = 803
    rehash(p)


expect_refusal("denominator_changed", change_d, "denominator")

# 9. date-fence unit checks on the frozen validator
try:
    runner.validate_dates([
        {"event_id": f"E{i}", "event_date": "2026-07-25"} for i in range(804)
    ])
    findings["validate_dates_holdout"] = {"refused": False, "VIOLATION": True}
except runner.GridExecutionError as err:
    findings["validate_dates_holdout"] = {
        "refused": True, "error": str(err)[:80],
        "expected_reason_matched": "holdout hard-refused" in str(err),
    }
try:
    runner.validate_dates([
        {"event_id": f"E{i}", "event_date": "2026-07-22"} for i in range(804)
    ])
    findings["validate_dates_nondev"] = {"refused": False, "VIOLATION": True}
except runner.GridExecutionError as err:
    findings["validate_dates_nondev"] = {
        "refused": True, "error": str(err)[:80],
        "expected_reason_matched": "non-development" in str(err),
    }

# 10. dispatcher single-invocation law
calls = []


def fake_score(bundle, contract):
    calls.append(bundle["candidate_id"])
    return {"candidate_id": bundle["candidate_id"]}


d = runner.FrozenScorerDispatcher(score_fn=fake_score)
try:
    d.invoke("r2_causal_steer__park_join__hold", {"candidate_id": "x"}, {})
    findings["dispatcher_out_of_order"] = {"refused": False, "VIOLATION": True}
except runner.GridExecutionError as err:
    findings["dispatcher_out_of_order"] = {
        "refused": True, "error": str(err)[:80],
    }
d2 = runner.FrozenScorerDispatcher(score_fn=fake_score)
calls.clear()
for cid in runner.FROZEN_CANDIDATES:
    d2.invoke(cid, {"candidate_id": cid}, {})
try:
    d2.invoke(
        runner.FROZEN_CANDIDATES[0],
        {"candidate_id": runner.FROZEN_CANDIDATES[0]},
        {},
    )
    findings["dispatcher_double_invoke"] = {"refused": False, "VIOLATION": True}
except runner.GridExecutionError as err:
    findings["dispatcher_double_invoke"] = {
        "refused": True, "error": str(err)[:80],
        "single_pass_counts_all_one": all(
            v == 1 for v in d2.counts.values()
        ),
        "invocation_order_frozen": calls == runner.FROZEN_CANDIDATES,
    }

# 11. untampered package on a detached worktree: progresses past hash,
# identity, grid, and denominator checks, then refuses at the git-state
# guard (this audit worktree is detached, not the frozen branch).
try:
    runner.validate_package(WT, PKG, mode="validate-only")
    findings["untampered_detached_worktree"] = {
        "refused": False,
        "note": "validated fully (unexpected on detached head)",
    }
except runner.GridExecutionError as err:
    findings["untampered_detached_worktree"] = {
        "refused": True,
        "error": str(err)[:120],
        "refused_at_branch_guard": "frozen Codex branch" in str(err),
        "meaning": (
            "hash/identity/grid/denominator checks all passed on the "
            "committed package; refusal happened only at the git-state "
            "guard, which is the correct behavior off-branch"
        ),
    }

OUT.write_text(json.dumps(findings, indent=2) + "\n", encoding="utf-8")
print(json.dumps(findings, indent=2))
