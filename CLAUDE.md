# CLAUDE.md

## Setup & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python todo_app.py
```

## Architecture

Single file: `todo_app.py`. A terminal UI application built with the Textual framework.

- `TodoApp` — main application class
- `TodoItem` — list item widget
- Todos are persisted in `todos.json` (auto-created on first run)

## Keyboard Shortcuts

| Key     | Action             |
|---------|--------------------|
| `Space` | Toggle selected done |
| `D`     | Delete selected    |
| `Q`     | Quit               |
| `Enter` | Add new todo       |
