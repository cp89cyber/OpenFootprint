from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlannedRequest:
    source_id: str
    url: str
    input_type: str
    headers: dict[str, str]
    transport: str


def build_plan(inputs, registry) -> list[PlannedRequest]:
    present = {key for key, value in inputs.__dict__.items() if value}
    plan = []
    for source in registry.for_inputs(present):
        for request in source.build_requests(inputs):
            plan.append(
                PlannedRequest(
                    source_id=source.source_id,
                    url=request.url,
                    input_type=request.input_type,
                    headers=request.headers,
                    transport=request.transport,
                )
            )
    return plan
