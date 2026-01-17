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
