from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Evidence:
    source_id: str
    request_url: str
    raw_path: str
    raw_hash: str
    parser_id: str
    match_excerpt: str | None
    fetched_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "request_url": self.request_url,
            "raw_path": self.raw_path,
            "raw_hash": self.raw_hash,
            "parser_id": self.parser_id,
            "match_excerpt": self.match_excerpt,
            "fetched_at": self.fetched_at,
        }


@dataclass(frozen=True)
class Identifier:
    type: str
    value: str
    evidence: list[Evidence] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "value": self.value,
            "evidence": [ev.to_dict() for ev in self.evidence],
        }


@dataclass(frozen=True)
class Entity:
    entity_id: str
    display_name: str | None
    profile_urls: list[str] = field(default_factory=list)
    identifiers: list[Identifier] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "display_name": self.display_name,
            "profile_urls": self.profile_urls,
            "identifiers": [ident.to_dict() for ident in self.identifiers],
            "evidence": [ev.to_dict() for ev in self.evidence],
        }


@dataclass(frozen=True)
class Artifact:
    url: str
    title: str | None
    snippet: str | None
    evidence: list[Evidence] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "snippet": self.snippet,
            "evidence": [ev.to_dict() for ev in self.evidence],
        }


@dataclass(frozen=True)
class Finding:
    source_id: str
    type: str
    entity: Entity
    artifacts: list[Artifact] = field(default_factory=list)
    confidence: str = "medium"

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "type": self.type,
            "entity": self.entity.to_dict(),
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class RunManifest:
    run_id: str
    inputs: dict[str, str | None]
    sources: list[str]
    started_at: str
    finished_at: str | None
    config: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "inputs": self.inputs,
            "sources": self.sources,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "config": self.config,
        }
