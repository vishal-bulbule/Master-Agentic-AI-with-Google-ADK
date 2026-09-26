# Author: Vishal Bulbule
# Date: 2026-09-22

"""McpToolset: connect an ADK agent to an MCP server.

One `McpToolset` in the agent's tools list, pointed at the reference
filesystem MCP server over stdio. ADK starts the server with `npx`, calls
`tools/list`, turns each MCP tool into an ADK tool, and forwards the model's
calls with `tools/call`. There is no adapter code.

The filesystem server enforces its own sandbox: it only accepts paths under
the folder passed on its command line, whatever the instruction says.
"""

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

# The only folder the MCP server may touch. Create it with: mkdir -p /tmp/mcp-demo
TARGET_FOLDER = "/tmp/mcp-demo"

root_agent = LlmAgent(
    name="file_agent",
    model="gemini-3.5-flash",
    description="Reads and writes files inside /tmp/mcp-demo through MCP.",
    instruction=(
        f"You help the user manage files in {TARGET_FOLDER}. "
        "You can list directories, read files, write files, and search. "
        "Use absolute paths under that folder. "
        "If the user asks about files outside that folder, refuse politely."
    ),
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        TARGET_FOLDER,
                    ],
                ),
                # The first run downloads the npm package; the 5 second
                # default can expire before the server is ready.
                timeout=30,
            ),
        )
    ],
)
