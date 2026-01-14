from openfootprint.policies.robots import RobotsPolicy


def test_robots_disallow():
    policy = RobotsPolicy()

    def fetcher(_url):
        return "User-agent: *\nDisallow: /"

    assert policy.allows("https://example.com/private", "OpenFootprint", fetcher) is False
