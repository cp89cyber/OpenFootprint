from pathlib import Path

from openfootprint.storage.runs import create_run_dir, save_raw_artifact


def test_run_dir_and_raw_artifact(tmp_path: Path):
    run_dir = create_run_dir(tmp_path)
    raw_path = save_raw_artifact(run_dir, "https://example.com", b"hello")
    assert raw_path.exists()
    assert "raw" in raw_path.parts
