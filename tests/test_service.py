from todo_dashboard.models import TodoItem
from todo_dashboard.service import filter_items, sort_items, status_counts


def _sample_items() -> list[TodoItem]:
    return [
        TodoItem("A", "HIGH", "FEATURE", "OPEN", "AI", "Global", ".notes/todo.md", 1, "Body A"),
        TodoItem("B", "LOW", "RESEARCH", "CLOSED", "HUMAN", "proj", "proj/.notes/todo.md", 2, "Body B"),
        TodoItem("C", "MEDIUM", "MISC", "IN PROGRESS", "AI + HUMAN", "proj", "proj/.notes/todo.md", 3, "Body C"),
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
