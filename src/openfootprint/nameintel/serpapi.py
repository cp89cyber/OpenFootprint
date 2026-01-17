from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass

import requests


def query_to_artifact_name(*, site: str, query: str) -> str:
    h = hashlib.sha256(query.encode("utf-8")).hexdigest()[:12]
    return f"serpapi_{site}_{h}.json"


@dataclass(frozen=True)
class SerpApiResult:
    query: str
    response: dict


class SerpApiClient:
    def __init__(self, *, api_key: str | None = None, sleep_seconds: float = 1.0):
        self.api_key = api_key or os.getenv("SERPAPI_API_KEY")
        self.sleep_seconds = float(sleep_seconds)

    def search(self, *, query: str, num: int = 10) -> SerpApiResult:
        if not self.api_key:
            raise RuntimeError("Missing SERPAPI_API_KEY")
        params = {
            "engine": "google",
            "q": query,
            "num": int(num),
            "api_key": self.api_key,
        }
        resp = requests.get("https://serpapi.com/search.json", params=params, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
        time.sleep(self.sleep_seconds)
        return SerpApiResult(query=query, response=payload)


def write_serpapi_artifact(*, path: str, response: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(response, f, ensure_ascii=False, indent=2, sort_keys=True)

