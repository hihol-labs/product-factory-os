#!/usr/bin/env python3
from pathlib import Path
import argparse
from datetime import datetime, timezone
import json
import re


PLANNING_ARTIFACTS = [
    "DISCOVERY.md",
    "IDEA_SCORECARD.md",
    "VALIDATION_PLAN.md",
    "FEEDBACK_LOG.md",
    "ITERATION_REVIEW.md",
    "FUNNEL_MODEL.md",
    "ASSET_REGISTER.md",
    "CONTENT_BACKLOG.md",
    "MARKET_BRIEF.md",
    "ICP.md",
    "BUSINESS_MODEL.md",
    "GO_TO_MARKET.md",
    "LAUNCH_MATURITY_GATE.md",
    "SCALE_MOAT_REGISTER.md",
    "PRD.md",
    "PRODUCT_BLUEPRINT.md",
    "PROJECT_ARCHITECTURE.md",
    "PHASE_CONTEXT.md",
    "BUILD_PLAN.md",
    "EXECUTION_GRAPH.md",
    "IMPLEMENTATION_PLAN.md",
    "TEST_PLAN.md",
    "QUALITY_GATES.md",
]

KNOWLEDGE_ARTIFACTS = [
    "PFO_REPORT.md",
    "HANDOFF.md",
    ".codex-memory/MEMORY.md",
    ".codex-memory/LEARNINGS.md",
    ".codex-memory/LEARNING_PROPOSALS.json",
    ".codex-memory/events.jsonl",
    ".pfo/UNIT_CONTEXT_MANIFEST.json",
    ".pfo/EXECUTION_POLICY.json",
    ".pfo/PERMISSION_MATRIX.json",
    ".pfo/VERIFICATION_CONTRACT.json",
    ".pfo/TOOL_CAPABILITY_REGISTRY.json",
]


def load_state(project: Path) -> dict:
    path = project / ".codex-memory" / "STATE.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def save_state(project: Path, state: dict) -> None:
    path = project / ".codex-memory" / "STATE.json"
    if path.is_file():
        path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slug(value: str) -> str:
    item = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip().lower())
    item = re.sub(r"-{2,}", "-", item).strip("-")
    return item or "project"


def yaml_quote(value: object) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def note_name(source: str) -> str:
    path = Path(source)
    if path.name == "STATE.json":
        return "STATE"
    if path.suffix == ".json":
        return path.stem
    return path.stem


def frontmatter(project: Path, title: str, tags: list[str], source: str = "") -> str:
    lines = [
        "---",
        f"title: {yaml_quote(title)}",
        f"project: {yaml_quote(project.name)}",
        f"generated: {yaml_quote(now_iso())}",
        "tags:",
    ]
    for tag in tags:
        lines.append(f"  - {tag}")
    if source:
        lines.append(f"source: {yaml_quote(source)}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def strip_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + 5 :].lstrip()
    return text


def read_source(project: Path, source: str) -> str:
    path = project / source
    if path.suffix == ".json":
        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
            return "```json\n" + json.dumps(parsed, indent=2, ensure_ascii=False) + "\n```\n"
        except json.JSONDecodeError:
            return "```text\n" + path.read_text(encoding="utf-8") + "\n```\n"
    return strip_frontmatter(path.read_text(encoding="utf-8"))


def callout(kind: str, title: str, body: str) -> str:
    lines = str(body or "TBD").splitlines() or ["TBD"]
    quoted = "\n".join(f"> {line}" if line else ">" for line in lines)
    return f"> [!{kind}] {title}\n{quoted}\n"


def markdown_table(rows: list[tuple[str, str]]) -> str:
    if not rows:
        return "_None recorded._\n"
    body = "\n".join(f"| {name} | {value} |" for name, value in rows)
    return "| Item | Value |\n|---|---|\n" + body + "\n"


def write_note(out_dir: Path, project: Path, title: str, tags: list[str], source: str, body: str) -> Path:
    path = out_dir / f"{title}.md"
    path.write_text(frontmatter(project, title, tags, source) + body.rstrip() + "\n", encoding="utf-8")
    return path


def existing_sources(project: Path) -> list[tuple[str, str]]:
    sources: list[tuple[str, str]] = []
    for source in PLANNING_ARTIFACTS:
        if (project / source).is_file():
            sources.append((source, "planning"))
    for source in KNOWLEDGE_ARTIFACTS:
        if (project / source).is_file():
            sources.append((source, "knowledge"))
    for path in sorted((project / ".codex-memory").glob("session_*.md")):
        sources.append((str(path.relative_to(project)), "memory"))
    return sources


def write_artifact_notes(project: Path, out_dir: Path, sources: list[tuple[str, str]]) -> list[str]:
    notes = []
    for source, category in sources:
        title = note_name(source)
        body = f"""# {title}

{callout("info", "Source", f"Exported from `{source}`.")}
## PFO Links

- [[PROJECT_INDEX]]
- [[STATE]]
- [[DECISIONS]]
- [[GATES]]

## Source Content

{read_source(project, source)}
"""
        write_note(out_dir, project, title, [f"pfo/{category}", f"pfo/project/{slug(project.name)}"], source, body)
        notes.append(title)
    return notes


def write_state_notes(project: Path, out_dir: Path, state: dict) -> list[str]:
    blockers = state.get("blockers", []) if isinstance(state.get("blockers"), list) else []
    gate_results = state.get("gateResults", {}) if isinstance(state.get("gateResults"), dict) else {}
    decisions = state.get("decisionLog", []) if isinstance(state.get("decisionLog"), list) else []

    state_body = f"""# STATE

{callout("todo", "Next Action", str(state.get("nextAction", "") or "TBD"))}
{callout("warning", "Blockers", "\n".join(f"- {item}" for item in blockers) if blockers else "No blockers recorded.")}
## Current Status

{markdown_table([
    ("Stage", str(state.get("currentStage", ""))),
    ("Node", str(state.get("currentNode", ""))),
    ("Session", str(state.get("sessionState", ""))),
    ("Last Successful State", str(state.get("lastSuccessfulState", ""))),
])}

## Raw State

```json
{json.dumps(state, indent=2, ensure_ascii=False)}
```
"""
    write_note(out_dir, project, "STATE", ["pfo/state", f"pfo/project/{slug(project.name)}"], ".codex-memory/STATE.json", state_body)

    gate_rows = [(str(name), str(status or "PENDING")) for name, status in gate_results.items()]
    gates_body = f"""# GATES

{callout("info", "Gate Source", "Canonical gate details stay in [[QUALITY_GATES]] when that note exists.")}
{markdown_table(gate_rows)}
"""
    write_note(out_dir, project, "GATES", ["pfo/gates", f"pfo/project/{slug(project.name)}"], ".codex-memory/STATE.json", gates_body)

    if decisions:
        decision_items = []
        for item in decisions:
            if isinstance(item, dict):
                event = str(item.get("event", "decision"))
                details = ", ".join(f"{key}: {value}" for key, value in item.items() if key != "event" and value)
                decision_items.append(f"- **{event}**" + (f" - {details}" if details else ""))
            else:
                decision_items.append(f"- {item}")
        decisions_markdown = "\n".join(decision_items)
    else:
        decisions_markdown = "_No decisions recorded yet._"
    decisions_body = f"""# DECISIONS

{callout("tip", "Use", "Keep durable product and execution decisions linked back to planning notes.")}
{decisions_markdown}
"""
    write_note(out_dir, project, "DECISIONS", ["pfo/decisions", f"pfo/project/{slug(project.name)}"], ".codex-memory/STATE.json", decisions_body)
    return ["STATE", "GATES", "DECISIONS"]


def write_knowledge_graph(project: Path, out_dir: Path, notes: list[str], state: dict) -> list[str]:
    planning = [note_name(source) for source in PLANNING_ARTIFACTS if note_name(source) in notes]
    memory = [note_name(source) for source in KNOWLEDGE_ARTIFACTS if note_name(source) in notes]
    memory.extend(sorted(name for name in notes if name.startswith("session_")))
    edges = [
        ("PROJECT_INDEX", "STATE"),
        ("PROJECT_INDEX", "DECISIONS"),
        ("PROJECT_INDEX", "GATES"),
    ]
    for name in planning:
        edges.append(("PROJECT_INDEX", name))
    for name in memory:
        edges.append(("PROJECT_INDEX", name))
    for left, right in [
        ("PRODUCT_BLUEPRINT", "BUILD_PLAN"),
        ("BUILD_PLAN", "EXECUTION_GRAPH"),
        ("EXECUTION_GRAPH", "TEST_PLAN"),
        ("QUALITY_GATES", "GATES"),
        ("STATE", "HANDOFF"),
        ("STATE", "MEMORY"),
        ("DECISIONS", "PHASE_CONTEXT"),
        ("LEARNINGS", "ASSET_REGISTER"),
        ("LEARNINGS", "CONTENT_BACKLOG"),
    ]:
        if left in notes and right in notes:
            edges.append((left, right))

    node_names = sorted({item for edge in edges for item in edge})
    graph_lines = ["graph TD"]
    for left, right in edges:
        graph_lines.append(f'    {left}["{left}"] --> {right}["{right}"]')
    if node_names:
        graph_lines.append(f"    class {','.join(node_names)} internal-link;")
    graph_body = "# KNOWLEDGE_GRAPH\n\n```mermaid\n" + "\n".join(graph_lines) + "\n```\n"
    write_note(out_dir, project, "KNOWLEDGE_GRAPH", ["pfo/graph", f"pfo/project/{slug(project.name)}"], "", graph_body)

    planning_links = "\n".join(f"- [[{name}]]" for name in planning) or "- _No planning docs exported._"
    memory_links = "\n".join(f"- [[{name}]]" for name in memory) or "- _No memory docs exported._"
    index_body = f"""# {project.name}

{callout("summary", "Product Factory OS State", f"Stage: `{state.get('currentStage', '')}`\nNode: `{state.get('currentNode', '')}`\nNext action: {state.get('nextAction', '') or 'TBD'}")}
## Core

- [[STATE]]
- [[DECISIONS]]
- [[GATES]]
- ![[KNOWLEDGE_GRAPH]]

## Planning Docs

{planning_links}

## Memory And Handoff

{memory_links}
"""
    write_note(out_dir, project, "PROJECT_INDEX", ["pfo/project", "pfo/obsidian", f"pfo/project/{slug(project.name)}"], "", index_body)
    return ["PROJECT_INDEX", "KNOWLEDGE_GRAPH"]


def export_obsidian(project: Path, state: dict) -> Path:
    out_dir = project / ".pfo-integrations" / "obsidian"
    out_dir.mkdir(parents=True, exist_ok=True)
    sources = existing_sources(project)
    notes = write_artifact_notes(project, out_dir, sources)
    notes.extend(write_state_notes(project, out_dir, state))
    notes.extend(write_knowledge_graph(project, out_dir, notes, state))
    manifest = {
        "target": "obsidian",
        "project": project.name,
        "generated": now_iso(),
        "entrypoint": "PROJECT_INDEX.md",
        "notes": sorted(f"{name}.md" for name in set(notes)),
        "sourceArtifacts": [source for source, _ in sources] + [".codex-memory/STATE.json"],
        "rules": [
            "Canonical PFO docs remain the source of truth.",
            "Obsidian notes are export-only and may be regenerated.",
            "Use wikilinks for local vault navigation and Markdown links for external URLs.",
        ],
    }
    (out_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    state.setdefault("knowledgeLog", []).append(
        {
            "target": "obsidian",
            "path": ".pfo-integrations/obsidian/PROJECT_INDEX.md",
            "generatedAt": manifest["generated"],
            "noteCount": len(manifest["notes"]),
        }
    )
    artifacts = set(state.get("artifacts", []))
    artifacts.update(
        [
            ".pfo-integrations/obsidian/PROJECT_INDEX.md",
            ".pfo-integrations/obsidian/KNOWLEDGE_GRAPH.md",
            ".pfo-integrations/obsidian/MANIFEST.json",
        ]
    )
    state["artifacts"] = sorted(artifacts)
    write_state_notes(project, out_dir, state)
    save_state(project, state)
    return out_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Export PFO project state as integration payloads.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--target", choices=["github", "linear", "notion", "google-drive", "obsidian"], required=True)
    args = parser.parse_args()
    project = args.project.resolve()
    state = load_state(project)
    if args.target == "obsidian":
        out_dir = export_obsidian(project, state)
        print(f"OK: wrote Obsidian export to {out_dir}")
        return
    payload = {
        "target": args.target,
        "project": project.name,
        "currentStage": state.get("currentStage", ""),
        "currentNode": state.get("currentNode", ""),
        "nextAction": state.get("nextAction", ""),
        "blockers": state.get("blockers", []),
        "gateResults": state.get("gateResults", {}),
        "decisionLog": state.get("decisionLog", []),
    }
    out_dir = project / ".pfo-integrations"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"{args.target}.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK: wrote {out}")


if __name__ == "__main__":
    main()
