# Author: Vishal Bulbule
# Date: 2026-09-22

"""An ADK agent calling the MCP server built in `../03_fastmcp_first_server/`.

Everything else in this module talks to MCP servers through Inspector, Claude
Desktop, or a raw JSON-RPC client. This is the same server with an agent as
the host: `McpToolset` starts `server.py` over stdio, reads `tools/list`, and
turns `get_weather` into a tool the model can call.

The server is unchanged. A server written once is reused by every host that
speaks MCP, which is the point of the protocol. Module 6 goes further with
remote servers, tool filters, and several servers in one agent.
"""

import sys
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

SERVER = Path(__file__).resolve().parents[2] / "03_fastmcp_first_server" / "server.py"

root_agent = LlmAgent(
    name="weather_mcp_agent",
    model="gemini-3.5-flash",
    description="Answers weather questions through the module's own MCP server.",
    instruction=(
        "You answer questions about the weather. Call the get_weather tool for "
        "the city the user names and answer from its result. If the tool "
        "reports an unknown city, say so and list the cities you do have. "
        "Never guess a temperature."
    ),
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    # sys.executable keeps the server on the same interpreter
                    # as this agent, so it has fastmcp installed.
                    command=sys.executable,
                    args=[str(SERVER)],
                ),
                timeout=30,
            ),
        )
    ],
)
