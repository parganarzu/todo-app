from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Button, Label, ListView, ListItem
from textual.containers import Vertical, Horizontal
from textual import on
import json
import os

DATA_FILE = "todos.json"


def load_todos() -> list[dict]:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_todos(todos: list[dict]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)


class TodoItem(ListItem):
    def __init__(self, todo_id: int, text: str, done: bool) -> None:
        super().__init__()
        self.todo_id = todo_id
        self.todo_text = text
        self.done = done

    def compose(self) -> ComposeResult:
        status = "✅" if self.done else "⬜"
        yield Label(f"{status}  {self.todo_text}", id=f"label-{self.todo_id}")


class TodoApp(App):
    def __init__(self) -> None:
        super().__init__()
        self.todos: list[dict] = []

    CSS = """
    Screen {
        background: $surface;
    }

    #main {
        padding: 1 2;
        height: 1fr;
    }

    #title {
        text-align: center;
        color: $accent;
        text-style: bold;
        padding: 1 0;
        height: 3;
    }

    #input-row {
        height: 5;
        padding: 1 0;
    }

    #new-todo {
        width: 1fr;
        margin-right: 1;
    }

    #add-btn {
        width: 12;
        background: $success;
    }

    #todo-list {
        height: 1fr;
        border: solid $accent;
        padding: 0 1;
    }

    #action-row {
        height: 5;
        padding: 1 0;
    }

    #done-btn {
        width: 1fr;
        background: $primary;
        margin-right: 1;
    }

    #delete-btn {
        width: 1fr;
        background: $error;
    }

    #status {
        height: 2;
        color: $text-muted;
        text-align: center;
    }

    ListItem {
        padding: 0 1;
    }

    ListItem:hover {
        background: $boost;
    }

    ListItem.--highlight {
        background: $accent 20%;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "delete_selected", "Delete"),
        ("space", "toggle_done", "Done"),
    ]

    def on_mount(self) -> None:
        self.todos = load_todos()
        lv = self.query_one("#todo-list", ListView)
        for t in self.todos:
            lv.append(TodoItem(t["id"], t["text"], t["done"]))
        self.query_one("#new-todo", Input).focus()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="main"):
            yield Label("📝  Todo App", id="title")
            with Horizontal(id="input-row"):
                yield Input(placeholder="Add new task...", id="new-todo")
                yield Button("➕ Add", id="add-btn", variant="success")
            yield ListView(id="todo-list")
            with Horizontal(id="action-row"):
                yield Button("✅ Done", id="done-btn", variant="primary")
                yield Button("🗑  Delete", id="delete-btn", variant="error")
            yield Label(self._status_text(), id="status")
        yield Footer()

    def _status_text(self) -> str:
        total = len(self.todos)
        done = sum(1 for t in self.todos if t["done"])
        return f"Total: {total}  |  Done: {done}  |  Pending: {total - done}"

    def _next_id(self) -> int:
        return max((t["id"] for t in self.todos), default=0) + 1

    def _refresh_status(self) -> None:
        self.query_one("#status", Label).update(self._status_text())

    def _selected_todo(self) -> dict | None:
        lv = self.query_one("#todo-list", ListView)
        if lv.highlighted_child is None:
            return None
        todo_id = lv.highlighted_child.todo_id  # type: ignore[attr-defined]
        return next((t for t in self.todos if t["id"] == todo_id), None)

    @on(Button.Pressed, "#add-btn")
    @on(Input.Submitted, "#new-todo")
    def add_todo(self) -> None:
        inp = self.query_one("#new-todo", Input)
        text = inp.value.strip()
        if not text:
            return
        new_todo = {"id": self._next_id(), "text": text, "done": False}
        self.todos.append(new_todo)
        save_todos(self.todos)
        self.query_one("#todo-list", ListView).append(
            TodoItem(new_todo["id"], new_todo["text"], new_todo["done"])
        )
        inp.value = ""
        inp.focus()
        self._refresh_status()

    @on(Button.Pressed, "#done-btn")
    def action_toggle_done(self) -> None:
        lv = self.query_one("#todo-list", ListView)
        item = lv.highlighted_child
        if item is None:
            return
        todo = next((t for t in self.todos if t["id"] == item.todo_id), None)  # type: ignore[attr-defined]
        if todo is None:
            return
        todo["done"] = not todo["done"]
        save_todos(self.todos)
        status = "✅" if todo["done"] else "⬜"
        item.query_one(Label).update(f"{status}  {item.todo_text}")  # type: ignore[attr-defined]
        self._refresh_status()

    @on(Button.Pressed, "#delete-btn")
    def action_delete_selected(self) -> None:
        lv = self.query_one("#todo-list", ListView)
        item = lv.highlighted_child
        if item is None:
            return
        self.todos = [t for t in self.todos if t["id"] != item.todo_id]  # type: ignore[attr-defined]
        save_todos(self.todos)
        item.remove()
        self._refresh_status()


if __name__ == "__main__":
    TodoApp().run()
