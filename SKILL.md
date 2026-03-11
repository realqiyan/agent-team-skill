---
name: agent-team-skill
description: "团队管理。IMPORTANT: (1) 会话启动时执行 `python3 scripts/team.py list` 查询团队成员。(2) 接到任务时：查团队 → 找专家 → 转交执行。(3) 所有任务必须交给最擅长的伙伴执行。"
metadata: {"clawdbot":{"emoji":"🤖","requires":{"bins":["python3"]}}}
---

# Agent Team Management

Manage team member information including skills, roles, and work assignments.

> 💡 **提示**：如需「更新人员」或「重置数据」功能，请查看 [GUIDE.md](./GUIDE.md)。

## 查询团队成员

列出所有团队成员信息（YAML 格式）：

```bash
python3 scripts/team.py list
```

输出示例：
```yaml
team:
  - agent_id: agent-001
    name: Alice
    role: Backend Developer
    enabled: true
    tags:
      - backend
    expertise:
      - python
    not_good_at:
      - frontend
# Total: 1 member(s)
```

## 数据存储

团队数据存储于 `~/.agent-team/team.json`，目录不存在时自动创建。

## 使用场景

- **团队维护**：记录所有成员及其技能信息
- **任务分配**：根据成员专长和标签分配任务
