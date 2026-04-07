# Todo Dashboard

Read-only local web app that aggregates every workspace `.notes/todo.md` into one filterable dashboard.

## Features

- Aggregates all `.notes/todo.md` files recursively from a workspace root.
- Table columns: title, priority, type, status, assignee.
- Filters: status, priority, type, assignee, project, search text.
- Summary cards for OPEN / IN PROGRESS / CLOSED / TOTAL.
- Tolerant parsing: malformed or missing fields are included as `UNKNOWN`.
- Parse diagnostics panel so format issues are visible.
- Read-only by design (no write-back to markdown files).

## Project Structure Assumptions

The dashboard assumes a layered workspace where each project/repository may have its own `.notes/` folder.
It scans recursively from `--workspace-root` and includes every `.notes/todo.md` it finds.

Illustrative example (not a required exact layout):

```text
global_workspace
├── project_1/
│   ├── repository_1/
│   │   └── .notes/
│   │       └── todo.md
│   └── repository_2/
│       └── .notes/
│           └── todo.md
├── project_2/
│   └── .notes/
│       └── todo.md
└── .notes/
	└── todo.md
```

Parsing assumptions for each todo entry:

- Todo items are markdown headers starting with `###`.
- Metadata is expected in bracket format `[PRIORITY: ...] [TYPE: ...] [STATUS: ...] [ASSIGNEE: ...]`.
- Missing or malformed metadata is kept visible and normalized to `UNKNOWN`. See the Parse diagnostics panel for details on any issues.

## Setup

```powershell
cd tools/todo-dashboard
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
pip install -e ".[dev]"
```

## Run

From your global_workspace, run the dashboard with:

```powershell
python -m todo_dashboard --workspace-root ../.. --open-browser
```

Or with installed script:

```powershell
todo-dashboard --workspace-root ../.. --open-browser
```

Default `--workspace-root` points to this repository's top-level workspace (`global_workspace`) when run from this project.

## CLI options

```powershell
python -m todo_dashboard --help
```

Key flags:

- `--workspace-root`: root folder to scan for `.notes/todo.md`.
- `--host`: bind host (default `127.0.0.1`).
- `--port`: bind port (default `8008`).
- `--open-browser`: open dashboard in default browser.

## Test

```powershell
pytest
```
