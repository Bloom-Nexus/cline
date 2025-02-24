import { BrowserSettings } from "../../../shared/BrowserSettings"

export function getBrowserToolsPrompt(browserSettings: BrowserSettings): string {
	return `
## browser_action
Description: Request to interact with a Puppeteer-controlled browser. Every action, except \`close\`, will be responded to with a screenshot of the browser's current state.
- The browser window has a resolution of ${browserSettings.viewport.width}x${browserSettings.viewport.height} pixels...
Parameters:
- action: (required) The action to perform (e.g., launch, click, type, close)...
Usage:
<browser_action>
<action>launch</action>
<url>https://example.com</url>
</browser_action>
`
}
