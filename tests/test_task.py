#!/usr/bin/env python3
"""Tests for task.py"""

import json
import sys
from io import StringIO
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import task


@pytest.fixture
def temp_data_file(tmp_path: Path):
    """Create a temporary data file for testing."""
    data_file = tmp_path / "tasks.json"
    task.set_data_file(str(data_file))
    yield data_file
    # Reset after test
    task.set_data_file(None)


@pytest.fixture
def sample_task_data():
    """Sample task data for testing."""
    return {
        "id": "task-abc12345",
        "title": "Test Task",
        "description": "A test task description",
        "assignee": "agent-001",
        "status": "assigned",
        "priority": "high",
        "tags": ["backend", "api"],
        "result": "",
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T10:30:00",
    }


class TestAddCommand:
    """Tests for the add command."""

    def test_add_task_minimal(self, temp_data_file, capsys):
        """Test adding a task with minimal required fields."""
        task.add_task(
            title="New Task",
            description="",
            priority="medium",
            assignee=None,
            tags="",
            extra=None,
        )
        captured = capsys.readouterr()

        assert "Created task:" in captured.out
        assert "Title: New Task" in captured.out
        assert "Priority: medium" in captured.out
        assert "Status: pending" in captured.out

        # Verify data was saved
        data = task.load_data()
        assert len(data["tasks"]) == 1
        saved_task = list(data["tasks"].values())[0]
        assert saved_task["title"] == "New Task"
        assert saved_task["status"] == "pending"
        assert saved_task["assignee"] == ""
        assert saved_task["extra"] == {}

    def test_add_task_with_assignee(self, temp_data_file, capsys):
        """Test adding a task with an assignee sets status to assigned."""
        task.add_task(
            title="Assigned Task",
            description="Task with assignee",
            priority="high",
            assignee="agent-001",
            tags="backend, api",
            extra=None,
        )
        captured = capsys.readouterr()

        assert "Created task:" in captured.out
        assert "Assignee: agent-001" in captured.out
        assert "Status: assigned" in captured.out

        # Verify status is assigned
        data = task.load_data()
        saved_task = list(data["tasks"].values())[0]
        assert saved_task["status"] == "assigned"
        assert saved_task["assignee"] == "agent-001"

    def test_add_task_with_tags(self, temp_data_file):
        """Test that tags are correctly parsed from comma-separated string."""
        task.add_task(
            title="Tagged Task",
            description="",
            priority="low",
            assignee=None,
            tags=" tag1 , tag2 , tag3 ",
            extra=None,
        )

        data = task.load_data()
        saved_task = list(data["tasks"].values())[0]
        assert saved_task["tags"] == ["tag1", "tag2", "tag3"]

    def test_add_task_with_extra(self, temp_data_file, capsys):
        """Test adding a task with extra metadata."""
        task.add_task(
            title="Task with Extra",
            description="Task with extra metadata",
            priority="high",
            assignee="agent-001",
            tags="backend",
            extra='{"project": "alpha", "deadline": "2024-12-31"}',
        )
        captured = capsys.readouterr()

        assert "Created task:" in captured.out
        assert "Extra:" in captured.out

        # Verify extra data was saved
        data = task.load_data()
        saved_task = list(data["tasks"].values())[0]
        assert saved_task["extra"]["project"] == "alpha"
        assert saved_task["extra"]["deadline"] == "2024-12-31"

    def test_add_task_with_invalid_extra(self, temp_data_file, capsys):
        """Test adding a task with invalid JSON for extra uses empty object."""
        task.add_task(
            title="Task with Invalid Extra",
            description="",
            priority="medium",
            assignee=None,
            tags="",
            extra="not valid json",
        )
        captured = capsys.readouterr()

        assert "Warning: Invalid JSON" in captured.out

        # Verify empty extra is used
        data = task.load_data()
        saved_task = list(data["tasks"].values())[0]
        assert saved_task["extra"] == {}

    def test_add_task_priority_levels(self, temp_data_file):
        """Test adding tasks with different priority levels."""
        priorities = ["low", "medium", "high", "urgent"]

        for priority in priorities:
            task.add_task(
                title=f"{priority} priority task",
                description="",
                priority=priority,
                assignee=None,
                tags="",
                extra=None,
            )

        data = task.load_data()
        assert len(data["tasks"]) == 4

        saved_priorities = [t["priority"] for t in data["tasks"].values()]
        assert set(saved_priorities) == set(priorities)


class TestListCommand:
    """Tests for the list command."""

    def test_list_empty_data(self, temp_data_file, capsys):
        """Test listing when no tasks exist."""
        task.list_tasks(status=None, assignee=None)
        captured = capsys.readouterr()
        assert "No tasks found" in captured.out

    def test_list_with_tasks(self, temp_data_file, capsys):
        """Test listing with existing tasks."""
        # Add some tasks
        task.add_task(title="Task 1", description="", priority="high", assignee=None, tags="", extra=None)
        task.add_task(title="Task 2", description="", priority="low", assignee=None, tags="", extra=None)

        task.list_tasks(status=None, assignee=None)
        captured = capsys.readouterr()

        assert "Task 1" in captured.out
        assert "Task 2" in captured.out
        assert "Total: 2 task(s)" in captured.out

    def test_list_filter_by_status(self, temp_data_file, capsys):
        """Test filtering tasks by status."""
        # Add tasks with different statuses
        task.add_task(title="Pending Task", description="", priority="medium", assignee=None, tags="", extra=None)
        task.add_task(title="Assigned Task", description="", priority="medium", assignee="agent-001", tags="", extra=None)
        # Clear the captured output from add_task calls
        capsys.readouterr()

        task.list_tasks(status="pending", assignee=None)
        captured = capsys.readouterr()

        assert "Pending Task" in captured.out
        assert "Assigned Task" not in captured.out

    def test_list_filter_by_assignee(self, temp_data_file, capsys):
        """Test filtering tasks by assignee."""
        task.add_task(title="Task A", description="", priority="medium", assignee="agent-001", tags="", extra=None)
        task.add_task(title="Task B", description="", priority="medium", assignee="agent-002", tags="", extra=None)
        # Clear the captured output from add_task calls
        capsys.readouterr()

        task.list_tasks(status=None, assignee="agent-001")
        captured = capsys.readouterr()

        assert "Task A" in captured.out
        assert "Task B" not in captured.out

    def test_list_filter_no_match(self, temp_data_file, capsys):
        """Test filtering returns no match message."""
        task.add_task(title="Task", description="", priority="medium", assignee="agent-001", tags="", extra=None)

        task.list_tasks(status="pending", assignee=None)
        captured = capsys.readouterr()

        assert "No tasks match the filter criteria" in captured.out

    def test_list_shows_extra(self, temp_data_file, capsys):
        """Test that list command shows extra field."""
        task.add_task(
            title="Task with Extra",
            description="",
            priority="medium",
            assignee=None,
            tags="",
            extra='{"key": "value"}',
        )
        capsys.readouterr()  # Clear add output

        task.list_tasks(status=None, assignee=None)
        captured = capsys.readouterr()

        assert "extra:" in captured.out


class TestUpdateCommand:
    """Tests for the update command."""

    def test_update_task_status(self, temp_data_file, capsys):
        """Test updating task status."""
        task.add_task(title="Task to Update", description="", priority="medium", assignee=None, tags="", extra=None)
        data = task.load_data()
        task_id = list(data["tasks"].keys())[0]

        task.update_task(task_id=task_id, status="in_progress", result=None, priority=None, title=None, description=None, tags=None, extra=None)
        captured = capsys.readouterr()

        assert f"Updated task: {task_id}" in captured.out

        # Verify update
        data = task.load_data()
        assert data["tasks"][task_id]["status"] == "in_progress"

    def test_update_task_result(self, temp_data_file, capsys):
        """Test updating task result."""
        task.add_task(title="Task", description="", priority="medium", assignee=None, tags="", extra=None)
        data = task.load_data()
        task_id = list(data["tasks"].keys())[0]

        task.update_task(task_id=task_id, status=None, result="Work completed", priority=None, title=None, description=None, tags=None, extra=None)

        data = task.load_data()
        assert data["tasks"][task_id]["result"] == "Work completed"

    def test_update_task_priority(self, temp_data_file):
        """Test updating task priority."""
        task.add_task(title="Task", description="", priority="low", assignee=None, tags="", extra=None)
        data = task.load_data()
        task_id = list(data["tasks"].keys())[0]

        task.update_task(task_id=task_id, status=None, result=None, priority="urgent", title=None, description=None, tags=None, extra=None)

        data = task.load_data()
        assert data["tasks"][task_id]["priority"] == "urgent"

    def test_update_task_title_and_description(self, temp_data_file):
        """Test updating task title and description."""
        task.add_task(title="Old Title", description="Old desc", priority="medium", assignee=None, tags="", extra=None)
        data = task.load_data()
        task_id = list(data["tasks"].keys())[0]

        task.update_task(task_id=task_id, status=None, result=None, priority=None, title="New Title", description="New desc", tags=None, extra=None)

        data = task.load_data()
        assert data["tasks"][task_id]["title"] == "New Title"
        assert data["tasks"][task_id]["description"] == "New desc"

    def test_update_task_tags(self, temp_data_file):
        """Test updating task tags."""
        task.add_task(title="Task", description="", priority="medium", assignee=None, tags="old", extra=None)
        data = task.load_data()
        task_id = list(data["tasks"].keys())[0]

        task.update_task(task_id=task_id, status=None, result=None, priority=None, title=None, description=None, tags="new, updated", extra=None)

        data = task.load_data()
        assert data["tasks"][task_id]["tags"] == ["new", "updated"]

    def test_update_task_extra(self, temp_data_file):
        """Test updating task extra field."""
        task.add_task(title="Task", description="", priority="medium", assignee=None, tags="", extra=None)
        data = task.load_data()
        task_id = list(data["tasks"].keys())[0]

        task.update_task(task_id=task_id, status=None, result=None, priority=None, title=None, description=None, tags=None, extra='{"new_key": "new_value"}')

        data = task.load_data()
        assert data["tasks"][task_id]["extra"]["new_key"] == "new_value"

    def test_update_task_extra_invalid_json(self, temp_data_file, capsys):
        """Test updating task extra with invalid JSON."""
        task.add_task(title="Task", description="", priority="medium", assignee=None, tags="", extra='{"initial": "value"}')
        data = task.load_data()
        task_id = list(data["tasks"].keys())[0]

        task.update_task(task_id=task_id, status=None, result=None, priority=None, title=None, description=None, tags=None, extra="invalid json")
        captured = capsys.readouterr()

        assert "Warning: Invalid JSON" in captured.out
        # Original extra should be preserved
        data = task.load_data()
        assert data["tasks"][task_id]["extra"]["initial"] == "value"

    def test_update_task_no_changes(self, temp_data_file, capsys):
        """Test updating with no changes."""
        task.add_task(title="Task", description="", priority="medium", assignee=None, tags="", extra=None)
        data = task.load_data()
        task_id = list(data["tasks"].keys())[0]

        task.update_task(task_id=task_id, status=None, result=None, priority=None, title=None, description=None, tags=None, extra=None)
        captured = capsys.readouterr()

        assert f"No changes made to task: {task_id}" in captured.out

    def test_update_task_not_found(self, temp_data_file, capsys):
        """Test updating non-existent task."""
        with pytest.raises(SystemExit) as exc_info:
            task.update_task(task_id="nonexistent", status="completed", result=None, priority=None, title=None, description=None, tags=None, extra=None)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error: Task 'nonexistent' not found" in captured.out


class TestAssignCommand:
    """Tests for the assign command."""

    def test_assign_task(self, temp_data_file, capsys):
        """Test assigning a task."""
        task.add_task(title="Unassigned Task", description="", priority="medium", assignee=None, tags="", extra=None)
        data = task.load_data()
        task_id = list(data["tasks"].keys())[0]

        task.assign_task(task_id=task_id, assignee="agent-001")
        captured = capsys.readouterr()

        assert f"Assigned task '{task_id}' to: agent-001" in captured.out

        # Verify assignment
        data = task.load_data()
        assert data["tasks"][task_id]["assignee"] == "agent-001"

    def test_assign_updates_status_from_pending(self, temp_data_file):
        """Test that assigning a pending task changes status to assigned."""
        task.add_task(title="Pending Task", description="", priority="medium", assignee=None, tags="", extra=None)
        data = task.load_data()
        task_id = list(data["tasks"].keys())[0]

        # Verify initial status is pending
        assert data["tasks"][task_id]["status"] == "pending"

        task.assign_task(task_id=task_id, assignee="agent-001")

        data = task.load_data()
        assert data["tasks"][task_id]["status"] == "assigned"

    def test_assign_does_not_change_completed_status(self, temp_data_file):
        """Test that assigning a completed task doesn't change its status."""
        task.add_task(title="Task", description="", priority="medium", assignee="agent-001", tags="", extra=None)
        data = task.load_data()
        task_id = list(data["tasks"].keys())[0]

        # First complete the task
        task.complete_task(task_id=task_id, result="Done")

        # Then reassign
        task.assign_task(task_id=task_id, assignee="agent-002")

        data = task.load_data()
        assert data["tasks"][task_id]["status"] == "completed"
        assert data["tasks"][task_id]["assignee"] == "agent-002"

    def test_assign_task_not_found(self, temp_data_file, capsys):
        """Test assigning non-existent task."""
        with pytest.raises(SystemExit) as exc_info:
            task.assign_task(task_id="nonexistent", assignee="agent-001")

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error: Task 'nonexistent' not found" in captured.out


class TestCompleteCommand:
    """Tests for the complete command."""

    def test_complete_task(self, temp_data_file, capsys):
        """Test completing a task."""
        task.add_task(title="Task to Complete", description="", priority="medium", assignee="agent-001", tags="", extra=None)
        data = task.load_data()
        task_id = list(data["tasks"].keys())[0]

        task.complete_task(task_id=task_id, result="Successfully implemented feature")
        captured = capsys.readouterr()

        assert f"Completed task: {task_id}" in captured.out
        assert "Result: Successfully implemented feature" in captured.out

        # Verify completion
        data = task.load_data()
        assert data["tasks"][task_id]["status"] == "completed"
        assert data["tasks"][task_id]["result"] == "Successfully implemented feature"

    def test_complete_task_not_found(self, temp_data_file, capsys):
        """Test completing non-existent task."""
        with pytest.raises(SystemExit) as exc_info:
            task.complete_task(task_id="nonexistent", result="Done")

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error: Task 'nonexistent' not found" in captured.out


class TestShowCommand:
    """Tests for the show command."""

    def test_show_task(self, temp_data_file, capsys):
        """Test showing a specific task."""
        task.add_task(title="Show Test Task", description="Test description", priority="high", assignee="agent-001", tags="test, demo", extra=None)
        data = task.load_data()
        task_id = list(data["tasks"].keys())[0]

        task.show_task(task_id=task_id)
        captured = capsys.readouterr()

        assert f"id: {task_id}" in captured.out
        assert "title: Show Test Task" in captured.out
        assert "description: Test description" in captured.out
        assert "assignee: agent-001" in captured.out
        assert "status: assigned" in captured.out
        assert "priority: high" in captured.out
        assert "- test" in captured.out
        assert "- demo" in captured.out
        assert "extra:" in captured.out

    def test_show_task_unassigned(self, temp_data_file, capsys):
        """Test showing task with no assignee."""
        task.add_task(title="Unassigned", description="", priority="low", assignee=None, tags="", extra=None)
        data = task.load_data()
        task_id = list(data["tasks"].keys())[0]

        task.show_task(task_id=task_id)
        captured = capsys.readouterr()

        assert "assignee: (unassigned)" in captured.out

    def test_show_task_with_extra(self, temp_data_file, capsys):
        """Test showing task with extra field."""
        task.add_task(title="Task with Extra", description="", priority="medium", assignee=None, tags="", extra='{"project": "alpha", "count": 42}')
        data = task.load_data()
        task_id = list(data["tasks"].keys())[0]

        task.show_task(task_id=task_id)
        captured = capsys.readouterr()

        assert "extra:" in captured.out
        assert "project" in captured.out
        assert "alpha" in captured.out

    def test_show_task_not_found(self, temp_data_file, capsys):
        """Test showing non-existent task."""
        with pytest.raises(SystemExit) as exc_info:
            task.show_task(task_id="nonexistent")

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error: Task 'nonexistent' not found" in captured.out


class TestResetCommand:
    """Tests for the reset command."""

    def test_reset_clears_data(self, temp_data_file, capsys):
        """Test that reset clears all task data."""
        # Add some tasks
        task.add_task(title="Task 1", description="", priority="medium", assignee=None, tags="", extra=None)
        task.add_task(title="Task 2", description="", priority="high", assignee="agent-001", tags="", extra=None)

        # Verify tasks exist
        data = task.load_data()
        assert len(data["tasks"]) == 2

        # Reset
        task.reset_data()
        captured = capsys.readouterr()
        assert "reset to empty" in captured.out

        # Verify data is empty
        data = task.load_data()
        assert data["tasks"] == {}


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_load_data_file_not_exists(self, tmp_path):
        """Test loading when file doesn't exist."""
        non_existent = tmp_path / "nonexistent.json"
        task.set_data_file(str(non_existent))
        data = task.load_data()
        assert data == {"tasks": {}}
        task.set_data_file(None)

    def test_load_data_invalid_json(self, tmp_path):
        """Test loading when JSON is invalid."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("not valid json {")
        task.set_data_file(str(invalid_file))
        data = task.load_data()
        assert data == {"tasks": {}}
        task.set_data_file(None)

    def test_load_data_missing_tasks_key(self, tmp_path):
        """Test loading when JSON is missing 'tasks' key."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text('{"other": "data"}')
        task.set_data_file(str(bad_file))
        data = task.load_data()
        assert data == {"tasks": {}}
        task.set_data_file(None)

    def test_format_datetime_valid(self):
        """Test formatting valid datetime string."""
        result = task.format_datetime("2024-01-15T10:30:00")
        assert result == "2024-01-15 10:30:00"

    def test_format_datetime_invalid(self):
        """Test formatting invalid datetime string."""
        result = task.format_datetime("invalid")
        assert result == "invalid"

    def test_generate_task_id_format(self):
        """Test that generated task IDs have correct format."""
        task_id = task.generate_task_id()
        assert task_id.startswith("task-")
        assert len(task_id) == 13  # "task-" + 8 hex chars

    def test_generate_task_id_uniqueness(self):
        """Test that generated task IDs are unique."""
        ids = set()
        for _ in range(100):
            task_id = task.generate_task_id()
            assert task_id not in ids
            ids.add(task_id)

    def test_custom_data_file_path(self, tmp_path):
        """Test using a custom data file path."""
        custom_file = tmp_path / "custom_tasks.json"
        task.set_data_file(str(custom_file))

        task.add_task(title="Custom Path Task", description="", priority="medium", assignee=None, tags="", extra=None)

        assert custom_file.exists()
        task.set_data_file(None)


class TestCLI:
    """Tests for command-line interface."""

    def test_add_cli(self, temp_data_file, monkeypatch, capsys):
        """Test add command via CLI."""
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "task.py",
                "--data-file",
                str(temp_data_file),
                "add",
                "--title",
                "CLI Task",
                "--description",
                "Created via CLI",
                "--priority",
                "high",
                "--assignee",
                "agent-cli",
                "--tags",
                "cli, test",
            ],
        )
        task.main()
        captured = capsys.readouterr()
        assert "Created task:" in captured.out
        assert "Title: CLI Task" in captured.out

    def test_add_cli_with_extra(self, temp_data_file, monkeypatch, capsys):
        """Test add command via CLI with extra field."""
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "task.py",
                "--data-file",
                str(temp_data_file),
                "add",
                "--title",
                "Task with Extra",
                "--priority",
                "high",
                "--extra",
                '{"key": "value", "number": 123}',
            ],
        )
        task.main()
        captured = capsys.readouterr()
        assert "Created task:" in captured.out
        assert "Extra:" in captured.out

        # Verify extra was saved
        data = task.load_data()
        saved_task = list(data["tasks"].values())[0]
        assert saved_task["extra"]["key"] == "value"
        assert saved_task["extra"]["number"] == 123

    def test_list_cli(self, temp_data_file, monkeypatch, capsys):
        """Test list command via CLI."""
        # Add a task first
        task.add_task(title="List Test", description="", priority="medium", assignee=None, tags="", extra=None)

        monkeypatch.setattr(sys, "argv", ["task.py", "--data-file", str(temp_data_file), "list"])
        task.main()
        captured = capsys.readouterr()
        assert "List Test" in captured.out

    def test_update_cli(self, temp_data_file, monkeypatch, capsys):
        """Test update command via CLI."""
        task.add_task(title="To Update", description="", priority="low", assignee=None, tags="", extra=None)
        data = task.load_data()
        task_id = list(data["tasks"].keys())[0]

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "task.py",
                "--data-file",
                str(temp_data_file),
                "update",
                "--id",
                task_id,
                "--status",
                "completed",
                "--result",
                "Done via CLI",
            ],
        )
        task.main()
        captured = capsys.readouterr()
        assert f"Updated task: {task_id}" in captured.out

    def test_update_cli_with_extra(self, temp_data_file, monkeypatch, capsys):
        """Test update command via CLI with extra field."""
        task.add_task(title="To Update", description="", priority="low", assignee=None, tags="", extra=None)
        data = task.load_data()
        task_id = list(data["tasks"].keys())[0]

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "task.py",
                "--data-file",
                str(temp_data_file),
                "update",
                "--id",
                task_id,
                "--extra",
                '{"new_field": "updated_value"}',
            ],
        )
        task.main()
        captured = capsys.readouterr()
        assert f"Updated task: {task_id}" in captured.out

        # Verify extra was updated
        data = task.load_data()
        assert data["tasks"][task_id]["extra"]["new_field"] == "updated_value"

    def test_assign_cli(self, temp_data_file, monkeypatch, capsys):
        """Test assign command via CLI."""
        task.add_task(title="To Assign", description="", priority="medium", assignee=None, tags="", extra=None)
        data = task.load_data()
        task_id = list(data["tasks"].keys())[0]

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "task.py",
                "--data-file",
                str(temp_data_file),
                "assign",
                "--id",
                task_id,
                "--assignee",
                "agent-cli",
            ],
        )
        task.main()
        captured = capsys.readouterr()
        assert f"Assigned task '{task_id}' to: agent-cli" in captured.out

    def test_complete_cli(self, temp_data_file, monkeypatch, capsys):
        """Test complete command via CLI."""
        task.add_task(title="To Complete", description="", priority="medium", assignee="agent-001", tags="", extra=None)
        data = task.load_data()
        task_id = list(data["tasks"].keys())[0]

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "task.py",
                "--data-file",
                str(temp_data_file),
                "complete",
                "--id",
                task_id,
                "--result",
                "Completed via CLI",
            ],
        )
        task.main()
        captured = capsys.readouterr()
        assert f"Completed task: {task_id}" in captured.out

    def test_show_cli(self, temp_data_file, monkeypatch, capsys):
        """Test show command via CLI."""
        task.add_task(title="To Show", description="Show desc", priority="medium", assignee=None, tags="", extra=None)
        data = task.load_data()
        task_id = list(data["tasks"].keys())[0]

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "task.py",
                "--data-file",
                str(temp_data_file),
                "show",
                "--id",
                task_id,
            ],
        )
        task.main()
        captured = capsys.readouterr()
        assert "title: To Show" in captured.out

    def test_reset_cli(self, temp_data_file, monkeypatch, capsys):
        """Test reset command via CLI."""
        task.add_task(title="To Reset", description="", priority="medium", assignee=None, tags="", extra=None)

        monkeypatch.setattr(
            sys, "argv", ["task.py", "--data-file", str(temp_data_file), "reset"]
        )
        task.main()
        captured = capsys.readouterr()
        assert "reset to empty" in captured.out

    def test_list_filter_status_cli(self, temp_data_file, monkeypatch, capsys):
        """Test list with status filter via CLI."""
        task.add_task(title="Pending Task", description="", priority="medium", assignee=None, tags="", extra=None)
        task.add_task(title="Assigned Task", description="", priority="medium", assignee="agent-001", tags="", extra=None)
        # Clear the captured output from add_task calls
        capsys.readouterr()

        monkeypatch.setattr(
            sys,
            "argv",
            ["task.py", "--data-file", str(temp_data_file), "list", "--status", "pending"],
        )
        task.main()
        captured = capsys.readouterr()
        assert "Pending Task" in captured.out
        assert "Assigned Task" not in captured.out

    def test_list_filter_assignee_cli(self, temp_data_file, monkeypatch, capsys):
        """Test list with assignee filter via CLI."""
        task.add_task(title="Task A", description="", priority="medium", assignee="agent-001", tags="", extra=None)
        task.add_task(title="Task B", description="", priority="medium", assignee="agent-002", tags="", extra=None)
        # Clear the captured output from add_task calls
        capsys.readouterr()

        monkeypatch.setattr(
            sys,
            "argv",
            ["task.py", "--data-file", str(temp_data_file), "list", "--assignee", "agent-001"],
        )
        task.main()
        captured = capsys.readouterr()
        assert "Task A" in captured.out
        assert "Task B" not in captured.out

    def test_no_command_shows_help(self, monkeypatch, capsys):
        """Test that running without command shows help."""
        monkeypatch.setattr(sys, "argv", ["task.py"])

        with pytest.raises(SystemExit) as exc_info:
            task.main()

        assert exc_info.value.code == 1

    def test_update_not_found_cli(self, temp_data_file, monkeypatch, capsys):
        """Test update command with non-existent task via CLI."""
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "task.py",
                "--data-file",
                str(temp_data_file),
                "update",
                "--id",
                "nonexistent",
                "--status",
                "completed",
            ],
        )

        with pytest.raises(SystemExit) as exc_info:
            task.main()

        assert exc_info.value.code == 1