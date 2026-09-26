# Author: Vishal Bulbule
# Date: 2026-09-22

"""Stdio transport: the MCP server runs as a local child process.

`StdioConnectionParams` wraps the `mcp` SDK's `StdioServerParameters` (the
command and arguments to launch) and adds a connection timeout. ADK starts the
process on first use and talks JSON-RPC over its stdin and stdout.
"""

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

root_agent = LlmAgent(
    name="stdio_file_agent",
    model="gemini-3.5-flash",
    description="Uses a local MCP server over stdio (npx child process).",
    instruction="Help the user with files in /tmp/mcp-demo. Use absolute paths.",
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        "/tmp/mcp-demo",
                    ],
                ),
                # Allow time for npx to download the package on first run.
                timeout=30,
            ),
        )
    ],
)
