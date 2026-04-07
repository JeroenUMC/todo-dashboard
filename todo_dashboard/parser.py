from __future__ import annotations

import re
from pathlib import Path

from todo_dashboard.models import ParseWarning, TodoItem

BRACKET_PATTERN = re.compile(r"\[(?P<key>[A-Za-z ]+):\s*(?P<value>[^\]]+)\]")


def discover_todo_files(workspace_root: Path) -> list[Path]:
    return sorted(workspace_root.rglob(".notes/todo.md"))


def parse_workspace(workspace_root: Path) -> tuple[list[TodoItem], list[ParseWarning]]:
    items: list[TodoItem] = []
    warnings: list[ParseWarning] = []

    for todo_file in discover_todo_files(workspace_root):
        file_items, file_warnings = parse_todo_file(todo_file, workspace_root)
        items.extend(file_items)
        warnings.extend(file_warnings)

    return items, warnings


def parse_todo_file(todo_file: Path, workspace_root: Path) -> tuple[list[TodoItem], list[ParseWarning]]:
    items: list[TodoItem] = []
    warnings: list[ParseWarning] = []
    project = derive_project_name(todo_file, workspace_root)
    relative_path = str(todo_file.relative_to(workspace_root)).replace("\\", "/")

    lines = todo_file.read_text(encoding="utf-8").splitlines()
    header_indexes = [idx for idx, line in enumerate(lines) if line.strip().startswith("### ")]

    for current_idx, header_idx in enumerate(header_indexes):
        next_idx = header_indexes[current_idx + 1] if current_idx + 1 < len(header_indexes) else len(lines)
        raw_header = lines[header_idx]
        stripped = raw_header.strip()
        line_no = header_idx + 1

        title = parse_title(stripped)
        metadata = parse_metadata(stripped)
        body_markdown = "\n".join(lines[header_idx + 1 : next_idx]).strip()

        priority = normalize_priority(metadata.get("PRIORITY"))
        item_type = normalize_type(metadata.get("TYPE"))
        status = normalize_status(metadata.get("STATUS"))
        assignee = normalize_assignee(metadata.get("ASSIGNEE") or metadata.get("ASSIGNEE_ALT"))

        if "ASSIGNEE" not in metadata and "ASSIGNEE_ALT" in metadata:
            warnings.append(
                ParseWarning(
                    source_path=relative_path,
                    source_line=line_no,
                    message="Assignee key uses non-canonical casing",
                    raw_line=stripped,
                )
            )

        missing_fields: list[str] = []
        if priority == "UNKNOWN":
            missing_fields.append("PRIORITY")
        if item_type == "UNKNOWN":
            missing_fields.append("TYPE")
        if status == "UNKNOWN":
            missing_fields.append("STATUS")
        if assignee == "UNKNOWN":
            missing_fields.append("ASSIGNEE")

        if missing_fields:
            warnings.append(
                ParseWarning(
                    source_path=relative_path,
                    source_line=line_no,
                    message=f"Missing or invalid fields: {', '.join(missing_fields)}",
                    raw_line=stripped,
                )
            )

        items.append(
            TodoItem(
                title=title,
                priority=priority,
                item_type=item_type,
                status=status,
                assignee=assignee,
                project=project,
                source_path=relative_path,
                source_line=line_no,
                body_markdown=body_markdown,
            )
        )

    return items, warnings


def derive_project_name(todo_file: Path, workspace_root: Path) -> str:
    notes_parent = todo_file.parent.parent
    if notes_parent == workspace_root:
        return "Global"
    return notes_parent.name


def parse_title(header_line: str) -> str:
    without_hashes = header_line[4:].strip()
    bracket_idx = without_hashes.find("[")
    if bracket_idx == -1:
        return without_hashes
    return without_hashes[:bracket_idx].strip()


def parse_metadata(header_line: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for match in BRACKET_PATTERN.finditer(header_line):
        raw_key = match.group("key").strip()
        value = match.group("value").strip()
        key_upper = raw_key.upper()
        if key_upper == "ASSIGNEE" and raw_key != "ASSIGNEE":
            metadata["ASSIGNEE_ALT"] = value
        elif key_upper == "ASSIGNEE":
            metadata["ASSIGNEE"] = value
        else:
            metadata[key_upper] = value
    return metadata


def normalize_priority(value: str | None) -> str:
    if not value:
        return "UNKNOWN"
    normalized = value.strip().upper()
    return normalized if normalized in {"LOW", "MEDIUM", "HIGH"} else "UNKNOWN"


def normalize_type(value: str | None) -> str:
    if not value:
        return "UNKNOWN"
    normalized = value.strip().upper()
    return normalized if normalized in {"BUG", "FEATURE", "REFACTOR", "RESEARCH", "MISC"} else "UNKNOWN"


def normalize_status(value: str | None) -> str:
    if not value:
        return "UNKNOWN"
    normalized = re.sub(r"\s+", " ", value.strip().upper())
    normalized = normalized.replace("IN_PROGRESS", "IN PROGRESS")
    return normalized if normalized in {"OPEN", "IN PROGRESS", "CLOSED"} else "UNKNOWN"


def normalize_assignee(value: str | None) -> str:
    if not value:
        return "UNKNOWN"
    normalized = re.sub(r"\s+", " ", value.strip()).upper()
    return normalized if normalized else "UNKNOWN"
