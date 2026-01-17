from __future__ import annotations

from collections.abc import Iterable


def summarize_sherlock_findings(findings: Iterable[dict]) -> list[dict]:
    out: list[dict] = []
    for f in findings:
        entity = (f or {}).get("entity") or {}
        urls = entity.get("profile_urls") or []
        url = urls[0] if urls else None
        if not url:
            continue
        out.append(
            {
                "url": url,
                "display_name": entity.get("display_name"),
            }
        )
    return out

