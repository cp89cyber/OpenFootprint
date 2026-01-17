import subprocess
import sys


def test_nameintel_dry_run_exits_zero():
    proc = subprocess.run(
        [sys.executable, "-m", "openfootprint", "nameintel", "--first", "John", "--last", "Doe", "--dry-run"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "permutations" in (proc.stdout + proc.stderr).lower()

