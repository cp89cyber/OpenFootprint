from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from openfootprint.core.config import load_config
from openfootprint.core.inputs import LookupInputs
from openfootprint.core.schema import RunManifest
from openfootprint.nameintel.crosslinked import is_crosslinked_available
from openfootprint.nameintel.dorks import build_dork_queries
from openfootprint.nameintel.permutations import generate_permutations
from openfootprint.nameintel.serpapi import SerpApiClient, query_to_artifact_name, write_serpapi_artifact
from openfootprint.storage.runs import create_run_dir, write_manifest, write_text
from openfootprint.tools.subprocess import run_command


def run_nameintel(
    *,
    first: str,
    last: str,
    birth_year: int | None,
    sherlock: bool,
    dorks: bool,
    dorks_sites: list[str],
    dorks_limit: int,
    keywords: str,
    crosslinked: bool,
    dry_run: bool,
    config_path: str | None,
    output: str | None,
) -> int:
    config = load_config(config_path)
    if output:
        config["output"]["runs_dir"] = output

    runs_dir = Path(config["output"]["runs_dir"]).resolve()
    run_paths = create_run_dir(runs_dir)
    run_id = run_paths.run_dir.name
    started_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    full_name = f"{first} {last}".strip()
    perms = generate_permutations(first=first, last=last, birth_year=birth_year, limit=100)
    top_perms = perms[:5]

    kws = [k.strip() for k in keywords.split(",")] if keywords else []
    kws = [k for k in kws if k]

    dork_queries: list[str] = []
    if dorks:
        dork_queries = build_dork_queries(
            full_name=full_name,
            sites=dorks_sites,
            keywords=kws,
            top_permutations=top_perms,
        )

    estimated_cost = len(dork_queries) if dorks else 0
    if dorks:
        print(f"[i] Estimated cost: {estimated_cost} SerpAPI credits")

    warnings: list[str] = []
    if crosslinked and not is_crosslinked_available():
        warnings.append("crosslinked not found on PATH; skipping")

    serpapi_results: list[dict] = []
    if dorks and not dry_run:
        if not os.getenv("SERPAPI_API_KEY"):
            raise RuntimeError("SERPAPI_API_KEY is required for --dorks (or use --dry-run)")
        client = SerpApiClient()
        for site_key in dorks_sites:
            for query in [q for q in dork_queries if f"site:{site_key}" in q or site_key in q]:
                _ = site_key
                _ = query
        for query in dork_queries:
            result = client.search(query=query, num=dorks_limit)
            name = query_to_artifact_name(site="dorks", query=query)
            artifact_path = run_paths.raw_dir / name
            write_serpapi_artifact(path=str(artifact_path), response=result.response)
            serpapi_results.append(
                {
                    "query": query,
                    "artifact": str(artifact_path),
                    "top": [
                        {
                            "title": (o.get("title") if isinstance(o, dict) else None),
                            "link": (o.get("link") if isinstance(o, dict) else None),
                            "snippet": (o.get("snippet") if isinstance(o, dict) else None),
                        }
                        for o in (result.response.get("organic_results") or [])[: max(1, int(dorks_limit))]
                    ],
                }
            )

    # Sherlock execution is best-effort (requires submodule deps).
    sherlock_hits: dict[str, list[str]] = {}
    if sherlock and not dry_run:
        try:
            from openfootprint.sources.tools.sherlock import SOURCE as SHERLOCK_SOURCE
            from openfootprint.sources.base import RequestSpec

            for username in perms:
                inputs = LookupInputs.from_raw(username, None, None, None)
                reqs = SHERLOCK_SOURCE.build_requests(inputs)
                if not reqs or not SHERLOCK_SOURCE.execute:
                    continue
                findings = SHERLOCK_SOURCE.execute(reqs[0], inputs, run_paths, config, run_command)
                urls: list[str] = []
                for f in findings:
                    try:
                        urls.extend(f.entity.profile_urls)
                    except Exception:
                        continue
                if urls:
                    sherlock_hits[username] = sorted(set(urls))
        except Exception as e:
            warnings.append(f"sherlock failed: {e}")

    payload = {
        "run_id": run_id,
        "nameintel": {
            "inputs": {"first": first, "last": last, "birth_year": birth_year},
            "permutations": perms,
            "top_permutations": top_perms,
            "keywords": kws,
            "dorks": {
                "enabled": bool(dorks),
                "sites": dorks_sites,
                "queries": dork_queries,
                "estimated_cost": estimated_cost,
                "results": serpapi_results,
            },
            "sherlock": {"enabled": bool(sherlock), "hits": sherlock_hits},
            "crosslinked": {"enabled": bool(crosslinked), "available": is_crosslinked_available()},
            "warnings": warnings,
            "dry_run": bool(dry_run),
        },
    }

    manifest = RunManifest(
        run_id=run_id,
        inputs={"name": full_name, "username": None, "email": None, "phone": None},
        sources=[s for s in ["nameintel"] if s],
        started_at=started_at,
        finished_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        config=config,
    )

    write_manifest(run_paths, manifest)
    write_text(run_paths.run_dir, "report.json", json.dumps(payload, indent=2, sort_keys=True))
    md_lines = [
        f"# NameIntel Report ({run_id})",
        "",
        f"- Name: {full_name}",
        f"- Birth year: {birth_year or ''}",
        f"- Permutations: {len(perms)}",
        f"- Dorks: {'enabled' if dorks else 'disabled'} (queries: {len(dork_queries)})",
        f"- Sherlock: {'enabled' if sherlock else 'disabled'} (hits: {len(sherlock_hits)})",
    ]
    if warnings:
        md_lines.extend(["", "## Warnings", *[f"- {w}" for w in warnings]])
    write_text(run_paths.run_dir, "report.md", "\n".join(md_lines) + "\n")

    print(f"Permutations ({len(perms)}):")
    for p in perms:
        print(f"- {p}")
    if dorks:
        print("Dorks:")
        for q in dork_queries:
            print(f"- {q}")
    print(f"[i] Run: {run_paths.run_dir}")
    return 0
