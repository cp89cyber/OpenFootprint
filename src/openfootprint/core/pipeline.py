from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

import requests

from openfootprint.core.correlate import correlate_findings
from openfootprint.core.fetcher import Fetcher
from openfootprint.core.plan import build_plan
from openfootprint.core.schema import RunManifest
from openfootprint.policies.robots import RobotsPolicy
from openfootprint.policies.rate_limit import RateLimiter
from openfootprint.reporting.console import render_console
from openfootprint.reporting.json_report import render_json
from openfootprint.reporting.markdown_report import render_markdown
from openfootprint.storage.runs import create_run_dir, save_raw_artifact, write_text, write_manifest


def _http_get(url, headers, timeout):
    response = requests.get(url, headers=headers, timeout=timeout)
    return response


def _robots_fetch(url):
    return requests.get(url, timeout=10).text


def run_lookup(inputs, registry, config):
    runs_dir = Path(config["output"]["runs_dir"]).resolve()
    run_paths = create_run_dir(runs_dir)

    policy = RobotsPolicy()
    limiter = RateLimiter(min_interval=config["rate_limit"]["min_interval_seconds"])
    fetcher = Fetcher(
        config["http"]["user_agent"],
        config["http"]["timeout_seconds"],
        policy,
        limiter,
        _http_get,
        _robots_fetch,
    )

    plan = build_plan(inputs, registry)
    findings = []
    for request in plan:
        source = registry.get(request.source_id)
        if not source:
            continue
        result = fetcher.get(request.url, request.source_id, request.headers)
        raw_info = []
        if result.content:
            raw_path = save_raw_artifact(run_paths, result.url, result.content)
            raw_hash = sha256(result.content).hexdigest()
            raw_info.append((str(raw_path), raw_hash))
        findings.extend(source.parse(result, inputs, raw_info))

    entities = correlate_findings(findings)
    run_id = run_paths.run_dir.name
    started_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest = RunManifest(
        run_id=run_id,
        inputs=inputs.__dict__,
        sources=[req.source_id for req in plan],
        started_at=started_at,
        finished_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        config=config,
    )

    console = render_console(findings, manifest.sources, run_id)
    report_json = render_json(findings, manifest.sources, run_id)
    report_md = render_markdown(findings, manifest.sources, run_id)

    manifest_path = write_manifest(run_paths, manifest)
    report_json_path = write_text(run_paths.run_dir, "report.json", report_json)
    report_md_path = write_text(run_paths.run_dir, "report.md", report_md)

    return {
        "run_id": run_id,
        "findings": findings,
        "entities": entities,
        "console": console,
        "paths": {
            "manifest": str(manifest_path),
            "report_json": str(report_json_path),
            "report_markdown": str(report_md_path),
        },
    }
