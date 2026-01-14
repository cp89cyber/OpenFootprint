from __future__ import annotations

import json
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
