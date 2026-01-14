import os
import subprocess
import sys
from pathlib import Path


def test_cli_lookup_runs(tmp_path: Path):
    config_path = tmp_path / "openfootprint.toml"
    config_path.write_text("[sources]\nenabled = ['nonexistent']\n", encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "openfootprint",
            "lookup",
            "--username",
            "alice",
            "--output",
            str(tmp_path),
            "--config",
            str(config_path),
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0
    assert "Sources:" in result.stdout
    assert "github" not in result.stdout
