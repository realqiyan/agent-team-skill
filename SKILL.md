---
name: agent-team-skill
description: "Agent团队管理：成员档案（技能、角色、专长）和任务管理（创建、分配、追踪）。初始化时获取成员列表；成员能力变化时更新档案；根据专长分配任务。"
homepage: https://github.com/realqiyan/agent-team-skill
metadata: {"clawdbot":{"emoji":"🤖","requires":{"bins":["python3"]}}}
allowed-tools: Bash(python3:*) Read(*.json)
---

# Agent Team Management

Manage team member information including skills, roles, and work assignments.

## Commands

All commands are executed via the `team.py` script:

```bash
python3 scripts/team.py <command> [options]
```

### List Members

List all team members in YAML format:

```bash
python3 scripts/team.py list
```

Output example:
```yaml
team:
  - agent_id: q
    name: Q
    role: 主助手/协调者
    enabled: true
    tags:
      - 协调
      - 路由
    expertise:
      - 任务分发
      - 日程管理
    not_good_at:
      - 深度开发
# Total: 1 member(s)
```

### Add/Update Member

Add a new member or update an existing one:

```bash
python3 scripts/team.py update \
  --agent-id "agent-001" \
  --name "Alice" \
  --role "Backend Developer" \
  --enabled true \
  --tags "backend,api,database" \
  --expertise "python,go,postgresql" \
  --not-good-at "frontend,design"
```

Parameters:
- `--agent-id`: Member unique identifier (required)
- `--name`: Member name (required)
- `--role`: Role/position (required)
- `--enabled`: Enable status (true/false, required)
- `--tags`: Tags (comma-separated, required)
- `--expertise`: Skills (comma-separated, required)
- `--not-good-at`: Weak areas (comma-separated, required)

### Reset Data

Clear all team data and reset to empty state:

```bash
python3 scripts/team.py reset
```

This resets the team data to `{"team": {}}`.

## Data Storage

Team data is stored at `~/.agent-team/team.json`. The directory is created automatically if it doesn't exist.

## Task Management

Manage team tasks including creation, assignment, and status tracking. All task commands are executed via the `task.py` script:

```bash
python3 scripts/task.py <command> [options]
```

### Add Task

Create a new task:

```bash
python3 scripts/task.py add \
  --title "Implement API endpoint" \
  --description "Create REST API for user management" \
  --priority high \
  --assignee "agent-001" \
  --tags "backend,api,urgent" \
  --extra '{"deadline": "2026-03-10", "estimate_hours": 8}'
```

Parameters:
- `--title`: Task title (required)
- `--description`: Task description (optional, default: empty)
- `--priority`: Task priority - low/medium/high/urgent (optional, default: medium)
- `--assignee`: Assign to agent by agent_id (optional)
- `--tags`: Tags (comma separated, optional)
- `--extra`: Custom metadata as JSON string (optional, default: {})

### List Tasks

List all tasks in YAML format, optionally filtered:

```bash
python3 scripts/task.py list [--status STATUS] [--assignee AGENT_ID]
```

Output example:
```yaml
tasks:
  - id: task-a1b2c3d4
    title: Implement API endpoint
    description: Create REST API for user management
    assignee: agent-001
    status: assigned
    priority: high
    tags:
      - backend
      - api
      - urgent
    result: (none)
    created_at: 2024-01-15 10:30:00
    updated_at: 2024-01-15 10:30:00
# Total: 1 task(s)
```

Filter options:
- `--status`: Filter by status (pending/assigned/in_progress/completed/blocked)
- `--assignee`: Filter by assignee agent_id

### Update Task

Update an existing task:

```bash
python3 scripts/task.py update --id task-a1b2c3d4 --status in_progress
```

Parameters:
- `--id`: Task ID (required)
- `--status`: Update status (pending/assigned/in_progress/completed/blocked)
- `--result`: Task result
- `--priority`: Update priority (low/medium/high/urgent)
- `--title`: Update title
- `--description`: Update description
- `--tags`: Update tags (comma separated)
- `--extra`: Update custom metadata as JSON string

### Assign Task

Assign a task to a team member:

```bash
python3 scripts/task.py assign --id task-a1b2c3d4 --assignee agent-001
```

This automatically changes status from `pending` to `assigned` if applicable.

### Complete Task

Mark a task as completed and record the result:

```bash
python3 scripts/task.py complete --id task-a1b2c3d4 --result "API endpoint implemented and tested"
```

Parameters:
- `--id`: Task ID (required)
- `--result`: Task result (required)

### Show Task Details

Show details of a specific task:

```bash
python3 scripts/task.py show --id task-a1b2c3d4
```

### Reset Task Data

Clear all task data and reset to empty state:

```bash
python3 scripts/task.py reset
```

### Extensible Extra Field

Tasks support an `extra` field for storing custom metadata. This allows you to attach any additional information to a task:

```bash
# Add task with custom metadata
python3 scripts/task.py add \
  --title "Implement login" \
  --extra '{"deadline": "2026-03-10", "estimate_hours": 8, "related_docs": ["doc-001"]}'

# Update the extra field
python3 scripts/task.py update \
  --id task-abc123 \
  --extra '{"deadline": "2026-03-12", "progress": 60}'
```

The `extra` field accepts any valid JSON object and is displayed in `show` and `list` outputs.

## Task Data Storage

Task data is stored at `~/.agent-team/tasks.json`. The directory is created automatically if it doesn't exist.

## Use Cases

- Team Building: Record all team members and their skill information
- Task Assignment: Assign tasks based on member expertise and tags
- Task Tracking: Track task status from creation to completion
- Result Synchronization: Record task results for team coordination
- Capability Assessment: Understand each member's strengths and weaknesses
- Team Collaboration: Quickly find members with specific skills