from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path


@dataclass(frozen=True)
class RunPaths:
    run_dir: Path
    raw_dir: Path


def _now_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def create_run_dir(base_dir: Path) -> RunPaths:
    run_id = _now_id()
    run_dir = base_dir / run_id
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=False)
    return RunPaths(run_dir=run_dir, raw_dir=raw_dir)


def save_raw_artifact(run_paths: RunPaths, url: str, content: bytes) -> Path:
    digest = sha256(content + url.encode("utf-8")).hexdigest()
    raw_path = run_paths.raw_dir / f"{digest}.bin"
    raw_path.write_bytes(content)
    return raw_path
