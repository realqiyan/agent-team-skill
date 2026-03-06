# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A CLI tool for managing AI agent teams and tasks. It's packaged as a "skill" for ClawHub/ClawDBot - a system for installing and running CLI tools as AI agent capabilities.

## Commands

```bash
# Run team management
python3 scripts/team.py list
python3 scripts/team.py update --agent-id "id" --name "Name" --role "Role" --enabled true --tags "tag1,tag2" --expertise "skill1" --not-good-at "weakness1"
python3 scripts/team.py reset

# Run task management
python3 scripts/task.py add --title "Title" --description "Desc" --priority high --assignee "agent-id" --tags "tag1,tag2"
python3 scripts/task.py list [--status STATUS] [--assignee AGENT_ID]
python3 scripts/task.py update --id task-xxx --status in_progress
python3 scripts/task.py assign --id task-xxx --assignee agent-id
python3 scripts/task.py complete --id task-xxx --result "Result"
python3 scripts/task.py show --id task-xxx
python3 scripts/task.py reset

# Run tests
python3 -m pytest tests/ -v
```

## Architecture

Two independent CLI modules with parallel design:

- `scripts/team.py` - Team member CRUD (stores in `~/.agent-team/team.json`)
- `scripts/task.py` - Task CRUD with status workflow (stores in `~/.agent-team/tasks.json`)

Both use argparse subcommands, output YAML format for list commands, and support `--data-file` for custom storage paths.

## Task Status Workflow

`pending` → `assigned` → `in_progress` → `completed` (or `blocked` at any stage)

## Data File Paths

Default: `~/.agent-team/team.json` and `~/.agent-team/tasks.json`

Directory is auto-created. Both scripts handle missing/invalid files gracefully.