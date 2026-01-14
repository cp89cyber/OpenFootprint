from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FetchResult:
    url: str
    status_code: int | None
    headers: dict[str, str]
    content: bytes | None
    error: str | None
    skipped: bool = False


class Fetcher:
    def __init__(
        self,
        user_agent: str,
        timeout_seconds: int,
        robots_policy,
        rate_limiter,
        http_get,
        robots_fetcher,
    ) -> None:
        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds
        self.robots_policy = robots_policy
        self.rate_limiter = rate_limiter
        self.http_get = http_get
        self.robots_fetcher = robots_fetcher

    def get(self, url: str, source_id: str, headers: dict[str, str] | None = None) -> FetchResult:
        if not self.robots_policy.allows(url, self.user_agent, self.robots_fetcher):
            return FetchResult(url=url, status_code=None, headers={}, content=None, error=None, skipped=True)
        self.rate_limiter.wait(source_id)
        try:
            merged = {"User-Agent": self.user_agent}
            if headers:
                merged.update(headers)
            response = self.http_get(url, merged, self.timeout_seconds)
            return FetchResult(
                url=url,
                status_code=response.status_code,
                headers=dict(response.headers),
                content=response.content,
                error=None,
            )
        except Exception as exc:  # noqa: BLE001 - surface as error string
            return FetchResult(url=url, status_code=None, headers={}, content=None, error=str(exc))
