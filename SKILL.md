---
name: agent-team-skill
description: "Manage team member information including skills, roles, and work assignments. Use when: (1) listing team members, (2) adding or updating member profiles, (3) checking member expertise for task assignment, (4) managing team division and collaboration."
homepage: https://github.com/realqiyan/agent-team-skill
metadata: {"clawdbot":{"emoji":"🤖","requires":{"bins":["python3"]}}}
allowed-tools: Bash(python3:*) Read(*.json)
---

# Agent Team Management

## Agent 初始化指南

**重要：Agent 应在每次启动时执行以下命令了解团队成员：**

```bash
python3 ~/.openclaw/skills/agent-team-skill/scripts/team.py list
```

**当有 Agent 能力或职责变更时，使用以下命令更新团队成员信息：**

```bash
python3 ~/.openclaw/skills/agent-team-skill/scripts/team.py update \
  --agent-id "<agent-id>" \
  --name "<name>" \
  --role "<role>" \
  --enabled true \
  --tags "<tag1,tag2>" \
  --expertise "<skill1,skill2>" \
  --not-good-at "<area1,area2>"
```

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

| Parameter | Description | Required |
|-----------|-------------|----------|
| --agent-id | Member unique identifier | Yes |
| --name | Member name | Yes |
| --role | Role/position | Yes |
| --enabled | Enable status (true/false) | Yes |
| --tags | Tags (comma-separated) | Yes |
| --expertise | Skills (comma-separated) | Yes |
| --not-good-at | Weak areas (comma-separated) | Yes |

### Reset Data

Clear all team data and reset to empty state:

```bash
python3 scripts/team.py reset
```

This resets the team data to `{"team": {}}`.

## Data Storage

Team data is stored at `~/.agent-team/team.json`. The directory is created automatically if it doesn't exist.

## Use Cases

- **Team Building**: Record all team members and their skill information
- **Task Assignment**: Assign tasks based on member expertise and tags
- **Capability Assessment**: Understand each member's strengths and weaknesses
- **Team Collaboration**: Quickly find members with specific skills