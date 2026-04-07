from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from todo_dashboard.models import ParseWarning, TodoItem
from todo_dashboard.parser import parse_workspace

PRIORITY_RANK = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "UNKNOWN": 3}
STATUS_RANK = {"OPEN": 0, "IN PROGRESS": 1, "CLOSED": 2, "UNKNOWN": 3}


@dataclass(frozen=True)
class DashboardData:
    items: list[TodoItem]
    warnings: list[ParseWarning]


def load_dashboard_data(workspace_root: Path) -> DashboardData:
    items, warnings = parse_workspace(workspace_root)
    return DashboardData(items=items, warnings=warnings)


def filter_items(
    items: list[TodoItem],
    *,
    status: str | None = None,
    priority: str | None = None,
    item_type: str | None = None,
    assignee: str | None = None,
    project: str | None = None,
    query: str | None = None,
) -> list[TodoItem]:
    filtered = items

    if status:
        target = status.strip().upper()
        filtered = [item for item in filtered if item.status == target]
    if priority:
        target = priority.strip().upper()
        filtered = [item for item in filtered if item.priority == target]
    if item_type:
        target = item_type.strip().upper()
        filtered = [item for item in filtered if item.item_type == target]
    if assignee:
        target = assignee.strip().upper()
        filtered = [item for item in filtered if target in item.assignee]
    if project:
        target = project.strip().lower()
        filtered = [item for item in filtered if item.project.lower() == target]
    if query:
        needle = query.strip().lower()
        filtered = [item for item in filtered if needle in item.title.lower()]

    return filtered


def sort_items(items: list[TodoItem], sort_by: str, order: str) -> list[TodoItem]:
    reverse = order.lower() == "desc"

    if sort_by == "priority":
        key = lambda item: PRIORITY_RANK.get(item.priority, 3)
    elif sort_by == "status":
        key = lambda item: STATUS_RANK.get(item.status, 3)
    elif sort_by == "type":
        key = lambda item: item.item_type
    elif sort_by == "assignee":
        key = lambda item: item.assignee
    elif sort_by == "project":
        key = lambda item: item.project.lower()
    else:
        key = lambda item: item.title.lower()

    return sorted(items, key=key, reverse=reverse)


def status_counts(items: list[TodoItem]) -> dict[str, int]:
    counts = {"OPEN": 0, "IN PROGRESS": 0, "CLOSED": 0, "UNKNOWN": 0}
    for item in items:
        counts[item.status if item.status in counts else "UNKNOWN"] += 1
    counts["TOTAL"] = len(items)
    return counts


def facets(items: list[TodoItem]) -> dict[str, list[str]]:
    return {
        "priorities": sorted({item.priority for item in items}),
        "types": sorted({item.item_type for item in items}),
        "statuses": sorted({item.status for item in items}),
        "assignees": sorted({item.assignee for item in items}),
        "projects": sorted({item.project for item in items}),
    }
