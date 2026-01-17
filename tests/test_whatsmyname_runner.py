from openfootprint.tools.whatsmyname_runner import evaluate_match


def test_evaluate_match_prefers_match_code():
    site = {"m_code": 200, "e_code": 404}
    assert evaluate_match(site, status_code=200, body="") is True
    assert evaluate_match(site, status_code=404, body="") is False
