from pathlib import Path

from openfootprint.core.inputs import LookupInputs
from openfootprint.core.pipeline import run_lookup
from openfootprint.core.schema import Entity, Finding, Identifier
from openfootprint.sources.base import Source, RequestSpec
from openfootprint.sources.registry import SourceRegistry


def test_pipeline_executes_tool_source(tmp_path: Path, monkeypatch):
    def build(_inputs):
        return [RequestSpec(url="tool://example", input_type="username", transport="tool")]

    def parse(_result, _inputs, _raw):
        return []

    called = {"ran": False}

    def execute(_request, inputs, _run_paths, _config, _runner):
        called["ran"] = True
        entity = Entity(
            entity_id="tool:alice",
            display_name="alice",
            profile_urls=["https://example.com/alice"],
            identifiers=[Identifier(type="username", value=inputs.username)],
        )
        return [Finding(source_id="tool", type="profile", entity=entity)]

    source = Source(
        source_id="tool",
        name="Tool",
        category="tools",
        supported_inputs={"username"},
        build_requests=build,
        parse=parse,
        execute=execute,
    )

    registry = SourceRegistry([source])
    inputs = LookupInputs.from_raw("alice", None, None, None)

    def fail_get(*_args, **_kwargs):
        raise AssertionError("http fetch should not be used for tool sources")

    from openfootprint.core import pipeline

    monkeypatch.setattr(pipeline.Fetcher, "get", lambda *_args, **_kwargs: fail_get())

    config = {
        "http": {"user_agent": "UA", "timeout_seconds": 1},
        "rate_limit": {"min_interval_seconds": 0},
        "output": {"runs_dir": str(tmp_path)},
        "tools": {"python_executable": "python3", "timeout_seconds": 5},
    }

    result = run_lookup(inputs, registry, config)
    assert called["ran"] is True
    assert result["findings"]
