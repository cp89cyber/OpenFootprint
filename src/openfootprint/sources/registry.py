from __future__ import annotations

from dataclasses import dataclass

from .base import Source


@dataclass
class SourceRegistry:
    sources: list[Source]

    def for_inputs(self, inputs: set[str]) -> list[Source]:
        return [source for source in self.sources if source.supported_inputs & inputs]

    def list_sources(self) -> list[Source]:
        return sorted(self.sources, key=lambda s: s.source_id)

    def get(self, source_id: str) -> Source | None:
        for source in self.sources:
            if source.source_id == source_id:
                return source
        return None
