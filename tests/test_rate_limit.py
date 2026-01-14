from openfootprint.policies.rate_limit import RateLimiter


def test_rate_limit_sleeps():
    slept = []

    def fake_sleep(seconds):
        slept.append(seconds)

    times = [0.0, 0.1]

    def fake_now():
        return times.pop(0)

    limiter = RateLimiter(min_interval=1.0, now=fake_now, sleeper=fake_sleep)
    limiter.wait("github")
    limiter.wait("github")

    assert slept and slept[0] >= 0.9
