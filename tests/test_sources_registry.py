from openfootprint.sources.base import Source, RequestSpec
from openfootprint.sources.registry import SourceRegistry


def test_registry_filters_by_input():
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
    matched = registry.for_inputs({"username"})
    assert matched and matched[0].source_id == "example"
