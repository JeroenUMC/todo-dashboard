from pathlib import Path

import pytest

from todo_dashboard.api import create_app


@pytest.fixture
def workspace_root(tmp_path: Path) -> Path:
    global_notes = tmp_path / ".notes"
    global_notes.mkdir(parents=True)
    (global_notes / "todo.md").write_text(
        "# Todo\n"
        "### GL-1: Root task [PRIORITY: HIGH] [TYPE: FEATURE] [STATUS: OPEN] [Assignee: AI]\n",
        encoding="utf-8",
    )

    project_notes = tmp_path / "project_alpha" / ".notes"
    project_notes.mkdir(parents=True)
    (project_notes / "todo.md").write_text(
        "# Todo\n"
        "### PA-1: Project task [PRIORITY: LOW] [TYPE: RESEARCH] [STATUS: CLOSED] [ASSIGNEE: HUMAN]\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def sample_file() -> Path:
    return Path(__file__).resolve().parent / "fixtures" / "sample_todo.md"


@pytest.fixture
def app(workspace_root: Path):
    return create_app(workspace_root)
