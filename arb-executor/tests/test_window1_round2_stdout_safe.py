from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "arb-executor" / "analysis"))

import window1_round2_grid_runner as grid  # noqa: E402


class FailAfterOneWrite:
    def __init__(self) -> None:
        self.write_calls = 0

    def write(self, value: str) -> int:
        self.write_calls += 1
        if self.write_calls > 1:
            raise OSError(22, "synthetic vanished pipe")
        return len(value)

    def flush(self) -> None:
        return None


def test_progress_flush_precedes_cosmetic_console(monkeypatch, tmp_path):
    progress = tmp_path / "PROGRESS.log"

    class OrderCheckingStream:
        def write(self, value: str) -> int:
            assert progress.read_text(encoding="utf-8") == "first\n"
            return len(value)

        def flush(self) -> None:
            assert progress.read_text(encoding="utf-8") == "first\n"

    monkeypatch.setattr(sys, "stdout", OrderCheckingStream())
    lines: list[str] = []
    grid.ProgressEmitter(
        progress, lines, grid.ConsoleEchoGuard()
    )("first")
    assert lines == ["first"]


def test_pipe_reader_disappears_after_initial_success(
    monkeypatch, tmp_path,
):
    reader_fd, writer_fd = os.pipe()
    writer = os.fdopen(writer_fd, "w", encoding="utf-8", buffering=1)
    monkeypatch.setattr(sys, "stdout", writer)
    guard = grid.ConsoleEchoGuard()
    progress = tmp_path / "PROGRESS.log"
    emit = grid.ProgressEmitter(progress, [], guard)
    emit("reader_alive")
    os.close(reader_fd)
    emit("reader_gone")
    assert progress.read_text(encoding="utf-8") == (
        "reader_alive\nreader_gone\n"
    )
    assert guard.stdout_enabled is False
    assert guard.receipt()["stdout_rebound_to_devnull"] is True
    assert sys.stdout is not writer
    with contextlib.suppress(OSError, ValueError):
        writer.close()


def test_detached_non_console_stdout_is_nonfatal(monkeypatch, tmp_path):
    with open(os.devnull, "w", encoding="utf-8") as detached:
        monkeypatch.setattr(sys, "stdout", detached)
        guard = grid.ConsoleEchoGuard()
        progress = tmp_path / "PROGRESS.log"
        emit = grid.ProgressEmitter(progress, [], guard)
        emit("detached_start")
        emit("detached_complete")
        assert guard.stdout_enabled is True
    assert progress.read_text(encoding="utf-8") == (
        "detached_start\ndetached_complete\n"
    )


def test_explicitly_closed_stdout_valueerror_is_nonfatal(
    monkeypatch, tmp_path,
):
    closed = io.StringIO()
    closed.close()
    monkeypatch.setattr(sys, "stdout", closed)
    guard = grid.ConsoleEchoGuard()
    progress = tmp_path / "PROGRESS.log"
    grid.ProgressEmitter(progress, [], guard)("closed_stdout")
    assert progress.read_text(encoding="utf-8") == "closed_stdout\n"
    assert guard.stdout_enabled is False
    assert guard.stdout_failure is not None
    assert guard.stdout_failure.startswith("ValueError:")
    assert sys.stdout is not closed


def test_closed_stderr_echo_is_equally_nonfatal(monkeypatch):
    closed = io.StringIO()
    closed.close()
    monkeypatch.setattr(sys, "stderr", closed)
    guard = grid.ConsoleEchoGuard()
    guard.echo_stderr("cosmetic failure echo")
    assert guard.stderr_enabled is False
    assert guard.stderr_failure is not None
    assert guard.stderr_failure.startswith("ValueError:")
    assert sys.stderr is not closed


def test_exit_time_flush_after_pipe_failure_returns_zero(tmp_path):
    script = textwrap.dedent(
        f"""
        import json
        import os
        import sys
        from pathlib import Path

        sys.path.insert(0, {str(ROOT / "arb-executor" / "analysis")!r})
        import window1_round2_grid_runner as grid

        output = Path({str(tmp_path)!r})
        read_fd, write_fd = os.pipe()
        writer = os.fdopen(write_fd, "w", encoding="utf-8", buffering=1)
        sys.stdout = writer
        guard = grid.ConsoleEchoGuard()
        emit = grid.ProgressEmitter(output / "PROGRESS.log", [], guard)
        emit("before_reader_exit")
        os.close(read_fd)
        emit("after_reader_exit")
        grid.write_json(output / "FINAL_RECEIPT.json", {{
            "fixture_candidates_completed": 2,
            "scored": False,
            "console": guard.receipt(),
        }})
        """
    )
    completed = subprocess.run(
        [sys.executable, "-B", "-c", script],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr.decode(
        errors="replace"
    )
    assert (tmp_path / "PROGRESS.log").read_text(encoding="utf-8") == (
        "before_reader_exit\nafter_reader_exit\n"
    )
    receipt = json.loads(
        (tmp_path / "FINAL_RECEIPT.json").read_text(encoding="utf-8")
    )
    assert receipt["scored"] is False
    assert receipt["console"]["stdout_rebound_to_devnull"] is True


def test_all_fixture_candidates_and_final_receipt_survive_console_loss(
    monkeypatch, tmp_path,
):
    failing = FailAfterOneWrite()
    monkeypatch.setattr(sys, "stdout", failing)
    guard = grid.ConsoleEchoGuard()
    progress = tmp_path / "PROGRESS.log"
    lines: list[str] = []
    emit = grid.ProgressEmitter(progress, lines, guard)
    fixture_candidates = [
        f"fixture_candidate_{index}" for index in range(1, 9)
    ]
    emit("fixture_execution_start")
    for candidate in fixture_candidates:
        emit(f"candidate_start={candidate}")
        emit(f"candidate_complete={candidate}")
    emit("final_receipts_written")
    grid.write_json(tmp_path / "FINAL_RECEIPT.json", {
        "candidate_order": fixture_candidates,
        "candidate_count": len(fixture_candidates),
        "performance_results_produced": False,
        "scorer_invocations": 0,
        "final_receipts_written": True,
        "console": guard.receipt(),
    })
    progress_lines = progress.read_text(encoding="utf-8").splitlines()
    assert progress_lines == lines
    assert progress_lines[-1] == "final_receipts_written"
    assert len(progress_lines) == 18
    receipt = json.loads(
        (tmp_path / "FINAL_RECEIPT.json").read_text(encoding="utf-8")
    )
    assert receipt["candidate_count"] == 8
    assert receipt["candidate_order"] == fixture_candidates
    assert receipt["performance_results_produced"] is False
    assert receipt["scorer_invocations"] == 0
    assert receipt["final_receipts_written"] is True
    assert receipt["console"]["stdout_rebound_to_devnull"] is True
