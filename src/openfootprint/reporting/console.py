from __future__ import annotations


def render_console(findings, sources, run_id) -> str:
    lines = [f"OpenFootprint run {run_id}", f"Sources: {', '.join(sources)}", "Findings:"]
    for finding in findings:
        lines.append(f"- {finding.source_id}: {finding.entity.display_name or finding.entity.entity_id}")
    return "\n".join(lines)
