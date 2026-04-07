from datetime import date
from pathlib import Path

from todo_dashboard.parser import parse_todo_file


def test_parse_todo_file_tolerant(sample_file: Path):
    items, warnings = parse_todo_file(sample_file, sample_file.parents[2])

    assert len(items) == 6

    by_title = {item.title: item for item in items}
    assert by_title["TST-1: Valid open item"].status == "OPEN"
    assert by_title["TST-2: Alternate assignee casing"].assignee == "HUMAN"
    assert by_title["TST-2: Alternate assignee casing"].closed_at == date(2026, 4, 6)
    assert by_title["TST-3: Missing assignee"].assignee == "UNKNOWN"
    assert by_title["TST-4: Malformed status"].status == "BLOCKED"
    assert by_title["TST-5: Custom values"].priority == "CRITICAL"
    assert by_title["TST-5: Custom values"].item_type == "INVESTIGATION"
    assert by_title["TST-5: Custom values"].status == "CLOSED"
    assert by_title["TST-5: Custom values"].closed_at == date(2026, 4, 7)
    assert by_title["TST-6: Invalid closed date"].status == "CLOSED"
    assert by_title["TST-6: Invalid closed date"].closed_at is None
    assert by_title["TST-1: Valid open item"].body_markdown == "Some body text."
    assert by_title["TST-2: Alternate assignee casing"].body_markdown == ""

    assert len(warnings) >= 3


def test_parse_file_project_label(sample_file: Path):
    items, _ = parse_todo_file(sample_file, sample_file.parents[2])
    assert all(item.project == "tests" for item in items)
