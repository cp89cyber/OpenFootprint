# NameIntel Design

**Status:** Approved (with effectiveness tweaks)

## Goal

Add a focused name-based workflow that:

- Accepts `First Name`, `Last Name`, and optional `Birth Year`.
- Generates a bounded, ordered list of common username permutations.
- Validates username permutations on major platforms via Sherlock.
- Generates and executes high-signal Google dorks via SerpAPI (with optional analyst-provided context).
- Optionally derives/boosts likely naming patterns via CrossLinked (best-effort; skip if not installed).

## CLI Shape

Add a new command:

```bash
openfootprint nameintel --first John --last Doe --birth-year 1990 \
  --sherlock \
  --dorks --dorks-sites linkedin instagram --dorks-limit 10 \
  --keywords "software, engineer, berlin" \
  --crosslinked
```

Key flags:

- `--first`, `--last` (required)
- `--birth-year` (optional)
- `--sherlock` (optional, enabled-by-flag)
- `--dorks` (optional, enabled-by-flag)
- `--dorks-sites` (subset selection; at least `linkedin`, `instagram`)
- `--dorks-limit` (default small; see “Safety Controls”)
- `--keywords` / `--context` (optional comma-separated analyst context)
- `--crosslinked` (optional, enabled-by-flag)
- `--dry-run` (prints dorks/plan; does not call SerpAPI / external tools)

## Outputs

Each run continues to write under `runs/<run_id>/`:

- `manifest.json` (inputs, config, enabled modules)
- `raw/` (artifacts for SerpAPI + external tools)
- `report.json` (machine-readable, includes `nameintel` section)
- `report.md` (human-readable summary)
- Console summary (high signal, low noise)

## Permutation Generator

### Normalization

Inputs are normalized before permutation:

- Lowercase.
- Strip accents (e.g., `José` → `jose`).
- Collapse internal whitespace/punctuation to a canonical token form.

Both a “token” form and “display” form can be retained for reporting, but generated usernames use the normalized form.

### Strategy

Generate a bounded, ordered, de-duplicated list (target cap: ~50–150) using common patterns:

- Separators: `""`, `.`, `_`, `-`
- Forms:
  - `firstlast`, `lastfirst`
  - `first{sep}last`, `last{sep}first`
  - `f{sep}last`, `first{sep}l`
  - `fi{sep}last`, `first{sep}li` (two-letter initials)
  - `first`, `last` (lower priority)
- Birth year (optional):
  - Append `YYYY` and `YY` to “compound” forms (avoid runaway duplication)

Each candidate carries metadata describing its generation rule (pattern id + components) so reports can explain “why this username”.

## Validation via Sherlock

Use the existing Sherlock integration already present in OpenFootprint:

- For each candidate username, run Sherlock checks and collect hits per platform.
- Respect existing rate limits/policies.
- Store raw artifacts per candidate.
- Summarize results as: `candidate -> [{site, url, status}]`.

## Corporate Naming Conventions via CrossLinked (Optional)

Integrate CrossLinked as a best-effort naming convention hint provider:

- If CrossLinked isn’t installed / not found on `PATH`, skip gracefully with a structured warning.
- If available, run in a constrained way (timeouts, minimal flags, no retries by default).
- Prefer stable parsing; otherwise store raw output and extract patterns opportunistically.
- Use extracted patterns to boost/re-rank permutation candidates rather than being required for baseline operation.

## Google Dorks (Generation + Execution via SerpAPI)

### Dork Generator Inputs

- Full name variants:
  - `"First Last"`
  - `"Last, First"`
  - `"F. Last"` (lower weight)
- `--keywords` context (optional): comma-separated list (e.g., `software, engineer, berlin`).
- Top N permutations (recommended: 5) from the sorted permutation list.

### Query Strategies (per site)

1) **Exact Name**

`site:{domain} "First Last"`

2) **Contextual Name (if --keywords provided)**

Append a grouped OR-clause:

`site:{domain} "First Last" ("software" OR "engineer" OR "berlin")`

3) **Handle Discovery (bridge permutations & dorks)**

Use top permutations to search for handles efficiently:

`site:{domain} ("perm1" OR "perm2" OR "perm3" OR "perm4" OR "perm5")`

Also include URL-focused variants where appropriate:

- Instagram: `site:instagram.com inurl:perm1`
- (Optional future) Twitter/X: `site:twitter.com "perm1"` / `site:x.com "perm1"`

### SerpAPI Executor

- Read API key from env: `SERPAPI_API_KEY` (required when `--dorks` is used without `--dry-run`).
- Add a small delay between queries (e.g., `time.sleep(1)`) for local stability.
- Artifact naming:
  - `runs/<run_id>/raw/serpapi_<site>_<query_hash>.json`
- Summaries should include top URLs/titles/snippets and SerpAPI metadata for provenance.

### Safety Controls

- Default `--dorks-limit` should be conservative (suggestion: `1`).
- Print estimated credit cost before executing (unless `--dry-run`).
- `--dry-run` prints generated queries and estimated cost without calling SerpAPI.

