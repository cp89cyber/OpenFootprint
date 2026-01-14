import os
import subprocess
import sys
from pathlib import Path


def test_cli_help_includes_commands():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    result = subprocess.run(
        [sys.executable, "-m", "openfootprint", "--help"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0
    assert "lookup" in result.stdout
    assert "sources" in result.stdout
