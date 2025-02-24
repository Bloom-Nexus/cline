import os from "os"
import osName from "os-name"
import { getShell } from "../../../utils/shell"

export function getSystemInfoPrompt(cwd: string): string {
	return `
====

SYSTEM INFORMATION

Operating System: ${osName()}
Default Shell: ${getShell()}
Home Directory: ${os.homedir().toPosix()}
Current Working Directory: ${cwd.toPosix()}
`
}
