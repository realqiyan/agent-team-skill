# Agent Team Skill

Agent 团队管理工具，包含成员管理和任务管理两个模块。

## 功能特性

- 👥 **成员管理** - 管理团队成员信息，包括技能、角色和工作分配
- 📋 **任务管理** - 创建、分配、跟踪团队任务
- 🔍 **智能路由** - 根据成员专长匹配任务
- 📊 **状态追踪** - 实时跟踪任务状态和进度

## 安装方法

```bash
# 通过 ClawHub 安装
clawhub install agent-team-skill

# 或克隆仓库
git clone https://github.com/realqiyan/agent-team-skill.git
cd agent-team-skill

# 确保安装了 Python 3.10+
python3 --version
```

## 使用方法

### 成员管理 (team.py)

管理团队成员信息：

```bash
python3 scripts/team.py <command> [options]
```

| 命令 | 说明 |
|------|------|
| `list` | 列出所有成员 |
| `update` | 添加/更新成员 |
| `reset` | 重置成员数据 |

### 列出成员

列出所有团队成员（YAML 格式）：

```bash
python3 scripts/team.py list
```

输出示例：
```yaml
team:
  - agent_id: alice
    name: Alice
    role: Backend Developer
    enabled: true
    tags:
      - backend
      - api
      - database
    expertise:
      - python
      - go
      - postgresql
    not_good_at:
      - frontend
      - design
  - agent_id: bob
    name: Bob
    role: Designer
    enabled: true
    tags:
      - ui
      - ux
    expertise:
      - figma
      - css
    not_good_at:
      - backend
# Total: 2 member(s)
```

### 添加/更新成员

添加新成员或更新现有成员：

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

参数说明：
- `--agent-id`: 成员唯一标识符 (必需)
- `--name`: 成员名称 (必需)
- `--role`: 角色/职位 (必需)
- `--enabled`: 启用状态 true/false (必需)
- `--tags`: 标签，逗号分隔 (必需)
- `--expertise`: 专长技能，逗号分隔 (必需)
- `--not-good-at`: 弱项领域，逗号分隔 (必需)

### 重置数据

清除所有团队数据，重置为空状态：

```bash
python3 scripts/team.py reset
```

## 自定义数据文件

使用 `--data-file` 参数指定自定义数据文件路径：

```bash
python3 scripts/team.py --data-file /path/to/team.json list
```

默认数据存储位置：`~/.agent-team/team.json`

## 数据文件说明

数据文件使用 JSON 格式存储，结构如下：

```json
{
  "team": {
    "agent-001": {
      "agent_id": "agent-001",
      "name": "Alice",
      "role": "Backend Developer",
      "enabled": true,
      "tags": ["backend", "api", "database"],
      "expertise": ["python", "go", "postgresql"],
      "not_good_at": ["frontend", "design"]
    }
  }
}
```

## 用例场景

- Team Building: 记录所有团队成员及其技能信息
- Task Assignment: 根据成员专长和标签分配任务
- Capability Assessment: 了解每个成员的优势和弱点
- Team Collaboration: 快速找到具有特定技能的成员

---

### 任务管理 (task.py)

管理团队任务：

```bash
python3 scripts/task.py <command> [options]
```

| 命令 | 说明 |
|------|------|
| `add` | 创建新任务 |
| `list` | 列出任务（可过滤） |
| `show` | 查看任务详情 |
| `update` | 更新任务 |
| `assign` | 指派任务 |
| `complete` | 完成任务 |
| `reset` | 重置任务数据 |

#### 创建任务

```bash
python3 scripts/task.py add \
  --title "实现用户认证" \
  --description "添加 JWT 认证功能" \
  --priority high \
  --assignee coder \
  --tags "backend,auth"
```

参数说明：
- `--title`: 任务标题 (必需)
- `--description`: 任务描述
- `--priority`: 优先级 (low/medium/high/urgent，默认 medium)
- `--assignee`: 指派给成员
- `--tags`: 标签，逗号分隔

#### 列出任务

```bash
# 列出所有任务
python3 scripts/task.py list

# 按状态过滤
python3 scripts/task.py list --status pending

# 按指派人过滤
python3 scripts/task.py list --assignee coder
```

状态值：`pending`、`assigned`、`in_progress`、`completed`、`blocked`

#### 查看任务详情

```bash
python3 scripts/task.py show --id task-abc123
```

#### 更新任务

```bash
python3 scripts/task.py update \
  --id task-abc123 \
  --status in_progress \
  --priority urgent
```

#### 指派任务

```bash
python3 scripts/task.py assign --id task-abc123 --assignee coder
```

#### 完成任务

```bash
python3 scripts/task.py complete --id task-abc123 --result "已完成 JWT 认证实现"
```

#### 任务数据文件

默认存储位置：`~/.agent-team/tasks.json`

```json
{
  "tasks": {
    "task-abc123": {
      "id": "task-abc123",
      "title": "实现用户认证",
      "description": "添加 JWT 认证功能",
      "assignee": "coder",
      "status": "completed",
      "priority": "high",
      "tags": ["backend", "auth"],
      "result": "已完成 JWT 认证实现",
      "created_at": "2026-03-06T14:00:00",
      "updated_at": "2026-03-06T16:30:00"
    }
  }
}
```

## 测试

运行测试：

```bash
python3 -m pytest tests/
```

测试覆盖：
- `test_team.py` - 成员管理测试 (14 个测试)
- `test_task.py` - 任务管理测试 (45 个测试)