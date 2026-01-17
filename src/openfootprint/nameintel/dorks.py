from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DorkSite:
    key: str
    domain: str
    name_query_prefix: str


SITES: dict[str, DorkSite] = {
    "linkedin": DorkSite(key="linkedin", domain="linkedin.com", name_query_prefix="site:linkedin.com/in"),
    "instagram": DorkSite(key="instagram", domain="instagram.com", name_query_prefix="site:instagram.com"),
}


def _or_group(terms: list[str]) -> str:
    cleaned = [t.strip() for t in terms if t and t.strip()]
    if not cleaned:
        return ""
    inner = " OR ".join(f'"{t}"' for t in cleaned)
    return f"({inner})"


def build_dork_queries(
    *,
    full_name: str,
    sites: list[str],
    keywords: list[str] | None = None,
    top_permutations: list[str] | None = None,
) -> list[str]:
    keywords = keywords or []
    top_permutations = top_permutations or []

    out: list[str] = []
    for site_key in sites:
        site = SITES.get(site_key)
        if not site:
            continue

        base = f'{site.name_query_prefix} "{full_name}"'
        out.append(base)

        if keywords:
            out.append(f"{base} {_or_group(keywords)}")

        if top_permutations:
            out.append(f"site:{site.domain} {_or_group(top_permutations)}")

            if site_key == "instagram":
                out.append(f"site:{site.domain} inurl:{top_permutations[0]}")

    deduped: list[str] = []
    seen: set[str] = set()
    for q in out:
        if q in seen:
            continue
        seen.add(q)
        deduped.append(q)
    return deduped

