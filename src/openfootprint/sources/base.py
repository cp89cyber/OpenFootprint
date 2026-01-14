from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RequestSpec:
    url: str
    input_type: str
    headers: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Source:
    source_id: str
    name: str
    category: str
    supported_inputs: set[str]
    build_requests: callable
    parse: callable
