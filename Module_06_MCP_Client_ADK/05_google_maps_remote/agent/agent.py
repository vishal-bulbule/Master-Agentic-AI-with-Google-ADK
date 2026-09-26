# Author: Vishal Bulbule
# Date: 2026-09-22

"""Remote MCP server: Google Maps Grounding Lite.

A hosted Google MCP server at https://mapstools.googleapis.com/mcp, reached
over Streamable HTTP with an API key header. There is no local process and no
client library: the agent gets place search, weather, and routing tools from
the server's `tools/list`.

Listing tools works without a key; every tool call needs a Maps Platform API
key with the Maps Grounding Lite API enabled.
"""

import logging
import os

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

MAPS_MCP_URL = "https://mapstools.googleapis.com/mcp"
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")

if not GOOGLE_MAPS_API_KEY:
    logging.warning(
        "GOOGLE_MAPS_API_KEY is not set. The agent will list the Maps tools, "
        "but every tool call will fail."
    )

root_agent = LlmAgent(
    name="travel_planner",
    model="gemini-3.5-flash",
    description="Plans trips with the Google Maps Grounding Lite MCP server.",
    instruction=(
        "You help users plan trips. You have Google Maps tools for:\n"
        "- searching places (cafes, hotels, landmarks)\n"
        "- looking up weather (current conditions and forecast)\n"
        "- computing routes (driving, walking)\n"
        "Always cite the place name and any Google Maps link a tool returns. "
        "If a tool returns an error, tell the user what failed."
    ),
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=MAPS_MCP_URL,
                # An empty header value is rejected by httpx, so send the
                # header only when a key is configured.
                headers=(
                    {"X-Goog-Api-Key": GOOGLE_MAPS_API_KEY}
                    if GOOGLE_MAPS_API_KEY
                    else None
                ),
                timeout=30,
            )
        )
    ],
)
