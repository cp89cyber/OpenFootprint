from openfootprint.nameintel.crosslinked import is_crosslinked_available


def test_is_crosslinked_available_false_when_missing(monkeypatch):
    monkeypatch.setenv("PATH", "")
    assert is_crosslinked_available() is False

