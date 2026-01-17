from pathlib import Path

from openfootprint.sources.tools.maigret import parse_maigret_json


def test_parse_maigret_json_filters_matches():
    json_path = Path("tests/fixtures/maigret_simple.json")
    findings = parse_maigret_json(json_path, username="alice", source_id="maigret")
    assert len(findings) == 1
    assert findings[0].entity.profile_urls == ["https://github.com/alice"]
