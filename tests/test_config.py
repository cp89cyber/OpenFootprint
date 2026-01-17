from pathlib import Path

from openfootprint.core.config import load_config


def test_load_config_merges_defaults(tmp_path: Path):
    config_path = tmp_path / "openfootprint.toml"
    config_path.write_text("[sources]\nenabled = ['github']\n", encoding="utf-8")

    config = load_config(config_path)

    assert "github" in config["sources"]["enabled"]
    assert config["http"]["timeout_seconds"] == 15


def test_config_includes_tools_defaults():
    config = load_config(None)
    assert "tools" in config
    assert "sherlock_path" in config["tools"]
