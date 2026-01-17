from pathlib import Path

from openfootprint.sources.tools.whatsmyname import parse_whatsmyname_report


def test_parse_whatsmyname_report():
    report_path = Path(__file__).resolve().parent / "fixtures" / "whatsmyname_report.json"
    findings = parse_whatsmyname_report(report_path, username="alice", source_id="whatsmyname")
    assert len(findings) == 1
    assert findings[0].entity.profile_urls == ["https://example.com/alice"]
