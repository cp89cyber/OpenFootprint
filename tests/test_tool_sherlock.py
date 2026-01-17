from pathlib import Path

from openfootprint.sources.tools.sherlock import parse_sherlock_csv


def test_parse_sherlock_csv_filters_matches():
    csv_path = Path("tests/fixtures/sherlock.csv")
    findings = parse_sherlock_csv(csv_path, username="alice", source_id="sherlock")
    assert len(findings) == 1
    assert findings[0].entity.profile_urls == ["https://example.com/alice"]
