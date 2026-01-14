from openfootprint.reporting.markdown_report import render_markdown
from openfootprint.core.schema import Entity, Finding, Identifier


def test_markdown_includes_sources():
    entity = Entity(entity_id="a", display_name="Alice", profile_urls=["https://x"], identifiers=[Identifier("username", "alice")])
    findings = [Finding(source_id="github", type="profile", entity=entity)]
    report = render_markdown(findings, ["github"], "run-1")
    assert "github" in report
