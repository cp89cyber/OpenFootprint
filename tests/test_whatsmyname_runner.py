from pathlib import Path

import requests

from openfootprint.tools.whatsmyname_runner import check_site, evaluate_match, run


def test_evaluate_match_prefers_match_code():
    site = {"m_code": 200, "e_code": 404}
    assert evaluate_match(site, status_code=200, body="") is True
    assert evaluate_match(site, status_code=404, body="") is False


def test_check_site_returns_none_on_request_error(monkeypatch):
    def boom(*_args, **_kwargs):
        raise requests.RequestException("network down")

    monkeypatch.setattr(requests, "get", boom)

    site = {"uri_check": "https://example.com/{account}"}
    assert check_site(site, "alice", 1) is None


def test_run_creates_parent_dir(tmp_path: Path):
    data_path = tmp_path / "data.json"
    data_path.write_text("{\"sites\": []}", encoding="utf-8")
    output_path = tmp_path / "nested" / "report.json"

    run(data_path, "alice", output_path, 1)

    assert output_path.exists()
