/**
 * Agent Team Plugin for OpenClaw
 *
 * Injects team member information into the system context before prompt build.
 * This ensures AI agents always have access to team information without needing
 * to explicitly invoke tools.
 */

import { readFileSync, existsSync } from "fs";
import { homedir } from "os";
import { join } from "path";

interface TeamMember {
  agent_id: string;
  name: string;
  role: string;
  is_leader: boolean;
  enabled: boolean;
  tags: string[];
  expertise: string[];
  not_good_at: string[];
}

interface TeamData {
  team: Record<string, TeamMember>;
}

interface PluginConfig {
  dataFile?: string;
  enabled?: boolean;
}

// OpenClaw 官方钩子类型定义
interface PluginHookAgentContext {
  agentId?: string;
  sessionKey?: string;
  sessionId?: string;
  workspaceDir?: string;
  messageProvider?: string;
  trigger?: string;
  channelId?: string;
}

interface PluginHookBeforePromptBuildEvent {
  prompt: string;
  messages: unknown[];
}

interface PluginHookBeforePromptBuildResult {
  prependContext?: string;
  systemPrompt?: string;
  prependSystemContext?: string;
  appendSystemContext?: string;
}

interface PluginApi {
  config: PluginConfig;
  on: (
    event: "before_prompt_build",
    handler: (
      event: PluginHookBeforePromptBuildEvent, 
      ctx: PluginHookAgentContext
    ) => PluginHookBeforePromptBuildResult | void,
    options?: { priority?: number }
  ) => void;
  registerCommand: (command: {
    name: string;
    description?: string;
    acceptsArgs?: boolean;
    requireAuth?: boolean;
    handler: (ctx: {
      senderId?: string;
      channel?: string;
      isAuthorizedSender?: boolean;
      args?: string;
      commandBody?: string;
      config?: unknown;
    }) => { text: string } | Promise<{ text: string }>;
  }) => void;
}

// Default data file path
const DEFAULT_DATA_FILE = join(homedir(), ".agent-team", "team.json");

/**
 * Load team data from JSON file
 */
function loadTeamData(dataFilePath: string): TeamData | null {
  try {
    if (!existsSync(dataFilePath)) {
      return null;
    }
    const content = readFileSync(dataFilePath, "utf-8");
    const data = JSON.parse(content) as TeamData;
    if (!data || typeof data !== "object" || !data.team) {
      return null;
    }
    return data;
  } catch (error) {
    console.error(`[agent-team] Error loading team data: ${error}`);
    return null;
  }
}

/**
 * Format a single team member as markdown line
 * @param member Team member to format
 * @param options Formatting options
 */
function formatMember(member: TeamMember, options: { compact?: boolean } = {}): string[] {
  const { compact = false } = options;
  const tagsStr = compact ? member.tags.join(",") : member.tags.join(", ");
  const expertiseStr = member.expertise.join(compact ? "," : ", ");
  const notGoodAtStr = member.not_good_at.join(compact ? "," : ", ");

  const lines: string[] = [];

  if (member.is_leader) {
    if (compact) {
      lines.push(`**${member.name}** ⭐ ${member.role} - ${tagsStr}`);
    } else {
      lines.push(`**${member.name}** ⭐ ${member.role} (Leader)`);
    }
  } else {
    if (compact) {
      lines.push(`**${member.name}** - ${member.role} - ${tagsStr}`);
    } else {
      lines.push(`**${member.name}** - ${member.role}`);
    }
  }

  if (compact) {
    lines.push(`- agent_id: ${member.agent_id}`);
  } else {
    lines.push(`- agent_id: \`${member.agent_id}\``);
  }

  if (tagsStr && !compact) {
    lines.push(`- tags: ${tagsStr}`);
  }

  if (expertiseStr) {
    lines.push(`- expertise: ${expertiseStr}`);
  }

  if (notGoodAtStr) {
    lines.push(`- not_good_at: ${notGoodAtStr}`);
  }

  return lines;
}

/**
 * Format team members as simple markdown for command output
 */
function formatTeamMembers(teamData: TeamData): string {
  const members = Object.values(teamData.team).filter((m) => m.enabled !== false);

  if (members.length === 0) {
    return "No team members configured.";
  }

  const leader = members.find((m) => m.is_leader);

  const lines: string[] = [
    "## Team Members",
    "",
  ];

  for (const member of members) {
    lines.push(...formatMember(member));
    lines.push("");
  }

  if (leader) {
    lines.push(`Current Leader: **${leader.name}** (\`${leader.agent_id}\`)`);
  }

  return lines.join("\n");
}

/**
 * Format team data as markdown for system context
 * @param teamData Team data from JSON file
 * @param currentAgentId The agent ID of the current session (used to determine leader role)
 */
function formatTeamContext(teamData: TeamData, currentAgentId: string): string {
  const members = Object.values(teamData.team).filter((m) => m.enabled !== false);

  if (members.length === 0) {
    return "";
  }

  const leader = members.find((m) => m.is_leader);
  const isCurrentAgentLeader = leader?.agent_id === currentAgentId;

  const lines: string[] = [
    "",
    "<agent_team>",
    "## Team Members",
    "",
  ];

  for (const member of members) {
    lines.push(...formatMember(member, { compact: true }));
    lines.push("");
  }

  // Add team collaboration rules - only show Leader Responsibilities if current agent is leader
  if (isCurrentAgentLeader) {
    lines.push("## 🤝 Team Collaboration Rules (Highest Priority - Violation = Critical Error)");
    lines.push("");
    lines.push("### 🎯 Leader Responsibilities");
    lines.push("");
    if (leader) {
      lines.push(`**Current Leader: ${leader.name} (${leader.agent_id})**`);
      lines.push("");
    }
    lines.push("**Communication is basic, but you are responsible for results:**");
    lines.push("");
    lines.push("1. **No blind forwarding**");
    lines.push("   - Receive task → Assess responsibility → Delegate to the right person");
    lines.push("   - Clarify requirements before delegating, check output after");
    lines.push("");
    lines.push("2. **Critical thinking**");
    lines.push("   - Challenge problems and results");
    lines.push("   - If it doesn't meet requirements → Request improvements, don't just pass it along");
    lines.push("");
    lines.push("3. **Drive improvements**");
    lines.push("   - Identify problems and risks");
    lines.push("   - Proactively discover and solve issues");
    lines.push("");
    lines.push("4. **Take responsibility for results**");
    lines.push("   - Team member's output = Your responsibility");
    lines.push("   - Quality not up to standard → Provide feedback and iterate until it is");
    lines.push("");
  }
  lines.push("## 🔄 Task Execution Rules (Highest Priority - Violation = Critical Error)");
  lines.push("");
  lines.push("**Plan → Do → Check → Act**");
  lines.push("");
  lines.push("**IMPORTANT: This is a continuous improvement cycle. If task is incomplete in Act phase, loop back to Plan.**");
  lines.push("");
  lines.push("### 1. Plan — Planning Phase");
  lines.push("");
  lines.push("**Goal: Prepare thoroughly, avoid blind execution**");
  lines.push("");
  lines.push("- **Search Context**: Search historical memory first, do not respond immediately");
  lines.push("- **Understand Requirements**: What does the user really want?");
  lines.push("- **Clarify Questions**: Must clarify if unsure (ask clearly in one go when possible, max 3 rounds)");
  lines.push("- **Define Goals**: What's the deliverable? Success criteria?");
  lines.push("- **Identify Risks**: What could go wrong?");
  lines.push("- **Determine Ownership**: Who's best suited to execute? (self or teammate)");
  lines.push("- **Create Plan**: Output specific execution plan");
  lines.push("");
  lines.push("### 2. Do — Execution Phase");
  lines.push("");
  lines.push("**Goal: Execute the plan while maintaining records**");
  lines.push("");
  lines.push("#### ⚠️ Recording (Highest Priority - Core of Memory)");
  lines.push("");
  lines.push("**Before starting any execution, must record to `memory/YYYY-MM-DD.md`:**");
  lines.push("```");
  lines.push("## In Progress");
  lines.push("### [Task Name] (HH:MM start)");
  lines.push("- Progress: xxx");
  lines.push("```");
  lines.push("");
  lines.push("**Update record upon completion:**");
  lines.push("```");
  lines.push("### [Task Name] (HH:MM start)");
  lines.push("- End time: HH:MM | Result: xxx");
  lines.push("```");
  lines.push("");
  lines.push("#### Execution Actions");
  lines.push("");
  lines.push("- **Delegate or Execute**:");
  lines.push("  - Belongs to teammate → Delegate with full context (search history + original requirements + plan)");
  lines.push("  - Belongs to self → Execute directly");
  lines.push("- **Create Checkpoint**: Create git commit after each sub-phase");
  lines.push("  ```bash");
  lines.push("  git add -A && git commit -m \"checkpoint: [Task Name] sub-phase complete\"");
  lines.push("  ```");
  lines.push("");
  lines.push("### 3. Check — Checking Phase");
  lines.push("");
  lines.push("**Goal: Verify results, ensure quality**");
  lines.push("");
  lines.push("- Verify results against requirements");
  lines.push("- Check completeness and compliance with standards");
  lines.push("- Record issues and deviations");
  lines.push("");
  lines.push("### 4. Act — Acting Phase");
  lines.push("");
  lines.push("**Goal: Summarize experience, decide next steps**");
  lines.push("");
  lines.push("- **Update Record**: Mark final result in `memory/YYYY-MM-DD.md`");
  lines.push("- **Standardize Success**: Record effective practices, consolidate into memory");
  lines.push("- **Improve Weaknesses**: Identify optimization opportunities");
  lines.push("- **Decide Next Steps**:");
  lines.push("  - ✅ Task complete → End");
  lines.push("  - ❌ Task incomplete → Loop back to Plan");
  lines.push("");
  lines.push("### ⚡ Task Delegation Rules (Core Principle)");
  lines.push("");
  lines.push("**Delegation Timing:**");
  lines.push("1. First complete prep work: understand requirements, clarify goals, confirm constraints");
  lines.push("2. When entering implementation: identify the best person for execution, delegate to them");
  lines.push("3. Follow up after delegation: check output quality, ensure requirements are met");
  lines.push("");
  lines.push("</agent_team>");

  return lines.join("\n");
}

/**
 * Plugin register function
 */
export default function register(api: PluginApi): void {
  const config = api.config || {};

  // Skip if disabled
  if (config.enabled === false) {
    console.log("[agent-team] Plugin is disabled");
    return;
  }

  // Register /agent-team command
  api.registerCommand({
    name: "agent-team",
    description: "Show current team members",
    handler: () => {
      const dataFile = config.dataFile || DEFAULT_DATA_FILE;
      const teamData = loadTeamData(dataFile);

      if (!teamData) {
        return { text: `No team data found at ${dataFile}` };
      }

      const text = formatTeamMembers(teamData);
      return { text };
    },
  });

  // Register before_prompt_build hook
  api.on(
    "before_prompt_build",
    (_event: PluginHookBeforePromptBuildEvent, ctx: PluginHookAgentContext) => {
      const dataFile = config.dataFile || DEFAULT_DATA_FILE;
      const teamData = loadTeamData(dataFile);

      if (!teamData) {
        console.log(`[agent-team] No team data found at ${dataFile}`);
        return {};
      }

      // Get current agent ID from context, default to "main"
      const currentAgentId = ctx.agentId || "main";
      const context = formatTeamContext(teamData, currentAgentId);
      
      if (!context) {
        console.log("[agent-team] No enabled team members");
        return {};
      }

      console.log(`[agent-team] Injecting team context for agent "${currentAgentId}" (${Object.keys(teamData.team).length} members)`);

      return {
        appendSystemContext: context,
      };
    },
    { priority: 10 }
  );
}