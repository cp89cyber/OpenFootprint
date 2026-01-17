from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from openfootprint.core.schema import Evidence, Entity, Finding, Identifier
from openfootprint.sources.base import RequestSpec, Source


@dataclass(frozen=True)
class WhatsMyNameSource:
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
        base_dir = Path(tools_cfg.get("whatsmyname_path", "third_party/WhatsMyName"))
        python_exec = tools_cfg.get("python_executable") or "python3"
        timeout = int(tools_cfg.get("timeout_seconds", 120))

        output_dir = run_paths.raw_dir / "tools" / "whatsmyname"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"report_{username}.json"
        data_path = base_dir / "wmn-data.json"

        command = [
            python_exec,
            "-m",
            "openfootprint.tools.whatsmyname_runner",
            "--data",
            str(data_path),
            "--username",
            username,
            "--output",
            str(output_file),
            "--timeout",
            str(config.get("http", {}).get("timeout_seconds", 15)),
        ]
        runner(command, Path.cwd(), {"PYTHONPATH": str(Path.cwd())}, timeout)
        if not output_file.exists():
            return []
        return parse_whatsmyname_report(output_file, username, source_id=self.source_id)


def parse_whatsmyname_report(path: Path, username: str, source_id: str) -> list[Finding]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    findings = []
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    raw_hash = sha256(path.read_bytes()).hexdigest()

    for item in payload.get("results", []):
        if not item.get("matched"):
            continue
        url = item.get("url")
        if not url:
            continue
        evidence = Evidence(
            source_id=source_id,
            request_url=url,
            raw_path=str(path),
            raw_hash=raw_hash,
            parser_id=f"{source_id}.json",
            match_excerpt=item.get("site_name"),
            fetched_at=fetched_at,
        )
        identifier = Identifier(type="username", value=username, evidence=[evidence])
        entity = Entity(
            entity_id=f"{source_id}:{username}:{item.get('site_name') or url}",
            display_name=username,
            profile_urls=[url],
            identifiers=[identifier],
            evidence=[evidence],
        )
        findings.append(Finding(source_id=source_id, type="profile", entity=entity))
    return findings


SOURCE = Source(
    source_id="whatsmyname",
    name="WhatsMyName",
    category="tools",
    supported_inputs={"username"},
    build_requests=WhatsMyNameSource("whatsmyname", "WhatsMyName", "tools").build_requests,
    parse=WhatsMyNameSource("whatsmyname", "WhatsMyName", "tools").parse,
    execute=WhatsMyNameSource("whatsmyname", "WhatsMyName", "tools").execute,
)
