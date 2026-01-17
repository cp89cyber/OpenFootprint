from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass


def is_crosslinked_available() -> bool:
    return shutil.which("crosslinked") is not None


@dataclass(frozen=True)
class CrossLinkedRunResult:
    available: bool
    returncode: int | None
    stdout: str
    stderr: str


def run_crosslinked(*, args: list[str], timeout_seconds: int = 60) -> CrossLinkedRunResult:
    if not is_crosslinked_available():
        return CrossLinkedRunResult(available=False, returncode=None, stdout="", stderr="crosslinked not found on PATH")

    proc = subprocess.run(
        ["crosslinked", *args],
        capture_output=True,
        text=True,
        timeout=int(timeout_seconds),
    )
    return CrossLinkedRunResult(
        available=True,
        returncode=int(proc.returncode),
        stdout=proc.stdout or "",
        stderr=proc.stderr or "",
    )

