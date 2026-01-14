from openfootprint.core.inputs import LookupInputs
from openfootprint.core.plan import build_plan
from openfootprint.sources.base import Source, RequestSpec
from openfootprint.sources.registry import SourceRegistry


def test_build_plan_includes_username_sources():
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
    plan = build_plan(LookupInputs.from_raw("alice", None, None, None), registry)
    assert plan and plan[0].source_id == "example"
