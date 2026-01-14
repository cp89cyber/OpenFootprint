from openfootprint.sources.parsers import extract_title, extract_text


def test_extract_title_and_text():
    html = "<html><head><title>Alice</title></head><body>Hello</body></html>"
    assert extract_title(html) == "Alice"
    assert "Hello" in extract_text(html)
