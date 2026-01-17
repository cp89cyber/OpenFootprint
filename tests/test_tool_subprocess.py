from pathlib import Path
import subprocess

from openfootprint.tools.subprocess import run_command


def test_run_command_captures_output(monkeypatch, tmp_path: Path):
    def fake_run(cmd, cwd, env, capture_output, text, timeout, check):
        return subprocess.CompletedProcess(cmd, 0, stdout="ok\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = run_command(["echo", "ok"], tmp_path, {"X": "1"}, 2)
    assert result.returncode == 0
    assert result.stdout == "ok\n"
