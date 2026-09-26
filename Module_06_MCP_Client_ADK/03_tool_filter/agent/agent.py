# Author: Vishal Bulbule
# Date: 2026-09-22

"""Filtering MCP tools with tool_filter.

The same filesystem MCP server as topic 01, but `tool_filter` exposes only
`read_text_file` and `list_directory`. The server still offers `write_file`,
`edit_file`, `move_file`, and others, but ADK drops them before the model sees
the tool list, so the model has nothing to call for a write. The agent is
read-only by construction, not only by instruction.

`tool_filter` also accepts a predicate `(tool, readonly_context) -> bool` for
rules that a fixed list cannot express.
"""

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

TARGET_FOLDER = "/tmp/mcp-demo"

root_agent = LlmAgent(
    name="readonly_file_agent",
    model="gemini-3.5-flash",
    description="Read-only MCP filesystem agent.",
    instruction=(
        f"You can read files and list directories inside {TARGET_FOLDER}. "
        "Use absolute paths. You cannot write, move, or delete files. If the "
        "user asks you to modify anything, explain that you are read-only."
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
                timeout=30,
            ),
            tool_filter=["read_text_file", "list_directory"],
        )
    ],
)
