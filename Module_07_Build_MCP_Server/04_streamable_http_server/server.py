# Author: Vishal Bulbule
# Date: 2026-09-22

"""A stateless Streamable HTTP MCP server, ready for Cloud Run.

This uses the low-level `mcp` SDK so every moving part is visible: a `Server`
with handler functions, a `StreamableHTTPSessionManager` that speaks the
transport, and a Starlette app that mounts it at /mcp and runs the manager in
its lifespan. FastMCP does the same wiring for you (see ../lab_techtrapture_mcp/).

`stateless=True` is the Cloud Run choice. A stateful server keeps each MCP
session in process memory, so every request from a client must reach the same
instance. Stateless mode builds a fresh transport per request, so any instance
can serve any request and the service scales out behind the load balancer.

Run:
    python server.py      # listens on http://0.0.0.0:8080/mcp (PORT overrides)
"""

import contextlib
import json
import os
from collections.abc import AsyncIterator

import mcp_types
import uvicorn
from mcp.server.context import ServerRequestContext
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import (
    StreamableHTTPASGIApp,
    StreamableHTTPSessionManager,
)
from starlette.applications import Starlette
from starlette.routing import Route

WEATHER_TOOL = mcp_types.Tool(
    name="get_weather",
    description="Return current weather for a city.",
    input_schema={
        "type": "object",
        "properties": {"city": {"type": "string", "description": "City name."}},
        "required": ["city"],
    },
)


async def list_tools(
    ctx: ServerRequestContext, params: mcp_types.PaginatedRequestParams | None
) -> mcp_types.ListToolsResult:
    return mcp_types.ListToolsResult(tools=[WEATHER_TOOL])


async def call_tool(
    ctx: ServerRequestContext, params: mcp_types.CallToolRequestParams
) -> mcp_types.CallToolResult:
    if params.name != WEATHER_TOOL.name:
        return mcp_types.CallToolResult(
            content=[mcp_types.TextContent(type="text", text=f"Unknown tool: {params.name}")],
            is_error=True,
        )
    city = (params.arguments or {}).get("city", "")
    result = {"status": "success", "city": city, "temp_c": 22, "condition": "sunny"}
    return mcp_types.CallToolResult(
        content=[mcp_types.TextContent(type="text", text=json.dumps(result))],
        structured_content=result,
    )


# In mcp 2.x handlers are passed to the constructor; the 1.x decorators
# (@server.list_tools(), @server.call_tool()) no longer exist.
server = Server("weather-http", on_list_tools=list_tools, on_call_tool=call_tool)

session_manager = StreamableHTTPSessionManager(app=server, stateless=True)


@contextlib.asynccontextmanager
async def lifespan(_app: Starlette) -> AsyncIterator[None]:
    # The manager only dispatches requests while run() is active.
    async with session_manager.run():
        yield


starlette_app = Starlette(
    routes=[Route("/mcp", endpoint=StreamableHTTPASGIApp(session_manager))],
    lifespan=lifespan,
)


if __name__ == "__main__":
    # Cloud Run sets PORT. 0.0.0.0 is required inside a container.
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)
