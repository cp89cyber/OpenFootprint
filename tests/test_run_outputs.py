from pathlib import Path

from openfootprint.core.schema import RunManifest
from openfootprint.storage.runs import create_run_dir, write_json, write_text, write_manifest


def test_write_outputs(tmp_path: Path):
    run_paths = create_run_dir(tmp_path)
    json_path = write_json(run_paths.run_dir, "report.json", {"ok": True})
    md_path = write_text(run_paths.run_dir, "report.md", "hello")

    manifest = RunManifest(
        run_id=run_paths.run_dir.name,
        inputs={"username": "alice"},
        sources=["github"],
        started_at="2026-01-14T00:00:00Z",
        finished_at=None,
        config={"http": {"timeout_seconds": 1}},
    )
    manifest_path = write_manifest(run_paths, manifest)

    assert json_path.exists()
    assert md_path.read_text(encoding="utf-8") == "hello"
    assert manifest_path.name == "manifest.json"
