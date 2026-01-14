import os
import subprocess
import sys
from pathlib import Path


def test_cli_lookup_runs(tmp_path: Path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    result = subprocess.run(
        [sys.executable, "-m", "openfootprint", "lookup", "--username", "alice", "--output", str(tmp_path)],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0
