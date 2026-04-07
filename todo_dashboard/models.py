from __future__ import annotations

from datetime import date
from dataclasses import dataclass


@dataclass(frozen=True)
class TodoItem:
    title: str
    priority: str
    item_type: str
    status: str
    assignee: str
    closed_at: date | None
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
