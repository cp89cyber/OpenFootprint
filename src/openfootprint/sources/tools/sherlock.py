from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from openfootprint.core.schema import Evidence, Entity, Finding, Identifier
from openfootprint.sources.base import RequestSpec, Source


@dataclass(frozen=True)
class SherlockSource:
    source_id: str
    name: str
    category: str

    def build_requests(self, inputs) -> list[RequestSpec]:
        if not inputs.username:
            return []
        url = f"tool://{self.source_id}/{inputs.username}"
        return [RequestSpec(url=url, input_type="username", transport="tool")]

    def parse(self, _result, _inputs, _raw):
        return []

    def execute(self, _request, inputs, run_paths, config, runner):
        username = inputs.username
        if not username:
            return []
        tools_cfg = config.get("tools", {})
        base_dir = Path(tools_cfg.get("sherlock_path", "third_party/sherlock"))
        python_exec = tools_cfg.get("python_executable") or "python3"
        timeout = int(tools_cfg.get("timeout_seconds", 120))

        output_dir = run_paths.raw_dir / "tools" / "sherlock"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{username}.csv"

        command = [
            python_exec,
            "-m",
            "sherlock_project",
            "--csv",
            "--folderoutput",
            str(output_dir),
            "--no-color",
            "--local",
            "--timeout",
            str(timeout),
            username,
        ]
        env = tools_cfg.get("env") or {}
        runner(command, base_dir, {**env, **{"PYTHONPATH": str(base_dir)}}, timeout)
        if not output_file.exists():
            return []
        return parse_sherlock_csv(output_file, username, source_id=self.source_id)


def parse_sherlock_csv(path: Path, username: str, source_id: str) -> list[Finding]:
    rows = list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))
    findings = []
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    raw_hash = sha256(path.read_bytes()).hexdigest()

    for row in rows:
        exists = str(row.get("exists", "")).strip().lower() in {"true", "1", "yes"}
        if not exists:
            continue
        url = row.get("url_user") or row.get("url")
        if not url:
            continue
        evidence = Evidence(
            source_id=source_id,
            request_url=url,
            raw_path=str(path),
            raw_hash=raw_hash,
            parser_id=f"{source_id}.csv",
            match_excerpt=row.get("name"),
            fetched_at=fetched_at,
        )
        identifier = Identifier(type="username", value=username, evidence=[evidence])
        entity = Entity(
            entity_id=f"{source_id}:{username}:{row.get('name') or url}",
            display_name=username,
            profile_urls=[url],
            identifiers=[identifier],
            evidence=[evidence],
        )
        findings.append(Finding(source_id=source_id, type="profile", entity=entity))
    return findings


SOURCE = Source(
    source_id="sherlock",
    name="Sherlock",
    category="tools",
    supported_inputs={"username"},
    build_requests=SherlockSource("sherlock", "Sherlock", "tools").build_requests,
    parse=SherlockSource("sherlock", "Sherlock", "tools").parse,
    execute=SherlockSource("sherlock", "Sherlock", "tools").execute,
)
