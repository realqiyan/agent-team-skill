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

interface BeforePromptBuildContext {
  messages?: unknown[];
}

interface BeforePromptBuildResult {
  prependContext?: string;
  systemPrompt?: string;
  prependSystemContext?: string;
  appendSystemContext?: string;
}

interface PluginApi {
  config: PluginConfig;
  on: (
    event: "before_prompt_build",
    handler: (event: string, ctx: BeforePromptBuildContext) => BeforePromptBuildResult,
    options?: { priority?: number }
  ) => void;
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
 * Format team data as markdown for system context
 */
function formatTeamContext(teamData: TeamData): string {
  const members = Object.values(teamData.team).filter((m) => m.enabled !== false);

  if (members.length === 0) {
    return "";
  }

  // Find leader
  const leader = members.find((m) => m.is_leader);

  const lines: string[] = [
    "",
    "<agent_team>",
    "## Agent Team Members",
    "",
    "The following are the current available team members. When assigning tasks, please consider the member's expertise direction:",
    "",
  ];

  for (const member of members) {
    const leaderBadge = member.is_leader ? " [Leader]" : "";
    lines.push(`### ${member.name}${leaderBadge} (agent_id:${member.agent_id})`);
    lines.push(`- **role**: ${member.role}`);
    if (member.tags.length > 0) {
      lines.push(`- **tags**: ${member.tags.join(", ")}`);
    }
    if (member.expertise.length > 0) {
      lines.push(`- **expertise**:`);
      for (const exp of member.expertise) {
        lines.push(`  - ${exp}`);
      }
    }
    if (member.not_good_at.length > 0) {
      lines.push(`- **not_good_at**:`);
      for (const ng of member.not_good_at) {
        lines.push(`  - ${ng}`);
      }
    }
    lines.push("");
  }

  // Add team collaboration rules
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
  lines.push("### ⚡ Task Delegation Rules (Core Principle)");
  lines.push("");
  lines.push("**When receiving a task, first thing: Determine whose responsibility it is, delegate immediately!**");
  lines.push("");
  lines.push("### Agent Coordination");
  lines.push("");
  lines.push("### Delegation Rules");
  lines.push("- Use explore agent for open-ended codebase questions");
  lines.push("- Spawn sub-agents for long-running tasks");
  lines.push("- Use sessions_send for cross-session communication");
  lines.push("");
  lines.push("### Session Handoff");
  lines.push("When delegating to another session:");
  lines.push("1. Provide full context in the handoff message");
  lines.push("2. Include relevant file paths");
  lines.push("3. Specify expected output format");
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

  // Register before_prompt_build hook
  api.on(
    "before_prompt_build",
    (_event: string, _ctx: BeforePromptBuildContext) => {
      const dataFile = config.dataFile || DEFAULT_DATA_FILE;
      const teamData = loadTeamData(dataFile);

      if (!teamData) {
        console.log(`[agent-team] No team data found at ${dataFile}`);
        return {};
      }

      const context = formatTeamContext(teamData);
      if (!context) {
        console.log("[agent-team] No enabled team members");
        return {};
      }

      console.log(`[agent-team] Injecting team context (${Object.keys(teamData.team).length} members)`);

      return {
        appendSystemContext: context,
      };
    },
    { priority: 10 }
  );
}
