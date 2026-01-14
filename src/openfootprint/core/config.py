from __future__ import annotations

from pathlib import Path
import tomllib


DEFAULT_CONFIG = {
    "http": {
        "user_agent": "OpenFootprint/0.1 (+https://example.com)",
        "timeout_seconds": 15,
    },
    "rate_limit": {
        "min_interval_seconds": 1.0,
    },
    "sources": {
        "enabled": [],
        "disabled": [],
    },
    "output": {
        "runs_dir": "runs",
    },
}


def _merge_dicts(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: str | Path | None = None) -> dict:
    if path is None:
        return dict(DEFAULT_CONFIG)

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    override = tomllib.loads(config_path.read_text(encoding="utf-8"))
    return _merge_dicts(DEFAULT_CONFIG, override)
