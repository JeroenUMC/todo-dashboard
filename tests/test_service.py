import os
from datetime import date, datetime, timedelta

from todo_dashboard.models import TodoItem
from todo_dashboard.service import facets, filter_items, sort_items, status_counts, status_statistics


def _sample_items() -> list[TodoItem]:
    return [
        TodoItem("A", "HIGH", "FEATURE", "OPEN", "AI", None, "Global", ".notes/todo.md", 1, "Body A"),
        TodoItem("B", "LOW", "RESEARCH", "CLOSED", "HUMAN", date(2026, 4, 6), "proj", "proj/.notes/todo.md", 2, "Body B"),
        TodoItem("C", "MEDIUM", "MISC", "IN PROGRESS", "AI + HUMAN", None, "proj", "proj/.notes/todo.md", 3, "Body C"),
    ]


def test_filter_items_combined():
    items = _sample_items()
    filtered = filter_items(items, status="OPEN", assignee="AI")
    assert len(filtered) == 1
    assert filtered[0].title == "A"


def test_sort_items_priority():
    items = _sample_items()
    sorted_items = sort_items(items, sort_by="priority", order="asc")
    assert [item.title for item in sorted_items] == ["A", "C", "B"]


def test_status_counts():
    counts = status_counts(_sample_items())
    assert counts["OPEN"] == 1
    assert counts["IN PROGRESS"] == 1
    assert counts["CLOSED"] == 1
    assert counts["TOTAL"] == 3


def test_facets_dynamic_discovery():
    """Verify facets dynamically discover values from items, including custom values."""
    items = [
        TodoItem("T1", "HIGH", "FEATURE", "OPEN", "AI", None, "proj1", ".notes/todo.md", 1, "Body"),
        TodoItem("T2", "CRITICAL", "INVESTIGATION", "BLOCKED", "HUMAN", None, "proj2", ".notes/todo.md", 2, "Body"),
        TodoItem("T3", "UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN", None, "proj1", ".notes/todo.md", 3, "Body"),
    ]

    result = facets(items)

    assert "HIGH" in result["priorities"]
    assert "CRITICAL" in result["priorities"]
    assert "UNKNOWN" in result["priorities"]

    assert "FEATURE" in result["types"]
    assert "INVESTIGATION" in result["types"]

    assert "OPEN" in result["statuses"]
    assert "BLOCKED" in result["statuses"]
    assert "UNKNOWN" in result["statuses"]

    assert "AI" in result["assignees"]
    assert "HUMAN" in result["assignees"]

    assert len(result["priorities"]) == 3
    assert len(result["types"]) == 3
    assert len(result["statuses"]) == 3


def test_status_statistics(tmp_path):
    workspace_root = tmp_path
    reference_date = date(2026, 4, 7)
    reference_datetime = datetime(2026, 4, 7, 12, 0, 0)

    open_file = workspace_root / "open_project" / ".notes" / "todo.md"
    in_progress_file = workspace_root / "progress_project" / ".notes" / "todo.md"
    closed_file = workspace_root / "closed_project" / ".notes" / "todo.md"

    for file_path, days_old in [
        (open_file, 2),
        (in_progress_file, 10),
        (closed_file, 4),
    ]:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("# Todo\n", encoding="utf-8")
        timestamp = (reference_datetime - timedelta(days=days_old)).timestamp()
        os.utime(file_path, (timestamp, timestamp))

    items = [
        TodoItem("Open item", "HIGH", "FEATURE", "OPEN", "AI", None, "open_project", "open_project/.notes/todo.md", 1, ""),
        TodoItem("In progress item", "LOW", "MISC", "IN PROGRESS", "HUMAN", None, "progress_project", "progress_project/.notes/todo.md", 1, ""),
        TodoItem("Closed today", "MEDIUM", "FEATURE", "CLOSED", "AI", reference_date, "closed_project", "closed_project/.notes/todo.md", 1, ""),
        TodoItem("Closed yesterday", "MEDIUM", "FEATURE", "CLOSED", "HUMAN", reference_date.replace(day=6), "closed_project", "closed_project/.notes/todo.md", 2, ""),
        TodoItem("Closed missing date", "LOW", "BUG", "CLOSED", "AI", None, "closed_project", "closed_project/.notes/todo.md", 3, ""),
    ]

    stats = status_statistics(workspace_root, items, reference_date=reference_date, reference_datetime=reference_datetime)

    assert stats["closed"]["metrics"][0]["value"] == 3
    assert stats["closed"]["metrics"][1]["value"] == 1
    assert stats["closed"]["metrics"][2]["value"] == 2
    assert stats["closed"]["metrics"][3]["value"] == 2
    assert stats["closed"]["metrics"][4]["value"] == 1
    assert stats["closed"]["highlight"]["value"] == "FEATURE"
    assert stats["closed"]["highlight"]["count"] == 2

    assert stats["open"]["metrics"][0]["value"] == 1
    assert stats["open"]["metrics"][1]["value"] == "1:3"
    assert stats["open"]["highlight"]["title"] == "Open item"
    assert stats["open"]["highlight"]["age_days"] == 2.0

    assert stats["in_progress"]["metrics"][0]["value"] == 1
    assert stats["in_progress"]["metrics"][1]["value"] == 10.0
    assert stats["in_progress"]["highlight"]["title"] == "In progress item"
    assert stats["in_progress"]["highlight"]["age_days"] == 10.0
