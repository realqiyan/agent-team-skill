---
name: agent-team-skill
description: "Manage AI agent team members with skills, roles, and task delegation. Use when team coordination is needed, delegating tasks to experts, or managing team member information. Keywords: team, agent, delegation, expertise, leader, collaboration."
license: MIT
compatibility: Requires Python 3.10+
metadata:
  clawdbot:
    emoji: "🤖"
    requires:
      bins:
        - python3
---

# Agent Team Skill

管理 Agent 团队成员信息，包括技能、角色和工作分配。

## 🤝 团队协作规则（最高优先级 - 违反 = 严重错误）

### 🎯 Leader 职责

**沟通是基本要求，但要为结果负责：**

1. **禁止无脑透传**
   - 收到任务 → 评估职责 → 转交给正确的人
   - 转交前明确需求，转交后检查产出

2. **批判思维**
   - 对问题和结果提出挑战
   - 不符合需求 → 要求改进，不能直接传递

3. **推进改进**
   - 识别问题和风险
   - 主动发现问题并解决

4. **为结果负责**
   - 团队成员的产出 = 你的责任
   - 质量不达标 → 提供反馈并迭代直到达标

### ⚡ 任务转交规则（核心原则）

**任务转交流程：理解需求 → 明确目标 → 判断职责 → 转交给正确的人**

转交时机：
1. 先完成前置工作：理解需求、明确目标、确认约束条件
2. 进入实施阶段时：判断谁最适合执行，转交给对应成员
3. 转交后跟进：检查产出质量，确保符合需求

### 🔄 Leader 任务分配原则

**Leader 收到任务后的正确做法：**

1. **前置工作自己做**
   - 理解需求、明确目标、识别风险
   - 不要把需求理解的包袱扔给团队成员

2. **实施工作转交出去**
   - 识别最适合执行的团队成员
   - 清晰传达任务目标和约束条件
   - 转交后跟进检查产出质量

3. **避免两个极端**
   - ❌ 收到就转：前置工作没做，团队成员一头雾水
   - ❌ 自己全干：团队成员闲置，Leader 忙不过来

Leader 只在以下情况亲自实施：
1. 团队成员处理失败
2. 团队成员明确无法处理
3. 找不到相关成员

## 查询团队成员

列出所有团队成员信息：

```bash
python3 scripts/team.py list
```

输出示例：
```markdown
## Team Members

**Alice** ⭐ Leader - 协调,统筹,决策
- agent_id: alice
- expertise: 任务拆解,综合决策,agent协调
- not_good_at: 代码开发,投资分析

**Bob** - Backend Developer - 后端,API,数据库
- agent_id: bob
- expertise: Python,Go,PostgreSQL
- not_good_at: 前端,设计

# Total: 2 member(s), Leader: Alice (alice)
```

## 添加/更新成员

添加新成员或更新现有成员信息：

```bash
python3 scripts/team.py update \
  --agent-id "agent-001" \
  --name "Alice" \
  --role "Backend Developer" \
  --is-leader "true" \
  --enabled "true" \
  --tags "backend,api,database" \
  --expertise "python,go,postgresql" \
  --not-good-at "frontend,design"
```

参数说明：
- `--agent-id`: 成员唯一标识符 (必需)
- `--name`: 成员名称 (必需)
- `--role`: 角色/职位 (必需)
- `--is-leader`: 是否为团队 Leader (必需，true/false，一个团队只能有一个 Leader)
- `--enabled`: 启用状态 true/false (必需)
- `--tags`: 标签，逗号分隔 (必需)
- `--expertise`: 专长技能，逗号分隔 (必需)
- `--not-good-at`: 弱项领域，逗号分隔 (必需)

## 重置数据

清空所有团队数据，重置为初始状态：

```bash
python3 scripts/team.py reset
```

⚠️ 此操作会清空 `~/.agent-team/team.json` 中的所有数据。

## 数据存储

团队数据存储于 `~/.agent-team/team.json`，全局共享，目录不存在时自动创建。

## 使用场景

- **团队维护**：记录所有成员及其技能信息
- **任务分配**：根据成员专长和标签分配任务
