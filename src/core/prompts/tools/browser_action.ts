import { BrowserSettings } from "../../../shared/BrowserSettings"

export function getBrowserActionPrompt(browserSettings: BrowserSettings): string {
	return `
   ## browser_action
   Description: Request to interact with a Puppeteer-controlled browser. Every action, except \`close\`, will be responded to with a screenshot of the browser's current state, along with any new console logs. You may only perform one browser action per message, and wait for the user's response including a screenshot and logs to determine the next action.
   - The sequence of actions **must always start with** launching the browser at a URL, and **must always end with** closing the browser. If you need to visit a new URL that is not possible to navigate to from the current webpage, you must first close the browser, then launch again at the new URL.
   - While the browser is active, only the \`browser_action\` tool can be used. No other tools should be called during this time. You may proceed to use other tools only after closing the browser.
   - The browser window has a resolution of ${browserSettings.viewport.width}x${browserSettings.viewport.height} pixels. When performing any click actions, ensure the coordinates are within this resolution range.
   - Before clicking on any elements such as icons, links, or buttons, you must consult the provided screenshot of the page to determine the coordinates of the element. The click should be targeted at the **center of the element**, not on its edges.
   Parameters:
   - action: (required) The action to perform. The available actions are:
       * launch: Launch a new Puppeteer-controlled browser instance at the specified URL. This **must always be the first action**.
           - Use with the \`url\` parameter to provide the URL.
           - Ensure the URL is valid and includes the appropriate protocol (e.g. http://localhost:3000/page, file:///path/to/file.html, etc.)
       * click: Click at a specific x,y coordinate.
           - Use with the \`coordinate\` parameter to specify the location.
           - Always click in the center of an element (icon, button, link, etc.) based on coordinates derived from a screenshot.
       * type: Type a string of text on the keyboard. You might use this after clicking on a text field to input text.
           - Use with the \`text\` parameter to provide the string to type.
       * scroll_down: Scroll down the page by one page height.
       * scroll_up: Scroll up the page by one page height.
       * close: Close the Puppeteer-controlled browser instance. This **must always be the final browser action**.
   - url: (optional) Use this for providing the URL for the \`launch\` action.
   - coordinate: (optional) The X and Y coordinates for the \`click\` action. Coordinates should be within the ${browserSettings.viewport.width}x${browserSettings.viewport.height} resolution.
   - text: (optional) Use this for providing the text for the \`type\` action.
   Usage:
   <browser_action>
   <action>Action to perform (e.g., launch, click, type, scroll_down, scroll_up, close)</action>
   <url>URL to launch the browser at (optional)</url>
   <coordinate>x,y coordinates (optional)</coordinate>
   <text>Text to type (optional)</text>
   </browser_action>
   `
}
