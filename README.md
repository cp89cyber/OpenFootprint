# OpenFootprint

Open-source, terminal OSINT tool for researching people using only public info. It aggregates and correlates open sources transparently and reproducibly, without scraping private services, bypassing paywalls, or collecting non-consensual data. Built for journalists, researchers, investigators, and developers to map a public digital footprint.

## Install (local)

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

## Usage

Run a lookup with any combination of identifiers:

```bash
openfootprint lookup --username alice --name "Alice Smith"
openfootprint lookup --email alice@example.com --phone "+1 415 555 0100"
```

List or inspect sources:

```bash
openfootprint sources list
openfootprint sources info github
```

Preview the query plan without fetching:

```bash
openfootprint plan --username alice
```

## Output

Each run creates a timestamped folder under `runs/` containing:
- `manifest.json` (inputs, sources, config)
- `raw/` (fetched artifacts)
- `report.json` (machine-readable results)
- `report.md` (human-readable report)

## Ethics and Constraints

OpenFootprint is designed for public information and transparency.

- No private services, no logins, no paywalls.
- Respect `robots.txt` and site terms.
- Rate-limited requests with clear user-agent.
- Evidence-first results with raw artifacts and provenance.
- No non-consensual collection or hidden enrichment.

Use responsibly and comply with applicable laws and terms of service.

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
