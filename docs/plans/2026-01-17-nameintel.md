# NameIntel Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add `openfootprint nameintel` to generate username permutations, validate via Sherlock, optionally run CrossLinked, and generate/execute SerpAPI dorks (with optional keywords/context).

**Architecture:** Keep `nameintel` as a small, self-contained module that produces a `nameintel` section in `report.json` and stores raw artifacts under `runs/<run_id>/raw/`. Integrate via CLI without disturbing existing `lookup` flow.

**Tech Stack:** Python, existing OpenFootprint run storage/reporting, external tools via subprocess (Sherlock, CrossLinked), SerpAPI via HTTPS (no scraping Google directly).

---

### Task 1: Add core permutation generator

**Files:**
- Create: `src/openfootprint/nameintel/__init__.py`
- Create: `src/openfootprint/nameintel/permutations.py`
- Test: `tests/test_nameintel_permutations.py`

**Step 1: Write the failing test**

```python
from openfootprint.nameintel.permutations import generate_permutations


def test_generate_permutations_includes_common_forms_and_year():
    perms = generate_permutations(first="John", last="Doe", birth_year=1990, limit=200)
    assert "j.doe" in perms
    assert "doejohn1990" in perms
    assert "johndoe90" in perms
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_nameintel_permutations.py -v`  
Expected: FAIL (module/function not found)

**Step 3: Write minimal implementation**

```python
def generate_permutations(first: str, last: str, birth_year: int | None, limit: int = 100) -> list[str]:
    ...
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_nameintel_permutations.py -v`  
Expected: PASS

---

### Task 2: Add dork generator (keywords + handle OR)

**Files:**
- Create: `src/openfootprint/nameintel/dorks.py`
- Test: `tests/test_nameintel_dorks.py`

**Step 1: Write the failing test**

```python
from openfootprint.nameintel.dorks import build_dork_queries


def test_build_dork_queries_uses_keywords_and_handle_or():
    queries = build_dork_queries(
        full_name="John Doe",
        sites=["linkedin", "instagram"],
        keywords=["software", "engineer", "berlin"],
        top_permutations=["johndoe1990", "j.doe"],
    )
    assert any('site:linkedin.com/in "John Doe"' in q for q in queries)
    assert any('("software" OR "engineer" OR "berlin")' in q for q in queries)
    assert any('("johndoe1990" OR "j.doe")' in q for q in queries)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_nameintel_dorks.py -v`  
Expected: FAIL

**Step 3: Write minimal implementation**

```python
def build_dork_queries(...)-> list[str]:
    ...
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_nameintel_dorks.py -v`  
Expected: PASS

---

### Task 3: Add SerpAPI client + artifact naming

**Files:**
- Create: `src/openfootprint/nameintel/serpapi.py`
- Test: `tests/test_nameintel_serpapi.py`

**Step 1: Write the failing test**

```python
from openfootprint.nameintel.serpapi import query_to_artifact_name


def test_query_to_artifact_name_is_stable_and_scoped():
    name = query_to_artifact_name(site="instagram", query='site:instagram.com "john doe"')
    assert name.startswith("serpapi_instagram_")
    assert name.endswith(".json")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_nameintel_serpapi.py -v`  
Expected: FAIL

**Step 3: Write minimal implementation**

Implement hashing and naming: `serpapi_<site>_<sha256-12>.json`.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_nameintel_serpapi.py -v`  
Expected: PASS

---

### Task 4: Add CrossLinked optional runner (skip if missing)

**Files:**
- Create: `src/openfootprint/nameintel/crosslinked.py`
- Test: `tests/test_nameintel_crosslinked.py`

**Step 1: Write the failing test**

```python
from openfootprint.nameintel.crosslinked import is_crosslinked_available


def test_is_crosslinked_available_false_when_missing(monkeypatch):
    monkeypatch.setenv("PATH", "")
    assert is_crosslinked_available() is False
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_nameintel_crosslinked.py -v`  
Expected: FAIL

**Step 3: Write minimal implementation**

Use `shutil.which("crosslinked")`.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_nameintel_crosslinked.py -v`  
Expected: PASS

---

### Task 5: Wire `nameintel` into CLI (dry-run, estimated credits)

**Files:**
- Modify: `src/openfootprint/cli.py`
- Create: `src/openfootprint/nameintel/command.py`
- Test: `tests/test_cli_nameintel.py`

**Step 1: Write the failing test**

```python
from openfootprint.cli import build_parser


def test_cli_has_nameintel_subcommand():
    parser = build_parser()
    args = parser.parse_args(["nameintel", "--first", "John", "--last", "Doe", "--dry-run"])
    assert args.command == "nameintel"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli_nameintel.py -v`  
Expected: FAIL

**Step 3: Write minimal implementation**

Add subparser + route to `openfootprint.nameintel.command`.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli_nameintel.py -v`  
Expected: PASS

---

### Task 6: Add Sherlock validation loop for permutations

**Files:**
- Create: `src/openfootprint/nameintel/sherlock_validate.py`
- Test: `tests/test_nameintel_sherlock_validate.py`

**Step 1: Write the failing test**

```python
from openfootprint.nameintel.sherlock_validate import summarize_sherlock_findings


def test_summarize_sherlock_findings_shapes_output():
    summary = summarize_sherlock_findings(
        [
            {
                "entity": {
                    "profile_urls": ["https://github.com/johndoe"],
                    "display_name": "johndoe",
                }
            }
        ]
    )
    assert summary[0]["url"] == "https://github.com/johndoe"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_nameintel_sherlock_validate.py -v`  
Expected: FAIL

**Step 3: Write minimal implementation**

Keep parsing logic isolated; store raw tool output separately.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_nameintel_sherlock_validate.py -v`  
Expected: PASS

---

### Task 7: End-to-end smoke test (dry-run)

**Files:**
- Test: `tests/test_nameintel_smoke.py`

**Step 1: Write the failing test**

```python
import subprocess
import sys


def test_nameintel_dry_run_exits_zero():
    proc = subprocess.run(
        [sys.executable, "-m", "openfootprint", "nameintel", "--first", "John", "--last", "Doe", "--dry-run"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "permutations" in (proc.stdout + proc.stderr).lower()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_nameintel_smoke.py -v`  
Expected: FAIL

**Step 3: Write minimal implementation**

Ensure `__main__` dispatch supports `nameintel` via `cli.py`.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_nameintel_smoke.py -v`  
Expected: PASS

