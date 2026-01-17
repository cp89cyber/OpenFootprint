from openfootprint.nameintel.dorks import build_dork_queries


def test_build_dork_queries_uses_keywords_and_handle_or():
    queries = build_dork_queries(
        full_name="John Doe",
        sites=["linkedin", "instagram"],
        keywords=["software", "engineer", "berlin"],
        top_permutations=["johndoe1990", "j.doe"],
    )
    assert any('site:linkedin.com/in "John Doe"' in q for q in queries)
    assert any('("software" OR "engineer" OR "berlin")' in q for q in queries)
    assert any('("johndoe1990" OR "j.doe")' in q for q in queries)

