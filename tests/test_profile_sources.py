from pathlib import Path

from openfootprint.core.inputs import LookupInputs
from openfootprint.sources.developer.github import SOURCE as GITHUB
from openfootprint.sources.social.reddit import SOURCE as REDDIT


def _fake_fetch_result(html: str):
    return type("R", (), {"status_code": 200, "content": html.encode("utf-8"), "url": "https://example.com"})


def test_github_profile_parses_title():
    html = Path("tests/fixtures/github.html").read_text(encoding="utf-8")
    result = _fake_fetch_result(html)
    findings = GITHUB.parse(result, LookupInputs.from_raw("alice", None, None, None), [])
    assert findings and findings[0].entity.identifiers[0].value == "alice"


def test_reddit_profile_parses_title():
    html = Path("tests/fixtures/reddit.html").read_text(encoding="utf-8")
    result = _fake_fetch_result(html)
    findings = REDDIT.parse(result, LookupInputs.from_raw("alice", None, None, None), [])
    assert findings and findings[0].source_id == "reddit"
