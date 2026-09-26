# Author: Vishal Bulbule
# Date: 2026-09-22

"""Module-scope agent definition with an MCP toolset.

`root_agent` is created when the module is imported, which is what `adk web`,
`adk run`, `adk deploy`, and the API server look for. This works with MCP
because `McpToolset(...)` is a plain constructor: nothing connects at import
time, and the MCP server process starts the first time the agent needs its
tools (on the first turn). The server is stopped when the runner closes, which
`adk web` and `adk run` do on shutdown.

An agent built inside an `async def` is not loadable by those tools; the
README shows that pattern for code that runs its own Runner.
"""

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

root_agent = LlmAgent(
    name="sync_file_agent",
    model="gemini-3.5-flash",
    description="Agent defined synchronously at module scope.",
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
                timeout=30,
            ),
            tool_filter=["read_text_file", "list_directory"],
        )
    ],
)
