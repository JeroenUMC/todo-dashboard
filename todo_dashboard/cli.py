from __future__ import annotations

import argparse
import threading
import webbrowser
from pathlib import Path

import uvicorn

from todo_dashboard.api import create_app
from todo_dashboard.config import default_workspace_root


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local todo dashboard web app")
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=default_workspace_root(),
        help="Workspace root to scan for .notes/todo.md files",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind server")
    parser.add_argument("--port", type=int, default=8008, help="Port to bind server")
    parser.add_argument(
        "--open-browser",
        action="store_true",
        help="Open dashboard in default browser after startup",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    workspace_root = args.workspace_root.resolve()
    app = create_app(workspace_root=workspace_root)

    if args.open_browser:
        dashboard_url = f"http://{args.host}:{args.port}/"
        threading.Timer(0.7, lambda: webbrowser.open(dashboard_url)).start()

    uvicorn.run(app, host=args.host, port=args.port)
