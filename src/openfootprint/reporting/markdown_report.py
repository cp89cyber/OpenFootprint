from __future__ import annotations


def render_markdown(findings, sources, run_id) -> str:
    lines = ["# OpenFootprint Report", "", f"Run: {run_id}", "", "## Sources", ""]
    for source in sources:
        lines.append(f"- {source}")
    lines.append("")
    lines.append("## Findings")
    for finding in findings:
        lines.append(f"- {finding.source_id}: {finding.entity.display_name or finding.entity.entity_id}")
    lines.append("")
    return "\n".join(lines)
