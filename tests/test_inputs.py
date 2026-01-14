from openfootprint.core.inputs import normalize_email, normalize_phone, normalize_username


def test_normalize_email_lowercases():
    assert normalize_email("Alice@Example.COM") == "alice@example.com"


def test_normalize_phone_e164():
    assert normalize_phone("+1 415 555 0100") == "+14155550100"


def test_normalize_username_strips():
    assert normalize_username("  Alice ") == "alice"
