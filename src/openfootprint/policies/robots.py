from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser


@dataclass
class RobotsPolicy:
    cache: dict[str, RobotFileParser] = field(default_factory=dict)

    def allows(self, url: str, user_agent: str, fetcher) -> bool:
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        if base not in self.cache:
            robots_url = f"{base}/robots.txt"
            content = fetcher(robots_url)
            parser = RobotFileParser()
            parser.parse(content.splitlines())
            self.cache[base] = parser
        return self.cache[base].can_fetch(user_agent, url)
