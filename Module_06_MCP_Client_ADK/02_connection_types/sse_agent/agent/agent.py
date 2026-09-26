# Author: Vishal Bulbule
# Date: 2026-09-22

"""SSE transport: a remote MCP server over HTTP and Server-Sent Events.

`SseConnectionParams` connects to the legacy two-endpoint HTTP+SSE transport.
New servers use Streamable HTTP instead (see ../streamable_http_agent/); use
SSE only for servers that have not moved yet.

By default the agent expects a local SSE server on port 8001. The README shows
how to start one from the Module 5 sample with the `fastmcp` CLI. Set
MCP_SSE_URL to point at another server.
"""

import os

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, SseConnectionParams

SSE_URL = os.environ.get("MCP_SSE_URL", "http://127.0.0.1:8001/sse")

root_agent = LlmAgent(
    name="sse_agent",
    model="gemini-3.5-flash",
    description="Uses a remote MCP server over the HTTP+SSE transport.",
    instruction="Use the MCP tools to answer the user. Report tool results exactly.",
    tools=[
        McpToolset(
            connection_params=SseConnectionParams(
                url=SSE_URL,
                # For a server behind auth, pass headers, for example:
                # headers={"Authorization": f"Bearer {token}"},
            ),
        )
    ],
)
