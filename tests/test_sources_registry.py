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


def test_registry_filters_by_config():
    def build(_inputs):
        return []

    def parse(_result, _inputs, _raw):
        return []

    alpha = Source(
        source_id="alpha",
        name="Alpha",
        category="developer",
        supported_inputs={"username"},
        build_requests=build,
        parse=parse,
    )
    beta = Source(
        source_id="beta",
        name="Beta",
        category="social",
        supported_inputs={"username"},
        build_requests=build,
        parse=parse,
    )

    registry = SourceRegistry([alpha, beta])
    enabled_only = registry.filtered(enabled=["alpha"], disabled=[])
    assert [source.source_id for source in enabled_only.sources] == ["alpha"]

    disabled_only = registry.filtered(enabled=[], disabled=["beta"])
    assert [source.source_id for source in disabled_only.sources] == ["alpha"]
