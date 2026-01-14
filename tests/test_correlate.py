from openfootprint.core.correlate import correlate_findings
from openfootprint.core.schema import Entity, Finding, Identifier


def test_correlate_merges_by_identifier():
    ent1 = Entity(entity_id="a", display_name=None, profile_urls=[], identifiers=[Identifier("email", "a@b.com")])
    ent2 = Entity(entity_id="b", display_name=None, profile_urls=[], identifiers=[Identifier("email", "a@b.com")])
    findings = [
        Finding(source_id="s1", type="profile", entity=ent1),
        Finding(source_id="s2", type="profile", entity=ent2),
    ]
    merged = correlate_findings(findings)
    assert len(merged) == 1
