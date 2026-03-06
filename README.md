# Agent Team Skill

Agent 团队管理工具，用于管理团队成员信息，包括技能、角色和工作分配。

## 功能特性

- 👥 **成员管理** - 管理团队成员信息，包括技能、角色和工作分配
- 🔍 **智能路由** - 根据成员专长匹配任务
- 📊 **能力评估** - 了解每个成员的优势和弱点

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

### 会话启动初始化

在会话启动时，需要执行以下命令查询团队成员：

```bash
python3 scripts/team.py list
```

这是团队协作的基础步骤，确保了解当前团队中有哪些成员及其专长。

### 团队协作规则

团队协作规则已整合到 SKILL.md 的 description 中，核心流程如下：

1. **会话启动时** - 执行 `python3 scripts/team.py list` 查询团队成员
2. **接到任务时** - 查团队 → 找专家 → 转交执行
3. **任务分配原则** - 所有任务必须交给最擅长的伙伴执行

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

## 测试

运行测试：

```bash
python3 -m pytest tests/
```

测试覆盖：
- `test_team.py` - 成员管理测试 (14 个测试)