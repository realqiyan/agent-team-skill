#!/usr/bin/env python3
"""Task Management Tool

Manages team tasks including creation, assignment, and status tracking.
Data is stored in ~/.agent-team/tasks.json by default, or a custom path via --data-file.
"""

import argparse
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Global variable to store custom data file path
_data_file_path: Path | None = None


def set_data_file(path: str | None) -> None:
    """Set a custom data file path."""
    global _data_file_path
    if path:
        _data_file_path = Path(path)


def get_data_file() -> Path:
    """Get the path to the task data file."""
    if _data_file_path:
        data_file = _data_file_path
        data_file.parent.mkdir(parents=True, exist_ok=True)
        return data_file
    data_dir = Path.home() / ".agent-team"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "tasks.json"


def load_data() -> dict:
    """Load task data from JSON file."""
    data_file = get_data_file()
    if not data_file.exists():
        return {"tasks": {}}

    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict) or "tasks" not in data:
                return {"tasks": {}}
            return data
    except (json.JSONDecodeError, IOError):
        return {"tasks": {}}


def save_data(data: dict) -> None:
    """Save task data to JSON file."""
    data_file = get_data_file()
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def reset_data() -> None:
    """Reset all task data to empty state."""
    save_data({"tasks": {}})
    print("Task data has been reset to empty.")


def generate_task_id() -> str:
    """Generate a unique task ID."""
    return f"task-{uuid.uuid4().hex[:8]}"


def format_datetime(dt: str) -> str:
    """Format datetime string for display."""
    try:
        parsed = datetime.fromisoformat(dt)
        return parsed.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return dt


def add_task(
    title: str,
    description: str,
    priority: str,
    assignee: str | None,
    tags: str,
    extra: str | None,
) -> None:
    """Create a new task."""
    data = load_data()

    task_id = generate_task_id()
    now = datetime.now().isoformat()

    # Determine initial status based on assignee
    status = "assigned" if assignee else "pending"

    # Parse extra JSON if provided
    extra_data = {}
    if extra:
        try:
            extra_data = json.loads(extra)
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON for --extra, using empty object")
            extra_data = {}

    task = {
        "id": task_id,
        "title": title,
        "description": description,
        "assignee": assignee or "",
        "status": status,
        "priority": priority,
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "result": "",
        "extra": extra_data,
        "created_at": now,
        "updated_at": now,
    }

    data["tasks"][task_id] = task
    save_data(data)

    print(f"Created task: {task_id}")
    print(f"  Title: {title}")
    print(f"  Priority: {priority}")
    print(f"  Status: {status}")
    if assignee:
        print(f"  Assignee: {assignee}")
    if extra_data:
        print(f"  Extra: {json.dumps(extra_data, ensure_ascii=False)}")


def list_tasks(status: str | None, assignee: str | None) -> None:
    """List all tasks in YAML format, optionally filtered by status and assignee."""
    data = load_data()
    tasks = data.get("tasks", {})

    if not tasks:
        print("No tasks found.")
        return

    # Filter tasks
    filtered_tasks = []
    for task_id, task in tasks.items():
        if status and task.get("status") != status:
            continue
        if assignee and task.get("assignee") != assignee:
            continue
        filtered_tasks.append(task)

    if not filtered_tasks:
        print("No tasks match the filter criteria.")
        return

    print("tasks:")
    for task in filtered_tasks:
        print(f"  - id: {task.get('id', '')}")
        print(f"    title: {task.get('title', '')}")
        print(f"    description: {task.get('description', '')}")
        print(f"    assignee: {task.get('assignee', '') or '(unassigned)'}")
        print(f"    status: {task.get('status', '')}")
        print(f"    priority: {task.get('priority', '')}")

        tags = task.get("tags", [])
        print("    tags:")
        for tag in tags:
            print(f"      - {tag}")

        print(f"    result: {task.get('result', '') or '(none)'}")

        extra = task.get("extra", {})
        if extra:
            print(f"    extra: {json.dumps(extra, ensure_ascii=False)}")
        else:
            print(f"    extra: {{}}")

        print(f"    created_at: {format_datetime(task.get('created_at', ''))}")
        print(f"    updated_at: {format_datetime(task.get('updated_at', ''))}")

    print(f"# Total: {len(filtered_tasks)} task(s)")


def update_task(
    task_id: str,
    status: str | None,
    result: str | None,
    priority: str | None,
    title: str | None,
    description: str | None,
    tags: str | None,
    extra: str | None,
) -> None:
    """Update an existing task."""
    data = load_data()
    tasks = data.get("tasks", {})

    if task_id not in tasks:
        print(f"Error: Task '{task_id}' not found.")
        sys.exit(1)

    task = tasks[task_id]
    updated = False

    if status:
        task["status"] = status
        updated = True
    if result is not None:
        task["result"] = result
        updated = True
    if priority:
        task["priority"] = priority
        updated = True
    if title:
        task["title"] = title
        updated = True
    if description:
        task["description"] = description
        updated = True
    if tags is not None:
        task["tags"] = [t.strip() for t in tags.split(",") if t.strip()]
        updated = True
    if extra is not None:
        try:
            task["extra"] = json.loads(extra)
            updated = True
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON for --extra, skipping update")

    if updated:
        task["updated_at"] = datetime.now().isoformat()
        save_data(data)
        print(f"Updated task: {task_id}")
    else:
        print(f"No changes made to task: {task_id}")


def assign_task(task_id: str, assignee: str) -> None:
    """Assign a task to a team member."""
    data = load_data()
    tasks = data.get("tasks", {})

    if task_id not in tasks:
        print(f"Error: Task '{task_id}' not found.")
        sys.exit(1)

    task = tasks[task_id]

    # Update status if currently pending
    if task["status"] == "pending":
        task["status"] = "assigned"

    task["assignee"] = assignee
    task["updated_at"] = datetime.now().isoformat()

    save_data(data)
    print(f"Assigned task '{task_id}' to: {assignee}")


def complete_task(task_id: str, result: str) -> None:
    """Mark a task as completed and record the result."""
    data = load_data()
    tasks = data.get("tasks", {})

    if task_id not in tasks:
        print(f"Error: Task '{task_id}' not found.")
        sys.exit(1)

    task = tasks[task_id]
    task["status"] = "completed"
    task["result"] = result
    task["updated_at"] = datetime.now().isoformat()

    save_data(data)
    print(f"Completed task: {task_id}")
    print(f"  Result: {result}")


def show_task(task_id: str) -> None:
    """Show details of a specific task."""
    data = load_data()
    tasks = data.get("tasks", {})

    if task_id not in tasks:
        print(f"Error: Task '{task_id}' not found.")
        sys.exit(1)

    task = tasks[task_id]

    print(f"id: {task.get('id', '')}")
    print(f"title: {task.get('title', '')}")
    print(f"description: {task.get('description', '')}")
    print(f"assignee: {task.get('assignee', '') or '(unassigned)'}")
    print(f"status: {task.get('status', '')}")
    print(f"priority: {task.get('priority', '')}")

    tags = task.get("tags", [])
    print("tags:")
    for tag in tags:
        print(f"  - {tag}")

    print(f"result: {task.get('result', '') or '(none)'}")

    extra = task.get("extra", {})
    if extra:
        print(f"extra: {json.dumps(extra, ensure_ascii=False)}")
    else:
        print(f"extra: {{}}")

    print(f"created_at: {format_datetime(task.get('created_at', ''))}")
    print(f"updated_at: {format_datetime(task.get('updated_at', ''))}")


def main():
    parser = argparse.ArgumentParser(
        description="Task Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--data-file",
        help="Path to data file (default: ~/.agent-team/tasks.json)",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # add command
    add_parser = subparsers.add_parser("add", help="Create a new task")
    add_parser.add_argument("--title", required=True, help="Task title")
    add_parser.add_argument("--description", default="", help="Task description")
    add_parser.add_argument(
        "--priority",
        choices=["low", "medium", "high", "urgent"],
        default="medium",
        help="Task priority (default: medium)",
    )
    add_parser.add_argument("--assignee", help="Assign to agent (optional)")
    add_parser.add_argument("--tags", default="", help="Tags (comma separated)")
    add_parser.add_argument("--extra", help="Extra metadata (JSON string)")

    # list command
    list_parser = subparsers.add_parser("list", help="List all tasks")
    list_parser.add_argument(
        "--status",
        choices=["pending", "assigned", "in_progress", "completed", "blocked"],
        help="Filter by status",
    )
    list_parser.add_argument("--assignee", help="Filter by assignee")

    # update command
    update_parser = subparsers.add_parser("update", help="Update a task")
    update_parser.add_argument("--id", required=True, help="Task ID")
    update_parser.add_argument(
        "--status",
        choices=["pending", "assigned", "in_progress", "completed", "blocked"],
        help="Update status",
    )
    update_parser.add_argument("--result", help="Task result")
    update_parser.add_argument(
        "--priority",
        choices=["low", "medium", "high", "urgent"],
        help="Update priority",
    )
    update_parser.add_argument("--title", help="Update title")
    update_parser.add_argument("--description", help="Update description")
    update_parser.add_argument("--tags", help="Update tags (comma separated)")
    update_parser.add_argument("--extra", help="Update extra metadata (JSON string)")

    # assign command
    assign_parser = subparsers.add_parser("assign", help="Assign a task to a member")
    assign_parser.add_argument("--id", required=True, help="Task ID")
    assign_parser.add_argument("--assignee", required=True, help="Assignee agent ID")

    # complete command
    complete_parser = subparsers.add_parser("complete", help="Mark task as completed")
    complete_parser.add_argument("--id", required=True, help="Task ID")
    complete_parser.add_argument("--result", required=True, help="Task result")

    # show command
    show_parser = subparsers.add_parser("show", help="Show task details")
    show_parser.add_argument("--id", required=True, help="Task ID")

    # reset command
    subparsers.add_parser("reset", help="Reset all task data to empty")

    args = parser.parse_args()

    # Set custom data file if provided
    set_data_file(args.data_file)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "add":
        add_task(
            title=args.title,
            description=args.description,
            priority=args.priority,
            assignee=args.assignee,
            tags=args.tags,
            extra=args.extra,
        )
    elif args.command == "list":
        list_tasks(status=args.status, assignee=args.assignee)
    elif args.command == "update":
        update_task(
            task_id=args.id,
            status=args.status,
            result=args.result,
            priority=args.priority,
            title=args.title,
            description=args.description,
            tags=args.tags,
            extra=args.extra,
        )
    elif args.command == "assign":
        assign_task(task_id=args.id, assignee=args.assignee)
    elif args.command == "complete":
        complete_task(task_id=args.id, result=args.result)
    elif args.command == "show":
        show_task(task_id=args.id)
    elif args.command == "reset":
        reset_data()


if __name__ == "__main__":
    main()