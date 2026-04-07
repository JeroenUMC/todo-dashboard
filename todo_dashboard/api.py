from __future__ import annotations

import html
from pathlib import Path

import markdown
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from todo_dashboard.config import default_workspace_root
from todo_dashboard.service import facets, filter_items, load_dashboard_data, sort_items, status_counts

VALID_SORT_FIELDS = {"title", "priority", "status", "type", "assignee", "project"}
VALID_ORDERS = {"asc", "desc"}


def markdown_preview(text: str) -> str:
    if not text.strip():
        text = "_No additional details provided._"
    # Escape raw HTML from source markdown while preserving markdown formatting.
    escaped = html.escape(text)
    return markdown.markdown(escaped, extensions=["extra", "sane_lists", "nl2br"], output_format="html5")


def create_app(workspace_root: Path | None = None) -> FastAPI:
    app = FastAPI(title="Todo Dashboard", version="0.1.0")
    resolved_workspace = workspace_root or default_workspace_root()

    package_dir = Path(__file__).resolve().parent
    templates = Jinja2Templates(directory=str(package_dir / "templates"))
    templates.env.filters["markdown_preview"] = markdown_preview
    app.mount("/static", StaticFiles(directory=str(package_dir / "static")), name="static")

    def _load_and_query(
        status: str | None,
        priority: str | None,
        item_type: str | None,
        assignee: str | None,
        project: str | None,
        q: str | None,
        sort: str,
        order: str,
    ):
        if sort not in VALID_SORT_FIELDS:
            raise HTTPException(status_code=400, detail=f"Invalid sort field: {sort}")
        if order not in VALID_ORDERS:
            raise HTTPException(status_code=400, detail=f"Invalid order: {order}")

        data = load_dashboard_data(resolved_workspace)
        filtered = filter_items(
            data.items,
            status=status,
            priority=priority,
            item_type=item_type,
            assignee=assignee,
            project=project,
            query=q,
        )

        sort_key = "item_type" if sort == "type" else sort
        sorted_items = sort_items(filtered, sort_by=sort_key, order=order)

        return data, sorted_items

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/todos")
    def api_todos(
        status: str | None = None,
        priority: str | None = None,
        item_type: str | None = Query(default=None, alias="type"),
        assignee: str | None = None,
        project: str | None = None,
        q: str | None = None,
        sort: str = "priority",
        order: str = "asc",
    ) -> dict[str, object]:
        data, sorted_items = _load_and_query(status, priority, item_type, assignee, project, q, sort, order)
        return {
            "total": len(sorted_items),
            "items": [
                {
                    "title": item.title,
                    "priority": item.priority,
                    "type": item.item_type,
                    "status": item.status,
                    "assignee": item.assignee,
                    "project": item.project,
                    "source_path": item.source_path,
                    "source_line": item.source_line,
                    "body_markdown": item.body_markdown,
                }
                for item in sorted_items
            ],
            "counts": status_counts(data.items),
        }

    @app.get("/api/facets")
    def api_facets() -> dict[str, list[str]]:
        data = load_dashboard_data(resolved_workspace)
        return facets(data.items)

    @app.get("/api/diagnostics")
    def api_diagnostics() -> dict[str, object]:
        data = load_dashboard_data(resolved_workspace)
        return {
            "total_warnings": len(data.warnings),
            "warnings": [
                {
                    "source_path": warning.source_path,
                    "source_line": warning.source_line,
                    "message": warning.message,
                    "raw_line": warning.raw_line,
                }
                for warning in data.warnings
            ],
        }

    @app.get("/", response_class=HTMLResponse)
    def dashboard(
        request: Request,
        status: str | None = None,
        priority: str | None = None,
        item_type: str | None = Query(default=None, alias="type"),
        assignee: str | None = None,
        project: str | None = None,
        q: str | None = None,
        sort: str = "priority",
        order: str = "asc",
    ) -> HTMLResponse:
        data, sorted_items = _load_and_query(status, priority, item_type, assignee, project, q, sort, order)
        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "items": sorted_items,
                "counts": status_counts(data.items),
                "filtered_count": len(sorted_items),
                "facets": facets(data.items),
                "warnings": data.warnings,
                "filters": {
                    "status": status or "",
                    "priority": priority or "",
                    "type": item_type or "",
                    "assignee": assignee or "",
                    "project": project or "",
                    "q": q or "",
                    "sort": sort,
                    "order": order,
                },
            },
        )

    return app
