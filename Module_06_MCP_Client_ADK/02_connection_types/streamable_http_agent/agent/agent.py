# Author: Vishal Bulbule
# Date: 2026-09-22

"""Streamable HTTP transport: the current transport for remote MCP servers.

`StreamableHTTPConnectionParams` takes the server URL (including the `/mcp`
path) and optional static headers. For headers that change per request, such
as a token read from session state, pass `header_provider=` to McpToolset.

By default the agent connects to the Module 5 HTTP server on port 8000. Set
MCP_SERVER_URL to point at another server, for example a Cloud Run service
from Module 7.
"""

import os

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

STREAMABLE_HTTP_URL = os.environ.get("MCP_SERVER_URL", "http://127.0.0.1:8000/mcp")

root_agent = LlmAgent(
    name="streamable_http_agent",
    model="gemini-3.5-flash",
    description="Uses a remote MCP server over Streamable HTTP.",
    instruction="Use the MCP tools to answer the user. Report tool results exactly.",
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=STREAMABLE_HTTP_URL,
                # For a server behind auth, pass headers, for example:
                # headers={"Authorization": f"Bearer {token}"},
            ),
        )
    ],
)
