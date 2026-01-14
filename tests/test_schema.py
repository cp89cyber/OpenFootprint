from openfootprint.core.schema import Evidence, Identifier


def test_evidence_to_dict():
    ev = Evidence(
        source_id="github",
        request_url="https://example.com",
        raw_path="raw/abc.html",
        raw_hash="deadbeef",
        parser_id="github.profile",
        match_excerpt="alice",
        fetched_at="2026-01-14T00:00:00Z",
    )
    assert ev.to_dict()["source_id"] == "github"


def test_identifier_to_dict():
    ident = Identifier(type="username", value="alice", evidence=[])
    assert ident.to_dict()["type"] == "username"
