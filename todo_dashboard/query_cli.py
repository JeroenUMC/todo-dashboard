"""
Lightweight CLI for querying workspace todos.

Usage:
    python -m todo_dashboard.query_cli [options]

Examples:
    python -m todo_dashboard.query_cli --status OPEN --priority HIGH
    python -m todo_dashboard.query_cli --type BUG --format json
    python -m todo_dashboard.query_cli --query FEAT-1 --format json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from todo_dashboard.config import default_workspace_root
from todo_dashboard.service import filter_items, load_dashboard_data, sort_items


def _item_to_dict(item) -> dict:
    return {
        "title": item.title,
        "priority": item.priority,
        "type": item.item_type,
        "status": item.status,
        "assignee": item.assignee,
        "closed_at": item.closed_at.isoformat() if item.closed_at else None,
        "project": item.project,
        "source_path": item.source_path,
        "source_line": item.source_line,
        "body_markdown": item.body_markdown,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Query workspace todos")
    parser.add_argument("--workspace-root", type=Path, default=None)
    parser.add_argument("--priority", help="Filter by priority (HIGH, MEDIUM, LOW)")
    parser.add_argument("--type", dest="item_type", help="Filter by type (BUG, FEATURE, ...)")
    parser.add_argument("--status", help="Filter by status (OPEN, CLOSED, IN PROGRESS)")
    parser.add_argument("--assignee", help="Filter by assignee (AI, HUMAN, ...)")
    parser.add_argument("--project", help="Filter by project name (exact, case-insensitive)")
    parser.add_argument("--query", help="Substring search in title")
    parser.add_argument(
        "--sort-by",
        default="priority",
        choices=["priority", "status", "type", "assignee", "project", "title"],
    )
    parser.add_argument("--order", default="asc", choices=["asc", "desc"])
    parser.add_argument("--format", dest="fmt", default="text", choices=["text", "json"])
    args = parser.parse_args()

    workspace_root = args.workspace_root or default_workspace_root()
    data = load_dashboard_data(workspace_root)

    items = filter_items(
        data.items,
        status=args.status,
        priority=args.priority,
        item_type=args.item_type,
        assignee=args.assignee,
        project=args.project,
        query=args.query,
    )
    items = sort_items(items, args.sort_by, args.order)

    if args.fmt == "json":
        print(json.dumps([_item_to_dict(i) for i in items], indent=2))
        return

    # Text output — compact, one line per item
    print(f"Found {len(items)} item(s).")
    for item in items:
        print(f"[{item.priority}/{item.item_type}/{item.status}] {item.title} — {item.project} ({item.source_path}:{item.source_line})")


if __name__ == "__main__":
    sys.exit(main())
