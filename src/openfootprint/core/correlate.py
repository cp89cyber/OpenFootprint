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
    for _key, entities in buckets.items():
        primary = entities[0]
        profile_urls = []
        identifiers = []
        evidence = []
        for entity in entities:
            profile_urls.extend(entity.profile_urls)
            identifiers.extend(entity.identifiers)
            evidence.extend(entity.evidence)
        merged.append(
            Entity(
                entity_id=primary.entity_id,
                display_name=primary.display_name,
                profile_urls=profile_urls,
                identifiers=identifiers,
                evidence=evidence,
            )
        )
    return merged
