# External Tool Integrations Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Integrate Sherlock, Maigret, and WhatsMyName via submodules and subprocess execution, parsing their outputs into OpenFootprint findings with raw artifacts stored per run.

**Architecture:** Add tool-aware sources that execute external CLIs (or an internal WhatsMyName runner) through a shared subprocess wrapper. Tool sources bypass the HTTP fetcher, write outputs into `runs/<id>/raw/tools/<tool>/`, and parse CSV/JSON reports into the unified schema. Configuration provides submodule paths and the Python executable to use.

**Tech Stack:** Python 3.11, subprocess, csv/json parsing, requests (WhatsMyName runner), pytest.

### Task 1: Add tool submodules

**Files:**
- Create: `.gitmodules`
- Create: `third_party/sherlock`
- Create: `third_party/maigret`
- Create: `third_party/WhatsMyName`

**Step 1: No tests (repo wiring)**

**Step 2: Add submodules**

```bash
git submodule add https://github.com/sherlock-project/sherlock third_party/sherlock
git submodule add https://github.com/soxoj/maigret third_party/maigret
git submodule add https://github.com/WebBreacher/WhatsMyName third_party/WhatsMyName
```

**Step 3: Commit**

```bash
git add .gitmodules third_party/sherlock third_party/maigret third_party/WhatsMyName
git commit -m "chore: add external tool submodules"
```

### Task 2: Tool execution plumbing in core pipeline

**Files:**
- Modify: `src/openfootprint/sources/base.py`
- Modify: `src/openfootprint/core/plan.py`
- Modify: `src/openfootprint/core/pipeline.py`
- Create: `src/openfootprint/tools/__init__.py`
- Create: `src/openfootprint/tools/subprocess.py`
- Test: `tests/test_pipeline_tools.py`
- Test: `tests/test_tool_subprocess.py`

**Step 1: Write the failing tests**

```python
# tests/test_pipeline_tools.py
from pathlib import Path

from openfootprint.core.inputs import LookupInputs
from openfootprint.core.pipeline import run_lookup
from openfootprint.core.schema import Entity, Finding, Identifier
from openfootprint.sources.base import Source, RequestSpec
from openfootprint.sources.registry import SourceRegistry


def test_pipeline_executes_tool_source(tmp_path: Path, monkeypatch):
    def build(_inputs):
        return [RequestSpec(url="tool://example", input_type="username", transport="tool")]

    def parse(_result, _inputs, _raw):
        return []

    called = {"ran": False}

    def execute(_request, inputs, _run_paths, _config, _runner):
        called["ran"] = True
        entity = Entity(
            entity_id="tool:alice",
            display_name="alice",
            profile_urls=["https://example.com/alice"],
            identifiers=[Identifier(type="username", value=inputs.username)],
        )
        return [Finding(source_id="tool", type="profile", entity=entity)]

    source = Source(
        source_id="tool",
        name="Tool",
        category="tools",
        supported_inputs={"username"},
        build_requests=build,
        parse=parse,
        execute=execute,
    )

    registry = SourceRegistry([source])
    inputs = LookupInputs.from_raw("alice", None, None, None)

    def fail_get(*_args, **_kwargs):
        raise AssertionError("http fetch should not be used for tool sources")

    from openfootprint.core import pipeline

    monkeypatch.setattr(pipeline.Fetcher, "get", lambda *_args, **_kwargs: fail_get())

    config = {
        "http": {"user_agent": "UA", "timeout_seconds": 1},
        "rate_limit": {"min_interval_seconds": 0},
        "output": {"runs_dir": str(tmp_path)},
        "tools": {"python_executable": "python3", "timeout_seconds": 5},
    }

    result = run_lookup(inputs, registry, config)
    assert called["ran"] is True
    assert result["findings"]
```

```python
# tests/test_tool_subprocess.py
from pathlib import Path
import subprocess

from openfootprint.tools.subprocess import run_command


def test_run_command_captures_output(monkeypatch, tmp_path: Path):
    def fake_run(cmd, cwd, env, capture_output, text, timeout, check):
        return subprocess.CompletedProcess(cmd, 0, stdout="ok\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = run_command(["echo", "ok"], tmp_path, {"X": "1"}, 2)
    assert result.returncode == 0
    assert result.stdout == "ok\n"
```

**Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_pipeline_tools.py tests/test_tool_subprocess.py -v`
Expected: FAIL with `TypeError` for new `RequestSpec` args or missing module.

**Step 3: Write minimal implementation**

```python
# src/openfootprint/sources/base.py
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RequestSpec:
    url: str
    input_type: str
    headers: dict[str, str] = field(default_factory=dict)
    transport: str = "http"


@dataclass(frozen=True)
class Source:
    source_id: str
    name: str
    category: str
    supported_inputs: set[str]
    build_requests: callable
    parse: callable
    execute: callable | None = None
```

```python
# src/openfootprint/core/plan.py
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlannedRequest:
    source_id: str
    url: str
    input_type: str
    headers: dict[str, str]
    transport: str


def build_plan(inputs, registry) -> list[PlannedRequest]:
    present = {key for key, value in inputs.__dict__.items() if value}
    plan = []
    for source in registry.for_inputs(present):
        for request in source.build_requests(inputs):
            plan.append(
                PlannedRequest(
                    source_id=source.source_id,
                    url=request.url,
                    input_type=request.input_type,
                    headers=request.headers,
                    transport=request.transport,
                )
            )
    return plan
```

```python
# src/openfootprint/tools/subprocess.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess


@dataclass(frozen=True)
class ToolResult:
    command: list[str]
    cwd: Path
    returncode: int
    stdout: str
    stderr: str
    error: str | None


def run_command(command: list[str], cwd: Path, env: dict[str, str], timeout: int) -> ToolResult:
    try:
        result = subprocess.run(
            command,
            cwd=str(cwd),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return ToolResult(
            command=command,
            cwd=cwd,
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            error=None,
        )
    except Exception as exc:  # noqa: BLE001 - surface as error string
        return ToolResult(
            command=command,
            cwd=cwd,
            returncode=-1,
            stdout="",
            stderr="",
            error=str(exc),
        )
```

```python
# src/openfootprint/tools/__init__.py
"""External tool helpers for OpenFootprint."""
```

```python
# src/openfootprint/core/pipeline.py (adjust loop)
from openfootprint.tools.subprocess import run_command

# ... inside run_lookup
    plan = build_plan(inputs, registry)
    findings = []
    for request in plan:
        source = registry.get(request.source_id)
        if not source:
            continue
        if request.transport == "tool" and source.execute:
            findings.extend(source.execute(request, inputs, run_paths, config, run_command))
            continue
        result = fetcher.get(request.url, request.source_id, request.headers)
        raw_info = []
        if result.content:
            raw_path = save_raw_artifact(run_paths, result.url, result.content)
            raw_hash = sha256(result.content).hexdigest()
            raw_info.append((str(raw_path), raw_hash))
        findings.extend(source.parse(result, inputs, raw_info))
```

**Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/test_pipeline_tools.py tests/test_tool_subprocess.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/openfootprint/sources/base.py src/openfootprint/core/plan.py \
  src/openfootprint/core/pipeline.py src/openfootprint/tools/__init__.py \
  src/openfootprint/tools/subprocess.py tests/test_pipeline_tools.py \
  tests/test_tool_subprocess.py
git commit -m "feat: add tool execution plumbing"
```

### Task 3: Sherlock tool source and CSV parsing

**Files:**
- Create: `src/openfootprint/sources/tools/__init__.py`
- Create: `src/openfootprint/sources/tools/sherlock.py`
- Create: `tests/fixtures/sherlock.csv`
- Test: `tests/test_tool_sherlock.py`

**Step 1: Write the failing test**

```python
# tests/test_tool_sherlock.py
from pathlib import Path

from openfootprint.sources.tools.sherlock import parse_sherlock_csv


def test_parse_sherlock_csv_filters_matches():
    csv_path = Path("tests/fixtures/sherlock.csv")
    findings = parse_sherlock_csv(csv_path, username="alice", source_id="sherlock")
    assert len(findings) == 1
    assert findings[0].entity.profile_urls == ["https://example.com/alice"]
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_tool_sherlock.py -v`
Expected: FAIL with `ModuleNotFoundError` for tool source.

**Step 3: Write minimal implementation**

```python
# src/openfootprint/sources/tools/__init__.py
"""External tool-backed sources."""
```

```python
# src/openfootprint/sources/tools/sherlock.py
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
        env = {
            **{k: v for k, v in (tools_cfg.get("env") or {}).items()},
            **{},
        }
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
```

```text
# tests/fixtures/sherlock.csv
username,name,url_main,url_user,exists,http_status,response_time
alice,Example,https://example.com,https://example.com/alice,True,200,0.42
alice,Missing,https://missing.example,https://missing.example/alice,False,404,0.10
```

**Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_tool_sherlock.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/openfootprint/sources/tools/__init__.py src/openfootprint/sources/tools/sherlock.py \
  tests/fixtures/sherlock.csv tests/test_tool_sherlock.py
git commit -m "feat: add sherlock tool source"
```

### Task 4: Maigret tool source and JSON parsing

**Files:**
- Create: `src/openfootprint/sources/tools/maigret.py`
- Create: `tests/fixtures/maigret_simple.json`
- Test: `tests/test_tool_maigret.py`

**Step 1: Write the failing test**

```python
# tests/test_tool_maigret.py
from pathlib import Path

from openfootprint.sources.tools.maigret import parse_maigret_json


def test_parse_maigret_json_filters_matches():
    json_path = Path("tests/fixtures/maigret_simple.json")
    findings = parse_maigret_json(json_path, username="alice", source_id="maigret")
    assert len(findings) == 1
    assert findings[0].entity.profile_urls == ["https://github.com/alice"]
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_tool_maigret.py -v`
Expected: FAIL with `ModuleNotFoundError` for Maigret tool source.

**Step 3: Write minimal implementation**

```python
# src/openfootprint/sources/tools/maigret.py
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from openfootprint.core.schema import Evidence, Entity, Finding, Identifier
from openfootprint.sources.base import RequestSpec, Source


@dataclass(frozen=True)
class MaigretSource:
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
        base_dir = Path(tools_cfg.get("maigret_path", "third_party/maigret"))
        python_exec = tools_cfg.get("python_executable") or "python3"
        timeout = int(tools_cfg.get("timeout_seconds", 120))

        output_dir = run_paths.raw_dir / "tools" / "maigret"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"report_{username}_simple.json"

        command = [
            python_exec,
            "-m",
            "maigret",
            username,
            "--json",
            "simple",
            "--folderoutput",
            str(output_dir),
        ]
        runner(command, base_dir, {"PYTHONPATH": str(base_dir)}, timeout)
        if not output_file.exists():
            return []
        return parse_maigret_json(output_file, username, source_id=self.source_id)


def parse_maigret_json(path: Path, username: str, source_id: str) -> list[Finding]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    findings = []
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    raw_hash = sha256(path.read_bytes()).hexdigest()

    for site_name, data in payload.items():
        status = data.get("status") or {}
        url = status.get("url")
        if not url:
            continue
        evidence = Evidence(
            source_id=source_id,
            request_url=url,
            raw_path=str(path),
            raw_hash=raw_hash,
            parser_id=f"{source_id}.json",
            match_excerpt=site_name,
            fetched_at=fetched_at,
        )
        identifier = Identifier(type="username", value=username, evidence=[evidence])
        entity = Entity(
            entity_id=f"{source_id}:{username}:{site_name}",
            display_name=username,
            profile_urls=[url],
            identifiers=[identifier],
            evidence=[evidence],
        )
        findings.append(Finding(source_id=source_id, type="profile", entity=entity))
    return findings


SOURCE = Source(
    source_id="maigret",
    name="Maigret",
    category="tools",
    supported_inputs={"username"},
    build_requests=MaigretSource("maigret", "Maigret", "tools").build_requests,
    parse=MaigretSource("maigret", "Maigret", "tools").parse,
    execute=MaigretSource("maigret", "Maigret", "tools").execute,
)
```

```json
// tests/fixtures/maigret_simple.json
{
  "GitHub": {
    "status": {
      "username": "alice",
      "site_name": "GitHub",
      "url": "https://github.com/alice",
      "status": "Claimed",
      "ids": {},
      "tags": []
    },
    "site": {
      "name": "GitHub",
      "urlMain": "https://github.com"
    }
  }
}
```

**Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_tool_maigret.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/openfootprint/sources/tools/maigret.py tests/fixtures/maigret_simple.json \
  tests/test_tool_maigret.py
git commit -m "feat: add maigret tool source"
```

### Task 5: WhatsMyName runner and tool source

**Files:**
- Create: `src/openfootprint/tools/whatsmyname_runner.py`
- Create: `src/openfootprint/sources/tools/whatsmyname.py`
- Create: `tests/fixtures/whatsmyname_data.json`
- Test: `tests/test_whatsmyname_runner.py`
- Test: `tests/test_tool_whatsmyname.py`

**Step 1: Write the failing tests**

```python
# tests/test_whatsmyname_runner.py
from openfootprint.tools.whatsmyname_runner import evaluate_match


def test_evaluate_match_prefers_match_code():
    site = {"m_code": 200, "e_code": 404}
    assert evaluate_match(site, status_code=200, body="") is True
    assert evaluate_match(site, status_code=404, body="") is False
```

```python
# tests/test_tool_whatsmyname.py
from pathlib import Path

from openfootprint.sources.tools.whatsmyname import parse_whatsmyname_report


def test_parse_whatsmyname_report():
    report_path = Path("tests/fixtures/whatsmyname_report.json")
    findings = parse_whatsmyname_report(report_path, username="alice", source_id="whatsmyname")
    assert len(findings) == 1
    assert findings[0].entity.profile_urls == ["https://example.com/alice"]
```

```json
// tests/fixtures/whatsmyname_report.json
{
  "username": "alice",
  "results": [
    {
      "site_name": "Example",
      "url": "https://example.com/alice",
      "matched": true,
      "status_code": 200
    }
  ]
}
```

**Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_whatsmyname_runner.py tests/test_tool_whatsmyname.py -v`
Expected: FAIL with `ModuleNotFoundError` for new runner/source.

**Step 3: Write minimal implementation**

```python
# src/openfootprint/tools/whatsmyname_runner.py
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
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
        resp = requests.post(url, data=site["post_body"].replace("{account}", username), headers=headers, timeout=timeout)
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
```

```python
# src/openfootprint/sources/tools/whatsmyname.py
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
```

```json
// tests/fixtures/whatsmyname_data.json
{
  "sites": [
    {
      "name": "Example",
      "uri_check": "https://example.com/{account}",
      "uri_pretty": "https://example.com/{account}",
      "m_code": 200,
      "e_code": 404
    }
  ]
}
```

**Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/test_whatsmyname_runner.py tests/test_tool_whatsmyname.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/openfootprint/tools/whatsmyname_runner.py src/openfootprint/sources/tools/whatsmyname.py \
  tests/test_whatsmyname_runner.py tests/test_tool_whatsmyname.py \
  tests/fixtures/whatsmyname_report.json tests/fixtures/whatsmyname_data.json
git commit -m "feat: add whatsmyname tool source"
```

### Task 6: Wire tools into registry and defaults

**Files:**
- Modify: `src/openfootprint/cli.py`
- Modify: `src/openfootprint/core/config.py`
- Modify: `README.md`

**Step 1: Write the failing test**

```python
# tests/test_config.py (append)
from openfootprint.core.config import load_config


def test_config_includes_tools_defaults():
    config = load_config(None)
    assert "tools" in config
    assert "sherlock_path" in config["tools"]
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_config.py::test_config_includes_tools_defaults -v`
Expected: FAIL with missing keys.

**Step 3: Write minimal implementation**

```python
# src/openfootprint/core/config.py (extend DEFAULT_CONFIG)
DEFAULT_CONFIG = {
    "http": {
        "user_agent": "OpenFootprint/0.1 (+https://example.com)",
        "timeout_seconds": 15,
    },
    "rate_limit": {
        "min_interval_seconds": 1.0,
    },
    "sources": {
        "enabled": [],
        "disabled": [],
    },
    "output": {
        "runs_dir": "runs",
    },
    "tools": {
        "python_executable": "python3",
        "timeout_seconds": 120,
        "sherlock_path": "third_party/sherlock",
        "maigret_path": "third_party/maigret",
        "whatsmyname_path": "third_party/WhatsMyName",
    },
}
```

```python
# src/openfootprint/cli.py (add tool sources to registry)
from openfootprint.sources.tools.sherlock import SOURCE as SHERLOCK
from openfootprint.sources.tools.maigret import SOURCE as MAIGRET
from openfootprint.sources.tools.whatsmyname import SOURCE as WHATS_MY_NAME

# inside _registry()
        SHERLOCK,
        MAIGRET,
        WHATS_MY_NAME,
```

```markdown
# README.md (append section)
## External Tools

OpenFootprint can run the following tools via subprocess when enabled:
- Sherlock (submodule: `third_party/sherlock`)
- Maigret (submodule: `third_party/maigret`)
- WhatsMyName data (submodule: `third_party/WhatsMyName`)

Initialize submodules after cloning:

```bash
git submodule update --init --recursive
```

These tools have their own Python dependencies. Install them in your environment as needed, for example:

```bash
pip install -e third_party/sherlock
pip install -e third_party/maigret
```
```

**Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_config.py::test_config_includes_tools_defaults -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/openfootprint/core/config.py src/openfootprint/cli.py README.md tests/test_config.py
git commit -m "feat: add tool defaults and registry wiring"
```
