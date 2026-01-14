from pathlib import Path

from openfootprint.core.inputs import LookupInputs
from openfootprint.core.pipeline import run_lookup
from openfootprint.sources.base import Source, RequestSpec
from openfootprint.sources.registry import SourceRegistry


def test_pipeline_runs_with_fake_source(tmp_path: Path, monkeypatch):
    def build(_inputs):
        return [RequestSpec(url="https://example.com", input_type="username")]

    def parse(_result, _inputs, _raw):
        return []

    source = Source(
        source_id="example",
        name="Example",
        category="developer",
        supported_inputs={"username"},
        build_requests=build,
        parse=parse,
    )

    registry = SourceRegistry([source])
    inputs = LookupInputs.from_raw("alice", None, None, None)

    class FakeResponse:
        status_code = 200
        content = b""
        url = "https://example.com"
        headers = {}

    def fake_http_get(_url, _headers, _timeout):
        return FakeResponse()

    def fake_robots(_url):
        return "User-agent: *\nAllow: /"

    from openfootprint.core import pipeline

    monkeypatch.setattr(pipeline, "_http_get", fake_http_get)
    monkeypatch.setattr(pipeline, "_robots_fetch", fake_robots)

    config = {
        "http": {"user_agent": "UA", "timeout_seconds": 1},
        "rate_limit": {"min_interval_seconds": 0},
        "output": {"runs_dir": str(tmp_path)},
    }
    results = run_lookup(inputs, registry, config)
    assert Path(results["paths"]["manifest"]).exists()
