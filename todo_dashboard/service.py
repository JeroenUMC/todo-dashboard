from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

from todo_dashboard.models import ParseWarning, TodoItem
from todo_dashboard.parser import parse_workspace

PRIORITY_RANK = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "UNKNOWN": 3}
STATUS_RANK = {"OPEN": 0, "IN PROGRESS": 1, "CLOSED": 2, "UNKNOWN": 3}


@dataclass(frozen=True)
class DashboardData:
    items: list[TodoItem]
    warnings: list[ParseWarning]


def _source_modified_at(workspace_root: Path, item: TodoItem) -> datetime | None:
    try:
        return datetime.fromtimestamp((workspace_root / item.source_path).stat().st_mtime)
    except OSError:
        return None


def _age_in_days(workspace_root: Path, item: TodoItem, reference_datetime: datetime) -> float | None:
    modified_at = _source_modified_at(workspace_root, item)
    if modified_at is None:
        return None
    age_days = (reference_datetime - modified_at).total_seconds() / 86400
    return max(age_days, 0.0)


def _oldest_item_summary(
    workspace_root: Path,
    items: list[TodoItem],
    reference_datetime: datetime,
) -> dict[str, object] | None:
    candidates: list[tuple[float, TodoItem]] = []
    for item in items:
        age_days = _age_in_days(workspace_root, item, reference_datetime)
        if age_days is not None:
            candidates.append((age_days, item))

    if not candidates:
        return None

    age_days, item = max(candidates, key=lambda pair: (pair[0], pair[1].source_path, pair[1].source_line))
    return {
        "title": item.title,
        "project": item.project,
        "source_path": item.source_path,
        "source_line": item.source_line,
        "age_days": round(age_days, 1),
    }


def _average_age_days(workspace_root: Path, items: list[TodoItem], reference_datetime: datetime) -> float | None:
    ages = [
        age_days
        for item in items
        if (age_days := _age_in_days(workspace_root, item, reference_datetime)) is not None
    ]
    if not ages:
        return None
    return round(mean(ages), 1)


def _most_common_value(values: list[str]) -> tuple[str, int]:
    if not values:
        return "UNKNOWN", 0
    counts = Counter(values)
    value, count = max(counts.items(), key=lambda pair: (pair[1], pair[0]))
    return value, count


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


def status_statistics(
    workspace_root: Path,
    items: list[TodoItem],
    *,
    reference_date: date | None = None,
    reference_datetime: datetime | None = None,
) -> dict[str, dict[str, object]]:
    current_datetime = reference_datetime or datetime.now()
    current_date = reference_date or current_datetime.date()
    week_start = current_date - timedelta(days=current_date.weekday())

    closed_items = [item for item in items if item.status == "CLOSED"]
    open_items = [item for item in items if item.status == "OPEN"]
    in_progress_items = [item for item in items if item.status == "IN PROGRESS"]

    closed_with_dates = [item for item in closed_items if item.closed_at is not None]
    closed_today = sum(1 for item in closed_with_dates if item.closed_at == current_date)
    closed_this_week = sum(1 for item in closed_with_dates if week_start <= item.closed_at <= current_date)
    closed_this_month = sum(
        1
        for item in closed_with_dates
        if item.closed_at.year == current_date.year and item.closed_at.month == current_date.month
    )

    most_common_type, most_common_type_count = _most_common_value([item.item_type for item in closed_items])
    open_total = len(open_items)
    closed_total = len(closed_items)

    return {
        "closed": {
            "metrics": [
                {"label": "Closed total", "value": closed_total},
                {"label": "Closed today", "value": closed_today},
                {"label": "Closed this week", "value": closed_this_week},
                {"label": "Closed this month", "value": closed_this_month},
                {"label": "Closed without CLOSED_AT", "value": closed_total - len(closed_with_dates)},
            ],
            "highlight": {"label": "Most common type", "value": most_common_type, "count": most_common_type_count},
            "note": "Closed timing uses CLOSED_AT. Missing dates are skipped from time buckets.",
        },
        "open": {
            "metrics": [
                {"label": "Open total", "value": open_total},
                {"label": "Open vs closed ratio", "value": f"{open_total}:{closed_total}"},
            ],
            "highlight": _oldest_item_summary(workspace_root, open_items, current_datetime),
            "note": "Oldest open item uses source file age as a simple approximation.",
        },
        "in_progress": {
            "metrics": [
                {"label": "In progress total", "value": len(in_progress_items)},
                {"label": "Average time open (days)", "value": _average_age_days(workspace_root, in_progress_items, current_datetime)},
            ],
            "highlight": _oldest_item_summary(workspace_root, in_progress_items, current_datetime),
            "note": "Ages are approximate and based on source file modification time.",
        },
    }
