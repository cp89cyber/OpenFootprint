from __future__ import annotations

import re
import unicodedata


def _normalize_token(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c))
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "", value)
    return value


def generate_permutations(first: str, last: str, birth_year: int | None, limit: int = 100) -> list[str]:
    first_n = _normalize_token(first)
    last_n = _normalize_token(last)
    if not first_n or not last_n:
        return []

    seps = ["", ".", "_", "-"]
    first_initial = first_n[0]
    last_initial = last_n[0]
    first2 = first_n[:2] if len(first_n) >= 2 else first_n
    last2 = last_n[:2] if len(last_n) >= 2 else last_n

    base: list[str] = []
    for sep in seps:
        base.extend(
            [
                f"{first_n}{sep}{last_n}",
                f"{last_n}{sep}{first_n}",
                f"{first_initial}{sep}{last_n}",
                f"{first_n}{sep}{last_initial}",
                f"{first2}{sep}{last_n}",
                f"{first_n}{sep}{last2}",
            ]
        )
    base.extend([first_n, last_n, f"{first_n}{last_n}", f"{last_n}{first_n}"])

    years: list[str] = []
    if birth_year is not None:
        y = int(birth_year)
        years = [str(y), f"{y % 100:02d}"]

    def _with_year(s: str) -> list[str]:
        if not years:
            return [s]
        if len(s) < 4:
            return [s]
        return [s, *(f"{s}{yy}" for yy in years)]

    seen: set[str] = set()
    out: list[str] = []
    for cand in base:
        for item in _with_year(cand):
            if item in seen:
                continue
            seen.add(item)
            out.append(item)
            if len(out) >= limit:
                return out
    return out

