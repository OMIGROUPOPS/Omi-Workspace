#!/usr/bin/env python3
"""Independent process-level fixture campaign for the stdout-safe runner.

AUDIT FIXTURE ONLY — synthetic candidates, temp directories, zero real
scoring inputs, zero scorer/instrument invocations. Imports ONLY the
ConsoleEchoGuard / ProgressEmitter classes from the frozen runner at the
PRE-RUN under audit (path passed via --runner-dir) and drives them through
a full synthetic 8-candidate emission sequence in a child process under
every output-handle class:

  pipe_live             live pipe reader for the whole run
  pipe_closed_early     reader vanishes after the first successful write
  detached_no_console   DETACHED_PROCESS (Windows), no console at all
  redirect_file         stdout redirected to a file
  redirect_devnull      stdout redirected to os.devnull
  closed_in_process     child closes sys.stdout before any emission
  stderr_dead           stderr closed; cosmetic stderr echo must be nonfatal

Asserted per case: child exit code 0, PROGRESS.log contains exactly the
18 expected one-line events in order with no duplicates or gaps, the final
receipt file exists and is valid JSON, and (for the console-loss cases)
the guard receipt records the permanent devnull rebind.

Usage:
  python -B fixture_stdout_safe_campaign.py --runner-dir <analysis dir> \
      --out FIXTURE_RESULTS.json
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CHILD_SOURCE = r'''
import io, json, os, sys, time
runner_dir, result_path, work_dir, case = sys.argv[1:5]
sys.path.insert(0, runner_dir)
import window1_round3_grid_runner as grid

from pathlib import Path
result_dir = Path(work_dir)
result_dir.mkdir(parents=True, exist_ok=True)

if case == "closed_in_process":
    closed = io.StringIO()
    closed.close()
    sys.stdout = closed
if case == "stderr_dead":
    dead = io.StringIO()
    dead.close()
    sys.stderr = dead

guard = grid.ConsoleEchoGuard()
lines = []
emit = grid.ProgressEmitter(result_dir / "PROGRESS.log", lines, guard)

candidates = [f"synthetic_candidate_{i}" for i in range(1, 9)]
emit("fixture_execution_start")
for index, candidate in enumerate(candidates, 1):
    emit(f"candidate_start={index}:{candidate}")
    if case == "pipe_closed_early" and index == 1:
        # parent closes the read end while we sleep, so the NEXT
        # flushed console write hits a vanished reader
        time.sleep(0.6)
    emit(f"candidate_complete={index}:{candidate}")
emit("final_receipts_written")
if case == "stderr_dead":
    guard.echo_stderr("cosmetic failure echo must be nonfatal")

grid.write_json(result_dir / "FINAL_RECEIPT.json", {
    "candidate_count": len(candidates),
    "performance_results_produced": False,
    "scorer_invocations": 0,
    "console": guard.receipt(),
    "tee_lines": len(lines),
})
Path(result_path).write_text(json.dumps({
    "case": case,
    "console": guard.receipt(),
    "tee_lines": len(lines),
}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
'''

EXPECTED_EVENTS = (
    ["fixture_execution_start"]
    + [
        line
        for i in range(1, 9)
        for line in (
            f"candidate_start={i}:synthetic_candidate_{i}",
            f"candidate_complete={i}:synthetic_candidate_{i}",
        )
    ]
    + ["final_receipts_written"]
)


def run_case(case: str, runner_dir: Path, base: Path) -> dict:
    work = base / case
    work.mkdir(parents=True, exist_ok=True)
    child_py = base / "_child.py"
    if not child_py.exists():
        child_py.write_text(CHILD_SOURCE, encoding="utf-8", newline="\n")
    verdict_path = work / "_verdict.json"
    argv = [sys.executable, "-B", str(child_py), str(runner_dir),
            str(verdict_path), str(work / "results"), case]
    kwargs: dict = {}
    if case in ("pipe_live", "pipe_closed_early", "closed_in_process",
                "stderr_dead"):
        kwargs["stdout"] = subprocess.PIPE
    elif case == "redirect_file":
        kwargs["stdout"] = open(work / "_stdout.txt", "w")
    elif case == "redirect_devnull":
        kwargs["stdout"] = open(os.devnull, "w")
    elif case == "detached_no_console":
        kwargs["stdout"] = None
        kwargs["stderr"] = subprocess.DEVNULL
        kwargs["stdin"] = subprocess.DEVNULL
        if os.name == "nt":
            kwargs["creationflags"] = (
                subprocess.DETACHED_PROCESS
                | subprocess.CREATE_NEW_PROCESS_GROUP
            )
    else:
        raise ValueError(case)

    proc = subprocess.Popen(argv, **kwargs)
    if case == "pipe_closed_early":
        time.sleep(0.3)
        proc.stdout.close()
    elif case in ("pipe_live", "closed_in_process", "stderr_dead"):
        proc.stdout.read()
        proc.stdout.close()
    exit_code = proc.wait(timeout=90)
    handle = kwargs.get("stdout")
    if hasattr(handle, "close"):
        try:
            handle.close()
        except Exception:
            pass

    progress_path = work / "results" / "PROGRESS.log"
    events = (
        progress_path.read_text(encoding="utf-8").splitlines()
        if progress_path.exists() else None
    )
    receipt_path = work / "results" / "FINAL_RECEIPT.json"
    receipt = (
        json.loads(receipt_path.read_text(encoding="utf-8"))
        if receipt_path.exists() else None
    )
    verdict = (
        json.loads(verdict_path.read_text(encoding="utf-8"))
        if verdict_path.exists() else None
    )
    return {
        "case": case,
        "exit_code": exit_code,
        "progress_events": len(events) if events is not None else None,
        "progress_exact_match": events == EXPECTED_EVENTS,
        "progress_duplicates": (
            len(events) != len(set(events)) if events else None
        ),
        "final_receipt_written": receipt is not None,
        "scorer_invocations": (
            receipt.get("scorer_invocations") if receipt else None
        ),
        "console_receipt": (verdict or {}).get("console"),
        "pass": (
            exit_code == 0
            and events == EXPECTED_EVENTS
            and receipt is not None
            and receipt.get("scorer_invocations") == 0
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runner-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    cases = ["pipe_live", "pipe_closed_early", "detached_no_console",
             "redirect_file", "redirect_devnull", "closed_in_process",
             "stderr_dead"]
    base = Path(tempfile.mkdtemp(prefix="w1r2_stdoutsafe_audit_"))
    rows = [run_case(case, args.runner_dir.resolve(), base) for case in cases]
    summary = {
        "schema_version": "w1r2-stdoutsafe-audit-fixture-v1",
        "platform": sys.platform,
        "python": sys.version.split()[0],
        "runner_dir": str(args.runner_dir),
        "synthetic_only": True,
        "real_scorer_invocations": 0,
        "all_pass": all(row["pass"] for row in rows),
        "cases": rows,
    }
    args.out.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    for row in rows:
        print(
            f"{row['case']:>20s} exit={row['exit_code']} "
            f"events={row['progress_events']} "
            f"exact={row['progress_exact_match']} "
            f"pass={row['pass']}",
            file=sys.stderr,
        )
    return 0 if summary["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
