---
name: agent-team-skill
description: "Team collaboration and task processing flow with delegation, progress tracking, and multi-agent coordination. Use when team coordination, task delegation, or workflow management is needed."
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

Manage AI agent team members with skills, roles, and task delegation.

## 🤝 Team Collaboration Rules (Highest Priority - Violation = Critical Error)

### 🎯 Leader Responsibilities

**Communication is basic, but you are responsible for results:**

1. **No blind forwarding**
   - Receive task → Assess responsibility → Delegate to the right person
   - Clarify requirements before delegating, check output after

2. **Critical thinking**
   - Challenge problems and results
   - If it doesn't meet requirements → Request improvements, don't just pass it along

3. **Drive improvements**
   - Identify problems and risks
   - Proactively discover and solve issues

4. **Take responsibility for results**
   - Team member's output = Your responsibility
   - Quality not up to standard → Provide feedback and iterate until it is

### 🔄 Task Execution Flow (Six Phases)

**SEARCH → RECORD → ORIENT → DISPATCH → REVIEW → UPDATE**

**IMPORTANT: All tasks must follow this flow without exception.**

#### 1. SEARCH — Context Search
- Search memory/ directory for historical records
- Understand task background and relevant context

#### 2. RECORD — Progress Logging
- Create/update memory/YYYY-MM-DD.md
- Log task start status

#### 3. ORIENT — Orientation Phase (Core Leader Responsibility)
- **Understand Requirements**: What does the user really want?
- **Interview**: Clarify unclear requirements (max 5 questions / 2 rounds, prefer multiple choice)
- **Clarify Goals**: What's the deliverable? Success criteria?
- **Identify Risks**: What could go wrong?
- **Determine Responsibility**: Who's best suited to execute?

#### 4. DISPATCH — Delegate/Execute
- **Belongs to team member** → Delegate with full context
- **Belongs to self** → Execute directly
  - Simple task: Just do it
  - Complex task: Write plan file → Execute → Checkpoint

#### 5. REVIEW — Check Task Results
- Review completed work against requirements
- If task incomplete → Loop back to node 1 (SEARCH)

#### 6. UPDATE — Update Progress Status
- Update task status in memory/YYYY-MM-DD.md
- Mark as completed or note remaining work

### 📋 Complex Task Rules (Applies to Everyone)

**Criteria**: >3 tool calls, involves multiple files, or needs >3 minutes.

**Flow**:
1. Write plan file — Create task-name-plan.md in work/
2. After each step — Check off and update progress
3. After each Phase — Create git checkpoint
4. Upon completion — Delete plan file or move to archive/

### 📝 Templates

**Progress Log Template** (memory/YYYY-MM-DD.md):
```markdown
## [Task Name] (HH:MM)
- Executor: [Name/Team Member]
- Goal: [One-line description]
- Status: In Progress / Completed
- Result: [Fill when complete]
```

**Plan File Template** (work/task-name-plan.md):
```markdown
# [Task Name] Plan

## Goal
[What we want to achieve]

## Success Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]

## Risks
- [Risk 1]: [Mitigation]
- [Risk 2]: [Mitigation]

## Execution

### Phase 1: [Phase Name]
- [ ] [Step 1]
- [ ] [Step 2]

### Phase 2: [Phase Name]
- [ ] [Step 1]
- [ ] [Step 2]

## Checkpoints
- [ ] Phase 1 complete: [commit hash]
- [ ] Phase 2 complete: [commit hash]
```

### ⚡ Task Delegation Rules (Core Principle)

**Delegation Timing:**
1. First complete prep work: understand requirements, clarify goals, confirm constraints
2. When entering implementation: identify the best person for execution, delegate to them
3. Follow up after delegation: check output quality, ensure requirements are met

## Query Team Members

List all team member information:

```bash
python3 scripts/team.py list
```

Output example:
```markdown
## Team Members

**Alice** ⭐ Leader - coordination,planning,decision-making
- agent_id: alice
- expertise: task breakdown, comprehensive decisions, agent coordination
- not_good_at: code development, investment analysis

**Bob** - Backend Developer - backend,API,database
- agent_id: bob
- expertise: Python,Go,PostgreSQL
- not_good_at: frontend,design

# Total: 2 member(s), Leader: Alice (alice)
```

## Add/Update Member

Add a new member or update existing member information:

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

Parameters:
- `--agent-id`: Member unique identifier (required)
- `--name`: Member name (required)
- `--role`: Role/position (required)
- `--is-leader`: Whether team Leader (required, true/false, only one Leader per team)
- `--enabled`: Enable status true/false (required)
- `--tags`: Tags, comma-separated (required)
- `--expertise`: Expertise skills, comma-separated (required)
- `--not-good-at`: Weak areas, comma-separated (required)

## Reset Data

Clear all team data and reset to initial state:

```bash
python3 scripts/team.py reset
```

⚠️ This operation will clear all data in `~/.agent-team/team.json`.

## Data Storage

Team data is stored in `~/.agent-team/team.json`, shared globally. Directory is auto-created if it doesn't exist.

## Use Cases

- **Team Maintenance**: Record all members and their skill information
- **Task Assignment**: Assign tasks based on member expertise and tags
