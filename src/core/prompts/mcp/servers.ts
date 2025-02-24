import { McpHub } from "../../../services/mcp/McpHub"

export function getMcpServersPrompt(mcpHub: McpHub): string {
	const mcpMode = mcpHub.getMode()
	if (mcpMode === "off") return ""
	const connectedServers =
		mcpHub
			.getServers()
			.filter((server) => server.status === "connected")
			.map((server) => {
				const config = JSON.parse(server.config)
				const tools = server.tools?.map((tool) => `- ${tool.name}: ${tool.description}`).join("\n") || ""
				return `## ${server.name} (\`${config.command} ${config.args?.join(" ") || ""}\`)\n\n### Available Tools\n${tools}`
			})
			.join("\n\n") || "(No MCP servers currently connected)"
	return `
====

MCP SERVERS

The Model Context Protocol (MCP) enables communication between the system and locally running MCP servers that provide additional tools and resources to extend your capabilities.

# Connected MCP Servers

When a server is connected, you can use the server's tools via the \`use_mcp_tool\` tool, and access the server's resources via the \`access_mcp_resource\` tool.

${connectedServers}

- MCP operations should be used one at a time, similar to other tool usage. Wait for confirmation of success before proceeding with additional operations.
`
}
