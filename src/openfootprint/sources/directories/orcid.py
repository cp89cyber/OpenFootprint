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
