from openfootprint.nameintel.permutations import generate_permutations


def test_generate_permutations_includes_common_forms_and_year():
    perms = generate_permutations(first="John", last="Doe", birth_year=1990, limit=200)
    assert "j.doe" in perms
    assert "doejohn1990" in perms
    assert "johndoe90" in perms

