# OpenFootprint MVP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python CLI that performs public-source lookups for username/email/phone/name and outputs console summary, JSON, and Markdown with reproducible artifacts.

**Architecture:** Minimal plugin-based source connectors with a shared schema, policy checks (robots, rate limit), and a storage layer for raw artifacts and run manifests.

**Tech Stack:** Python 3.11, requests, beautifulsoup4, phonenumbers, pytest.

**Notes:**
- Skills: @superpowers:test-driven-development, @superpowers:verification-before-completion
- Use `.venv/bin/python` and `.venv/bin/pytest` for commands.

### Task 1: Test scaffolding and version constant

**Files:**
- Create: `pyproject.toml`
- Create: `src/openfootprint/__init__.py`
- Create: `src/openfootprint/core/__init__.py`
- Create: `src/openfootprint/policies/__init__.py`
- Create: `src/openfootprint/storage/__init__.py`
- Create: `src/openfootprint/sources/__init__.py`
- Create: `src/openfootprint/reporting/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/test_version.py`

**Step 1: Write the failing test**

```python
# tests/test_version.py
from openfootprint import __version__


def test_version_present():
    assert __version__
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_version.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'openfootprint'`

**Step 3: Write minimal implementation**

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "openfootprint"
version = "0.1.0"
description = "Open-source, terminal OSINT tool for public-person research"
readme = "README.md"
requires-python = ">=3.11"
license = { text = "AGPL-3.0-or-later" }
dependencies = [
  "requests>=2.31.0",
  "beautifulsoup4>=4.12.0",
  "phonenumbers>=8.13.0",
]

[project.scripts]
openfootprint = "openfootprint.cli:main"

[tool.setuptools]
package-dir = { "" = "src" }

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

```python
# src/openfootprint/__init__.py
__version__ = "0.1.0"
```

```python
# src/openfootprint/core/__init__.py
\"\"\"Core modules for OpenFootprint.\"\"\"
```

```python
# src/openfootprint/policies/__init__.py
\"\"\"Policy modules (robots, rate limiting).\"\"\"
```

```python
# src/openfootprint/storage/__init__.py
\"\"\"Storage helpers for run artifacts.\"\"\"
```

```python
# src/openfootprint/sources/__init__.py
\"\"\"Source connector registry and helpers.\"\"\"
```

```python
# src/openfootprint/reporting/__init__.py
\"\"\"Report rendering helpers.\"\"\"
```

```python
# tests/conftest.py
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
```

**Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_version.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add pyproject.toml src/openfootprint/__init__.py src/openfootprint/core/__init__.py \\
  src/openfootprint/policies/__init__.py src/openfootprint/storage/__init__.py \\
  src/openfootprint/sources/__init__.py src/openfootprint/reporting/__init__.py \\
  tests/conftest.py tests/test_version.py
git commit -m "chore: add python package scaffold"
```

### Task 2: CLI entrypoint skeleton

**Files:**
- Create: `src/openfootprint/cli.py`
- Create: `src/openfootprint/__main__.py`
- Create: `tests/test_cli_help.py`

**Step 1: Write the failing test**

```python
# tests/test_cli_help.py
import os
import subprocess
import sys
from pathlib import Path


def test_cli_help_includes_commands():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    result = subprocess.run(
        [sys.executable, "-m", "openfootprint", "--help"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0
    assert "lookup" in result.stdout
    assert "sources" in result.stdout
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_cli_help.py -v`
Expected: FAIL with `No module named openfootprint.__main__` or missing help output

**Step 3: Write minimal implementation**

```python
# src/openfootprint/cli.py
import argparse

from . import __version__


def _cmd_stub(_args):
    print("Not implemented yet")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="openfootprint", description="Public-source OSINT lookup tool")
    parser.add_argument("--version", action="version", version=__version__)

    subparsers = parser.add_subparsers(dest="command")

    lookup = subparsers.add_parser("lookup", help="Run a public-source lookup")
    lookup.set_defaults(func=_cmd_stub)

    sources = subparsers.add_parser("sources", help="List or inspect sources")
    sources_sub = sources.add_subparsers(dest="sources_command")
    sources_list = sources_sub.add_parser("list", help="List available sources")
    sources_list.set_defaults(func=_cmd_stub)
    sources_info = sources_sub.add_parser("info", help="Show details for a source")
    sources_info.add_argument("source_id")
    sources_info.set_defaults(func=_cmd_stub)

    plan = subparsers.add_parser("plan", help="Show a dry-run query plan")
    plan.set_defaults(func=_cmd_stub)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    return int(args.func(args))
```

```python
# src/openfootprint/__main__.py
from .cli import main


if __name__ == "__main__":
    raise SystemExit(main())
```

**Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_cli_help.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/openfootprint/cli.py src/openfootprint/__main__.py tests/test_cli_help.py
git commit -m "feat: add cli entrypoint skeleton"
```

### Task 3: Configuration loading

**Files:**
- Create: `src/openfootprint/core/config.py`
- Create: `tests/test_config.py`

**Step 1: Write the failing test**

```python
# tests/test_config.py
from pathlib import Path

from openfootprint.core.config import load_config


def test_load_config_merges_defaults(tmp_path: Path):
    config_path = tmp_path / "openfootprint.toml"
    config_path.write_text("[sources]\nenabled = ['github']\n", encoding="utf-8")

    config = load_config(config_path)

    assert "github" in config["sources"]["enabled"]
    assert config["http"]["timeout_seconds"] == 15
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'openfootprint.core'`

**Step 3: Write minimal implementation**

```python
# src/openfootprint/core/config.py
from __future__ import annotations

from pathlib import Path
import tomllib


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
}


def _merge_dicts(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: str | Path | None = None) -> dict:
    if path is None:
        return dict(DEFAULT_CONFIG)

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    override = tomllib.loads(config_path.read_text(encoding="utf-8"))
    return _merge_dicts(DEFAULT_CONFIG, override)
```

**Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_config.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/openfootprint/core/config.py tests/test_config.py
git commit -m "feat: add config loading with defaults"
```

### Task 4: Input normalization

**Files:**
- Create: `src/openfootprint/core/inputs.py`
- Create: `tests/test_inputs.py`

**Step 1: Write the failing test**

```python
# tests/test_inputs.py
from openfootprint.core.inputs import normalize_email, normalize_phone, normalize_username


def test_normalize_email_lowercases():
    assert normalize_email("Alice@Example.COM") == "alice@example.com"


def test_normalize_phone_e164():
    assert normalize_phone("+1 415 555 0100") == "+14155550100"


def test_normalize_username_strips():
    assert normalize_username("  Alice ") == "alice"
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_inputs.py -v`
Expected: FAIL with `ModuleNotFoundError` for `openfootprint.core.inputs`

**Step 3: Write minimal implementation**

```python
# src/openfootprint/core/inputs.py
from __future__ import annotations

from dataclasses import dataclass

import phonenumbers


def normalize_email(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value.lower() if value else None


def normalize_username(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value.lower() if value else None


def normalize_name(value: str | None) -> str | None:
    if value is None:
        return None
    value = " ".join(value.strip().split())
    return value if value else None


def normalize_phone(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    parsed = phonenumbers.parse(value, None)
    if not phonenumbers.is_valid_number(parsed):
        raise ValueError("Phone number is not valid E.164")
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)


@dataclass(frozen=True)
class LookupInputs:
    username: str | None
    email: str | None
    phone: str | None
    name: str | None

    @classmethod
    def from_raw(
        cls,
        username: str | None,
        email: str | None,
        phone: str | None,
        name: str | None,
    ) -> "LookupInputs":
        return cls(
            username=normalize_username(username),
            email=normalize_email(email),
            phone=normalize_phone(phone),
            name=normalize_name(name),
        )
```

**Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_inputs.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/openfootprint/core/inputs.py tests/test_inputs.py
git commit -m "feat: add input normalization"
```

### Task 5: Core schema dataclasses

**Files:**
- Create: `src/openfootprint/core/schema.py`
- Create: `tests/test_schema.py`

**Step 1: Write the failing test**

```python
# tests/test_schema.py
from openfootprint.core.schema import Evidence, Identifier


def test_evidence_to_dict():
    ev = Evidence(
        source_id="github",
        request_url="https://example.com",
        raw_path="raw/abc.html",
        raw_hash="deadbeef",
        parser_id="github.profile",
        match_excerpt="alice",
        fetched_at="2026-01-14T00:00:00Z",
    )
    assert ev.to_dict()["source_id"] == "github"


def test_identifier_to_dict():
    ident = Identifier(type="username", value="alice", evidence=[])
    assert ident.to_dict()["type"] == "username"
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_schema.py -v`
Expected: FAIL with `ModuleNotFoundError` for `openfootprint.core.schema`

**Step 3: Write minimal implementation**

```python
# src/openfootprint/core/schema.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Evidence:
    source_id: str
    request_url: str
    raw_path: str
    raw_hash: str
    parser_id: str
    match_excerpt: str | None
    fetched_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "request_url": self.request_url,
            "raw_path": self.raw_path,
            "raw_hash": self.raw_hash,
            "parser_id": self.parser_id,
            "match_excerpt": self.match_excerpt,
            "fetched_at": self.fetched_at,
        }


@dataclass(frozen=True)
class Identifier:
    type: str
    value: str
    evidence: list[Evidence] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "value": self.value,
            "evidence": [ev.to_dict() for ev in self.evidence],
        }


@dataclass(frozen=True)
class Entity:
    entity_id: str
    display_name: str | None
    profile_urls: list[str] = field(default_factory=list)
    identifiers: list[Identifier] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "display_name": self.display_name,
            "profile_urls": self.profile_urls,
            "identifiers": [ident.to_dict() for ident in self.identifiers],
            "evidence": [ev.to_dict() for ev in self.evidence],
        }


@dataclass(frozen=True)
class Artifact:
    url: str
    title: str | None
    snippet: str | None
    evidence: list[Evidence] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "snippet": self.snippet,
            "evidence": [ev.to_dict() for ev in self.evidence],
        }


@dataclass(frozen=True)
class Finding:
    source_id: str
    type: str
    entity: Entity
    artifacts: list[Artifact] = field(default_factory=list)
    confidence: str = "medium"

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "type": self.type,
            "entity": self.entity.to_dict(),
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class RunManifest:
    run_id: str
    inputs: dict[str, str | None]
    sources: list[str]
    started_at: str
    finished_at: str | None
    config: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "inputs": self.inputs,
            "sources": self.sources,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "config": self.config,
        }
```

**Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_schema.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/openfootprint/core/schema.py tests/test_schema.py
git commit -m "feat: add core schema dataclasses"
```

### Task 6: Run storage and artifact persistence

**Files:**
- Create: `src/openfootprint/storage/runs.py`
- Create: `tests/test_runs.py`

**Step 1: Write the failing test**

```python
# tests/test_runs.py
from pathlib import Path

from openfootprint.storage.runs import create_run_dir, save_raw_artifact


def test_run_dir_and_raw_artifact(tmp_path: Path):
    run_dir = create_run_dir(tmp_path)
    raw_path = save_raw_artifact(run_dir, "https://example.com", b"hello")
    assert raw_path.exists()
    assert "raw" in raw_path.parts
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_runs.py -v`
Expected: FAIL with `ModuleNotFoundError` for `openfootprint.storage`

**Step 3: Write minimal implementation**

```python
# src/openfootprint/storage/runs.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path


@dataclass(frozen=True)
class RunPaths:
    run_dir: Path
    raw_dir: Path


def _now_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def create_run_dir(base_dir: Path) -> RunPaths:
    run_id = _now_id()
    run_dir = base_dir / run_id
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=False)
    return RunPaths(run_dir=run_dir, raw_dir=raw_dir)


def save_raw_artifact(run_paths: RunPaths, url: str, content: bytes) -> Path:
    digest = sha256(content + url.encode("utf-8")).hexdigest()
    raw_path = run_paths.raw_dir / f"{digest}.bin"
    raw_path.write_bytes(content)
    return raw_path
```

**Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_runs.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/openfootprint/storage/runs.py tests/test_runs.py
git commit -m "feat: add run storage helpers"
```

### Task 7: Robots and rate limit policies

**Files:**
- Create: `src/openfootprint/policies/robots.py`
- Create: `src/openfootprint/policies/rate_limit.py`
- Create: `tests/test_robots.py`
- Create: `tests/test_rate_limit.py`

**Step 1: Write the failing tests**

```python
# tests/test_robots.py
from openfootprint.policies.robots import RobotsPolicy


def test_robots_disallow():
    policy = RobotsPolicy()

    def fetcher(_url):
        return "User-agent: *\nDisallow: /"  # disallow all

    assert policy.allows("https://example.com/private", "OpenFootprint", fetcher) is False
```

```python
# tests/test_rate_limit.py
from openfootprint.policies.rate_limit import RateLimiter


def test_rate_limit_sleeps():
    slept = []

    def fake_sleep(seconds):
        slept.append(seconds)

    times = [0.0, 0.1]

    def fake_now():
        return times.pop(0)

    limiter = RateLimiter(min_interval=1.0, now=fake_now, sleeper=fake_sleep)
    limiter.wait("github")
    limiter.wait("github")

    assert slept and slept[0] >= 0.9
```

**Step 2: Run tests to verify they fail**

Run: `.venv/bin/pytest tests/test_robots.py tests/test_rate_limit.py -v`
Expected: FAIL with `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/openfootprint/policies/robots.py
from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser


@dataclass
class RobotsPolicy:
    cache: dict[str, RobotFileParser] = field(default_factory=dict)

    def allows(self, url: str, user_agent: str, fetcher) -> bool:
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        if base not in self.cache:
            robots_url = f"{base}/robots.txt"
            content = fetcher(robots_url)
            parser = RobotFileParser()
            parser.parse(content.splitlines())
            self.cache[base] = parser
        return self.cache[base].can_fetch(user_agent, url)
```

```python
# src/openfootprint/policies/rate_limit.py
from __future__ import annotations

from dataclasses import dataclass, field
import time


@dataclass
class RateLimiter:
    min_interval: float
    now: callable = time.monotonic
    sleeper: callable = time.sleep
    last_seen: dict[str, float] = field(default_factory=dict)

    def wait(self, key: str) -> None:
        last = self.last_seen.get(key)
        current = self.now()
        if last is not None:
            elapsed = current - last
            if elapsed < self.min_interval:
                sleep_for = self.min_interval - elapsed
                self.sleeper(sleep_for)
                current = current + sleep_for
        self.last_seen[key] = current
```

**Step 4: Run tests to verify they pass**

Run: `.venv/bin/pytest tests/test_robots.py tests/test_rate_limit.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/openfootprint/policies/robots.py src/openfootprint/policies/rate_limit.py tests/test_robots.py tests/test_rate_limit.py
git commit -m "feat: add robots and rate limit policies"
```

### Task 8: Source base and registry

**Files:**
- Create: `src/openfootprint/sources/base.py`
- Create: `src/openfootprint/sources/registry.py`
- Create: `tests/test_sources_registry.py`

**Step 1: Write the failing test**

```python
# tests/test_sources_registry.py
from openfootprint.sources.base import Source, RequestSpec
from openfootprint.sources.registry import SourceRegistry


def test_registry_filters_by_input():
    def build(_inputs):
        return [RequestSpec(url="https://example.com", input_type="username")]

    def parse(_result, _inputs):
        return []

    source = Source(
        source_id="example",
        name="Example",
        category="developer",
        supported_inputs={"username"},
        build_requests=build,
        parse=parse,
    )
    registry = SourceRegistry([source])
    matched = registry.for_inputs({"username"})
    assert matched and matched[0].source_id == "example"
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_sources_registry.py -v`
Expected: FAIL with `ModuleNotFoundError`

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


@dataclass(frozen=True)
class Source:
    source_id: str
    name: str
    category: str
    supported_inputs: set[str]
    build_requests: callable
    parse: callable
```

```python
# src/openfootprint/sources/registry.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .base import Source


@dataclass
class SourceRegistry:
    sources: list[Source]

    def for_inputs(self, inputs: set[str]) -> list[Source]:
        return [source for source in self.sources if source.supported_inputs & inputs]

    def list_sources(self) -> list[Source]:
        return sorted(self.sources, key=lambda s: s.source_id)

    def get(self, source_id: str) -> Source | None:
        for source in self.sources:
            if source.source_id == source_id:
                return source
        return None
```

**Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_sources_registry.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/openfootprint/sources/base.py src/openfootprint/sources/registry.py tests/test_sources_registry.py
git commit -m "feat: add source base and registry"
```

### Task 9: Fetcher wrapper with policy checks

**Files:**
- Create: `src/openfootprint/core/fetcher.py`
- Create: `tests/test_fetcher.py`

**Step 1: Write the failing test**

```python
# tests/test_fetcher.py
from openfootprint.core.fetcher import Fetcher
from openfootprint.policies.robots import RobotsPolicy
from openfootprint.policies.rate_limit import RateLimiter


def test_fetcher_respects_robots():
    policy = RobotsPolicy()

    def robots_fetcher(_url):
        return "User-agent: *\nDisallow: /"

    def http_get(_url, _headers, _timeout):
        raise AssertionError("should not fetch")

    limiter = RateLimiter(min_interval=0.0, now=lambda: 0.0, sleeper=lambda _s: None)
    fetcher = Fetcher("UA", 10, policy, limiter, http_get, robots_fetcher)

    result = fetcher.get("https://example.com", "example")
    assert result.skipped is True
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_fetcher.py -v`
Expected: FAIL with `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/openfootprint/core/fetcher.py
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FetchResult:
    url: str
    status_code: int | None
    headers: dict[str, str]
    content: bytes | None
    error: str | None
    skipped: bool = False


class Fetcher:
    def __init__(
        self,
        user_agent: str,
        timeout_seconds: int,
        robots_policy,
        rate_limiter,
        http_get,
        robots_fetcher,
    ) -> None:
        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds
        self.robots_policy = robots_policy
        self.rate_limiter = rate_limiter
        self.http_get = http_get
        self.robots_fetcher = robots_fetcher

    def get(self, url: str, source_id: str, headers: dict[str, str] | None = None) -> FetchResult:
        if not self.robots_policy.allows(url, self.user_agent, self.robots_fetcher):
            return FetchResult(url=url, status_code=None, headers={}, content=None, error=None, skipped=True)
        self.rate_limiter.wait(source_id)
        try:
            merged = {"User-Agent": self.user_agent}
            if headers:
                merged.update(headers)
            response = self.http_get(url, merged, self.timeout_seconds)
            return FetchResult(
                url=url,
                status_code=response.status_code,
                headers=dict(response.headers),
                content=response.content,
                error=None,
            )
        except Exception as exc:  # noqa: BLE001 - surface as error string
            return FetchResult(url=url, status_code=None, headers={}, content=None, error=str(exc))
```

**Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_fetcher.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/openfootprint/core/fetcher.py tests/test_fetcher.py
git commit -m "feat: add fetcher with policy checks"
```

### Task 10: HTML and JSON parsing helpers

**Files:**
- Create: `src/openfootprint/sources/parsers.py`
- Create: `tests/test_parsers.py`

**Step 1: Write the failing test**

```python
# tests/test_parsers.py
from openfootprint.sources.parsers import extract_title, extract_text


def test_extract_title_and_text():
    html = "<html><head><title>Alice</title></head><body>Hello</body></html>"
    assert extract_title(html) == "Alice"
    assert "Hello" in extract_text(html)
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_parsers.py -v`
Expected: FAIL with `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/openfootprint/sources/parsers.py
from __future__ import annotations

from bs4 import BeautifulSoup


def extract_title(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find("title")
    if not title or not title.text:
        return None
    return title.text.strip()


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(" ", strip=True)
```

**Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_parsers.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/openfootprint/sources/parsers.py tests/test_parsers.py
git commit -m "feat: add html parsing helpers"
```

### Task 11: Simple profile source helper and connectors

**Files:**
- Create: `src/openfootprint/sources/helpers.py`
- Create: `src/openfootprint/sources/developer/__init__.py`
- Create: `src/openfootprint/sources/social/__init__.py`
- Create: `src/openfootprint/sources/blogs/__init__.py`
- Create: `src/openfootprint/sources/directories/__init__.py`
- Create: `src/openfootprint/sources/developer/github.py`
- Create: `src/openfootprint/sources/developer/gitlab.py`
- Create: `src/openfootprint/sources/developer/codeberg.py`
- Create: `src/openfootprint/sources/social/reddit.py`
- Create: `src/openfootprint/sources/social/hackernews.py`
- Create: `src/openfootprint/sources/social/mastodon.py`
- Create: `src/openfootprint/sources/blogs/devto.py`
- Create: `src/openfootprint/sources/blogs/medium.py`
- Create: `src/openfootprint/sources/blogs/wordpress.py`
- Create: `tests/fixtures/*.html`
- Create: `tests/test_profile_sources.py`

**Step 1: Write the failing test**

```python
# tests/test_profile_sources.py
from pathlib import Path

from openfootprint.core.inputs import LookupInputs
from openfootprint.sources.developer.github import SOURCE as GITHUB
from openfootprint.sources.social.reddit import SOURCE as REDDIT


def _fake_fetch_result(html: str):
    return type("R", (), {"status_code": 200, "content": html.encode("utf-8"), "url": "https://example.com"})


def test_github_profile_parses_title():
    html = Path("tests/fixtures/github.html").read_text(encoding="utf-8")
    result = _fake_fetch_result(html)
    findings = GITHUB.parse(result, LookupInputs.from_raw("alice", None, None, None), [])
    assert findings and findings[0].entity.identifiers[0].value == "alice"


def test_reddit_profile_parses_title():
    html = Path("tests/fixtures/reddit.html").read_text(encoding="utf-8")
    result = _fake_fetch_result(html)
    findings = REDDIT.parse(result, LookupInputs.from_raw("alice", None, None, None), [])
    assert findings and findings[0].source_id == "reddit"
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_profile_sources.py -v`
Expected: FAIL with `ModuleNotFoundError` for source modules

**Step 3: Write minimal implementation**

```python
# src/openfootprint/sources/helpers.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from openfootprint.core.schema import Evidence, Identifier, Entity, Finding
from openfootprint.sources.base import RequestSpec, Source
from openfootprint.sources.parsers import extract_title


@dataclass(frozen=True)
class HtmlProfileSource:
    source_id: str
    name: str
    category: str
    url_template: str

    def build_requests(self, inputs) -> list[RequestSpec]:
        if not inputs.username:
            return []
        return [RequestSpec(url=self.url_template.format(username=inputs.username), input_type="username")]

    def parse(self, result, inputs, raw_info: list[tuple[str, str]]) -> list[Finding]:
        if result.status_code != 200 or not result.content:
            return []
        html = result.content.decode("utf-8", errors="replace")
        title = extract_title(html)
        fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        evidence = []
        for raw_path, raw_hash in raw_info:
            evidence.append(
                Evidence(
                    source_id=self.source_id,
                    request_url=result.url,
                    raw_path=raw_path,
                    raw_hash=raw_hash,
                    parser_id=f"{self.source_id}.profile",
                    match_excerpt=title,
                    fetched_at=fetched_at,
                )
            )
        identifier = Identifier(type="username", value=inputs.username, evidence=evidence)
        entity = Entity(
            entity_id=f"{self.source_id}:{inputs.username}",
            display_name=title,
            profile_urls=[result.url],
            identifiers=[identifier],
            evidence=evidence,
        )
        return [Finding(source_id=self.source_id, type="profile", entity=entity, artifacts=[], confidence="medium")]


def make_html_profile_source(source_id: str, name: str, category: str, url_template: str) -> Source:
    helper = HtmlProfileSource(source_id, name, category, url_template)
    return Source(
        source_id=source_id,
        name=name,
        category=category,
        supported_inputs={"username"},
        build_requests=helper.build_requests,
        parse=helper.parse,
    )
```

```python
# src/openfootprint/sources/developer/__init__.py
\"\"\"Developer platform sources.\"\"\"
```

```python
# src/openfootprint/sources/social/__init__.py
\"\"\"Social platform sources.\"\"\"
```

```python
# src/openfootprint/sources/blogs/__init__.py
\"\"\"Blog and feed sources.\"\"\"
```

```python
# src/openfootprint/sources/directories/__init__.py
\"\"\"People directory sources.\"\"\"
```

```python
# src/openfootprint/sources/developer/github.py
from openfootprint.sources.helpers import make_html_profile_source


SOURCE = make_html_profile_source("github", "GitHub", "developer", "https://github.com/{username}")
```

```python
# src/openfootprint/sources/developer/gitlab.py
from openfootprint.sources.helpers import make_html_profile_source


SOURCE = make_html_profile_source("gitlab", "GitLab", "developer", "https://gitlab.com/{username}")
```

```python
# src/openfootprint/sources/developer/codeberg.py
from openfootprint.sources.helpers import make_html_profile_source


SOURCE = make_html_profile_source("codeberg", "Codeberg", "developer", "https://codeberg.org/{username}")
```

```python
# src/openfootprint/sources/social/reddit.py
from openfootprint.sources.helpers import make_html_profile_source


SOURCE = make_html_profile_source("reddit", "Reddit", "social", "https://www.reddit.com/user/{username}")
```

```python
# src/openfootprint/sources/social/hackernews.py
from openfootprint.sources.helpers import make_html_profile_source


SOURCE = make_html_profile_source("hackernews", "Hacker News", "social", "https://news.ycombinator.com/user?id={username}")
```

```python
# src/openfootprint/sources/social/mastodon.py
from openfootprint.sources.base import RequestSpec, Source
from openfootprint.sources.helpers import HtmlProfileSource


class MastodonSource(HtmlProfileSource):
    def build_requests(self, inputs) -> list[RequestSpec]:
        if not inputs.username or "@" not in inputs.username:
            return []
        user, instance = inputs.username.split("@", 1)
        url = f"https://{instance}/@{user}"
        return [RequestSpec(url=url, input_type="username")]


_helper = MastodonSource("mastodon", "Mastodon", "social", "")
SOURCE = Source(
    source_id="mastodon",
    name="Mastodon",
    category="social",
    supported_inputs={"username"},
    build_requests=_helper.build_requests,
    parse=_helper.parse,
)
```

```python
# src/openfootprint/sources/blogs/devto.py
from openfootprint.sources.helpers import make_html_profile_source


SOURCE = make_html_profile_source("devto", "Dev.to", "blogs", "https://dev.to/{username}")
```

```python
# src/openfootprint/sources/blogs/medium.py
from openfootprint.sources.helpers import make_html_profile_source


SOURCE = make_html_profile_source("medium", "Medium", "blogs", "https://medium.com/@{username}")
```

```python
# src/openfootprint/sources/blogs/wordpress.py
from openfootprint.sources.helpers import make_html_profile_source


SOURCE = make_html_profile_source("wordpress", "WordPress.com", "blogs", "https://{username}.wordpress.com")
```

```html
<!-- tests/fixtures/github.html -->
<html><head><title>alice - GitHub</title></head><body>Profile</body></html>
```

```html
<!-- tests/fixtures/reddit.html -->
<html><head><title>u/alice - Reddit</title></head><body>Profile</body></html>
```

**Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_profile_sources.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/openfootprint/sources/helpers.py \
  src/openfootprint/sources/developer/__init__.py \
  src/openfootprint/sources/social/__init__.py \
  src/openfootprint/sources/blogs/__init__.py \
  src/openfootprint/sources/directories/__init__.py \
  src/openfootprint/sources/developer/github.py \
  src/openfootprint/sources/developer/gitlab.py \
  src/openfootprint/sources/developer/codeberg.py \
  src/openfootprint/sources/social/reddit.py \
  src/openfootprint/sources/social/hackernews.py \
  src/openfootprint/sources/social/mastodon.py \
  src/openfootprint/sources/blogs/devto.py \
  src/openfootprint/sources/blogs/medium.py \
  src/openfootprint/sources/blogs/wordpress.py \
  tests/fixtures/github.html tests/fixtures/reddit.html tests/test_profile_sources.py
git commit -m "feat: add html profile source connectors"
```

### Task 12: Directory connectors (JSON search)

**Files:**
- Create: `src/openfootprint/sources/directories/wikidata.py`
- Create: `src/openfootprint/sources/directories/orcid.py`
- Create: `src/openfootprint/sources/directories/openalex.py`
- Create: `tests/fixtures/wikidata.json`
- Create: `tests/fixtures/openalex.json`
- Create: `tests/fixtures/orcid.json`
- Create: `tests/test_directory_sources.py`

**Step 1: Write the failing test**

```python
# tests/test_directory_sources.py
from pathlib import Path

from openfootprint.core.inputs import LookupInputs
from openfootprint.sources.directories.wikidata import SOURCE as WIKIDATA


def _fake_json_result(text: str):
    return type("R", (), {"status_code": 200, "content": text.encode("utf-8"), "url": "https://example.com"})


def test_wikidata_parses_entities():
    data = Path("tests/fixtures/wikidata.json").read_text(encoding="utf-8")
    result = _fake_json_result(data)
    findings = WIKIDATA.parse(result, LookupInputs.from_raw(None, None, None, "Alice"), [])
    assert findings and findings[0].source_id == "wikidata"
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_directory_sources.py -v`
Expected: FAIL with `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/openfootprint/sources/directories/wikidata.py
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone

from openfootprint.core.schema import Evidence, Identifier, Entity, Finding
from openfootprint.sources.base import RequestSpec, Source


def build_requests(inputs):
    if not inputs.name:
        return []
    url = (
        "https://www.wikidata.org/w/api.php?action=wbsearchentities"
        f"&format=json&language=en&search={inputs.name}"
    )
    return [RequestSpec(url=url, input_type="name")]


def parse(result, inputs, raw_info):
    if result.status_code != 200 or not result.content:
        return []
    payload = json.loads(result.content.decode("utf-8", errors="replace"))
    hits = payload.get("search", [])
    if not hits:
        return []
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    evidence = []
    for raw_path, raw_hash in raw_info:
        evidence.append(
            Evidence(
                source_id="wikidata",
                request_url=result.url,
                raw_path=raw_path,
                raw_hash=raw_hash,
                parser_id="wikidata.search",
                match_excerpt=inputs.name,
                fetched_at=fetched_at,
            )
        )
    entity = Entity(
        entity_id=f"wikidata:{hits[0].get('id', 'unknown')}",
        display_name=hits[0].get("label"),
        profile_urls=[hits[0].get("concepturi", "")],
        identifiers=[Identifier(type="name", value=inputs.name, evidence=evidence)],
        evidence=evidence,
    )
    return [Finding(source_id="wikidata", type="directory", entity=entity, artifacts=[], confidence="low")]


SOURCE = Source(
    source_id="wikidata",
    name="Wikidata",
    category="directories",
    supported_inputs={"name"},
    build_requests=build_requests,
    parse=parse,
)
```

```python
# src/openfootprint/sources/directories/openalex.py
from __future__ import annotations

import json
from datetime import datetime, timezone

from openfootprint.core.schema import Evidence, Identifier, Entity, Finding
from openfootprint.sources.base import RequestSpec, Source


def build_requests(inputs):
    if not inputs.name:
        return []
    url = f"https://api.openalex.org/authors?search={inputs.name}"
    return [RequestSpec(url=url, input_type="name")]


def parse(result, inputs, raw_info):
    if result.status_code != 200 or not result.content:
        return []
    payload = json.loads(result.content.decode("utf-8", errors="replace"))
    hits = payload.get("results", [])
    if not hits:
        return []
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    evidence = []
    for raw_path, raw_hash in raw_info:
        evidence.append(
            Evidence(
                source_id="openalex",
                request_url=result.url,
                raw_path=raw_path,
                raw_hash=raw_hash,
                parser_id="openalex.search",
                match_excerpt=inputs.name,
                fetched_at=fetched_at,
            )
        )
    entity = Entity(
        entity_id=f"openalex:{hits[0].get('id', 'unknown')}",
        display_name=hits[0].get("display_name"),
        profile_urls=[hits[0].get("id", "")],
        identifiers=[Identifier(type="name", value=inputs.name, evidence=evidence)],
        evidence=evidence,
    )
    return [Finding(source_id="openalex", type="directory", entity=entity, artifacts=[], confidence="low")]


SOURCE = Source(
    source_id="openalex",
    name="OpenAlex",
    category="directories",
    supported_inputs={"name"},
    build_requests=build_requests,
    parse=parse,
)
```

```python
# src/openfootprint/sources/directories/orcid.py
from __future__ import annotations

import json
from datetime import datetime, timezone

from openfootprint.core.schema import Evidence, Identifier, Entity, Finding
from openfootprint.sources.base import RequestSpec, Source


def build_requests(inputs):
    if not inputs.name:
        return []
    url = f"https://pub.orcid.org/v3.0/search/?q={inputs.name}"
    headers = {"Accept": "application/json"}
    return [RequestSpec(url=url, input_type="name", headers=headers)]


def parse(result, inputs, raw_info):
    if result.status_code != 200 or not result.content:
        return []
    payload = json.loads(result.content.decode("utf-8", errors="replace"))
    hits = payload.get("result", [])
    if not hits:
        return []
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    evidence = []
    for raw_path, raw_hash in raw_info:
        evidence.append(
            Evidence(
                source_id="orcid",
                request_url=result.url,
                raw_path=raw_path,
                raw_hash=raw_hash,
                parser_id="orcid.search",
                match_excerpt=inputs.name,
                fetched_at=fetched_at,
            )
        )
    orcid_id = hits[0].get("orcid-identifier", {}).get("path", "")
    profile_url = f"https://orcid.org/{orcid_id}" if orcid_id else ""
    entity = Entity(
        entity_id=f"orcid:{orcid_id or 'unknown'}",
        display_name=inputs.name,
        profile_urls=[profile_url],
        identifiers=[Identifier(type="name", value=inputs.name, evidence=evidence)],
        evidence=evidence,
    )
    return [Finding(source_id="orcid", type="directory", entity=entity, artifacts=[], confidence="low")]


SOURCE = Source(
    source_id="orcid",
    name="ORCID",
    category="directories",
    supported_inputs={"name"},
    build_requests=build_requests,
    parse=parse,
)
```

```json
// tests/fixtures/wikidata.json
{"search":[{"id":"Q1","label":"Alice","concepturi":"https://www.wikidata.org/wiki/Q1"}]}
```

```json
// tests/fixtures/openalex.json
{"results":[{"id":"https://openalex.org/A1","display_name":"Alice"}]}
```

```json
// tests/fixtures/orcid.json
{"result":[{"orcid-identifier":{"path":"0000-0000-0000-0000"}}]}
```

**Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_directory_sources.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/openfootprint/sources/directories/wikidata.py \
  src/openfootprint/sources/directories/orcid.py \
  src/openfootprint/sources/directories/openalex.py \
  tests/fixtures/wikidata.json tests/fixtures/openalex.json tests/fixtures/orcid.json \
  tests/test_directory_sources.py
git commit -m "feat: add directory source connectors"
```

### Task 13: Query planning

**Files:**
- Create: `src/openfootprint/core/plan.py`
- Create: `tests/test_plan.py`

**Step 1: Write the failing test**

```python
# tests/test_plan.py
from openfootprint.core.inputs import LookupInputs
from openfootprint.core.plan import build_plan
from openfootprint.sources.base import Source, RequestSpec
from openfootprint.sources.registry import SourceRegistry


def test_build_plan_includes_username_sources():
    def build(_inputs):
        return [RequestSpec(url="https://example.com", input_type="username")]

    def parse(_result, _inputs, _raw):
        return []

    source = Source(
        source_id="example",
        name="Example",
        category="developer",
        supported_inputs={"username"},
        build_requests=build,
        parse=parse,
    )
    registry = SourceRegistry([source])
    plan = build_plan(LookupInputs.from_raw("alice", None, None, None), registry)
    assert plan and plan[0].source_id == "example"
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_plan.py -v`
Expected: FAIL with `ModuleNotFoundError`

**Step 3: Write minimal implementation**

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
                )
            )
    return plan
```

**Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_plan.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/openfootprint/core/plan.py tests/test_plan.py
git commit -m "feat: add query planning"
```

### Task 14: Correlation logic

**Files:**
- Create: `src/openfootprint/core/correlate.py`
- Create: `tests/test_correlate.py`

**Step 1: Write the failing test**

```python
# tests/test_correlate.py
from openfootprint.core.correlate import correlate_findings
from openfootprint.core.schema import Entity, Finding, Identifier


def test_correlate_merges_by_identifier():
    ent1 = Entity(entity_id="a", display_name=None, profile_urls=[], identifiers=[Identifier("email", "a@b.com")])
    ent2 = Entity(entity_id="b", display_name=None, profile_urls=[], identifiers=[Identifier("email", "a@b.com")])
    findings = [
        Finding(source_id="s1", type="profile", entity=ent1),
        Finding(source_id="s2", type="profile", entity=ent2),
    ]
    merged = correlate_findings(findings)
    assert len(merged) == 1
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_correlate.py -v`
Expected: FAIL with `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/openfootprint/core/correlate.py
from __future__ import annotations

from collections import defaultdict

from openfootprint.core.schema import Entity


def correlate_findings(findings):
    buckets = defaultdict(list)
    for finding in findings:
        identifiers = [f"{ident.type}:{ident.value}" for ident in finding.entity.identifiers]
        key = identifiers[0] if identifiers else finding.entity.entity_id
        buckets[key].append(finding.entity)

    merged = []
    for key, entities in buckets.items():
        primary = entities[0]
        for extra in entities[1:]:
            primary.profile_urls.extend(extra.profile_urls)
            primary.identifiers.extend(extra.identifiers)
            primary.evidence.extend(extra.evidence)
        merged.append(primary)
    return merged
```

**Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_correlate.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/openfootprint/core/correlate.py tests/test_correlate.py
git commit -m "feat: add basic correlation"
```

### Task 15: Reporting (console, JSON, Markdown)

**Files:**
- Create: `src/openfootprint/reporting/console.py`
- Create: `src/openfootprint/reporting/json_report.py`
- Create: `src/openfootprint/reporting/markdown_report.py`
- Create: `tests/test_reporting.py`

**Step 1: Write the failing test**

```python
# tests/test_reporting.py
from openfootprint.reporting.markdown_report import render_markdown
from openfootprint.core.schema import Entity, Finding, Identifier


def test_markdown_includes_sources():
    entity = Entity(entity_id="a", display_name="Alice", profile_urls=["https://x"], identifiers=[Identifier("username", "alice")])
    findings = [Finding(source_id="github", type="profile", entity=entity)]
    report = render_markdown(findings, ["github"], "run-1")
    assert "github" in report
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_reporting.py -v`
Expected: FAIL with `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/openfootprint/reporting/json_report.py
from __future__ import annotations

import json


def render_json(findings, sources, run_id) -> str:
    payload = {
        "run_id": run_id,
        "sources": sources,
        "findings": [finding.to_dict() for finding in findings],
    }
    return json.dumps(payload, indent=2, sort_keys=True)
```

```python
# src/openfootprint/reporting/markdown_report.py
from __future__ import annotations


def render_markdown(findings, sources, run_id) -> str:
    lines = [f"# OpenFootprint Report", "", f"Run: {run_id}", "", "## Sources", ""]
    for source in sources:
        lines.append(f"- {source}")
    lines.append("")
    lines.append("## Findings")
    for finding in findings:
        lines.append(f"- {finding.source_id}: {finding.entity.display_name or finding.entity.entity_id}")
    lines.append("")
    return "\n".join(lines)
```

```python
# src/openfootprint/reporting/console.py
from __future__ import annotations


def render_console(findings, sources, run_id) -> str:
    lines = [f"OpenFootprint run {run_id}", f"Sources: {', '.join(sources)}", "Findings:"]
    for finding in findings:
        lines.append(f"- {finding.source_id}: {finding.entity.display_name or finding.entity.entity_id}")
    return "\n".join(lines)
```

**Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_reporting.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/openfootprint/reporting/console.py src/openfootprint/reporting/json_report.py src/openfootprint/reporting/markdown_report.py tests/test_reporting.py
git commit -m "feat: add report renderers"
```

### Task 16: Persist run outputs

**Files:**
- Modify: `src/openfootprint/storage/runs.py`
- Create: `tests/test_run_outputs.py`

**Step 1: Write the failing test**

```python
# tests/test_run_outputs.py
from pathlib import Path

from openfootprint.core.schema import RunManifest
from openfootprint.storage.runs import create_run_dir, write_json, write_text, write_manifest


def test_write_outputs(tmp_path: Path):
    run_paths = create_run_dir(tmp_path)
    json_path = write_json(run_paths.run_dir, "report.json", {"ok": True})
    md_path = write_text(run_paths.run_dir, "report.md", "hello")

    manifest = RunManifest(
        run_id=run_paths.run_dir.name,
        inputs={"username": "alice"},
        sources=["github"],
        started_at="2026-01-14T00:00:00Z",
        finished_at=None,
        config={"http": {"timeout_seconds": 1}},
    )
    manifest_path = write_manifest(run_paths, manifest)

    assert json_path.exists()
    assert md_path.read_text(encoding="utf-8") == "hello"
    assert manifest_path.name == "manifest.json"
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_run_outputs.py -v`
Expected: FAIL with `ImportError` for new helpers

**Step 3: Write minimal implementation**

```python
# src/openfootprint/storage/runs.py (append)
import json

from openfootprint.core.schema import RunManifest


def write_json(run_dir: Path, filename: str, payload: dict) -> Path:
    path = run_dir / filename
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def write_text(run_dir: Path, filename: str, text: str) -> Path:
    path = run_dir / filename
    path.write_text(text, encoding="utf-8")
    return path


def write_manifest(run_paths: RunPaths, manifest: RunManifest) -> Path:
    return write_json(run_paths.run_dir, "manifest.json", manifest.to_dict())
```

**Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_run_outputs.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/openfootprint/storage/runs.py tests/test_run_outputs.py
git commit -m "feat: add run output writers"
```

### Task 17: Pipeline orchestration

**Files:**
- Create: `src/openfootprint/core/pipeline.py`
- Create: `tests/test_pipeline.py`

**Step 1: Write the failing test**

```python
# tests/test_pipeline.py
from pathlib import Path

from openfootprint.core.inputs import LookupInputs
from openfootprint.core.pipeline import run_lookup
from openfootprint.sources.base import Source, RequestSpec
from openfootprint.sources.registry import SourceRegistry


def test_pipeline_runs_with_fake_source(tmp_path: Path, monkeypatch):
    def build(_inputs):
        return [RequestSpec(url="https://example.com", input_type="username")]

    def parse(_result, _inputs, _raw):
        return []

    source = Source(
        source_id="example",
        name="Example",
        category="developer",
        supported_inputs={"username"},
        build_requests=build,
        parse=parse,
    )

    registry = SourceRegistry([source])
    inputs = LookupInputs.from_raw("alice", None, None, None)

    class FakeResponse:
        status_code = 200
        content = b""
        url = "https://example.com"
        headers = {}

    def fake_http_get(_url, _headers, _timeout):
        return FakeResponse()

    def fake_robots(_url):
        return "User-agent: *\nAllow: /"

    from openfootprint.core import pipeline

    monkeypatch.setattr(pipeline, "_http_get", fake_http_get)
    monkeypatch.setattr(pipeline, "_robots_fetch", fake_robots)

    config = {
        "http": {"user_agent": "UA", "timeout_seconds": 1},
        "rate_limit": {"min_interval_seconds": 0},
        "output": {"runs_dir": str(tmp_path)},
    }
    results = run_lookup(inputs, registry, config)
    assert Path(results["paths"]["manifest"]).exists()
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_pipeline.py -v`
Expected: FAIL with `ModuleNotFoundError`

**Step 3: Write minimal implementation**

```python
# src/openfootprint/core/pipeline.py
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
```

**Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_pipeline.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/openfootprint/core/pipeline.py tests/test_pipeline.py
git commit -m "feat: add minimal pipeline"
```

### Task 18: CLI commands wired to pipeline

**Files:**
- Modify: `src/openfootprint/cli.py`
- Create: `tests/test_cli_lookup.py`

**Step 1: Write the failing test**

```python
# tests/test_cli_lookup.py
import os
import subprocess
import sys
from pathlib import Path


def test_cli_lookup_runs(tmp_path: Path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    result = subprocess.run(
        [sys.executable, "-m", "openfootprint", "lookup", "--username", "alice", "--output", str(tmp_path)],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_cli_lookup.py -v`
Expected: FAIL because `lookup` is stubbed

**Step 3: Write minimal implementation**

```python
# src/openfootprint/cli.py (replace stub logic)
import argparse

from openfootprint.core.config import load_config
from openfootprint.core.inputs import LookupInputs
from openfootprint.core.pipeline import run_lookup
from openfootprint.sources.registry import SourceRegistry
from openfootprint.sources.developer.github import SOURCE as GITHUB
from openfootprint.sources.developer.gitlab import SOURCE as GITLAB
from openfootprint.sources.developer.codeberg import SOURCE as CODEBERG
from openfootprint.sources.social.reddit import SOURCE as REDDIT
from openfootprint.sources.social.hackernews import SOURCE as HN
from openfootprint.sources.social.mastodon import SOURCE as MASTODON
from openfootprint.sources.blogs.devto import SOURCE as DEVTO
from openfootprint.sources.blogs.medium import SOURCE as MEDIUM
from openfootprint.sources.blogs.wordpress import SOURCE as WORDPRESS
from openfootprint.sources.directories.wikidata import SOURCE as WIKIDATA
from openfootprint.sources.directories.orcid import SOURCE as ORCID
from openfootprint.sources.directories.openalex import SOURCE as OPENALEX

from . import __version__


def _registry() -> SourceRegistry:
    return SourceRegistry([
        GITHUB, GITLAB, CODEBERG,
        REDDIT, HN, MASTODON,
        DEVTO, MEDIUM, WORDPRESS,
        WIKIDATA, ORCID, OPENALEX,
    ])


def _cmd_lookup(args) -> int:
    config = load_config(args.config)
    if args.output:
        config["output"]["runs_dir"] = args.output
    inputs = LookupInputs.from_raw(args.username, args.email, args.phone, args.name)
    result = run_lookup(inputs, _registry(), config)
    print(result["console"])
    return 0


def _cmd_sources_list(_args) -> int:
    for source in _registry().list_sources():
        print(f"{source.source_id}\t{source.name}\t{source.category}")
    return 0


def _cmd_sources_info(args) -> int:
    source = _registry().get(args.source_id)
    if not source:
        print("Source not found")
        return 1
    print(f"{source.source_id} - {source.name}\nCategory: {source.category}\nInputs: {', '.join(sorted(source.supported_inputs))}")
    return 0


def _cmd_plan(args) -> int:
    from openfootprint.core.plan import build_plan

    config = load_config(args.config)
    inputs = LookupInputs.from_raw(args.username, args.email, args.phone, args.name)
    plan = build_plan(inputs, _registry())
    for item in plan:
        print(f"{item.source_id}\t{item.input_type}\t{item.url}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="openfootprint", description="Public-source OSINT lookup tool")
    parser.add_argument("--version", action="version", version=__version__)

    subparsers = parser.add_subparsers(dest="command")

    lookup = subparsers.add_parser("lookup", help="Run a public-source lookup")
    lookup.add_argument("--username")
    lookup.add_argument("--email")
    lookup.add_argument("--phone")
    lookup.add_argument("--name")
    lookup.add_argument("--config")
    lookup.add_argument("--output")
    lookup.set_defaults(func=_cmd_lookup)

    sources = subparsers.add_parser("sources", help="List or inspect sources")
    sources_sub = sources.add_subparsers(dest="sources_command")
    sources_list = sources_sub.add_parser("list", help="List available sources")
    sources_list.set_defaults(func=_cmd_sources_list)
    sources_info = sources_sub.add_parser("info", help="Show details for a source")
    sources_info.add_argument("source_id")
    sources_info.set_defaults(func=_cmd_sources_info)

    plan = subparsers.add_parser("plan", help="Show a dry-run query plan")
    plan.add_argument("--username")
    plan.add_argument("--email")
    plan.add_argument("--phone")
    plan.add_argument("--name")
    plan.add_argument("--config")
    plan.set_defaults(func=_cmd_plan)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    return int(args.func(args))
```

**Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_cli_lookup.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/openfootprint/cli.py tests/test_cli_lookup.py
git commit -m "feat: wire cli commands to pipeline"
```

### Task 19: Integration test with fixtures

**Files:**
- Create: `tests/test_integration.py`

**Step 1: Write the failing test**

```python
# tests/test_integration.py
from pathlib import Path

from openfootprint.core.inputs import LookupInputs
from openfootprint.core.pipeline import run_lookup
from openfootprint.sources.developer.github import SOURCE as GITHUB
from openfootprint.sources.registry import SourceRegistry


def test_integration_with_fixture(tmp_path: Path, monkeypatch):
    html = Path("tests/fixtures/github.html").read_text(encoding="utf-8")

    class FakeResponse:
        status_code = 200
        content = html.encode("utf-8")
        url = "https://github.com/alice"
        headers = {}

    def fake_http_get(_url, _headers, _timeout):
        return FakeResponse()

    def fake_robots(_url):
        return "User-agent: *\nAllow: /"

    from openfootprint.core import pipeline

    monkeypatch.setattr(pipeline, "_http_get", fake_http_get)
    monkeypatch.setattr(pipeline, "_robots_fetch", fake_robots)

    registry = SourceRegistry([GITHUB])
    inputs = LookupInputs.from_raw("alice", None, None, None)
    config = {"http": {"user_agent": "UA", "timeout_seconds": 1}, "rate_limit": {"min_interval_seconds": 0}, "output": {"runs_dir": str(tmp_path)}}

    result = run_lookup(inputs, registry, config)
    assert result["findings"]
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/pytest tests/test_integration.py -v`
Expected: FAIL before monkeypatch hooks exist

**Step 3: Write minimal implementation**

Adjust `src/openfootprint/core/pipeline.py` so `_http_get` and `_robots_fetch` are module-level functions that can be monkeypatched (already present). No code change expected unless names differ.

**Step 4: Run test to verify it passes**

Run: `.venv/bin/pytest tests/test_integration.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add integration test with fixtures"
```

### Task 20: README usage and ethics update

**Files:**
- Modify: `README.md`

**Step 1: Write a failing test (doc check)**

Skip test (documentation-only change).

**Step 2: Update README**

Add sections for install, basic usage, and ethics policy. Include example commands:
- `openfootprint lookup --username alice --name "Alice Smith"`
- `openfootprint sources list`
- `openfootprint plan --username alice`

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add usage and ethics policy"
```
