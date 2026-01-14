from openfootprint.core.fetcher import Fetcher
from openfootprint.policies.robots import RobotsPolicy
from openfootprint.policies.rate_limit import RateLimiter


def test_fetcher_respects_robots():
    policy = RobotsPolicy()

    def robots_fetcher(_url):
        return "User-agent: *\nDisallow: /"

    def http_get(_url, _headers, _timeout):
        raise AssertionError("should not fetch")

    limiter = RateLimiter(min_interval=0.0, now=lambda: 0.0, sleeper=lambda _s: None)
    fetcher = Fetcher("UA", 10, policy, limiter, http_get, robots_fetcher)

    result = fetcher.get("https://example.com", "example")
    assert result.skipped is True
