from __future__ import annotations

import json


def render_json(findings, sources, run_id) -> str:
    payload = {
        "run_id": run_id,
        "sources": sources,
        "findings": [finding.to_dict() for finding in findings],
    }
    return json.dumps(payload, indent=2, sort_keys=True)
