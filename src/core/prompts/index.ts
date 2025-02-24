import { getBasePrompt } from "./foundation/base"
import { getToolUsePrompt } from "./tools/tool_use"
import { getExecuteCommandPrompt } from "./tools/execute_command"
import { getBrowserActionPrompt } from "./tools/browser_action"
import { getListCodeDefinitionNamesPrompt } from "./tools/list_code_definition_names"
import { getListFilesPrompt } from "./tools/list_files"
import { getReadFilePrompt } from "./tools/read_file"
import { getReplaceInFilePrompt } from "./tools/replace_in_file"
import { getSearchFilesPrompt } from "./tools/search_files"
import { getWriteToFilePrompt } from "./tools/write_to_file"
import { getAskFollowupQuestionPrompt } from "./tools/modes/ask_followup_question"
import { getAttemptCompletionPrompt } from "./tools/modes/attempt_completion"
import { getPlanModeResponsePrompt } from "./tools/modes/plan_mode_response"
import { getUseMcpToolPrompt } from "./mcp/tools/use_mcp_tool"
import { getAccessMcpResourcePrompt } from "./mcp/tools/access_mcp_resource"
import { getModesPrompt } from "./core_prompts/modes"
import { getCapabilitiesPrompt } from "./core_prompts/capabilities"
import { getEditingPrompt } from "./core_prompts/editing"
import { getMcpServersPrompt } from "./mcp/servers"
import { getSystemInfoPrompt } from "./core_prompts/system_info"
import { getObjectivePrompt } from "./core_prompts/objective"
import { getRulesPrompt } from "./core_prompts/rules"
import { getMcpCreationPrompt } from "./mcp/creation"
import { SYSTEM_PROMPT as getSystemPrompt } from "./foundation/system"
import { getUserInstructionsPrompt } from "./foundation/user_instructions"
import { McpHub } from "../../services/mcp/McpHub"
import { BrowserSettings } from "../../shared/BrowserSettings"

export const SYSTEM_PROMPT = async (
	cwd: string,
	supportsComputerUse: boolean,
	mcpHub: McpHub,
	browserSettings: BrowserSettings,
) => {
	const sections: string[] = [
		getBasePrompt(),
		getToolUsePrompt(),
		getExecuteCommandPrompt(cwd),
		getListCodeDefinitionNamesPrompt(cwd),
		getListFilesPrompt(cwd),
		getReadFilePrompt(cwd),
		getReplaceInFilePrompt(cwd),
		getSearchFilesPrompt(cwd),
		getWriteToFilePrompt(cwd),
		getAskFollowupQuestionPrompt(),
		getAttemptCompletionPrompt(),
		getPlanModeResponsePrompt(),
		getUseMcpToolPrompt(),
		getAccessMcpResourcePrompt(),
		getModesPrompt(),
		await getCapabilitiesPrompt(cwd, supportsComputerUse, mcpHub),
		getEditingPrompt(),
		getMcpServersPrompt(mcpHub),
		getSystemInfoPrompt(cwd),
		getObjectivePrompt(),
		getRulesPrompt(cwd, supportsComputerUse),
		await getMcpCreationPrompt(mcpHub),
	]

	if (supportsComputerUse) {
		sections.splice(3, 0, getBrowserActionPrompt(browserSettings))
	}

	return sections.join("\n\n")
}
