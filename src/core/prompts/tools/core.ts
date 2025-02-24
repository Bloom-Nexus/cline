export function getCoreToolsPrompt(cwd: string): string {
	return `
TOOL USE

You have access to a set of tools that are executed upon the user's approval. You can use one tool per message, and will receive the result of that tool use in the user's response.

## execute_command
Description: Request to execute a CLI command on the system. Use this when you need to perform system operations or run specific commands.
Parameters:
- command: (required) The CLI command to execute. This should be valid for the current operating system.
- requires_approval: (required) A boolean indicating whether this command requires explicit user approval.
Usage:
<execute_command>
<command>Your command here</command>
<requires_approval>true or false</requires_approval>
</execute_command>

Current working directory: ${cwd.toPosix()}
`
}
