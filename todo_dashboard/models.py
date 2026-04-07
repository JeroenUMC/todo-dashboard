from __future__ import annotations

from dataclasses import dataclass


VALID_PRIORITIES = {"LOW", "MEDIUM", "HIGH"}
VALID_TYPES = {"BUG", "FEATURE", "REFACTOR", "RESEARCH", "MISC"}
VALID_STATUSES = {"OPEN", "IN PROGRESS", "CLOSED"}


@dataclass(frozen=True)
class TodoItem:
    title: str
    priority: str
    item_type: str
    status: str
    assignee: str
    project: str
    source_path: str
    source_line: int
    body_markdown: str


@dataclass(frozen=True)
class ParseWarning:
    source_path: str
    source_line: int
    message: str
    raw_line: str
