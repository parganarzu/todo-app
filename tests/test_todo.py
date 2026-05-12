import json
import pytest
from unittest.mock import patch, PropertyMock

from todo_app import load_todos, save_todos, TodoApp, TodoItem
from textual.widgets import Input, ListView


# ── Pure function tests ──────────────────────────────────────────────────────

def test_load_todos_missing_file(tmp_path):
    with patch("todo_app.DATA_FILE", str(tmp_path / "nonexistent.json")):
        assert load_todos() == []


def test_load_todos_existing_file(tmp_path):
    data = [{"id": 1, "text": "Buy milk", "done": False}]
    f = tmp_path / "todos.json"
    f.write_text(json.dumps(data), encoding="utf-8")
    with patch("todo_app.DATA_FILE", str(f)):
        assert load_todos() == data


def test_save_todos(tmp_path):
    data = [{"id": 1, "text": "Buy milk", "done": True}]
    f = tmp_path / "todos.json"
    with patch("todo_app.DATA_FILE", str(f)):
        save_todos(data)
    assert json.loads(f.read_text(encoding="utf-8")) == data


def test_next_id_empty():
    app = TodoApp()
    app.todos = []
    assert app._next_id() == 1


def test_next_id_with_todos():
    app = TodoApp()
    app.todos = [{"id": 3, "text": "x", "done": False}, {"id": 7, "text": "y", "done": False}]
    assert app._next_id() == 8


def test_status_text_empty():
    app = TodoApp()
    app.todos = []
    assert app._status_text() == "Total: 0  |  Done: 0  |  Pending: 0"


def test_status_text_mixed():
    app = TodoApp()
    app.todos = [
        {"id": 1, "text": "a", "done": True},
        {"id": 2, "text": "b", "done": False},
        {"id": 3, "text": "c", "done": True},
    ]
    assert app._status_text() == "Total: 3  |  Done: 2  |  Pending: 1"


# ── UI tests ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_add_todo():
    with patch("todo_app.load_todos", return_value=[]), patch("todo_app.save_todos"):
        app = TodoApp()
        async with app.run_test() as pilot:
            app.query_one("#new-todo", Input).value = "Buy coffee"
            await pilot.click("#add-btn")
            assert len(app.todos) == 1
            assert app.todos[0]["text"] == "Buy coffee"
            assert app.todos[0]["done"] is False


@pytest.mark.asyncio
async def test_add_empty_todo_ignored():
    with patch("todo_app.load_todos", return_value=[]), patch("todo_app.save_todos"):
        app = TodoApp()
        async with app.run_test() as pilot:
            await pilot.click("#add-btn")
            assert len(app.todos) == 0


@pytest.mark.asyncio
async def test_toggle_done():
    with patch("todo_app.load_todos", return_value=[]), patch("todo_app.save_todos"):
        app = TodoApp()
        async with app.run_test() as pilot:
            app.query_one("#new-todo", Input).value = "Test task"
            await pilot.click("#add-btn")
            item = app.query(TodoItem).first()
            with patch.object(ListView, "highlighted_child", new_callable=PropertyMock) as mock_hc:
                mock_hc.return_value = item
                app.action_toggle_done()
                await pilot.pause()
                assert app.todos[0]["done"] is True
                app.action_toggle_done()
                await pilot.pause()
                assert app.todos[0]["done"] is False


@pytest.mark.asyncio
async def test_delete_todo():
    with patch("todo_app.load_todos", return_value=[]), patch("todo_app.save_todos"):
        app = TodoApp()
        async with app.run_test() as pilot:
            app.query_one("#new-todo", Input).value = "Task to delete"
            await pilot.click("#add-btn")
            assert len(app.todos) == 1
            item = app.query(TodoItem).first()
            with patch.object(ListView, "highlighted_child", new_callable=PropertyMock) as mock_hc:
                mock_hc.return_value = item
                app.action_delete_selected()
                await pilot.pause()
            assert len(app.todos) == 0
