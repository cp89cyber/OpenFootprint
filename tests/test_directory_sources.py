from pathlib import Path

from openfootprint.core.inputs import LookupInputs
from openfootprint.sources.directories.wikidata import SOURCE as WIKIDATA


def _fake_json_result(text: str):
    return type("R", (), {"status_code": 200, "content": text.encode("utf-8"), "url": "https://example.com"})


def test_wikidata_parses_entities():
    data = Path("tests/fixtures/wikidata.json").read_text(encoding="utf-8")
    result = _fake_json_result(data)
    findings = WIKIDATA.parse(result, LookupInputs.from_raw(None, None, None, "Alice"), [])
    assert findings and findings[0].source_id == "wikidata"
