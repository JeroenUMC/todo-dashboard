from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    workspace_root: Path


def default_workspace_root() -> Path:
    # cli.py lives in tools/todo-dashboard/todo_dashboard/
    # parents[3] resolves to global_workspace/
    return Path(__file__).resolve().parents[3]
