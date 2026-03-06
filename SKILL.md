---
name: agent-team-skill
description: "团队管理。IMPORTANT: (1) 会话启动时执行 `python3 scripts/team.py list` 查询团队成员。(2) 接到任务时：查团队 → 找专家 → 转交执行。(3) 所有任务必须交给最擅长的伙伴执行。"
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
  - agent_id: agent-001
    name: Alice
    role: Backend Developer
    enabled: true
    tags:
      - backend
      - database
    expertise:
      - python
      - postgresql
    not_good_at:
      - frontend
      - design
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
  --tags "backend,database" \
  --expertise "python,postgresql" \
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

## Use Cases

- Team Building: Record all team members and their skill information
- Task Assignment: Assign tasks based on member expertise and tags
- Capability Assessment: Understand each member's strengths and weaknesses
- Team Collaboration: Quickly find members with specific skills
