#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re

ALIAS_DOCUMENT_NAMES = [
    "MASTER_CONTEXT.md",
    "ARCHITECTURE.md",
    "TASKS.md",
    "PROGRESS.md",
    "TESTING.md",
]

LOCAL_SUFFIXES = (
    ".md",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".txt",
    ".tsv",
)

MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
CODE_SPAN_RE = re.compile(r"`([^`\n]+)`")


def normalize_reference(value: str) -> str:
    ref = value.strip().strip("<>")
    ref = ref.split("#", 1)[0].split("?", 1)[0].strip()
    ref = ref.replace("\\", "/")
    while ref.startswith("./"):
        ref = ref[2:]
    return ref


def is_external_reference(ref: str) -> bool:
    lowered = ref.lower()
    return (
        not ref
        or lowered.startswith(("http://", "https://", "mailto:", "tel:", "#"))
        or lowered.startswith("app://")
    )


def looks_like_local_reference(ref: str) -> bool:
    if is_external_reference(ref):
        return False
    if ref.endswith("/"):
        return True
    if ref.lower().endswith(LOCAL_SUFFIXES):
        return True
    return "/" in ref and " " not in ref


def candidate_references_from_code_span(value: str) -> list[str]:
    refs: list[str] = []
    for item in re.split(r"[,;\s]+", value):
        ref = normalize_reference(item)
        if looks_like_local_reference(ref):
            refs.append(ref)
    return refs


def local_references(text: str) -> list[str]:
    refs: list[str] = []
    seen: set[str] = set()
    for match in MARKDOWN_LINK_RE.finditer(text):
        ref = normalize_reference(match.group(1))
        if looks_like_local_reference(ref) and ref not in seen:
            refs.append(ref)
            seen.add(ref)
    for match in CODE_SPAN_RE.finditer(text):
        for ref in candidate_references_from_code_span(match.group(1)):
            if ref not in seen:
                refs.append(ref)
                seen.add(ref)
    return refs


def target_exists(project: Path, ref: str) -> bool:
    target = project / ref
    if ref.endswith("/"):
        return target.is_dir()
    return target.exists()


def missing_targets_for_text(project: Path, alias_name: str, text: str) -> list[str]:
    errors: list[str] = []
    for ref in local_references(text):
        if not target_exists(project, ref):
            errors.append(f"{alias_name}: missing alias target: {ref}")
    return errors


def missing_alias_targets(project: Path) -> list[str]:
    errors: list[str] = []
    for name in ALIAS_DOCUMENT_NAMES:
        path = project / name
        if not path.is_file():
            continue
        errors.extend(missing_targets_for_text(project, name, path.read_text(encoding="utf-8")))
    return errors
