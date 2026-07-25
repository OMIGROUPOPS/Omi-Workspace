#!/usr/bin/env python3
"""Fixture harness: reproduce the w1r2 grid-runner stdout-emit failure.

FORENSIC FIXTURE ONLY. Consumes no real scoring inputs, no package data,
no candidate streams, no holdout. It replicates ONLY the runner's output
pattern (window1_round2_grid_runner.py emit()/failure-handler shape) with
synthetic messages, and exercises it against every output-handle class:

  console_inherit      normal attached console
  redirect_file        stdout redirected to a file
  redirect_devnull     stdout redirected to os.devnull
  pipe_open            stdout is a pipe with a live reader
  pipe_closed_early    stdout is a pipe whose reader closed mid-run
  detached_no_console  DETACHED_PROCESS, stdout handle never valid
  closed_in_process    child closes sys.stdout before emitting

Each child replicates the exact emit sequence:
    stdout_lines.append(message)   # in-memory tee (survives print failure)
    print(message, flush=True)     # the failing statement
then, on exception, writes STDOUT/STDERR/FAILURE files exactly like the
runner's except-handler, proving the failure-path file writes survive a
dead stdout handle. It also exercises the proposed repair (safe_emit with
OSError/ValueError suppression + authoritative PROGRESS.log file) under
the same conditions.

Usage:  python -B fixture_emit_handles.py --out FIXTURE_RESULTS.json
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
import json, sys, time, traceback

mode = sys.argv[1]            # "runner" (current pattern) | "repaired"
result_path = sys.argv[2]     # verdict file (never stdout)
work_dir = sys.argv[3]        # simulated result directory
delay = float(sys.argv[4])    # seconds before the mid-run emit

if len(sys.argv) > 5 and sys.argv[5] == "close-stdout":
    sys.stdout.close()

from pathlib import Path
result_dir = Path(work_dir)
result_dir.mkdir(parents=True, exist_ok=True)
stdout_lines = []
stderr_lines = []
progress_path = result_dir / "PROGRESS.log"

def emit_runner(message):
    # Exact shape of window1_round2_grid_runner.py lines 1075-1077.
    stdout_lines.append(message)
    print(message, flush=True)

def emit_repaired(message):
    # Proposed repair: authoritative file write first, console best-effort.
    stdout_lines.append(message)
    with progress_path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(message + "\n")
        fh.flush()
    try:
        print(message, flush=True)
    except (OSError, ValueError):
        pass

emit = emit_runner if mode == "runner" else emit_repaired
verdict = {
    "mode": mode,
    "emits_attempted": 0,
    "emits_survived": 0,
    "exception_type": None,
    "exception_errno": None,
    "exception_str": None,
    "failure_files_written": False,
    "progress_file_lines": None,
    "completed_all_emits": False,
}
try:
    emit("execution_id=fixture-synthetic")
    verdict["emits_attempted"] += 1
    verdict["emits_survived"] += 1
    emit("candidate_start=1:synthetic_candidate")
    verdict["emits_attempted"] += 1
    verdict["emits_survived"] += 1
    # Simulated candidate work; the ledger write happens BEFORE the
    # completion emit, mirroring the real ordering.
    (result_dir / "01_synthetic_EVENT_LEDGER.jsonl").write_text(
        '{"event_id": "synthetic", "classification": "fixture"}\n',
        encoding="utf-8", newline="\n",
    )
    time.sleep(delay)
    verdict["emits_attempted"] += 1
    emit("candidate_complete=1:synthetic_candidate")
    verdict["emits_survived"] += 1
    verdict["completed_all_emits"] = True
    exit_code = 0
except Exception as exc:
    # Exact shape of the runner's except-handler file preservation.
    message = f"{type(exc).__name__}: {exc}"
    stderr_lines.extend([message, traceback.format_exc()])
    try:
        (result_dir / "STDOUT.log").write_text(
            "\n".join(stdout_lines) + ("\n" if stdout_lines else ""),
            encoding="utf-8", newline="\n",
        )
        (result_dir / "STDERR.log").write_text(
            "\n".join(stderr_lines) + "\n", encoding="utf-8", newline="\n",
        )
        (result_dir / "EXECUTION_FAILURE.json").write_text(
            json.dumps({"error": message, "fixture": True}, indent=2,
                       sort_keys=True) + "\n",
            encoding="utf-8", newline="\n",
        )
        verdict["failure_files_written"] = True
    except Exception:
        verdict["failure_files_written"] = False
    verdict["exception_type"] = type(exc).__name__
    verdict["exception_errno"] = getattr(exc, "errno", None)
    verdict["exception_str"] = str(exc)
    exit_code = 1
if progress_path.exists():
    verdict["progress_file_lines"] = len(
        progress_path.read_text(encoding="utf-8").splitlines()
    )
Path(result_path).write_text(
    json.dumps(verdict, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
raise SystemExit(exit_code)
'''


def run_case(case: str, mode: str, base: Path) -> dict:
    tag = f"{case}__{mode}"
    work = base / tag
    work.mkdir(parents=True, exist_ok=True)
    child_py = base / "_child.py"
    if not child_py.exists():
        child_py.write_text(CHILD_SOURCE, encoding="utf-8", newline="\n")
    result_path = work / "_verdict.json"
    delay = "1.0" if case == "pipe_closed_early" else "0.0"
    argv = [sys.executable, "-B", str(child_py), mode, str(result_path),
            str(work / "results"), delay]
    kwargs: dict = {}
    extra: list[str] = []

    if case == "console_inherit":
        kwargs["stdout"] = None
    elif case == "redirect_file":
        kwargs["stdout"] = open(work / "_stdout_redirect.txt", "w")
    elif case == "redirect_devnull":
        kwargs["stdout"] = open(os.devnull, "w")
    elif case == "pipe_open":
        kwargs["stdout"] = subprocess.PIPE
    elif case == "pipe_closed_early":
        kwargs["stdout"] = subprocess.PIPE
    elif case == "detached_no_console":
        kwargs["stdout"] = None
        kwargs["stderr"] = subprocess.DEVNULL
        kwargs["stdin"] = subprocess.DEVNULL
        if os.name == "nt":
            kwargs["creationflags"] = (
                subprocess.DETACHED_PROCESS
                | subprocess.CREATE_NEW_PROCESS_GROUP
            )
    elif case == "closed_in_process":
        kwargs["stdout"] = subprocess.PIPE
        extra = ["close-stdout"]
    else:
        raise ValueError(case)

    proc = subprocess.Popen(argv + extra, **kwargs)
    if case == "pipe_closed_early":
        time.sleep(0.3)          # let the first two emits land
        proc.stdout.close()      # reader vanishes mid-run
    elif case in ("pipe_open", "closed_in_process"):
        proc.stdout.read()
        proc.stdout.close()
    exit_code = proc.wait(timeout=60)
    for handle in (kwargs.get("stdout"),):
        if hasattr(handle, "close") and handle not in (None,):
            try:
                handle.close()
            except Exception:
                pass
    verdict = {"case": case, "mode": mode, "exit_code": exit_code,
               "verdict_file_missing": True}
    if result_path.exists():
        verdict.update(json.loads(result_path.read_text(encoding="utf-8")))
        verdict["verdict_file_missing"] = False
    results_dir = work / "results"
    verdict["files_in_result_dir"] = (
        sorted(p.name for p in results_dir.iterdir())
        if results_dir.exists() else []
    )
    return verdict


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    cases = [
        "console_inherit",
        "redirect_file",
        "redirect_devnull",
        "pipe_open",
        "pipe_closed_early",
        "detached_no_console",
        "closed_in_process",
    ]
    base = Path(tempfile.mkdtemp(prefix="w1r2_emit_fixture_"))
    rows = []
    for case in cases:
        for mode in ("runner", "repaired"):
            row = run_case(case, mode, base)
            rows.append(row)
            print(
                f"{case:>20s} {mode:>9s} exit={row['exit_code']} "
                f"exc={row.get('exception_type')} "
                f"errno={row.get('exception_errno')} "
                f"all_emits={row.get('completed_all_emits')} "
                f"failure_files={row.get('failure_files_written')}",
                file=sys.stderr,
            )
    summary = {
        "schema_version": "w1r2-emit-fixture-results-v1",
        "platform": sys.platform,
        "python": sys.version.split()[0],
        "fixture_root": str(base),
        "synthetic_only": True,
        "cases": rows,
    }
    args.out.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
