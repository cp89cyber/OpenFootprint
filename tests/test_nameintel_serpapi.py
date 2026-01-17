from openfootprint.nameintel.serpapi import query_to_artifact_name


def test_query_to_artifact_name_is_stable_and_scoped():
    name = query_to_artifact_name(site="instagram", query='site:instagram.com "john doe"')
    assert name.startswith("serpapi_instagram_")
    assert name.endswith(".json")

