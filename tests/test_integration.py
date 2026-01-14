from pathlib import Path

from openfootprint.core.inputs import LookupInputs
from openfootprint.core.pipeline import run_lookup
from openfootprint.sources.developer.github import SOURCE as GITHUB
from openfootprint.sources.registry import SourceRegistry


def test_integration_with_fixture(tmp_path: Path, monkeypatch):
    html = Path("tests/fixtures/github.html").read_text(encoding="utf-8")

    class FakeResponse:
        status_code = 200
        content = html.encode("utf-8")
        url = "https://github.com/alice"
        headers = {}

    def fake_http_get(_url, _headers, _timeout):
        return FakeResponse()

    def fake_robots(_url):
        return "User-agent: *\nAllow: /"

    from openfootprint.core import pipeline

    monkeypatch.setattr(pipeline, "_http_get", fake_http_get)
    monkeypatch.setattr(pipeline, "_robots_fetch", fake_robots)

    registry = SourceRegistry([GITHUB])
    inputs = LookupInputs.from_raw("alice", None, None, None)
    config = {
        "http": {"user_agent": "UA", "timeout_seconds": 1},
        "rate_limit": {"min_interval_seconds": 0},
        "output": {"runs_dir": str(tmp_path)},
    }

    result = run_lookup(inputs, registry, config)
    assert result["findings"]
