from __future__ import annotations

from dataclasses import dataclass, field
import time


@dataclass
class RateLimiter:
    min_interval: float
    now: callable = time.monotonic
    sleeper: callable = time.sleep
    last_seen: dict[str, float] = field(default_factory=dict)

    def wait(self, key: str) -> None:
        last = self.last_seen.get(key)
        current = self.now()
        if last is not None:
            elapsed = current - last
            if elapsed < self.min_interval:
                sleep_for = self.min_interval - elapsed
                self.sleeper(sleep_for)
                current = current + sleep_for
        self.last_seen[key] = current
