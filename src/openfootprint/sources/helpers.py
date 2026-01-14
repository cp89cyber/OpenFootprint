from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from openfootprint.core.schema import Evidence, Identifier, Entity, Finding
from openfootprint.sources.base import RequestSpec, Source
from openfootprint.sources.parsers import extract_title


@dataclass(frozen=True)
class HtmlProfileSource:
    source_id: str
    name: str
    category: str
    url_template: str

    def build_requests(self, inputs) -> list[RequestSpec]:
        if not inputs.username:
            return []
        return [RequestSpec(url=self.url_template.format(username=inputs.username), input_type="username")]

    def parse(self, result, inputs, raw_info: list[tuple[str, str]]) -> list[Finding]:
        if result.status_code != 200 or not result.content:
            return []
        html = result.content.decode("utf-8", errors="replace")
        title = extract_title(html)
        fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        evidence = []
        for raw_path, raw_hash in raw_info:
            evidence.append(
                Evidence(
                    source_id=self.source_id,
                    request_url=result.url,
                    raw_path=raw_path,
                    raw_hash=raw_hash,
                    parser_id=f"{self.source_id}.profile",
                    match_excerpt=title,
                    fetched_at=fetched_at,
                )
            )
        identifier = Identifier(type="username", value=inputs.username, evidence=evidence)
        entity = Entity(
            entity_id=f"{self.source_id}:{inputs.username}",
            display_name=title,
            profile_urls=[result.url],
            identifiers=[identifier],
            evidence=evidence,
        )
        return [Finding(source_id=self.source_id, type="profile", entity=entity, artifacts=[], confidence="medium")]


def make_html_profile_source(source_id: str, name: str, category: str, url_template: str) -> Source:
    helper = HtmlProfileSource(source_id, name, category, url_template)
    return Source(
        source_id=source_id,
        name=name,
        category=category,
        supported_inputs={"username"},
        build_requests=helper.build_requests,
        parse=helper.parse,
    )
