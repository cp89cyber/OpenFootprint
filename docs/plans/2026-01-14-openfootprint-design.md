# OpenFootprint MVP Design

Date: 2026-01-14

## Goals
- Provide a transparent, reproducible CLI for public-person OSINT lookups.
- Support inputs for username, email, phone, and real name.
- Query a small, curated set of public sources across developer, social, blogs/feeds, and people directories.
- Output console summary plus JSON and Markdown reports with evidence and provenance.
- Enforce ethics: no private services, no paywalls, no logins, robots.txt compliance.

## Non-Goals
- No scraping of private or paywalled services.
- No data enrichment beyond evidence-backed correlation.
- No automated deanonymization or hidden data collection.
- No live tests that hit third-party services in CI.

## MVP Scope
Inputs:
- `--username`, `--email`, `--phone`, `--name` (any combination).
- Normalize email casing, E.164 phone normalization, and name whitespace cleanup.

Output:
- Console summary with per-source status and key findings.
- JSON report for machine use.
- Markdown report for human review.

Initial source set (2-3 per category):
- Developer platforms: GitHub, GitLab, Codeberg.
- Social/community: Reddit, Hacker News, Mastodon (requires `user@instance`).
- Blogs/feeds: Dev.to, Medium, WordPress.com.
- People directories: Wikidata (SPARQL), ORCID, OpenAlex.

Notes:
- Sources can support a subset of inputs; username is expected to drive most queries.
- Email/phone are used for direct queries where supported and for matching within fetched content.

## Architecture
A minimal plugin architecture with explicit connectors per source:
- `sources/<category>/<source_id>.py` defines metadata and a small interface.
- Each connector implements `build_requests()`, `fetch()`, `parse()`, and `normalize()`.
- Core pipeline orchestrates lookup, storage, correlation, and reporting.

Core modules:
- `cli/` argument parsing, config loading, and command orchestration.
- `core/` pipeline, schema, correlation, rendering.
- `sources/` connectors by category.
- `storage/` run folder structure, raw artifacts, and manifests.
- `policies/` robots.txt checks, rate limits, and source allow/deny rules.

## Data Flow
1) Validate and normalize inputs.
2) Build a query plan per source based on supported inputs.
3) Fetch using a shared HTTP client with rate limits and retries.
4) Persist raw artifacts (HTTP response body, headers, URL, timestamp).
5) Parse and normalize findings into a common schema.
6) Correlate findings by shared identifiers and URLs.
7) Render console, JSON, and Markdown outputs.

## Unified Schema (MVP)
- `RunManifest`: run_id, inputs, sources_used, versions, timestamps.
- `Entity`: stable id, display name, profile urls, handles.
- `Identifier`: type (username/email/phone/name), value, evidence.
- `Artifact`: url, title, snippet, timestamps, evidence.
- `Evidence`: source_id, request_url, raw_hash, match_excerpt, parser_id.
- `Finding`: type, entity reference, confidence, evidence list.

## Reproducibility
- Each run creates `runs/<run_id>/` with:
  - `manifest.json`
  - `raw/` (fetched artifacts)
  - `normalized.json`
  - `report.md`
- All findings include evidence pointers to raw artifacts.

## Policy & Ethics
- Respect robots.txt; skip sources that disallow fetching.
- Identify tool in user-agent.
- No logins, no paywalls, no private or non-consensual datasets.
- Rate limits per source with sane defaults.
- Report includes a coverage table listing skipped/failed sources.

## Configuration
Config file (YAML or TOML):
- enabled sources, user-agent, timeouts, rate limits, output dir.
- allow/deny list for sources.
- optional per-source settings (API base, endpoints).

## CLI UX
Commands:
- `openfootprint lookup [--username ...] [--email ...] [--phone ...] [--name ...]`
- `openfootprint sources list`
- `openfootprint sources info <id>`
- `openfootprint plan --dry-run` to show query plan

Flags:
- `--config` for custom config path.
- `--output` to override run directory.
- `--dry-run` to skip fetch and only show planned requests.

## Error Handling
- Invalid inputs or config errors exit non-zero.
- Source fetch/parse errors are captured and reported, but do not abort the run.
- All errors recorded in the report and manifest for transparency.

## Testing Strategy
- Unit tests for normalization and schema validation.
- Fixture-based parser tests with saved public artifacts.
- Integration test that runs the pipeline against fixtures and compares JSON output.
- No live external requests in CI.

## Future Extensions
- Add more connectors and categories as opt-in.
- Pluggable correlation rules and scoring.
- Optional export to graph formats (GraphML, Neo4j CSV).
