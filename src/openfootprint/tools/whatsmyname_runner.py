from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests


def evaluate_match(site: dict, status_code: int, body: str) -> bool | None:
    if site.get("m_code") is not None and status_code == site.get("m_code"):
        return True
    if site.get("m_string") and site["m_string"] in body:
        return True
    if site.get("e_code") is not None and status_code == site.get("e_code"):
        return False
    if site.get("e_string") and site["e_string"] in body:
        return False
    return None


def check_site(site: dict, username: str, timeout: int) -> dict | None:
    url = site["uri_check"].replace("{account}", username)
    headers = site.get("headers") or {}
    if site.get("post_body"):
        resp = requests.post(
            url,
            data=site["post_body"].replace("{account}", username),
            headers=headers,
            timeout=timeout,
        )
    else:
        resp = requests.get(url, headers=headers, timeout=timeout)
    match = evaluate_match(site, resp.status_code, resp.text)
    if match is not True:
        return None
    return {
        "site_name": site.get("name") or url,
        "url": site.get("uri_pretty", url).replace("{account}", username),
        "matched": True,
        "status_code": resp.status_code,
    }


def run(data_path: Path, username: str, output_path: Path, timeout: int) -> None:
    payload = json.loads(data_path.read_text(encoding="utf-8"))
    results = []
    for site in payload.get("sites", []):
        if not site.get("uri_check"):
            continue
        item = check_site(site, username, timeout)
        if item:
            results.append(item)
    output = {"username": username, "results": results}
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout", type=int, default=15)
    args = parser.parse_args(argv)

    run(Path(args.data), args.username, Path(args.output), args.timeout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
