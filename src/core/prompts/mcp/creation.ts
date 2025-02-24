import { McpHub } from "../../../services/mcp/McpHub"

export async function getMcpCreationPrompt(mcpHub: McpHub): Promise<string> {
	const mcpServersPath = await mcpHub.getMcpServersPath()
	const mcpSettingsFilePath = await mcpHub.getMcpSettingsFilePath()
	const connectedServers =
		mcpHub
			.getServers()
			.filter((server) => server.status === "connected")
			.map((server) => server.name)
			.join(", ") || "(None running currently)"
	return `
## Creating an MCP Server

The user may ask you something along the lines of "add a tool" that does some function, in other words to create an MCP server that provides tools and resources that may connect to external APIs for example. You have the ability to create an MCP server and add it to a configuration file that will then expose the tools and resources for you to use with \`use_mcp_tool\` and \`access_mcp_resource\`.

When creating MCP servers, it's important to understand that they operate in a non-interactive environment. All credentials and authentication tokens must be provided upfront through environment variables in the MCP settings configuration.

Unless the user specifies otherwise, new MCP servers should be created in: ${mcpServersPath}

### Example MCP Server

For example, if the user wanted to give you the ability to retrieve weather information, you could create an MCP server that uses the OpenWeather API:

1. Use the \`create-typescript-server\` tool to bootstrap a new project:

\`\`\`bash
cd ${mcpServersPath}
npx @modelcontextprotocol/create-server weather-server
cd weather-server
npm install axios
\`\`\`

2. Replace \`src/index.ts\` with:

\`\`\`typescript
#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ErrorCode, ListToolsRequestSchema, McpError } from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';

const API_KEY = process.env.OPENWEATHER_API_KEY;
if (!API_KEY) throw new Error('OPENWEATHER_API_KEY required');

class WeatherServer {
    private server: Server;
    private axiosInstance;

    constructor() {
        this.server = new Server({ name: 'weather-server', version: '0.1.0' }, { capabilities: { tools: {} } });
        this.axiosInstance = axios.create({ baseURL: 'http://api.openweathermap.org/data/2.5', params: { appid: API_KEY, units: 'metric' } });
        this.setupToolHandlers();
    }

    private setupToolHandlers() {
        this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
            tools: [{ name: 'get_forecast', description: 'Get weather forecast', inputSchema: { type: 'object', properties: { city: { type: 'string' } }, required: ['city'] } }]
        }));
        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            if (request.params.name === 'get_forecast') {
                const city = request.params.arguments.city;
                const response = await this.axiosInstance.get('weather', { params: { q: city } });
                return { content: [{ type: 'text', text: JSON.stringify(response.data, null, 2) }] };
            }
            throw new McpError(ErrorCode.MethodNotFound, \`Unknown tool: \${request.params.name}\`);
        });
    }

    async run() {
        const transport = new StdioServerTransport();
        await this.server.connect(transport);
        console.error('Weather MCP server running');
    }
}

const server = new WeatherServer();
server.run().catch(console.error);
\`\`\`

3. Build the server:

\`\`\`bash
npm run build
\`\`\`

4. Add to the MCP settings file at '${mcpSettingsFilePath}':

\`\`\`json
{
    "mcpServers": {
        "weather": {
            "command": "node",
            "args": ["${mcpServersPath}/weather-server/build/index.js"],
            "env": { "OPENWEATHER_API_KEY": "user-provided-api-key" },
            "disabled": false,
            "autoApprove": []
        }
    }
}
\`\`\`

## Editing MCP Servers

The user may ask to add tools or resources to an existing MCP server (e.g., ${connectedServers}). This is possible if you can locate the repository via server arguments.

# MCP Servers Are Not Always Necessary

Only implement MCP servers when explicitly requested (e.g., "add a tool that...").
`
}
